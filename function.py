import json
import subprocess
from ipaddress import IPv4Network


class NetManage:
    """网络适配器管理类，用于获取和配置网络接口信息
    
    Attributes:
        adapters (list): 存储网卡适配器信息的列表
        window: 关联的GUI窗口对象
    """
    
    def __init__(self, window=None):
        """初始化网络管理实例
        
        Args:
            window (optional): 关联的GUI窗口对象，默认为None
        """
        self.adapters: list = []  # 网卡适配器信息列表
        self.window = window      # GUI窗口引用

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
            if self.window:
                self.window.statusBar().showMessage(error_msg, 5000)

    def get_optimized(self, Name: str):
        """获取指定网络适配器的优化配置信息
        
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
        # 使用三引号+str.format()提高可读性
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
                return None

            # 使用walrus运算符简化代码
            if (mask := output.get('SubnetMask')) is not None:
                SubnetMask = IPv4Network(f"0.0.0.0/{mask}").netmask.exploded
            else:
                SubnetMask = "255.255.255.255"  # 默认无效掩码

            # 添加类型注解
            IPv4Address: str = output.get('IPv4Address', "")
            IPv4DefaultGateway: str = output.get('IPv4DefaultGateway', '')
            DNSServer: list[str] = output.get('DNSServer', [])
            DHCPEnabled: str = output.get('DHCPEnabled', '')

            self.window.ip_entry.setText(IPv4Address)
            self.window.subnet_entry.setText(SubnetMask)
            self.window.gateway_entry.setText(IPv4DefaultGateway)
            self.window.dns_entry_1.setText(DNSServer[0] if len(DNSServer) > 0 else "")
            self.window.dns_entry_2.setText(DNSServer[1] if len(DNSServer) > 1 else "")
            self.window.dhcp_status_label.setText(DHCPEnabled)

            return IPv4Address, SubnetMask, IPv4DefaultGateway, DNSServer, DHCPEnabled
        else:
            return None
