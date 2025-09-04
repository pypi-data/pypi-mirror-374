#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===========================================================================
import csv
import ipaddress
import os
import re
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class HostInfo:
    def __init__(self, data_list, table_header):
        self.error_msg = []
        self.ip = self.get_option_value("IP", data_list, table_header)
        self.ansible_ssh_user = self.get_option_value("ansible_ssh_user", data_list, table_header)
        self.ansible_ssh_pass = self.get_option_value("ansible_ssh_pass", data_list, table_header)

    def get_option_value(self, option_name, data_list, table_header):
        if not data_list:
            return ""
        if option_name not in table_header:
            self.error_msg.append("Please check whether the {} is in the table".format(option_name))
            return ""
        index = table_header.index(option_name)
        return data_list[index].strip()
    
    def process_check_host(self):
        self.check_ip()
        self.check_ansible_ssh_user()

    @staticmethod
    def is_valid_ip(ip):  # Check if the input string is a valid IP address or IP network.
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(ip)
                return True
            except ValueError:
                pass
        return False

    def check_ip(self):
        if not self.ip:
            self.error_msg.append("Please fill in IP")
            return
        if not self.is_valid_ip(self.ip):
            self.error_msg.append(f"Invalid IP: {self.ip}")

    def check_ansible_ssh_user(self):
        if not self.ansible_ssh_user:
            self.error_msg.append("Please fill in ansible_ssh_user")
            return
        if self.ansible_ssh_user != "root":
            self.error_msg.append(f"Invalid ansible_ssh_user: {self.ansible_ssh_user}")


