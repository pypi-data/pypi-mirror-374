import abc
import functools
import glob
import json
import os.path
import shlex
import shutil
import subprocess
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

import math

_CUR_PATH = os.path.abspath(__file__)
_CUR_DIR = os.path.dirname(_CUR_PATH)
_ROOT_DIR = os.path.dirname(os.path.dirname(_CUR_DIR))
_RESOURCE_DIR = os.path.join(_ROOT_DIR, "resources")

_USER_HOME = os.path.expanduser("~")
_LARGE_SCALE_TMP_DIR = os.path.join(_USER_HOME, ".ascend_deployer", "large_scale_deploy")
_LARGE_SCALE_DEPLOYER_TMP_DIR = os.path.join(_LARGE_SCALE_TMP_DIR, "ascend_deployer")
SPREAD_TASK_TMP_DIR = os.path.join(_LARGE_SCALE_TMP_DIR, "spread_task")
_SPREAD_NODES_TREE_JSON = os.path.join(SPREAD_TASK_TMP_DIR, "spread_nodes_tree.json")
_DEPLOYER_PKG_PATH = os.path.join(SPREAD_TASK_TMP_DIR, "ascend_deployer.zip")
_SPREAD_TOOL_FILE_PATH = os.path.join(SPREAD_TASK_TMP_DIR, os.path.basename(__file__))
_NEXT_SPREAD_NODES_DIR = os.path.join(SPREAD_TASK_TMP_DIR, "next_spread_nodes")
# 本地执行结果
_EXEC_RESULT_PATH = os.path.join(SPREAD_TASK_TMP_DIR, "exec_result")
# 主机收集执行结果目录
_EXEC_RESULT_DIR = os.path.join(SPREAD_TASK_TMP_DIR, "exec_results")
# 主机重定向log
_EXEC_RESULT_TMP_LOG = os.path.join(SPREAD_TASK_TMP_DIR, ".exec.log")
TIMEOUT = 30 * 60  # seconds


class MsgCls:

    @abc.abstractmethod
    def add_msg(self, msg):
        pass


def validate_cmd_result(allowed_returncode=0, raise_error=True, result_handler=lambda x: x):
    if not isinstance(allowed_returncode, (int, list, tuple)):
        raise ValueError("allowed_returncode error.")

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd, returncode, stdout, stderr = func(*args, **kwargs)
            if isinstance(cmd, list):
                cmd = " ".join(cmd)
            msg_obj = None
            if args and isinstance(args[0], MsgCls):
                msg_obj = args[0]
            valid_codes = allowed_returncode
            if isinstance(allowed_returncode, int):
                valid_codes = [allowed_returncode]
            if returncode not in valid_codes:
                error_str = str(stdout or "") + str(stderr or "")
                msg_obj and msg_obj.add_msg(f"Execute cmd: {cmd} failed. code: {returncode}, err: {error_str}")
                if raise_error:
                    raise RuntimeError(error_str)
                else:
                    return False, error_str
            msg_obj and msg_obj.add_msg(f"Execute cmd: {cmd} success.")
            return True, result_handler(stdout)

        return wrapper

    return decorator


