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
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.check_output_manager import check_event, wait_for_finish
from ansible.module_utils.common_info import get_os_and_arch, get_npu_info, need_skip_sys_package, UNKNOWN
from ansible.module_utils.common_utils import run_command
from ansible.module_utils.compatibility_config import EOL_CARD, EOL_MODEL, CARD_OS_COMPONENTS_MAP, \
    MODEL_TAGS_NOT_SUPPORT
from ansible.module_utils.check_library_utils.dl_checks import DLCheck
from ansible.module_utils.check_library_utils.frame_checks import FrameCheck
from ansible.module_utils.check_library_utils.npu_checks import NPUCheck
from ansible.module_utils.check_library_utils.check_user import UserCheck
from ansible.module_utils.check_library_utils.apt_yum_check import AptYumCheck
from ansible.module_utils.check_library_utils.localhost_check import LocalhostCheck
from ansible.module_utils.check_library_utils.check_k8s_device_ip import K8sDeviceIpCheck
from ansible.module_utils.check_library_utils.cann_checks import CANNCheck
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.check_library_utils.mindie_image_check import MindIEImageCheck
from ansible.module_utils.check_output_manager import CHECK_OUTPUT_MANAGER

EOL_MSG = "[ASCEND] The lifecycle of {} is over and is no longer supported"
SUPPORT_MSG = "[ASCEND] {} has no support for {} on this device"

MAX_CIRCLES = 8
DL_TAGS = {'dl', 'ascend-docker-runtime', 'clusterd', 'volcano', 'hccl-controller', 'ascend-operator',
           'ascend-device-plugin', 'noded', 'npu-exporter', 'resilience-controller'}


