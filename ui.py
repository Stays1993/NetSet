from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        # self.setGeometry(200, 200, 700, 500)
        self.setWindowTitle("IP地址切换工具")
        self.setWindowIcon(QIcon("images/python.png"))

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
        self.ip_list: QListWidget = QListWidget()

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
        right_vbox.addWidget(self.ip_list)

        # 页面布局
        hbox: QHBoxLayout = QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(right_vbox)
        self.setLayout(hbox)


def main_ui():
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_ui()
