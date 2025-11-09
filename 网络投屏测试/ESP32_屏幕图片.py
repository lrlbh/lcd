import socket
from machine import SPI, Pin
from lib import st7789, udp,st7796
import struct


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

w, h, bit = 480, 320, 24
HOST = "192.168.1.9"
PORT = 8848


# 热压机V6,初始化
spi = SPI(
    1,
    baudrate=100_000_000,
    polarity=0,
    phase=0,
    sck=38,
    mosi=17,
    miso=None,
)   
udp.send(spi)                                                 
st = st7796.ST7796(
    spi,
    cs=16,
    dc=48,
    rst=18,
    bl=11,
    旋转=2,
    color_bit=bit,
)._init().load_bmf("/no_delete/270度左旋转几个字符.bmf")


# # 双7789板子引脚
# spi = SPI(
#     1,
#     baudrate=100_000_000,
#     polarity=0,
#     phase=0,
#     sck=38,
#     mosi=39,
#     miso=None,
# )
# st = st7789.ST7789(
#     spi,
#     cs=48,
#     dc=47,
#     rst=None,
#     bl=9,
#     旋转=2,
#     color_bit=bit,
#     # w=w,  # 此乃屏幕原始比例参数
#     # h=h,
# )._init()

byte = 3
if bit == 16:
    byte = 2
    

buf =  bytearray(w*h*byte)

# ====== 连接 TCP ======
s = socket.socket()
udp.send("正在连接服务器...")
s.connect((HOST, PORT))
udp.send("已连接")
s.sendall(struct.pack(">HHB7x", w, h, bit))
udp.send("已协商格式")

# ====== 接收并显示 ======
st._set_window(0, 0, w - 1, h - 1)
st._dc.value(1)
st._cs_open()
while True:
    s.readinto(buf)
    st._spi.write(buf)
