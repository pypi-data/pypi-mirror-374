project(
  'homalos-ctp',
  'cpp',
  version: '6.7.11.1',
  license: 'MIT',
  meson_version: '>=1.9.0',
  default_options: [
    'buildtype=release',
    'cpp_std=c++17',
    'warning_level=2',
  ],
)

# 导入Python模块
py = import('python').find_installation(pure: false)
py_dep = py.dependency()

# 获取pybind11路径
python_cmd = host_machine.system() == 'windows' ? 'python' : 'python3'
pybind11_include_dir = run_command(python_cmd, '-c', 'import pybind11; print(pybind11.get_include())', check: true).stdout().strip()
message('使用pybind11路径: ' + pybind11_include_dir)

# 创建pybind11依赖对象
pybind11_dep = declare_dependency(
  compile_args: ['-I' + pybind11_include_dir]
)

# 获取编译器信息
cpp = meson.get_compiler('cpp')

# 输出构建目标系统信息
message('构建目标系统: ' + host_machine.system())

# 初始化变量
thostmduserapi_lib = []
thosttraderapi_lib = []
extra_cpp_args = []
extra_link_args = []

# 初始化库变量
thostmduserapi_lib = []
thosttraderapi_lib = []

# 初始化其他编译选项
extra_link_args = []
install_rpath_value = ''
api_abs_dir = 'homalos-ctp/api'

# 设置Windows特定编译选项
if host_machine.system() == 'windows'
  # Windows编译器设置 - 使用/MD与Python保持一致，避免运行时库冲突
  add_project_arguments('/MD', language : 'cpp')

  # 添加编码和安全警告屏蔽参数
  extra_cpp_args += [
    '/source-charset:GB2312',  # 使用GB2312编码匹配CTP API头文件编码
    '/execution-charset:GB2312',
    '-D_CRT_SECURE_NO_WARNINGS', 
    '-D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING',
    '/wd4819',  # 禁用C4819警告（字符编码警告）
    '/wd4828'   # 禁用C4828警告（UTF-8字符无效警告）
  ]

  # 设置库目录
  lib_dir = meson.current_source_dir() / api_abs_dir + '/libs'
  api_dir = meson.current_source_dir() / api_abs_dir

  # 设置include目录
  include_dirs = include_directories(
    api_abs_dir + '/include',
    api_abs_dir + '/src',
  )

  # 定义CTP库
  thostmduserapi_lib = cpp.find_library('thostmduserapi_se',
                                       dirs: [lib_dir, api_dir],
                                       required: true)
  thosttraderapi_lib = cpp.find_library('thosttraderapi_se',
                                       dirs: [lib_dir, api_dir],
                                       required: true)

# 设置Linux特定编译选项
else  # Linux
  # Linux编译器设置
  extra_cpp_args = [
    '-std=c++17',
    '-O3',
    '-Wno-delete-incomplete',
    '-Wno-sign-compare',
  ]

  extra_link_args = [
    '-lstdc++',
    '-Wl,-rpath,$ORIGIN',  # 添加rpath设置，使库能在运行时找到同目录下的动态库
  ]

  # 设置库目录
  lib_dir = meson.current_source_dir() / api_abs_dir

  # 设置include目录
  include_dirs = include_directories(
    api_abs_dir + '/include',
    api_abs_dir + '/src',
  )

  # 定义CTP库
  thostmduserapi_lib = cpp.find_library('thostmduserapi_se',
                                       dirs: [lib_dir],
                                       required: true)
  thosttraderapi_lib = cpp.find_library('thosttraderapi_se',
                                       dirs: [lib_dir],
                                       required: true)
endif

# 创建MD模块扩展
md_module = py.extension_module(
  'ctpmd',
  sources: [api_abs_dir + '/src/ctpmd/ctpmd.cpp'],
  include_directories: include_dirs,
  dependencies: [py_dep, pybind11_dep, thostmduserapi_lib],
  cpp_args: extra_cpp_args,
  link_args: extra_link_args,
  install: true,
  subdir: api_abs_dir
)

# 创建TD模块扩展
td_module = py.extension_module(
  'ctptd',
  sources: [api_abs_dir + '/src/ctptd/ctptd.cpp'],
  include_directories: include_dirs,
  dependencies: [py_dep, pybind11_dep, thosttraderapi_lib],
  cpp_args: extra_cpp_args,
  link_args: extra_link_args,
  install: true,
  subdir: api_abs_dir
)

# 安装Python源代码
python_files = [
  ['homalos-ctp/__init__.py', 'homalos-ctp'],
  ['homalos-ctp/api/__init__.py', 'homalos-ctp/api']
]

foreach file : python_files
  py.install_sources(
    [file[0]],
    pure: false,
    subdir: file[1]
  )
endforeach

# 安装API动态库文件
if host_machine.system() == 'windows'
  api_libs = [
    api_abs_dir + '/thostmduserapi_se.dll',
    api_abs_dir + '/thosttraderapi_se.dll',
  ]

  install_data(
    api_libs,
    install_dir: py.get_install_dir() / 'homalos-ctp/api'
  )
else  # Linux
  api_libs = [
    api_abs_dir + '/libthostmduserapi_se.so',
    api_abs_dir + '/libthosttraderapi_se.so',
  ]

  install_data(
    api_libs,
    install_dir: py.get_install_dir() / 'homalos-ctp/api'
  )
endif
