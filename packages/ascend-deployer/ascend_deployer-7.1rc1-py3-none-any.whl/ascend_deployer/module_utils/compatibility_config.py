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
from itertools import chain

try:
    from ansible.module_utils.common_info import OSName
except ImportError:
    class OsNameTag:
        @staticmethod
        def __getattr__(name):
            return name.lower()


    OSName = OsNameTag()


class HardwareModel:
    ATLAS_200I_SOC_A1 = "Atlas 200I Soc A1"
    ATLAS_500_PRO_MODEL_3000 = "Atlas 500 Pro (Model 3000)"


EOL_CARD = []
EOL_MODEL = [HardwareModel.ATLAS_200I_SOC_A1]


class VersionConstraint:
    START_VERSION = "start_version"


class Hardware:
    A300_3010 = "A300-3010"
    A300_3000 = "A300-3000"
    A300I_PRO = "A300i-pro"
    A300I_DUO = "A300i-duo"
    A200I_A2 = "A200i-a2"
    A300T_9000 = "A300T-9000"
    A900T = "A900T"
    A300T_A2 = "A300t-a2"
    ATLAS_800I_A2 = "Atlas 800I A2"
    ATLAS_800I_A3 = "Atlas 800I A3"
    ATLAS_900_A3_POD = "Atlas 900 A3 Pod"


class Tags:
    SYS_PKG = "sys_pkg"
    PYTHON = "python"
    DOCKER_IMAGES = "docker_images"
    DRIVER = "driver"
    FIRMWARE = "firmware"
    NPU = "npu"
    MCU = "mcu"
    TFPLUGIN = "tfplugin"
    NNAE = "nnae"
    NNRT = "nnrt"
    TOOLKIT = "toolkit"
    KERNELS = "kernels"
    TOOLBOX = "toolbox"
    FAULT_DIAG = "fault-diag"
    DL = "dl"
    VOLCANO = "volcano"
    HCCL_CONTROLLER = "hccl-controller"
    ASCEND_DEVICE_PLUGIN = "ascend-device-plugin"
    NODED = "noded"
    NPU_EXPORTER = "npu-exporter"
    ASCEND_DOCKER_RUNTIME = "ascend-docker-runtime"
    ASCEND_OPERATOR = "ascend-operator"
    CLUSTERD = "clusterd"
    RESILIENCE_CONTROLLER = "resilience-controller"
    PYTORCH = "pytorch"
    MINDSPORE = "mindspore"
    MINDSPORE_SCENE = "mindspore_scene"
    TENSORFLOW = "tensorflow"
    PYTORCH_DEV = "pytorch_dev"
    PYTORCH_RUN = "pytorch_run"
    TENSORFLOW_DEV = "tensorflow_dev"
    TENSORFLOW_RUN = "tensorflow_run"
    AUTO = "auto"
    OFFLINE_DEV = "offline_dev"
    OFFLINE_RUN = "offline_run"
    MINDIO = "mindio"
    MINDIE_IMAGE = "mindie_image"

    SYS_DEP_TAGS = {
        SYS_PKG,
        PYTHON,
        DOCKER_IMAGES
    }

    NPU_TAGS = {
        DRIVER,
        FIRMWARE,
        NPU,
        MCU
    }

    # The tfplugin component was removed after version 8.0.0.
    CANN_TAGS = {
        TFPLUGIN,
        NNAE,
        NNRT,
        TOOLKIT,
        KERNELS,
    }

    TOOLBOX_TAGS = {
        TOOLBOX,
        FAULT_DIAG
    }

    # add resilience-controller tag when device is 910A
    # The hccl-controller component was removed after version 6.0.0.
    MINDCLUSTER_TAGS = {
        DL,
        VOLCANO,
        HCCL_CONTROLLER,
        ASCEND_DEVICE_PLUGIN,
        NODED,
        NPU_EXPORTER,
        ASCEND_DOCKER_RUNTIME,
        ASCEND_OPERATOR,
        CLUSTERD,
        HCCL_CONTROLLER,
    }

    AI_FRAMEWORKS_TAGS = {
        PYTORCH,
        MINDSPORE,
        TENSORFLOW,
        MINDSPORE_SCENE,
        PYTORCH_DEV,
        PYTORCH_RUN,
        TENSORFLOW_DEV,
        TENSORFLOW_RUN,
    }

    # mindio only support on Atlas 800 (Model 9000)
    # mindie_image only support on 300i-duo and 800i a2
    OTHERS_TAGS = {
        AUTO,
        OFFLINE_DEV,
        OFFLINE_RUN,
        MINDIO,
        MINDIE_IMAGE
    }

    BASIC_TAGS = SYS_DEP_TAGS | NPU_TAGS | CANN_TAGS | TOOLBOX_TAGS