class HccnHostInfo(HostInfo):
    def __init__(self, host_info_list, var_list, table_header):
        super().__init__(host_info_list, table_header)
        self.gateways = self.get_option_value("gateways", var_list, table_header)
        self.netmask = self.get_option_value("netmask", var_list, table_header)
        self.bitmap = self.get_option_value("bitmap", var_list, table_header)
        self.dscp_tc = self.get_option_value("dscp_tc", var_list, table_header)
        self.common_network = self.get_option_value("common_network", var_list, table_header)
        self.roce_port = 4791
        self.is_ipv6 = False

        if table_header.count("NPU0") == 2:
            device_ip_index = table_header.index('NPU0')
            detect_ip_index = table_header.index('NPU0', device_ip_index + 1)
            self.device_ip = host_info_list[device_ip_index:device_ip_index + 16]
            self.detect_ip = host_info_list[detect_ip_index:detect_ip_index + 16]
        else:
            self.error_msg.append("Please make sure npu id is in the table")
        if self.device_ip:
            self.is_ipv6 = self._is_ipv6(self.device_ip[0])

    def process_check_host(self):
        self.check_ip()
        self.check_ansible_ssh_user()
        self.check_device_ip()
        self.check_detect_ip()
        self.check_deviceip_detectip_number()

    def process_check_var(self):
        self._check_gateways()
        self._check_netmask()
        self._check_bitmap()
        self._check_dscp_tc()
        self._check_common_network()

    def get_host_info(self):
        device_ip = [ip.strip() for ip in self.device_ip if ip]
        device_ip = ",".join(device_ip)
        detect_ip = [ip.strip() for ip in self.detect_ip if ip]
        detect_ip = ",".join(detect_ip)
        host_info = f'{self.ip} ansible_ssh_user="{self.ansible_ssh_user}" '
        if self.ansible_ssh_pass:
            host_info += f'ansible_ssh_pass="{self.ansible_ssh_pass}" '
        host_info += f'deviceip={device_ip} detectip={detect_ip}'
        return host_info

    def get_var_info(self):
        var_info = (f'gateways="{self.gateways}"\n'
                    f'netmask="{self.netmask}"\n'
                    f'roce_port="{self.roce_port}"\n'
                    f'bitmap="{self.bitmap}"\n'
                    f'dscp_tc="{self.dscp_tc}"\n'
                    f'common_network="{self.common_network}"\n')
        return var_info

    @staticmethod
    def _is_ipv6(ip):
        return ":" in ip

    def _get_npu_ip(self, npu_list):
        if all(npu_list) or (all(npu_list[:8]) and not any(npu_list[8:])):
            npu_ips = []
            for npu_ip in npu_list:
                if self.is_valid_ip(npu_ip):
                    if self.is_ipv6 != self._is_ipv6(npu_ip):
                        self.error_msg.append(f"The npu ip {npu_ip} is different from deviceip[0]'s Internet Protocol "
                                              f"version, deviceip, detectip, gateway and netmask all should be set to "
                                              f"IPv4 or IPv6.")
                    npu_ips.append(npu_ip)
                elif npu_ip.strip() == '':
                    pass
                else:
                    self.error_msg.append(f"Invalid npu IP address: {npu_ip}")
            return npu_ips
        self.error_msg.append(f"Please confirm the number of npu ip is correct.The number of npu ip should be "
                              f"8 or 16.The npu ip is {npu_list}")
        return []

    def check_deviceip_detectip_number(self):
        if not self.device_ip or not self.detect_ip:
            return
        device_ip = [ip for ip in self.device_ip if ip]
        detect_ip = [ip for ip in self.detect_ip if ip]
        if len(device_ip) != len(detect_ip):
            self.error_msg.append(f"The valid deviceip's number {len(device_ip)} is different from valid detectip's "
                                  f"number {len(detect_ip)}")

    def check_device_ip(self):
        self.device_ip = self._get_npu_ip(self.device_ip)
        if not self.device_ip:
            return
        duplicate_ip = set([ip for ip in self.device_ip if self.device_ip.count(ip) > 1])
        if duplicate_ip:
            self.error_msg.append(f"The deviceip {duplicate_ip} is set repeatedly, please keep only one")
            return

    def check_detect_ip(self):
        self.detect_ip = self._get_npu_ip(self.detect_ip)

    def _check_bitmap(self):
        if not self.bitmap:
            return
        bitmap_length = 8
        bitmap = self.bitmap.split(",")
        if not all([i in ("0", "1") for i in bitmap]) or len(bitmap) != bitmap_length:
            self.error_msg.append("Invalid bitmap: {}.The bitmap you configured consist of 0 and 1, "
                                  "combined by ',', and the length should be 8".format(self.bitmap))

    def _check_dscp_tc(self):
        if not self.dscp_tc:
            return
        pattern = r"^(\d{1,2}):(\d),$"
        match = re.match(pattern, self.dscp_tc)
        if match:
            dscp_tc = self.dscp_tc.strip(',')
            dscp, tc = map(int, dscp_tc.split(':'))
            if 0 <= dscp <= 63 and 0 <= tc <= 3:
                return
        self.error_msg.append("Invalid dscp_tc: {}".format(self.dscp_tc))

    def _check_common_network(self):
        if self.common_network and self.common_network != "0.0.0.0/0":
            self.error_msg.append("Invalid common_network: {}".format(self.common_network))
        return

    def _check_netmask(self):
        if not self.netmask:
            self.error_msg.append("Please fill in netmask")
            return
        try:
            ipaddress.IPv4Network(f"0.0.0.0/{self.netmask}", strict=False)  # Check for IPv4 netmask
            if self.is_ipv6:
                self.error_msg.append(f"The netmask {self.netmask} is different from deviceip[0]'s Internet Protocol "
                                      f"version, deviceip, detectip, gateway and netmask all should be set to IPv4 or "
                                      f"IPv6.")
        except ValueError:
            if not (self.netmask.isdigit() and 0 <= int(self.netmask) <= 128):  # Check for IPv6 netmask
                self.error_msg.append("Invalid netmask: {}".format(self.netmask))
            elif not self.is_ipv6:
                self.error_msg.append(f"The netmask {self.netmask} is different from deviceip[0]'s Internet Protocol "
                                      f"version, deviceip, detectip, gateway and netmask all should be set to IPv4 or "
                                      f"IPv6.")

    def _check_gateways(self):
        if not self.gateways:
            self.error_msg.append("Please fill in gateways")
            return
        gateways_list = self.gateways.split(',')
        valid_gateways = []
        for gateway in gateways_list:
            gateway = gateway.strip()
            if self.is_valid_ip(gateway):
                if self.is_ipv6 != self._is_ipv6(gateway):
                    self.error_msg.append(f"The gateway {gateway} is different from deviceip[0]'s Internet Protocol "
                                          f"version, deviceip, detectip, gateway and netmask all should be set to IPv4 "
                                          f"or IPv6.")
                valid_gateways.append(gateway)
                continue
            self.error_msg.append("Invalid gateways: {}".format(self.gateways))
        for ip in self.device_ip + self.detect_ip:
            in_same_subnet = False
            for gateway in valid_gateways:
                if self._in_same_subnet(ip, gateway):
                    in_same_subnet = True
            if not in_same_subnet:
                self.error_msg.append("Please check the network configuration. "
                                      "The IP：{} and gateways are not in the same subnet.".format(ip))

    @staticmethod
    def _ip_to_binary(ip):
        if '.' in ip:  # IPv4
            return ''.join(['{0:08b}'.format(int(octet)) for octet in ip.split('.')])
        elif ':' in ip:  # IPv6
            packed_ip = socket.inet_pton(socket.AF_INET6, ip)
            return ''.join(['{0:08b}'.format(byte) for byte in packed_ip])
        return ''

    def _in_same_subnet(self, ip, gateway):
        try:
            ipaddress.IPv4Network(f"0.0.0.0/{self.netmask}", strict=False)  # Check for IPv4 netmask
        except ValueError:
            if not self.netmask.isdigit() or 0 <= int(self.netmask) <= 128:  # Check for IPv6 netmask
                return True
        if not ip or not self.is_valid_ip(ip):
            return True
        ip_binary = self._ip_to_binary(ip)
        gateway_binary = self._ip_to_binary(gateway)
        prefix_length = None
        if '.' in ip and '.' in gateway:  # IPv4
            netmask_binary = self._ip_to_binary(self.netmask)
            prefix_length = netmask_binary.count('1')

        elif ':' in ip and ':' in gateway:  # IPv6
            if '/' in self.netmask:  # Prefix length notation
                prefix_length = int(self.netmask.split('/')[1])
            else:  # Integer notation
                prefix_length = int(self.netmask)

        # All are IPv4 networks or IPv6 networks.
        if not prefix_length:
            self.error_msg.append("Please fill in both the IP:{} and gateway:{} in either IPv4 or IPv6.".format(
                ip, gateway))
            return False
        # netmask:  0.0.0.0(ipv4) or 0(ipv6)
        if prefix_length == 0:
            return True
        return ip_binary[:prefix_length] == gateway_binary[:prefix_length]


