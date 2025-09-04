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
TYPE_CPP2PY = {
    "int": "int",
    "char": "char",
    "double": "double",
    "short": "int",
}


class DataTypeGenerator:

    def __init__(self, filename: str, prefix: str) -> None:
        self.filename: str = filename  # "../include/ThostFtdcUserApiDataType.h"
        self.prefix: str = prefix  # "homalos-ctp"或"tts"
        self.f_cpp = None
        self.f_define = None
        self.f_typedef = None

    def run(self) -> None:
        """主函数"""
        print("3. 第三步：生成API DataType文件")
        self.f_cpp = open(self.filename)
        self.f_define = open(f"{self.prefix}_constant.py", "w")
        self.f_typedef = open(f"{self.prefix}_typedef.py", "w")

        for line in self.f_cpp:
            self.process_line(line)

        self.f_cpp.close()
        self.f_define.close()
        self.f_typedef.close()

        print("DataType生成完毕")

    def process_line(self, line: str) -> None:
        """处理每行"""
        line = line.replace("\n", "")
        line = line.replace(";", "")

        if line.startswith("#define"):
            self.process_define(line)
        elif line.startswith("typedef"):
            self.process_typedef(line)

    def process_define(self, line: str) -> None:
        """处理常量定义"""
        words = line.split(" ")
        words = [word for word in words if word]
        if len(words) < 3:
            return

        name = words[1]
        value = words[2]

        new_line = f"{name} = {value}\n"
        self.f_define.write(new_line)

    def process_typedef(self, line: str) -> None:
        """处理类型定义"""
        words = line.split(" ")
        words = [word for word in words if word != " "]

        name = words[2]
        typedef = TYPE_CPP2PY[words[1]]

        if typedef == "char":
            if "[" in name:
                typedef = "string"
                name = name[:name.index("[")]

        new_line = f"{name} = \"{typedef}\"\n"
        self.f_typedef.write(new_line)


if __name__ == "__main__":
    generator = DataTypeGenerator("../include/ThostFtdcUserApiDataType.h", "homalos-ctp")
    generator.run()
