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
import platform
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import common_info, common_utils, venv_installer
from ansible.module_utils.common_info import DeployStatus


class MindIEImageInstaller:
    _card_model_map = {"Atlas 800I A2": "800i-a2", "A900T": "800i-a2", "A300i-duo": "300i-duo"}

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                tags=dict(type="list", required=True),
                resources_dir=dict(type="str", required=True),
                npu_info=dict(type="dict", required=True),
                davinci_devices=dict(type="list", required=True),
                weights_path=dict(type="str", required=True),
            )
        )
        self.run_tags = self.module.params["tags"]
        self.resources_dir = os.path.expanduser(self.module.params["resources_dir"])
        self.davinci_devices = self.module.params["davinci_devices"]
        self.weights_path = self.module.params["weights_path"]
        self.npu_info = self.module.params["npu_info"]
        self.card = self.npu_info["card"]
        self.arch = platform.machine()
        self.messages = []

    def _module_failed(self):
        return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)

    def _module_success(self):
        return self.module.exit_json(msg="Install MindIE_image success.", rc=0, changed=True)

    def _find_mindie_pkg(self):
        model = self._card_model_map.get(self.card)
        if not model:
            self.module.fail_json(
                "[ASCEND][ERROR] can not find MindIE image for {0}, or MindIE not support on {0}".format(self.card))
        mindie_pattern = "Ascend-mindie-image-{}*{}.tar.gz".format(model, self.arch)
        pkgs, msgs = common_utils.find_files(os.path.join(self.resources_dir, "MindIE-image*"), mindie_pattern)
        self.messages.extend(msgs)
        if not pkgs:
            if "auto" in self.run_tags:
                self.module.exit_json(std_out="[ASCEND] can not find mindie package, mindie install skipped", rc=0,
                                      result={DeployStatus.DEPLOY_STATUS: DeployStatus.SKIP},
                                      changed=False)
            else:
                self.messages.append("[ASCEND] can not find mindie package.")
                self._module_failed()

        return pkgs[0]

    def load_mindie_image(self):
        mindie_path = self._find_mindie_pkg()
        if not self.module.get_bin_path("docker"):
            self.module.fail_json("[ASCEND][ERROR] Docker not installed, please install docker first.")
        rc, out, err = self.module.run_command(["docker", "load", "-i", mindie_path])
        if rc != 0:
            self.module.fail_json(
                '[ASCEND][ERROR] Failed to loading Docker image from {}, error:{}'.format(mindie_path, err))
        self.messages.append("Loading Docker image from {} successfully.".format(mindie_path))
        for line in out.splitlines():
            if 'Loaded image:' in line:
                return line.split()[-1]
        return self.module.fail_json('[ASCEND][ERROR] mindie image loaded, but can not get image name.')

    def get_davinci_device(self):
        _, out, _ = self.module.run_command("ls /dev/")
        all_davinci = re.findall(r"davinci\d+", out)
        if self.davinci_devices:
            davinci_nodes = []
            for device_num in self.davinci_devices:
                davinci_node = "davinci{}".format(device_num)
                if davinci_node not in all_davinci:
                    self.module.fail_json("[ASCEND][ERROR] davinci device {} not found.".format(device_num))
                davinci_nodes.append(davinci_node)
                return davinci_nodes
        return all_davinci

    def run_mindie_container(self):
        image_name = self.load_mindie_image()
        davinci_nodes = self.get_davinci_device()
        device_command = []
        for davinci_node in davinci_nodes:
            device_command.append("--device=/dev/{}".format(davinci_node))
        weights_path = "{0}:{0}:ro".format(self.weights_path)
        command = [
            "docker", "run", "--name", "MindIE", "-it", "-d", "--net=host", "--shm-size=1g",
            "-w", "/home",
            "--device=/dev/davinci_manager",
            "--device=/dev/hisi_hdc",
            "--device=/dev/devmm_svm"]
        command.extend(device_command)
        command.extend([
            "-v", "/usr/local/Ascend/driver:/usr/local/Ascend/driver:ro",
            "-v", "/usr/local/sbin:/usr/local/sbin:ro",
            "-v", weights_path,
            image_name, "bash"])
        rc, _, err = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json(msg='Failed to run MindIE, error:{}'.format(err))
        self.messages.append("Docker run MindIE successfully.")

    def run(self):
        try:
            self.run_mindie_container()
        except Exception as e:
            self.messages.append(str(e))
            self._module_failed()
        self._module_success()


def main():
    MindIEImageInstaller().run()


if __name__ == "__main__":
    main()
