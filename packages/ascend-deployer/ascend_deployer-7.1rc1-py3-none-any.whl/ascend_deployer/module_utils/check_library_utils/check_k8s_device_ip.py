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
import glob
import re

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.common_utils import clean_env, compare_version


class K8sDeviceIpCheck(object):
    max_k8s_version = '1.29'
    min_k8s_version = '1.19.16'

    def __init__(self, module, error_messages):
        self.module = module
        self.error_messages = error_messages
        self.tags = self.module.params['tags']
        self.master_groups = self.module.params['master_groups']
        self.worker_groups = self.module.params['worker_groups']
        self.current_hostname = self.module.params['current_hostname']
        self.use_k8s_version = self.module.params['use_k8s_version']
        self.facts = dict()
        self.kubeadm_version = ''
        self.kubectl_version = ''
        self.kubelet_version = ''

    @check_event
    def check_k8s_version(self):
        kubeadm_bin = self.module.get_bin_path('kubeadm')
        if kubeadm_bin:
            _, out, _ = self.module.run_command('kubeadm version', check_rc=True)
            reg = re.search(r'GitVersion:\"v(.+?)\"', out)
            if reg:
                self.kubeadm_version = reg.group(1)
        kubectl_bin = self.module.get_bin_path('kubectl')
        if kubectl_bin:
            _, out, _ = self.module.run_command('kubectl version')
            # case 1:
            #     Client Version: version.Info{Major:"1", Minor:"19", GitVersion:"v1.19.16", GitCommit:...."}
            # case 2:
            #     Client Version: v1.28.2
            #     Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
            #     Server Version: v1.28.2
            reg = re.search(r'(GitVersion|Client Version):\s*\"?v([0-9]+\.[0-9]+\.[0-9]+)\"?', out)
            if reg:
                self.kubectl_version = reg.group(2)
        kubelet_bin = self.module.get_bin_path('kubelet')
        if kubelet_bin:
            _, out, _ = self.module.run_command('kubelet --version', check_rc=True)
            self.kubelet_version = re.search(r'(?<=v)\d+\.\d+(\.\d+)?', out).group()
        self.facts['k8s_installed'] = bool(self.kubeadm_version or self.kubectl_version or self.kubelet_version)
        if not all((self.kubeadm_version, self.kubectl_version, self.kubelet_version)):
            msg = 'Please install k8s first or confirm components of k8s, kubeadm_version: {}, kubectl_version: {}, ' \
                  ' kubelet_version: {}'.format(self.kubeadm_version, self.kubectl_version, self.kubelet_version)
            util.record_error(msg, self.error_messages)
            return
        if self.kubeadm_version != self.kubectl_version or self.kubeadm_version != self.kubelet_version:
            msg = 'k8s on this node has different version, kubeadm_version: {}, kubectl_version: {},' \
                  'kubelet_version: {}'.format(self.kubeadm_version, self.kubectl_version, self.kubelet_version)
            util.record_error(msg, self.error_messages)
            return
        if compare_version(self.kubelet_version, self.max_k8s_version) >= 0:
            util.record_error('node k8s version should be < {}'.format(self.max_k8s_version), self.error_messages)
            return
        if compare_version(self.kubelet_version, self.min_k8s_version) < 0:
            util.record_error('node k8s version should be >= {}'.format(self.min_k8s_version), self.error_messages)
            return

    @check_event
    def check_driver_status(self):
        if self.current_hostname not in self.worker_groups:
            return
        if not self.module.get_bin_path('npu-smi'):
            return
        rc, out, err = self.module.run_command('lspci')
        if rc or err:
            util.record_error('can lspci failed: {}'.format(err), self.error_messages)
            return
        if not ('processing_accelerator' in out and 'Device d801' in out):
            return
        devices = glob.glob('/dev/davinci[0-9]*')
        if not devices:
            self.module.warn('no davinci device')
        if not self.module.get_bin_path('hccn_tool'):
            return
        for device in devices:
            device_id = device.replace('/dev/davinci', '')
            cmd = 'hccn_tool -i {} -ip -g'.format(device_id)
            rc, out, err = self.module.run_command(cmd)
            if rc or err:
                util.record_error('run cmd failed: {}'.format(err), self.error_messages)
                return
            if 'ipaddr' not in out:
                self.module.warn('{} has no device IP'.format(device_id))

    def k8s_device_ip_check(self):
        clean_env()
        if self.current_hostname in self.master_groups + self.worker_groups:
            self.check_k8s_version()
        self.check_driver_status()
