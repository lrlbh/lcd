import socket


def __send():
    # 读取 IP 地址
    def read_ip(file_path="/no_delete/ip.txt"):
        with open(file_path, "r") as f:
            ip = f.read().strip()
            return ip

    # 初始化 UDP 套接字
    ip = read_ip()

    UDP_PORT = 9002
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 自增计数器
    _counter = 0

    # 发送函数
    def _send(msg: str):
        nonlocal _counter
        try:
            """发送消息，自动拼接自增编号"""
            _counter += 1
            full_msg = "{} {}".format(_counter, msg)
            sock.sendto(full_msg.encode(), (ip, UDP_PORT))
        except Exception:
            pass

    return _send


send = __send()


# print("初始化")
