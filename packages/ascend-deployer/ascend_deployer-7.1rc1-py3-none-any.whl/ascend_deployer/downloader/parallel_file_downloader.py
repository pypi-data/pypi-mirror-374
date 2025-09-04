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
import random
import socket
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import multiprocessing
from urllib import request
from urllib.parse import urlparse

from . import logger_config
from .download_util import Color, DownloadError, calc_sha256, DownloadUtil, is_exists, delete_if_exist, \
    DownloadCheckError, calc_md5, get_remote_content_length, DOWNLOAD_INST, UrlOpenError, UrlOpenErrInfo

LOG = logger_config.LOG


class DownloadingStatus:

    def __init__(self, pkg_name: str, speed: float, percent: float, total_size: float):
        self.pkg_name = pkg_name
        self.speed = speed
        self.percent = percent
        self.total_size = total_size

    def get_speed_str(self):
        if self.speed < 1024:
            speed_str = r" {:.2f} KB/s".format(self.speed)
        else:
            speed_str = r" {:.2f} MB/s".format(self.speed / 1024)
        return speed_str

    def get_percent_str(self):
        return "{:.2f}%".format(self.percent * 100)

    def get_pkg_str(self):
        if len(self.pkg_name) > 50:
            pkg_str = self.pkg_name[:47] + "..."
        else:
            pkg_str = self.pkg_name
        return pkg_str

    def get_progress_str(self):
        progress_str_weight = round(self.percent * 30)
        if self.percent == 1:
            progress_str = ('=' * progress_str_weight)
        else:
            progress_str = ('=' * (progress_str_weight - 1) + '>').ljust(30, '-')
        return progress_str

    def get_downloading_print_str(self):
        return Color.info("start downloading ") \
            + self.get_pkg_str().ljust(53, ' ') + ' ' \
            + self.get_percent_str().ljust(7, ' ') \
            + '[' + self.get_progress_str() + ']' \
            + self.get_speed_str().ljust(20)

    def is_finished(self):
        return self.percent >= 1

    def is_downloading(self):
        return 0 < self.percent < 1


class DownloadingBlockInfo:

    def __init__(self, block_num, block_size, total_size):
        self.block_num = block_num
        self.block_size = block_size
        self.total_size = total_size


class DownloadingStatusBuilder:

    def __init__(self, pkg_name, ):
        self.pkg_name = pkg_name
        self.start_time = time.time()

    def get_speed(self, block_info: DownloadingBlockInfo):
        speed = self._get_normal_speed(block_info.block_num, block_info.block_size)
        return float(speed) / 1024

    def _get_normal_speed(self, block_num, block_size):
        used_time = time.time() - self.start_time
        if used_time == 0:
            return 0
        return block_num * block_size / used_time

    @staticmethod
    def get_percent(block_info: DownloadingBlockInfo):
        if block_info.total_size == 0:
            return 0
        percent = block_info.block_num * block_info.block_size / block_info.total_size
        return percent if percent <= 1 else 1

    def build_downloading_status(self, block_info: DownloadingBlockInfo):
        speed = self.get_speed(block_info)
        percent = self.get_percent(block_info)
        return DownloadingStatus(self.pkg_name, speed, percent, block_info.total_size)


class DownloadFileInfo:

    def __init__(self, filename="", url="", sha256="", md5="", dst_file_path="", content_length=0):
        self.filename = filename
        self.url = url
        self.sha256 = sha256
        self.md5 = md5
        self.dst_file_path = dst_file_path
        self.content_length = content_length
        if 'sha256=' in url:
            self.sha256 = url.split('sha256=')[1]
        elif 'md5=' in url:
            self.md5 = url.split('md5=')[1]


class CalcHashResult:
    MD5_TYPE = 0
    SHA256_TYPE = 1

    def __init__(self, file_info: DownloadFileInfo, file_hash="", is_hash_equals=False, hash_type=SHA256_TYPE):
        self.file_info = file_info
        self.file_hash = file_hash
        self.is_hash_equals = is_hash_equals
        self.hash_type = hash_type


def get_calc_sha256_result(file_info: DownloadFileInfo) -> CalcHashResult:
    file_sha256 = calc_sha256(file_info.dst_file_path)
    return CalcHashResult(file_info, file_sha256 or "", file_sha256 == file_info.sha256,
                          hash_type=CalcHashResult.SHA256_TYPE)


def get_calc_md5_result(file_info: DownloadFileInfo) -> CalcHashResult:
    file_md5 = calc_md5(file_info.dst_file_path)
    return CalcHashResult(file_info, file_md5 or "", file_md5 == file_info.md5, hash_type=CalcHashResult.MD5_TYPE)


def get_no_hash_result(file_info: DownloadFileInfo) -> CalcHashResult:
    return CalcHashResult(file_info, "", False, hash_type=CalcHashResult.SHA256_TYPE)


