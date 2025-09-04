import ipaddress
import socket
import struct

from large_scale_deploy.tools.errors import ParseError, ConfigrationError
from large_scale_deploy.tools import spread_tool


class NetworkTool:

    @staticmethod
    def expand_ip_range(ip_range, step_len=1):
        start_ip, end_ip = ip_range.split('-')
        try:
            start = ipaddress.ip_address(start_ip)
            end = ipaddress.ip_address(end_ip)
        except Exception as e:
            raise ParseError(f"Parse ip range {ip_range} failed: {str(e)}.") from e
        if start >= end:
            raise ParseError(f"Start IP {start} must be less than to end IP {end}.")
        ip_list = []
        current = start
        while current <= end:
            ip_list.append(str(current))
            current += step_len
        if ip_list[-1] != str(end):
            ip_list.append(str(end))
        return ip_list

    @classmethod
    def ip_to_int(cls, ip):
        try:
            if "." in ip:
                return struct.unpack("!I", socket.inet_aton(ip))[0]
            else:
                packed_ip = socket.inet_pton(socket.AF_INET6, ip)
                return int.from_bytes(packed_ip, byteorder='big')
        except Exception as e:
            raise ConfigrationError(f"Incorrect IP format: {ip}. Error: {str(e)}") from e

    @classmethod
    @spread_tool.validate_cmd_result(result_handler=lambda res: str(res).split())
    def get_local_host_ips(cls):
        return spread_tool.run_cmd("hostname -I")
