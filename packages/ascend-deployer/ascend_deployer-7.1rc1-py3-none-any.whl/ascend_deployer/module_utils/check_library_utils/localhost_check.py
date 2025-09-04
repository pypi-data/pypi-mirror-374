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
from ansible.module_utils.common_utils import run_command, get_cmd_color_str

IPV4_PATTERN = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
IPV6_PATTERN = re.compile(r'inet6 ([a-fA-F0-9:]+)')


class LocalhostCheck(object):

    def __init__(self, module, error_messages):
        self.module = module
        self.error_messages = error_messages
        self.master_groups = self.module.params['master_groups']
        self.master0_arch = self.module.params['master0_arch']
        self.worker0_arch = self.module.params['worker0_arch']
        self.groups = self.module.params['groups']

    @check_event
    def check_dl_diff_arch(self):
        """
        Check dl different arch
        Check the heterogeneous scenario: Master0 and worker0 exist and are heterogeneous.
        You need to fill in the other_build_image item in the inventory.
        """
        if not self.master0_arch or not self.worker0_arch:
            return
        if self.master0_arch != self.worker0_arch and (
                'other_build_image' not in self.groups or not self.groups.get('other_build_image')):
            msg = "Master and worker have different architectures. " \
                  "The 'other_build_image' group is required but is empty."
            util.record_error(msg, self.error_messages)

    @check_event
    def check_mtos_kernel_devel_pkg(self):
        """
        Check mtos kernel devel pkg
        1. Check whether there is the MTOS_22.03LTS-SP4_aarch64 directory in the resources folder.
        2. Search kernel-devel-5.10.0-218.0.0.mt20240808.560.mt2203sp4.aarch64.rpm in the
            MTOS_22.03LTS-SP4_aarch64 directory.
        """
        mtos_sys_dir = self.module.params.get("mtos_sys_dir")
        package_pattern = 'kernel-devel.*mt.*mt.*aarch64.rpm'

        # 检查目录是否存在
        if not os.path.isdir(mtos_sys_dir):
            util.record_error("Directory {} does not exist".format(mtos_sys_dir), self.error_messages)
            return

        matched_files = []
        try:
            # 遍历目录中的文件并匹配正则表达式
            for filename in os.listdir(mtos_sys_dir):
                file_path = os.path.join(mtos_sys_dir, filename)
                if os.path.isfile(file_path) and re.fullmatch(package_pattern, filename):
                    matched_files.append(file_path)
        except Exception as e:
            util.record_error("Error accessing directory {}: {}".format(mtos_sys_dir, str(e)), self.error_messages)
            return

        # 如果没有找到匹配的文件则失败
        if not matched_files:
            msg = (
                "MTOS needs to use the kernel-devel package that is not available on the public network. "
                "If you need to use it, please download the dependencies and replace kernel-devel with "
                "the kernel-devel-5.10.0-218.0.0.mt20240808.560.mt2203sp4.aarch64.rpm package "
                "after decompressing the image."
            )
            util.record_error(msg, self.error_messages)

    def check_dl_executor(self):
        local_all_ips = self.get_local_all_ips()
        if bool((set(local_all_ips) & set(self.master_groups))) or 'localhost' in self.master_groups:
            message = get_cmd_color_str(
                '[ASCEND][WARNING]: It is recommended to select non-master nodes for running execution task',
                'yellow')
            # It is just an alert, not an error, so there is no need to add the check_event decorator.
            self.module.warn(message)

    def get_local_all_ips(self):
        # Run the ip addr or ifconfig command to obtain network interface information.
        ips_list = []
        try:
            lines, _ = run_command(self.module, 'ip addr')
        except FileNotFoundError:
            lines, _ = run_command(self.module, 'ifconfig')
        for line in lines.splitlines():
            line = line.strip()
            if 'inet' not in line or ' ' not in line:
                continue
            for pattern in [IPV4_PATTERN, IPV6_PATTERN]:
                search = pattern.search(line)
                if search:
                    ips_list.append(search.group(1))
                    break
        return ips_list
