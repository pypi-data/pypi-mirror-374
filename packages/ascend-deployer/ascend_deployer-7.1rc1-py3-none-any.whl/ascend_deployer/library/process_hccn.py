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
import os
import socket

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.check_utils import CheckUtil
from ansible.module_utils.common_info import NPUCardName


class CommonInfo:

    def __init__(self, device_ip, sub_network, detect_ip, gateway):
        # str
        self.device_ip = device_ip
        # str, only exists when ipv4
        self.sub_network = sub_network
        # str
        self.detect_ip = detect_ip
        # str
        self.gateway = gateway


class BaseModule(object):

    def __init__(self):

        self.module = AnsibleModule(
            argument_spec=dict(
                device_ips=dict(type='list', required=True),
                gateways=dict(type='list', required=True),
                netmask=dict(type='str', required=True),
                detect_ips=dict(type='list', required=True),
                common_network=dict(type='str', required=True),
                bitmap=dict(type='str', required=False),
                dscp_tc=dict(type='str', required=False),
                roce_port=dict(type="str", required=True)
            ))

        self.device_ips = self.module.params.get("device_ips")
        self.gateways = self.module.params.get("gateways")
        self.netmask = self.module.params.get("netmask")
        self.detect_ips = self.module.params.get("detect_ips")
        self.common_network = self.module.params.get("common_network")
        self.bitmap = self.module.params.get("bitmap")
        self.dscp_tc = self.module.params.get("dscp_tc")
        self.roce_port = self.module.params.get("roce_port")

        self.working_on_ipv6 = self._is_ipv6(self.device_ips)
        self.npu_name = self._get_npu_name()

    @staticmethod
    def _is_ipv6(ip):
        """
        judge the ip is ipv6 or not by simply checking ':' whether in ip or not.
        Args:
            ip: support list[str] and str.
        """
        if isinstance(ip, list):
            return ":" in ip[0] if len(ip) > 0 else False
        return ":" in ip


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


class Template(BaseModule):

    _IP_RULE_TEMPLATE = "ip_rule_{}=add from {} table {}\n"
    _IP_ROUTE_TEMPLATE = "ip_route_{}=add {} via {} dev eth{} table {}\n"
    _IPV4_ADDRESS_TEMPLATE = "address_{}={}\nnetmask_{}={}\nnetdetect_{}={}\n"
    _IPV6_ADDRESS_TEMPLATE = "IPv6address_{}={}\nIPv6netmask_{}={}\nIPv6netdetect_{}={}\n"
    _ROCE_PORT_TEMPLATE = "roce_port_{}={}\n"
    _ARP_SEND_TEMPLATE = "send_arp_status_{}={}\n"
    _DSCP_TC_TEMPLATE = "dscp_tc_{}={}\n"
    _BITMAP_TEMPLATE = "bitmap_{}={}\n"

    _IPV4_GATEWAY_TEMPLATE = "gateway_{}={}\n"
    _IPV6_GATEWAY_TEMPLATE = "IPv6gateway_{}={}\n"
    _ARP_TEMPLATE = "arp_{}=-i eth{} -s {} {}\n"

    def __init__(self):
        super(Template, self).__init__()

    def _get_basic_defines(self, common_info, npu_id):
        if self.working_on_ipv6:
            template = Template._IPV6_ADDRESS_TEMPLATE
        else:
            template = Template._IPV4_ADDRESS_TEMPLATE
        conf = template.format(npu_id, common_info.device_ip, npu_id,
                                  self.netmask, npu_id, common_info.detect_ip)
        if self.dscp_tc.strip():
            conf += Template._DSCP_TC_TEMPLATE.format(npu_id, self.dscp_tc)
        if self.bitmap.strip():
            conf += Template._BITMAP_TEMPLATE.format(npu_id, self.bitmap)
        return conf

    def _get_gateway_defines(self, common_info, npu_id):
        if self.working_on_ipv6:
            template = Template._IPV6_GATEWAY_TEMPLATE
        else:
            template = Template._IPV4_GATEWAY_TEMPLATE
        return template.format(npu_id, common_info.gateway)

    def generate_hccn_conf(self, basic_info, is_standard_npu_card, gateway_set, mac_addresses):
        """
        This function is maily to generate the hccn configuration
        Args:
            basic_info: npu info sets, example: {npu_id: CommonInfo}
            is_standard_npu_card: bool, 非模组形态
            gateway_set: the set of gateways
            mac_addresses: npu_id: mac_address
        """
        conf = ""
        if self.npu_name == NPUCardName.A910A2:
            # same operation for generating conf both ipv4 and both ipv6
            for npu_id, common_info in basic_info.items():
                conf += self._get_basic_defines(common_info, npu_id)
                conf += self._get_gateway_defines(common_info, npu_id)
            return conf

        # 910A1 and 910A3
        # only ipv4
        table_start = 100
        first_group = (0, 1, 2, 3)
        second_group = (4, 5, 6, 7)
        for npu_id, common_info in basic_info.items():
            table_id = table_start + npu_id
            conf += self._get_basic_defines(common_info, npu_id)
            conf += self._get_gateway_defines(common_info, npu_id)

            # 非模组形态
            if is_standard_npu_card:
                continue

            conf += Template._IP_RULE_TEMPLATE.format(npu_id, common_info.device_ip, table_id)
            conf += Template._IP_ROUTE_TEMPLATE.format(
                npu_id, self.common_network, common_info.gateway, npu_id, table_id)

            # 非全连接组网
            # Here is not list, len(set("192.168.0.1")) == 11
            if len(gateway_set) > 1:
                continue

            conf += Template._IP_ROUTE_TEMPLATE.format(
                npu_id, common_info.sub_network, common_info.device_ip, npu_id, table_id)

            group = first_group if npu_id in first_group else second_group
            for npu_id_two in group:
                if npu_id != npu_id_two:
                    conf += Template._ARP_TEMPLATE.format(
                        npu_id,
                        npu_id,
                        basic_info[npu_id_two].device_ip,
                        mac_addresses[npu_id_two],
                    )
        return conf


