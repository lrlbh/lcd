import network, socket, time

SSID = "CMCC-Ef6Z"
PASSWORD = "ddtzpts9"
PORT = 8848

# Wi-Fi连接
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)
while not sta.isconnected():
    time.sleep_ms(100)
print("Wi-Fi已连接:", sta.ifconfig()[0])

# UDP接收
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", PORT))
print("UDP监听中...")


# 测速
bsize =  1472  # 153600
buf = bytearray(bsize)  # 预分配一个缓冲区
buf = memoryview(buf)

单包时间 = []

total = 0
start = time.ticks_ms()

while True:
    #total += len(s.recv(bsize))
    #ss = time.ticks_us()
    total += s.readinto(buf)
    #单包时间.append(time.ticks_us() - ss)
    if total > 10_000_000:
        end = time.ticks_ms() - start
        break


每秒数据 = total / (end/ 1000) 
print(f"{每秒数据/1024/1024}MiB/s ")
#print(min(单包时间))
#print(max(单包时间))

