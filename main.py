import ctypes
import sys

from PyQt6.QtWidgets import QApplication

from function import NetManage
from ui import Window


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":

    if not is_admin():
        # 请求管理员权限并重启脚本
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    app = QApplication(sys.argv)
    window = Window()
    net = NetManage(window=window)
    net.get_network_adapters()

    adapter_names = [adapter["Name"] for adapter in net.adapters]
    window.adapter_combobox.addItems(adapter_names)
    window.adapter_combobox.currentTextChanged.connect(lambda: net.get_optimized(window.adapter_combobox.currentText()))
    adapter = adapter_names[0]

    net.get_optimized(adapter)

    window.show()
    sys.exit(app.exec())