def retry(retries=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    time.sleep(delay)
                    if attempt == retries:
                        raise e

        return wrapper

    return decorator


def run_cmd(cmd: str, timeout=10, shell=False):
    if not shell:
        cmd = shlex.split(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    stdout, stderr = process.communicate(timeout=timeout)
    if stdout and not isinstance(stdout, str):
        stdout = str(stdout, encoding='utf-8')
    if stderr and not isinstance(stderr, str):
        stderr = str(stderr, encoding='utf-8')
    return cmd, process.returncode, stdout, stderr


def write_json_file(json_dict, dest_file):
    with open(dest_file, "w", encoding="utf8") as f:
        f.write(json.dumps(json_dict))


class _JsonDict:

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return ", ".join(f"{k}: {v}" for k, v in self.__dict__.items())

    def __repr__(self):
        return str(self)


class ConnHostInfo(_JsonDict):
    _ANSIBLE_CONN_INFO_MAPPING = {
        "ip": "ip",
        "ansible_ssh_user": "account",
        "ansible_ssh_pass": "password"
    }

    def __init__(self, ip, account="", password=""):
        self.ip = ip
        self.account = account
        self.password = password

    @classmethod
    def from_ansible_host_info(cls, ansible_host_info_dict: Dict):
        return cls(**{v: ansible_host_info_dict.get(k).strip('"') for k, v in cls._ANSIBLE_CONN_INFO_MAPPING.items()})

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)

    @classmethod
    def from_file(cls, file_path):
        try:
            with open(file_path, "w", encoding="utf8") as f:
                json_list = json.loads(f.read()) or []
        except Exception:
            json_list = []
        return list(map(cls.from_json, json_list))


def run_ssh_cmd(host_info: ConnHostInfo, cmd, timeout=10):
    sshpass_cmd = f"sshpass -p {host_info.password} " if host_info.password else ""
    account_ = host_info.account and f"{host_info.account}@"
    ssh_cmd = f"{sshpass_cmd}ssh -o StrictHostKeyChecking=no {account_}{host_info.ip} '{cmd}'"
    return run_cmd(ssh_cmd, timeout=timeout)


def _get_remote_path(remote_host_info: ConnHostInfo, remote_path):
    account_ = remote_host_info.account and f"{remote_host_info.account}@"
    return f"{account_}{remote_host_info.ip}:{remote_path}"


def scp(remote_host_info: ConnHostInfo, src_path, dest_path, timeout=10):
    sshpass_cmd = f"sshpass -p {remote_host_info.password} " if remote_host_info.password else ""
    scp_cmd = f"{sshpass_cmd}scp -o StrictHostKeyChecking=no {src_path} {dest_path}"
    return run_cmd(scp_cmd, timeout=timeout)


def scp_upload(remote_host_info: ConnHostInfo, local_path, remote_path, timeout=10):
    return scp(remote_host_info, local_path, _get_remote_path(remote_host_info, remote_path), timeout)


def scp_download(remote_host_info: ConnHostInfo, local_path, remote_path, timeout=10):
    return scp(remote_host_info, _get_remote_path(remote_host_info, remote_path), local_path, timeout)


class SpreadInfo(_JsonDict):

    def __init__(self, src_host: ConnHostInfo, src_host_tmp_dir: str, pkg_sha256: str):
        self.src_host = ConnHostInfo(**src_host) if isinstance(src_host, dict) else src_host
        self.src_host_tmp_dir = src_host_tmp_dir
        self.pkg_sha256 = pkg_sha256

    def to_json(self):
        return {
            "src_host": self.src_host.to_json(),
            "src_host_tmp_dir": self.src_host_tmp_dir,
            "pkg_sha256": self.pkg_sha256
        }

    @classmethod
    def from_json(cls, json_dict: Dict):
        return cls(**json_dict)


class SpreadNode:

    def __init__(self, host_info: ConnHostInfo, spread_info: SpreadInfo = None, spread_nodes: list = None):
        self.host_info = host_info
        self.spread_info = spread_info
        self.spread_nodes: List[SpreadNode] = spread_nodes or []

    @classmethod
    def from_json(cls, node_json: dict):
        host_info = ConnHostInfo.from_json(node_json.get("host_info"))
        spread_info = node_json.get("spread_info")
        spread_info = spread_info and SpreadInfo.from_json(spread_info)
        spread_nodes = [cls.from_json(spread_node) for spread_node in node_json.get("spread_nodes", [])]
        return cls(host_info, spread_info, spread_nodes=spread_nodes)

    def to_json(self):
        return {
            "host_info": self.host_info.to_json(),
            "spread_info": self.spread_info.to_json() if self.spread_info else {},
            "spread_nodes": [spread_node.to_json() for spread_node in self.spread_nodes],
        }

    def to_file(self, file_path):
        with open(file_path, "w", encoding="utf8") as f:
            f.write(json.dumps(self.to_json(), indent=4))


class TreeNode:

    def __init__(self, spread_node: SpreadNode, idx: int, level: int, parend_node):
        self.spread_node = spread_node
        self.parend_node = parend_node
        self.idx = idx
        self.level = level
        self.next_level = []


class SpreadTool:

    @staticmethod
    def find_binary_power(x):
        return max(math.ceil(math.log2(x)), 2)

    @staticmethod
    def _get_next_node_idx(bi_range, start_idx: int, level: int):
        host_range = bi_range // (2 ** level)
        if host_range > 0:
            return True, start_idx + host_range
        return False, -1

    @classmethod
    def analyse_spread_tree(cls, spread_nodes: List[ConnHostInfo], src_host: ConnHostInfo):
        root_tree_node, src_host_node = cls._build_spread_tree(spread_nodes, src_host)
        # 若执行节点为首节点
        if src_host.ip == root_tree_node.spread_node.host_info.ip:
            return root_tree_node.spread_node
        # 将执行节点移到首节点
        if not src_host_node:
            src_host_node = TreeNode(SpreadNode(src_host), 0, 0, None)
        src_host_node.spread_node.spread_nodes.append(root_tree_node.spread_node)
        if not src_host_node.parend_node:
            return src_host_node.spread_node
        # 移除执行节点父节点对它的引用
        src_host_parent_next_nodes = []
        for spread_node in src_host_node.parend_node.spread_node.spread_nodes:
            if spread_node != src_host_node.spread_node:
                src_host_parent_next_nodes.append(spread_node)
        src_host_node.parend_node.spread_node.spread_nodes = src_host_parent_next_nodes
        return src_host_node.spread_node

    @classmethod
    def _build_spread_tree(cls, spread_nodes, src_host):
        bi_range = 2 ** cls.find_binary_power(len(spread_nodes))
        src_host_node = None
        root_tree_node = TreeNode(SpreadNode(spread_nodes[0]), 0, 1, None)
        tree_node_list = [root_tree_node]
        while True:
            new_nodes = []
            for tree_node in tree_node_list:
                res, next_node_idx = cls._get_next_node_idx(bi_range, tree_node.idx, tree_node.level)
                if not res:
                    continue
                if next_node_idx < len(spread_nodes):
                    next_spread_node = SpreadNode(spread_nodes[next_node_idx])
                    tree_node.spread_node.spread_nodes.append(next_spread_node)
                else:
                    next_spread_node = None
                tree_node.level += 1
                new_tree_node = TreeNode(next_spread_node, next_node_idx, tree_node.level, tree_node)
                if next_spread_node and src_host.ip == next_spread_node.host_info.ip:
                    src_host_node = new_tree_node
                tree_node.next_level.append(new_tree_node)
                new_nodes.append(new_tree_node)
            if not new_nodes:
                break
            tree_node_list.extend(new_nodes)
        return root_tree_node, src_host_node


class ExecResult(_JsonDict):

    def __init__(self, result=True, msg_list: List[str] = None):
        self.msg_list = msg_list or []
        self.result = result


class SpreadManager(MsgCls):
    _ROUND_RADIO = 1.6
    _LOOP_WAIT_TIME = 10

    def __init__(self, spread_node: SpreadNode, is_src_host=False, deploy_nodes: List[str] = None):
        self.spread_node = spread_node
        self.is_src_host = is_src_host
        self._pkg_manager_type = None
        self._io_workers_num = min(os.cpu_count() * 2, len(self.spread_node.spread_nodes))
        self._msg = []
        self._deploy_nodes = deploy_nodes or []

    def add_msg(self, msg):
        self._msg.append(msg)

    @classmethod
    def from_tree_json(cls, tree_json_path, is_execute_host=False, all_host_info: List[str] = None):
        with open(tree_json_path, encoding="utf8") as f:
            return cls(SpreadNode.from_json(json.loads(f.read())), is_execute_host, all_host_info)

    @validate_cmd_result()
    def _recover_dir(self, dir_path):
        os.path.exists(dir_path) and shutil.rmtree(dir_path)
        return run_cmd(f"mkdir -p {dir_path}")

    @validate_cmd_result()
    def _copy_to_tmp_dir(self, src_path):
        if not os.path.exists(src_path):
            raise RuntimeError(f"File {src_path} not existed.")
        return run_cmd(f"cp -rf {src_path} {SPREAD_TASK_TMP_DIR}")

    @validate_cmd_result(raise_error=False)
    def _check_bin_existed(self, bin_name):
        return run_cmd(f"which {bin_name}")

    @staticmethod
    def _find_pkg_by_type(base_dir, pkg_name, pkg_type):
        res = glob.glob(os.path.join(base_dir, f"**/{pkg_name}*{pkg_type}"), recursive=True)
        return res and res[0]

    @validate_cmd_result()
    def _install_pkg_by_rpm(self, pkg_path):
        return run_cmd(f"rpm -ivh --force {pkg_path}")

    @validate_cmd_result()
    def _install_pkg_by_dpkg(self, pkg_path):
        return run_cmd(f"dpkg -i --force-depends {pkg_path}")

    def _check_pkg_manager_type(self):
        if self._check_bin_existed("rpm")[0]:
            pkg_manager_type = "rpm"
        elif self._check_bin_existed("dpkg")[0]:
            pkg_manager_type = "dpkg"
        else:
            raise RuntimeError("No package manager like rpm or dpkg was found.")
        return pkg_manager_type

    def _find_pkg(self, base_dir, pkg_name):
        if self._pkg_manager_type == "rpm":
            return self._find_pkg_by_type(base_dir, pkg_name, "rpm")
        return self._find_pkg_by_type(base_dir, pkg_name, "deb")

    def _install_package(self, pkg_path):
        if not pkg_path:
            return
        if self._pkg_manager_type == "rpm":
            self._install_pkg_by_rpm(pkg_path)
        else:
            self._install_pkg_by_dpkg(pkg_path)

    def _prepare_package(self, pkg_name, pkg_path):
        if not pkg_path or self._check_bin_existed(pkg_name)[0]:
            return
        self._install_package(pkg_path)

    @validate_cmd_result()
    def _make_compress_package(self, src_dir, target_path):
        cmd = f"cd {src_dir} && find . -type f | zip {target_path} -@"
        return run_cmd(cmd, timeout=TIMEOUT, shell=True)

    @validate_cmd_result()
    def _create_remote_dir(self, remote_host_info: ConnHostInfo, dir_path):
        return run_ssh_cmd(remote_host_info, f"mkdir -p {dir_path}")

    @validate_cmd_result(raise_error=False)
    def _clear_remote_dir(self, remote_host_info: ConnHostInfo, dir_path):
        return run_ssh_cmd(remote_host_info, f"rm -rf {dir_path}")

    def _clear_and_create(self, remote_host_info: ConnHostInfo, dir_path):
        self._clear_remote_dir(remote_host_info, dir_path)
        self._create_remote_dir(remote_host_info, dir_path)

    @validate_cmd_result()
    def _scp_to_remote(self, remote_host_info: ConnHostInfo, local_path, remote_path, timeout=60):
        return scp_upload(remote_host_info, local_path, remote_path, timeout)

    @validate_cmd_result(result_handler=lambda sha_sum_res: str(sha_sum_res).split()[0])
    def _calculate_sha256(self, file_path):
        return run_cmd(f"sha256sum {file_path}", timeout=TIMEOUT)

    @validate_cmd_result(result_handler=lambda sha_sum_res: str(sha_sum_res).splitlines()[-1].split()[0])
    def _calculate_remote_sha256(self, remote_host_info: ConnHostInfo, file_path):
        return run_ssh_cmd(remote_host_info, f"sha256sum {file_path}", timeout=TIMEOUT)

    @retry()
    def _scp_and_validate(self, remote_host_info: ConnHostInfo, local_path, target_path, sha256="", timeout=60):
        self._scp_to_remote(remote_host_info, local_path, target_path, timeout)
        local_sha_res = sha256 or self._calculate_sha256(local_path)[1]
        remote_sha_res = self._calculate_remote_sha256(remote_host_info, target_path)[1]
        if local_sha_res != remote_sha_res:
            raise RuntimeError(f"From {self.spread_node.host_info.ip} {local_path} "
                               f"scp to {remote_host_info.ip} {target_path} failed.")

    @validate_cmd_result()
    def _uncompress(self, tar_path, target_dir=""):
        self._recover_dir(target_dir)
        return run_cmd(f"unzip {tar_path} -d {target_dir}", timeout=TIMEOUT)

    @validate_cmd_result()
    def _start_spread_node_task(self, remote_host_info: ConnHostInfo):
        return run_ssh_cmd(remote_host_info, f"nohup python3 {_SPREAD_TOOL_FILE_PATH} > {_EXEC_RESULT_TMP_LOG} 2>&1 &")

    def _prepare_in_spread_node(self):
        self._prepare_package("sshpass", self._find_pkg(SPREAD_TASK_TMP_DIR, "sshpass"))

    def _prepare_in_execute_host(self):
        self._recover_dir(SPREAD_TASK_TMP_DIR)
        self._recover_dir(_NEXT_SPREAD_NODES_DIR)
        self._recover_dir(_EXEC_RESULT_DIR)
        # copy self to remote
        self._copy_to_tmp_dir(__file__)
        # copy packages
        sshpass_path = self._find_pkg(_RESOURCE_DIR, "sshpass")
        zip_path = self._find_pkg(_RESOURCE_DIR, "zip")
        self._prepare_package("sshpass", sshpass_path)
        self._prepare_package("zip", zip_path)
        if sshpass_path:
            self._copy_to_tmp_dir(sshpass_path)
        # make deployer package
        self._make_compress_package(_ROOT_DIR, _DEPLOYER_PKG_PATH)
        pkg_sha256 = self._calculate_sha256(_DEPLOYER_PKG_PATH)[1]
        self.spread_node.spread_info = SpreadInfo(self.spread_node.host_info, SPREAD_TASK_TMP_DIR, pkg_sha256)

    def _prepare_for_spread_node(self, remote_host_info: ConnHostInfo):
        self._clear_and_create(remote_host_info, _NEXT_SPREAD_NODES_DIR)
        local_sshpass_path = self._find_pkg(SPREAD_TASK_TMP_DIR, "sshpass")
        if not local_sshpass_path:
            raise RuntimeError(f"Not found sshpass package in {SPREAD_TASK_TMP_DIR}")
        remote_sshpass_path = os.path.join(SPREAD_TASK_TMP_DIR, os.path.basename(local_sshpass_path))
        self._scp_and_validate(remote_host_info, local_sshpass_path, remote_sshpass_path)
        self._scp_and_validate(remote_host_info, _DEPLOYER_PKG_PATH, _DEPLOYER_PKG_PATH,
                               self.spread_node.spread_info.pkg_sha256, timeout=20 * 60)
        self._scp_and_validate(remote_host_info, _SPREAD_TOOL_FILE_PATH, _SPREAD_TOOL_FILE_PATH)

    def _send_back_res(self, exec_result: ExecResult, src_host: ConnHostInfo, failed_host: ConnHostInfo):
        write_json_file(exec_result.to_json(), _EXEC_RESULT_PATH)
        self._scp_and_validate(src_host, _EXEC_RESULT_PATH, os.path.join(_EXEC_RESULT_DIR, failed_host.ip))

    def _start_next_spread_node(self, next_spread_node: SpreadNode):
        try:
            if self.is_src_host:
                self.spread_node.to_file(_SPREAD_NODES_TREE_JSON)
            self._prepare_for_spread_node(next_spread_node.host_info)
            next_spread_node.spread_info = self.spread_node.spread_info
            next_spread_node_path = os.path.join(_NEXT_SPREAD_NODES_DIR, next_spread_node.host_info.ip)
            next_spread_node.to_file(next_spread_node_path)
            self._scp_and_validate(next_spread_node.host_info, next_spread_node_path, _SPREAD_NODES_TREE_JSON)
            self._start_spread_node_task(next_spread_node.host_info)
        except Exception as e:
            if self.spread_node.spread_info:
                self._send_back_res(ExecResult(False, [str(traceback.format_exc()), str(e)]),
                                    self.spread_node.spread_info.src_host,
                                    next_spread_node.host_info)
            raise e

    def _start_scp_to_remote_parallel(self):
        if self._io_workers_num <= 0:
            return []
        futures = []
        with ThreadPoolExecutor(max_workers=self._io_workers_num) as executor:
            for next_spread_node in self.spread_node.spread_nodes:
                futures.append(executor.submit(self._start_next_spread_node, next_spread_node))
        return [future.result() for future in futures]

    def _wait_total_scp(self, deploy_nodes: List[str], round_cost_time: float):
        power = SpreadTool.find_binary_power(len(deploy_nodes))
        max_wait_time = round_cost_time * self._ROUND_RADIO * power
        start_time = time.time()
        deploy_nodes = set(deploy_nodes)
        while True:
            send_success_worker = [file.name for file in os.scandir(_EXEC_RESULT_DIR)]
            if set(send_success_worker).issuperset(deploy_nodes):
                return True, ["Send ascend-deployer package to all deploy nodes success."]
            sending_workers = sorted(list(deploy_nodes - set(send_success_worker)))
            if time.time() - start_time > max_wait_time:
                break
            time.sleep(self._LOOP_WAIT_TIME)
        return False, [
            f"Sending package to deploy node(s) failed: {', '.join(sending_workers)}. Detail see {_EXEC_RESULT_DIR}"]

    def start(self):
        self._pkg_manager_type = self._check_pkg_manager_type()
        try:
            if self.is_src_host:
                self._prepare_in_execute_host()
            else:
                self._prepare_in_spread_node()
            round_start_time = time.time()
            self._start_scp_to_remote_parallel()
            self._uncompress(_DEPLOYER_PKG_PATH, _LARGE_SCALE_DEPLOYER_TMP_DIR)
            res = ExecResult(True, self._msg)
            self._send_back_res(res, self.spread_node.spread_info.src_host, self.spread_node.host_info)
            if self.is_src_host:
                round_end_time = time.time()
                wait_res, msg_list = self._wait_total_scp(self._deploy_nodes, round_end_time - round_start_time)
                res = ExecResult(wait_res, self._msg + msg_list)
        except Exception as e:
            self.add_msg(f"Host: {self.spread_node.host_info.ip} spread error.")
            self.add_msg(str(traceback.format_exc()))
            self.add_msg(str(e))
            res = ExecResult(False, self._msg)
            if self.spread_node.spread_info:
                self._send_back_res(res, self.spread_node.spread_info.src_host, self.spread_node.host_info)
        return res


if __name__ == '__main__':
    SpreadManager.from_tree_json(_SPREAD_NODES_TREE_JSON, False, []).start()
