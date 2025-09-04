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


class DevicePluginInstaller(Installer):
    component_name = 'device-plugin'

    def __init__(self):
        super(DevicePluginInstaller, self).__init__()
        self.all_yaml_files = []

    def get_yaml_path(self):
        yaml_files = []
        for root, _, files in os.walk(self.extract_dir):
            for filename in files:
                if filename.endswith('.yaml') and "1usoc" not in filename and "volcano" in filename:
                    yaml_files.append(os.path.join(root, filename))
        if not yaml_files:
            self.module.fail_json('failed to find the yaml about volcano in {}'.format(self.extract_dir))
        self.all_yaml_files.extend(sorted(yaml_files, reverse=self.use_new_k8s))
        matching_yaml_files = []
        for line in self.iter_cmd_output('lspci'):
            if 'Processing accelerators' in line:
                if 'Device d500' in line:
                    substring = 'device-plugin-310P-'
                    matching_yaml_files = [file for file in yaml_files if substring in file]
                elif 'Device d100' in line or 'Device d107' in line:
                    substring = 'device-plugin-310-'
                    matching_yaml_files = [file for file in yaml_files if substring in file]
                elif 'Device d801' in line or 'Device d802' in line or 'Device d803' in line:
                    substring = 'device-plugin-volcano-'
                    matching_yaml_files = [file for file in yaml_files if substring in file]
        if not matching_yaml_files:
            matching_yaml_files.append(yaml_files[0])
        return matching_yaml_files[0]

    def get_modified_yaml_contents(self, yaml_file_path):
        with open(yaml_file_path) as f:
            return f.readlines()

    def create_log_dir(self):
        """ do jobs such as creating log dir and logrotate file """
        log_path = os.path.join(self.dl_log, "devicePlugin")
        if not os.path.exists(log_path):
            os.makedirs(log_path, 0o750)
            os.chown(log_path, self.user_id, self.group_id)

    def apply_yaml(self):
        if not os.path.exists(self.yaml_dir):
            os.makedirs(self.yaml_dir, 0o755)
        accelerator_labels = set()
        for labels in self.labels.values():
            for label in labels.values():
                if 'huawei-Ascend' in label:
                    accelerator_labels.add(label.replace('huawei-Ascend', ''))
        for yaml_file in self.all_yaml_files:
            device_met = False
            for device_type in accelerator_labels:
                if device_type == "910" and "device-plugin-volcano" in yaml_file:
                    device_met = True
                    break
                if device_type + '-volcano' in yaml_file:
                    device_met = True
                    break
            if not device_met:
                continue
            basename = os.path.basename(yaml_file)
            blank_yaml_path = os.path.join(self.yaml_dir, basename)
            with open(blank_yaml_path, 'w') as f:
                f.writelines(self.get_modified_yaml_contents(yaml_file))
            cmd = 'kubectl delete -f {}'.format(blank_yaml_path)
            self.module.run_command(cmd)
            cmd = 'kubectl apply -f {}'.format(blank_yaml_path)
            self.module.run_command(cmd, check_rc=True)
            self.module.log(msg='apply yaml: {} for component: {}'.format(blank_yaml_path, self.component_name))


if __name__ == '__main__':
    DevicePluginInstaller().run()
