import ipaddress
import re
from typing import List, Tuple

from large_scale_deploy.config_model.base import KeyValue, StringRepr, Var
from large_scale_deploy.tools.errors import ConfigrationError
from large_scale_deploy.tools.network_tool import NetworkTool
from large_scale_deploy.tools.str_tool import StrTool


class HostParams(StringRepr):

    def __init__(self, params: str):
        self._params_str = params
        self.params_dict = self._parse(params)

    @classmethod
    def _parse(cls, params_str):
        res = {}
        param_list = re.split(r"\s+", params_str)
        for param in param_list:
            if Var.get_delimiter() in param:
                tmp_var = Var.parse(param)
                res[tmp_var.option] = tmp_var.value
            else:
                res[param] = True
        return res

    def get(self, key, default=None):
        return self.params_dict.get(key, default)

    def remove_param(self, param_key: str):
        if param_key not in self._params_str:
            return
        self._params_str = re.sub(rf"{param_key}\S*\s*", "", self._params_str)
        self.params_dict.pop(param_key)

    def __str__(self):
        return self._params_str

    def __getitem__(self, item):
        return self.params_dict[item]


class IpRangeHostParams(HostParams):
    _STEP_LEN_PARAM_KEY = "step_len"
    _INDEX_KEY = "index"
    _IP_KEY = "ip"
    _PARAM_PATTERN = re.compile(r"\{.+?}")

    def get_step_len(self):
        step_len = self.params_dict.get(self._STEP_LEN_PARAM_KEY, 1)
        if (not isinstance(step_len, int) and
                not (isinstance(step_len, str) and step_len.isdigit())):
            raise ConfigrationError(f"step_len {step_len} must be int.")
        step_len = int(step_len)
        if step_len <= 0:
            raise ConfigrationError(f"step_len {step_len} must bigger than 0.")
        return step_len

    def remove_step_len(self):
        self.remove_param(self._STEP_LEN_PARAM_KEY)

    def calc_expr(self, ip, index):
        new_params_str = self._params_str
        for key, value in self.params_dict.items():
            if not isinstance(value, str):
                continue
            search_res_list = self._PARAM_PATTERN.findall(value)
            if not search_res_list:
                continue
            for search_str in search_res_list:
                replaced_str = search_str.replace(self._IP_KEY, repr(ip)) \
                    .replace(self._INDEX_KEY, repr(index))
                parse_str = StrTool.safe_eval(replaced_str[1:-1])
                new_params_str = new_params_str.replace(search_str, parse_str)
        return new_params_str


class InventoryHostInfo(KeyValue):

    def __init__(self, ip, params=""):
        super().__init__(ip, params)
        self.ip = ip
        self.int_ip = NetworkTool.ip_to_int(ip)
        self.params = HostParams(params)

    def to_info_dict(self):
        res = {"ip": self.ip}
        res.update(self.params.params_dict)
        return res

    @classmethod
    def get_delimiter(cls):
        return " "

    @staticmethod
    def _parse_ip_range_host_params(ip_range: str, params_str: str):
        res = []
        ip_range_host_params = IpRangeHostParams(params_str)
        step_len = ip_range_host_params.get_step_len()
        ip_range_host_params.remove_step_len()
        for index, ip in enumerate(NetworkTool.expand_ip_range(ip_range, step_len)):
            new_params_str = ip_range_host_params.calc_expr(ip, str(index + 1))
            res.append(InventoryHostInfo(ip, new_params_str))
        return res

    @staticmethod
    def parse_hosts(host_items: List[Tuple[str, str]]):
        hosts = []
        for host_item in host_items:
            if "-" in host_item[0]:
                hosts.extend(InventoryHostInfo._parse_ip_range_host_params(host_item[0], host_item[1]))
            else:
                ipaddress.ip_address(host_item[0])
                hosts.append(InventoryHostInfo(*host_item))
        return sorted(hosts, key=lambda host_info: host_info.int_ip)
