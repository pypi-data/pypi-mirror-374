from xesrepair.add_cdn import addCdnsFn
import platform
import os
from xesrepair.common import PYTHONW_EXE, USER_LIB_PATH, create_python_process
import subprocess
import sys
import importlib
from xesrepair.update_cert import handle_update_cert
PACKAGE_NAME = 'xesrepair'
name = PACKAGE_NAME

SHOW_BUTTON = True  # 是否在学而思编程助手的托盘处进行清理
__version__ = "0.2.9"

addCdnsFn()

handle_update_cert()


class RepairHandler:
    def __init__(self):
        self._modules = ['numpy', 'imageio']  # 待检查的库

    def check_common(self, name):
        try:
            check_module = importlib.import_module(name)
            # 更新
            importlib.reload(sys.modules[name])
            # except Exception as e:
            #     print(e)
            print(check_module.__version__)
            return {"state": True}
        except Exception as e:
            print("check error:"+str(e))
            return {"state": False, "reason": str(e)}

    def repair_common(self, name):
        '''
        :return 修复后再次检测的结果
        '''
        check_res = self.check_common(name)
        if check_res['state']:
            return check_res

        # 通用修复
        # 先卸载
        uninstall_args = [PYTHONW_EXE, "-m", "pip", "uninstall", "-y", name]
        create_python_process(uninstall_args)
        # 再安装
        install_args = [PYTHONW_EXE, "-m", "pip", "install", '--target', USER_LIB_PATH, name, '--no-cache-dir',
                        '--no-warn-script-location', "--index-url", 'https://mirrors.aliyun.com/pypi/simple/', "--upgrade"]
        create_python_process(install_args)

        # 修复后再次检测验证有没有修复成功
        check_res = self.check_common(name)
        return check_res

    def run(self):
        total_check_res = {"state": True}
        # for module in self._modules:
        #     try:
        #         check_module = importlib.import_module(
        #             PACKAGE_NAME+".repair_"+module)
        #         single_check_res = check_module.repair()
        #     except Exception as e:
        #         print(module + ".run() error:"+str(e))
        #         single_check_res = self.repair_common(module)
        #     finally:
        #         # 存储每个模块修复的结果
        #         total_check_res[module] = single_check_res
        #         total_check_res["state"] = total_check_res["state"] and single_check_res["state"]
        if platform.system() == "Windows":
            try:
                from xesrepair.repair_dll import fn_repair_dll_not_found
                fn_repair_dll_not_found()
            except Exception as e:
                total_check_res = {"state": False, "msg": str(e)}
        return total_check_res
