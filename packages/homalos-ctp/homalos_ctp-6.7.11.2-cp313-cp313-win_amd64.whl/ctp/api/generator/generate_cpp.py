#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ProjectName: homalos-ctp
@FileName   : generate_cpp.py
@Date       : 2025/8/27 14:53
@Author     : Donny
@Email      : donnymoving@gmail.com
@Software   : PyCharm
@Description: CTP MD和TD API CPP文件自动拼装脚本
从生成的header和source文件自动拼装生成完整的ctpmd.cpp、ctpmd.h、ctptd.cpp、ctptd.h文件
"""
import os
from pathlib import Path
from typing import List

from ctp.api.generator.generate_helper import create_output_dir


class GenerateCpp:
    """MD和TD CPP文件拼装器"""
    
    def __init__(self, filename: str, prefix: str, name: str):
        self.filename: str = filename  # ../include/ThostFtdcMdApi.h/../include/ThostFtdcTraderApi.h
        self.prefix: str = prefix  # homalos-ctp/tts
        self.name: str = name  # md/td

        if self.name == "md":
            self.class_name: str = "MdApi"
            self.full_class_name: str = "CThostFtdcMdSpi"
        else:
            self.class_name: str = "TdApi"
            self.full_class_name: str = "CThostFtdcTraderSpi"

        self.h_filename = Path(self.filename).name  # ThostFtdcMdApi.h/ThostFtdcTraderApi.h
        self.file_prefix: str = f"{self.prefix}{self.name}"

        self.output_filename: str = f"{self.file_prefix}.cpp"  # 例如：homalos-ctp/ctpmd.cpp
        self.output_header_filename: str = f"{self.file_prefix}.h"  # 例如：homalos-ctp/ctpmd.h

        # 定义所需的文件
        self.header_files = {
            'define': f'{self.prefix}_{self.name}_header_define.h',
            'function': f'{self.prefix}_{self.name}_header_function.h',
            'on': f'{self.prefix}_{self.name}_header_on.h',
            'process': f'{self.prefix}_{self.name}_header_process.h'
        }

        self.source_files = {
            'task': f'{self.prefix}_{self.name}_source_task.cpp',
            'switch': f'{self.prefix}_{self.name}_source_switch.cpp',
            'process': f'{self.prefix}_{self.name}_source_process.cpp',
            'function': f'{self.prefix}_{self.name}_source_function.cpp',
            'on': f'{self.prefix}_{self.name}_source_on.cpp',
            'module': f'{self.prefix}_{self.name}_source_module.cpp'
        }
        # md cpp 头文件内容
        self.md_header_content = """
///-------------------------------------------------------------------------------------
///C++ SPI的回调函数的继承实现
///-------------------------------------------------------------------------------------

