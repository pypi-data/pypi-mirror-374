#!/usr/bin/env python3
# coding: utf-8
# Copyright 2025 Huawei Technologies Co., Ltd
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
import shutil
from utils import ROOT_PATH


class ConfigrationError(Exception):
    pass


class Mark:
    EQUAL = "="
    SPACE = " "
    EMPTY = ""


class StrTool:
    _NON_WORD_PATTERN = re.compile(r"[^a-zA-Z0-9]")
    _SAFE_EVAL_SCOPE = {
        '__builtins__': None,
        'int': int,
        'str': str
    }

    @classmethod
    def to_py_field(cls, src_field):
        return cls._NON_WORD_PATTERN.sub("_", src_field)

    @classmethod
    def safe_eval(cls, expr):
        return str(eval(expr, cls._SAFE_EVAL_SCOPE))


class Var:

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_string(self):
        return self.key + Mark.EQUAL + self.value


class Host:

    def __init__(self, ip, params):
        self.ip = ip
        self.params = params

    def to_string(self):
        return self.ip + Mark.SPACE + self.params


class InventoryFilePath:
    OldFilePath = "inventory_file"
    ParsedFilePath = "parsed_inventory_file"


class IPRange:

    def __init__(self, ip_range, step_len):
        self.ip_range = ip_range
        self.step_len = step_len

    def expand_ip_range(self):
        import ipaddress
        start_ip, end_ip = self.ip_range.split('-')
        try:
            start = ipaddress.ip_address(start_ip)
            end = ipaddress.ip_address(end_ip)
        except Exception as e:
            raise ConfigrationError("Parse ip range {} failed: {}.".format(self.ip_range, str(e)))
        if start >= end:
            raise ConfigrationError("Start IP {} must be less than to end IP {}.".format(start, end))
        ip_list = []
        current = start
        while current <= end:
            ip_list.append(str(current))
            current += self.step_len
        if ip_list[-1] != str(end):
            ip_list.append(str(end))
        return ip_list


class HostParams:
    _STEP_LEN_PARAM_KEY = "step_len"
    _INDEX_KEY = "index"
    _IP_KEY = "ip"
    _PARAM_PATTERN = re.compile(r"\{.+?}")

    def __init__(self, params):
        self.params = params
        self.params_dict = self._convert_to_dict(params)

    @staticmethod
    def _convert_to_dict(params):
        """
        Args:
            params: str, example: 'ansible_ssh_user="root" ansible_ssh_pass="test1234" step_len=3'
        Response:
            res: dict, example:{"ansible_ssh_user": "root", "ansible_ssh_pass": "test1234", "step_len": 3}
        """
        param_list = re.split(r"\s+", params)
        res = {}
        for param in param_list:
            if Mark.EQUAL in param:
                parts = param.split(Mark.EQUAL)
                res[parts[0]] = parts[1]
            else:
                res[param] = True
        return res

    def get_step_len(self):
        step_len = self.params_dict.get(self._STEP_LEN_PARAM_KEY, 1)
        try:
            step_len = int(step_len)
        except Exception as e:
            raise ConfigrationError("step_len {} must be int.".format(step_len))

        if step_len <= 0:
            raise ConfigrationError("step_len {} must bigger than 0.".format(step_len))
        return step_len

    def remove_step_len(self):
        if self._STEP_LEN_PARAM_KEY not in self.params:
            return
        self.params = re.sub(r"{}\S*\s*".format(self._STEP_LEN_PARAM_KEY), "", self.params)
        self.params = self.params.strip()
        self.params_dict.pop(self._STEP_LEN_PARAM_KEY)

    def generate_new_params_str_list(self, ips):
        new_params_str_list = []
        self.remove_step_len()
        for index, ip in enumerate(ips):
            new_params_str = self.params
            for key, value in self.params_dict.items():
                if not isinstance(value, str):
                    continue
                search_res_list = self._PARAM_PATTERN.findall(value)
                if not search_res_list:
                    continue
                for search_str in search_res_list:
                    replaced_str = search_str.replace(self._IP_KEY, repr(ip)) \
                        .replace(self._INDEX_KEY, repr(index + 1))
                    parse_str = StrTool.safe_eval(replaced_str[1:-1])
                    new_params_str = new_params_str.replace(search_str, parse_str)
            new_params_str_list.append(Host(ip, new_params_str).to_string())
        return new_params_str_list


