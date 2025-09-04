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
import os.path

from ansible.module_utils.dl import Installer
from ansible.module_utils.common_info import ContainerRuntimeType


class NpuExporterInstaller(Installer):
    component_name = 'npu-exporter'

    def get_modified_yaml_contents(self):
        lines = self._get_yaml_contents()
        replace_line = ""
        offset = -1
        node_type = self.container_runtime_type.get(self.node_name)
        if not node_type:
            self.module.fail_json("[ASCEND][ERROR] failed to find container runtime type for node: {}"
                                  "in dict: {}.".format(self.node_name, self.container_runtime_type))

        for index, line in enumerate(lines):
            """
             Check if the line contains the default docker container mode parameter
             NPU Exporter's YAML defaults to "-containerMode=docker".
             If node's container runtime is docker: no modification needed
             If container runtime is containerd: modify -containerMode, -containerd and -endpoint parameters
             """
            if "-containerMode=docker" in line:
                if node_type == ContainerRuntimeType.CONTAINERD:
                    # Replace docker mode with containerd configuration
                    replace_line = line.replace("-containerMode=docker",
                                                "-containerMode=containerd -containerd=/run/containerd/containerd.sock "
                                                "-endpoint=/run/containerd/containerd.sock")
                    offset = index
                    break

        if replace_line:
            lines[offset] = replace_line
        return lines

    def create_pull_secret(self):
        create_namespace_cmd = 'kubectl create namespace npu-exporter'
        self.module.run_command(create_namespace_cmd)


if __name__ == '__main__':
    NpuExporterInstaller().run()
