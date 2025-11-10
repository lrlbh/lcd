import socket, time

HOST = "0.0.0.0"
PORT = 8848
FRAME_SIZE = 320*240*100
buf = b'\x55' * FRAME_SIZE

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
server.settimeout(0.1)  # 10秒无连接自动退出
print(f"[PC] TCP 服务启动，监听 {PORT}...")

while True:
    try:
        conn, addr = server.accept()
    except socket.timeout:
        continue

    print(f"[PC] ✅ 客户端连接: {addr}")
    conn.settimeout(5)  # 客户端5秒无响应则断开
    count = 0
    t0 = time.time()

    try:
        while True:
            conn.sendall(buf)
    except Exception as e:
        print(f"[PC] ⚠️ 未知错误: {e}")


# MPY: soft reboot
# Wi-Fi 已连接: 192.168.1.11
# TCP 已连接
# 1.6155909MiB/s 
