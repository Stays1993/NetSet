from ipaddress import IPv4Network, NetmaskValueError
from typing import Union


def test_time(func_name: str, number: int = 100):
    """
    测试函数执行时间
    :param func_name: 函数名称
    :param number: 测试次数
    :return:
    """
    import timeit
    print(f'开始测试函数：{func_name}')
    optimized_time = timeit.timeit(stmt=f"{func_name}()", setup=f"from __main__ import {func_name}", number=number)
    print(f"{func_name} | 平均耗时: {optimized_time / 100:.4f} 秒/次")


def subnet_converter(subnet_mask: str = None, cidr: Union[int, str] = None) -> Union[int, str]:
    """
    实现子网掩码与CIDR前缀长度的双向转换

    参数:
        subnet_mask: 子网掩码字符串（如"255.255.255.0"）
        cidr: CIDR前缀长度（如24或"/24"）

    返回:
        CIDR前缀长度（int）或子网掩码字符串（str）

    异常:
        ValueError: 输入格式错误或参数冲突时抛出
    """
    # 参数冲突检查
    if (subnet_mask and cidr) or (not subnet_mask and not cidr):
        raise ValueError("必须且只能指定一个参数：subnet_mask 或 cidr")

    try:
        # 子网掩码 → CIDR
        if subnet_mask:
            network = IPv4Network(f"0.0.0.0/{subnet_mask}", strict=False)
            return int(network.prefixlen)

        # CIDR → 子网掩码
        else:
            # 处理字符串格式的CIDR（如"/24"）
            if isinstance(cidr, str):
                cidr = int(cidr.strip('/'))
            if not 0 <= cidr <= 32:
                raise ValueError("CIDR必须在0~32之间")
            network = IPv4Network(f"0.0.0.0/{cidr}", strict=False)
            return str(network.netmask)

    except NetmaskValueError as e:
        raise ValueError(f"无效的子网掩码格式：{e}") from None
