import os.path
from configparser import ConfigParser
from typing import List

from large_scale_deploy.config_model.base import Var
from large_scale_deploy.config_model.host import InventoryHostInfo
from large_scale_deploy.tools.errors import ParseError
from large_scale_deploy.tools.str_tool import StrTool
from large_scale_deploy.config_model.large_scale_setting import LargeScaleSetting


class Inventory:
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

    def __init__(self, master: List[InventoryHostInfo] = None,
                 worker: List[InventoryHostInfo] = None,
                 apply_node: List[InventoryHostInfo] = None,
                 hccn: List[InventoryHostInfo] = None,
                 other_build_image: List[InventoryHostInfo] = None,
                 npu_node: List[InventoryHostInfo] = None,
                 all_vars: List[Var] = None,
                 hccn_vars: List[Var] = None,
                 ):
        self.master = master or []
        self.worker = worker or []
        self.apply_node = apply_node or []
        self.hccn = hccn or []
        self.other_build_image = other_build_image or []
        self.npu_node = npu_node or []
        self.all_vars = all_vars or []
        self.hccn_vars = hccn_vars or []

    @classmethod
    def _parse_hosts(cls, config: ConfigParser):
        res = {}
        for host_sec in cls._HOST_SECS:
            if not config.has_section(host_sec):
                continue
            res[StrTool.to_py_field(host_sec)] = InventoryHostInfo.parse_hosts(config.items(host_sec))
        return res

    @classmethod
    def _parse_vars(cls, config: ConfigParser):
        res = {}
        for var_sec in cls._VAR_SECS:
            if not config.has_section(var_sec):
                continue
            res[StrTool.to_py_field(var_sec)] = [Var(*var) for var in config.items(var_sec)]
        return res

    @classmethod
    def parse(cls, file_path):
        if not os.path.exists(file_path):
            raise ParseError(f"File {os.path.abspath(file_path)} not existed.")
        config = ConfigParser(delimiters=(InventoryHostInfo.get_delimiter(), Var.get_delimiter()), allow_no_value=True)
        config.optionxform = str
        config.read(file_path)
        if not config.has_section(cls._MASTER_SEC) and not config.has_section(cls._WORKER_SEC):
            raise ParseError("Either a worker group or a master group of host nodes must exist!")
        host_sec_dict = cls._parse_hosts(config)
        var_sec_dict = cls._parse_vars(config)
        return cls(**host_sec_dict, **var_sec_dict)

    def output(self, new_file_path):
        config = ConfigParser(delimiters=[""], allow_no_value=True)
        config.optionxform = str
        for section in self._ALL_SECS:
            sec_values = getattr(self, StrTool.to_py_field(section), [])
            if not sec_values and section not in self._REQUIRED_SECS:
                continue
            config.add_section(section)
            for value in sec_values:
                config.set(section, str(value))
        new_dir = os.path.dirname(new_file_path)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        with open(new_file_path, "w") as f:
            config.write(f)


class LargeScaleInventory(Inventory):
    _DEPLOY_NODE_SEC = "deploy_node"
    _LARGE_SCALE_SEC = "large_scale"
    _VAR_SECS = Inventory._VAR_SECS + [_LARGE_SCALE_SEC]
    _HOST_SECS = Inventory._HOST_SECS + [_DEPLOY_NODE_SEC]
    _ALL_SECS = _HOST_SECS + _VAR_SECS

    def __init__(self, master: List[InventoryHostInfo] = None, worker: List[InventoryHostInfo] = None,
                 hccn: List[InventoryHostInfo] = None, npu_node: List[InventoryHostInfo] = None,
                 deploy_node: List[InventoryHostInfo] = None, other_build_image: List[InventoryHostInfo] = None,
                 all_vars: List[Var] = None, large_scale: List[Var] = None, hccn_vars: List[Var] = None,
                 apply_node: List[InventoryHostInfo] = None):
        super().__init__(master, worker, apply_node, hccn, other_build_image, npu_node, all_vars, hccn_vars)
        self.deploy_node = self._fill_deploy_nodes(deploy_node or [])
        self.large_scale_setting = LargeScaleSetting.from_inventory_vars(large_scale)

    def _fill_deploy_nodes(self, deploy_nodes: List[InventoryHostInfo]):
        deploy_nodes_set = {deploy_node.ip for deploy_node in deploy_nodes}
        return [worker for worker in self.worker if worker.ip in deploy_nodes_set]

    def to_inventory_copy(self) -> Inventory:
        new_inventory = Inventory()
        for var_sec in Inventory._VAR_SECS:
            if var_sec in Inventory._WORKER_SEC:
                continue
            self_sec = getattr(self, StrTool.to_py_field(var_sec), [])
            setattr(new_inventory, StrTool.to_py_field(var_sec), self_sec)
        for host_sec in Inventory._HOST_SECS:
            self_sec = getattr(self, StrTool.to_py_field(host_sec), [])
            getattr(new_inventory, StrTool.to_py_field(host_sec), []).extend(self_sec)
        return new_inventory
