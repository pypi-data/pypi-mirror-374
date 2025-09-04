#!/usr/bin/env python3
# coding: utf-8
# Copyright 2024 Huawei Technologies Co., Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ===========================================================================
import glob
import os
import json
import shlex
import re
import socket
import threading
import time
import functools

from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.common_info import get_os_and_arch
from ansible.module_utils.path_manager import TmpPath

try:
    # Python 2
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue
HTTP = "http"
HTTPS = "https"

VERSION_PATTERN = re.compile(r"(\d+)")


class McuMultiProcess(object):
    def __init__(self, device_ids, module, mcu_file=''):
        self._device_ids = device_ids
        self._max_workers = len(device_ids)
        self._results = {}
        self._queue = Queue()
        self._threads = []
        self._module = module
        self.mcu_file = mcu_file

    def _upgrade_mcu(self, device_id):
        """
            Upgrade and Activate mcu.

            This function execute 'npu-smi upgrade -t mcu -i NPU_ID -f mcu.bin(hpm)' to Upgrade mcu,
                then execute 'npu-smi upgrade -a mcu -i NPU_ID' to activate mcu

            Args:
                device_id : NPU_ID from ‘npu-smi info -l’.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                upgrade_cmd = "npu-smi upgrade -t mcu -i {0} -f {1}".format(device_id, self.mcu_file)
                rc1, out1, err1 = self._module.run_command(upgrade_cmd)
                if rc1 != 0:
                    raise Exception("MCU upgrade failed: {}".format(out1 + err1))

                activate_cmd = "npu-smi upgrade -a mcu -i {0}".format(device_id)
                rc2, out2, err2 = self._module.run_command(activate_cmd)
                if rc2 != 0:
                    raise Exception("MCU activation failed: {}".format(out2 + err2))

                # Combine the output of the two steps and put both the output and the result into quene
                self._queue.put((device_id, {
                    'success': True,
                    'output': out1 + "\n" + out2,
                    'error': '',
                    'rc': 0,
                    'upgrade_rc': rc1,
                    'activate_rc': rc2
                }))
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    self._queue.put((device_id, {
                        'success': False,
                        'output': '',
                        'error': str(e),
                        'rc': -1,
                        'upgrade_rc': -1,
                        'activate_rc': -1
                    }))
                else:
                    time.sleep(1)

    def _test_mcu(self, device_id):
        """
            Test mcu and get the mcu version info.

            This function execute 'npu-smi upgrade -b mcu -i NPU_ID' to query the mcu version

            Args:
                device_id : NPU_ID from ‘npu-smi info -l’.
        """
        try:
            upgrade_cmd = "npu-smi upgrade -b mcu -i {0} ".format(device_id)
            rc, out, err = self._module.run_command(upgrade_cmd)
            if rc != 0:
                raise Exception("MCU test failed: {}".format(out + err))
            self._queue.put((device_id, {
                'success': True,
                'output': out,
                'error': '',
                'rc': 0,
            }))
        except Exception as e:
            self._queue.put((device_id, {
                'success': False,
                'output': '',
                'error': str(e),
                'rc': -1,
            }))

    def multi_run_command(self, tag='test'):
        """
            Multi run mcu command.

            This function multi-thread execution of mcu upgrade or version query commands, the default is test

            Args:
                tag : Execute upgrade or query command. optional 'upgrade' or 'test', the default is test

            Returns:
                _results: upgrade:{0:{
                                    'success': Bool,
                                    'output': String,
                                    'error': String,
                                    'rc': int,
                                    'upgrade_rc': int,
                                    'activate_rc': int
                                }..}
                            test:{0:{
                                    'success': Bool,
                                    'output': String,
                                    'error': String,
                                    'rc': int,
                                }..}
        """
        # Create and start all threads
        if tag == 'upgrade':
            target_function = self._upgrade_mcu
        else:
            target_function = self._test_mcu
        for device_id in self._device_ids:
            thread = threading.Thread(
                target=target_function,
                args=(device_id,)
            )
            self._threads.append(thread)
            thread.start()
            time.sleep(5)

        # Wait for all threads to complete
        for thread in self._threads:
            thread.join()

        # Collect results
        while not self._queue.empty():
            device_id, result = self._queue.get()
            self._results[device_id] = result

        return self._results


# same as the function in ~/utils.py, do not delete it cuz need to be imported in ansible
def compare_version(src_version, target_version):
    """
    This function is mainly to compare two versions(consist of number), return the first diff value of them.
    Especially compare two Python version.
    Args:
        src_version: your source version
        target_version: the target version you want to compare

    Example:
        src_version: 3.9.9
        target_version: 2.7.5

        the first diff value is (3 -2 ) = 1

        Steps:
        using RE to split the version by number
        results is: ['', '3', '.', '9', '.', '9', ''] and ['', '2', '.', '7', '.', '5', '']
        using zip to compress them: [('', ''), ('3', '3'), ('.', '.'), ('7', '9'), ('.', '.'), ('6', '9'), ('', '')]
        loop the zipped value, compare them, get the diff:
        ('', '') -> both not number, result = 0, skip to next loop
        (3, 2) -> 3 - 2 = 1, and 1 != 0, return 1 as final result.
    """
    use_version_parts = VERSION_PATTERN.split(src_version)
    new_version_parts = VERSION_PATTERN.split(target_version)
    for cur_ver_part, new_ver_part in zip(use_version_parts, new_version_parts):
        if cur_ver_part.isdigit() and new_ver_part.isdigit():
            result = int(cur_ver_part) - int(new_ver_part)
        else:
            # compare two string value
            # if cur_ver_part > new_ver_part, True - False = 1 Otherwise False - True = -1
            result = (cur_ver_part > new_ver_part) - (cur_ver_part < new_ver_part)
        if result != 0:
            return result
    # if the length of use_version_parts and new_version_parts are not same
    # and all the version in the same index are the same, just compare the length
    return len(use_version_parts) - len(new_version_parts)


def ascend_compare_version(src_version, target_version):
    """
    Adapted from compare_version function with modifications for Ascend software versions

    Args:
        src_version (str): Source version string, e.g. "6.0.rc1"
        target_version (str): Target version string, e.g. "6.0.0"

    Returns:
        True if src_version >= target_version else False

    Version Comparison Rules:
        - Handle versions with RC identifiers (case-insensitive)
        - Version priority: 6.0.0 > 6.0.rc3 > 6.0.rc2 > 6.0.rc1
    """
    use_version_parts = src_version.lower().split(".")
    new_version_parts = target_version.lower().split(".")
    for cur_ver_part, new_ver_part in zip(use_version_parts, new_version_parts):
        # Skip identical parts
        if cur_ver_part == new_ver_part:
            continue

        # Handle type mismatch: numeric vs alphanumeric
        # ‘r' in "rc1'，should 'r' < '0', 6.0.0 > 6.0.rcx
        if cur_ver_part.isdigit() != new_ver_part.isdigit():
            return not (cur_ver_part[0] > new_ver_part[0])

        # Same type components comparison
        # 6.0.1 > 6.0.0 or 6.0.rc3 > 6.0.rc2 > 6.0.rc1
        if len(cur_ver_part) == len(new_ver_part):
            return cur_ver_part > new_ver_part
        # Length-based comparison for same-type components (10>6）
        return len(cur_ver_part) > len(new_ver_part)
    # 6.0.rc1 == 6.0.rc1
    return True


def get(module, url):
    resp, info = fetch_url(module, url, method='GET', use_proxy=False)
    try:
        content = resp.read()
    except AttributeError:
        content = info.pop('body', '')
    return to_text(content, encoding='utf-8')


def get_protocol(module, host):
    https_url = 'https://{}/c/login'.format(host)
    content = get(module, https_url)
    if 'Not Found' in content:
        return HTTPS
    if 'wrong version number' in content:
        return HTTP

    http_url = 'http://{}/c/login'.format(host)
    content = get(module, http_url)
    if 'The plain HTTP request was sent to HTTPS port' in content:
        return HTTPS
    return HTTP


def clean_env():
    for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        os.environ.pop(key, None)


def ensure_docker_daemon_exist(module):
    docker_daemon = "/etc/docker/daemon.json"
    if os.path.exists(docker_daemon):
        return
    content_dict = dict()
    rpm = module.get_bin_path('rpm')
    if not rpm:
        content_dict.update({
            "exec-opts": ["native.cgroupdriver=systemd"],
            "live-restore": True
        })
    elif get_os_and_arch().startswith('OpenEuler'):
        content_dict.update({
            "live-restore": True
        })
    docker_config_path = os.path.dirname(docker_daemon)
    if not os.path.exists(docker_config_path):
        os.makedirs(docker_config_path, mode=0o750)
    with open(docker_daemon, 'w') as f:
        json.dump(content_dict, f, indent=4)
    module.run_command('systemctl daemon-reload')
    module.run_command('systemctl restart docker')


def find_files(path, pattern):
    messages = ["try to find {} for {}".format(path, pattern)]
    matched_files = glob.glob(os.path.join(path, pattern))
    messages.append("find files: " + ",".join(matched_files))
    return matched_files, messages


def run_command(module, command, ok_returns=None, working_dir=None):
    messages = ["calling " + command]
    return_code, out, err = module.run_command(shlex.split(command), cwd=working_dir)
    output = out + err
    if not ok_returns:
        ok_returns = [0]
    if return_code not in ok_returns:
        raise Exception("calling {} failed on {}: {}".format(command, return_code, output))
    messages.append("output of " + command + " is: " + str(output))
    return output, messages


def result_handler(failed_msg=""):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                res, msgs = func(self, *args, **kwargs)
                self.messages.extend(msgs)
            except Exception as e:
                self.messages.append(failed_msg)
                raise e
            if not res:
                raise Exception(failed_msg)

            return res

        return wrapper

    return decorator


def get_cmd_color_str(s, color):
    # 定义颜色对应的 ANSI 转义序列
    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    # 获取对应的颜色代码，如果颜色不存在则直接返回原始字符串
    if color not in colors:
        return s

    # 返回带颜色的字符串
    return "{}{}{}".format(colors[color], s, colors['reset'])


def generate_table(result, title, columns, header_name):
    # 获取实际存在的列
    # result:{'driver': ['OK', '24.1.RC2'], 'firmware': ['not installed', ''],
    #           'mcu': {'npu_id_1': '24.2.1', 'npu_id_2': '24.2.1','npu_id_4':'24.2.1'}}}
    actual_columns = [col for col in columns if any(col in data for data in result.values())]

    # 如果没有实际存在的列，返回空字符串
    if not actual_columns:
        return ""

    # 构建表头
    if 'mcu' in columns:
        actual_columns = []
        for v in result.values():
            for k, _ in v.get('mcu').items():
                actual_columns.append(k)
        actual_columns = sorted(set(actual_columns), key=lambda x: int(x.split('_')[-1]))
    header = [header_name] + actual_columns
    table = [header]

    # 构建表格
    for worker, data in result.items():
        if 'mcu' in columns:
            mcu_version_list = []
            if not data.get('mcu'):
                worker = worker + "(ERROR)"
            for npu_id in actual_columns:
                mcu_version_list.append(data.get('mcu').get(npu_id) if data.get('mcu').get(npu_id) else '')
            row = [worker] + mcu_version_list
            table.append(row)
        else:
            if any(col in data for col in actual_columns):
                row = [worker]
                for col in actual_columns:
                    if isinstance(data.get(col, " "), str):
                        row.append("{}".format(data.get(col, " ")))
                    else:
                        row.append(
                            "{}, {}".format(data.get(col, ["", ""])[0], data.get(col, ["", ""])[1]).strip(", "))
                table.append(row)

    # 如果表格只有表头，返回空字符串
    if len(table) == 1:
        return ""

    # 计算每一列的最大宽度
    col_widths = [max(len(str(item)) for item in col) for col in zip(*table)]

    # 构建格式化字符串
    format_str = " | ".join(["{{:<{}}}".format(width) for width in col_widths])

    # 构建分割线
    separator = "-+-".join(["-" * width for width in col_widths])

    # 将表格转换为字符串
    table_str = title + "\n" + separator + "\n" + "\n".join(
        [format_str.format(*row) for row in table[:1]]) + "\n" + separator + "\n" + "\n".join(
        [format_str.format(*row) for row in table[1:]]) + "\n" + separator

    # 利用shell标签增加颜色
    table_str = table_str.replace("not installed", get_cmd_color_str("not installed", 'yellow'))
    table_str = table_str.replace("OK", get_cmd_color_str("OK", 'green'))
    table_str = table_str.replace("ERROR", get_cmd_color_str("ERROR", 'red'))

    return table_str


def get_dl_yaml_file(component, version):
    yaml_file = ""
    yaml_dir = os.path.join(TmpPath.DL_YAML_DIR, "install")
    for root, dirs, files in os.walk(yaml_dir):
        for filename in files:
            if component in filename and version in filename:
                yaml_file = os.path.join(root, filename)
    return yaml_file


def to_yaml_str(data, indent=0):
    """
    将字典或列表转换成YAML格式的字符串。
    :param data: 待转换的数据，可以是字典或列表
    :param indent: 缩进级别
    :return: YAML格式字符串
    """
    yaml_str = ""
    indent_str = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            yaml_str += "{}{}: ".format(indent_str, key)
            if isinstance(value, (dict, list)):
                yaml_str += '\n' + to_yaml_str(value, indent + 2)
            else:
                yaml_str += "'{}'\n".format(value)
    elif isinstance(data, list):
        for item in data:
            yaml_str += "{}- ".format(indent_str)
            if isinstance(item, (dict, list)):
                yaml_str += '\n' + to_yaml_str(item, indent + 2)
            else:
                yaml_str += "'{}'\n".format(item)

    return yaml_str


def dump_all_to_yaml(data, output_file):
    """
    将多个数据转换成YAML格式写入到文件，每个数据以‘---’分隔。
    :param data: 待转换数据
    :param output_file: 目标文件
    """
    for index, obj in enumerate(data):
        # 添加分隔符
        output_file.write("---\n")

        yaml_str = to_yaml_str(obj)
        output_file.write(yaml_str)


def extract_package_version(filename):
    """
    Extract version number from filename following specific formats

    Args:
        filename (str): Input filename string containing version number

    Returns:
        str: Matched version string, returns None if not found

    Version Format Requirements:
        1. Standard format: number.number.number (e.g., 24.1.0)
        2. RC format: number.number.rc[1-3] (e.g., 24.1.rc1, case-insensitive)
    firmware:
    Ascend-hdk-310b-npu-firmware_7.3.0.1.231.run
    """
    firmware_pattern = r"\d+\.\d+\.\d+\.\d+\.\d+\."
    version_pattern = r"\d+\.\d+\.(?:\d+|[rR][cC][1-3])"
    for pattern in [firmware_pattern, version_pattern]:
        match = re.search(pattern, filename)
        if match:
            return match.group()
    return None


def retry(max_retries, delay=1):
    """
    A decorator to retry a function multiple times if it fails.

    Args:
        max_retries (int): The maximum number of retry attempts.
        delay (int, optional): The delay (in seconds) between retries. Defaults to 1 second.

    Returns:
        A decorated function that retries on failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        raise  # Re-raise the exception after max retries
                    time.sleep(delay)  # Wait before retrying
        return wrapper
    return decorator


def is_valid_ip(ip):
    try:
        # Attempt to convert the IP address to IPv4
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        pass

    try:
        # Attempt to convert the IP address to IPv6
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        return False
