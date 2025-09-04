#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_struct.py
@Date       : 2025/8/27 14:53
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: 生成结构体定义文件
功能：
1. 读取CTP的头文件 `ThostFtdcUserApiDataType.h`
2. 依赖 `ctp_typedef.py` 中的类型映射
3. 解析C++结构体定义，生成Python字典格式的结构体定义文件 `ctp_struct.py`
"""
import importlib


class StructGenerator:

    def __init__(self, filename: str, prefix: str) -> None:
        self.filename: str = filename  # "../include/ThostFtdcUserApiStruct.h"
        self.prefix: str = prefix  # "homalos-ctp"或"tts"
        self.typedefs: dict[str, str] = {}
        self.f_cpp = None
        self.f_struct = None

        self.load_constant()

    def load_constant(self) -> None:
        """"""
        module_name = f"{self.prefix}_typedef"
        module = importlib.import_module(module_name)

        for name in dir(module):
            if "__" not in name:
                self.typedefs[name] = getattr(module, name)

    def run(self) -> None:
        """运行生成"""
        print("4. 第四步：生成API结构体文件")
        self.f_cpp = open(self.filename)
        self.f_struct = open(f"{self.prefix}_struct.py", "w")

        for line in self.f_cpp:
            self.process_line(line)

        self.f_cpp.close()
        self.f_struct.close()

        print("Struct生成成功")

    def process_line(self, line: str) -> None:
        """处理每行"""
        line = line.replace(";", "")
        line = line.replace("\n", "")

        if line.startswith("struct"):
            self.process_declare(line)
        elif line.startswith("{"):
            self.process_start(line)
        elif line.startswith("}"):
            self.process_end()
        elif "\t" in line and "///" not in line:
            self.process_member(line)

    def process_declare(self, line: str) -> None:
        """处理声明"""
        words = line.split(" ")
        name = words[1]
        end = "{"

        new_line = f"{name} = {end}\n"
        self.f_struct.write(new_line)

    def process_start(self, line: str) -> None:
        """处理开始"""
        pass

    def process_end(self) -> None:
        """处理结束"""
        new_line = "}\n\n"
        self.f_struct.write(new_line)

    def process_member(self, line: str) -> None:
        """处理成员"""
        # 先尝试按制表符分割
        words = line.split("\t")
        words = [word for word in words if word]
        
        # 如果只有一个元素，说明可能是用空格分隔的
        if len(words) == 1:
            # 按空格分割，然后过滤空字符串
            words = line.split()
            words = [word for word in words if word]
        
        # 确保至少有两个元素（类型和字段名）
        if len(words) < 2:
            return
            
        # 取第一个作为类型，最后一个作为字段名
        type_name = words[0]
        field_name = words[-1]
        
        if type_name not in self.typedefs:
            print(f"Warning: Unknown type '{type_name}' in line: {line.strip()}")
            return
            
        py_type = self.typedefs[type_name]

        new_line = f"    \"{field_name}\": \"{py_type}\",\n"
        self.f_struct.write(new_line)


if __name__ == "__main__":
    generator = StructGenerator("../include/ThostFtdcUserApiStruct.h", "homalos-ctp")
    generator.run()
