<p align="center">
  简体中文 |
  <a href="README_CN.md">English</a>
</p>

# 项目说明

用于根据CTP C++ API 自动化生成 Python API，便于 CTP Python 开发者维护最新的 CTP 接口，实现 CTP 版本的快速升级。

注意：本项目仅在CTP v6.7.11下测试通过，其他版本未做测试，项目 CTP 版本号配置位于`ctp/__init__.py`文件。

## 1. 编译环境

本项目使用以下环境编译，若自行使用其他工具版本，请做相应调整。

- **Windows 11 + MSVC 2022**
- **Python 3.13.6** 虚拟环境，由 UV 安装。
- **CTP v6.7.11**：[CTP官方下载地址](https://www.simnow.com.cn/static/apiDownload.action)
- **Meson + Ninja**: 现代化的C++扩展构建系统。
- **Pybind11**: Python - C++绑定。
- **UV**: 现代化Python包管理器，提供更快的安装速度和更智能的依赖解析。

## 2. 项目结构

```reStructuredText
ctp/
├── 📂 assets/								# 资源文件
├── 📂 ctp/ 								# CTP接口模块
│   ├── 📂 api/ 							# CTP API模块
│   │   ├── 📂 generator/ 					# C++与Python绑定生成脚本
│   │   ├── 📂 include/ 					# CTP API头文件
│   │   ├── 📂 libs/ 						# CTP API静态库文件
│   │   ├── 📂 src/ 						# CTP与Python绑定代码文件
│   │   ├── 📁 __init__.py 					# MdApi和TdApi初始化导入
│   │   ├── 📁 ctpmd.cp313-win_amd64.pyd	# C++编译为Python的行情扩展模块
│   │   ├── 📁 ctpmd.pyi 					# 行情扩展模块对应的存根文件
│   │   ├── 📁 ctptd.cp313-win_amd64.pyd	# C++编译为Python的交易扩展模块
│   │   ├── 📁 ctptd.pyi 					# 交易扩展模块对应的存根文件
│   │   ├── 📁 thostmduserapi_se.dll		# Windows CTP行情API动态链接库
│   │   ├── 📁 thostmduserapi_se.so			# Linuxs CTP行情API动态链接库
│   │   ├── 📁 thosttraderapi_se.dll		# Windows CTP交易API动态链接库
│   │   ├── 📁 thosttraderapi_se.so			# Linuxs CTP交易API动态链接库
│   ├── 📁 __init__.py						# CTP版本配置文件
│   ├── 📁 ctp.h							# 任务处理及编码转换
├── 📂 docs/								# 项目相关文档
├── 📁 .gitignore							# git提交忽略文件，由uv自动生成
├── 📁 .python-version						# 项目Python版本文件，由uv自动生成
├── 📁 LICENSE								# 项目License文件
├── 📁 README.md							# 项目中文说明文件
├── 📁 README_CN.md							# 项目英文说明文件
├── 📁 build.py								# 扩展模块自动化编译脚本，组装了meson命令
├── 📁 demo.py								# 扩展模块使用示例
├── 📁 hatch_build.py						# hatch钩子，用hatch打包时设置平台标识
├── 📁 meson.build							# meson构建配置文件
├── 📁 pyproject.toml						# Python项目管理配置文件，由uv自动生成
└── 📁 uv.lock								# uv锁定文件，由uv自动生成
```

## 3. 安装基础环境(已安装可跳过)

1. 安装UV

   On Windows

   **方式一：全局安装(推荐方式，二选一)**

   ```bash
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   **方式二：单独在 Python 环境中安装(二选一)**

   ```bash
   pip install uv
   ```

   On Linux

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. 安装 Python(方式一进行这一步，方式二直接跳过)，我自己用的是 3.13.6，你可以安装自己需要的版本

   ```bash
   uv python install 3.13
   ```

## 4. 使用

1. 安装 Python 虚拟环境及依赖(根目录下执行)

   ```bash
   # 使用uv在当前项目下创建指定版本的Python虚拟环境
   uv venv --python 3.13 .venv
   ```
   ```bash
   # 安装依赖库
   uv add meson-python
   uv add pybind11
   uv add pybind11-stubgen
   ```

2. 在`generator`目录下执行生成一键生成脚本(生成 CTP C++ API 的 Python 绑定代码)

   ```bash
   # 激活Python虚拟环境进入generator
   .venv\Scripts\activate
   cd homalos-ctp\api\generator
   ```
   ```bash
   # 一键生成绑定文件
   python generate_onekey.py
   ```

3. 根目录执行如下构建脚本，生成 CTP 的 C++ API 封装成 Python 可调用的接口

   ```bash
   # 一键编译出CTP Python API
   python build.py
   ```

## 5. Demo测试

在项目根目录下 `demo.py`中填入 CTP 环境信息后运行

## 6. 脚本功能详细说明

generator脚本位于`ctp/api/generator/`

1. `generator_function_const.py`

- **作用**：**生成基础函数常量文件**
- **功能**：
  - 读取CTP的头文件 `ThostFtdcMdApi.h`、`ThostFtdcTraderApi.h.h`
  - 解析其中的函数，生成 `ctp_function_const.py`（函数常量定义）

2. `generate_data_type.py`

- **作用**：**生成数据类型定义文件**
- **功能**：
  - 读取CTP的头文件 `ThostFtdcUserApiDataType.h`
  - 解析其中的 `#define` 常量定义和 `typedef` 类型定义
  - 生成 `ctp_function_const.py`

3. `generate_struct.py`

- **作用**：**生成结构体定义文件**
- **功能**：
  - 读取CTP的头文件 `ThostFtdcUserApiStruct.h`
  - 依赖 `ctp_typedef.py` 中的类型映射
  - 解析C++结构体定义，生成Python字典格式的结构体定义文件 `ctp_struct.py`

4. `generate_api_functions.py`

- **作用**：**生成API函数绑定代码**
- **功能**：
  - 读取CTP的API头文件（如 `ThostFtdcTraderApi.h`、`ThostFtdcMdApi.h`）
  - 依赖 `ctp_struct.py` 中的结构体定义
  - 生成大量的C++源代码文件，用于Python绑定

5. `generate_dll_entry.py`

- **作用**：**生成C++ DLL入口点代码文件**
- **功能**：
  - 生成`dllmain.cpp`、`stdafx.cpp`、`stdafx.h`三个文件
  - **dllmain.cpp**: 包含标准的DLL入口点函数，处理进程和线程的加载/卸载
  - **stdafx.cpp**: 简单的预编译头包含文件
  - **stdafx.h**: 包含Windows API头文件和常用定义

6. `generate_cpp.py`

- **作用**：**生成cpp和h文件**
- **功能**：
  - 分别在`ctp.api.src.ctpmd`和`ctp.api.src.ctptd`中生成`ctpmd.cpp`、`ctpmd.h`和`ctptd.cpp`、`ctptd.h`四个文件
  - 头文件包含完整的类声明和函数原型
  - CPP文件包含所有实现和绑定

7. `generate_onekey.py`

- **作用**：**一键组装所有md和td header、source等文件生成cpp和h文件**
- **功能**：
  - 一键组装上述文件生成的文件及header、source等文件生成`ctpmd.cpp`、`ctpmd.h`和`ctptd.cpp`、`ctptd.h`四个文件

8. `build.py`

- **作用**：**一键将CTP C++ API 编译为 Python API**
- **功能**：
  - 一键编译出 Python 可调用的 CTP API 文件，文件位于`ctp/api/`包括：
    - `ctpmd.cp313-win_amd64.pyd`
    - `ctptd.cp313-win_amd64.pyd`
    - `ctpmd.pyi`
    - `ctptd.pyi`

文件依赖关系：

1. **`generator_function_const.py`** → 生成`ctp_function_const.py`
2. **`generate_data_type.py`** → 生成 `ctp_typedef.py` 和 `ctp_constant.py`
3. **`generate_struct.py`**(依赖`ctp_typedef.py`) → 生成 `ctp_struct.py`
4. **`generate_api_functions.py`**(依赖`ctp_struct.py`、`ctp_function_const.py`) → 生成md和td多个API header、source绑定文件
5. **`generate_dll_entry.py`** → 生成 `dllmain.cpp`、`stdafx.cpp`、`stdafx.h`
6. **`generate_cpp.py`**(依赖上述所有文件生成的文件及header、source文件) →  生成`ctpmd.cpp`、`ctpmd.h`和`ctptd.cpp`、`ctptd.h`
7. **`generate_onekey.py`** → 一键组装出`ctpmd.cpp`、`ctpmd.h`和`ctptd.cpp`、`ctptd.h`文件(相当于上述过程一键执行)
8. **`build.py`**(依赖`ctp/api/src/`下的`ctpmd`和`ctptd`模块) → 一键编译出`ctpmd.cp313-win_amd64.pyd`、`ctptd.cp313-win_amd64.pyd`、`ctpmd.pyi`、`ctptd.pyi`


## 7. 脚本用途

这些脚本最终生成的代码用于：
- 将CTP的C++ API封装成Python可调用的接口
- 自动处理数据类型转换
- 生成回调函数的Python绑定
- 生成请求函数的Python绑定


## 8. 优势

- 使用pybind将C++与Python CTP API绑定，性能优于Swig转换方式。
- 自动同步: 当CTP官方更新头文件时，替换最新h、dll、so、lib文件，执行生成脚本后，脚本会自动反映最新的虚函数
- 易于维护: 无需手动更新大量硬编码的函数声明
- 减少错误: 避免了手动维护可能导致的遗漏或错误
- 提高效率: 开发者只需关注业务逻辑，不用担心底层接口变化

总结：这是一个完整的代码生成工具链，用于自动化生成CTP API的Python绑定代码，避免手工编写大量重复的绑定代码，具有更好的可维护性和健壮性！

## 9. 社区支持

- **技术交流 (QQ Group)**: `446042777`

## 10. 免责声明

**[免责声明内容](docs/免责声明.md)**

## 11. 补充

**Meson**: 类似于Make、CMake，它的主要任务是配置编译环境、生成编译指令（比如给Ninja），并管理整个编译过程。它本身并不直接编译代码，而是驱动像Ninja这样的工具来完成。

**Pybind11**: 轻量级的 C++ 库，用于将 C++ 代码暴露（绑定）给 Python 解释器。它允许 Python 代码像调用普通 Python 模块一样，无缝地调用 C++ 编写的函数和类。其核心目标是提供一个极致简单、近乎零样板代码的接口，能轻松地将 C++ 的高性能计算能力与 Python 的易用性和庞大的生态系统结合起来。