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
import shlex
import time
import functools

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.check_utils import CallCmdException
from ansible.module_utils import common_info

CARD_CODE_MAP = {"310p": "d500", "910": "d801", "910b": "d802"}


def retry(max_retries, delay=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                if not func(*args, **kwargs):
                    return False
                else:
                    retries += 1
                    time.sleep(delay)
            return True

        return wrapper

    return decorator


class NPUCheck:

    def __init__(self, module, error_messages):
        self.module = module
        self.force_upgrade_npu = module.params.get("force_upgrade_npu")
        self.npu_num = module.params.get("npu_num")
        self.card = util.get_card()
        self.error_messages = error_messages
        self.npu_info = common_info.get_npu_info()

    @check_event
    def check_mcu(self):
        if not self.module.get_bin_path('npu-smi'):
            util.record_error("[ASCEND][ERROR] can not find npu-smi tool.", self.error_messages)
            return
        rc, _, _ = self.module.run_command(shlex.split("npu-smi info -l"))
        if rc != 0:
            util.record_error("[ASCEND][ERROR] can not run npu-smi info -l.", self.error_messages)
        return

    def check_npu(self):
        self.check_npu_health()
        self.check_firmware()
        self.check_driver()

    @check_event
    def check_firmware(self):
        self.check_physical_chain()
        self.check_device()

    @check_event
    def check_driver(self):
        if os.path.isdir("/usr/local/sbin/npu-smi"):
            util.record_error("[ASCEND][ERROR] Maybe you did a wrong container mapping, "
                              "suggest you rm the directory /usr/local/sbin/npu-smi", self.error_messages)
            return
        if os.path.exists("/usr/local/Ascend/driver/version.info"):
            self.check_davinci()

    @retry(3)
    def is_occupied_by_process(self):
        is_occupied = False
        #  check by npu-smi info
        if not self.module.get_bin_path('npu-smi'):
            return False
        try:
            out = util.run_cmd("npu-smi info")
        except CallCmdException as err:
            util.record_error("[ASCEND][[ERROR]] {}".format(str(err)), self.error_messages)
            return False
        lines = [line.decode("utf-8") for line in out.splitlines()]
        check_process = False
        for line in lines:
            if "process id" in line.lower() and "process name" in line.lower():
                check_process = True
                continue
            if check_process:
                if "no running processes" not in line.lower() and len(line.split()) > 4:
                    is_occupied = True
        return is_occupied

    def is_occupied_by_docker(self, file):
        if not self.module.get_bin_path("docker"):
            return False

        cmd = "docker ps -q"
        out = util.run_cmd(cmd)
        if not out:
            return False
        try:
            container_ids = out.decode("utf-8").strip().splitlines()
        except Exception as e:
            raise RuntimeError("Get docker container ids failed, err info: {}".format(e))

        if not container_ids:
            return False

        cmd = "docker inspect {} | grep {}".format(" ".join(container_ids), file)
        out = util.run_cmd(cmd, util.GREP_RETURN_CODE)
        if not out:
            return False

        return True

    def check_davinci(self):
        dev_files = ["/dev/davinci_manager", "/dev/devmm_svm", "/dev/hisi_hdc"]
        cmd = "find /dev -name 'davinci[0-9]*'"
        try:
            out = util.run_cmd(cmd)
            davinci_files = out.splitlines() + dev_files
            if self.is_occupied_by_process():
                util.record_error("[ASCEND][ERROR] Davinci node is occupied by a process, "
                                    "please kill the process.", self.error_messages)
                return
            for file in davinci_files:
                if self.is_occupied_by_docker(file):
                    util.record_error("[ASCEND][ERROR] Davinci node is occupied by docker, "
                                      "please kill the docker container.", self.error_messages)
                    return
        except CallCmdException as err:
            util.record_error("[ASCEND][[ERROR]] {}".format(str(err)), self.error_messages)

    def check_device(self):
        if not os.path.exists("/usr/local/Ascend/driver/version.info"):
            return
        cmd = "npu-smi info"
        try:
            util.run_cmd(cmd)
        except CallCmdException as err:
            if "-8005" in str(err):
                util.record_error("[ASCEND][ERROR] {}. Maybe Device is not started normally, "
                                  "you need to restart the device.".format(str(err)), self.error_messages)
                return
            util.record_error("[ASCEND][[ERROR]] {}".format(str(err)), self.error_messages)

    def check_physical_chain(self):
        if self.npu_num == -1:
            return
        code = CARD_CODE_MAP.get(self.card)
        if not code:
            return
        cmd = "lspci | grep {}".format(code)
        try:
            out = util.run_cmd(cmd)
        except CallCmdException as err:
            util.record_error("[ASCEND][[ERROR]] {}".format(str(err)), self.error_messages)
            return
        if len(out.splitlines()) != int(self.npu_num):
            util.record_error("[ASCEND][ERROR] The physical link is not set up. "
                              " Check the card status or contact Huawei engineers.", self.error_messages)

    @check_event
    def check_npu_health(self):
        if self.force_upgrade_npu:
            return
        if not self.module.get_bin_path("npu-smi"):
            return
        try:
            out = util.run_cmd("npu-smi info")
        except CallCmdException as err:
            util.record_error("[ASCEND][[ERROR]] {}".format(str(err)), self.error_messages)
            return
        lines = [line.decode("utf-8") for line in out.splitlines()]
        for line in lines:
            if "910" in line or "710" in line or "310" in line:
                info = line.split()
                if len(info) < 5:
                    continue
                status = info[4]
                if status != "|" and status != "OK":
                    util.record_error("[ASCEND][[ERROR]] Critical issue with NPU, please check the health of card.",
                                      self.error_messages)
                    return
