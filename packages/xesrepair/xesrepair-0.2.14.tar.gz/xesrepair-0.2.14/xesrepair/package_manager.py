import subprocess,sys
from thonny.common import get_user_lib_path

# 安装库,可以在库名后边用==a.b.c来指定版本，第二个参数mirror可以指定源
# 阿里源：https://mirrors.aliyun.com/pypi/simple/
# 清华源：https://pypi.tuna.tsinghua.edu.cn/simple
# 豆瓣源：https://pypi.douban.com/simple/
# pypi官方源：https://pypi.org/simple
# 学而思私有源：https://账号:密码@codepypi.xueersi.com/simple,需要替换账号和密码
def install_package(package_name, mirror=''):
    # 使用pip安装包

    #不能用xesrepair.common中的PYTHONW_EXE，会生成一个超级大的文件，很奇怪
    PYTHON_EXE = sys.executable
    USER_LIB_PATH = get_user_lib_path()
    cmd = [PYTHON_EXE, "-m", "pip", "install", "-t", USER_LIB_PATH, "--no-cache-dir", '--no-warn-script-location', "--upgrade"]
    package_names = package_name.split(" ")
    for package_name in package_names:
        if package_name.strip() != "":
            cmd.append(package_name)
    if mirror != '' and mirror is not None:
        cmd.append("-i")
        cmd.append(mirror)
    print(" ".join(cmd))
    subprocess.check_call(cmd)

# 卸载库
def uninstall_package(package_name):
    PYTHON_EXE = sys.executable
    cmd = [PYTHON_EXE, "-m", "pip", "uninstall", "-y", package_name]
    subprocess.check_call(cmd)
    
# 查看库版本
def show_package(package_name):
    PYTHON_EXE = sys.executable
    cmd = [PYTHON_EXE, "-m", "pip", "show", package_name]
    subprocess.check_call(cmd)
    
if __name__ == "__main__":
    # 安装库
    # install_package("ursina==5.2.0", mirror="https://账号:密码@codepypi.xueersi.com/simple")
    # 卸载库
    # uninstall_package("ursina")
    # 查看库版本
    # show_package("ursina")
    pass

