


def test_time(func_name: str, number: int = 100):
    """
    测试函数执行时间
    :param func_name: 函数名称
    :param number: 测试次数
    :return:
    """
    import timeit
    print(f'开始测试函数：{func_name}')
    optimized_time = timeit.timeit(
        stmt=f"{func_name}()",
        setup=f"from __main__ import {func_name}",
        number=number
    )
    print(f"{func_name} | 平均耗时: {optimized_time / 100:.4f} 秒/次")
