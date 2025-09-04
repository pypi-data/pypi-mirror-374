import csv
import glob
import json
import os
import queue
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import utils
from ascend_deployer import CLI
from jobs import PrepareJob
from large_scale_deploy.config_model.base import Var
from large_scale_deploy.config_model.inventory import LargeScaleInventory
from large_scale_deploy.handler.inventory_spliter import InventorySpliter
from large_scale_deploy.process.remote_deploy_task import RemoteDeployTask, HostError
from large_scale_deploy.tools.decorators import process_output
from large_scale_deploy.tools.errors import ConfigrationError, LargeScaleDeployFailed
from large_scale_deploy.tools.network_tool import NetworkTool
from large_scale_deploy.tools.spread_tool import ConnHostInfo, SpreadTool, SpreadManager, run_ssh_cmd
from large_scale_deploy.view.viewer import ClusterDeployProgressViewer, FailedTaskReporter
from module_utils.common_info import TestReport
from module_utils.path_manager import LargeScalePath, TmpPath, PathManager

RETRY_FAST = "fast"
RETRY_FULL = "full"


class LargeScaleDeployer:
    _MAX_DEPLOY_WAIT_TIME = 8 * 60 * 60
    _ROUND_WAIT_TIME = 30

    def __init__(self):
        self._large_scale_inventory = LargeScaleInventory.parse(LargeScalePath.INVENTORY_FILE_PATH)
        self._subgroups = self._generate_subgroups()
        self._prepare_job = PrepareJob()
        self._io_workers_num = len(self._subgroups)
        self._thread_pool = ThreadPoolExecutor(max_workers=self._io_workers_num)
        self._progress_table_viewer = ClusterDeployProgressViewer(
            [subgroup.deploy_node for subgroup in self._subgroups], self._large_scale_inventory.worker)
        self._failed_task_reporter = FailedTaskReporter()
        self._host_error_que = queue.Queue()

    def _generate_subgroups(self):
        spliter = InventorySpliter(self._large_scale_inventory)
        if self._large_scale_inventory.deploy_node:
            subgroups = spliter.split_by_deploy_node()
        else:
            subgroups = spliter.split_by_network()
        return subgroups

    def _get_src_host(self):
        ips = NetworkTool.get_local_host_ips()[1]
        local_ip_set = {ip.strip() for ip in ips}
        for worker in self._large_scale_inventory.worker:
            if worker.ip in local_ip_set:
                return ConnHostInfo.from_ansible_host_info(worker.to_info_dict())
        raise ConfigrationError(f"Execute host must in worker nodes. local ip(s) {list(local_ip_set)} not in worker.")

    def _spread_deployer_pkg(self, retry_args):
        deploy_nodes = []
        for subgroup in self._subgroups:
            deploy_nodes.append(ConnHostInfo.from_ansible_host_info(subgroup.deploy_node.to_info_dict()))
        root_spread_node = SpreadTool.analyse_spread_tree(deploy_nodes, self._get_src_host())
        if not retry_args:
            deploy_nodes = [host_info.ip for host_info in deploy_nodes]
            spread_res = SpreadManager(root_spread_node, True, deploy_nodes).start()
        else:
            deploy_nodes = [file for file in os.listdir(LargeScalePath.EXEC_RESULTS_DIR)
                            if os.path.isfile(os.path.join(LargeScalePath.EXEC_RESULTS_DIR, file))]
            spread_res = SpreadManager.from_tree_json(LargeScalePath.SPREAD_NODES_TREE_JSON, True, deploy_nodes).start()
        if not spread_res.result:
            raise LargeScaleDeployFailed(os.linesep.join(spread_res.msg_list))

    def _start_deploy(self, ansible_args, retry_args):
        futures = []
        for sub_group in self._subgroups:
            task = RemoteDeployTask(sub_group.deploy_node_conn_info, sub_group.inventory, ansible_args,
                                    self._host_error_que, retry_args)
            futures.append(self._thread_pool.submit(task.start))
        return futures

    @staticmethod
    def _query_progress_json(host_res_dir):
        try:
            full_host_res_dir = os.path.join(LargeScalePath.REMOTE_HOST_RESULTS, host_res_dir)
            progress_json = os.path.join(full_host_res_dir, TmpPath.PROGRESS_JSON_NAME)
            if not os.path.exists(progress_json):
                return {}
            with open(progress_json, encoding="utf8") as f:
                progress_json = json.load(f)
        except Exception:
            progress_json = {}
        return progress_json

    def _build_host_task_error_info(self):
        error_msg_list = []
        while not self._host_error_que.empty():
            host_error: HostError = self._host_error_que.get()
            error_msg_list.append(f"Host: {host_error.host} task error: {host_error.error_info_list}")
        return os.linesep.join(error_msg_list)

    @staticmethod
    def finish_evnet(futures):
        return all(future.done() for future in futures)

    def _start_collect_progress(self, finish_event):
        start_time = time.time()
        while not finish_event():
            self._update_and_print()
            time.sleep(self._ROUND_WAIT_TIME)
            if time.time() - start_time > self._MAX_DEPLOY_WAIT_TIME:
                raise LargeScaleDeployFailed("Deploy time out.")
        self._update_and_print()

    def _update_and_print(self):
        for host_res_dir in os.listdir(LargeScalePath.REMOTE_HOST_RESULTS):
            progres_json = self._query_progress_json(host_res_dir)
            self._progress_table_viewer.update(host_res_dir, progres_json)
        display_str = self._progress_table_viewer.display()
        if display_str:
            print(display_str)

    def _collect_final_progress(self):
        for host_res_dir in os.listdir(LargeScalePath.REMOTE_HOST_RESULTS):
            progres_json = self._query_progress_json(host_res_dir)
            self._failed_task_reporter.update_failed_task(host_res_dir, progres_json)

    def _collect_failed_task(self):
        self._collect_final_progress()
        failed_str = self._failed_task_reporter.get_failed_task_lines()
        if not failed_str:
            return
        if os.path.exists(LargeScalePath.REPORT_DIR):
            shutil.rmtree(LargeScalePath.REPORT_DIR)
        os.makedirs(LargeScalePath.REPORT_DIR)
        report_file = os.path.join(LargeScalePath.REPORT_DIR, "host_deploy_report.csv")
        report_json = os.path.join(LargeScalePath.REPORT_DIR, "large_scale_deploy.json")
        with open(report_json, "w") as output_fs:
            json.dump(self._failed_task_reporter.to_dict(), output_fs, indent=4, ensure_ascii=False)
        with open(report_file, mode='w', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            for row in failed_str.splitlines():
                row = [col.strip() for col in row.split('|')]
                writer.writerow(row)
            print("The failed task report is saved in {}".format(report_file))

    @staticmethod
    def combine_dict(test_result, json_data):
        for key, value in json_data.items():
            if key not in test_result.keys():
                test_result[key] = json_data[key]
            else:
                if isinstance(test_result[key], dict) and isinstance(value, dict):
                    # 递归合并字典
                    test_result[key] = LargeScaleDeployer.combine_dict(test_result[key], value)
                elif not value:
                    test_result[key] = value
        return test_result

    @staticmethod
    def generate_table(table_name, cols_name, host, test_result):
        cols = [host] + cols_name
        rows = [[table_name], cols]
        for host_name, host_info in test_result.items():
            if not any(col in cols_name for col in host_info.keys()):
                continue
            row = [host_name]
            for col_name in cols_name:
                info = host_info.get(col_name, "not installed")
                if isinstance(info, list):
                    info = ','.join(info)
                row.append(info)
            rows.append(row)
        rows.append([])
        return rows

    @staticmethod
    def _collect_test_report():
        test_result = dict()
        remote_test_report = glob.glob("{}/*/test_report.json".format(LargeScalePath.REMOTE_HOST_RESULTS))
        for report in remote_test_report:
            with open(report, mode='r', encoding='utf-8') as test_report:
                data = json.load(test_report)
                test_result = LargeScaleDeployer.combine_dict(test_result, data)
        software_report = LargeScaleDeployer.generate_table(TestReport.ASCEND_SOFTWARE_TEST_REPORT,
                                                            TestReport.COLUMNS_SOFTWARE, "服务器",
                                                            test_result.get(TestReport.ASCEND_SOFTWARE_TEST_REPORT, {}))
        dl_master_report = LargeScaleDeployer.generate_table(TestReport.DL_MASTER_NODE_TEST_REPORT,
                                                             TestReport.COLUMNS_MASTER, "master-node",
                                                             test_result.get(TestReport.DL_TEST_REPORT, {}))
        dl_worker_report = LargeScaleDeployer.generate_table(TestReport.DL_WORKER_NODE_TEST_REPORT,
                                                             TestReport.COLUMNS_WORKER, "worker-node",
                                                             test_result.get(TestReport.DL_TEST_REPORT, {}))
        dl_report = [[TestReport.DL_TEST_REPORT]] + dl_master_report + dl_worker_report
        all_report = [software_report, dl_report]
        if os.path.exists(LargeScalePath.ALL_TEST_REPORT_CSV):
            os.remove(LargeScalePath.ALL_TEST_REPORT_CSV)
        with open(LargeScalePath.ALL_TEST_REPORT_CSV, mode='w', encoding='utf-8-sig') as report_file:
            writer = csv.writer(report_file)
            for table in all_report:
                writer.writerows(table)
                writer.writerow([])

    @staticmethod
    def _clear_old_label_yaml(master_conn_info):
        """
        清理前次安装dl时保存的标签信息
        """
        label_yaml = os.path.join(TmpPath.DL_YAML_DIR, "label")
        run_ssh_cmd(master_conn_info, f"rm -rf {label_yaml}")

    def _get_dl_label(self, master_conn_info):
        """
        判断是否需要添加nodeDEnable=on标签
        如果dl集群已经装了noded，将标签写入到inventory_file
        """
        _, _, out, _ = run_ssh_cmd(master_conn_info, "kubectl get pod -Ao wide")
        pods_info = out.splitlines()

        reader = csv.DictReader(pods_info, delimiter=' ', skipinitialspace=True)
        for row in reader:
            name = row['NAME']
            if "noded" in name:
                self._subgroups[0].inventory.all_vars.append(Var("NODED_LABEL", "on"))
                break

    def _process_dl(self, install_args):
        dl_args = {'dl', 'ascend-docker-runtime', 'clusterd', 'volcano', 'hccl-controller', 'ascend-operator',
                   'ascend-device-plugin', 'noded', 'npu-exporter', 'resilience-controller'}
        for dl_arg in dl_args:
            if dl_arg in install_args:
                if len(self._subgroups) > 0 and len(self._subgroups[0].inventory.master) > 0:
                    master_info_dict = self._subgroups[0].inventory.master[0].to_info_dict()
                    master_conn_info = ConnHostInfo.from_ansible_host_info(master_info_dict)
                    self._clear_old_label_yaml(master_conn_info)
                    self._get_dl_label(master_conn_info)
                    return
                else:
                    raise ConfigrationError("Please input at least one master node before install dl")

    def start(self, install_args, retry_args):
        try:
            if not retry_args:
                PathManager.init_large_scale_dirs()
            else:
                PathManager.clear_last_info_except_inventory()
            if retry_args != RETRY_FAST:
                self._spread_deployer_pkg(retry_args)
            self._process_dl(install_args)
            futures = self._start_deploy(install_args, retry_args)
            finish_evnet = partial(self.finish_evnet, futures)
            self._start_collect_progress(finish_evnet)
            self._collect_failed_task()
            if "test" in install_args:
                self._collect_test_report()
            if not self._host_error_que.empty():
                raise LargeScaleDeployFailed(self._build_host_task_error_info())
        finally:
            self._thread_pool.shutdown()


class LargeScaleCli(CLI):
    _retry_choice = [RETRY_FULL, RETRY_FAST]

    def __init__(self):
        super().__init__("large-scale-deployer", "Manage Ascend Packages and dependence packages for specified OS "
                                                 "in large scale deploy.")
        self.parser.add_argument("--retry", dest="retry", nargs="?", const=RETRY_FAST, choices=self._retry_choice,
                                 metavar="<retry_mode>", help="Retry specific mode: %(choices)s")
        self.retry = ""
        self.install_args = []

    def _process_retry_args(self):
        install_args = [arg for arg in sys.argv[1:] if "retry" not in arg]
        args = self.parser.parse_args(utils.args_with_comma(sys.argv[1:]))
        self.retry = args.retry
        if self.retry == RETRY_FAST:
            install_args.append("--nocopy")
        self.install_args = ' '.join(install_args)

    def run(self):
        self._process_args()
        self._process_retry_args()
        self._check_args()
        self._license_agreement()
        LargeScaleDeployer().start(self.install_args, self.retry)


@process_output()
def main():
    os.umask(0o022)
    LargeScaleCli().run()


if __name__ == '__main__':
    return_code, stdout, stderr = main()
    stdout and sys.stdout.write(stdout)
    stderr and sys.stdout.write(stderr)
    sys.exit(return_code)
