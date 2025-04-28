


def test_time(func):
    import time

    start = time.perf_counter()
    func()
    end = time.perf_counter()
    print(f"程序运行时间：{end - start}秒")


def print1():
    print(11111 * 11111)

if __name__ == '__main__':
    test_time(print1)
