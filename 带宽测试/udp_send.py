
import socket
import time

buf = b"a" * 1472

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("192.168.1.2", 8848)  # 改成ESP32的IP
print("目标:", addr)

count = 0
t0 = time.time()

while True:
    # print("发送中")
    s.sendto(buf, addr)
    # time.sleep(0.0001)



# Wi-Fi已连接: 192.168.1.2
# UDP监听中...
# 2.8595062MiB/s 