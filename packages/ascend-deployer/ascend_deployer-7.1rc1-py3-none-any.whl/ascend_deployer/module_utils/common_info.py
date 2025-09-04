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
import platform
import shlex
import subprocess

ID_LEN = 6  # read 6 chars in /sys/bus/pci/devices/*/{class,vendor,device,subsystem_vendor,subsystem_device}
ARCH = platform.machine()
FIND_PRODUCT_CMD = "dmidecode -t 1"
FIND_SOC_PRODUCT_CMD = "dmidecode -t 2"
UNKNOWN = "--"


class OSName:
    BCLINUX_21_10_AARCH64 = "BCLinux_21.10_aarch64"
    BCLINUX_21_10U4_AARCH64 = "BCLinux_21.10U4_aarch64"
    CENTOS_7_6_AARCH64 = "CentOS_7.6_aarch64"
    CENTOS_7_6_X86_64 = "CentOS_7.6_x86_64"
    CTYUNOS_22_06_AARCH64 = "CTyunOS_22.06_aarch64"
    CTYUNOS_22_06_X86_64 = "CTyunOS_22.06_x86_64"
    CTYUNOS_23_01_AARCH64 = "CTyunOS_23.01_aarch64"
    EULEROS_2_8_AARCH64 = "EulerOS_2.8_aarch64"
    EULEROS_2_9_AARCH64 = "EulerOS_2.9_aarch64"
    EULEROS_2_9_X86_64 = "EulerOS_2.9_x86_64"
    EULEROS_2_10_AARCH64 = "EulerOS_2.10_aarch64"
    EULEROS_2_10_X86_64 = "EulerOS_2.10_x86_64"
    EULEROS_2_12_AARCH64 = "EulerOS_2.12_aarch64"
    KYLIN_V10TERCEL_AARCH64 = "Kylin_V10Tercel_aarch64"
    KYLIN_V10TERCEL_X86_64 = "Kylin_V10Tercel_x86_64"
    KYLIN_V10_AARCH64 = "Kylin_V10_aarch64"
    KYLIN_V10SWORD_AARCH64 = "Kylin_V10Sword_aarch64"
    KYLIN_V10LANCE_AARCH64 = "Kylin_V10Lance_aarch64"
    KYLIN_V10HALBERD_AARCH64 = "Kylin_V10Halberd_aarch64"
    OPENEULER_20_03LTS_AARCH64 = "OpenEuler_20.03LTS_aarch64"
    OPENEULER_20_03LTS_X86_64 = "OpenEuler_20.03LTS_x86_64"
    OPENEULER_22_03LTS_AARCH64 = "OpenEuler_22.03LTS_aarch64"
    OPENEULER_22_03LTS_X86_64 = "OpenEuler_22.03LTS_x86_64"
    UBUNTU_18_04_AARCH64 = "Ubuntu_18.04_aarch64"
    UBUNTU_18_04_X86_64 = "Ubuntu_18.04_x86_64"
    UBUNTU_20_04_AARCH64 = "Ubuntu_20.04_aarch64"
    UBUNTU_20_04_X86_64 = "Ubuntu_20.04_x86_64"
    UBUNTU_22_04_AARCH64 = "Ubuntu_22.04_aarch64"
    UBUNTU_22_04_X86_64 = "Ubuntu_22.04_x86_64"
    UBUNTU_22_04_4_AARCH64 = "Ubuntu_22.04.4_aarch64"
    CULINUX_3_0_AARCH64 = "CULinux_3.0_aarch64"
    DEBIAN_10_AARCH64 = "Debian_10_aarch64"
    MTOS_22_03LTS_SP4_AARCH64 = "MTOS_22.03LTS-SP4_aarch64"
    OPENEULER_22_03LTS_SP4_AARCH64 = "OpenEuler_22.03LTS-SP4_aarch64"
    OPENEULER_24_03LTS_SP1_AARCH64 = "OpenEuler_24.03LTS-SP1_aarch64"
    UOS_20_1020E_AARCH64 = "UOS_20-1020e_aarch64"
    UOS_20_1050E_AARCH64 = "UOS_20-1050e_aarch64"
    VELINUX_1_3_AARCH64 = "veLinux_1.3_aarch64"


