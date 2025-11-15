import socket
from machine import SPI, Pin
from lib import lcd, udp, st7796, gc9a01
import struct
import time

bit = 16
HOST = "192.168.1.9"
PORT = 8848


# 老板子引脚
spi = SPI(
    1,
    baudrate=100_000_000,
    polarity=0,
    phase=0,
    sck=12,
    mosi=13,
    miso=None,  # 10
)
# st = lcd.LCD(
st = st7796.ST7796(
    spi,
    cs=47,
    dc=21,
    # rst=None,
    rst = 14,
    bl=48,
    size=lcd.LCD.Size.st7796,
    旋转=0,
    color_bit=16,
    逆CS=False,
    像素缺失=(0,0,0,0),
)._init()#左右镜像= 0,rgb=0) 


h = st._height
w = st._width
byte = 3
if bit == 16:
    byte = 2

buf = bytearray(w * h * byte)
mv = memoryview(buf)

# st._set_window(0, 0, w - 1, h - 1)
# st._dc.value(1)
st._cs_open()
w_buf = bytearray(4)
协议 = bytearray(16)
协议mv = memoryview(协议)
while True:
    try:
        # ====== 连接 TCP ======
        s = socket.socket()
        udp.send("正在连接服务器...")
        s.connect((HOST, PORT))
        udp.send("已连接")
        s.sendall(struct.pack(">HHB7x", w, h, bit))
        udp.send("已协商格式")

        while True:
            # 废弃了整个屏幕更新，需要加入协议引入包，以及设置坐标
            s.readinto(协议mv)
            x, y, wl, hl = struct.unpack(">4I", 协议mv)
            size = wl * hl * byte

            # 读取像素数据
            s.readinto(mv, size)

            st._set_window(x, y, x + wl - 1, y + hl - 1)
            st._write_data_bytes(mv[:size])

        while True:
            # 废弃了整个屏幕更新，需要加入协议引入包，以及设置坐标
            s.readinto(协议mv)
            x, y, wl, hl = struct.unpack(">4I", 协议mv)
            size = wl * hl * byte

            # 读取像素数据
            s.readinto(mv, size)

            # st._set_window(x, y, x + wl-1, y + hl-1)
            # 展开_set_window函数，略微加快速度
            t = y
            y0 = st._height - 1 - (y + hl - 1)
            y1 = st._height - 1 - t

            # === CASET (0x2A) ===
            st._dc.value(0)
            st._spi.write(b"\x2a")
            st._dc.value(1)

            w_buf[0] = (y0 >> 8) & 0xFF
            w_buf[1] = y0 & 0xFF
            w_buf[2] = (y1 >> 8) & 0xFF
            w_buf[3] = y1 & 0xFF
            st._spi.write(w_buf)

            st._dc.value(0)
            st._spi.write(b"\x2b")
            st._dc.value(1)

            w_buf[0] = (x >> 8) & 0xFF
            w_buf[1] = x & 0xFF
            w_buf[2] = ((x + wl - 1) >> 8) & 0xFF
            w_buf[3] = (x + wl - 1) & 0xFF
            st._spi.write(w_buf)

            # === RAMWR (0x2C) ===
            st._dc.value(0)
            st._spi.write(b"\x2c")
            st._dc.value(1)

            # ss = time.ticks_ms()
            st._spi.write(mv[:size])
            # udp.send(time.ticks_ms() - ss)
    except OSError as e:
        udp.send(f"ERRPR: {e}")
        time.sleep(0.5)
