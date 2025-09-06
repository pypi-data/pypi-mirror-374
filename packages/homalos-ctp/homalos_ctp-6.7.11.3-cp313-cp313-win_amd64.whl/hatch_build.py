#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : hatch_build.py
@Date       : 2025/9/3 18:21
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: 设置正确的平台标签
"""
import os
import platform
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """自定义构建钩子"""

    def initialize(self, version, build_data):
        """
        此方法在构建过程初始化时被调用。
        version: 当前项目版本
        build_data: 一个字典，用于存储和传递构建数据，可修改它以影响构建过程。
        """
        # 检查是否包含原生扩展
        has_extensions = self._has_native_extensions()
        
        if has_extensions:
            # 如果包含原生扩展，设置正确的平台标签
            build_data["infer_tag"] = True
            build_data["pure_python"] = False
            
            # 手动设置平台标签
            platform_tag = self._get_platform_tag()
            if platform_tag:
                build_data["tag"] = platform_tag
                print(f"设置平台标签为: {platform_tag}")
        else:
            build_data["pure_python"] = True

    @staticmethod
    def _has_native_extensions():
        """检查是否包含原生扩展文件"""
        api_dir = os.path.join(os.getcwd(), "ctp", "api")
        if not os.path.exists(api_dir):
            print(f"原生扩展目录不存在: {api_dir}")
            return False
        
        # 检查是否有 .pyd 或 .so 文件
        for file in os.listdir(api_dir):
            if file.endswith(('.pyd', '.so')):
                print(f"检测到原生扩展文件: {file}")
                return True
        print(f"在 {api_dir} 中未检测到原生扩展文件")
        return False

    @staticmethod
    def _get_platform_tag():
        """获取正确的平台标签"""
        # 获取 Python 版本信息
        python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
        
        # 获取平台信息
        if platform.system() == "Windows":
            # Windows 平台
            machine = platform.machine().lower()
            if machine in ["amd64", "x86_64"]:
                platform_tag = "win_amd64"
            elif machine == "i386":
                platform_tag = "win32"
            else:
                platform_tag = f"win_{machine}"
        elif platform.system() == "Linux":
            # Linux 平台
            machine = platform.machine()
            if machine == "x86_64":
                platform_tag = "linux_x86_64"
            elif machine == "i386":
                platform_tag = "linux_i686"
            else:
                platform_tag = f"linux_{machine}"
        elif platform.system() == "Darwin":
            # macOS 平台
            machine = platform.machine()
            if machine == "arm64":
                platform_tag = "macosx_11_0_arm64"
            else:
                platform_tag = "macosx_10_9_x86_64"
        else:
            return None
        
        return f"{python_version}-{python_version}-{platform_tag}"
