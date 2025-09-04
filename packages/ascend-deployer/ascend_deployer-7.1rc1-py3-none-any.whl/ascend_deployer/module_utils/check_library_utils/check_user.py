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

from ansible.module_utils.check_output_manager import check_event, set_error_msg
from ansible.module_utils.check_utils import CheckUtil as util


class UserCheck(object):
    """
    Checking user follows the following rules:
    1. User should be root
    2. Normal user could not run program by switch to root user.
    3. user could not run by sudo command.

    The only way running this program is login as a root user.
    """
    MAX_CIRCLES = 8

    def __init__(self, module, error_messages):
        self.module = module
        self.error_messages = error_messages

    def run(self):
        self.check_root()
        self.check_user_privilege_escalation()

        if self.error_messages:
            return self.module.fail_json('\n'.join(self.error_messages))
        return self.module.exit_json(changed=True, rc=0)

    @check_event
    def check_root(self):
        err_msg = "[ASCEND][ERROR] The installation command could only be executed by root user."
        if os.getuid() != 0:
            util.record_error(err_msg, self.error_messages)

    @check_event
    def check_user_privilege_escalation(self):
        """
        Check for user privilege escalation.

        This function gets the parent process ID of the current process and recursively checks each parent process to determine whether there is a privilege escalation using 'su' or 'sudo'.

        Parameters:
        None

        Return value:
        None

        Exception description:
        If it is found that there is a privilege escalation using 'su' or 'sudo', an error message will be logged.
        """
        ppid = os.getppid()
        count = 0
        while ppid != 1 and count < self.MAX_CIRCLES:
            # 使用准确的命令获取指定PID的进程信息
            cmd = "ps -o args= -p {}".format(ppid)
            out = util.run_cmd(cmd, util.GREP_RETURN_CODE)
            if not out.strip():  # 无输出说明进程不存在，退出
                return
            line = out.decode("utf-8").strip()
            # 解析进程参数
            parts = line.split()
            if not parts:
                return
            # 检查是否为su或sudo
            cmd_name = parts[0]
            if cmd_name.endswith("su") or cmd_name.endswith("sudo"):
                util.record_error("[ASCEND][ERROR] The installation command cannot be executed "
                                  "by a user that is switched from running the 'su - root' "
                                  "or by using 'sudo' to escalate privileges.", self.error_messages)
                return
            # 获取父进程的PPID
            cmd_ppid = "ps -o ppid= -p {}".format(ppid)
            ppid_out = util.run_cmd(cmd_ppid, util.GREP_RETURN_CODE)
            ppid = ppid_out.decode("utf-8").strip()
            if not ppid.isdigit():
                return
            ppid = int(ppid)
            count += 1