card_map = {
    ("0x19e5", "0xd100", "0x0200", "0x0100"): {"x86_64": "A300-3010", "aarch64": "A300-3000"},
    ("0x19e5", "0xd801", "0x0200", "0x0100"): "A300T-9000",
    ("0x19e5", "0xd802", "0x0200", "0x0100"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3000"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3001"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3003"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3400"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3401"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3402"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x3403"): "A900T",
    ("0x19e5", "0xd802", "0x19e5", "0x6000"): "A300t-a2",
    ("0x19e5", "0xd500", "0x0200", "0x0100"): "A300i-pro",
    ("0x19e5", "0xd500", "0x0200", "0x0110"): "A300i-duo",
    ("0x19e5", "0xd802", "0x19e5", "0x4000"): "A300i-a2",
    ("0x19e5", "0xd105", "0x0200", "0x0100"): "A200i-a2",
    ("0x19e5", "0xd107", "0x0000", "0x0000"): "A200i-a2",
    ("0x19e5", "0xd802", "0x19e5", "0x3002"): "Atlas 800I A2",
    ("0x19e5", "0xd802", "0x19e5", "0x3004"): "Atlas 800I A2",
    ("0x19e5", "0xd802", "0x19e5", "0x3005"): "Atlas 800I A2",
    ("0x19e5", "0xd803", "0x19e5", "0x3000"): "Atlas 900 A3 Pod",
    ("0x19e5", "0xd803", "0x19e5", "0x3001"): "Atlas 900 A3 Pod",
    ("0x19e5", "0xd803", "0x19e5", "0x3002"): "Atlas 900 A3 Pod",
    ("0x19e5", "0xd803", "0x19e5", "0x0100"): "Atlas 800I A3",
    ("0x19e5", "0xd803", "0x19e5", "0x3003"): "Atlas 800I A3",
}

product_model_dict = {
    "Atlas 800 (Model 9000)": {"product": "A800", "model": "9000", "name": "A800-9000"},
    "Atlas 800 (Model 9010)": {"product": "A800", "model": "9010", "name": "A800-9010"},
    "Atlas 900 (Model 9000)": {"product": "A900", "model": "9000"},
    "Atlas 900 Compute Node": {"product": "A900", "model": "9000"},
    "A300T-9000": {"product": "A300t", "model": "9000", "name": "A300t-9000"},
    "Atlas 800 (Model 3000)": {"product": "A300", "model": "3000", "name": "A300-3000"},
    "Atlas 800 (Model 3010)": {"product": "A300", "model": "3010", "name": "A300-3010"},
    "Atlas 500 Pro (Model 3000)": {"product": "A300", "model": "3000", "name": "A300-3000"},
    "A300-3010": {"product": "A300", "model": "3010", "name": "A300-3010"},
    "A300-3000": {"product": "A300", "model": "3000", "name": "A300-3000"},
    "Atlas 500 (Model 3000)": {"product": "A300", "model": "3000", "name": "A300-3000"},
    "A300i-pro": {"product": "A300i", "model": "pro", "name": "A300i-pro"},
    "A200-3000": {"product": "A300", "model": "3000"},
    "A300i-duo": {"product": "Atlas-300i-duo", "model": "duo", "name": "A300i-duo"},
    "A300i-a2": {"product": "Atlas-300I-A2", "model": "A2", "name": "A300i-a2"},
    "A200i-a2": {"product": "Atlas-200I-DK-A2", "model": "A2", "name": "A200i-a2"},
    "Atlas 800I A2": {"product": "Atlas-800I-A2", "model": "A2", "name": "A800i-a2"},
    "Atlas 800I A3": {"product": "Atlas-800I-A3", "model": "A3", "name": "A800i-a3"},
    "Atlas 900 A3 Pod": {"product": "Atlas-900-A3-Pod", "model": "A3", "name": "A900-a3"},
    "Atlas 800I A2 2UP": {"product": "Atlas-800I-A2-2UP", "model": "duo", "name": "A300i-duo"},
}


class SceneName:
    Infer = "infer"
    Train = "train"
    A300I = "a300i"
    A300IDUO = "a300iduo"


scenes_dict = {
    "A300i-pro": SceneName.A300I,
    "A300-3000": SceneName.Infer,
    "A300-3010": SceneName.Infer,
    "A200-3000": SceneName.Infer,
    "A800-9000": SceneName.Train,
    "A800-9010": SceneName.Train,
    "Atlas 900 Compute Node": SceneName.Train,
    "A900T": "a910b",
    "A300t-a2": "a910b",
    "A300i-duo": SceneName.A300IDUO,
    "A300i-a2": "a910b",
    "A200i-a2": "a310b",
    "Atlas 800I A2": "a910b",
    "Atlas 800I A3": 'a910_93',
    "Atlas 900 A3 Pod": 'a910_93',
    "Atlas 800I A2 2UP": SceneName.A300IDUO
}

product_name_tuple = (
    "Atlas 800 (Model 9000)",
    "Atlas 800 (Model 9010)",
    "Atlas 900 (Model 9000)",
    "Atlas 900 Compute Node",
    "Atlas 500 Pro (Model 3000)",
    "Atlas 500 (Model 3000)",
    "Atlas 900 A3 Pod",
    "Atlas 800I A2 2UP"
)


class NPUCardName:
    P3 = "P3"
    A910A1 = "910A1"
    A910A2 = "910A2"
    A910A3 = "910A3"


class DeployStatus:
    DEPLOY_STATUS = "deploy_status"

    WAIT = "wait"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    SKIP = "skip"


class ContainerRuntimeType:
    CONTAINERD = "containerd"
    DOCKER = "docker"


class TestReport:
    # 定义test表格名
    ASCEND_SOFTWARE_TEST_REPORT = u"表1-昇腾软件检验报告"
    DL_TEST_REPORT = u"表2-DL集群调度组件检验报告"
    DL_MASTER_NODE_TEST_REPORT = u"表2-1 DL集群调度master节点组件报告"
    DL_WORKER_NODE_TEST_REPORT = u"表2-2 DL集群调度worker节点组件报告"

    # 定义test表格的列名
    COLUMNS_NPU = ["driver", "firmware"]
    COLUMNS_MCU = ["mcu"]
    COLUMNS_CANN = ["toolbox", "tfplugin", "nnae", "nnrt", "toolkit", "mindie_image"]
    COLUMNS_PYPKG = ["mindspore", "tensorflow", "pytorch", "fault-diag"]
    COLUMNS_MASTER = ["ascend-operator", "clusterd", "hccl-controller", "volcano", "resilience-controller"]
    COLUMNS_WORKER_PHYSICAL = ["ascend-docker-runtime"]
    COLUMNS_WORKER_POD = ["ascend-device-plugin", "noded", "npu-exporter"]
    COLUMNS_SOFTWARE = COLUMNS_NPU + COLUMNS_CANN + COLUMNS_PYPKG


def get_profile_model(model):
    if model == "--":
        return "unknown"

    if "Atlas" in model and "Model" in model:
        model = "A" + model.split("(")[0].split()[1].strip() + "-" + model.split(")")[0].split("Model")[1].strip()

    if model == "A300T-9000":
        if ARCH == "aarch64":
            model = "A800-9000"
        else:
            model = "A800-9010"

    if model in ["A500-3000", "A800-3000"]:
        model = "A300-3000"
    if model == "A800-3010":
        model = "A300-3010"

    return model


def parse_item(dir_path):
    """
    parse device to tuple

    @rtype: tuple
    """
    id_list = []
    name_order = ("vendor", "device", "subsystem_vendor", "subsystem_device")
    for file_name in name_order:
        full_file_path = os.path.join(dir_path, file_name)
        if not os.path.exists(full_file_path):
            continue
        with open(os.path.join(full_file_path)) as f:
            id_list.append(f.read(ID_LEN))
    return tuple(id_list)


def parse_card():
    devices_path = "/sys/bus/pci/devices/"
    tmp_value = UNKNOWN
    for dir_name in os.listdir(devices_path):
        full_dir = os.path.join(devices_path, dir_name)
        class_file = os.path.join(full_dir, "class")
        if not os.path.exists(class_file):
            continue
        with open(class_file) as f:
            # to explain the device type, starting with 0x1200 represent the accelerator card, 0x0604 means pcie device
            class_id = f.read(ID_LEN)
            if not class_id.startswith("0x1200") and not class_id.startswith("0x0604"):
                continue
        item = parse_item(full_dir)
        value = card_map.get(item, UNKNOWN)
        if value == UNKNOWN:
            continue
        if class_id.startswith("0x0604"):
            tmp_value = value
            continue
        if isinstance(value, dict):
            return value.get(ARCH, UNKNOWN)
        return value
    return tmp_value


def get_accelerator_devices():
    """
    description: 解析lspci | grep acc命令，获取bus总线值
    """
    process = subprocess.Popen('lspci | grep acc | grep Device', shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # 检查命令是否成功执行
    if process.returncode != 0:
        print("Error executing command:", stderr.decode())
        return []

    # 解析输出并提取第一列的结果
    devices = []
    for line in stdout.decode().splitlines():
        first_column = line.split()[0]
        devices.append(first_column)

    return devices


def parse_device_info():
    """
    description: 获取四元组对应的服务器型号并打印，如果遇到没适配的情况则打印出四元组
    """
    devices = get_accelerator_devices()
    if not devices:
        print("No accelerator devices found.")
        return

    accelerator_devices = "0000:{}".format(devices[0])
    devices_path = "/sys/bus/pci/devices/"
    groups = ('vendor', 'device', 'subsystem_vendor', 'subsystem_device')
    item = []
    for each in groups:
        # 拼接devices路径
        id_path = "{}/{}".format(devices_path + accelerator_devices, each)
        # 查看路径下id信息
        id_result = subprocess.Popen(['cat', id_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = id_result.communicate()
        if id_result.returncode == 0:
            item.append(stdout.strip().decode('utf-8'))
        else:
            print("Error reading {}: {}".format(id_path, stderr))
            return

    # 通过四元组，获取服务器型号
    value = card_map.get(tuple(item), 'unmatched npu pci codes')
    print(value, tuple(item))


def get_product_from_dmi(cmd):
    try:
        cp = subprocess.Popen(
            args=shlex.split(cmd), shell=False, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except OSError:
        return ""
    for line in cp.stdout.readlines():
        if "Product" in line:
            product_infos = line.split(":")
            if len(product_infos) < 2:
                return ""
            raw_product = product_infos[1]
            return raw_product.replace("\t", "").replace("\n", "").strip()
    return ""


def parse_model(card):
    if card != "--":
        if os.path.exists("/run/board_cfg.ini"):
            return "Atlas 500 (Model 3000)"
        model_from_system = get_product_from_dmi(FIND_PRODUCT_CMD)
        if model_from_system in product_name_tuple:
            return model_from_system
    model_from_baseboard = get_product_from_dmi(FIND_SOC_PRODUCT_CMD)
    if model_from_baseboard == "Atlas 200I SoC A1":
        return model_from_baseboard
    return card


def get_npu_info():
    card = parse_card()
    product_model = parse_model(card)
    model = card if card == "A300i-pro" else product_model
    profile_model = get_profile_model(model)
    scene = scenes_dict.get(profile_model, "unknown")
    product = product_model_dict.get(model, {}).get("product", "")
    ret = {"card": card, "model": product_model, "scene": scene, "product": product}
    return ret


os_dict = {
    "bclinux": "BCLinux",
    "centos": "CentOS",
    "ubuntu": "Ubuntu",
    "euleros": "EulerOS",
    "kylin": "Kylin",
    "ctyunos": "CTyunOS",
    "uos": "UOS",
    "openEuler": "OpenEuler",
    "culinux": "CULinux",
    "debian": "Debian",
    "mtos": "MTOS"
}

os_version_dict = {"euleros": {"2.0": "2"}, "kylin": {"V10": "V10", "v10": "V10"}}

os_list = [
    OSName.BCLINUX_21_10_AARCH64,
    OSName.BCLINUX_21_10U4_AARCH64,
    OSName.CENTOS_7_6_AARCH64,
    OSName.CENTOS_7_6_X86_64,
    OSName.CTYUNOS_22_06_AARCH64,
    OSName.CTYUNOS_22_06_X86_64,
    OSName.CTYUNOS_23_01_AARCH64,
    OSName.EULEROS_2_8_AARCH64,
    OSName.EULEROS_2_9_AARCH64,
    OSName.EULEROS_2_9_X86_64,
    OSName.EULEROS_2_10_AARCH64,
    OSName.EULEROS_2_10_X86_64,
    OSName.EULEROS_2_12_AARCH64,
    OSName.KYLIN_V10TERCEL_AARCH64,
    OSName.KYLIN_V10TERCEL_X86_64,
    OSName.KYLIN_V10_AARCH64,
    OSName.KYLIN_V10SWORD_AARCH64,
    OSName.KYLIN_V10LANCE_AARCH64,
    OSName.KYLIN_V10HALBERD_AARCH64,
    OSName.OPENEULER_20_03LTS_AARCH64,
    OSName.OPENEULER_20_03LTS_X86_64,
    OSName.OPENEULER_22_03LTS_AARCH64,
    OSName.OPENEULER_22_03LTS_X86_64,
    OSName.UBUNTU_18_04_AARCH64,
    OSName.UBUNTU_18_04_X86_64,
    OSName.UBUNTU_20_04_AARCH64,
    OSName.UBUNTU_20_04_X86_64,
    OSName.UBUNTU_22_04_AARCH64,
    OSName.UBUNTU_22_04_X86_64,
    OSName.UBUNTU_22_04_4_AARCH64,
    OSName.CULINUX_3_0_AARCH64,
    OSName.DEBIAN_10_AARCH64,
    OSName.MTOS_22_03LTS_SP4_AARCH64,
    OSName.OPENEULER_22_03LTS_SP4_AARCH64,
    OSName.OPENEULER_24_03LTS_SP1_AARCH64,
    OSName.VELINUX_1_3_AARCH64,
]

no_sys_pkg_os_list = [
    OSName.UOS_20_1020E_AARCH64,
    OSName.UOS_20_1050E_AARCH64,
    OSName.EULEROS_2_12_AARCH64
]

os_list.extend(no_sys_pkg_os_list)

dl_os_list = [
    "MTOS_22.03LTS-SP4",
    "OpenEuler_22.03LTS-SP4",
    "CentOS_7.6",
    "CTyunOS_22.06",
    "CTyunOS_23.01",
    "OpenEuler_20.03LTS",
    "OpenEuler_22.03LTS",
    "OpenEuler_24.03LTS-SP1",
    "Ubuntu_18.04",
    "Ubuntu_20.04",
    "Ubuntu_22.04",
    "Ubuntu_22.04.4",
    "UOS_20-1020e",
    "UOS_20-1050e",
    "BCLinux_21.10",
    "BCLinux_21.10U4",
    "Kylin_V10",
    "Kylin_V10Tercel",
    "Kylin_V10Sword",
    "Kylin_V10Lance",
    "Kylin_V10Halberd",
    "EulerOS_2.12",
    "CULinux_3.0"
]

Atlas_800 = ('0x02', '0x27', '0x21', '0x24', '0x28')
Atlas_800_A2 = ('0x30', '0x31', '0x32', '0x33', '0x34', '0x38')
Atlas_900_A2_PoD = ('0x30', '0x31', '0x32', '0x34')
Atlas_200T_A2_Box16 = ('0x50', '0x51', '0x53', '0x52')
Atlas_200T_A3_Box8 = ('0xb1',)
Atlas_800I_A3 = ('0xb3',)
Atlas_300T = ('0x01', '0x03', '0x06')
Atlas_300T_A2 = ('0x10', '0x13', '0x12', '0x11')


def get_scene_dict(resource_dir):
    scene_dict = {
        "normalize310p": "{}/run_from_a310p_zip".format(resource_dir),
        "normalize910": "{}/run_from_910_zip".format(resource_dir),
        "a910b": "{}/run_from_910b_zip".format(resource_dir),
        "soc": "{}/run_from_soc_zip".format(resource_dir),
        "infer": "{}/run_from_infer_zip".format(resource_dir),
        "a300i": "{}/run_from_a300i_zip".format(resource_dir),
        "a300v": "{}/run_from_a300v_zip".format(resource_dir),
        "a300v_pro": "{}/run_from_a300v_pro_zip".format(resource_dir),
        "a300iduo": "{}/run_from_a300iduo_zip".format(resource_dir),
        "train": "{}/run_from_train_zip".format(resource_dir),
        "trainpro": "{}/run_from_train_pro_zip".format(resource_dir),
        "a310b": "{}/run_from_310b_zip".format(resource_dir),
        "a910_93": "{}/run_from_910_93_zip".format(resource_dir),
    }
    return scene_dict


def get_os_version(os_id, os_version, os_codename):
    if os_id == "centos":
        with open("/etc/centos-release", "r") as f:
            content = f.read()
            os_version = ".".join(content.split()[3].split(".")[:2])
    elif os_id == "euleros":
        code_name_dict = {
            "SP8": ".8",
            "SP9": ".9",
            "SP9x86_64": ".9",
            "SP10": ".10",
            "SP10x86_64": ".10",
            "SP12": ".12"
        }
        code_name = os_codename.split()[1].strip("()")
        try:
            os_version += code_name_dict[code_name]
        except KeyError:
            raise RuntimeError("os {}_{}{} is not supported".format(os_id, os_version, code_name))
    elif os_id == "kylin" or os_id == "openEuler" or os_id == "mtos":
        code_name = os_codename.split()
        if len(code_name) > 1:
            code_name = code_name[1].strip("()")
            os_version += code_name
    elif os_id == "ubuntu":
        ubuntu_support_version = ["18.04.1", "18.04.5", "20.04", "22.04", "22.04.4"]
        version_verbose = os_codename.split()[0]
        if version_verbose not in ubuntu_support_version:
            raise RuntimeError("os {}_{} is not supported".format(os_id, version_verbose))
        # The system dependency packages in this list may differ from the main version.
        ubuntu_point_releases = ["22.04.4"]
        if version_verbose in ubuntu_point_releases:
            os_version = version_verbose
    elif os_id == "uos":
        os_kernel = platform.uname().release
        if os_version == "20" and "4.19.90-2106.3.0.0095.up2.uel20" in os_kernel:
            os_version += "-1020e"
        elif os_version == "20" and "4.19.90-2211.5.0.0178.22.uel20" in os_kernel:
            os_version += "-1050e"
        else:
            raise RuntimeError("os {}_{} is not supported".format(os_id, os_version))
    elif os_id == "debian":
        code_name_dict = {
            "buster": ""
        }
        code_name = os_codename.split()[1].strip("()")
        try:
            os_version += code_name_dict[code_name]
        except KeyError:
            raise RuntimeError("os {}_{}{} is not supported".format(os_id, os_version, code_name))
    return os_version


def parse_os_release():
    os_name = os_version = os_id = ""
    with open("/etc/os-release", "r") as f:
        for line in f:
            if line.startswith("VERSION="):
                os_codename = line.strip().split("=")[1].strip('"')
            elif line.startswith("ID="):
                os_id = line.strip().split("=")[1].strip('"')
                if os_id not in os_dict:
                    raise RuntimeError("os {} is not supported".format(os_id))
                os_name = os_dict[os_id]
            elif line.startswith("VERSION_ID="):
                os_version = os_ver = line.strip().split("=")[1].strip('"')
                if os_id in os_version_dict:
                    os_version = os_version_dict[os_id][os_ver]
    os_version = get_os_version(os_id, os_version, os_codename)

    return os_name, os_version


def parse_velinux_os_release():
    os_name = os_version = ""
    if not os.path.exists("/etc/velinux-release"):
        return "", ""
    with open("/etc/velinux-release", "r") as f:
        for line in f:
            if line.startswith("VERSION_ID="):
                os_version = line.strip().split("=")[1].strip('"')
            elif line.startswith("NAME="):
                os_name = line.strip().split("=")[1].strip('"')
    return os_name, os_version


def get_os_and_arch():
    arch = platform.machine()
    os_name, os_version = parse_os_release()
    os_and_arch = "{}_{}_{}".format(os_name, os_version, arch)
    if os_and_arch == OSName.DEBIAN_10_AARCH64:
        os_name, os_version = parse_velinux_os_release()
        if os_name and os_version:
            os_and_arch = "{}_{}_{}".format(os_name, os_version, arch)

    if os_and_arch not in os_list:
        raise RuntimeError("os {} is not supported".format(os_and_arch))
    return os_and_arch


def need_skip_sys_package(os_and_arch):
    return os_and_arch in no_sys_pkg_os_list


def get_os_package_name():
    os_name, os_version = parse_os_release()
    os_package_name = "{}_{}".format(os_name, os_version)
    if os_package_name not in dl_os_list:
        raise RuntimeError("os {} is not supported".format(os_package_name))
    if os_package_name.startswith("OpenEuler"):
        os_package_name = os_package_name.replace("LTS", "_LTS")
    return os_package_name


def get_ascend_install_path(user_uid, user_dir):
    if user_uid == 0:
        return "/usr/local/Ascend"
    return "{}/Ascend".format(user_dir)


def get_local_path(user_uid, user_dir):
    if user_uid == 0:
        return "/usr/local"
    return "{}/.local".format(user_dir)


if __name__ == '__main__':
    print("OS and arch:", get_os_and_arch())
    print("Npu info:", get_npu_info())
    print("Npu pci device info:")
    parse_device_info()
