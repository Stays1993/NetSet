import ctypes
import sys

from PyQt6.QtWidgets import QApplication

from function import NetManage, IPList
from ui import Window


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":

    if not is_admin():
        # 请求管理员权限并重启脚本
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    app = QApplication(sys.argv)
    window = Window()
    net = NetManage()
    net.get_network_adapters()

    adapter_names = [adapter["Name"] for adapter in net.adapters]
    window.adapter_combobox.addItems(adapter_names)
    window.adapter_combobox.currentTextChanged.connect(
        lambda: window.update_ip_ui(net.get_adapter_info(window.adapter_combobox.currentText())))
    adapter = adapter_names[0]

    window.update_ip_ui(net.get_adapter_info(adapter))

    # IP列表
    iplist = IPList()
    window.ip_list.addItems(iplist.ip_dict)
    window.ip_list.currentTextChanged.connect(
        lambda: window.update_ip_ui(iplist.view_ip(window.ip_list.currentItem().text())))

    # 查看IP
    window.adapter_button.clicked.connect(
        lambda: window.update_ip_ui(net.get_adapter_info(window.adapter_combobox.currentText())))

    # 更改IP
    window.set_button_ip.clicked.connect(lambda: window.update_status_label(
        net.change_adapter_ip(window.adapter_combobox.currentText(), window.current_ip())))

    # 启动DHCP
    window.set_button_dhcp.clicked.connect(lambda: net.up_dhcp(window.adapter_combobox.currentText()))

    window.show()
    sys.exit(app.exec())
