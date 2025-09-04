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
import os
import platform

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.common_utils import compare_version


class FrameCheck:

    def __init__(self, module, npu_info, error_messages):
        self.tags = module.params.get("tags")
        self.python_version = module.params.get("python_version")
        self.packages = module.params.get("packages")
        self.error_messages = error_messages
        self.npu_info = npu_info
        self.resources_dir = os.path.join(module.params.get("ascend_deployer_work_dir"), "resources")

    def _get_tfadaptor_path(self):
        tensorflow_pkg = self.packages.get("tensorflow") or self.packages.get("tensorflow_cpu")
        if not tensorflow_pkg:
            return ""
        tensorflow_info = tensorflow_pkg.split('-')
        tensorflow_version = ""
        if len(tensorflow_info) > 1:
            tensorflow_version = tensorflow_info[1]
        tfadaptor_pkg = ""
        if tensorflow_version == "2.6.5":
            tfadaptor_pkg = self.packages.get("npu_device")
        elif tensorflow_version == "1.15.0":
            tfadaptor_pkg = self.packages.get("npu_bridge")
        return tfadaptor_pkg

    @check_event
    def check_torch(self):
        scene = self.npu_info.get("scene", "")

        if scene == "a910b":
            self.check_kernels("910b")
        elif scene == "a910_93":
            self.check_kernels("910_93")

        if not self._is_install_toolkit() and not self._is_install_nnae():
            util.record_error("[ASCEND][ERROR] Please install toolkit or nnae before install pytorch.",
                              self.error_messages)

    def check_kernels(self, scene):
        # 1. Check whether kernels have been installed.
        toolkit_kernels_path = "/usr/local/Ascend/ascend-toolkit/latest/opp" \
                               "/built-in/op_impl/ai_core/tbe/kernel/ascend{}/".format(scene)
        nnae_kernels_path = "/usr/local/Ascend/nnae/latest/opp" \
                            "/built-in/op_impl/ai_core/tbe/kernel/ascend{}/".format(scene)
        if os.path.exists(toolkit_kernels_path) or os.path.exists(nnae_kernels_path):
            return
        # 2. Check whether the installed tags contain kernels, pytorch_dev, or pytorch_run.
        skip_tags = {"pytorch_dev", "pytorch_run", "kernels"}
        if skip_tags & set(self.tags):
            return
        # 3. Check whether the kernels package exists during installation in the auto scenario.
        kernels_pkg = self.packages.get("kernels")
        if "auto" in self.tags and kernels_pkg:
            return
        # 4. In other cases.
        util.record_error(
            "[ASCEND][ERROR] For Atlas A2 training series products, please install kernels before install pytorch.",
            self.error_messages)

    @check_event
    def check_tensorflow(self):
        version = self.python_version.replace("python", "")
        if compare_version(version, "3.10.0") >= 0:
            util.record_error("[ASCEND][ERROR] Tensorflow does not support python3.10.* and above. "
                              "Please use an earlier python version.", self.error_messages)

        install_tfplugin_tags = {"tfplugin", "tensorflow_dev", "tensorflow_run", "auto"}
        tfplugin_pkg = self.packages.get("tfplugin")
        tfadaptor_pkg = self._get_tfadaptor_path()
        tfplugin_path = "/usr/local/Ascend/tfplugin/set_env.sh"
        """
        CANN 8.0.0之前，TensorFlow需要tfplugin+toolkit或tfplugin+nnae组合
        CANN 8.0.0及之后，提供tfadaptor的whl包代替tfplugin，whl包跟随tensorflow一起下载
        """
        install_tf = (install_tfplugin_tags.intersection(set(self.tags)) and tfplugin_pkg
                      or os.path.exists(tfplugin_path) or tfadaptor_pkg)
        if not self._is_install_toolkit() and not self._is_install_nnae():
            util.record_error("[ASCEND][ERROR] Please install toolkit or nnae before install tensorflow.",
                              self.error_messages)
        if not install_tf:
            util.record_error(
                "[ASCEND][ERROR] Please install tfplugin or download tfadaptor before install tensorflow.",
                self.error_messages)

    @check_event
    def check_mindspore(self):
        version = self.python_version.replace("python", "")
        if compare_version(version, "3.12.0") >= 0:
            util.record_error("[ASCEND][ERROR] Mindspore does not support python3.12.* and above. "
                              "Please use an earlier python version.", self.error_messages)

        if not self._is_install_toolkit() and not self._is_install_nnae():
            util.record_error("[ASCEND][ERROR] Please install toolkit or nnae before install mindspore.",
                              self.error_messages)

    def _is_install_toolkit(self):
        install_toolkit_tags = {"toolkit", "auto", "mindspore_scene", "tensorflow_dev", "pytorch_dev"}
        toolkit_pkg = self.packages.get("toolkit")
        toolkit_path = "/usr/local/Ascend/ascend-toolkit/set_env.sh"
        install_toolkit = ((install_toolkit_tags.intersection(set(self.tags)) and toolkit_pkg)
                           or os.path.exists(toolkit_path))
        return install_toolkit

    def _is_install_nnae(self):
        install_nnae_tags = {"nnae", "auto", "tensorflow_run", "pytorch_run"}
        nnae_pkg = self.packages.get("nnae")
        nnae_path = "/usr/local/Ascend/nnae/set_env.sh"
        install_nnae = (install_nnae_tags.intersection(set(self.tags)) and nnae_pkg) or os.path.exists(nnae_path)
        return install_nnae