class HardwareOSTags:
    A300_3010_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS
                              | {Tags.OFFLINE_RUN, Tags.OFFLINE_DEV}) - {Tags.MCU}

    A300_3000_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS
                              | {Tags.OFFLINE_RUN, Tags.OFFLINE_DEV}) - {Tags.MCU}

    A300I_PRO_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS
                              | {Tags.AUTO, Tags.OFFLINE_RUN, Tags.OFFLINE_DEV}) - {Tags.MINDSPORE}

    # 300I-duo support mindie_image
    A300I_DUO_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS
                              | Tags.OTHERS_TAGS) - {Tags.MINDSPORE, Tags.MINDIO}

    A200I_A2_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.AI_FRAMEWORKS_TAGS) - {Tags.MINDSPORE}

    # 910 support resilience-controller and mindio
    A300T_9000_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | {Tags.RESILIENCE_CONTROLLER}
                               | Tags.AI_FRAMEWORKS_TAGS | Tags.OTHERS_TAGS) - {Tags.MINDIE_IMAGE, Tags.MCU}

    A900T_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS
                          | Tags.OTHERS_TAGS) - {Tags.MINDIO}

    A300T_A2_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | Tags.AI_FRAMEWORKS_TAGS)

    # 800i-a2 support mindie_image
    ATLAS_800I_A2_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS | {Tags.MINDIE_IMAGE, Tags.OFFLINE_DEV,
                                                                             Tags.OFFLINE_RUN})

    ATLAS_800I_A3_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS) - {Tags.DOCKER_IMAGES}

    ATLAS_900_A3_POD_SUPPORT_TAGS = (Tags.BASIC_TAGS | Tags.MINDCLUSTER_TAGS) - {Tags.DOCKER_IMAGES}