//API的继承实现
class MdApi : public CThostFtdcMdSpi
{
private:
\tCThostFtdcMdApi* api;\t\t\t\t//API对象
\tthread task_thread;\t\t\t\t\t//工作线程指针（向python推送数据）
\tTaskQueue task_queue;\t\t\t//任务队列
\tbool active = false;\t\t\t\t//活动状态

public:
\tMdApi()
\t{
\t};

\tvirtual ~MdApi()
\t{
\t\tif (this->active)
\t\t{
\t\t\tthis->exit();
\t\t}
\t};

\t//-------------------------------------------------------------------------------------
\t//从CThostFtdcMdSpi继承的C++回调函数
\t//-------------------------------------------------------------------------------------

"""
        # td cpp 头文件内容
        self.td_header_content = """
///-------------------------------------------------------------------------------------
///C++ SPI的回调函数的继承实现
///-------------------------------------------------------------------------------------

//API的继承实现
class TdApi : public CThostFtdcTraderSpi
{
private:
\tCThostFtdcTraderApi* api;\t\t\t\t//API对象
\tthread task_thread;\t\t\t\t\t//工作线程指针（向python推送数据）
\tTaskQueue task_queue;\t\t\t\t//任务队列
\tbool active = false;\t\t\t\t//活动状态

public:
\tTdApi()
\t{
\t};

\tvirtual ~TdApi()
\t{
\t\tif (this->active)
\t\t{
\t\t\tthis->exit();
\t\t}
\t};

\t//-------------------------------------------------------------------------------------
\t//从CThostFtdcTraderSpi继承的C++回调函数
\t//-------------------------------------------------------------------------------------

"""
        # md cpp 文件内容
        self.md_cpp_content = """
///-------------------------------------------------------------------------------------
///工作线程从队列中取出数据，转化为python对象后，进行推送
///-------------------------------------------------------------------------------------

void MdApi::processTask()
{
\ttry
\t{
\t\twhile (this->active)
\t\t{
\t\t\tTask task = this->task_queue.pop();

\t\t\tswitch (task.task_name)
\t\t\t{
"""
        # td cpp 文件内容
        self.td_cpp_content = """
///-------------------------------------------------------------------------------------
///工作线程从队列中取出数据，转化为python对象后，进行推送
///-------------------------------------------------------------------------------------

void TdApi::processTask()
{
\ttry
\t{
\t\twhile (this->active)
\t\t{
\t\t\tTask task = this->task_queue.pop();

\t\t\tswitch (task.task_name)
\t\t\t{
"""
        self.md_pybind_header = """
///-------------------------------------------------------------------------------------
///pybind11封装
///-------------------------------------------------------------------------------------

class PyMdApi: public MdApi
{
public:
\tusing MdApi::MdApi;

"""
        self.md_pybind_content = """};


PYBIND11_MODULE(ctpmd, m)
{
\tclass_<MdApi, PyMdApi> mdapi(m, "MdApi", module_local());
\tmdapi
\t\t.def(init<>())
"""

        self.td_pybind_header = """
///-------------------------------------------------------------------------------------
///pybind11封装
///-------------------------------------------------------------------------------------

class PyTdApi : public TdApi
{
public:
\tusing TdApi::TdApi;

"""
        self.td_pybind_content = """};


PYBIND11_MODULE(ctptd, m)
{
\tclass_<TdApi, PyTdApi> tdApi(m, "TdApi", module_local());
\ttdApi
\t\t.def(init<>())
"""

    @staticmethod
    def read_file_content(filename: str) -> str:
        """读取文件内容"""
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                return content
        except Exception as e:
            print(f"读取文件 {filename} 失败: {e}")
            return ""
    
    def extract_virtual_functions_from_header(self, header_file_path: str, class_name: str) -> str:
        """从头文件中提取虚函数声明"""
        try:
            content = self.read_file_content(header_file_path)
            if not content:
                return ""
            
            # 查找类定义的开始
            class_start = content.find(f"class {class_name}")
            if class_start == -1:
                return ""
            
            # 查找类定义的结束（配对的大括号）
            brace_count = 0
            class_body_start = content.find("{", class_start)
            if class_body_start == -1:
                return ""
            
            class_end = class_body_start
            for i in range(class_body_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            # 提取类体内容
            class_body = content[class_body_start+1:class_end]
            
            # 提取虚函数声明
            virtual_functions = []
            lines = class_body.split('\n')
            
            current_function = ""
            in_function = False
            
            for line in lines:
                line = line.strip()
                
                # 跳过注释行
                if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                    continue
                
                # 检查是否是虚函数开始
                if line.startswith('virtual') and '(' in line:
                    in_function = True
                    current_function = line
                    
                    # 检查是否在同一行结束
                    if ';' in line:
                        # 移除函数体 {} 部分
                        if '{' in current_function:
                            current_function = current_function[:current_function.find('{')].strip()
                        if current_function.endswith('{}'):
                            current_function = current_function[:-2].strip()
                        if current_function.endswith(';'):
                            current_function = current_function[:-1].strip()
                        
                        virtual_functions.append(current_function + ';')
                        in_function = False
                        current_function = ""
                
                elif in_function:
                    # 多行函数声明
                    current_function += " " + line
                    if ';' in line:
                        # 移除函数体 {} 部分
                        if '{' in current_function:
                            current_function = current_function[:current_function.find('{')].strip()
                        if current_function.endswith('{}'):
                            current_function = current_function[:-2].strip()
                        if current_function.endswith(';'):
                            current_function = current_function[:-1].strip()
                        
                        virtual_functions.append(current_function + ';')
                        in_function = False
                        current_function = ""
            if virtual_functions:
                # 格式化虚函数声明，添加缩进
                formatted_functions = []
                for func in virtual_functions:
                    if func.strip():
                        formatted_functions.append('\t' + func.strip())

                return '\n\n'.join(formatted_functions)
            else:
                print(f"警告：无法从 {header_file_path} 提取虚函数，使用后备方案")
                return ""
            
        except Exception as e:
            print(f"解析头文件 {header_file_path} 时出错: {e}")
            return ""

    @staticmethod
    def format_switch_case(case_content: str) -> str:
        """格式化switch case语句，确保对齐正确"""
        lines = case_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.rstrip()
            if line.startswith('case '):
                # case语句前加制表符缩进
                formatted_lines.append('\t\t\t' + line)
            elif line.startswith('{'):
                # 左大括号缩进
                formatted_lines.append('\t\t\t' + line)
            elif line.startswith('}'):
                # 右大括号缩进
                formatted_lines.append('\t\t\t' + line)
            elif line.strip() == 'break;':
                # break语句缩进
                formatted_lines.append('\t\t\t\t' + 'break;')
            elif line.strip().startswith('this->'):
                # 函数调用缩进
                formatted_lines.append('\t\t\t\t' + line.strip())
            elif line.strip() == '':
                # 保持空行
                formatted_lines.append('')
            else:
                # 其他内容适当缩进
                if line.strip():
                    formatted_lines.append('\t\t\t\t' + line.strip())
                else:
                    formatted_lines.append('')
                
        return '\n'.join(formatted_lines)
    
    def generate_header_file(self) -> str:
        """生成头文件内容 - 使用动态解析"""
        header_content = f"""//系统
#ifdef WIN32
#include "stdafx.h"
#endif

#include "homalos-ctp.h"
#include "pybind11/pybind11.h"
#include "homalos-ctp/api/include/{self.h_filename}"

using namespace pybind11;

//常量
"""
        
        # 添加定义常量
        defines = self.read_file_content(self.header_files['define'])
        header_content += defines + "\n\n"

        if self.name == "md":
            header_content += self.md_header_content
        else:
            header_content += self.td_header_content
        
        # 动态提取虚函数声明
        virtual_functions = self.extract_virtual_functions_from_header(self.filename, self.full_class_name)
        if virtual_functions:
            header_content += virtual_functions + "\n"
        else:
            # 如果提取失败，使用基本的虚函数声明作为后备
            print(f"警告：无法从{self.full_class_name}提取虚函数，使用后备方案")

        header_content += """

\t//-------------------------------------------------------------------------------------
\t//工作线程处理函数
\t//-------------------------------------------------------------------------------------

\tvoid processTask();

"""
        
        # 添加处理函数声明
        process_declarations = self.read_file_content(self.header_files['process'])
        proc_lines = process_declarations.split('\n')
        formatted_proc = []
        for line in proc_lines:
            if line.strip():
                formatted_proc.append('\t' + line.strip())
            else:
                formatted_proc.append('')
        header_content += '\n'.join(formatted_proc) + "\n\n"

        header_content += """
\t//-------------------------------------------------------------------------------------
\t//Python回调函数
\t//data：回调函数的数据字典
\t//error：回调函数的错误字典
\t//id：请求id
\t//last：是否为最后返回
\t//i：整数
\t//-------------------------------------------------------------------------------------

"""
        
        # 添加on函数声明
        on_declarations = self.read_file_content(self.header_files['on'])
        on_lines = on_declarations.split('\n')
        formatted_on = []
        for line in on_lines:
            if line.strip():
                formatted_on.append('\t' + line.strip())
            else:
                formatted_on.append('')
        header_content += '\n'.join(formatted_on) + "\n\n"
        
        header_content += """\t//-------------------------------------------------------------------------------------
\t//主动函数
\t//-------------------------------------------------------------------------------------

"""
        
        # 添加函数声明
        function_declarations = self.read_file_content(self.header_files['function'])
        func_lines = function_declarations.split('\n')
        formatted_func = []
        for line in func_lines:
            if line.strip():
                formatted_func.append('\t' + line.strip())
            else:
                formatted_func.append('')
        header_content += '\n'.join(formatted_func) + "\n"
        
        header_content += "};\n"
        
        return header_content
    

    def generate_cpp_file(self) -> str:
        """生成CPP文件内容"""
        cpp_content = f"""// homalos-ctp{self.name}.cpp : 定义 DLL 应用程序的导出函数。
#include "homalos-ctp{self.name}.h"


///-------------------------------------------------------------------------------------
///C++的回调函数将数据保存到队列中
///-------------------------------------------------------------------------------------

"""
        
        # 添加任务处理部分
        task_content = self.read_file_content(self.source_files['task'])
        cpp_content += task_content + "\n\n"
        
        # 添加工作线程处理部分
        if self.name == "md":
            cpp_content += self.md_cpp_content
        else:
            cpp_content += self.td_cpp_content
        
        # 添加switch语句内容并格式化
        switch_content = self.read_file_content(self.source_files['switch'])
        formatted_switch = self.format_switch_case(switch_content)
        cpp_content += formatted_switch + "\n"
        
        cpp_content += """\t\t\t};
\t\t}
\t}
\tcatch (const TerminatedError&)
\t{
\t}
};

"""
        
        # 添加处理函数实现
        process_content = self.read_file_content(self.source_files['process'])
        cpp_content += process_content + "\n\n"
        
        # 添加主动函数部分
        cpp_content += """///-------------------------------------------------------------------------------------
///主动函数
///-------------------------------------------------------------------------------------

"""
        
        function_content = self.read_file_content(self.source_files['function'])
        # # 修复函数实现中的void::CreateFtdcMdApi错误
        # function_content = function_content.replace("void::CreateFtdcMdApi", "CThostFtdcMdApi::CreateFtdcMdApi")
        cpp_content += function_content + "\n\n"
        
        # 添加pybind11封装部分
        if self.name == "md":
            cpp_content += self.md_pybind_header
        else:
            cpp_content += self.td_pybind_header

        # 添加on函数重载实现
        on_content = self.read_file_content(self.source_files['on'])

        # 为on函数添加正确的缩进
        on_lines = on_content.split('\n')
        formatted_on = []
        for line in on_lines:
            if line.strip():
                formatted_on.append('\t' + line)
            else:
                formatted_on.append('')
        cpp_content += '\n'.join(formatted_on) + "\n"

        if self.name == "md":
            cpp_content += self.md_pybind_content
        else:
            cpp_content += self.td_pybind_content

        # 添加模块绑定
        module_content = self.read_file_content(self.source_files['module'])
        # 为模块绑定添加适当的缩进
        module_lines = module_content.split('\n')
        formatted_module = []
        for line in module_lines:
            if line.strip():
                if line.startswith('.def'):
                    formatted_module.append('\t\t' + line.strip())
                elif line.strip() == ';':
                    formatted_module.append('\t\t' + line.strip())
                else:
                    formatted_module.append('\t' + line.strip())
            else:
                formatted_module.append('')
        
        cpp_content += '\n'.join(formatted_module) + "\n"
        
        cpp_content += "}\n"
        
        return cpp_content

    def fix_encoding_and_format(self, content: str) -> str:
        """修复编码问题和格式化"""
        # 修复常见的编码问题
        replacements = {
            "constants ": "const ",
            "void::": f"CThostFtdc{self.class_name}::",
            "\t    ": "\t",  # 统一缩进
            "    \t": "\t",  # 统一缩进
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        return content
    
    def assemble(self) -> None:
        """拼装生成完整文件"""
        # 创建输出目录
        output_path = create_output_dir(self.file_prefix)
        if not output_path:
            print(f"无法创建输出目录{self.file_prefix}，终止生成")
            return

        full_output_header_filename = f"{output_path}/{self.output_header_filename}"
        full_output_filename = f"{output_path}/{self.output_filename}"
        
        # 生成头文件
        header_content = self.generate_header_file()
        header_content = self.fix_encoding_and_format(header_content)
        
        # 生成CPP文件
        cpp_content = self.generate_cpp_file()
        cpp_content = self.fix_encoding_and_format(cpp_content)
        
        # 写入头文件
        try:
            with open(full_output_header_filename, 'w', encoding='gb2312') as f:
                f.write(header_content)
            print(f"成功生成头文件: {full_output_header_filename}")
        except Exception as e:
            print(f"写入头文件失败: {e}")
            
        # 写入CPP文件
        try:
            with open(full_output_filename, 'w', encoding='gb2312') as f:
                f.write(cpp_content)
            print(f"成功生成CPP文件: {full_output_filename}")
        except Exception as e:
            print(f"写入CPP文件失败: {e}")
    
    def check_required_files(self) -> List[str]:
        """检查必要文件是否存在"""
        missing_files = []
        
        # 检查头文件
        for name, filename in self.header_files.items():
            if not os.path.exists(filename):
                missing_files.append(f"头文件: {filename}")
                
        # 检查源文件
        for name, filename in self.source_files.items():
            if not os.path.exists(filename):
                missing_files.append(f"源文件: {filename}")
                
        return missing_files
    
    def run(self):
        """运行拼装程序"""
        print("6. 第六步：生成API cpp、h文件")

        # 检查必要的文件是否存在
        missing_files = self.check_required_files()
        
        if missing_files:
            print("错误：以下必要文件不存在：")
            for file in missing_files:
                print(f"  - {file}")
            return
        
        self.assemble()


if __name__ == "__main__":
    md_assembler = GenerateCpp("../include/ThostFtdcMdApi.h", "homalos-ctp", "md")
    md_assembler.run()

    td_assembler = GenerateCpp("../include/ThostFtdcTraderApi.h", "homalos-ctp", "td")
    td_assembler.run()
