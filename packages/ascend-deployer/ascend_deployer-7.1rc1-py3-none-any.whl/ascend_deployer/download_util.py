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
import hashlib
import argparse
import os
import shutil
from urllib import request
from typing import Optional
from zipfile import ZipFile, BadZipfile
from downloader.download_util import CONFIG_INST, get_obs_downloader_path, DownloadUtil
from downloader.parallel_file_downloader import ParallelDownloader, DownloadFileInfo

ROOT_PATH = SRC_PATH = os.path.dirname(__file__)
REFERER = "https://www.hiascend.com/"
LOCAL_FILE = os.path.normpath('./downloader/obs_downloader_config.zip')
EXTRACT_FILE = './downloader/obs_downloader_config'


def get_os_list():
    os_items = sorted(os.listdir(get_obs_downloader_path(os.path.join(ROOT_PATH, 'downloader', "config"))))
    return os_items


def get_pkg_list():
    pkg_file_list = os.listdir(get_obs_downloader_path(os.path.join(ROOT_PATH, 'downloader', "software")))
    pkg_items = set()
    for pkg_file in pkg_file_list:
        pkg_name, version = pkg_file.split('_')
        pkg_items.add(pkg_name)
        pkg_items.discard("MindIE-image")
        pkg_items.add('{}=={}'.format(pkg_name, version.replace('.json', '')))
    pkg_items = sorted(pkg_items)
    return pkg_items


class CustomHelpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        update_obs_config()
        for action in parser._actions:
            if action.dest == 'pkg_list':
                action.choices = get_pkg_list()  # 获取最新列表
            elif action.dest == 'os_list':
                action.choices = get_os_list()
        parser.print_help()
        parser.exit()


class UpdateStatus:
    UPDATE_SUCCESS = 0
    NO_CHANGE = 1
    UPDATE_FAILED = 2


def update_obs_config():
    obs_config_url, obs_config_md5 = CONFIG_INST.get_obs_downloader_config()
    # Get the remote MD5
    remote_md5 = get_remote_md5(obs_config_url, REFERER)
    if remote_md5:
        print(f"[INFO] remote file MD5: {remote_md5}")
    else:
        print("[WARN] No remote MD5 check value found, the download list will not refresh.")
        return UpdateStatus.UPDATE_FAILED
    if remote_md5 == obs_config_md5:
        print("The remote file is the same as that of the local storage md5 file, and the download is skipped.")
        return UpdateStatus.NO_CHANGE
    # Configure a download task
    download_files = [
        DownloadFileInfo(
            filename=os.path.basename(LOCAL_FILE),
            url=obs_config_url,
            md5=remote_md5,
            dst_file_path=LOCAL_FILE
        )
    ]

    # Perform the download
    try:
        ParallelDownloader(download_files).download(download_files[0])
    except Exception as e:
        print(f"[ERROR] File download failed: {str(e)}")
        return UpdateStatus.UPDATE_FAILED

    # Integrity verification (when there is a remote MD5)
    try:
        local_md5 = calculate_file_md5(LOCAL_FILE)
        if local_md5 == remote_md5:
            print("[SUCCESS] file integrity verification passed")
        else:
            print(f"[FAIL] file corruption! Local MD5: {local_md5}")
            return UpdateStatus.UPDATE_FAILED
    except Exception as e:
        print(f"[ERROR] Integrity check failed: {str(e)}")
        return UpdateStatus.UPDATE_FAILED
    if os.path.isdir(EXTRACT_FILE):
        # 删除文件夹及其所有内容
        shutil.rmtree(EXTRACT_FILE)
    extract_zip(LOCAL_FILE, EXTRACT_FILE)
    return UpdateStatus.UPDATE_SUCCESS


def extract_zip(file, path, filter_rule=None):
    try:
        with ZipFile(file) as z:
            members = z.namelist()
            if filter_rule:
                members = filter_rule(file, members)
            z.extractall(path, members)
            return members
    except BadZipfile:
        raise Exception('{} is corrupted'.format(file)) from e


def get_remote_md5(url: str, referer: str) -> Optional[str]:
    """
    Obtaining the MD5 Checksum of a Remote File via a HEAD Request (From the ETag Header)

    :param url: File URL
    :param referer: The value of the Referer's head
    :return: MD5 string (returned None not found)
    """
    try:
        # Create a custom opener with Referer
        DownloadUtil.proxy_inst.build_proxy_handler()
        # Send a HEAD request
        head_request = request.Request(url, method='HEAD')
        with request.urlopen(head_request, timeout=10) as response:
            etag = response.getheader('ETag', '').strip('"')
            return etag if etag and len(etag) == 32 else None  # Verify that the MD5 format is legal

    except Exception as e:
        print(f"[ERROR] Failed to get remote MD5: {str(e)}")
        return None


def calculate_file_md5(file_path: str, chunk_size: int = 4096) -> str:
    """
    Calculate the MD5 check value of the local file

    :param file_path: Local file path
    :param chunk_size: Chunk read size
    :return: MD5 string
    """
    md5_hash = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                md5_hash.update(chunk)
                chunk = f.read(chunk_size)
        return md5_hash.hexdigest()
    except Exception as e:
        raise RuntimeError(f"MD5 calculation failed: {str(e)}") from e