CARD_OS_COMPONENTS_MAP = {
    # this is the A300 series NPU card for x86
    # A standard NPU info: {"aarch": "A300-3000", "x86_64": "A300-3010"}
    Hardware.A300_3010: {
        OSName.UBUNTU_18_04_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS,
        OSName.UBUNTU_20_04_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS,
        OSName.OPENEULER_20_03LTS_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS,
        OSName.KYLIN_V10TERCEL_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS,
        OSName.EULEROS_2_9_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_10_X86_64: HardwareOSTags.A300_3010_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
    },
    # this is the A300 series NPU card for aarch
    Hardware.A300_3000: {
        OSName.UBUNTU_20_04_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.OPENEULER_20_03LTS_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.KYLIN_V10TERCEL_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.KYLIN_V10SWORD_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.KYLIN_V10LANCE_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS,
        OSName.EULEROS_2_9_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_10_AARCH64: HardwareOSTags.A300_3000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
    },
    Hardware.A300I_PRO: {
        OSName.UBUNTU_20_04_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.UBUNTU_20_04_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_4_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.AUTO},
        OSName.OPENEULER_20_03LTS_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.OPENEULER_20_03LTS_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.KYLIN_V10TERCEL_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.KYLIN_V10TERCEL_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.KYLIN_V10SWORD_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.KYLIN_V10LANCE_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.CENTOS_7_6_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.CENTOS_7_6_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.EULEROS_2_9_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_9_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_10_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_10_X86_64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_12_AARCH64:
            HardwareOSTags.A300I_PRO_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.SYS_PKG, Tags.AUTO},
        OSName.BCLINUX_21_10_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS,
        OSName.CTYUNOS_22_06_AARCH64: HardwareOSTags.A300I_PRO_SUPPORT_TAGS
    },
    Hardware.A300I_DUO: {
        OSName.UBUNTU_20_04_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS,
        OSName.UBUNTU_20_04_X86_64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.UBUNTU_22_04_X86_64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.UBUNTU_22_04_4_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS,
        OSName.BCLINUX_21_10_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS,
        OSName.CTYUNOS_22_06_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_12_AARCH64:
            HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.SYS_PKG, Tags.AUTO},
        OSName.OPENEULER_22_03LTS_SP4_AARCH64:
            HardwareOSTags.A300I_DUO_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.AUTO}
    },
    Hardware.A200I_A2: {
        OSName.KYLIN_V10_AARCH64: HardwareOSTags.A200I_A2_SUPPORT_TAGS,
    },
    Hardware.A300T_9000: {
        OSName.UBUNTU_18_04_X86_64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.UBUNTU_18_04_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.UBUNTU_20_04_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.UBUNTU_20_04_X86_64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.OPENEULER_20_03LTS_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.OPENEULER_20_03LTS_X86_64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.KYLIN_V10TERCEL_AARCH64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.KYLIN_V10TERCEL_X86_64: HardwareOSTags.A300T_9000_SUPPORT_TAGS - {Tags.MINDIO},
        OSName.KYLIN_V10SWORD_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.CENTOS_7_6_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.CENTOS_7_6_X86_64: HardwareOSTags.A300T_9000_SUPPORT_TAGS,
        OSName.UOS_20_1020E_AARCH64: HardwareOSTags.A300T_9000_SUPPORT_TAGS - {Tags.SYS_PKG},
        OSName.EULEROS_2_8_AARCH64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.EULEROS_2_9_AARCH64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.EULEROS_2_9_X86_64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.EULEROS_2_10_AARCH64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
        OSName.EULEROS_2_10_X86_64:
            HardwareOSTags.A300T_9000_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS - {Tags.MINDIO, Tags.RESILIENCE_CONTROLLER},
    },
    Hardware.A900T: {
        OSName.BCLINUX_21_10_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.CTYUNOS_22_06_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.CTYUNOS_23_01_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.EULEROS_2_10_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_10_X86_64: HardwareOSTags.A900T_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.EULEROS_2_12_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS - {Tags.SYS_PKG},
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.CENTOS_7_6_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.CENTOS_7_6_X86_64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.KYLIN_V10_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.KYLIN_V10SWORD_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.KYLIN_V10LANCE_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.KYLIN_V10HALBERD_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {
            Tags.AUTO} - Tags.MINDCLUSTER_TAGS,
        OSName.UOS_20_1050E_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS - {Tags.SYS_PKG},
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_X86_64: HardwareOSTags.A900T_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_4_AARCH64: HardwareOSTags.A900T_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.AUTO},
        OSName.CULINUX_3_0_AARCH64:
            HardwareOSTags.A900T_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS,
        OSName.OPENEULER_22_03LTS_SP4_AARCH64:
            HardwareOSTags.A900T_SUPPORT_TAGS - Tags.AI_FRAMEWORKS_TAGS - {Tags.AUTO}
    },
    Hardware.A300T_A2: {
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.A300T_A2_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.A300T_A2_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.A300T_A2_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_X86_64: HardwareOSTags.A300T_A2_SUPPORT_TAGS,
    },
    Hardware.ATLAS_800I_A2: {
        OSName.OPENEULER_22_03LTS_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.OPENEULER_22_03LTS_X86_64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_X86_64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_4_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.KYLIN_V10LANCE_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.KYLIN_V10HALBERD_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.BCLINUX_21_10_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.CTYUNOS_22_06_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.CTYUNOS_23_01_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.EULEROS_2_12_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS - {Tags.SYS_PKG},
        OSName.OPENEULER_22_03LTS_SP4_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.OPENEULER_24_03LTS_SP1_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS,
        OSName.CULINUX_3_0_AARCH64: HardwareOSTags.ATLAS_800I_A2_SUPPORT_TAGS
    },
    Hardware.ATLAS_800I_A3: {
        OSName.OPENEULER_22_03LTS_SP4_AARCH64: HardwareOSTags.ATLAS_800I_A3_SUPPORT_TAGS,
        OSName.KYLIN_V10HALBERD_AARCH64: HardwareOSTags.ATLAS_800I_A3_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.VELINUX_1_3_AARCH64: HardwareOSTags.ATLAS_800I_A3_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS
    },
    Hardware.ATLAS_900_A3_POD: {
        OSName.DEBIAN_10_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.OPENEULER_22_03LTS_SP4_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.KYLIN_V10HALBERD_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.MTOS_22_03LTS_SP4_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.UBUNTU_22_04_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.CTYUNOS_22_06_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.CTYUNOS_23_01_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.BCLINUX_21_10_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS,
        OSName.BCLINUX_21_10U4_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS | Tags.AI_FRAMEWORKS_TAGS,
        OSName.VELINUX_1_3_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS - Tags.MINDCLUSTER_TAGS,
        OSName.OPENEULER_24_03LTS_SP1_AARCH64: HardwareOSTags.ATLAS_900_A3_POD_SUPPORT_TAGS
    }
}

