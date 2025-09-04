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
import json
import os
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass
from ansible.module_utils.basic import AnsibleModule

HOME_PATH = os.path.expanduser('~')
DEPLOY_INFO_OUTPUT_DIR = os.path.join(HOME_PATH, ".ascend_deployer", "deploy_info")
CHECK_RES_OUTPUT_PATH = os.path.join(DEPLOY_INFO_OUTPUT_DIR, "check_res_output.json")


class OutputCheck:
    def __init__(self):
        module = AnsibleModule(
            argument_spec=dict(
                check_results=dict(type="list", required=True)
            )
        )
        self.check_results = module.params.get('check_results')
        self.module = module

    def run(self):
        try:
            check_output = self.format_result_to_json()
            self.generate_check_result_json(check_output)
            return self.module.exit_json(changed=True, rc=0, fail_flag=False)
        except Exception as e:
            return self.module.fail_json(msg=str(e), stdout=str(e), fail_flag=True)

    def format_result_to_json(self):
        """
        Format check result to json
        This function convert the JSON content of each server into a unified JSON format.
        Examples:
        check_results = [
            {
                "192.168.1.1": [
                    {
                        "check_status": "failed",
                        "error_msg": "Check card failed: [ASCEND] A300i - pro has no support for
                                    MTOS_22.03LTS - SP4_aarch64 on this device",
                        "check_item": "check_card",
                        "desc_en": "Check NPU card compatibility",
                        "desc_zh": "检查NPU卡兼容性",
                        "tip_en": "",
                        "tip_zh": ""
                    }
                ]
            }
        ]

        check_output = {
            "CheckList": [
                {
                    "check_item": "check_card",
                    "desc_en": "Check NPU card compatibility",
                    "desc_zh": "检查NPU卡兼容性",
                    "tip_en": "",
                    "tip_zh": ""
                }
            ],
            "HostCheckResList": {
                "192.168.1.1": {
                    "check_res_list": [
                        {
                            "check_item": "check_card",
                            "status": "failed",
                            "error_msg": "Check card failed: [ASCEND] A300i - pro has no support for
                                    MTOS_22.03LTS - SP4_aarch64 on this device"
                        }
                    ]
                }
            }
        }
        """
        check_list_items_dict = dict()
        check_list = []
        host_check_res_dict = dict()
        for host_entry in self.check_results:
            for ip, checks in host_entry.items():
                if checks:
                    # 处理localhost的result
                    if ip == "localhost":
                        checks = next(iter(checks.values()), {})
                    # 初始化当前 IP 的检查结果列表
                    host_check_res_dict.setdefault(ip, {"check_res_list": []})
                    host_check_res_item_list = dict()
                    for check in checks:
                        check_item = check.get("check_item", "")

                        # 处理CheckList（去重）
                        if check_item not in check_list_items_dict:
                            check_list_items_dict[check_item] = {
                                "check_item": check_item,
                                "desc_en": check.get("desc_en", ""),
                                "desc_zh": check.get("desc_zh", ""),
                                "tip_en": check.get("tip_en", ""),
                                "tip_zh": check.get("tip_zh", ""),
                                "help_url": check.get("help_url", "")
                            }
                            check_list.append(check_list_items_dict[check_item])
                        if check_item not in host_check_res_item_list:
                            # 处理当前 IP 的检查结果
                            host_check_result = {
                                "check_item": check_item,
                                "status": check.get("check_status", "")
                            }

                            # 如果状态为 failed，则添加 error_msg
                            if check.get("check_status", "") == "failed":
                                host_check_result["error_msg"] = check.get("error_msg", "")
                            host_check_res_item_list[check_item] = host_check_result
                            host_check_res_dict[ip]["check_res_list"].append(host_check_result)
        # 构建最终结果
        check_output = {
            "CheckList": check_list,
            "HostCheckResList": host_check_res_dict
        }
        return check_output

    @staticmethod
    def generate_check_result_json(check_output):
        if not os.path.exists(DEPLOY_INFO_OUTPUT_DIR):
            os.makedirs(DEPLOY_INFO_OUTPUT_DIR)
        with open(CHECK_RES_OUTPUT_PATH, "w") as output_fs:
            json.dump(check_output, output_fs, indent=4, ensure_ascii=False)


def main():
    OutputCheck().run()


if __name__ == "__main__":
    main()
