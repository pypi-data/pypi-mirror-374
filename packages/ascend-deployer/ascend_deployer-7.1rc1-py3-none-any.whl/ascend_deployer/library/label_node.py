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
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import common_info, path_manager, common_utils, compatibility_config


class LabelNode:
    common_master_labels = {'masterselector': 'dls-master-node'}
    common_worker_labels = {
        'node-role.kubernetes.io/worker': 'worker',
        'workerselector': 'dls-worker-node'
    }

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                step=dict(type='str', required=True),
                ansible_run_tags=dict(type='list'),
                node_name=dict(type='str'),
                master_node=dict(type='bool'),
                worker_node=dict(type='bool'),
                nodes_label=dict(type='dict'),
                group_count=dict(type='int'),
                noded_label=dict(type='str')
            )
        )
        self.step = self.module.params['step']
        self.tags = self.module.params['ansible_run_tags']
        self.node_name = self.module.params['node_name']
        self.master_node = self.module.params['master_node']
        self.worker_node = self.module.params['worker_node']
        self.nodes_label = self.module.params['nodes_label']
        self.sub_groups = self.module.params['group_count']
        self.noded_label = self.module.params['noded_label']
        self.arch = platform.machine()
        self.facts = dict()
        self.label_yaml_dir = os.path.join(path_manager.TmpPath.DL_YAML_DIR, "label")
        if not os.path.exists(self.label_yaml_dir):
            os.makedirs(self.label_yaml_dir)

    def _get_noded_label(self):
        if self.noded_label == "on" or "noded" in self.tags or "dl" in self.tags:
            return {'nodeDEnable': 'on'}
        return {}

    def _get_device_plugin_label(self):
        labels = {}
        if self.arch == 'x86_64':
            labels.update({'host-arch': 'huawei-x86'})
        else:
            labels.update({'host-arch': 'huawei-arm'})
        for line in self.iter_cmd_output('lspci'):
            if 'Processing accelerators' in line:
                if 'Device d100' in line:
                    labels.update({'accelerator': 'huawei-Ascend310'})
                if 'Device d500' in line:
                    labels.update({'accelerator': 'huawei-Ascend310P'})
                if 'Device d801' in line or 'Device d802' in line or 'Device d803' in line:
                    labels.update({'accelerator': 'huawei-Ascend910'})
        card_nums = 0
        npu_id = '0'
        chip_id = '0'
        for line in self.iter_cmd_output('npu-smi info -m'):
            if 'Ascend' in line and len(line.split(None, 2)) == 3:
                card_nums += 1
                if card_nums == 1:
                    npu_id, chip_id, _ = line.split(None, 2)
        board_id = ''
        for line in self.iter_cmd_output('npu-smi info -t board -i {} -c {}'.format(npu_id, chip_id)):
            if 'Board' in line and ':' in line:
                board_id = line.strip().split(':')[1].strip().lower()
                break
        if board_id in common_info.Atlas_800:
            if card_nums == 8:
                labels.update({'accelerator-type': 'module'})
            elif card_nums == 4:
                labels.update({'accelerator-type': 'half'})
        elif board_id in common_info.Atlas_800_A2 + common_info.Atlas_900_A2_PoD:
            labels.update({'accelerator-type': 'module-910b-8'})
        elif board_id in common_info.Atlas_200T_A2_Box16:
            labels.update({'accelerator-type':'module-910b-16'})
        elif board_id in common_info.Atlas_300T:
            labels.update({'accelerator-type': 'card'})
        elif board_id in common_info.Atlas_300T_A2:
            labels.update({'accelerator-type': 'card-910b-2'})
        elif board_id in common_info.Atlas_200T_A3_Box8 + common_info.Atlas_800I_A3:
            labels.update({'accelerator-type': 'module-a3-16'})

        npu_info = common_info.get_npu_info()
        if npu_info.get('card') == compatibility_config.Hardware.ATLAS_800I_A2:
            labels.update({'server-usage': 'infer'})
        return labels

    def iter_cmd_output(self, cmd):
        if not self.module.get_bin_path(cmd.split()[0]):
            return
        rc, out, err = self.module.run_command(cmd)
        if out:
            for line in out.splitlines():
                yield line

    def get_labels(self):
        node_label = dict()
        if self.master_node:
            node_label.update(self.common_master_labels)
        if self.worker_node:
            node_label.update(self.common_worker_labels)
            node_label.update(self._get_device_plugin_label())
            node_label.update(self._get_noded_label())

        self.facts['node_label'] = {self.node_name: node_label}
        self.module.exit_json(changed=True, msg='{} successfully'.format(self.step), ansible_facts=self.facts)

    def save_labels(self):
        """
        将标签信息转换成yaml，保存到worker[0]
        """
        label_yaml = os.path.join(self.label_yaml_dir, "label_node.json")
        nodes = []
        for node_name, node_label in self.nodes_label.items():
            node_data = {
                "apiVersion": "v1",
                "kind": "Node",
                "metadata": {
                    "name": node_name,
                    "labels": node_label
                }
            }
            nodes.append(node_data)
        with open(label_yaml, 'w') as f:
            f.write(json.dumps(nodes))
        self.module.exit_json(changed=True, msg='{} successfully'.format(self.step), ansible_facts=self.facts)

    def label_node(self):
        """
        将各个集群的标签信息的yaml文件合并成一个文件label_nodes.yaml，
        通过kubectl apply -f label_nodes.yaml给节点打标签
        """
        groups_json_dir = os.path.join(self.label_yaml_dir, "groups")
        groups_json = os.listdir(groups_json_dir)
        if 0 < len(groups_json) < self.sub_groups:
            self.module.exit_json(changed=False, rc=0, msg="Did not get all labels, skipped.")
        label_yaml = os.path.join(self.label_yaml_dir, "label_nodes.yaml")
        with open(label_yaml, 'w') as write_file:
            for groups_name in groups_json:
                group_json_path = os.path.join(groups_json_dir, groups_name, "label_node.json")
                with open(group_json_path, 'r') as read_file:
                    data = json.load(read_file)
                    common_utils.dump_all_to_yaml(data, write_file)
        cmd = 'kubectl apply -f {}'.format(label_yaml)
        self.module.run_command(cmd, check_rc=True)
        self.module.log(msg='apply yaml: {} for label nodes'.format(label_yaml))
        self.module.exit_json(changed=True, msg='{} successfully'.format(self.step), ansible_facts=self.facts)

    def run(self):
        steps = {
            'get_label': self.get_labels,
            'save_label': self.save_labels,
            'label': self.label_node
        }
        if self.step not in steps:
            self.module.fail_json(msg='invalid step: {}, choose from {}'.format(self.step, list(steps)))
        steps.get(self.step)()

if __name__ == '__main__':
    LabelNode().run()
