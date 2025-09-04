#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_function_const.py
@Date       : 2025/8/28 14:31
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: 1. 第一步：生成API函数常量文件，请运行 main 函数
"""
import datetime
import re
from pathlib import Path

from ctp.api.generator.generate_helper import underscore_to_camelcase, camel_to_underscore_upper


class GeneratorFunctionConst:
    def __init__(self, filename: str, prefix: str, name: str, class_name: str) -> None:
        self.filename: str = filename  # "../include/ThostFtdcMdApi.h"或"../include/ThostFtdcTdApi.h"
        self.prefix: str = prefix  # "homalos-ctp"或"tts"
        self.name: str = name  # "md"或"td"
        self.class_name: str = class_name  # "MdApi"或"TdApi"
        self.file_cpp = None
        self.function_names: list = ["Exit"]

    def run(self):
        """运行"""
        print("1. 第一步：生成API函数常量文件")
        self.file_cpp = open(self.filename)
        for line in self.file_cpp:
            func_name = self.process_function_name(line)
            if func_name and func_name not in self.function_names:
                self.function_names.append(func_name)
        self.file_cpp.close()

        self.generate_base_functon_names()

    @staticmethod
    def process_function_name(line: str) -> str | None:
        """处理原始.h文件中的每行字符串"""
        if line and isinstance(line, str):
            # 使用translate高效删除字符，一次操作移除;、\n、\t
            translator = str.maketrans('', '', ';\n\t')
            line = line.translate(translator)

            line = line.replace("{}", "")  # 移除 "{}"
            stripped_line = line.strip()

            # 检查是否不包含"virtual void On"或"virtual int Req"
            no_forbidden = not re.search(r"virtual void On|virtual int Req", stripped_line)

            # 检查是否包含"static"或"virtual"
            has_required = re.search(r"static|virtual", stripped_line) is not None

            if no_forbidden and has_required:
                newline = stripped_line[0:stripped_line.index("(")]
                # 移除字符串中多余空格（保留单词间单个空格）
                normalized = ' '.join(newline.split())
                # 查找最后一个空格的位置
                last_space_index = normalized.rfind(' ')
                # 获取函数原始名称
                func_part = normalized[last_space_index + 1:].strip().replace('*', '')

                return func_part

    def generate_base_functon_names(self):
        """生成md和td基础函数名称文件(不是Req和On开头的函数)"""
        func_filename_prefix = f"{self.prefix}_function_const"
        funcs_filename = f"{func_filename_prefix}.py"
        # 将文件名前缀转换为驼峰，作为类名写入文件
        camel_name = underscore_to_camelcase(func_filename_prefix)

        funcs_file_path = Path(funcs_filename)

        if self.name == "md":
            if funcs_file_path.exists() and funcs_file_path.is_file():
                funcs_file_path.unlink()

            with open(funcs_filename, "w", encoding="utf-8") as f:
                f.write("#!/usr/bin/env python\n")
                f.write("# -*- coding: utf-8 -*-\n")
                f.write("\"\"\"\n")
                f.write("@ProjectName: homalos-ctp\n")
                f.write(f"@FileName\t: {funcs_filename}\n")
                f.write(f"@Date\t\t: {datetime.datetime.now()}\n")
                f.write("@Author\t\t: Donny\n")
                f.write("@Email\t\t: donnymoving@gmail.com\n")
                f.write("@Software\t: PyCharm\n")
                f.write(f"@Description: {self.prefix} md和td基础函数名称文件， 不是 Req 和 On 开头的函数\n")
                f.write("\"\"\"\n\n\n")
                f.write(f"class {camel_name}:\n")
                f.write("\t# 原有函数名\n")
                for func_name in self.function_names:
                    upper_name = camel_to_underscore_upper(func_name)  # 将函数名称变为大写作为变量名
                    f.write(f"\t{upper_name}: str = \"{func_name}\"\n")
                f.write("\n")
            print(f"{funcs_filename} 生成完毕")

        else:
            if funcs_file_path.exists() and funcs_file_path.is_file():
                # 读取文件内容
                with open(funcs_filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查类CtpFunctionConst是否存在
                if 'class CtpFunctionConst:' not in content:
                    print("类 CtpFunctionConst 不存在于文件中")
                    return
                else:
                    # 提取类中所有现有的值
                    pattern = r'(\w+): str = "([^"]+)"'
                    existing_values = re.findall(pattern, content)
                    existing_value_strings = [value for _, value in existing_values]

                    with open(funcs_filename, "a", encoding="utf-8") as f:
                        f.write("\t# 新增函数名\n")
                        for func_name in self.function_names:
                            if func_name not in existing_value_strings:
                                upper_name = camel_to_underscore_upper(func_name)  # 将函数名称变为大写作为变量名
                                f.write(f"\t{upper_name}: str = \"{func_name}\"\n")

                    print(f"{funcs_filename} 写入完毕")


if __name__ == "__main__":
    md_const_generator = GeneratorFunctionConst("../include/ThostFtdcMdApi.h", "homalos-ctp", "md", "MdApi")
    md_const_generator.run()

    td_const_generator = GeneratorFunctionConst("../include/ThostFtdcTraderApi.h", "homalos-ctp", "td", "TdApi")
    td_const_generator.run()