class InventoryFile:
    """
    This class is mainly to convert the human-friendly inventory_file to ansible-friendly inventory_file.
    read the old inventory file, parse it and generate a new inventory file.
    An example:
        User could input the ip like this:
        10.10.10.1-10.10.10.3 ansible_ssh_user="root" ansible_ssh_pass="test1234"
        this class will parse it as following:
        10.10.10.1 ansible_ssh_user="root" ansible_ssh_pass="test1234"
        10.10.10.2 ansible_ssh_user="root" ansible_ssh_pass="test1234"
        10.10.10.3 ansible_ssh_user="root" ansible_ssh_pass="test1234"
    """

    _MASTER_SEC = "master"
    _WORKER_SEC = "worker"
    _NPU_NODE_SEC = "npu_node"
    _APPLY_NODE_SEC = "apply"
    _ALL_VARS_SEC = "all:vars"
    _HCCN_SEC = "hccn"
    _HCCN_VARS = "hccn:vars"
    _OTHER_BUILD_IMAGE_SEC = "other_build_image"

    _HOST_SECS = [_MASTER_SEC, _WORKER_SEC, _APPLY_NODE_SEC, _HCCN_SEC, _OTHER_BUILD_IMAGE_SEC, _NPU_NODE_SEC]
    _VAR_SECS = [_HCCN_VARS, _ALL_VARS_SEC]
    _ALL_SECS = _HOST_SECS + _VAR_SECS
    _REQUIRED_SECS = [_MASTER_SEC, _WORKER_SEC]

    OLD_FILE_PATH = os.path.join(ROOT_PATH, InventoryFilePath.OldFilePath)
    PARSED_FILE_PATH = os.path.join(ROOT_PATH, InventoryFilePath.ParsedFilePath)

    config = None

    is_python2 = False
    is_parsed = False

    def __init__(self):
        try:
            from configparser import ConfigParser
        except ImportError:
            self.is_python2 = True
            return
        self.config = ConfigParser(delimiters=(Mark.SPACE, Mark.EQUAL), allow_no_value=True, interpolation=None)
        self.config.optionxform = str
        self.new_config = ConfigParser(delimiters=[Mark.EMPTY], allow_no_value=True)
        self.new_config.optionxform = str
        try:
            self.config.read(self.OLD_FILE_PATH)
        except Exception as e:
            raise ConfigrationError(str(e))

    def _copy(self):
        try:
            shutil.copy(self.OLD_FILE_PATH, self.PARSED_FILE_PATH)
        except Exception as e:
            raise ConfigrationError(
                "Copy {} to {} failed: {}".format(self.OLD_FILE_PATH, self.PARSED_FILE_PATH, str(e)))

    def _parse_hosts(self):
        res = {}
        for host_sec in self._HOST_SECS:
            if not self.config.has_section(host_sec):
                continue
            hosts = []
            for host_item in self.config.items(host_sec):
                if "-" in host_item[0]:
                    host_params = HostParams(host_item[1])
                    ip_range = host_item[0]
                    ips = IPRange(ip_range, host_params.get_step_len()).expand_ip_range()
                    hosts.extend(host_params.generate_new_params_str_list(ips))
                else:
                    hosts.append(Host(*host_item).to_string())
            res[StrTool.to_py_field(host_sec)] = hosts
        return res

    def _parse_vars(self):
        res = {}
        for var_sec in self._VAR_SECS:
            if not self.config.has_section(var_sec):
                continue
            res[StrTool.to_py_field(var_sec)] = [Var(*var).to_string() for var in self.config.items(var_sec)]
        return res

    def _generate_parsed_inventory_file(self, sec_dict):
        for section, _ in self.config.items():
            if section not in self._ALL_SECS:
                continue
            key = StrTool.to_py_field(section)
            sec_values = sec_dict.get(key, [])
            self.new_config.add_section(section)
            for value in sec_values:
                self.new_config.set(section, value)
        with open(self.PARSED_FILE_PATH, "w") as f:
            self.new_config.write(f)

    def parse(self):
        if self.is_parsed:
            return 
        if self.is_python2:
            self._copy()
        else:
            if not self.config.has_section(self._MASTER_SEC) and not self.config.has_section(self._WORKER_SEC):
                raise ConfigrationError("Either a worker group or a master group of host nodes must exist!")
            # sec_dict: {str: [str]}
            sec_dict = self._parse_hosts()
            var_sec_dict = self._parse_vars()
            sec_dict.update(var_sec_dict)
            self._generate_parsed_inventory_file(sec_dict)
        self.is_parsed = True

    def get_parsed_inventory_file_path(self):
        return self.PARSED_FILE_PATH


inventory_file = InventoryFile()
