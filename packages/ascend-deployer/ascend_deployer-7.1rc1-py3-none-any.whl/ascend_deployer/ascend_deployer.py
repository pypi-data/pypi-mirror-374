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
import argparse
import codecs
import json
import logging
import logging.config
import os
import sys
from functools import wraps

import jobs
import utils
from module_utils.path_manager import TmpPath

__cached__ = 'ignore'  # fix bug for site.py in ubuntu_18.04_aarch64

LOG = logging.getLogger('ascend_deployer')
LOG_OP = logging.getLogger('install_operation')


def add_log(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        cmd = ' '.join(sys.argv[1:])
        dl_scene = False
        if 'dl' in cmd:  # only for support XX ugly implementation
            dl_scene = True
        reason = ''
        try:
            f(*args, **kwargs)
            if dl_scene:
                LOG.info("[INFO] Ascend DL deployed success --ascend-deployer")
            return 0
        except SystemExit as e:
            if e.code == 0:
                return 0
            reason = 'exit code: {}'.format(e.code)
            return -1
        except KeyboardInterrupt:  # handle KeyboardInterrupt
            reason = "User interrupted the program by Keyboard"
            return -1
        except BaseException as e:  # handle other exceptions
            LOG.exception(e)
            reason = str(e)
            return -1
        finally:
            msg = "run cmd: {} successfully".format(cmd)
            if reason:
                msg = "run cmd: {} failed, reason: {}".format(cmd, reason)
            print(msg)
            if dl_scene and reason:
                LOG.error("[ERROR]Ascend DL deployed failed --ascend-deployer")
            if reason:
                LOG_OP.error(msg)
            else:
                LOG_OP.info(msg)

    return wrap


class CLI(object):

    def __init__(self, prog, desc, epilog=None):
        self.parser = argparse.ArgumentParser(
            prog=prog, description=desc, epilog=epilog, formatter_class=utils.HelpFormatter)
        self.parser.add_argument("--check", dest="check", action="store_true", default=False, help="check environment")
        self.parser.add_argument("--clean", dest="clean", action="store_true", default=False,
                                 help="clean resources on remote servers")
        self.parser.add_argument("--force_upgrade_npu", dest="force_upgrade_npu", action="store_true", default=False,
                                 help="can force upgrade NPU when not all devices have exception")
        self.parser.add_argument("--verbose", dest="verbose", action="store_true", default=False, help="Print verbose")
        self.parser.add_argument("--install", dest="install", nargs="+", choices=utils.install_items,
                                 action=utils.ValidChoices,
                                 metavar="<package_name>", help="Install specific package: %(choices)s")
        self.parser.add_argument("--stdout_callback", dest="stdout_callback",
                                 help="set display plugin, e.g. ansible_log")
        self.parser.add_argument("--install-scene", dest="scene", nargs="?", choices=utils.scene_items,
                                 metavar="<scene_name>", help="Install specific scene: %(choices)s")
        self.parser.add_argument("--patch", dest="patch", nargs="+", choices=utils.patch_items,
                                 action=utils.ValidChoices,
                                 metavar="<package_name>", help="Patching specific package: %(choices)s")
        self.parser.add_argument("--patch-rollback", dest="patch_rollback", nargs="+", choices=utils.patch_items,
                                 action=utils.ValidChoices,
                                 metavar="<package_name>", help="Rollback specific package: %(choices)s")
        self.parser.add_argument("--test", dest="test", nargs="+", choices=utils.test_items, metavar="<target>",
                                 action=utils.ValidChoices,
                                 help="test the functions: %(choices)s")
        self.parser.add_argument("--hccn", dest="hccn", action="store_true", default=False,
                                 help="Setting hccn")
        exclusive_group = self.parser.add_mutually_exclusive_group()
        exclusive_group.add_argument("--nocopy", dest="no_copy", action="store_true", default=False,
                                     help="do not copy resources to remote servers when install for remote")
        exclusive_group.add_argument("--only_copy", dest="only_copy", action="store_true", default=False,
                                     help="copy the packages of the software you choose to install, but do not install."
                                          "only existing packages will be copied. If the package does not exist,"
                                          "please check and download it.")
        self.parser.add_argument("--skip_check", dest="skip_check", action="store_true", default=False,
                                 help="Control whether to perform a pre-installation check")
        self.parser.add_argument("--check_mode", dest="check_mode", choices=utils.check_items,
                                 help="Check mode: %(choices)s")
        self.parser.add_argument("--upgrade", dest="upgrade", nargs="+", choices=utils.upgrade_items,
                                 action=utils.ValidChoices,
                                 metavar="<package_name>", help="Upgrading specific package: %(choices)s")

    def _process_args(self):
        args = self.parser.parse_args(utils.args_with_comma(sys.argv[1:]))
        # str: full or fast
        self.check_mode = args.check_mode
        # bool: false or true
        self.check = args.check
        # bool: false or true
        self.clean = args.clean
        # bool: false or true
        self.force_upgrade_npu = args.force_upgrade_npu
        # bool: false or ture
        self.hccn = args.hccn
        # list: [sys_pkg, npu, toolkit, toolbox...]
        self.install = args.install
        # bool: false or true
        self.no_copy = args.no_copy
        # bool: false or true
        self.only_copy = args.only_copy
        # list: [nnae, nnrt, ftplugin, toolkit]
        self.patch = args.patch
        # list: [npu, nnae, nnrt, ftplugin, toolkit, kernels, toolbox]
        self.upgrade = args.upgrade
        # list: [nnae, nnrt, ftplugin, toolkit]
        self.patch_rollback = args.patch_rollback
        # str: auto, dl, edge, mindspre, offline_dev...
        self.scene = args.scene
        # bool: false or true
        self.skip_check = args.skip_check
        # str: callback_name, check it by: ansible-doc -t callback -l
        self.stdout_callback = args.stdout_callback
        # str: all, firmware, driver...
        self.test = args.test
        # args.verbose: bool: false or true
        self.ansible_args = ['-vv'] if args.verbose else []

    def _check_ai_frameworks(self):
        """
        currently, support 3 ai frameworks: tensorflow, mindspore and pytorch
        Only one ai framework allowed installation at one time.
        """
        ai_frameworks = {"tensorflow", "mindspore", "pytorch"}
        # self.install maybe None
        return not self.install or len(ai_frameworks & set(self.install)) <= 1

    def _check_args(self):
        """
        Some allowed commands(hide the prefix command: bash install.sh):
        --test
        --hccn
        --install=sys_pkg,npu
        --upgrade=npu
        --clean
        --hccn --check

        Some UNSUPPORTED commands:

        This test argument will be ignored
        --install=sys_pkg --test

        Raise error, program will not process this kind of installation
        --install=sys_pkg --install-scene

        The program process order is test, clean, hccn, so the clean and hccn will be ignored
        --test --clean -- hccn

        Raise error, DO NOT support check for patch, check only for install/install-scene/hccn
        --patch=nnae --check
        """
        if not any([self.install, self.scene, self.patch, self.upgrade, self.patch_rollback, self.test, self.check,
                    self.clean, self.hccn, self.check_mode]):
            self.parser.print_help()
            raise Exception("expected one valid argument at least")

        # check the ai frameworks valid or not
        if not self._check_ai_frameworks():
            raise Exception("tensorFlow, mindSpore, and pytorch cannot be installed at the same time.")

        commands_map = {"scene": "--install-scene"}

        def exclusive_commands_check(exclusive_commands):
            """
            Determine whether the input commands are mutual exclusion or not by exclusive_commands.
            If yes, raise Error
            Args:
                exclusive_commands([str]): a list of str which is input command. eg: ["hccn", "test", "clean"]
            """
            input_commands = []
            for k, v in self.__dict__.items():
                if k not in exclusive_commands or not v:
                    continue
                input_commands.append(commands_map.get(k, "--" + k))

            if len(input_commands) > 1:
                raise Exception("Unsupported {} at the same time.".format(" and ".join(input_commands)))

        exclusive_commands_check(["install", "scene", "hccn", "test", "clean", "upgrade"])
        exclusive_commands_check(["test", "clean", "patch", "check"])
        exclusive_commands_check(["test", "clean", "patch_rollback", "check"])
        exclusive_commands_check(["skip_check", "check"])
        exclusive_commands_check(["skip_check", "check_mode"])

        # validate the `--check` tags
        if self.check and not any([self.install, self.upgrade, self.scene, self.hccn]):
            raise Exception("The check option must be used together with install, upgrade, install-scene or hccn, for "
                            "example: '--install=<package_name> --check','--upgrade=<package_name> --check' or "
                            "'--install-scene=<scene_name> --check' or '--hccn --check'")
        if self.check_mode and not any([self.install, self.upgrade, self.scene, self.hccn]):
            raise Exception(
                "The check_mode option must be used together with install, upgrade, install-scene or hccn, for example:"
                " '--install=<package_name> --check_mode=<mode_name>' or "
                "'--upgrade=<package_name> --check_mode=<mode_name>' or "
                "'--install-scene=<scene_name> --check_mode=<mode_name>' or "
                "'--hccn --check_mode=<mode_name>'")

    def _process_env(self):
        if self.stdout_callback:
            os.environ['ANSIBLE_STDOUT_CALLBACK'] = self.stdout_callback
        os.environ['ANSIBLE_CACHE_PLUGIN_CONNECTION'] = os.path.join(utils.ROOT_PATH, 'facts_cache')
        os.environ['ANSIBLE_CONFIG'] = os.path.join(utils.ROOT_PATH, 'ansible.cfg')
        os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

    def _license_agreement(self):
        if any([self.install, self.upgrade, self.scene, self.patch]) and not self.check:
            if not jobs.accept_eula():
                LOG_OP.error('reject EULA, quit the installation')
                raise Exception('reject EULA, quit the installation')
            LOG_OP.info("accept EULA, start to install")

    def _prepare_job(self):
        if self.scene == 'auto':
            print('Warning: --install-scene=auto feature will be deprecated soon.')
        try:
            jobs.PrepareJob().run()
        except Exception as e:
            check_item = {"check_item": "prepare_job",
                          "desc_en": "check whether the prepare job is normal.",
                          "desc_zh": u"检查准备工作是否正常。",
                          "tip_en": "",
                          "tip_zh": "",
                          "help_url": ""}
            check_res = {"check_item": "prepare_job",
                         "status": "failed",
                         "error_msg": str(e)}
            error_info = {"CheckList": [check_item],
                          "HostCheckResList":
                              {"localhost": {
                                  "check_res_list": [check_res]}}}
            if not os.path.exists(TmpPath.DEPLOY_INFO):
                os.makedirs(TmpPath.DEPLOY_INFO)
            with codecs.open(TmpPath.CHECK_RES_OUTPUT_JSON, 'w', encoding='utf-8') as file:
                json.dump(error_info, file, indent=4, ensure_ascii=False)
            raise

        self.envs = {
            'deployer_check_mode': self.check_mode if self.check_mode else 'full',
            'force_upgrade_npu': 'true' if self.force_upgrade_npu else 'false',
            'do_upgrade': 'true',
            'working_on_ipv6': 'true' if ':' in jobs.get_localhost_ip() else 'false',
            'use_k8s_version': os.environ.get('USE_K8S_VERSION', '1.25.3'),
        }

    def _run_check(self):
        """
        This function is mainly check the current envs/os/configurations are supported or not.
        Currently, we support:
        --install=<package_name> --check
        --upgrade=<package_name> --check
        --install-scene=<scene_name> --check
        --hccn --check
        """

        # the args have been validated in _check_args, so we can ensure that the check_tags will not be empty
        check_tags = []
        if self.install:
            check_tags = self.install
        elif self.scene:
            check_tags = ["mindspore_scene" if self.scene == "mindspore" else self.scene]
        elif self.upgrade:
            check_tags = self.upgrade
        elif self.hccn:
            check_tags = ["hccn"]
            return jobs.process_hccn_check(check_tags, no_copy=True, envs=self.envs, ansible_args=self.ansible_args)

        total_tags = []
        for tmp_tags in (self.install, self.upgrade, self.scene, self.patch, self.patch_rollback):
            if not tmp_tags:
                continue
            if isinstance(tmp_tags, str):
                total_tags.append(tmp_tags)
            if isinstance(tmp_tags, list):
                total_tags.extend(tmp_tags)

        self.envs['hosts_name'] = utils.get_hosts_name(total_tags)
        return jobs.process_check(check_tags, no_copy=True, envs=self.envs, ansible_args=self.ansible_args)

    def _run_handler(self):
        for handler, tags in (
                (jobs.process_install, self.install),
                (jobs.process_scene, self.scene if self.scene != "mindspore" else "mindspore_scene"),
                (jobs.process_patch, self.patch),
                (jobs.process_upgrade, self.upgrade),
                (jobs.process_patch_rollback, self.patch_rollback)):
            if not tags:
                continue
            ip = jobs.get_localhost_ip()
            job = jobs.ResourcePkg(tags, "copy_pkgs" in tags)
            if not self.no_copy:
                job.handle_pkgs()
            self.envs['hosts_name'] = utils.get_hosts_name(tags)
            nexus_url = job.start_nexus_daemon(ip)
            if nexus_url:
                self.envs['nexus_url'] = nexus_url
            if not self.skip_check and tags:
                jobs.process_check(tags, no_copy=True, envs=self.envs, ansible_args=self.ansible_args)
            result = handler(tags, no_copy=self.no_copy, only_copy=self.only_copy, envs=self.envs,
                             ansible_args=self.ansible_args)
            job.clean(ip)
            return result

    def _run_test(self):
        envs = {'hosts_name': 'worker'}
        os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'ansible_log'
        if '-v' not in self.ansible_args:  # test always detail output
            self.ansible_args.append('-v')
        return jobs.process_test(self.test, envs=envs, ansible_args=self.ansible_args)

    def _run_clean(self):
        run_args = ['worker', '-m', 'shell', '-a', 'rm -rf ~/resources*.tar ~/resources']
        run_args.extend(self.ansible_args)
        return jobs.process_clean(run_args)

    def _run_hccn(self):
        if not self.skip_check:
            jobs.process_hccn_check(['hccn'], no_copy=True, envs=self.envs, ansible_args=self.ansible_args)
        return jobs.process_hccn(['hccn'], ansible_args=self.ansible_args)

    @add_log
    def run(self):
        self._process_args()
        self._check_args()
        self._process_env()
        self._license_agreement()
        self._prepare_job()
        if self.check:
            self._run_check()
        elif any([self.install, self.scene, self.upgrade, self.patch, self.patch_rollback]):
            self._run_handler()
        elif self.test:
            self._run_test()
        elif self.clean:
            self._run_clean()
        elif self.hccn:
            self._run_hccn()


def main():
    os.umask(0o022)
    logging.config.dictConfig(utils.LOGGING_CONFIG)
    cli = CLI(
        "ascend-deployer",
        "Manage Ascend Packages and dependence packages for specified OS"
    )
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
