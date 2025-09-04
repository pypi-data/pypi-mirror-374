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
import grp
import pwd
import csv
import json
from collections import defaultdict
from ansible.module_utils.check_output_manager import check_event

from ansible.module_utils.check_utils import CheckUtil as util

GB = 1024 * 1024 * 1024


class DLCheck:
    user = 'hwMindX'
    user_id = 9000
    group = 'hwMindX'
    group_id = 9000
    k8s_extra_space = 6 * GB
    dl_extra_space = 12 * GB
    throttle = 0.70

    def __init__(self, module, error_messages):
        self.module = module
        self.master_group = module.params.get("master_groups")
        self.cluster_info = module.params.get("cluster_info")
        self.ip = module.params.get('current_hostname')
        self.node_name = module.params.get("node_name")
        self.error_messages = error_messages
        self.master0_arch = module.params.get("master0_arch")
        self.master_arch = module.params.get("master_arch")

    def _get_k8s_pods(self):
        _, out, _ = self.module.run_command("kubectl get pods -A", check_rc=True)
        dl_pods_info = defaultdict(list)

        # dl中的组件
        match_list = ['device-plugin', 'volcano', 'noded', 'clusterd',
                      'hccl-controller', 'ascend-operator', 'npu-exporter', 'resilience-controller']
        # 解析回显信息
        lines = out.splitlines()
        reader = csv.DictReader(lines, delimiter=' ', skipinitialspace=True)
        for row in reader:
            name = row['NAME']
            for match in match_list:
                if match in name:
                    dl_pods_info[match].append(row)
        return dl_pods_info

    @check_event
    def check_docker_runtime(self):
        # step1.查看default runtime 字段是否为ascend
        _, out, _ = self.module.run_command('docker info', check_rc=True)
        if 'Default Runtime: ascend' not in out:
            util.record_error("Please install docker runtime firstly", self.error_messages)
            return
        # step2.查看daemon.json文件
        try:
            with open('/etc/docker/daemon.json', 'r') as file:
                docker_daemon = json.load(file)
            if docker_daemon.get('default-runtime') != 'ascend' or 'ascend' not in docker_daemon.get('runtimes'):
                util.record_error("Please install docker runtime firstly", self.error_messages)
                return
            with open('/usr/local/Ascend/Ascend-Docker-Runtime/ascend_docker_runtime_install.info', 'r') as file:
                for line in file:
                    if "version" in line:
                        return
        except FileNotFoundError:
            pass
        util.record_error("Please install docker runtime firstly", self.error_messages)
        return

    @check_event
    def check_volcano(self):
        msg = "Please install volcano firstly"
        all_k8s_pods_info = self._get_k8s_pods()
        volcano_controllers = {}
        volcano_scheduler = {}
        for pod in all_k8s_pods_info.get('volcano', []):
            # 验证命名空间
            if pod.get('NAMESPACE') == 'volcano-system':
                if 'volcano-controllers' in pod.get('NAME'):
                    volcano_controllers = pod
                elif 'volcano-scheduler' in pod.get('NAME'):
                    volcano_scheduler = pod

        if not volcano_controllers or not volcano_scheduler:
            util.record_error(msg, self.error_messages)
        return

    def check_master_arch(self):
        if not self.master_arch or not self.master0_arch:
            return
        if self.master0_arch != self.master_arch:
            util.record_error("The master nodes in the cluster have different architectures "
                              "and installation of DL in this cluster is not supported.", self.error_messages)

    def check_space_available(self):
        sv = os.statvfs('/')
        total = (sv.f_blocks * sv.f_frsize)
        used = (sv.f_blocks - sv.f_bfree) * sv.f_frsize
        usage = float(used + self.k8s_extra_space + self.dl_extra_space) / (total or 1)
        if usage > self.throttle:
            total_gb = "{:.2f}".format(total / GB)
            used_gb = "{:.2f}".format(used / GB)
            usage = "{:.2f}".format(usage)
            msg = 'Insufficient available remaining disk space for Docker containers, filesystems, or root ' \
                  'directories. Total disk space: {} GB, used disk space: {} GB. After installation, the disk ' \
                  'usage: {}, should be below {}'.format(total_gb, used_gb, usage, self.throttle)
            util.record_error(msg, self.error_messages)

    def check_inventory(self):
        master_cnt = len(self.master_group)
        if master_cnt == 0:
            util.record_error(
                "[ASCEND][ERROR] The master node configuration information is missing,"
                " please configure the master node info. For details about the master node configuration,"
                " see the user guide.", self.error_messages)
            return

        if master_cnt % 2 == 0:
            util.record_error("[ASCEND][ERROR] the number of Master nodes must be an odd number, "
                              "for example, 1, 3, 5 ,7. Please modify the master nodes configuration.",
                              self.error_messages)
            return

    def check_node_ready(self):
        """
        check the node on inventory whether in k8s cluster
        k8s cluster info like:
            NAME STATUS ROLES AGE VERSION INTERNAL-IP  ...
            name Ready  worker 1d  v1.2.0  0.0.0.0
        """
        name_pos = 0
        status_pos = 1
        ip_pos = 5
        for line in self.cluster_info.get('stdout_lines', []):
            contents = line.split()
            if not contents or len(contents) < 9:
                msg = "k8s cluster info not illegal. Please check either k8s is already installed or the cluster" \
                      "has been built"
                util.record_error(msg, self.error_messages)
                return
            if contents[name_pos] == self.node_name and contents[status_pos] == 'Ready' and contents[ip_pos] == self.ip:
                return
        msg = "current host {} not in k8s cluster. Please check your k8s " \
              "cluster info and join the node".format(self.node_name)
        util.record_error(msg, self.error_messages)
        return

    def check_user_and_group(self, uid, gid, username, groupname):
        errors = []

        def safe_check(check_func):
            try:
                check_func()
            except KeyError:
                pass
            except ValueError as e:
                errors.append(str(e))

        def raise_error(err):
            raise ValueError(err)

        # 检查 UID
        safe_check(
            lambda: pwd.getpwuid(uid).pw_name == username or raise_error(
                "UID {} exists,but username is {},instead of the expected {}".format(uid, pwd.getpwuid(uid).pw_name,
                                                                                     username))
        )

        # 检查 GID 对应的组
        safe_check(
            lambda: grp.getgrgid(gid).gr_name == groupname or raise_error(
                "GID {} exists,but group name is {},instead of the expected {}".format(gid, grp.getgrgid(gid).gr_name,
                                                                                       groupname))
        )

        # 检查用户名对应的 UID
        safe_check(
            lambda: pwd.getpwnam(username).pw_uid == uid or raise_error(
                "user {} exists,but UID is {},instead of the expected {}".format(username,
                                                                                 pwd.getpwnam(username).pw_uid, uid))
        )

        # 检查组名对应的 GID
        safe_check(
            lambda: grp.getgrnam(groupname).gr_gid == gid or raise_error(
                "group {} exists,but GID is {},instead of the expected {}".format(groupname,
                                                                                  grp.getgrnam(groupname).gr_gid, gid))
        )

        if errors:
            for error in errors:
                util.record_error(error, self.error_messages)

    @check_event
    def check_dl_basic(self):
        self.check_space_available()
        self.check_master_arch()
        self.check_node_ready()
        self.check_inventory()
        self.check_user_and_group(self.user_id, self.group_id, self.user, self.group)

    @check_event
    def check_dns(self):
        dns_file = "/etc/resolv.conf"
        if not os.path.exists(dns_file):
            util.record_error("[ASCEND][ERROR] Please config the DNS before install DL", self.error_messages)
            return
        with open(dns_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "nameserver" in line:
                    return
            util.record_error("[ASCEND][ERROR] Please config the DNS before install DL", self.error_messages)

    @check_event
    def check_mindio_install_path_permission(self):
        install_path = "/usr/local/Ascend"
        if not os.path.isdir(install_path):
            return
        if os.stat(install_path).st_uid != 0:
            util.record_error("[ASCEND][ERROR] The owner of the mindio installation dir "
                              "'/usr/local/Ascend' must be root, change the owner to root", self.error_messages)
            return

        mode = os.stat(install_path).st_mode
        permissions = oct(mode)[-3:]
        if int(permissions) != 755:
            util.record_error("[ASCEND][ERROR] When installing mindio, the user and group of the installation path "
                              "must be root, and the permission must be 755. ", self.error_messages)
        return

    @check_event
    def check_resilience_controller_support(self):
        """
        resilience_controller installation only supports 910A1
        """
        card = util.get_card()
        if card != "910":
            util.record_error(
                "[ASCEND][ERROR] Your device does not support resilience-controller.",
                self.error_messages
            )
