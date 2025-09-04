from typing import List

from large_scale_deploy.config_model.base import JsonDict


class HostStatus:
    WAIT = "wait"
    SUCCESS = "success"
    DEPLOYING = "deploying"
    FAILED = "failed"
    UNREACHABLE = "unreachable"

    ALL_STATUS = (WAIT, DEPLOYING, SUCCESS, FAILED, UNREACHABLE)
    FAILED_STATUS = (FAILED, UNREACHABLE)


class HostInfo(JsonDict):

    def __init__(self, ip, status, msg_list: List[str] = None):
        self.ip = ip
        self.status = status
        self.msg_list = msg_list or []


class PlayBook(JsonDict):

    def __init__(self, name, progress, actual_duration, deploy_status, desc_en, desc_zh,
                 host_info_list: List[HostInfo]):
        self.name = name
        self.progress = progress
        self.actual_duration = actual_duration
        self.deploy_status = deploy_status
        self.desc_en = desc_en
        self.desc_zh = desc_zh
        self.host_info_list = host_info_list


class ProgressInfo(JsonDict):

    def __init__(self, deploy_status, progress, playbooks: List[PlayBook], total_host_info: List[HostInfo],
                 total_expected_duration, error_msg):
        self.deploy_status = deploy_status
        self.progress = progress
        self.playbooks = playbooks
        self.total_host_info = total_host_info
        self.total_expected_duration = total_expected_duration
        self.error_msg = error_msg
