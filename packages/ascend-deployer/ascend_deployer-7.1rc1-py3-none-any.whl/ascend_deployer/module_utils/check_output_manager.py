# !/usr/bin/env python3
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
import functools
import os
import sys
import threading

HOME_PATH = os.path.expanduser('~')
DEPLOY_INFO_OUTPUT_DIR = os.path.join(HOME_PATH, ".ascend_deployer", "deploy_info")
try:
    # 适配python2 json打印中文异常问题
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass


class CheckConfig:

    def __init__(self, check_item, desc_en="", desc_zh="", tip_zh="", tip_en="", help_url=""):
        self.check_item = check_item
        self.desc_en = desc_en
        self.desc_zh = desc_zh
        self.tip_en = tip_en
        self.tip_zh = tip_zh
        self.help_url = help_url


CHECK_JSON_DATA = {
    "check_k8s_version": {
        "check_item": "check_k8s_version",
        "desc_en": "Judgment: 1. kubelet, kubectl, and kubeadm all exist"
                   "2. kubelet --version == kubeadm version == kubectl version "
                   "3.kubelet version < 1.29 "
                   "4. kubelet version >=1.19.16.",
        "desc_zh": "判断：1、kubelet，kubectl，kubeadm都存在"
                   "2、kubelet --version == kubeadm version == kubectl version "
                   "3、kubelet version < 1.29 "
                   "4、kubelet version >=1.19.16。",
        "tip_en": "Execute the version query command to confirm whether the component has been installed, "
                  "whether the version number is the same, and whether the version is within the supported range.",
        "tip_zh": "执行版本查询命令确认组件是否已安装，版本号是否相同，版本是否在支持范围。",
        "help_url": ""
    },
    "check_driver_status": {
        "check_item": "check_driver_status",
        "desc_en": "Check: 1. Whether there is an executable file npu-smi,"
                   "2. Is lspci executed successfully?"
                   "3. Does hccn_tool -i {device_id} ip -g report an error when executed?",
        "desc_zh": "检查:1、是否有可执行文件npu-smi，"
                   "2、lspci是否执行成功，"
                   "3、hccn_tool -i {device_id} ip -g执行是否报错。",
        "tip_en": "You can check by executing the corresponding command.",
        "tip_zh": "通过执行对应命令排查即可。",
        "help_url": ""
    },
    "check_os_and_card_compatibility": {
        "check_item": "check_os_and_card_compatibility",
        "desc_en": "Check: 1. Whether the npu card is no longer supported in the life cycle,"
                   "2. Whether the npu card is in the OS list supported by this card."
                   "3. Whether the component to be installed is in the component list supported by this card and os.",
        "desc_zh": "检查：1、npu卡是否已不在生命周期支持，"
                   "2、npu卡是否在此卡支持的os列表。"
                   "3、检查安装组件是否在硬件和os兼容性列表。",
        "tip_en": "Check the compatibility list via the official website for support.",
        "tip_zh": "通过官方网站查看兼容性列表以获得支持。",
        "help_url": "https://www.hiascend.com/document/detail/zh/mindx-dl/600/"
                    "ascenddeployer/ascenddeployer/deployer_0002.html"
    },
    "check_sys_pkg": {
        "check_item": "check_sys_pkg",
        "desc_en": "Check: "
                   "1. Whether the os does not support the installation of sys_pkg list,"
                   "2. Use yum history to check whether the system has installed dependencies. "
                   "If so, installing dependencies through this software is not supported.",
        "desc_zh": "检查："
                   "1、os是否在不支持安装sys_pkg列表，"
                   "2、通过yum history检查系统是否已安装过依赖，若有，则不支持再通过此软件安装依赖。",
        "tip_en": "Check the compatibility list through the official website for support or execute yum history "
                  "to confirm whether the system is pure.",
        "tip_zh": "通过官方网站查看兼容性列表以获得支持或执行yum history确认是否纯净系统。",
        "help_url": "https://www.hiascend.com/document/detail/zh/mindx-dl/600/"
                    "ascenddeployer/ascenddeployer/deployer_0002.html"
    },
    "apt_yum_check": {
        "check_item": "apt_yum_check",
        "desc_en": "Check whether there are dependency conflicts in the system through apt-get check "
                   "or yum check obsolete; yum check dependencies.",
        "desc_zh": "通过apt-get check或yum check obsoleted;yum check dependencies检查系统是否存在依赖冲突。",
        "tip_en": "Just check by executing the corresponding command. Before using this software, "
                  "please make sure that there are no dependency conflicts in the system.",
        "tip_zh": "通过执行对应命令检查即可，使用此软件前请确保系统不存在依赖冲突问题。",
        "help_url": ""
    },
    "check_kernels": {
        "check_item": "check_kernels",
        "desc_en": "Check: 1. Whether the npu belongs to the inference scenario. "
                   "The inference scenario does not support the installation of kernels,"
                   "2. Whether the kernels package is found?"
                   "3. Whether to obtain the kernel version from the kernel package name,"
                   "4. Whether the environment has installed toolkit, nnae or toolkit of the same version as kernels.",
        "desc_zh": "检查：1、npu是否属于推理场景，推理场景不支持安装kernels，"
                   "2、是否找到kernels包，"
                   "3、是否从kernels包名中获取到kernels版本，"
                   "4、环境是否已安装和kernels同版本的toolkit、nnae或toolkit。",
        "tip_en": "You can check them one by one through the description information.",
        "tip_zh": "根据描述信息排查即可。",
        "help_url": ""
    },
    "check_cann_basic": {
        "check_item": "check_cann_basic",
        "desc_en": "Basic checks for installing cann components:"
                   "1. If /etc/ascend_install.info exists and the file contains the Driver_Install_Path_Param field, "
                   "search for the driver/version.info file based on the path in the field,"
                   "2. If the /usr/local/Ascend folder exists, the folder owner ID must be root,"
                   "3. If the /usr/local/Ascend folder exists, the folder permissions must be 755.",
        "desc_zh": "安装cann组件的基本检查："
                   "1、若存在/etc/ascend_install.info且文件中包含Driver_Install_Path_Param字段，"
                   "根据字段中的路径查找driver/version.info文件，"
                   "2、若存在/usr/local/Ascend文件夹，文件夹所有者id需为root，"
                   "3、若存在/usr/local/Ascend文件夹，文件夹权限需为755。",
        "tip_en": "You can check them one by one through the description information.",
        "tip_zh": "通过描述信息依次排查即可。",
        "help_url": ""
    },
    "check_tfplugin": {
        "check_item": "check_tfplugin",
        "desc_en": "Check tfplugin compatibility: tfplugin does not support 3.10.* versions of python.",
        "desc_zh": "检查tfplugin兼容性：tfplugin不支持3.10.*版本的python。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_root": {
        "check_item": "check_root",
        "desc_en": "Check whether the executing user is root.",
        "desc_zh": "检查执行用户是否是root。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_user_privilege_escalation": {
        "check_item": "check_user_privilege_escalation",
        "desc_en": "Check whether user privileges to execute the installation command.",
        "desc_zh": "检查用户是否提权执行安装命令。",
        "tip_en": "If the check fails, the possible cause is the installation command is executed by a common user, "
                  "or the su is used to switch the root user or the sudo is used.",
        "tip_zh": "若检查失败，失败原因可能是由普通用户执行安装命令，也可能是使用su切换成root用户或者通过sudo提权执行安装命令。",
        "help_url": ""
    },
    "check_docker_runtime": {
        "check_item": "check_docker_runtime",
        "desc_en": "Check whether docker runtime is installed correctly:"
                   "1. Check whether the Default Runtime is ascend through the docker info echo field,"
                   "2. Use /etc/docker/daemon.json to determine "
                   "whether default-runtime is ascend or whether runtimes is ascend.",
        "desc_zh": "检查docker runtime是否正确安装："
                   "1、通过docker info回显字段检查Default Runtime是否为ascend，"
                   "2、通过/etc/docker/daemon.json判断default-runtime是否为ascend或runtimes是否为ascend。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_volcano": {
        "check_item": "check_volcano",
        "desc_en": "Determine whether volcano is installed correctly by checking "
                   "whether there are volcano-controllers and volcano-scheduler in kubectl get pod -A.",
        "desc_zh": "通过kubectl get pod -A中是否有volcano-controllers和volcano-scheduler判断volcano是否正确安装。",
        "tip_en": "Just execute kubectl get pod -A to determine.",
        "tip_zh": "执行kubectl get pod -A判断即可。",
        "help_url": ""
    },
    "check_dl_basic": {
        "check_item": "check_dl_basic",
        "desc_en": "Check DL Basics:"
                   "1. (System used space + 18G) / total space < 0.7,"
                   "2. kubectl get nodes -o wide||true must have output and the number of columns is less than 9,"
                   "3. The current node should be in kubectl get nodes -o wide and the node status is Ready "
                   "and the fifth column ip should be consistent with the current node ip,"
                   "4. The number of master nodes cannot be 0 and must be an odd number,"
                   "5. Check that the user name with user ID 9000 should be hwMindX, "
                   "the group name with group ID 9000 should be hwMindX, "
                   "the user ID corresponding to user name hwMindX should be 9000, "
                   "and the group ID corresponding to group name hwMindX should be 9000,"
                   "6. Check whether there is heterogeneity in the master node in the inventory. "
                   "The heterogeneity of the master node is not supported.",
        "desc_zh": "检查DL基础："
                   "1、(系统已用空间+18G)/总空间 < 0.7，"
                   "2、kubectl get nodes -o wide||true需有输出且列数小于9，"
                   "3、当前节点应该在kubectl get nodes -o wide中且节点状态为Ready且第五列ip应和当前节点ip一致，"
                   "4、master节点数量不能为0且必须为奇数，"
                   "5、检查用户id为9000的用户名应该为hwMindX，组id为9000的组名应该为hwMindX，"
                   "用户名hwMindX对应的用户id应该为9000，组名hwMindX对应的组id应该为9000，"
                   "6、检查inventory中master节点中是否存在异构情况，不支持master节点存在异构。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_dns": {
        "check_item": "check_dns",
        "desc_en": "Check whether the installed DL component is configured with DNS:"
                   "1. the /etc/resolv.conf file must exist,"
                   "2. There should be a nameserver field in the /etc/resolv.conf file.",
        "desc_zh": "检查安装DL组件是否配置了DNS："
                   "1，需存在/etc/resolv.conf文件，"
                   "2，/etc/resolv.conf文件中应该有nameserver字段。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": "https://www.hiascend.com/document/detail/zh/mindx-dl/600/"
                    "ascenddeployer/ascenddeployer/deployer_0041.html"
    },
    "check_mindio_install_path_permission": {
        "check_item": "check_mindio_install_path_permission",
        "desc_en": "Check mindio installation path permissions:"
                   "1. If /usr/local/Ascend exists, the owner of this folder must be root,"
                   "2. If /usr/local/Ascend exists, the permissions of this folder must be 755.",
        "desc_zh": "检查mindio安装路径权限："
                   "1、若存在/usr/local/Ascend，此文件夹所有者必须为root，"
                   "2、若存在/usr/local/Ascend，此文件夹权限必须为755。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_resilience_controller_support": {
        "check_item": "check_resilience_controller_support",
        "desc_en": "Check resilience_controller_support, this component only supports 910A1.",
        "desc_zh": "检查resilience_controller_support，此组件仅支持910A1。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_torch": {
        "check_item": "check_torch",
        "desc_en": "Check Pytorch dependencies. You must install nnae or toolkit before installing pytorch. "
                   "Check whether /usr/local/Ascend/ascend-toolkit/set_env.sh "
                   "or /usr/local/Ascend/nnae/set_env.sh exists.",
        "desc_zh": "检查Pytorch依赖，安装pytorch前必须安装nnae或toolkit，检查方式："
                   "查看/usr/local/Ascend/ascend-toolkit/set_env.sh或/usr/local/Ascend/nnae/set_env.sh是否存在。",
        "tip_en": "If this error occurs, check whether /usr/local/Ascend/ascend-toolkit/set_env.sh "
                  "or /usr/local/Ascend/nnae/set_env.sh exists.",
        "tip_zh": "若出现此项报错，检查/usr/local/Ascend/ascend-toolkit/set_env.sh或/usr/local/Ascend/nnae/set_env.sh是否存在。",
        "help_url": ""
    },
    "check_tensorflow": {
        "check_item": "check_tensorflow",
        "desc_en": "Check Tensorflow:"
                   "1. tensorflow does not support python3.10.*,"
                   "2. Before installing tensorflow, "
                   "you need to install nnae or toolkit or install tfplugin or download tfadaptor.",
        "desc_zh": "检查Tensorflow："
                   "1、tensorflow不支持python3.10.*，"
                   "2、安装tensorflow前需安装nnae或toolkit或安装tfplugin或下载tfadaptor。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_mindspore": {
        "check_item": "check_mindspore",
        "desc_en": "Check Mindspore compatibility:"
                   "1. Mindspore does not support python3.12.*,"
                   "2. You need to install toolkit or nnae before installing Mindspore.",
        "desc_zh": "检查Mindspore兼容性:"
                   "1、Mindspore不支持python3.12.*，"
                   "2、安装Mindspore前需安装toolkit或nnae。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_dl_diff_arch": {
        "check_item": "check_dl_diff_arch",
        "desc_en": "Check the heterogeneous scenario: Master0 and worker0 exist and are heterogeneous. "
                   "You need to fill in the other_build_image item in the inventory.",
        "desc_zh": "检查异构场景：Master0和worker0存在且为异构，需在inventory中填写other_build_image项。",
        "tip_en": "Check whether the other_build_image project is missing in inventory.",
        "tip_zh": "检查inventory中other_build_image项目是否缺失。",
        "help_url": "https://www.hiascend.com/document/detail/zh/mindx-dl/600/"
                    "ascenddeployer/ascenddeployer/deployer_0050.html"
    },
    "check_mtos_kernel_devel_pkg": {
        "check_item": "check_mtos_kernel_devel_pkg",
        "desc_en": "Check MTOS dependencies:"
                   "1. Check whether there is the MTOS_22.03LTS-SP4_aarch64 directory in the resources folder,"
                   "2. Search kernel-devel-5.10.0-218.0.0.mt20240808.560.mt2203sp4.aarch64.rpm "
                   "in the MTOS_22.03LTS-SP4_aarch64 directory.",
        "desc_zh": "检查MTOS依赖："
                   "1、检查resources文件夹中是否有MTOS_22.03LTS-SP4_aarch64目录，"
                   "2、在MTOS_22.03LTS-SP4_aarch64目录中查找kernel-devel-5.10.0-218.0.0.mt20240808.560.mt2203sp4.aarch64.rpm。",
        "tip_en": "After using MTOS deployer to download the dependencies, "
                  "you need to manually replace the kernel-devel package (just use the rpm package in the image).",
        "tip_zh": "MTOS使用deployer下载完依赖后需手动替换kernel-devel包(使用镜像中的rpm包即可)。",
        "help_url": ""
    },
    "check_npu_installed": {
        "check_item": "check_npu_installed",
        "desc_en": "Check whether npu is installed: execute the npu-smi info command to see if an error is reported.",
        "desc_zh": "检查npu是否安装:执行npu-smi info命令是否报错。",
        "tip_en": "After logging in to the device, perform npu-smi info on the device.",
        "tip_zh": "登录设备后在设备上执行npu-smi info命令排查即可。",
        "help_url": ""
    },
    "check_mindie_image": {
        "check_item": "check_mindie_image",
        "desc_en": "Check the compatibility of MindIE image installation:"
                   "1. Execute docker --version to check whether the version can be queried correctly,"
                   "2. Docker version should be greater than or equal to 18.03,"
                   "3. The weights_path parameter needs to be provided in inventory,"
                   "4. The weights_path path should have a valid file,"
                   "5. The supported number of davinci devices should be 1, 2, 4 or 8,"
                   "6. The davinci list cannot be repeated,"
                   "7. The entered davinci device needs to exist, query it through ls /dev/ | grep davinci,"
                   "8. Make sure the MindIE container does not exist, use docker ps -a --filter name=MindIE to query,"
                   "9. Check whether npu is installed: execute the npu-smi info command to see if  error is reported.",
        "desc_zh": "检查MindIE镜像安装的兼容性："
                   "1、执行docker --version查看是否能正确查询版本，"
                   "2、docker version应该大于等于18.03，"
                   "3、需在inventory中提供weights_path参数，"
                   "4、weights_path路径应该有有效文件，"
                   "5、davinci设备支持数量应该为1、2、4或者8，"
                   "6、davinci列表不能重复，"
                   "7、输入的davinci设备需要存在，通过ls /dev/ |grep davinci查询，"
                   "8、确保MindIE容器不存在，使用docker ps -a --filter name=MindIE 查询，"
                   "9、检查npu是否安装:执行npu-smi info命令是否报错。",
        "tip_en": "You can check through the description information",
        "tip_zh": "通过描述信息排查即可",
        "help_url": ""
    },
    "check_mcu": {
        "check_item": "check_mcu",
        "desc_en": "MCU pre-installation check:"
                   "1. Check whether there is npu-smi command,"
                   "2. Check whether npu-smi info -l can be executed correctly.",
        "desc_zh": "MCU安装前检查:"
                   "1，检查是否存在npu-smi命令，"
                   "2，检查npu-smi info -l是否能执行成。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_firmware": {
        "check_item": "check_firmware",
        "desc_en": "Check firmware:"
                   "1. The lspci | grep {} command must be executable, "
                   "where the possible values for {} are d500, d801, and d802,"
                   "2. Use the lspci |grep {} command to determine "
                   "whether the number of davinci devices is equal to npu_num in the inventory "
                   "and determine whether the physical link is normal. "
                   "The possible values for {} are d500, d801, and d802.",
        "desc_zh": "检查固件："
                   "1、lspci | grep {}命令需可执行，其中{}对应可取值为d500，d801，d802，"
                   "2、根据lspci |grep {}命令判断davinci设备数是否等于inventory中的npu_num判断物理链路是否正常，"
                   "其中{}对应可取值为d500，d801，d802。",
        "tip_en": "",
        "tip_zh": "",
        "help_url": ""
    },
    "check_driver": {
        "check_item": "check_driver",
        "desc_en": "Check whether the driver is normal and judge "
                   "whether the npu-smi info command is executed successfully.",
        "desc_zh": "检查驱动是否正常，通过npu-smi info命令是否执行成功判断。",
        "tip_en": "After logging in to the device, perform npu-smi info on the device.",
        "tip_zh": "登录设备后在设备上执行npu-smi info排查即可。",
        "help_url": ""
    },
    "check_npu_health": {
        "check_item": "check_npu_health",
        "desc_en": "Check NPU health status:"
                   "1. Check whether the driver is normal and judge "
                   "whether the npu-smi info command is successfully executed."
                   "2. Check the npu-smi info echo to determine whether there is a non-OK card in the status.",
        "desc_zh": "检查NPU健康状态："
                   "1、检查驱动是否正常，通过npu-smi info命令是否执行成功判断，"
                   "2、查看npu-smi info回显，判断状态是否有非OK的卡。",
        "tip_en": "After logging in to the device, perform npu-smi info on the device.",
        "tip_zh": "登录设备后在设备上执行npu-smi info排查即可。",
        "help_url": ""
    }
}
CONFIGS = {}
for key, value in CHECK_JSON_DATA.items():
    CONFIGS[key] = CheckConfig(
        check_item=value.get("check_item", ""),
        desc_en=value.get("desc_en", ""),
        desc_zh=value.get("desc_zh", ""),
        tip_zh=value.get("tip_zh", ""),
        tip_en=value.get("tip_en", ""),
        help_url=value.get("help_url", "")
    )


class CheckStatus(object):
    WAIT = "wait"
    CHECKING = "checking"
    SUCCESS = "success"
    FAILED = "failed"


class CheckOutput(object):

    def __init__(self, check_config, check_status=CheckStatus.WAIT):
        self.check_config = check_config
        self.error_msg = []
        self.check_status = check_status

    def to_json(self):
        res = {
            "check_status": self.check_status,
            "error_msg": self.get_formatted_error_msg()
        }
        res.update(vars(self.check_config))
        if self.check_status != CheckStatus.FAILED:
            res.update({
                "tip_en": "",
                "tip_zh": ""
            })
        return res

    def get_formatted_error_msg(self):
        """Format error messages

        Returns differently formatted results based on error message quantity:
        1. Returns empty string when no errors exist
        2. Returns directly concatenated string for single error
        3. Returns numbered list format for multiple errors (e.g., 1. xxx 2. yyy)
        """
        if not self.error_msg:
            return ""
        elif len(self.error_msg) == 1:
            return " ".join(self.error_msg)
        else:
            return " ".join("{}. {}".format(i + 1, msg) for i, msg in enumerate(self.error_msg))


class CheckOutputManager(object):
    _CHECK_RES_OUTPUT_PATH = os.path.join(DEPLOY_INFO_OUTPUT_DIR, "check_res_output.json")
    _OUTPUT_INTERVAL = 3

    def __init__(self):
        self.check_configs = []
        self.check_output_map = {}
        self.fail_happen = False

    def get_check_output(self, check_item):
        return self.check_output_map.setdefault(check_item, CheckOutput(CheckConfig(check_item)))

    def set_error_msg(self, error_msg, func_name):
        self.get_check_output(func_name).error_msg.append(error_msg)

    def start_check(self, check_item):
        self.check_configs.append(CONFIGS.get(check_item, CheckConfig('no_check_event_check')))
        self.check_output_map.setdefault(check_item, CheckOutput(CONFIGS.get(check_item)))
        self.get_check_output(check_item).check_status = CheckStatus.CHECKING

    def check_failed(self, check_item):
        check_output = self.get_check_output(check_item)
        check_output.check_status = CheckStatus.FAILED

    def check_success(self, check_item):
        check_output = self.get_check_output(check_item)
        check_output.check_status = CheckStatus.SUCCESS

    def generate_check_output(self):
        return [self.get_check_output(check_config.check_item).to_json() for check_config in self.check_configs]


class Future(object):
    def __init__(self, func_name):
        self.func_name = func_name
        self._result = None
        self._exception = None
        self._callbacks = []
        self._completed = False

    def add_done_callback(self, fn):
        if self._completed:
            fn(self)
        else:
            self._callbacks.append(fn)

    def set_result(self, result):
        self._result = result
        self._completed = True
        for cb in self._callbacks:
            cb(self)

    def set_exception(self, exc):
        self._exception = exc
        self._completed = True
        for cb in self._callbacks:
            cb(self)

    def result(self):
        if self._exception:
            raise self._exception
        return self.result


# 模拟ThreadPoolExecutor.submit
class DummyExecutor(object):
    @staticmethod
    def submit(func, *args, **kwargs):
        future = Future(func.__name__)

        def _run():
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except BaseException as e:
                future.set_exception(e)

        t = threading.Thread(target=_run)
        t.daemon = True
        future.thread = t  # 保存线程对象
        t.start()
        return future


EXECUTOR = DummyExecutor()
GLOBAL_FUTURES = []
CHECK_OUTPUT_MANAGER = CheckOutputManager()
CHECK_MODE = os.getenv('DEPLOYER_CHECK_MODE', 'full')


def check_event(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if CHECK_MODE == 'fast' and CHECK_OUTPUT_MANAGER.fail_happen:
            return
        CHECK_OUTPUT_MANAGER.start_check(func.__name__)
        try:
            if CHECK_MODE == 'fast':
                func(*args, **kwargs)
                if CHECK_OUTPUT_MANAGER.get_check_output(func.__name__).error_msg:
                    CHECK_OUTPUT_MANAGER.check_failed(func.__name__)
                    CHECK_OUTPUT_MANAGER.fail_happen = True
                else:
                    CHECK_OUTPUT_MANAGER.check_success(func.__name__)
            else:
                future = EXECUTOR.submit(func, *args, **kwargs)
                future.add_done_callback(_handle_result)
                GLOBAL_FUTURES.append(future)
        except BaseException as e:
            CHECK_OUTPUT_MANAGER.check_failed(func.__name__)
            raise e

    wrapper.decorated_by_check_event = True
    return wrapper


def _handle_result(future):
    func_name = future.func_name
    try:
        future.result()
        if CHECK_OUTPUT_MANAGER.get_check_output(func_name).error_msg:
            CHECK_OUTPUT_MANAGER.check_failed(func_name)
            CHECK_OUTPUT_MANAGER.fail_happen = True
        else:
            CHECK_OUTPUT_MANAGER.check_success(func_name)
    except BaseException as e:
        CHECK_OUTPUT_MANAGER.check_failed(func_name)
        raise e


def set_error_msg(error_msg, func):
    CHECK_OUTPUT_MANAGER.set_error_msg(error_msg, func)


def wait_for_finish():
    threads = []
    for future in GLOBAL_FUTURES:
        if hasattr(future, 'thread'):
            threads.append(future.thread)
    for thread in threads:
        thread.join()
