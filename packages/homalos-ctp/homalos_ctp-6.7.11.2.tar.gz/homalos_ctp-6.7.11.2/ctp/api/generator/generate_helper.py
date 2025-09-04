#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_helper.py
@Date       : 2025/8/28 11:41
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: generate工具函数
"""
import os
import re
from pathlib import Path


def create_output_dir(output_dir_name: str) -> str:
    """创建输出目录（如果不存在）"""
    last_parent_dir_name: str = "src"

    # 获取当前文件的Path对象
    current_file = Path(__file__).resolve()

    # 获取当前文件所在的目录父目录 /homalos-ctp/api
    parent_path: Path = current_file.parent.parent

    output_path: Path = Path(parent_path / last_parent_dir_name / output_dir_name)
    output_dir: str = os.fspath(output_path)

    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"目录已创建: {output_path}")
            return output_dir
        except PermissionError:
            print(f"权限不足，无法创建目录: {output_path}")
            return ""
        except OSError as e:
            print(f"创建目录时出错: {e}")
            return ""
    else:
        return output_dir


def replace_function_name(func_name: str) -> str:
    # 定义前缀映射表：原前缀 -> 新前缀
    prefix_mapping = {
        "Req": "req",
        "Create": "create",
        "Get": "get",
        "Release": "release",
        "Init": "init",
        "Join": "join",
        "Exit": "exit",
        "Register": "register",
        "Subscribe": "subscribe",
        "UnSubscribe": "unSubscribe",  # 特殊处理，保持第二个单词首字母大写
        "Submit": "submit"
    }
    # 检查每个前缀，只替换开头匹配的部分
    for old_prefix, new_prefix in prefix_mapping.items():
        if func_name.startswith(old_prefix):
            # 只替换开头的部分，保留剩余部分不变
            return new_prefix + func_name[len(old_prefix):]

    # 如果没有匹配的前缀，返回原函数名
    return func_name

def process_func_type(func_type: str) -> str:
    """处理特殊返回类型，将 CThostFtdcMdApi、CThostFtdcTraderApi类型替换为 void"""
    if func_type and (func_type == 'CThostFtdcMdApi' or func_type == 'CThostFtdcTraderApi'):
        new_func_type = func_type.replace('CThostFtdcMdApi', 'void')
        new_func_type = new_func_type.replace('CThostFtdcTraderApi', 'void')
        return new_func_type
    return func_type

def camel_to_underscore_upper(name: str) -> str:
    """
    将驼峰命名（首字母大写）转换为下划线大写命名
    例如：'CreateFtdcMdApi' -> 'CREATE_FTDC_MD_API'
    """
    if not name:
        return ""

    # 在大写字母前插入下划线（第一个字符除外）
    # 使用正则表达式匹配小写字母后跟大写字母的位置
    part1 = re.sub('([a-z])([A-Z])', r'\1_\2', name)
    # 在大写字母后跟小写字母前插入下划线（处理连续大写字母）
    part2 = re.sub('([A-Z])([A-Z][a-z])', r'\1_\2', part1)

    # 转换为大写
    return part2.upper()

def underscore_to_camelcase(name: str) -> str:
    """
    将下划线命名转换为驼峰命名（首字母大写）
    例如: "ctp_md_function_constant" -> "CtpMdFunctionConstant"
    """
    if not name:
        return ""

    # 分割字符串
    parts = name.split('_')

    # 将每个部分的首字母大写，其余字母小写，然后连接
    camel_case = ''.join(part.capitalize() for part in parts if part)

    return camel_case

def format_equal_arg(arg: str) -> str:
    """
    格式化参数中等号前后的空格，将等号前后空格去掉
    例如：
    string pszFlowPath = "" -> string pszFlowPath=""
    string pszFlowPath ="" -> string pszFlowPath=""
    string pszFlowPath= "" -> string pszFlowPath=""
    :param arg: 参数，例如 string pszFlowPath = ""
    :return:
    """
    return re.sub(r'\s*=\s*', '=', arg)

def format_pointer_arg(arg: str) -> str:
    """
    格式化指针参数，确保 * 紧贴变量名，但与类型之间有空格
    例如：
    CThostFtdcFrontInfoField* pFrontInfo -> CThostFtdcFrontInfoField *pFrontInfo
    CThostFtdcFensUserInfoField * pFensUserInfo -> CThostFtdcFensUserInfoField *pFensUserInfo
    :param arg: 格式化后的参数
    :return:
    """
    # 匹配模式：类型名（可能包含字母数字和下划线）、可选空格、星号、可选空格、变量名
    # 替换为：类型名 + 空格 + 星号 + 变量名（无空格）
    return re.sub(r'(\w+)\s*\*\s*(\w+)', r'\1 *\2', arg)
