import json
import subprocess
from json import JSONDecodeError

from PyQt6.QtGui import QStandardItemModel, QStandardItem

from tools import subnet_converter


class NetManage:
    """网络适配器管理类，用于获取和配置网络接口信息
    
    Attributes:
        adapters (list): 存储网卡适配器信息的列表
    """

    def __init__(self):
        """初始化网络管理实例
        """
        self.adapters: list = []  # 网卡适配器信息列表

    def get_network_adapters(self):
        """获取活动状态的网络适配器列表
        
        使用PowerShell命令获取状态为"up"的网络适配器信息，
        并将结果以JSON格式解析存储到adapters属性中
        
        Raises:
            subprocess.CalledProcessError: 当PowerShell命令执行失败时引发
        """
        try:
            # 构建PowerShell命令字符串（注意开头的空格避免命令拼接错误）
            command = (" Get-NetAdapter"
                       "| Where-Object { $_.Status -eq 'up' } "  # 过滤状态为up的适配器
                       "| Select-Object Name, InterfaceIndex, InterfaceAlias, InterfaceDescription "
                       "| ConvertTo-Json")

            # 配置隐藏控制台窗口参数
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # 0x00000001

            # 执行PowerShell命令
            output = subprocess.check_output(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                stderr=subprocess.STDOUT,  # 将标准错误重定向到标准输出
                startupinfo=startupinfo,
                encoding='gbk'  # 使用中文系统默认编码
            )

            # 解析JSON输出
            try:
                output = json.loads(output)
            except json.JSONDecodeError as e:
                print(f"JSON解析失败：{e}")
                return

            # 统一数据存储格式（适配单对象和多对象情况）
            self.adapters = [output] if isinstance(output, dict) else output

        except subprocess.CalledProcessError as e:
            # 增强错误处理：将错误信息传递到GUI界面
            error_msg = f"命令执行失败：{e.output.strip()}"
            print(error_msg)
            # if self.window:
            #     self.window.statusBar().showMessage(error_msg, 5000)

    @staticmethod
    def get_adapter_info(Name: str):
        """获取指定网络适配器的配置信息
        
        Args:
            Name (str): 网络接口名称（如"以太网"、"WLAN"等）
            
        Returns:
            tuple: 包含(IP地址, 子网掩码, 默认网关, DNS服务器列表, DHCP状态)的元组
            None: 当获取信息失败时返回
            
        执行流程：
        1. 通过PowerShell获取指定网卡的详细配置
        2. 解析IPv4地址、网关、子网掩码等信息
        3. 更新关联GUI窗口的控件显示
        4. 返回格式化后的网络配置信息
        """
        # 使用三引号
        command = '''
            $name = '%s'
            $config = Get-NetIPAddress -InterfaceAlias $name -AddressFamily IPv4
            $gateway = Get-NetRoute -InterfaceAlias 'WLAN' | Where-Object DestinationPrefix -eq '0.0.0.0/0'
            $dns = Get-DnsClientServerAddress -InterfaceAlias $name -AddressFamily IPv4
            $dhcp = Get-NetIPInterface -InterfaceAlias $name -AddressFamily IPv4 | 
                Select-Object @{Name='DHCP'; Expression={ if ($_.Dhcp -eq 1) { 'Enabled' } else { 'Disabled' } }}

            [PSCustomObject]@{
                InterfaceAlias = $config.InterfaceAlias
                IPv4Address = $config.IPAddress
                IPv4DefaultGateway = $gateway.NextHop
                SubnetMask = $config.PrefixLength
                DNSServer = $dns.ServerAddresses
                DHCPEnabled = $dhcp.Dhcp
            } | ConvertTo-Json
        ''' % Name

        # 设置 startupinfo 隐藏控制台窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 直接捕获输出
        output = subprocess.check_output(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            stderr=subprocess.STDOUT,
            startupinfo=startupinfo,
            encoding='gbk'
        )
        if output:
            try:
                output = json.loads(output)
            except json.JSONDecodeError as e:
                print(f"配置解析失败：{e}")
                return '', '', '', (), ''

            # 使用walrus运算符简化代码
            if (mask := output.get('SubnetMask')) is not None:
                SubnetMask = subnet_converter(cidr=mask)
            else:
                SubnetMask = "255.255.255.255"  # 默认无效掩码

            IPv4Address: str = output.get('IPv4Address', "")
            IPv4DefaultGateway: str = output.get('IPv4DefaultGateway', '')
            DNSServer: tuple[str] = output.get('DNSServer', ())
            DHCPEnabled: str = output.get('DHCPEnabled', '')

            return IPv4Address, SubnetMask, IPv4DefaultGateway, DNSServer, DHCPEnabled
        else:
            return '', '', '', (), ''

    def change_adapter_ip(self, Name: str, var=(str, str, str, (),)) :
        """修改IP"""

        # 清除网卡配置
        print(self.clear_ip_cfg(Name))

        command = f'''
                $interface = Get-NetAdapter -Name "{Name}"
                Remove-NetIPAddress -InterfaceIndex $interface.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
                New-NetIPAddress -InterfaceIndex $interface.ifIndex -IPAddress '{var[0]}' `
                                 -PrefixLength '{subnet_converter(subnet_mask=var[1])}' -DefaultGateway '{var[2]}'
                Set-DnsClientServerAddress -InterfaceIndex $interface.ifIndex -ServerAddresses {var[3]}
                '''

        # 设置 startupinfo 隐藏控制台窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            encoding='gbk',
            startupinfo=startupinfo
        )

        if output.returncode == 0:
            info = '[%s] 修改IP成功！' % Name
            return info
        else:
            info = '[%s] 修改IP失败！' % Name
            return info

    def up_dhcp(self, Name):
        """启动DHCP"""

        # 清除网卡配置
        print(self.clear_ip_cfg(Name))

        command = f'''
                        $name = "%s"
                        # 启用 DHCP 
                        Get-NetAdapter -InterfaceAlias $name | Set-NetIPInterface -Dhcp Enabled
                        ''' % Name

        # 设置 startupinfo 隐藏控制台窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            encoding='gbk',
            startupinfo=startupinfo
        )

        if output.returncode == 0:
            info = '[%s] 启用DHCP成功！' % Name
            return info
        else:
            info = '[%s] 启用DHCP失败！' % Name
            return info

    @staticmethod
    def clear_ip_cfg(Name: str):
        """清除指定网卡信息"""
        command = f'''
                $name = "%s"
                # 禁用DHCP
                Get-NetAdapter -InterfaceAlias $name | Set-NetIPInterface -Dhcp Disabled
                # 清除指定网卡Ip配置
                Remove-NetIPAddress -InterfaceAlias $name -Confirm:$false
                # 清除指定网卡网关配置
                Remove-NetRoute -InterfaceAlias $name -Confirm:$false
                # 清除指定网卡的DNS配置
                Set-DnsClientServerAddress -InterfaceAlias $name -ResetServerAddresses
                ''' % Name

        # 设置 startupinfo 隐藏控制台窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            encoding='gbk',
            startupinfo=startupinfo
        )

        if output.returncode == 0:
            info = '[%s] 清除网卡配置成功！' % Name
            return info
        else:
            info = '[%s] 清除网卡配置失败！' % Name
            return info