class IPUtils(BaseModule):

    _SEPARATE_MARK_DOT = "."

    def __init__(self):
        super(IPUtils, self).__init__()

    def _get_ipv6_subnet(self, ip):
        truncated_ip = ""
        try:
            ip = socket.inet_pton(socket.AF_INET6, ip).hex()
            ip_bin = bin(int(ip, 16)).replace('0b', '')
            truncated_ip = ip_bin[:int(self.netmask)]
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][[ERROR]] Invalid IPV6 address: {} or netmask: {}.".format(ip, self.netmask)
            )
        return truncated_ip

    def _is_same_ipv6_subnet(self, ip, gateway):
        return self._get_ipv6_subnet(ip) == self._get_ipv6_subnet(gateway)

    def _get_ipv4_subnet(self, gateway):
        # convert self.netmask to prefix length
        # split netmask by ".", convert the number to binary string, count the "1"
        # 255.255.224.0 -> 11111111.11111111.11100000.00000000 -> 19 (count of "1")
        prefix_length = sum(bin(int(octet)).count("1") for octet in self.netmask.split(self._SEPARATE_MARK_DOT))
        gateway_ip_octets = [int(octet) for octet in gateway.split(self._SEPARATE_MARK_DOT)]
        subnet_mask_octets = [int(octet) for octet in self.netmask.split(self._SEPARATE_MARK_DOT)]
        network_address_octets = [gateway_ip_octets[i] & subnet_mask_octets[i] for i in range(4)]
        network_address = ".".join([str(octet) for octet in network_address_octets])
        return "{}/{}".format(network_address, prefix_length)

    @staticmethod
    def _convert_ipv4_to_int(ip):
        oct_multiple = 8
        return sum(int(octet) << (oct_multiple * i) for i, octet in enumerate(reversed(ip.split('.'))))

    def _is_ipv4_in_subnet(self, ip, gateway):

        ip_int = self._convert_ipv4_to_int(ip)
        gateway_ip_int = self._convert_ipv4_to_int(gateway)
        subnet_mask_int = self._convert_ipv4_to_int(self.netmask)
        return (ip_int & subnet_mask_int) == (gateway_ip_int & subnet_mask_int)

    def get_ipv4_gateway(self, ip):
        for gateway in self.gateways:
            network = self._get_ipv4_subnet(gateway)
            if self._is_ipv4_in_subnet(ip, gateway):
                return gateway, network
        return "", ""

    def get_ipv6_gateway(self, ip):
        for gateway in self.gateways:
            if self._is_same_ipv6_subnet(ip, gateway):
                matching_gateway = gateway
                return matching_gateway
        return ""


