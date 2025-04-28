from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QApplication, QLabel, QComboBox, QLineEdit, QPushButton, QListWidget, QVBoxLayout,
                             QHBoxLayout, QMenu, QListView, QMainWindow, QWidget, QMessageBox)

from function import IPList


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 700, 500)
        self.setWindowTitle("IP地址切换工具")
        self.setWindowIcon(QIcon("images/python.png"))

        self.ipList = IPList()

        self._set_font()
        self._init_ui()
        self._init_layout()

    def _set_font(self):
        """
        设置字体
        :return:
        """
        font: QFont = QFont()
        font.setFamily("等距更纱黑体 SC")
        font.setPointSize(10)

        self.setFont(font)

    def _init_ui(self):
        """
        初始化Ui组件
        :return:
        """
        # 网卡下拉框
        self.adapter_label: QLabel = QLabel("选择网卡:")
        self.adapter_combobox: QComboBox = QComboBox()
        self.adapter_button: QPushButton = QPushButton('查看IP')

        # IP 地址输入框
        self.ip_label: QLabel = QLabel("IP  地址:")
        self.ip_entry: QLineEdit = QLineEdit()

        # 子网掩码输入框
        self.subnet_label: QLabel = QLabel("子网掩码:")
        self.subnet_entry: QLineEdit = QLineEdit()

        # 默认网关输入框
        self.gateway_label: QLabel = QLabel("默认网关:")
        self.gateway_entry: QLineEdit = QLineEdit()

        # DNS 输入框
        self.dns_label_1: QLabel = QLabel("  DNS1  :")
        self.dns_entry_1: QLineEdit = QLineEdit()
        self.dns_label_2: QLabel = QLabel("  DNS2  :")
        self.dns_entry_2: QLineEdit = QLineEdit()

        # DHCP
        self.dhcp_label: QLabel = QLabel("  DHCP  :")
        self.dhcp_status_label: QLineEdit = QLineEdit()
        self.dhcp_status_label.setReadOnly(True)

        # 设置按钮
        self.set_button_ip: QPushButton = QPushButton("设置 IP")
        self.set_button_dhcp: QPushButton = QPushButton("设置 DHCP")

        # 状态标签
        self.status_label: QLabel = QLabel("")

        # IP列表
        self.ip_list_view: MyListWidget = MyListWidget()
        # 右键菜单
        # 设置上下文菜单策略为CustomContextMenu，表示需要自定义右键菜单行为（而非使用默认菜单）
        self.ip_list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 当用户右键点击列表时，会触发customContextMenuRequested信号。此处将该信号连接到自定义的槽函数self.custom_right_menu，用于动态生成并弹出右键菜单
        self.ip_list_view.customContextMenuRequested.connect(self.custom_right_menu)

    def _init_layout(self):
        """
        初始化布局
        :return:
        """

        # 左边布局
        left_vbox: QVBoxLayout = QVBoxLayout()

        # 网卡下拉框布局
        adapter_layout: QHBoxLayout = QHBoxLayout()
        adapter_layout.addWidget(self.adapter_label)
        adapter_layout.addWidget(self.adapter_combobox)
        adapter_layout.addWidget(self.adapter_button)
        left_vbox.addLayout(adapter_layout)

        # IP 地址输入框布局
        ip_layout: QHBoxLayout = QHBoxLayout()
        ip_layout.addWidget(self.ip_label)
        ip_layout.addWidget(self.ip_entry)
        left_vbox.addLayout(ip_layout)

        # 子网掩码输入框
        subnet_layout: QHBoxLayout = QHBoxLayout()
        subnet_layout.addWidget(self.subnet_label)
        subnet_layout.addWidget(self.subnet_entry)
        left_vbox.addLayout(subnet_layout)

        # 默认网关输入框
        gateway_layout: QHBoxLayout = QHBoxLayout()
        gateway_layout.addWidget(self.gateway_label)
        gateway_layout.addWidget(self.gateway_entry)
        left_vbox.addLayout(gateway_layout)

        # DNS 输入框
        dns_layout_1: QHBoxLayout = QHBoxLayout()
        dns_layout_1.addWidget(self.dns_label_1)
        dns_layout_1.addWidget(self.dns_entry_1)
        left_vbox.addLayout(dns_layout_1)

        dns_layout_2: QHBoxLayout = QHBoxLayout()
        dns_layout_2.addWidget(self.dns_label_2)
        dns_layout_2.addWidget(self.dns_entry_2)
        left_vbox.addLayout(dns_layout_2)

        # DHCP 标签
        dhcp_layout: QHBoxLayout = QHBoxLayout()
        dhcp_layout.addWidget(self.dhcp_label)
        dhcp_layout.addWidget(self.dhcp_status_label)
        left_vbox.addLayout(dhcp_layout)

        # 设置按钮
        button_layout: QHBoxLayout = QHBoxLayout()
        button_layout.addWidget(self.set_button_dhcp)
        button_layout.addWidget(self.set_button_ip)
        left_vbox.addLayout(button_layout)

        # 状态标签
        left_vbox.addWidget(self.status_label)

        # 右边布局
        right_vbox: QVBoxLayout = QVBoxLayout()
        right_vbox.addWidget(self.ip_list_view)

        # 页面布局
        hbox: QHBoxLayout = QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(right_vbox)
        self.setLayout(hbox)

    def update_ip_ui(self, var=(str, str, str, (), str)):
        """更新IP信息窗口"""
        self.ip_entry.setText(var[0])
        self.subnet_entry.setText(str(var[1]))
        self.gateway_entry.setText(var[2])
        self.dns_entry_1.setText(var[3][0] if len(var[3]) > 0 else "")
        self.dns_entry_2.setText(var[3][1] if len(var[3]) > 1 else "")
        self.dhcp_status_label.setText(var[4])
        print('更新 [%s] IP信息' % self.adapter_combobox.currentText())

    def current_ip(self):
        """获取IP信息窗口信息"""
        IPv4Address: str = self.ip_entry.text()
        SubnetMask: str = self.subnet_entry.text()
        IPv4DefaultGateway: str = self.gateway_entry.text()
        DNSServer: tuple = (self.dns_entry_1.text(), self.dns_entry_2.text())

        return IPv4Address, SubnetMask, IPv4DefaultGateway, DNSServer

    def update_status_label(self, info: str):
        """更新状态标签"""
        self.status_label.setText(info)

    def custom_right_menu(self, pos):
        """IP列表右键菜单"""
        menu = QMenu()
        opt1 = menu.addAction("新增")
        opt2 = menu.addAction("删除")
        opt3 = menu.addAction("修改")
        opt4 = menu.addAction("排序")
        action = menu.exec(self.ip_list_view.mapToGlobal(pos))

        if action == opt1:
            print("新增")
        elif action == opt2:
            print('删除')
        elif action == opt3:
            print('修改')
        elif action == opt4:
            print('排序')


class MyListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDoubleClickedItem()

    def setDoubleClickedItem(self):
        self.itemDoubleClicked.connect(self.handleDoubleClickedItem)

    def handleDoubleClickedItem(self, item):
        QMessageBox.information(self, "双击事件", f"你双击了项目: {item.text()}")

def main_ui():
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_ui()
