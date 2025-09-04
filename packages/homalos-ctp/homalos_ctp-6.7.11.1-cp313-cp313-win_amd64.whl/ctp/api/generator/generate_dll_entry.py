#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动生成C++ DLL入口点代码文件
生成dllmain.cpp、stdafx.cpp、stdafx.h三个文件
生成所有文件到当前目录
python generate_dll_entry.py all

生成到指定目录
python generate_dll_entry.py all ./output

只生成dllmain.cpp
python generate_dll_entry.py dllmain.cpp

预览stdafx.h内容
python generate_dll_entry.py preview stdafx.h
"""

import os
from typing import Dict

from ctp.api.generator.generate_helper import create_output_dir


class DllEntryGenerator:
    """DLL入口点代码生成器"""
    
    def __init__(self, prefix: str, name: str):
        """
        初始化生成器
        """
        self.prefix = prefix  # homalos-ctp/tts
        self.name = name  # md/td
        self.output_path = "."  # 输出目录
        # 输出目录名称，例如：ctpmd、ctptd
        self.output_dir_name = f"{self.prefix}{self.name}"

        self.files_to_generate = {
            'dllmain.cpp': self.generate_dllmain_cpp,
            'stdafx.cpp': self.generate_stdafx_cpp,
            'stdafx.h': self.generate_stdafx_h
        }

    @staticmethod
    def generate_dllmain_cpp() -> str:
        """生成dllmain.cpp文件内容"""
        content = """// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "stdafx.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
\tswitch (ul_reason_for_call)
\t{
\tcase DLL_PROCESS_ATTACH:
\tcase DLL_THREAD_ATTACH:
\tcase DLL_THREAD_DETACH:
\tcase DLL_PROCESS_DETACH:
\t\tbreak;
\t}
\treturn TRUE;
}

"""
        return content

    @staticmethod
    def generate_stdafx_cpp() -> str:
        """生成stdafx.cpp文件内容"""
        content = """#include "stdafx.h"

"""
        return content

    @staticmethod
    def generate_stdafx_h() -> str:
        """生成stdafx.h文件内容"""
        content = """// stdafx.h: 标准系统包含文件的包含文件，
// 或是经常使用但不常更改的
// 特定于项目的包含文件
//

#pragma once

#include "targetver.h"

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include <windows.h>



// 在此处引用程序需要的其他标头

"""
        return content


    def write_file(self, filename: str, content: str) -> bool:
        """
        写入文件
        
        Args:
            filename: 文件名
            content: 文件内容
            
        Returns:
            bool: 是否成功写入
        """
        filepath = os.path.join(self.output_path, filename)
        try:
            with open(filepath, 'w', encoding='gb2312') as f:
                f.write(content)
            print(f"成功生成 {filename}")

            return True
        except Exception as e:
            print(f"✗ 写入文件 {filename} 失败: {e}")
            return False
    
    def run(self) -> None:
        """
        生成所有文件
        
        Returns:
            Dict[str, bool]: 每个文件的生成结果
        """
        print("2. 第二步：生成DLL入口文件")

        # 创建输出目录
        self.output_path = create_output_dir(self.output_dir_name)
        if not self.output_path:
            print(f"无法创建输出目录{self.output_path}，终止生成")
            return
        
        # 生成每个文件
        for filename, generator_func in self.files_to_generate.items():
            try:
                content = generator_func()
                self.write_file(filename, content)
            except Exception as e:
                print(f"生成 {filename} 时发生错误: {e}")


if __name__ == "__main__":
    generator = DllEntryGenerator("homalos-ctp", "md")
    generator.run()

    generator = DllEntryGenerator("homalos-ctp", "td")
    generator.run()