class HCCN(BaseModule):
    """
    hccn-tool is a tool that different NPU card could communicate.
    Here we parse and valid the input params, then execute hccn_tool.
    HCCN now only supports 910A1, 910A2, 910A3.
    Please refer to ascend_deployer/library/check_hccn.py see more detail.
    """

    _HCCN_CONF_PATH = "/etc/hccn.conf"
    _FILE_OPEN_MODE = 0o644

    def __init__(self):
        super(HCCN, self).__init__()

        self.ip_utils = IPUtils()
        self.template = Template()

    def _run_cmd(self, cmd, display_out=False):
        rc, out, err = self.module.run_command(cmd)
        if rc != 0 or err != "":
            msg = "[ASCEND][[ERROR]] Call '{}' failed: ".format(cmd)
            if display_out:
                msg += out
            else:
                msg += str(err)
            self.module.fail_json(changed=False, rc=1, msg=msg)
        return out

    def _get_npu_ids(self):
        """
        This function is mainly to gather all the NPU ID by command: npu-smi info -m
        return a list contains int value which indicates npu id.

        if the card is 910A1 or 910A2:
            Got the 1rt column of output, which displayed as NPU ID

            -----------example of the output---------------
            910A1:
            NPU ID            Chip ID            Chip Logic ID            Chip Name
            0                   0                     0                   Ascend 910A
            1                   0                     1                   Ascend 910A
            2                   0                     2                   Ascend 910A

            910A2
            NPU ID            Chip ID            Chip Logic ID            Chip Name
            0                   0                     0                   Ascend 910xx
            0                   0                     -                   MCU
            1                   0                     1                   Ascend 910xx
            1                   1                     -                   MCU
            2                   0                     2                   Ascend 910xx
            2                   0                     -                   MCU


        if the card is 910A3:
            Got the 4th column of output, which displayed Chip Phy-ID
            -----------example of the output---------------
            NPU ID            Chip ID            Chip Logic ID            Chip Phy-ID            Chip Name
            0                   0                     0                   0                       Ascend910
            0                   1                     1                   1                       Ascend910
            0                   2                     -                   -                       Mcu
            1                   0                     2                   2                       Ascend910
        """
        npu_info = self._run_cmd("npu-smi info -m")
        #for 910A1 and 910A2
        keyword1 = "Ascend 910"
        # for 910A3
        keyword2 = "Ascend910"

        npu_ids = []
        for line in npu_info.split("\n"):
            if keyword1 in line:
                npu_id = line.strip().split()[0]
            elif keyword2 in line:
                npu_id = line.strip().split()[3]
            else:
                continue
            if npu_id.isdigit():
                npu_ids.append(int(npu_id))
        if not npu_ids:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][[ERROR]] No training devices found! Please confirm."
            )
        return npu_ids

    def _is_standard_npu_card(self, npu_id):
        """
        This function is mainly to judge current NPU card is standard card or not.
        Using npu-smi info -t board -i {npu_id} get all the information of the board.
        is the value of Board ID is in the standard_card_board_ids, it's standard card.

        Args:
            npu_id: the id of the npu, you can get it from _get_npu_ids
        """
        cmd = "npu-smi info -t board -i {}".format(npu_id)
        npu_info = self._run_cmd(cmd)
        """A standard output:
            NPU ID               : 0
            Product Name         : IT21HMDC_Bin6x
            Model                : NA
            Manufacturer         : Huawei
            Serial Number        : 1000000000
            Software Version     : 24.1.0.b062
            Firmware Version     : 7.5.0.2.220
            Compatibility        : OK
            Board ID             : 0x67
            PCB ID               : A
            BOM ID               : 1
            PCIe Bus Info        : 0000:C1:00.0
            Slot ID              : 0
            Class ID             : NA
            PCI Vendor ID        : 0x19E5
            PCI Device ID        : 0xD802
            Subsystem Vendor ID  : 0x19E5
            Subsystem Device ID  : 0x3002
            Chip Count           : 1
        """

        standard_card_board_ids = ("0xc0", "0xdf", "0xe1")
        for line in npu_info.split("\n"):
            if "Board ID" in line:
                new_line = line.lower().split(":")
                if len(new_line) > 1 and new_line[1].strip() in standard_card_board_ids:
                    return True
        return False

    def _get_mac_address(self, npu_id):
        """
        This function is maily to obtain the mac address by given npu_id.
        return a mac_address.

        Using hccn_tool -i {npu_id} -mac -g to get the mac address.
        """
        cmd = "hccn_tool -i {} -mac -g".format(npu_id)
        mac = self._run_cmd(cmd)
        # example: "mac addr: 06:0c:b4:96.bc:85"
        mac_address = mac.replace("mac addr:", "").strip()
        return mac_address

    def ipv6_support(self):
        """
        3 kinds of NPU:
            910A1: only support IPV4 configuration.
            910A2: both support IPV4 and IPV6
            910A3: support IPV4, IPV6 support has been temporary banned.
        """
        support_ipv6 = [NPUCardName.A910A2]

        if self.working_on_ipv6 and self.npu_name not in support_ipv6:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][[ERROR]] Current NPU Do not support HCCN, please confirm."
            )

    def generate_basic_info(self, npu_ids):
        """
        This function is mainly to generate basic info of npu:
        return two values:
            basic_info: a map which key is npu id and value is CommonInfo of this npu
            gateway_set: set of gateways
        """
        gateway_set = set()
        basic_info = {} # npu_id: CommonInfo
        for npu_id, device_ip, detect_ip in zip(
                npu_ids,
                self.device_ips,
                self.detect_ips
        ):
            matching_network = ""
            if self.working_on_ipv6:
                matching_gateway = self.ip_utils.get_ipv6_gateway(device_ip)
            else:
                matching_gateway, matching_network = self.ip_utils.get_ipv4_gateway(device_ip)

            basic_info[npu_id] = CommonInfo(device_ip, matching_network, detect_ip, matching_gateway)
            gateway_set.add(matching_gateway)

        return basic_info, gateway_set

    def process_recovery(self):
        npu_ids = self._get_npu_ids()
        is_standard_npu_card = self._is_standard_npu_card(npu_ids[0])
        basic_info, gateway_set = self.generate_basic_info(npu_ids)
        mac_addresses = {npu_id: self._get_mac_address(npu_id) for npu_id in npu_ids}

        conf = self.template.generate_hccn_conf(
            basic_info, is_standard_npu_card, gateway_set, mac_addresses)

        fd = os.open(self._HCCN_CONF_PATH, os.O_RDWR | os.O_CREAT | os.O_TRUNC, self._FILE_OPEN_MODE)
        with os.fdopen(fd, 'w') as f:
            f.write(conf)

        """
        this cmd will cause partial err
        A standard result of this cmd(using self.module.run_command API):
        rc: 1
        out: 
            dev:0 recovery fail
            dev:1 recovery success
            dev:2 recovery success
            dev:3 recovery success
            dev:4 recovery success
            dev:5 recovery success
            dev:6 recovery success
            dev:7 recovery success
            Command execute failed!
            Recovery failed. Check '/var/log/hccn_tool/hccn_config.log' for details.
        err:
            dev:0 recovery fail\nCommand execute failed.\n
            
        So we just need to only display the out for the users.
        """

        self._run_cmd("hccn_tool -a -cfg recovery", display_out=True)

    def run(self):
        self.ipv6_support()
        self.process_recovery()
        self.module.exit_json(changed=True, rc=0)


if __name__ == "__main__":
    HCCN().run()
