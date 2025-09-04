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
import re
import socket

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.check_utils import CheckUtil
from ansible.module_utils.check_utils import CallCmdException
from ansible.module_utils.common_info import NPUCardName
from ansible.module_utils.common_utils import is_valid_ip


class HccnCheck:
    """
    All the check rule based on the Document:
    https://www.hiascend.com/document/detail/zh/mindx-dl/60rc3/ascenddeployer/ascenddeployer/deployer_0025.html

    function explanation:
    self.module.fail_json():
        break the process, and return the error msg immediately

    CheckUtil.record_error():
        Add the error msg to Ansible, but the process will not be blocked.

    if the next process will use the data you process, so you need to validate the data and use:
        self.module.fail_json()
    But the data will not be used in the next process, you just want to display this error msg to user, use:
        CheckUtil.record_error()
    """

    _SUPPORT_DEVICES = [NPUCardName.A910A1, NPUCardName.A910A2, NPUCardName.A910A3]
    _IPV6_SUPPORT = [NPUCardName.A910A2]

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                device_ips=dict(type='list', required=True),
                gateways=dict(type='list', required=True),
                netmask=dict(type='str', required=True),
                detect_ips=dict(type='list', required=True),
                common_network=dict(type='str', required=True),
                bitmap=dict(type='str', required=False),
                dscp_tc=dict(type='str', required=False)
            ))
        self.device_ips = self.module.params.get("device_ips")
        self.gateways = self.module.params.get("gateways")
        self.netmask = self.module.params.get("netmask")
        self.detect_ips = self.module.params.get("detect_ips")
        self.common_network = self.module.params.get("common_network")
        self.bitmap = self.module.params.get("bitmap")
        self.dscp_tc = self.module.params.get("dscp_tc")

        self.npu_name = self._get_npu_name()
        self.npu_count = self._get_npu_count()
        self.error_messages = []

    @staticmethod
    def _get_npu_name():
        npu = CheckUtil.get_card()
        if npu.endswith("b"):
            return NPUCardName.A910A2
        elif npu.endswith("93"):
            return NPUCardName.A910A3
        elif npu.endswith("910"):
            return NPUCardName.A910A1
        else:
            return npu

    def _get_npu_count(self):
        cmd = "lspci | grep -E 'accelerators.*Huawei.*Device' | wc -l "
        try:
            out = CheckUtil.run_cmd(cmd, CheckUtil.GREP_RETURN_CODE)
        except CallCmdException as err:
            return self.module.fail_json(
                changed=False, rc=1, msg="[ASCEND][[ERROR]] Call lspci failed:{}".format(str(err)))
        return int(out)

    @staticmethod
    def _is_ipv6(ip):
        return ":" in ip


    def _is_valid_netmask(self, netmask):
        # IPv4
        if '.' in netmask:
            octets = netmask.split('.')
            if len(octets) != 4:
                return False
            if any(not octet.isdigit() or int(octet) > 255 for octet in octets):
                return False
            binary_netmask = self._ip_to_binary(netmask)
            return '01' not in binary_netmask

        # IPv6
        elif ':' in netmask:  # CIDR
            if netmask.count('/') == 1:
                prefix_length = int(netmask.split('/')[1])
                return 0 <= prefix_length <= 128
        elif netmask.isdigit():  # # Integer notation
            prefix_length = int(netmask)
            return 0 <= prefix_length <= 128
        return False

    def _ip_to_binary(self, ip):
        if '.' in ip:  # IPv4
            return ''.join(['{0:08b}'.format(int(octet)) for octet in ip.split('.')])
        elif ':' in ip:  # IPv6
            packed_ip = socket.inet_pton(socket.AF_INET6, ip)
            return ''.join(['{0:08b}'.format(b if isinstance(b, int) else ord(b)) for b in packed_ip])

        return self.module.fail_json(changed=False,
                                     rc=1,
                                     msg="Invalid IP：{} address format".format(ip))

    def _in_same_subnet(self, ip, gateway):
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
            CheckUtil.record_error(
                "[ASCEND][ERROR] Please fill in both the IP:{} and gateway:{} in either IPv4 or IPv6.".format(
                    ip, gateway),
                self.error_messages)
            return False
        # netmask:  0.0.0.0(ipv4) or 0(ipv6)
        if prefix_length == 0:
            return True
        return ip_binary[:prefix_length] == gateway_binary[:prefix_length]

    def check_bitmap(self):
        """bitmap is an optional parameter;
        checking by following rules:
        - the length of bitmap should match the npu_count
        - all the value in bitmap should be '0' or '1'

        """

        bitmap_length = 8

        if self.bitmap:
            bitmap = self.bitmap.split(",")
            if not all([i in ("0", "1") for i in bitmap]) or len(bitmap) != bitmap_length:
                self.module.fail_json(
                    changed=False,
                    rc=1,
                    msg="[ASCEND][ERROR] The bitmap you configured in the inventory_file "
                        "consist of 0 and 1, combined by ',', and the length should be 8"
                )

    def check_dscp_tc(self):
        """
        The format of dscp_tc is: DCSP:TC, (Do not forget the "," at the end of data), e.g. "22:0,"

        Validation is based on the following rules:
        1. The number of dscp is between 0 and 63
        2. The number of tc is between 0 and 3
        """

        dscp_min, dscp_max = 0, 63
        tc_min, tc_max = 0, 3

        err_msg = (
            "[ASCEND][ERROR] The dscp_tc you configured in the inventory_file is not correct. "\
            "dscp must be between {} and {}, tc must be between {} and {} and match the priority queue in bitmap."\
            "You can configure it as empty or strict follow the rules."
        ).format(dscp_min, dscp_max, tc_min, tc_max)

        if not self.dscp_tc:
            return
        pattern = r"^(\d{1,2}):(\d),$"
        match = re.match(pattern, self.dscp_tc)
        if not match:
            err_msg += ("Please correct it and retry. Your value: {}".format(self.dscp_tc))
            CheckUtil.record_error(err_msg, self.error_messages)
            return
        dscp, tc = int(match.group(1)), int(match.group(2))
        if dscp_min <= dscp <= dscp_max and tc_min <= tc <= tc_max:
            return
        CheckUtil.record_error(err_msg, self.error_messages)
        return

    def check_support(self):
        """This function is mainly to check whether the NPU support HCCN or not.
        """
        if self.npu_name not in self._SUPPORT_DEVICES:
            msg = "[ASCEND][ERROR] Only {} support HCCN, please check your NPU card".format(
                ", ".join(self._SUPPORT_DEVICES))
            self.module.fail_json(changed=False, rc=1, msg=msg)

    def check_ip(self):
        """
        This function is mainly to validate whether the deviceip and detectip configured right or not.
        A standard format of deviceip/detectip is :
        IPV4:
        10.20.0.1,10.20.0.1,10.20.0.1,10.20.0.1,10.20.0.1,10.20.0.1,10.20.0.1,10.20.0.1
        IPV6:
        fec0:0090:1c02::2001,fec0:0090:1c02::2001,fec0:0090:1c02::2001,fec0:0090:1c02::2001,fec0:0090:1c02::2001

        check base on the rule:
        1. whether the number of ips is equal to the number of NPU or not.
        2. is the ip in IPV4 validate or not.
        3. ipv4 and ipv6 configured respectively, DO NOT combine them as one data.
        """
        ip_maps = {"deviceip": self.device_ips, "detectip": self.detect_ips}
        for name, ips in ip_maps.items():
            if not ips:
                self.module.fail_json(
                    changed=False,
                    rc=1,
                    msg="[ASCEND][ERROR] Please configure the {} in inventory_file.".format(name)
                )
                return
            if self.npu_count != len(ips):
                CheckUtil.record_error(
                    "[ASCEND][ERROR] The number of {0} is inconsistent with the number of NPU in position. "
                    "Please check whether the NPU cards are in position or whether {0} "
                    "in inventory_file is correctly configured.".format(name), self.error_messages)
                return

            error_ips = [(name, ip) for ip in ips if not is_valid_ip(ip)]
            if error_ips:
                msg = '\n'.join(["[ASCEND][ERROR] {} {} is not a valid ip.".format(i[0], i[1]) for i in error_ips])
                self.module.fail_json(changed=False, rc=1, msg=msg)
                return

            ip_categories = [self._is_ipv6(ip) for ip in ips]
            if sum(ip_categories) != 0 and sum(ip_categories) != self.npu_count:
                CheckUtil.record_error(
                    "[ASCEND][ERROR] The {0} ip you configured should all be IPV6 or IPV4."
                    "Do not combine them.".format(name), self.error_messages)
                return

            if self._is_ipv6(ips[0]) and self.npu_name not in self._IPV6_SUPPORT:
                CheckUtil.record_error(
                    "[ASCEND][ERROR] The {0} ip you configured DO NOT support IPV6."
                    "Only {1} support IPV6.".format(name, ",".join(self._IPV6_SUPPORT)), self.error_messages)
                return

    def check_gateways(self):
        if not self.gateways:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Please configure the gateways in inventory_file first.")
        for gateway in self.gateways:
            if not is_valid_ip(gateway):
                self.module.fail_json(changed=False,
                                      rc=1,
                                      msg="[ASCEND][ERROR] Gateway {} is not a valid IP.".format(gateway))

    def check_netmask(self):
        if not self.netmask:
            self.module.fail_json(changed=False,
                                  rc=1,
                                  msg="[ASCEND][ERROR] Please configure the netmask in inventory_file first.")

        if not self._is_valid_netmask(self.netmask):
            self.module.fail_json(changed=False,
                                  rc=1,
                                  msg="[ASCEND][ERROR] Netmask {} is not a valid netmask.".format(self.netmask))

    def check_configuration(self):
        for ip in self.device_ips:
            found_gateway = False  # flag indicating whether a gateway that meets the requirements has been found

            # iterate through each gateway
            for gateway in self.gateways:
                if self._in_same_subnet(ip, gateway):
                    found_gateway = True  # find a gateway that meets the requirements
                    break

            if not found_gateway:
                CheckUtil.record_error("[ASCEND][ERROR] Please check the network configuration in the inventory_file."
                                  " The IP：{} are not in the same subnet.".format(ip),
                                  self.error_messages)
                return

    def check_common_network(self):
        """
        Validation based on the following rules:
        1. If the product is one of:
            - 910A2
            common_network should be empty or 0.0.0.0/0
        2. If the product is one of:
            - 910A1
            - 910A3
            common_network should only be: "0.0.0.0/0"
        """
        default_common_network = "0.0.0.0/0"
        if self.npu_name == NPUCardName.A910A2:
            if self.common_network == "" or self.common_network == default_common_network:
                return
            CheckUtil.record_error("[ASCEND][ERROR] The common_network you configured should be '' or '0.0.0.0/0'",
                              self.error_messages)
            return
        # 910A1 or 910A3
        if self.common_network != default_common_network:
            CheckUtil.record_error("[ASCEND][ERROR] The common_network you configured should be '0.0.0.0/0'",
                              self.error_messages)
            return

    def run(self):
        self.check_support()
        self.check_ip()
        self.check_gateways()
        self.check_netmask()
        self.check_configuration()
        self.check_common_network()
        self.check_bitmap()
        self.check_dscp_tc()
        if self.error_messages:
            return self.module.fail_json('\n'.join(self.error_messages))
        self.module.exit_json(changed=True, rc=0)


if __name__ == '__main__':
    HccnCheck().run()
