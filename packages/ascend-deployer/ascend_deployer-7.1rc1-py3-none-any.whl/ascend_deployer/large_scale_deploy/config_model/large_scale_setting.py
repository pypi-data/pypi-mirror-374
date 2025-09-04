from typing import List

from large_scale_deploy.config_model.base import Var
from large_scale_deploy.tools.errors import ConfigrationError


class LargeScaleSetting:

    def __init__(self, sub_group_max_size=200, auto_group_by_subnet=0):
        self.sub_group_max_size = int(sub_group_max_size)
        self.auto_group_by_subnet = int(auto_group_by_subnet)

    @classmethod
    def from_inventory_vars(cls, inventory_vars: List[Var]):
        new_setting = cls()
        for var in inventory_vars:
            if not hasattr(new_setting, var.option.lower()):
                continue
            if not var.value.isdigit():
                raise ConfigrationError(f"large_scale setting option: {var.option} value: {var.value} must be number.")
            setattr(new_setting, var.option.lower(), int(var.value))
        return new_setting
