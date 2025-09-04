#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_onekey.py
@Date       : 2025/9/1 15:20
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: 一键生成 MD和TD cpp、h文件
"""
import glob
import os
import subprocess
import sys


def delete_ctp_files():
    """
    删除当前目录中所有以ctp_开头的文件
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 确保目录存在
    if not os.path.exists(current_dir):
        print(f"错误：目录 '{current_dir}' 不存在")
        return

    # 构建匹配模式 - 匹配所有以ctp_开头的文件
    pattern = os.path.join(current_dir, "ctp_*")

    # 查找所有匹配的文件
    ctp_files = glob.glob(pattern)

    if not ctp_files:
        print(f"在目录 '{current_dir}' 中未找到以ctp_开头的文件")
        return

    # 删除文件
    deleted_count = 0
    for file_path in ctp_files:
        try:
            if os.path.isfile(file_path):  # 确保是文件而不是目录
                os.remove(file_path)
                print(f"已删除: {file_path}")
                deleted_count += 1
        except Exception as e:
            print(f"删除文件 '{file_path}' 时出错: {e}")

    print(f"\n操作完成。共删除了 {deleted_count} 个文件")


def run_step(script_name, error_message):
    """执行单个生成步骤"""
    try:
        result = subprocess.run([sys.executable, script_name])
        if result.returncode != 0:
            print(error_message)
            sys.exit(1)
    except FileNotFoundError:
        print(f"找不到脚本文件: {script_name}")
        sys.exit(1)
    except Exception as e:
        print(f"执行 {script_name} 时发生错误: {e}")
        sys.exit(1)

def run():
    # 定义所有生成步骤
    steps = [
        ('generate_function_const.py', "生成API函数常量文件失败"),
        ('generate_dll_entry.py', "生成DLL入口文件失败"),
        ('generate_data_type.py', "生成API DataType文件失败"),
        ('generate_struct.py', "生成API结构体文件失败"),
        ('generate_api_functions.py', "生成API函数文件失败"),
        ('generate_cpp.py', "生成API cpp、h文件失败")
    ]

    # 依次执行每个步骤
    for script_name, error_message in steps:
        run_step(script_name, error_message)


if __name__ == '__main__':
    # 删除所有以ctp_开头的文件
    delete_ctp_files()
    # 执行所有生成步骤
    run()