class CommonHostInfo(HostInfo):
    def __init__(self, host_info_list, var_list, table_header):
        super().__init__(host_info_list, table_header)
        self.ansible_ssh_port = self.get_option_value("ansible_ssh_port", host_info_list, table_header)
        self.hostname = self.get_option_value("set_hostname", host_info_list, table_header)
        self.npu_num = self.get_option_value("npu_num", host_info_list, table_header)
        self.davinci = self.get_option_value("davinci", host_info_list, table_header)
        scale = self.get_option_value("SCALE", var_list, table_header) or "false"
        self.scale = scale.lower()
        self.runner_ip = self.get_option_value("RUNNER_IP", var_list, table_header)
        self.weights_path = self.get_option_value("WEIGHTS_PATH", var_list, table_header)

    def process_check_host(self):
        self.check_ip()
        self.check_ansible_ssh_user()
        self._check_ansible_ssh_port()
        self._check_hostname()
        self._check_npu_num()
        self._check_davinci()

    def process_check_var(self):
        self._check_scale()
        self._check_runner_ip()
        self._check_weights_path()

    def get_host_info(self):
        host_info = f'{self.ip} ansible_ssh_user="{self.ansible_ssh_user}" '
        if self.ansible_ssh_pass:
            host_info += f'ansible_ssh_pass="{self.ansible_ssh_pass}" '
        if self.ansible_ssh_port:
            host_info += f'ansible_ssh_port="{self.ansible_ssh_port}" '
        if self.hostname:
            host_info += f'set_hostname="{self.hostname}" '
        if self.npu_num:
            host_info += f'npu_num={self.npu_num} '
        if self.davinci:
            host_info += f'davinci={self.davinci} '
        return host_info

    def get_var_info(self):
        if self.scale:
            var_info = f'SCALE="{self.scale}"\n'
        else:
            var_info = 'SCALE="false"\n'
        var_info += f'RUNNER_IP="{self.runner_ip}"\n'
        var_info += f'WEIGHTS_PATH="{self.weights_path}"\n'
        return var_info

    def _check_ansible_ssh_port(self):
        if self.ansible_ssh_port and not (self.ansible_ssh_port.isdigit() and 1 <= int(self.ansible_ssh_port) <= 65535):
            self.error_msg.append("Invalid ansible_ssh_port: {}".format(self.ansible_ssh_port))

    def _check_hostname(self):
        if self.hostname and self.hostname != self.hostname.lower():
            self.error_msg.append("Invalid set_hostname: {}".format(self.hostname))

    def _check_npu_num(self):
        if not self.npu_num:
            return
        if not self.npu_num.isdigit() or int(self.npu_num) < 0 or int(self.npu_num) > 16:
            self.error_msg.append("Invalid npu_num: {}".format(self.npu_num))

    def _check_davinci(self):
        if self.davinci:
            davinci_list = self.davinci.split(',')
            for davinci_id in davinci_list:
                if not davinci_id.isdigit() or int(davinci_id) < 0 or int(davinci_id) > 15:
                    self.error_msg.append("Invalid davinci: {}".format(davinci_id))
                    return
                elif davinci_list.count(davinci_id) != 1:
                    self.error_msg.append("The davinci {} cannot be set repeatedly".format(davinci_id))
        if self.davinci and self.npu_num:
            davinci_num = len(self.davinci.split(','))
            if (self.npu_num.isdigit() and 0 <= int(self.npu_num) < davinci_num) or davinci_num > 16:
                self.error_msg.append(f"The npu_num must be greater than or equal to the number of davinci."
                                      f"The number of davinci is {len(self.davinci.split(','))}. "
                                      f"The npu_num is {int(self.npu_num)}")

    def _check_scale(self):
        scale_valid_value = {"True", "true", "Yes", "yes", "Y", "y", "On", "on", "1", "False", "false", "No", "no", "N",
                         "n", "Off", "off", "0"}
        if self.scale and self.scale not in scale_valid_value:
            self.error_msg.append("Invalid SCALE: {}".format(self.scale))

    def _check_runner_ip(self):
        if self.runner_ip and not self.is_valid_ip(self.runner_ip):
            self.error_msg.append("Invalid RUNNER_IP: {}".format(self.runner_ip))

    def _check_weights_path(self):
        if not self.weights_path:
            if self.davinci:
                self.error_msg.append("Please fill in WEIGHTS_PATH")
            return
        pattern = r'^~?/([a-zA-z0-9_.]+/?)*$'
        if not re.match(pattern, self.weights_path):
            self.error_msg.append("Invalid WEIGHTS_PATH: {}".format(self.weights_path))