MODEL_TAGS_NOT_SUPPORT = {
    HardwareModel.ATLAS_500_PRO_MODEL_3000: Tags.MINDCLUSTER_TAGS | {Tags.MINDIO},
}

NOT_FULL_LIFECYCLE_SUPPORT = {
    Hardware.A300I_PRO: {
        # support after 24.1.0
        OSName.CTYUNOS_22_06_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.5.0.2.220"}
        },
        OSName.UBUNTU_22_04_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.5.0.2.220"}
        },
        OSName.UBUNTU_22_04_X86_64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.5.0.2.220"}
        }
    },

    Hardware.A300I_DUO: {
        OSName.OPENEULER_22_03LTS_X86_64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.rc2"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.3.0.1.231"},
        },
        OSName.OPENEULER_22_03LTS_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.rc2"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.3.0.1.231"},
        },
        # support after 24.1.0
        OSName.CTYUNOS_22_06_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.5.0.2.220"}
        },
        OSName.UBUNTU_22_04_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.rc2"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.3.0.1.231"},
        },
        OSName.UBUNTU_22_04_X86_64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "24.1.rc2"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.3.0.1.231"},
        }
    },

    Hardware.ATLAS_800I_A2: {
        OSName.OPENEULER_24_03LTS_SP1_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "25.2.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.7.0.2.220"},
        }
    },

    Hardware.ATLAS_900_A3_POD: {
        OSName.OPENEULER_24_03LTS_SP1_AARCH64: {
            Tags.DRIVER: {VersionConstraint.START_VERSION: "25.2.0"},
            Tags.FIRMWARE: {VersionConstraint.START_VERSION: "7.7.0.2.220"},
        }
    }

}


def show_os_card_table():
    try:
        from prettytable import PrettyTable
        all_os = list({
            os
            for os_dict in CARD_OS_COMPONENTS_MAP.values()
            for os in os_dict
        })

        table = PrettyTable()
        table.field_names = ["OS"] + list(CARD_OS_COMPONENTS_MAP.keys())
        for os_ in sorted(all_os):
            support_status = []
            for card_name, supported_os in CARD_OS_COMPONENTS_MAP.items():
                status = "Y" if os_ in supported_os else "N"
                support_status.append(status)
            table.add_row([os_] + support_status)
        print("OS and card table:")
        print(table)
    except Exception as e:
        print(e)


def show_os_tag_table():
    try:
        from prettytable import PrettyTable
        all_tags = set()
        for os_dict in CARD_OS_COMPONENTS_MAP.values():
            for tags in os_dict.values():
                for tag in tags:
                    all_tags.add(tag)

        for card, os_support_dict in CARD_OS_COMPONENTS_MAP.items():
            table = PrettyTable()
            table.field_names = ["OS"] + list(all_tags)
            for os_, tags in os_support_dict.items():
                table.add_row([os_] + [("Y" if tag in tags else "N") for tag in all_tags])
            print(card + " support list:")
            print(table)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    show_os_card_table()
    show_os_tag_table()
