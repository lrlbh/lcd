import network, socket, time

SSID = "CMCC-Ef6Z"
PASSWORD = "ddtzpts9"
HOST = "192.168.1.9"
PORT = 8848

# Wi-Fi 连接
sta = network.WLAN(network.STA_IF)
sta.active(True)
while not sta.isconnected():
    sta.connect(SSID, PASSWORD)
    time.sleep_ms(100)
print("Wi-Fi 已连接:", sta.ifconfig()[0])

# 建立 TCP 连接
s = socket.socket()
s.connect((HOST, PORT))
print("TCP 已连接")


# 测速
bsize =   480*320*4
#bsize =   1024 * 32 
buf = bytearray(bsize)  # 预分配一个缓冲区
buf = memoryview(buf)
total = 0
end = 0
start = time.ticks_ms()




while True:
    total +=s.readinto(buf)
    #total += len(s.recv(12288))
    if total > 5_000_000:
        end = time.ticks_ms() - start
        break

每秒数据 = total / (end/ 1000) 
print(f"{每秒数据/1024/1024}MiB/s ")


s.close()