class InventoryInfo:
    CSV_FILE_NAME = 'inventory_template.csv'
    MASTER_SEC = "master"
    WORKER_SEC = "worker"
    NPU_NODE_SEC = "npu_node"
    HCCN_SEC = "hccn"
    OTHER_BUILD_IMAGE_SEC = "other_build_image"
    HOST_SECS = [MASTER_SEC, WORKER_SEC, HCCN_SEC, OTHER_BUILD_IMAGE_SEC, NPU_NODE_SEC]
    HCCN_VARS = ('gateways=""\n'
                'netmask=""\n'
                'roce_port=""\n'
                'bitmap=""\n'
                'dscp_tc=""\n'
                'common_network=""\n')
    ALL_VARS = ('SCALE="false"\n'
                'RUNNER_IP=""\n'
                'WEIGHTS_PATH=""\n')

    def __init__(self):
        self.error_msg = []
        self.table_header = []
        self.hosts_info = {
            self.HCCN_SEC: [],
            self.MASTER_SEC: [],
            self.WORKER_SEC: [],
            self.NPU_NODE_SEC: [],
            self.OTHER_BUILD_IMAGE_SEC: []
        }

    def get_table_info(self):
        hosts_info_list = []
        vars_info_list = []
        csv_file_path = os.path.join(os.getcwd(), self.CSV_FILE_NAME)
        if not os.path.exists(csv_file_path):
            raise Exception(f"File {csv_file_path} not found")
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if not any(row):
                    continue
                if 'IP' in row and 'ansible_ssh_user' in row:
                    self.table_header.extend(row)
                    continue
                if row[0].strip().lower() in self.HOST_SECS:
                    hosts_info_list.append(row)
                    if not vars_info_list:
                        vars_info_list = row
        if not self.table_header:
            raise Exception('Please make sure "IP" and "ansible_ssh_user" are in the table')
        return hosts_info_list, vars_info_list

    def trans_to_inventory_info(self, hosts_info_list, vars_info_list):
        for host_info in hosts_info_list:
            if not host_info:
                continue
            if host_info[0].strip().lower() != self.HCCN_SEC:
                host = CommonHostInfo(host_info, vars_info_list, self.table_header)
            else:
                host = HccnHostInfo(host_info, vars_info_list, self.table_header)
            host.process_check_host()
            host.process_check_var()
            if host.error_msg:
                self.error_msg.extend(host.error_msg)
            self.hosts_info.setdefault(host_info[0].strip().lower(), []).append(host)

        if self.error_msg:
            err_msg = set(self.error_msg)
            raise Exception("\n".join(err_msg))

    def write_inventory(self):
        with open('inventory_file', mode='w', encoding='utf-8') as file:
            # write hosts information
            for host_sec in self.hosts_info.keys():
                file.write(f"[{host_sec}]\n")
                for host in self.hosts_info[host_sec]:
                    host_info = host.get_host_info()
                    file.write(f"{host_info}\n")
                file.write('\n')

            # write hccn vars information
            hccn_vars = self.HCCN_VARS
            hccn_host_info = self.hosts_info.get(self.HCCN_SEC)
            if hccn_host_info:
                hccn_vars = hccn_host_info[0].get_var_info()
            file.write("[hccn:vars]\n")
            file.write(hccn_vars)
            file.write('\n')

            # write all vars information
            all_vars = self.ALL_VARS
            host_info = self.hosts_info.get(self.WORKER_SEC) or self.hosts_info.get(self.MASTER_SEC)
            if host_info:
                all_vars = host_info[0].get_var_info()
            file.write("[all:vars]\n")
            file.write(all_vars)
            file.write('\n')
        logging.info("Data has been written to the inventory_file successfully.")

    def run(self):
        hosts_info_list, vars_info_list = self.get_table_info()
        self.trans_to_inventory_info(hosts_info_list, vars_info_list)
        self.write_inventory()


if __name__ == '__main__':
    InventoryInfo().run()
