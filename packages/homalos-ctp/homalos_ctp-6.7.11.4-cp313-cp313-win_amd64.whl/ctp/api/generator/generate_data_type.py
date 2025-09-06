#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_api_functions.py
@Date       : 2025/8/27 14:53
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: 生成数据类型定义文件
功能：
1. 读取CTP的头文件 `ThostFtdcUserApiDataType.h`
2. 解析其中的 `#define` 常量定义和 `typedef` 类型定义
3. 生成 `ctp_constant.py`（常量定义）和 `ctp_typedef.py`（类型定义）

ctp_typedef.py：数据类型映射定义文件，定义了CTP API中各种数据类型到Python类型的映射关系
"""
import re
from pathlib import Path

TYPE_CPP2PY = {
    "int": "int",
    "char": "char",
    "double": "double",
    "short": "int",
}


class DataTypeGenerator:

    def __init__(self, filename: str, prefix: str) -> None:
        self.filename: str = filename  # "../include/ThostFtdcUserApiDataType.h"
        self.prefix: str = prefix  # "ctp"或"tts"
        self.f_cpp = None
        self.f_define = None
        self.f_typedef = None

        # .h文件中的枚举处理变量
        self.in_enum = False  # 是否处于枚举定义中
        self.enum_content = []  # 枚举内容
        self.in_multiline_comment = False  # 是否处于多行注释中
        self.brace_count = 0  # 大括号数量

    def run(self) -> None:
        """主函数"""
        print("3. 第三步：生成API DataType文件")

        # 获取当前文件的Path对象
        current_file = Path(__file__).resolve()

        # 获取当前文件所在的目录父目录 /ctp/api
        parent_path: Path = current_file.parent.parent

        self.f_cpp = open(self.filename)
        self.f_define = open(f"{str(parent_path)}/{self.prefix}_constant.py", "w")
        self.f_typedef = open(f"{self.prefix}_typedef.py", "w")

        for line_num, line in enumerate(self.f_cpp, 1):
            self.process_line(line)

        self.f_cpp.close()
        self.f_define.close()
        self.f_typedef.close()

        print("DataType生成完毕")

    def process_line(self, line: str) -> None:
        """
        处理每行
        :param line: 完整行字符串
        :return: None
        """
        # 处理多行注释
        if self.in_multiline_comment:
            if '*/' in line:
                comment_end = line.find('*/') + 2
                line = line[comment_end:]
                self.in_multiline_comment = False
            else:
                return

        # 处理单行注释
        if '//' in line:
            line = line.split('//')[0]

            # 处理多行注释开始
            if '/*' in line:
                comment_start = line.find('/*')
                if '*/' in line:
                    comment_end = line.find('*/') + 2
                    line = line[:comment_start] + line[comment_end:]
                else:
                    line = line[:comment_start]
                    self.in_multiline_comment = True

        # 移除换行符和分号，并去除两端空格
        line = line.replace("\n", "").replace(";", "").strip()

        if line.startswith("#define"):
            self.process_define(line)
        elif line.startswith("typedef"):
            self.process_typedef(line)
        else:
            # 处理枚举
            self.process_enum(line)

    def process_define(self, line: str) -> None:
        """
        处理常量定义

        解析C++中的#define语句，将其转换为Python的常量定义并写入文件。
        例如将 "#define THOST_FTDC_EXP_Normal '0'"

        :param line: 包含#define常量定义的完整行字符串
        :return: None
        """
        words = line.split(" ")
        words = [word for word in words if word]
        if len(words) < 3:
            return

        name = words[1]
        value = words[2]

        new_line = f"{name} = {value}\n"
        self.f_define.write(new_line)

    def process_typedef(self, line: str) -> None:
        """
        处理类型定义

        解析C++中的typedef语句，将其转换为Python的类型定义并写入文件。
        对于字符数组类型，会特殊处理为string类型。

        :param line: 包含typedef定义的完整行字符串
        :return: None
        """
        # 分割字符串并过滤空格
        words = line.split(" ")
        words = [word for word in words if word != " "]

        # 提取类型名称和对应的C++类型
        name = words[2]
        typedef = TYPE_CPP2PY[words[1]]

        # 特殊处理字符数组类型，将其转换为string
        if typedef == "char":
            if "[" in name:
                typedef = "string"
                name = name[:name.index("[")]

        # 写入类型定义到文件
        new_line = f"{name} = \"{typedef}\"\n"
        self.f_typedef.write(new_line)

    def process_enum(self, line: str) -> None:
        """
        处理C++枚举
        :param line: 完整行字符串
        :return:
        """
        # 检查是否进入枚举定义
        if not self.in_enum and re.match(r'^\s*enum\s+\w+', line):
            self.in_enum = True
            self.brace_count = 0
            self.enum_content = []

        # 如果处于枚举定义中，收集内容
        if self.in_enum:
            # 计算大括号数量
            self.brace_count += line.count('{')
            self.brace_count -= line.count('}')

            # 添加行内容
            self.enum_content.append(line)

            # 检查枚举定义是否结束
            if self.brace_count <= 0 and '}' in line:
                self.in_enum = False
                # 解析枚举内容
                enum_text = ' '.join(self.enum_content)
                self.parse_enum_content(enum_text)

    def parse_enum_content(self, enum_text) -> None:
        """
        解析枚举内容文本（假设enum_text是一个没有换行符和分号的长字符串）
        Args:
            enum_text (str): 枚举定义文本
        """
        # 提取大括号内的内容
        match = re.search(r'\{(.*?)}', enum_text, re.DOTALL)
        if not match:
            return

        inner_content = match.group(1).strip()

        # 如果内容为空，返回 None
        if not inner_content:
            return

        current_value = 0
        # 按逗号分割 inner_content
        parts = inner_content.split(',')

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # 解析枚举项
            item_match = re.match(r'(\w+)(?:\s*=\s*(\d+))?', part)
            if item_match:
                name, explicit_value = item_match.groups()
                if explicit_value:
                    current_value = int(explicit_value)

                new_line = f"{name} = {current_value}\n"
                self.f_define.write(new_line)
                current_value += 1


if __name__ == "__main__":
    generator = DataTypeGenerator("../include/ThostFtdcUserApiDataType.h", "ctp")
    generator.run()
