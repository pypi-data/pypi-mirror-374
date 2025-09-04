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
import zipfile
import hashlib
from typing import List, Optional
import configparser
import os


def create_zip_with_md5(
        folders: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        output_zip: str = "output.zip"
) -> str:
    """
    Generic compressed file generation function

    :param folders: A list of directories that need to be packaged
    :param files: A list of individual files that need to be packaged
    :param output_zip: The name of the ZIP file that was output
    :return: The MD5 hash of the ZIP file
    """
    # Parameter validation
    if not folders and not files:
        raise ValueError("At least one directory or file needs to be specified.")

    with zipfile.ZipFile(output_zip, 'w') as zipf:
        # Work with directories
        if folders:
            for folder in folders:
                if not os.path.isdir(folder):
                    raise FileNotFoundError(f"The directory does not exist: {folder}")

                # Maintain the directory structure
                for root, _, filenames in os.walk(folder):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.relpath(file_path, os.path.dirname(folder))
                        zipf.write(file_path, arcname=arcname)

        # Work with files
        if files:
            for file in files:
                if not os.path.isfile(file):
                    raise FileNotFoundError(f"The file does not exist: {file}")
                zipf.write(file, arcname=os.path.basename(file))

    # Calculate MD5
    md5 = hashlib.md5()
    with open(output_zip, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)

    return md5.hexdigest()


def update_md5_value(config_path: str, new_md5: str):
    """Modify the md5 value of the [obs_downloader_config] node in the specified configuration file"""
    # Preserve original capitalization and formatting
    config = configparser.RawConfigParser()

    try:
        # Read existing configuration (comments and formatting are preserved)
        with open(config_path, 'r', encoding='utf-8') as f:
            config.read_file(f)

        # Check for the presence of a [obs_downloader_config] section
        if not config.has_section('obs_downloader_config'):
            config.add_section('obs_downloader_config')

        # Update the MD5 value
        config.set('obs_downloader_config', 'md5', new_md5)

        # Write back the file (keep it in its original format)
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)

    except (IOError, configparser.Error) as e:
        raise Exception(f"Profile operation failed:: {str(e)}") from e


# Example of use
if __name__ == '__main__':
    folders = ["config", "python_requirements", "software"]
    files = ["ansible_reqs.json", "obs_resources.json", "other_resources.json", "python_version.json",
             "version_match.json"]
    output_zip = "obs_downloader_config.zip"
    md5 = create_zip_with_md5(
        folders,
        files,
        output_zip
    )
    update_md5_value('config.ini', md5)
