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
import glob
import itertools
import shlex
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import common_info
from ansible.module_utils.common_info import DeployStatus, SceneName
from ansible.module_utils.common_utils import McuMultiProcess


class McuInstallation:
    def __init__(self):
        module = AnsibleModule(
            argument_spec=dict(
                resource_dir=dict(type="str", required=True),
                cus_npu_info=dict(type="str", required=True),
                ansible_run_tags=dict(type="list", required=True),
            )
        )
        self.resource_dir = os.path.expanduser(module.params["resource_dir"])
        self.cus_npu_info = module.params.get("cus_npu_info", "")
        ansible_run_tags = module.params.get("ansible_run_tags", [])
        self.mcu_file_path = None
        self.auto_mode_flag = "auto" in ansible_run_tags
        self.module = module
        self.npu_info = common_info.get_npu_info()
        self.messages = []

    def _success_exit(self, result=None):
        return self.module.exit_json(changed=True, rc=0, stdout="\n".join(self.messages), result=result or {},
                                     fail_flag=False)

    def run(self):
        try:
            if self._process_mcu():
                self.messages.append(
                    "[ASCEND][WARNING] Operations on the MCU are not allowed during the upgrade process "
                    "and within 2 minutes after it takes effect. "
                    "After the new MCU version takes effect, "
                    "the main and backup areas of the MCU will be synchronized internally. "
                    "If you need to upgrade again, please wait 5 minutes before operating again.")
            return self._success_exit()
        except Exception as e:
            self.messages.append(str(e))
            return self.module.exit_json(stdout="\n".join(self.messages), fail_flag=True)

    def _find_mcu_file(self, path):
        """
            Find mcu file by patterns '*hdk*mcu*.hpm' or '*hdk*mcu*.bin'.

            Args:
                path : Package path like '/root/resources/run_from_a310p_zip/'.

            Returns:
                matched_files[0] or '': If there are multiple matches, only one is returned. If there is no match,
                                        an empty string is returned.

            Examples:
                >>> self._find_mcu_file('/root/resource/run_from_a310_zip/'])
                'matched.hpm'
            """
        patterns = [os.path.join(path, ext) for ext in ['*hdk*mcu*.hpm', '*hdk*mcu*.bin']]
        matched_files = list(itertools.chain.from_iterable(glob.glob(pattern) for pattern in patterns))
        self.messages.append("find files: " + ",".join(matched_files))
        if len(matched_files) > 0:
            return matched_files[0]
        return ""

    def _run_command(self, command, ok_returns=None):
        self.messages.append("calling " + command)
        return_code, out, err = self.module.run_command(shlex.split(command))
        output = out + err
        if not ok_returns:
            ok_returns = [0]
        if return_code not in ok_returns:
            raise Exception("calling {} failed on {}: {}".format(command, return_code, output))
        self.messages.append("output of " + command + " is: " + str(output))
        return output

    def _auto_skip(self, messages):
        self.messages.append(messages)
        return self._success_exit({DeployStatus.DEPLOY_STATUS: DeployStatus.SKIP})

    def _process_mcu(self):
        if os.getuid() != 0:
            if self.auto_mode_flag:
                return self._auto_skip("[ASCEND] Bypass mcu installation as non-root user")
            raise Exception("[ASCEND] None-root user cannot upgrade mcu!")

        if not self.npu_info.get("scene") or (self.npu_info.get("scene") == 'unknown'):
            if self.auto_mode_flag:
                return self._auto_skip("[ASCEND][WARNING] Can not detect npu, bypass mcu upgrade")
            raise Exception("[ASCEND][WARNING] Can not detect npu, exit!")

        if not self.module.get_bin_path('npu-smi'):
            if self.auto_mode_flag:
                return self._auto_skip("[ASCEND][WARNING] Can not find npu-smi bin, bypass mcu upgrade")
            raise Exception("[ASCEND][WARNING] Can not find npu-smi bin, exit!")

        self._find_mcu_files()
        if not self.mcu_file_path:
            if self.auto_mode_flag:
                return self._auto_skip("[ASCEND][WARNING] Can not find mcu file, bypass mcu upgrade")
            raise Exception("[ASCEND][WARNING] Can not find mcu file, exit!")

        return self._do_upgrade_mcu()

    def _find_mcu_files(self):
        npu_scene = self.npu_info.get("scene")
        # a910b a310b only has uniform package, equal to scene name
        if npu_scene in (SceneName.A300I, SceneName.A300IDUO):
            npu_scene = "normalize310p"
        if npu_scene == SceneName.Train:
            npu_scene = "normalize910"
        package_path = common_info.get_scene_dict(os.path.expanduser(self.resource_dir)).get(npu_scene)
        mcu_path = self._find_mcu_file(package_path)
        self.mcu_file_path = mcu_path or self.mcu_file_path

    def _do_upgrade_mcu(self):

        npu_id_info = self._run_command("npu-smi info -l")
        """     
        eg::
                Total Count                    : 1

                NPU ID                         : 8
                Product Name                   : IT21PDDA01
                Serial Number                  : 033VNY10MB000071
                Chip Count                     : 1
            A3:
                Total Count                    : 8

                NPU ID                         : 0
                Chip Count                     : 2
                ...
        """
        npu_id_list = []
        for line in npu_id_info.splitlines():
            if 'NPU ID' in line:
                npu_id = line.split(':')[-1].strip()
                if npu_id.isdigit():
                    npu_id_list.append(int(npu_id))

        mcu_multprocess = McuMultiProcess(npu_id_list, self.module, self.mcu_file_path)
        results = mcu_multprocess.multi_run_command('upgrade')
        for device_id in sorted(results.keys()):
            result = results[device_id]
            self.messages.append("----------------------------------------Device {0}: {1}"
                                 "--------------------------------------------".format(
                device_id,
                'Success' if result.get('success') else 'Failed'
            ))
            if result.get('output'):
                self.messages.append("Output:{}".format(result.get('output')))
            if result.get('error'):
                self.messages.append("Error:{}".format(result.get('error')))
            self.messages.append("Upgrade return code: {}".format(result.get('upgrade_rc')))
            self.messages.append("Activate return code: {}".format(result.get('activate_rc')))

        # 检查是否所有设备都成功
        all_success = all(r.get('success') for r in results.values())
        self.messages.append(
            "\n----------------------------------------Overall status: {0}"
            "--------------------------------------------".format(
                'All devices succeeded' if all_success else 'Some devices failed'
            ))
        if not all_success:
            self.messages.append(
                "If it is not the target version after the upgrade or the upgrade fails, please upgrade again. "
                "If the upgrade still fails, please record the fault symptoms and operation steps, "
                "and contact Huawei technical support for resolution.")
            raise Exception("[ASCEND][WARNING] MCU upgrade failed, exit!")
        return True


def main():
    McuInstallation().run()


if __name__ == "__main__":
    main()