class ParallelDownloader:
    _MAX_DOWNLOAD_THREAD_NUM = int(os.environ.get("ASCEND_DEPLOYER_DOWNLOAD_MAX_SIZE", 16))
    _MAX_CALC_HASH_NUM = min(multiprocessing.cpu_count(), 32)

    def __init__(self, file_info_list: List[DownloadFileInfo], parent_instance=None):
        self._file_info_list = self._deduplicate_download_files(file_info_list)
        self._lock = threading.Lock()
        self._pkg_download_status_map: Dict[str, DownloadingStatus] = {}
        self._need_download_files = []
        self._is_download_finished = False
        self._last_print_lines_num = -1
        self.parent = parent_instance  # 保存父实例引用

    @staticmethod
    def _deduplicate_download_files(download_files: List[DownloadFileInfo]):
        tmp_set = set()
        res = []
        for file_info in download_files:
            dst_info = (file_info.url, file_info.dst_file_path)
            if dst_info in tmp_set:
                continue
            tmp_set.add(dst_info)
            res.append(file_info)
        return res

    def _update_pkg_download_status_map(self, downloading_status: DownloadingStatus):
        with self._lock:
            self._pkg_download_status_map[downloading_status.pkg_name] = downloading_status

    def _call_schedule(self, downloading_status_builder: DownloadingStatusBuilder):
        def schedule(block_num, block_size, total_size):
            block_info = DownloadingBlockInfo(block_num, block_size, total_size)
            status = downloading_status_builder.build_downloading_status(block_info)
            self._update_pkg_download_status_map(status)

        return schedule

    def download(self, file_info: DownloadFileInfo):
        if self._is_download_finished:
            return False
        parent_dir = os.path.dirname(file_info.dst_file_path)
        if not os.path.exists(parent_dir):
            LOG.info("mkdir : %s", os.path.basename(parent_dir))
            os.makedirs(parent_dir, mode=0o750, exist_ok=True)
        delete_if_exist(file_info.dst_file_path)
        if self._download_with_retry(file_info):
            LOG.info('download %s successfully', file_info.url)
            return True
        return False

    def _download_with_retry(self, file_info: DownloadFileInfo, retry_times=5):
        socket.setdefaulttimeout(DownloadUtil.INIT_TIMEOUT)
        need_change_item = ["libtool-ltdl"]
        file_name = os.path.basename(file_info.dst_file_path)
        file_name_dir = os.path.basename(os.path.dirname(file_info.dst_file_path))
        for item in need_change_item:
            if "EulerOS" in file_info.dst_file_path and "docker" != file_name_dir and item in file_name:
                file_info.dst_file_path = '/docker/'.join(file_info.dst_file_path.rsplit('/', 1))
                break
        error_msg = ""
        for retry in range(1, retry_times + 1):
            try:
                LOG.info('downloading try: %s from %s', retry, file_info.url)
                DownloadUtil.proxy_inst.build_proxy_handler()
                status_builder = DownloadingStatusBuilder(file_info.filename)
                local_file, _ = request.urlretrieve(file_info.url, file_info.dst_file_path,
                                                    self._call_schedule(status_builder))
                if is_exists(local_file):
                    return True
            except Exception as ex:
                error_msg = DownloadUtil.handle_download_error(retry, retry_times, ex, file_info.url)
            time.sleep(retry * 2)
        LOG.error(f"Download {file_info.url} failed")
        raise DownloadError(file_info.url, file_info.dst_file_path, error_msg)

    @staticmethod
    def _cursor_up():
        sys.stdout.write('\x1b[1A')

    @staticmethod
    def _cursor_to_line_begin():
        sys.stdout.write('\033[K')

    def _sys_out_download_progress(self):
        with self._lock:
            self._clear_last_download_cursor()
            print_items = [status for pkg_name, status in self._pkg_download_status_map.items()
                           if status.is_downloading()]
            for item in print_items:
                sys.stdout.write(item.get_downloading_print_str() + "\n")
            sys.stdout.write(self._get_all_download_progress_str() + "\n")
            cur_print_lines_num = len(print_items)
            if self._last_print_lines_num > cur_print_lines_num:
                for _ in range(self._last_print_lines_num - cur_print_lines_num + 1):
                    self._cursor_to_line_begin()
            self._last_print_lines_num = cur_print_lines_num
            sys.stdout.flush()

    def _clear_last_download_cursor(self):
        for _ in range(self._last_print_lines_num + 1):
            self._cursor_up()
            self._cursor_to_line_begin()
        sys.stdout.flush()

    def _get_all_download_progress_str(self):
        total_download_size = sum(obj.content_length for obj in self._need_download_files if
                                  hasattr(obj, 'content_length') and isinstance(obj.content_length, (int, float)))

        downloaded_files_size = sum(
            status.total_size * status.percent for pkg_name, status in self._pkg_download_status_map.items())
        if total_download_size == 0:
            return ""

        percent = downloaded_files_size / total_download_size
        if percent > 1:
            percent = 1
        percent_str = "{:.2f}%".format(percent * 100)
        n = round(percent * 30)
        s = ('=' * (n - 1) + '>').ljust(30, '-')
        if percent == 1:
            s = ('=' * n).ljust(30, '-')
        return '\r' + Color.CLEAR + Color.info('All Download Progress:').ljust(81, ' ') + percent_str.ljust(7, ' ') \
            + '[' + s + ']'

    def _await_download(self):
        while not self._is_download_finished:
            self._sys_out_download_progress()
            time.sleep(1)
        self._sys_out_download_progress()
        self._clear_last_download_cursor()

    def _parallel_calc_all_file_hash(self, file_info_list: List[DownloadFileInfo]) -> List[CalcHashResult]:
        with multiprocessing.Pool(processes=self._MAX_CALC_HASH_NUM) as process_pool:
            process_results = []
            for file_info in file_info_list:
                if file_info.sha256:
                    process_results.append(process_pool.apply_async(get_calc_sha256_result, (file_info,)))
                elif file_info.md5:
                    process_results.append(process_pool.apply_async(get_calc_md5_result, (file_info,)))
                else:
                    process_results.append(process_pool.apply_async(get_no_hash_result, (file_info,)))
            results = [process_result.get() for process_result in process_results]
        return results

    def parallel_download(self, need_download_files):
        print_thread = threading.Thread(target=self._await_download)
        with ThreadPoolExecutor(max_workers=self._MAX_DOWNLOAD_THREAD_NUM) as thread_pool:
            results = thread_pool.map(self.download, need_download_files)
            print_thread.start()
        self._is_download_finished = True
        print_thread.join()
        return results

    def validate_domains(self, file_infos):
        domain_groups = defaultdict(list)
        for info in file_infos:
            if not info.url:
                continue
            try:
                parsed = urlparse(info.url)
                if not parsed.netloc:  # 无效URL
                    continue
                domain = parsed.netloc
                domain_groups[domain].append(info)
            except Exception as e:
                self.parent.open_failed_url.append(UrlOpenErrInfo("", info.url, str(e)).__dict__)
        need_download_files = self.get_download_files(domain_groups)
        return need_download_files

    def get_download_files(self, domain_groups):
        results = {}
        need_download_files = []
        for domain, infos in domain_groups.items():
            # 1. 随机选择最多2个URL进行测试
            test_urls = random.sample(infos, min(2, len(infos)))

            # 2. 测试选中的URL
            success_count = 0
            test_results = []

            for info in test_urls:
                try:
                    # 使用提供的urlopen函数校验URL
                    status_code = DOWNLOAD_INST.urlopen(info.url, read_response=False)
                    if 200 <= status_code < 400:
                        success_count += 1
                        test_results.append((info.url, "success"))
                    else:
                        test_results.append((info.url, f"error code: {str(status_code)}"))
                except UrlOpenError as e:
                    test_results.append((info.url, f"url open failed with err: {str(e.err_msg)}"))
                except Exception as e:
                    test_results.append((info.url, f"error: {str(e)}"))

            # 3. 评估域名组状态
            if success_count > 0:
                # 如果有成功测试，认为整个域名组可用
                results[domain] = "partial_success"
                for info in infos:
                    need_download_files.append(info)
            else:
                # 所有测试都失败
                results[domain] = "all_failed"
                # 只记录失败的测试URL，而不是整个组
                for url, status in test_results:
                    self.parent.open_failed_url.append(UrlOpenErrInfo(domain, url, status).__dict__)
        return need_download_files

    @staticmethod
    def get_file_size(need_download_file):
        need_download_file.content_length = get_remote_content_length(need_download_file.url)

    def start_download(self):
        calc_all_file_hash_results = self._parallel_calc_all_file_hash(self._file_info_list)
        self._need_download_files = self.validate_domains(
            [calc_result.file_info for calc_result in calc_all_file_hash_results
             if not calc_result.file_hash or not calc_result.is_hash_equals])
        with ThreadPoolExecutor(max_workers=self._MAX_DOWNLOAD_THREAD_NUM) as thread_pool:
            thread_pool.map(self.get_file_size, self._need_download_files)
        results = self.parallel_download(self._need_download_files)
        if not all(results):
            return results
        calc_download_file_hash_res = self._parallel_calc_all_file_hash(self._need_download_files)
        calc_failed_res = [result for result in calc_download_file_hash_res if
                           result.file_info.sha256 and not result.is_hash_equals]
        if calc_failed_res:
            for calc_result in calc_failed_res:
                LOG.error(f'The downloaded file：{calc_result.file_info.dst_file_path} ,url: {calc_result.file_info.url}'
                          f'  file hash is not equal to the hash in config file.')
            raise DownloadCheckError("\n".join(item.file_info.dst_file_path for item in calc_failed_res))
        return results