class CompatibilityCheck(object):

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                tags=dict(type='list'),
                python_version=dict(type='str', required=False),
                force_upgrade_npu=dict(type="bool", required=False),
                group_names=dict(type="list"),
                hosts_name=dict(type="str", required=False),
                master_groups=dict(type="list", required=False),
                worker_groups=dict(type="list", required=False),
                host_info=dict(type="dict", required=False),
                current_hostname=dict(type="str", required=False),
                ascend_deployer_work_dir=dict(type='str', required=True),
                npu_num=dict(type='int', required=False),
                packages=dict(type='dict', required=True),
                node_name=dict(type="str", required=True),
                resource_dir=dict(type="str", required=True),
                cluster_info=dict(type='dict', required=True),
                davinci_devices=dict(type="list", required=False),
                weights_path=dict(type="str", required=False),
                ip_address=dict(type="str", required=True),
                mtos_sys_dir=dict(typy="str", required=True),
                use_k8s_version=dict(type="str", required=False),
                master0_arch=dict(type="str", required=True),
                worker0_arch=dict(typy="str", required=True),
                master_arch=dict(typy="str", required=True),
                groups=dict(type="dict", required=True)
            ))
        self.tags = list(filter(bool, self.module.params.get('tags', [])))
        if 'all' in self.tags:
            self.tags.remove('all')
        # "group_names": [ "worker"]
        self.group_names = self.module.params.get("group_names")
        self.worker_groups = self.module.params.get("worker_groups")
        # "inventory_hostname": "localhost" "inventory_hostname": "192.168.1.1"
        self.current_hostname = self.module.params.get("current_hostname")
        # "hosts_name": "master,worker"
        self.hosts_name = self.module.params.get("hosts_name").split(",")
        self.packages = self.module.params.get("packages")
        self.npu_info = get_npu_info()
        self.os_and_arch = get_os_and_arch()
        self.card = util.get_card()
        self.error_messages = []
        self.dl_check = DLCheck(self.module, self.error_messages)
        self.frame_checks = FrameCheck(self.module, self.npu_info, self.error_messages)
        self.npu_check = NPUCheck(self.module, self.error_messages)
        self.user_check = UserCheck(self.module, self.error_messages)
        self.k8s_device_ip_check = K8sDeviceIpCheck(self.module, self.error_messages)
        self.cann_check = CANNCheck(self.module, self.npu_info, self.error_messages)
        self.apt_yum_check = AptYumCheck(self.module, self.error_messages)
        self.mindie_image_check = MindIEImageCheck(self.module, self.error_messages)
        self.localhost_check = LocalhostCheck(self.module, self.error_messages)
        self.tags_config = self.init_config()
        self.resources_dir = os.path.join(self.module.params.get("ascend_deployer_work_dir"), "resources")
        self.resource_dir = os.path.expanduser(self.module.params["resource_dir"])
        self.ip_address = self.module.params.get("ip_address")
        self.os_components_dict = dict()

    def base_check(self):
        if self.current_hostname in self.worker_groups:
            self.check_os_and_card_compatibility()
            self.check_sys_pkg()

    def feature_check(self):
        all_checks = set()
        for tag in self.tags:
            tag_config = self.tags_config.get(tag)
            if not tag_config:
                continue
            if not set(self.group_names).intersection(set(tag_config.get("nodes"))):
                continue
            checks = self.tags_config.get(tag).get("checks")
            if tag == "auto":
                checks = self.filter_auto_checks()
            if tag in DL_TAGS and self.current_hostname not in self.worker_groups:
                checks.remove(self.npu_check.check_npu)
            if tag == 'ascend-device-plugin' and set(self.tags).intersection({'dl', 'ascend-docker-runtime'}):
                checks.remove(self.dl_check.check_docker_runtime)
            if tag in {'ascend-operator', 'clusterd'} and set(self.tags).intersection({'dl', 'volcano'}):
                checks.remove(self.dl_check.check_volcano)
            all_checks.update(set(checks))

        for check_handler in all_checks:
            check_handler()

    def _localhost_check(self):
        if "localhost" in self.current_hostname:
            if 'MTOS' in self.os_and_arch and 'sys_pkg' in self.tags:
                self.localhost_check.check_mtos_kernel_devel_pkg()
            if set(self.tags).intersection(DL_TAGS):
                self.localhost_check.check_dl_executor()
                self.localhost_check.check_dl_diff_arch()

    def run(self):
        self.base_check()
        self._localhost_check()
        self.user_check.check_root()
        self.apt_yum_check.apt_yum_check()
        self.user_check.check_user_privilege_escalation()
        self.feature_check()
        wait_for_finish()
        check_result = {self.ip_address: CHECK_OUTPUT_MANAGER.generate_check_output()}
        if self.error_messages:
            self.error_messages.append("For check details, please see ~/.ascend_deployer/"
                                       "deploy_info/check_res_output.json.")
            return self.module.exit_json(stdout='\n'.join(self.error_messages), fail_flag=True,
                                         check_result_json=check_result)
        self.module.exit_json(stdout='\n'.join(self.error_messages), changed=True, rc=0, fail_flag=False,
                              check_result_json=check_result)

    @check_event
    def check_os_and_card_compatibility(self):
        self.check_card()
        self.check_model()
        if self.os_and_arch in self.os_components_dict:
            self.check_components()

    def check_card(self):
        card = self.npu_info.get('card')
        if card == UNKNOWN:
            # No card or could not recognise npu card
            return
        if card in EOL_CARD:
            util.record_error(EOL_MSG.format(card), self.error_messages)
            return
        self.os_components_dict = CARD_OS_COMPONENTS_MAP.get(card, dict())
        if not self.os_components_dict:
            util.record_error(
                "Check card failed: cannot find card support dict, ascend-deployer not support on this device",
                self.error_messages)
            return
        if self.os_and_arch not in self.os_components_dict:
            util.record_error("Check device supports os failed: {} is not supported on this device"
                              .format(self.os_and_arch), self.error_messages)

    def check_model(self):
        model = self.npu_info.get('model')
        if model in EOL_MODEL:
            util.record_error(EOL_MSG.format(model), self.error_messages)
        unsupported_tags = MODEL_TAGS_NOT_SUPPORT.get(model, [])
        for tag in self.tags:
            if tag in unsupported_tags:
                util.record_error("Check model failed: " + SUPPORT_MSG.format(tag, model), self.error_messages)

    def check_components(self):
        infer_devices = ('A300i-pro', 'A300i-duo', 'A200i-a2', 'Atlas 800I A2')
        card = self.npu_info.get('card')
        not_support_components = []
        supported_tags = self.os_components_dict.get(self.os_and_arch, [])
        for tag in self.tags:
            if tag not in supported_tags or (card in infer_devices and 'mindspore' in tag):
                # infer devices do not support mindspore anymore.
                not_support_components.append(tag)
        if not_support_components:
            util.record_error(
                "Check os failed: " + SUPPORT_MSG.format(','.join(not_support_components), self.os_and_arch),
                self.error_messages)

    @check_event
    def check_sys_pkg(self):
        if "sys_pkg" not in self.tags and "auto" not in self.tags:
            return

        if need_skip_sys_package(self.os_and_arch):
            util.record_error("[ASCEND][ERROR] Not support installing sys_pkg on {}".format(self.os_and_arch),
                              self.error_messages)

        need_print_sys_pkg_warning = False
        try:
            if not self.module.get_bin_path("yum"):
                return
            output, messages = run_command(self.module, "yum history")
            self.module.log(" ".join(messages))
            self.module.log(output)
            for line in output.splitlines():
                # e.g.:
                # Loaded plugins: fastestmirror
                # ID     | Command line             | Date and time    | Action(s)      | Altered
                # -------------------------------------------------------------------------------
                #     22 | install -y screen        | 2024-03-01 09:03 | Install        |    1
                words = line.split()
                if len(words) > 1 and words[0].isdigit() and words[0] != '1':
                    need_print_sys_pkg_warning = True
                    break
        except Exception as e:
            self.module.log(str(e))
            need_print_sys_pkg_warning = True
        if need_print_sys_pkg_warning:
            util.record_error("ascend-deployer is designed for initial system installation. After the "
                              "initial installation, there may be changes to the system packages on "
                              "this system. In this case, ascend-deployer may not be able to handle the"
                              " system packages correctly. If you encounter errors in this scenario, "
                              "please consider not using the auto nor sys_pkg parameters by ascend-deployer."
                              " Instead, rely on the instructions in the NPU and CANN documents to "
                              "manually install the system packages.", self.error_messages)

    def filter_cann_check(self):
        plugins = ["tfplugin", "nnrt", "nnae", "toolbox", "toolkit", "kernels"]
        for plugin in plugins:
            if self.packages.get(plugin):
                return True

        return False

    def filter_auto_checks(self):
        """
        auto场景时，过滤不需要的检查项

        """
        res = []
        checks = self.tags_config.get("auto").get("checks")
        for check in checks:
            name = check.__name__
            plugin = name.split("_")[1]
            if plugin == "cann" and self.filter_cann_check():
                res.append(check)
            elif self.packages.get(plugin):
                res.append(check)

        return res

    def init_config(self):
        return {
            'resilience-controller': {
                "checks": [
                    self.npu_check.check_npu,
                    self.dl_check.check_dl_basic,
                    self.dl_check.check_dns,
                    self.dl_check.check_resilience_controller_support,
                    self.k8s_device_ip_check.k8s_device_ip_check],
                "nodes": self.hosts_name
            },
            'npu': {"checks": [self.npu_check.check_npu], "nodes": self.hosts_name},
            'mcu': {"checks": [self.npu_check.check_npu, self.npu_check.check_mcu], "nodes": self.hosts_name},
            'firmware': {"checks": [self.npu_check.check_npu_health, self.npu_check.check_firmware],
                         "nodes": self.hosts_name},
            'driver': {"checks": [self.npu_check.check_npu_health, self.npu_check.check_driver],
                       "nodes": self.hosts_name},
            'pytorch_dev': {"checks": [self.npu_check.check_npu, self.cann_check.check_kernels,
                                       self.frame_checks.check_torch],
                            "nodes": self.hosts_name},
            'pytorch_run': {"checks": [self.npu_check.check_npu, self.cann_check.check_kernels,
                                       self.frame_checks.check_torch],
                            "nodes": self.hosts_name},
            'tensorflow_dev': {"checks": [self.npu_check.check_npu, self.frame_checks.check_tensorflow,
                                          self.cann_check.check_kernels, self.cann_check.check_tfplugin],
                               "nodes": self.hosts_name},
            'tensorflow_run': {"checks": [self.npu_check.check_npu, self.frame_checks.check_tensorflow,
                                          self.cann_check.check_kernels, self.cann_check.check_tfplugin],
                               "nodes": self.hosts_name},
            'npu-exporter': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic, self.dl_check.check_dns,
                                        self.mindie_image_check.check_npu_installed,
                                        self.k8s_device_ip_check.k8s_device_ip_check],
                             "nodes": ["worker"]},
            'noded': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic, self.dl_check.check_dns,
                                 self.mindie_image_check.check_npu_installed,
                                 self.k8s_device_ip_check.k8s_device_ip_check],
                      "nodes": ["worker"]},
            'volcano': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic, self.dl_check.check_dns,
                                   self.k8s_device_ip_check.k8s_device_ip_check],
                        "nodes": self.hosts_name},
            'ascend-operator': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic,
                                           self.dl_check.check_dns, self.dl_check.check_volcano,
                                           self.k8s_device_ip_check.k8s_device_ip_check],
                                "nodes": ["master"]},
            'clusterd': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic, self.dl_check.check_dns,
                                    self.dl_check.check_volcano, self.k8s_device_ip_check.k8s_device_ip_check],
                         "nodes": ["master"]},
            'kernels': {"checks": [self.cann_check.check_kernels, self.cann_check.check_cann_basic],
                        "nodes": self.hosts_name},
            'dl': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic, self.dl_check.check_dns,
                              self.k8s_device_ip_check.k8s_device_ip_check],
                   "nodes": self.hosts_name},
            'tfplugin': {"checks": [self.cann_check.check_tfplugin, self.cann_check.check_cann_basic],
                         "nodes": self.hosts_name},
            'toolkit': {"checks": [self.cann_check.check_cann_basic], "nodes": self.hosts_name},
            'nnrt': {"checks": [self.cann_check.check_cann_basic], "nodes": self.hosts_name},
            'nnae': {"checks": [self.cann_check.check_cann_basic], "nodes": self.hosts_name},
            'toolbox': {"checks": [self.cann_check.check_cann_basic], "nodes": self.hosts_name},
            'mindspore': {"checks": [self.frame_checks.check_mindspore], "nodes": self.hosts_name},
            'mindspore_scene': {"checks": [self.npu_check.check_npu, self.frame_checks.check_mindspore,
                                           self.cann_check.check_cann_basic, self.cann_check.check_kernels],
                                "nodes": self.hosts_name},
            'auto': {"checks": [self.npu_check.check_npu, self.frame_checks.check_tensorflow,
                                self.frame_checks.check_mindspore, self.cann_check.check_kernels,
                                self.frame_checks.check_torch, self.cann_check.check_tfplugin,
                                self.cann_check.check_cann_basic],
                     "nodes": self.hosts_name},
            'ascend-device-plugin': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic,
                                                self.dl_check.check_dns, self.mindie_image_check.check_npu_installed,
                                                self.dl_check.check_docker_runtime,
                                                self.k8s_device_ip_check.k8s_device_ip_check],
                                     "nodes": ["worker"]},
            'ascend-docker-runtime': {"checks": [self.npu_check.check_npu, self.dl_check.check_dns,
                                                 self.mindie_image_check.check_npu_installed],
                                      "nodes": ["worker"]},
            'mindio': {"checks": [self.dl_check.check_dns, self.dl_check.check_mindio_install_path_permission],
                       "nodes": ["worker"]},
            'offline_dev': {"checks": [self.npu_check.check_npu, self.cann_check.check_kernels],
                            "nodes": self.hosts_name},
            'offline_run': {"checks": [self.npu_check.check_npu], "nodes": self.hosts_name},
            'tensorflow': {"checks": [self.frame_checks.check_tensorflow], "nodes": self.hosts_name},
            'hccl-controller': {"checks": [self.npu_check.check_npu, self.dl_check.check_dl_basic,
                                           self.dl_check.check_dns, self.k8s_device_ip_check.k8s_device_ip_check],
                                "nodes": ["master"]},
            'pytorch': {"checks": [self.frame_checks.check_torch], "nodes": self.hosts_name},
            'mindie_image': {"checks": [self.mindie_image_check.check_mindie_image], "nodes": self.hosts_name}
        }


if __name__ == '__main__':
    CompatibilityCheck().run()