class IPList:
    """IP地址"""

    def __init__(self, filename: str = 'record.json'):
        super().__init__()
        self.ip_dict: dict = {}
        self.filename: str = filename
        self.load_ip()

    def add_ip(self, IPv4Address: str, SubnetMask: str, IPv4DefaultGateway: str, DNSServer: tuple):
        """添加IP"""
        temp = {IPv4Address: {"IPv4Address": IPv4Address, 'SubnetMask': SubnetMask,
                              'IPv4DefaultGateway': IPv4DefaultGateway, 'DNSServer': DNSServer}}
        self.ip_dict.update(temp)

    def update_ip(self):
        """更新IP"""

    def view_ip(self, IPv4Address: str):
        """查看IP"""
        if self.ip_dict.get(IPv4Address):
            ip_data = self.ip_dict.get(IPv4Address)

            IPv4Address: str = ip_data.get('IPv4Address', "")
            SubnetMask: str = ip_data.get('SubnetMask', '')
            IPv4DefaultGateway: str = ip_data.get('IPv4DefaultGateway', '')
            DNSServer: tuple[str] = ip_data.get('DNSServer', ())
            DHCPEnabled = ""

            return IPv4Address, SubnetMask, IPv4DefaultGateway, DNSServer, DHCPEnabled
        else:
            print('没有 %s' % IPv4Address)
            return "", "", "", ()

    def del_ip(self, IPv4Address: str):
        """删除IP"""
        if self.ip_dict.get(IPv4Address):
            self.ip_dict.pop(IPv4Address)
            print('已删除 %s' % IPv4Address)
        else:
            print('没有 %s' % IPv4Address)

    def load_ip(self):
        """加载IP"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.ip_dict = json.load(f)
            print('读取 [%s] 文件完成...' % self.filename)

        except FileNotFoundError:
            with open(self.filename, 'w', encoding='utf-8'):
                pass
            print('新建文件 [%s]' % self.filename)

        except JSONDecodeError:
            print('[%s] 文件为空，加载失败' % self.filename)

    def save_ip(self):
        """保存IP"""
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.ip_dict, f)
        print("保存 [%s] 文件完成..." % self.filename)
