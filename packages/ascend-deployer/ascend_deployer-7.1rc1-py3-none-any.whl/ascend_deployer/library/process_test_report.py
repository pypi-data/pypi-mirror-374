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
import json
import os.path
import codecs

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common_utils import generate_table
from ansible.module_utils.path_manager import TmpPath
from ansible.module_utils.common_info import TestReport


def to_json(file_path, table_name, data):
    """
    description: 将test结果转换成json文件
    """
    with codecs.open(file_path, "a+", encoding="utf8") as f:
        f.seek(0)
        if not f.read().strip():
            json_data = dict()
        else:
            f.seek(0)
            json_data = json.load(f)
        test_data = {table_name: data}
        json_data.update(test_data)
        f.seek(0)
        f.truncate()
        f.write(json.dumps(json_data, ensure_ascii=False))


def list_to_dict(result_list):
    result_dict = {}
    for item in result_list:
        for key, value in item.items():
            if key not in result_dict:
                result_dict[key] = value
            else:
                result_dict[key].update(value)
    return result_dict


def generate_test_result_table(module, cann_result, dl_result):
    # 生成表
    table_npu = generate_table(cann_result, "npu-clusters", TestReport.COLUMNS_NPU, "npu")
    table_mcu = generate_table(cann_result, "mcu-version", TestReport.COLUMNS_MCU, "ip")

    table_cann = generate_table(cann_result, "cann-clusters", TestReport.COLUMNS_CANN, "cann")
    table_pypkg = generate_table(cann_result, "pypkg-clusters", TestReport.COLUMNS_PYPKG, "pypkg")

    cann_table_result_str = "{}\n\n{}\n\n{}\n\n{}\n".format(table_npu, table_mcu, table_cann, table_pypkg)

    # 生成管理节点表和计算节点表
    table_master = generate_table(dl_result, "dl-clusters(master-node)", TestReport.COLUMNS_MASTER, "master-node")
    table_worker_pod = generate_table(dl_result, "dl-clusters(worker-node)", TestReport.COLUMNS_WORKER_POD,
                                      "worker-node")
    table_worker_physical = generate_table(dl_result, "dl-clusters(worker-node-physical)",
                                           TestReport.COLUMNS_WORKER_PHYSICAL, "worker-node")

    cann_test_result_str = dl_test_result = ""
    for node in module.params["cann_test_result"]:
        cann_test_result_str += '\n{}'.format(node)
    for node in dl_result:
        dl_test_result += '\n{}: {}'.format(node, dl_result.get(node))

    table_result_str = "[ASCEND]{}\n{}\n\n\n{}\n\n{}\n\n{}\n\n{}\n".format(cann_test_result_str, dl_test_result,
                                                                           cann_table_result_str, table_master,
                                                                           table_worker_pod, table_worker_physical)

    return table_result_str


def output_test_result_json(cann_result, dl_result):
    if os.path.exists(TmpPath.TEST_REPORT_JSON):
        os.remove(TmpPath.TEST_REPORT_JSON)
    if not os.path.exists(TmpPath.DEPLOY_INFO):
        os.makedirs(TmpPath.DEPLOY_INFO)
    to_json(TmpPath.TEST_REPORT_JSON, TestReport.ASCEND_SOFTWARE_TEST_REPORT, cann_result)
    to_json(TmpPath.TEST_REPORT_JSON, TestReport.DL_TEST_REPORT, dl_result)


def main():
    module = AnsibleModule(argument_spec=dict(
        cann_test_result=dict(type="list", required=True),
        docker_runtime_result=dict(type="list", required=True),
        dl_result=dict(type="dict", required=True)
    )
    )

    dl_result = module.params["dl_result"]
    cann_result = list_to_dict(module.params["cann_test_result"])
    docker_runtime_result = list_to_dict(module.params["docker_runtime_result"])

    # 合并docker runtime和其他组件的结果
    temp_updates = {}

    for key, value in docker_runtime_result.items():
        for host_info in dl_result:
            if key == host_info.split(':')[0].strip():
                dl_result[host_info].update(value)
                break
        else:
            # 如果未找到匹配的 host_info，则直接添加新键值对
            temp_updates[key] = value

    dl_result.update(temp_updates)

    table_result_str = generate_test_result_table(module, cann_result, dl_result)
    output_test_result_json(cann_result, dl_result)

    return module.exit_json(changed=True, rc=0, msg=table_result_str)


if __name__ == "__main__":
    main()
