#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Huawei Technologies Co., Ltd
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


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common_info import ContainerRuntimeType


class DLPrepareJob(object):

    def __init__(self):
        self.module = AnsibleModule(argument_spec=dict())
        self.facts = dict()
        self.messages = []

    @staticmethod
    def extract_indices(out):
        """
        Extract the indices of 'CONTAINER-RUNTIME' and 'NAME' from the command output.

        Parameters:
        out (str): The standard output string from the command.

        Returns:
        tuple: A tuple containing the indices of 'CONTAINER-RUNTIME' and 'NAME'.
               Returns (None, None) if 'CONTAINER-RUNTIME' or 'NAME' is not found.
        """
        name_index = None
        container_runtime_index = None
        for line in out.splitlines():
            # output in the normal format
            if 'NAME' == line.split()[0] and "CONTAINER-RUNTIME" == line.split()[-1]:
                return 0, -1
        return name_index, container_runtime_index,

    def query_container_runtime_type(self):
        """
        Query the container runtime type of the Kubernetes nodes on master.

        Command: `kubectl get node -A -o wide`

        Example output:
        NAME       STATUS   ROLES    AGE   VERSION   INTERNAL-IP   ...   KERNEL-VERSION      CONTAINER-RUNTIME
        master-1   Ready    master   10d   v1.20.0   10.0.0.1      ...   5.4.0-42-generic    docker://19.3.13
        worker-1   Ready    worker   10d   v1.20.0   10.0.0.2      ...   5.4.0-42-generic    docker://19.3.13
        worker-2   Ready    worker   10d   v1.24.0   10.0.0.3      ...   5.4.0-42-generic    containerd://1.4.3

        return dict:
        {master-1: dorker,
         worker-1: docker,
        ...}
        or
        {master-1: containerd,
         worker-1: containerd,
        ...}
        """
        cmd = 'kubectl get node -A -o wide'
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg="[ASCEND][ERROR] run cmd: {} failed, reason: {}".format(cmd, err))
        name_index, container_runtime_index = self.extract_indices(out)
        if container_runtime_index is None or name_index is None:
            self.module.fail_json(
                msg="[ASCEND][ERROR] k8s cluster info not illegal. Please check either k8s is already installed or the "
                    "cluster has been built, out:{}".format(out))
        container_runtime_type = dict()
        lines = out.splitlines()
        for line in lines[1:]:  # Skip the first line (header)
            node_name = line.split()[name_index]
            container_runtime = line.split()[container_runtime_index]
            if ContainerRuntimeType.DOCKER in container_runtime:
                container_runtime_type[node_name] = ContainerRuntimeType.DOCKER
            elif ContainerRuntimeType.CONTAINERD in container_runtime:
                container_runtime_type[node_name] = ContainerRuntimeType.CONTAINERD
            else:
                self.module.fail_json(
                    msg="[ASCEND][ERROR] node: {} has unknown container runtime type: {}".format(node_name,
                                                                                                 container_runtime))

        self.facts['container_runtime_type'] = container_runtime_type
        self.messages.append("[ASCEND] set the fact for container runtime type: {}".format(container_runtime_type))

    def _success_exit(self, result=None):
        return self.module.exit_json(changed=True, rc=0, msg="\n".join(self.messages), ansible_facts=self.facts)

    def run(self):
        self.query_container_runtime_type()
        self._success_exit()


if __name__ == '__main__':
    DLPrepareJob().run()
