import os
import shutil
import subprocess
import sys
import sysconfig


def check_and_install_stubgen():
    """检查并安装基础依赖工具"""
    # 获取 Python 版本
    print("正在检查当前 Python 版本...")
    subprocess.run([sys.executable, '-c', 'import sys; print(sys.version)'])

    try:
        import mesonbuild
        print("meson-python 已安装")
    except ImportError:
        print("未找到 meson-python，正在尝试安装...")
        ret = subprocess.run(['uv', 'add', 'meson-python'])
        if ret.returncode != 0:
            print("安装 meson-python 失败，请手动安装后再试")
            return False
    try:
        import pybind11
        print("pybind11 已安装")
    except ImportError:
        print("未找到 pybind11，正在尝试安装...")
        ret = subprocess.run(['uv', 'add', 'pybind11'])
        if ret.returncode != 0:
            print("安装 pybind11 失败，请手动安装后再试")
            return False
    try:
        import pybind11_stubgen
        print("pybind11-stubgen 已安装")
    except ImportError:
        print("未找到 pybind11-stubgen，正在尝试安装...")
        ret = subprocess.run(['uv', 'add', 'pybind11-stubgen'])
        if ret.returncode != 0:
            print("安装 pybind11-stubgen 失败，请手动安装后再试")
            return False

    return True

def setup_build() -> None:
    """设置构建环境"""
    build_dir = 'build'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"已删除目录: {build_dir}")
    # 执行 meson setup build
    print("正在设置构建环境...")
    ret = subprocess.run(['meson', 'setup', build_dir])
    if ret.returncode != 0:
        print('meson setup build 失败，自动退出。')
        sys.exit(1)
    print("构建环境设置完成。")


def compile_modules() -> None:
    """编译所有模块"""
    # 执行 meson compile -C build
    print("正在编译所有模块...")
    ret = subprocess.run(['meson', 'compile', '-C', 'build'])
    if ret.returncode != 0:
        print('meson compile 失败。')
        sys.exit(1)
    print("所有模块编译完成。")


def copy_module_files(module_name: str, module_names: list[str]) -> None:
    """复制指定模块的编译产物到目标目录"""
    # 动态确定 .pyd 文件名
    # 以下几行替换了原始硬编码的 pyd_files 列表
    ext_suffix = sysconfig.get_config_vars().get('EXT_SUFFIX')
    # 在 Windows 上使用 Python 3.13 的系统中，ext_suffix 示例：'.cp313-win_amd64.pyd'
    pyd_files = [f'{mod_name}{ext_suffix}' for mod_name in module_names]

    # 复制生成的pyd文件到目标目录
    build_dir = 'build'
    target_dir = os.path.join(module_name, 'api')

    print(f"正在复制{module_name}模块文件...")
    for pyd in pyd_files:
        src_path = os.path.join(build_dir, pyd)
        dst_path = os.path.join(target_dir, pyd)
        try:
            shutil.copy2(src_path, dst_path)
            print(f'已复制 {src_path} 到 {dst_path}')
        except FileNotFoundError as e:
            print(f'文件不存在: {src_path}: {e}')
        except PermissionError as e:
            print(f'权限不足: {e}')
        except OSError as e:
            print(f'复制 {src_path} 失败: {e}')


def generate_stub_files(module_name: str, module_names: list[str]) -> None:
    """为指定模块生成存根文件"""
    print(f"正在为{module_name}模块生成存根文件...")
    # 自动生成存根文件，使用包名并设置PYTHONPATH
    # 设置PYTHONPATH环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath('ctp') + os.pathsep + env.get('PYTHONPATH', '')

    stub_modules = [f'{module_name}.api.{mod_name}' for mod_name in module_names]

    for mod_base in stub_modules:
        print(f'正在为 {mod_base} 生成存根文件...')
        ret = subprocess.run([
            sys.executable, '-m', 'pybind11_stubgen',
            f'-o=.',
            mod_base
        ], env=env)
        if ret.returncode != 0:
            print(f'为 {mod_base} 生成存根文件失败。')
        else:
            print(f'为 {mod_base} 生成存根文件成功。')

def build_ctp() -> None:
    """构建CTP模块"""
    print("=" * 80)
    print("构建CTP模块")
    print("=" * 80)
    copy_module_files('homalos-ctp', ['ctpmd', 'ctptd'])
    generate_stub_files('homalos-ctp', ['ctpmd', 'ctptd'])


def main() -> None:
    """主构建流程"""
    print("CTP API 构建脚本")
    print("=" * 80)

    try:
        # 检查并安装 pybind11-stubgen
        check_and_install_stubgen()

        # 设置构建环境
        setup_build()

        # 编译所有模块
        compile_modules()

        # 处理各模块的构建产物
        build_ctp()

        print("=" * 80)
        print("所有模块构建流程已全部完成！")

    except KeyboardInterrupt:
        print("\n构建过程被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
