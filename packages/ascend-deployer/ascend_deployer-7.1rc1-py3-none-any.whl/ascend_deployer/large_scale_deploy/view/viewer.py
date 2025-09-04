import collections
import os
import sys
from typing import Dict, List

from large_scale_deploy.config_model.host import InventoryHostInfo
from large_scale_deploy.config_model.progress_json import HostStatus, ProgressInfo, HostInfo


class DisplayRow:

    def __init__(self, row_name):
        self.row_name = row_name
        self._status_map = {status: 0 for status in HostStatus.ALL_STATUS}
        self.progress = 0

    def update_status(self, status_name, count):
        self._status_map[status_name] = count

    def update_progress(self, progress):
        self.progress = str(round(float(progress) * 100, 2)) + "%"

    def get_row_field_list(self):
        return [self.row_name] + [self._status_map.get(status) for status in HostStatus.ALL_STATUS] + [self.progress]


class DisplayTable:
    _ROW_TITLES = ("Task\\Status",) + HostStatus.ALL_STATUS + ("progress",)
    _MAX_STEP_LEN = 32

    def __init__(self, row_names):
        self._rows = [DisplayRow(row_name) for row_name in row_names]
        len_list = [self._MAX_STEP_LEN] + [len(title) + 2 for title in self._ROW_TITLES[1:]]
        self._format_template = " | ".join(f"{{:<{length}}}" for length in len_list)
        self._row_map: Dict[str, DisplayRow] = {row.row_name: row for row in self._rows}
        self._last_print_lines_num = 0

    def update_status(self, row_name, status_name, count):
        if row_name not in self._row_map:
            return
        self._row_map.get(row_name).update_status(status_name, count)

    def update_progress(self, row_name, progress):
        if row_name not in self._row_map:
            return
        self._row_map.get(row_name).update_progress(progress)

    def _clear_last_print_lines(self):
        for _ in range(self._last_print_lines_num):
            # 光标上移一行
            sys.stdout.write('\x1b[1A')
            # 删除当前光标位置到行末的内容
            sys.stdout.write('\033[K')
        sys.stdout.flush()

    def display(self):
        # 打印内容如下
        # Task\Status   | wait  | deploying | success | failed | unreachable | progress
        # Prepare       | 0     | 0         | 4       | 0      | 0           | 100.00%
        # Install python| 0     | 0         | 4       | 0      | 0           | 100.00%
        # Report        | 0     | 0         | 4       | 0      | 0           | 100.00%
        if not self._rows:
            return ""
        display_rows = [self._format_template.format(*self._ROW_TITLES)]
        for row in self._rows:
            display_rows.append(self._format_template.format(*row.get_row_field_list()))
        cur_print_lines_num = len(display_rows)
        cur_print_lines = os.linesep.join(display_rows)
        if cur_print_lines:
            self._clear_last_print_lines()
            self._last_print_lines_num = cur_print_lines_num
        return cur_print_lines


class StatusCount:

    def __init__(self, status: str, count: int = 0):
        self.status = status
        self.count = count


class DeployStep:

    def __init__(self, step_name: str, status_count_list: List[StatusCount], progress: float):
        self.status_count_list = status_count_list
        self.step_name = step_name
        self.progress = progress


class ClusterDeployProgressViewer:
    _NON_HOST = ("localhost",)
    _LOCAL_HOST = "localhost"

    def __init__(self, deploy_nodes: List[InventoryHostInfo], all_worker: List[InventoryHostInfo]):
        self._deploy_nodes = [deploy_node.ip for deploy_node in deploy_nodes]
        self._all_worker = [worker.ip for worker in all_worker]
        self._deploy_steps = []
        self._deploy_node_step_info_map: Dict[str, Dict[str, DeployStep]] = {}
        for deploy_node in self._deploy_nodes:
            self._deploy_node_step_info_map[deploy_node] = {}
        self._display_table = DisplayTable([])

    def update(self, deploy_node_ip, progress_json: Dict):
        if not deploy_node_ip or not progress_json:
            return
        progress_info = ProgressInfo.from_json(progress_json)
        if not self._deploy_steps:
            self._deploy_steps = [playbook.desc_en for playbook in progress_info.playbooks]
            self._display_table = DisplayTable(self._deploy_steps)
        step_info_map = self._deploy_node_step_info_map.get(deploy_node_ip)
        for playbook in progress_info.playbooks:
            for host_info in playbook.host_info_list:
                if host_info.ip == self._LOCAL_HOST:
                    host_info.ip = deploy_node_ip
            status_count_map = dict(collections.Counter([host_info.status for host_info in playbook.host_info_list]))
            status_count_list = []
            for status in HostStatus.ALL_STATUS:
                count = status_count_map.get(status, 0)
                status_count_list.append(StatusCount(status, count))
            step_info_map[playbook.desc_en] = DeployStep(playbook.desc_en, status_count_list, playbook.progress)

    def display(self):
        for step in self._deploy_steps:
            step_progress_sum = 0
            step_host_count_map: Dict[str, StatusCount] = {}
            for status in HostStatus.ALL_STATUS:
                step_host_count_map[status] = StatusCount(status)
            for deploy_node, step_info_map in self._deploy_node_step_info_map.items():
                step_info = step_info_map.get(step)
                if not step_info:
                    continue
                step_progress_sum += step_info.progress
                for status_count in step_info.status_count_list:
                    step_host_count_map.get(status_count.status).count += status_count.count
            for status_count in step_host_count_map.values():
                self._display_table.update_status(step, status_count.status, status_count.count)
            progress = round(step_progress_sum / len(self._deploy_node_step_info_map), 2)
            self._display_table.update_progress(step, progress)
        return self._display_table.display()


class FailedTaskReporter:
    _ROW_TITLES = ["服务器", "失败任务", "状态", "部署信息"]
    _STATUS_TABLE = {"failed": "失败", "unreachable": "网络不可达"}
    _MAX_STEP_LEN = 32

    def __init__(self):
        self._failed_task: Dict[str, List] = {}

    def _update_failed_row(self, playbook):
        for host_info in playbook.host_info_list:
            if host_info.status in HostStatus.FAILED_STATUS:
                task_info = [playbook.desc_zh, host_info.status, host_info.msg_list]
                self._failed_task.setdefault(host_info.ip, []).append(task_info)

    def update_failed_task(self, deploy_node_ip, progress_json: Dict):
        if not deploy_node_ip or not progress_json:
            return
        progress_info = ProgressInfo.from_json(progress_json)
        for playbook in progress_info.playbooks:
            self._update_failed_row(playbook)

    def get_failed_task_lines(self):
        if not self._failed_task:
            return ""
        rows = ["|".join(self._ROW_TITLES)]
        for ip in self._failed_task.keys():
            # info = [[task1_name, status, [message]], [task2_name, status, [message]]]
            info = self._failed_task.get(ip, [])
            for failed_task in info:
                # failed_task = [task_name, status, [message]
                task = failed_task[0]
                status = self._STATUS_TABLE.get(failed_task[1])
                msg = "\r".join(failed_task[-1]).replace("\n", ";")
                line = [ip, task, status, msg]
                row = "|".join(line)
                rows.append(row)
        return os.linesep.join(rows)

    def to_dict(self):
        res = dict()
        host_info_list = []
        for ip in self._failed_task.keys():
            info = self._failed_task.get(ip, [])
            for failed_task in info:
                host_info = HostInfo(ip, *failed_task[1:])
                host_info_list.append(host_info.to_json())
        res["host_info_list"] = host_info_list
        return res
