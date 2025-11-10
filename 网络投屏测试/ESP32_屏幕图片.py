import socket
from machine import SPI, Pin
from lib import st7789, udp, st7796
import struct
import time

bit = 16
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
    旋转=0,
    color_bit=bit,
    w=320,
    h=480
)._init()#.load_bmf("/no_delete/270度左旋转几个字符.bmf")


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
#     rst=18,
#     bl=9,
#     旋转=2,
#     color_bit=bit,
#     # w=w,  # 此乃屏幕原始比例参数
#     # h=h, 
# )._init()


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
            协议 = s.recv(16)
            if not 协议:
                continue
            x, y, wl, hl = struct.unpack(">4I", 协议)
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
            st._spi.write(b"\x2A")
            st._dc.value(1)

            w_buf[0] = (y0 >> 8) & 0xFF
            w_buf[1] = y0 & 0xFF
            w_buf[2] = (y1 >> 8) & 0xFF
            w_buf[3] = y1 & 0xFF
            st._spi.write(w_buf)

            st._dc.value(0)
            st._spi.write(b"\x2B")
            st._dc.value(1)

            w_buf[0] = (x >> 8) & 0xFF
            w_buf[1] = x & 0xFF
            w_buf[2] = ((x + wl - 1) >> 8) & 0xFF 
            w_buf[3] = (x + wl - 1) & 0xFF
            st._spi.write(w_buf)

            # === RAMWR (0x2C) ===
            st._dc.value(0)
            st._spi.write(b"\x2C")
            st._dc.value(1)

            # ss = time.ticks_ms()
            st._spi.write(mv[:size])
            # udp.send(time.ticks_ms() - ss)
    except OSError as e:
        udp.send(f"ERRPR: {e}")
        time.sleep(0.5)