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
import re

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.common_utils import result_handler, compare_version


class MindIEImageCheck:
    min_docker_version = '18.03'
    supported_device_nums = [1, 2, 4, 8]

    def __init__(self, module, error_messages):
        self.module = module
        self.tags = list(filter(bool, self.module.params.get('tags', [])))
        self.davinci_devices = module.params["davinci_devices"]
        self.weights_path = module.params["weights_path"]
        self.error_messages = error_messages

    def check_docker_version(self):
        if not self.module.get_bin_path("docker"):
            if "sys_pkg" not in self.tags:
                util.record_error('[ASCEND][ERROR] Please install docker first.',
                                  self.error_messages)
            return
        rc, out, _ = self.module.run_command("docker --version")
        if rc != 0:
            util.record_error('[ASCEND][ERROR] Please confirm that the Docker status is healthy.',
                              self.error_messages)
        docker_version = re.search(r"\d+\.\d+\.\d+", out).group()
        if compare_version(docker_version, self.min_docker_version) < 0:
            util.record_error('[ASCEND][ERROR] Docker version should be >= {}'.format(self.min_docker_version),
                              self.error_messages)

    def check_weights_path(self):
        if not self.weights_path:
            util.record_error('[ASCEND][ERROR] Please provide a value for the weights_path parameter.',
                              self.error_messages)
        elif not os.path.exists(self.weights_path):
            util.record_error('[ASCEND][ERROR] weights_path {} does not exist'.format(self.weights_path),
                              self.error_messages)

    def check_davinci_nodes(self):
        if not self.davinci_devices:
            return
        if len(self.davinci_devices) not in self.supported_device_nums:
            util.record_error("[ASCEND][ERROR] The number of mounted devices is only allowed to match one of "
                              "the values in the {}.".format(self.supported_device_nums), self.error_messages)

        if len(self.davinci_devices) != len(set(self.davinci_devices)):
            util.record_error("[ASCEND][ERROR] There are duplicate devices in the davinci list.",
                              self.error_messages)

        if not os.path.exists("/usr/local/Ascend/driver"):
            return
        _, out, _ = self.module.run_command("ls /dev/")
        all_davinci = re.findall(r"davinci\d+", out)
        for davinci_num in self.davinci_devices:
            davinci_node = "davinci{}".format(davinci_num)
            if davinci_node not in all_davinci:
                util.record_error(
                    "[ASCEND][ERROR] davinci{} not found, please run 'ls /dev/ grep davinci' to check.".format(
                        davinci_num),
                    self.error_messages)

    def check_container_exist(self):
        if not self.module.get_bin_path("docker"):
            return
        rc, out, _ = self.module.run_command(
            ["docker", "ps", "-a", "--filter", "name=MindIE", "--format", "{{.Names}}"])
        container_names = out.splitlines()
        if 'MindIE' in container_names:
            util.record_error("[ASCEND][ERROR] The MindIE container already exists. Please delete or rename the "
                              "container before creating the container again.", self.error_messages)

    @check_event
    def check_npu_installed(self):
        driver_info = "/usr/local/Ascend/driver/version.info"
        firmware_info = "/usr/local/Ascend/firmware/version.info"

        if not os.path.exists(driver_info):
            required_tags = {"driver", "npu"}
            if not required_tags.intersection(self.tags):
                util.record_error(
                    "[ASCEND][ERROR] Please install NPU driver firstly.", self.error_messages)

        if not os.path.exists(firmware_info):
            required_tags = {"firmware", "npu"}
            if not required_tags.intersection(self.tags):
                util.record_error(
                    "[ASCEND][ERROR] Please install NPU firmware firstly.", self.error_messages)

    @check_event
    def check_mindie_image(self):
        self.check_docker_version()
        self.check_weights_path()
        self.check_davinci_nodes()
        self.check_container_exist()
        self.check_npu_installed()
