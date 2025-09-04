#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

'''
功    能：下载并安装rtos/hcc工具
修改记录：2021-10-11 创建
'''
import os
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

from bmcgo.tasks.task import Task
from bmcgo.tasks.misc import BUILD_TOOLS_SHA256_PATH
from bmcgo.utils.config import Config
from bmcgo import misc


class DownloadDefaultBuildtools(Task):
    def __init__(self, config: Config):
        super(DownloadDefaultBuildtools, self).__init__(config, "DownloadDefaultBuildtools")
        self.rtos_sdk_dir = f"{self.config.tools_path}/rtos-sdk-arm64"
        self.buildtools_new_sha256 = f"{self.config.tools_path}/buildtools_new.sha256"
        self.skip_install = False

    def download_tools(self):
        self.info(f"移除下载路径: {self.rtos_sdk_dir}")
        self.run_command(f"rm -rf {self.rtos_sdk_dir}", ignore_error=True, sudo=True)
        self.info('开始下载依赖工具...')
        partner_tools_dir = f"{os.path.expanduser('~')}/rtos_compiler"
        if self.config.partner_mode:
            self.info(f"从缓存目录{partner_tools_dir}复制编译器工具")
            self.run_command(f"cp -rf {partner_tools_dir}/. {self.rtos_sdk_dir}")

    def install_buildtools(self):
        is_ubuntu = self.tools.is_ubuntu
        self.chdir(self.rtos_sdk_dir)
        self.info("删除目录 /opt/RTOS")
        self.run_command(f"rm -rf {BUILD_TOOLS_SHA256_PATH}", sudo=True)
        self.run_command("rm -rf /opt/RTOS", sudo=True)
        self.info("安装 rpm 包")
        for rpm in os.listdir("./"):
            if not os.path.isfile(rpm) or not rpm.endswith(".rpm"):
                continue
            self.info("安装 {}".format(rpm))
            if not is_ubuntu:
                self.run_command("rpm -ivh {}".format(rpm), sudo=True)
            else:
                self.pipe_command(["rpm2cpio {}".format(rpm), "sudo cpio -id -D /"])

        self.info("删除目录 /opt/hcc_arm64le")
        self.run_command("rm -rf /opt/hcc_arm64le", sudo=True)
        self.info("解压 hcc_arm64le")
        self.run_command("tar -xzf hcc_arm64le.tar.gz -C /opt", sudo=True)

        logname = os.getenv(misc.ENV_LOGNAME, None)
        if logname and logname != "root":
            user_group = f"{os.getuid():{os.getgid()}}"
            self.run_command(f"chown {user_group} /opt/hcc_arm64le -R", sudo=True)
            self.run_command(f"chown {user_group} /opt/RTOS -R", sudo=True)
        self.chdir(self.config.code_path)

        libstdcpp_install_path = f"{self.config.sysroot}/usr/"
        os.makedirs(libstdcpp_install_path, exist_ok=True)
        self.run_command(f"cp -rf {self.config.cross_compile_install_path}/{self.config.cross_prefix}/lib64/" +
                         f" {libstdcpp_install_path}")
        self.run_command("cp -af {} {}".format(self.buildtools_new_sha256, BUILD_TOOLS_SHA256_PATH), sudo=True)
        self.run_command("chmod a+r {}".format(BUILD_TOOLS_SHA256_PATH), sudo=True)

    def download_sdk(self):
        downloads = self.get_manufacture_config("sdk/downloads")
        if downloads is None:
            self.log.warning("请在 manifest.yml 配置 sdk 字段或更新 manifest 仓库")
            return

        download_path = Path.home() / "downloads"
        download_path.mkdir(exist_ok=True, parents=True)

        for item in downloads:
            self.log.info(f"配置 {item['name']}...")

            curr_file_name = Path(urlparse(item['url']).path).name
            curr_file = download_path / curr_file_name
            curr_file_path = curr_file.as_posix()

            need_download = True
            if curr_file.exists():
                curr_pkg_sha256 = self.tools.sha256sum(curr_file_path)
                if curr_pkg_sha256 == item['sha256']:
                    self.log.info(f"已下载 {item["name"]}, 跳过.")
                    need_download = False

            if need_download:
                with tempfile.TemporaryDirectory() as tmp:
                    self.log.info(f"开始下载 {item['url']}...")
                    download_pkg_path = os.path.join(tmp, curr_file_name)
                    self.tools.download_file(item['url'], download_pkg_path)
                    downloaded_sha256 = self.tools.sha256sum(download_pkg_path)

                    if item['sha256'] != downloaded_sha256:
                        raise RuntimeError(f"manifest.yml /sdk/downloads/{item['name']} sha256 内容和下载包体不符，请检查配置！")

                    shutil.move(download_pkg_path, curr_file_path)

            if hasattr(self, f"install_{item['name']}"):
                getattr(self, f"install_{item['name']}")(curr_file_path)
            
            self.log.info(f"配置 {item['name']} 完成！")

    def install_bmc_sdk(self, zip_path):
        with tempfile.TemporaryDirectory() as tmp:
            self.log.info("安装 bmc_sdk")
            home_path = Path.home().as_posix()
            real_path = zip_path

            self.log.debug(f"解压 {real_path} 到 {tmp}")
            self.run_command(f"unzip {real_path} -d {tmp}")
            
            rtos_compiler_path = Path.home() / "rtos_compiler"
            if rtos_compiler_path.exists():
                shutil.rmtree(rtos_compiler_path)

            sdk_path = Path.home() / "sdk"
            if sdk_path.exists():
                shutil.rmtree(sdk_path)

            self.log.debug(f"move {tmp}/rtos_compiler -> {home_path}")
            self.run_command(f"mv {tmp}/rtos_compiler/ {home_path}")
            self.log.debug(f"move {tmp}/sdk -> {home_path}")
            self.run_command(f"mv {tmp}/sdk/ {home_path}")
            self.log.debug(f"move {tmp}/lua-format -> /usr/bin")
            self.run_command(f"chmod +x {tmp}/lua-format")
            self.run_command(f"mv -f {tmp}/lua-format /usr/bin/", sudo=True)

            self.log.debug(f"copy {tmp}/hpm_tools/. -> {home_path}")
            self.run_command(f"chmod -R +x {tmp}/hpm_tools")
            self.run_command(f"cp -rf {tmp}/hpm_tools/. /usr/local/bin/", sudo=True)

            self.log.info(f"安装 bmc_sdk 完成！")

    def run(self):
        self.download_sdk()
        self.download_tools()
        self.info("下载依赖工具结束")

    def install(self):
        self.skip_install = not self.check_need_install(self.rtos_sdk_dir, BUILD_TOOLS_SHA256_PATH,
                                                        self.buildtools_new_sha256)
        if self.skip_install:
            self.info("buildtools版本匹配，跳过安装")
            return
        # 检查rtos是否安装，未安装或版本不匹配时安装
        self.install_buildtools()


class TaskClass(Task):
    def __init__(self, config, work_name=""):
        super(TaskClass, self).__init__(config, work_name)
        self.download_buildtools = DownloadDefaultBuildtools(config)

    def run(self):
        self.download_buildtools.run()

    def install(self):
        self.download_buildtools.install()