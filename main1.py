import wmi
from PyQt6.QtWidgets import QApplication

from ui import IPManagerUI


def get_network_adapters():
    c = wmi.WMI()
    # 获取所有网络适配器
    all_network_adapters = c.Win32_NetworkAdapter()
    adapters = []
    for network_adapter in all_network_adapters:
        # 通过 Index 关联获取对应的网络适配器配置
        configs = c.Win32_NetworkAdapterConfiguration(
            Index=network_adapter.Index, IPEnabled=True
        )
        if configs:
            config = configs[0]
            # 通过 PNPDeviceID 判断是否为无线网卡
            pnp_id = network_adapter.PNPDeviceID.lower()
            is_wifi = "netwlan" in pnp_id or "mswifi" in pnp_id
            adapter_info = {
                "config": config,
                "description": f"{network_adapter.Description} ({'Wi-Fi' if is_wifi else '有线'})",
                "is_wifi": is_wifi,
            }
            adapters.append(adapter_info)
    return adapters


def get_current_ip_info(adapter):
    config = adapter["config"]
    if config.IPAddress:
        ip = config.IPAddress[0]
        subnet = config.IPSubnet[0]
        gateway = config.DefaultIPGateway[0] if config.DefaultIPGateway else ""
        dns = config.DNSServerSearchOrder[0] if config.DNSServerSearchOrder else ""
        return ip, subnet, gateway, dns
    return "", "", "", ""


def set_ip_info(adapter, ip, subnet, gateway, dns):
    config = adapter["config"]
    try:
        # 尝试设置静态 IP
        result = config.EnableStatic(IPAddress=[ip], SubnetMask=[subnet])
        if result[0] == 0:
            if gateway:
                config.SetGateways(DefaultIPGateway=[gateway])
            if dns:
                config.SetDNSServerSearchOrder(DNSServerSearchOrder=[dns])
            ui.status_label.setText("IP 设置成功")
        else:
            ui.status_label.setText("IP 设置失败")
    except Exception as e:
        ui.status_label.setText(f"发生错误: {str(e)}")


def on_adapter_select(index):
    global adapter
    adapter = adapters[index]
    ip, subnet, gateway, dns = get_current_ip_info(adapter)
    ui.ip_entry.setText(ip)
    ui.subnet_entry.setText(subnet)
    ui.gateway_entry.setText(gateway)
    ui.dns_entry.setText(dns)


if __name__ == "__main__":
    app = QApplication([])
    ui = IPManagerUI()

    adapters = get_network_adapters()
    if not adapters:
        ui.status_label.setText("未找到可用的网络适配器")
    else:
        adapter_names = [adapter["description"] for adapter in adapters]
        adapter = adapters[0]
        ui.adapter_combobox.addItems(adapter_names)
        ui.adapter_combobox.currentIndexChanged.connect(on_adapter_select)

        ip, subnet, gateway, dns = get_current_ip_info(adapter)
        ui.ip_entry.setText(ip)
        ui.subnet_entry.setText(subnet)
        ui.gateway_entry.setText(gateway)
        ui.dns_entry.setText(dns)

        ui.set_button.clicked.connect(
            lambda: set_ip_info(
                adapter,
                ui.ip_entry.text(),
                ui.subnet_entry.text(),
                ui.gateway_entry.text(),
                ui.dns_entry.text(),
            )
        )

    ui.show()
    app.exec()
