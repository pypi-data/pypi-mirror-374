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
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import common_info, common_utils
from ansible.module_utils.common_info import ContainerRuntimeType


class DockerRuntimeInstaller:
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                resources_dir=dict(type="str", required=True),
                node_name=dict(type='str'),
                container_runtime_type=dict(type='dict', required=False),
            )
        )
        self.resources_dir = os.path.expanduser(self.module.params["resources_dir"])
        self.node_name = self.module.params['node_name']
        self.container_runtime_type = self.module.params['container_runtime_type']
        self.messages = []

    def find_docker_runtime_file(self):
        arch = common_info.ARCH
        arch_pattern = "x86?64" if arch == "x86_64" else arch
        search_path = os.path.join(self.resources_dir, "mindxdl/dlPackage/{}".format(arch))
        pattern = "Ascend-docker-runtime*{}.run".format(arch_pattern)

        run_files, messages = common_utils.find_files(search_path, pattern)
        self.messages.extend(messages)

        if not run_files:
            self.messages.append("docker-runtime file not found, exiting...")
            self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)

        return run_files[0]

    def run(self):
        try:
            run_file = self.find_docker_runtime_file()
            self._install_pkg(run_file)
            return self.module.exit_json(msg="\n".join(self.messages), rc=0, changed=True)
        except Exception as e:
            self.messages.append(str(e))
            return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)

    def _install_pkg(self, run_file):
        node_type = self.container_runtime_type.get(self.node_name)
        if not node_type:
            self.messages.append("[ASCEND][ERROR] failed to find container runtime type for node: {}"
                                 "in dict: {}.".format(self.node_name, self.container_runtime_type))
            self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)
        # Check if nox11 parameter is needed
        _, help_messages = common_utils.run_command(self.module, "bash {} --help".format(run_file))
        cmd_arg = " --nox11" if any("nox11" in msg for msg in help_messages) else ""
        # Check if --install-scene parameter exists and k8s container runtime type is containerd
        extra_param = "--install-scene=containerd " if any("--install-scene" in msg for msg in help_messages) else ""
        # Execute installation commands
        commands = []
        if node_type == ContainerRuntimeType.CONTAINERD:
            commands = [
                "bash {0} --uninstall{1}".format(run_file, cmd_arg),
                "bash {0} --install{1} {2}".format(run_file, cmd_arg, extra_param),
                "systemctl daemon-reload",
                "systemctl restart containerd kubelet"
            ]
        elif node_type == ContainerRuntimeType.DOCKER:
            commands = [
                "bash {0} --uninstall{1}".format(run_file, cmd_arg),
                "bash {0} --install{1} ".format(run_file, cmd_arg),
                "systemctl daemon-reload",
                "systemctl restart docker"
            ]
        else:
            pass
        try:
            for cmd in commands:
                _, messages = common_utils.run_command(self.module, cmd)
                self.messages.extend(messages)

            # retry 10 times, wait 30s every time for k8s recovery from docker restart
            for i in range(1, 11):
                try:
                    _, _ = common_utils.run_command(self.module, "kubectl get nodes")
                except Exception as err:
                    self.messages.append(str(err))
                    self.messages.append("k8s is not ok, retry to get nodes the {} time".format(i))
                    time.sleep(30)
            return self.module.exit_json(msg="\n".join(self.messages), rc=0, changed=True)
        except Exception as e:
            self.messages.append(str(e))
            return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=True)


def main():
    installer = DockerRuntimeInstaller()
    installer.run()


if __name__ == "__main__":
    main()
