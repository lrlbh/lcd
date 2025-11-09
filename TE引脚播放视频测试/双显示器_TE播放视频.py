from lib import st7789, udp
from machine import SPI, Pin


# ==== 初始化LCD ====
spi = SPI(1, baudrate=80_000_000, polarity=0, phase=0, sck=38, mosi=39, miso=None,)
st = st7789.ST7789(
    spi,
    cs=48,
    dc=47,
    rst=None,
    bl=9,
    旋转=2,
    color_bit=16,
)._init()

zxc = Pin(21, Pin.IN, Pin.PULL_UP)


# ==== 配置服务器地址 ====
SERVER_IP = "192.168.1.9"  # 改成运行 send_gif_rgb565.py 的电脑IP
SERVER_PORT = 8848

# ==== 分辨率 ====
WIDTH = 240
HEIGHT = 320
FRAME_SIZE = WIDTH * HEIGHT * 2  # RGB565 2字节每像素


st._set_window(0, 0, 319, 239)
st._dc.value(1)
st._cs_open()
黄色 = st.color_fn(255, 0, 0) * (240 * 320)
青色 = st.color_fn(0, 255, 0) * (240 * 320)
while True:
    # TE 引脚测试
    # 当不使用TE时肉眼可见，更新时残影的线会移动。
    # 当不在中间时，很可能有条线
    # st._spi.write(黄色)

    # # # time.sleep_ms(1)

    # st._spi.write(青色)

    # # # time.sleep_ms(1)
    # continue

    # 当使用TE时肉眼可见，更新时残影的线总是居中。
    # 因为居中只有一条线
    while True:
        if zxc.value() == 1:
            # time.sleep_us(42000)  # 微调
            st._spi.write(黄色)
            break

    while True:
        if zxc.value() == 1:
            # time.sleep_us(42000)  # 微调
            st._spi.write(青色)
            break
    continue

    # while True:
    #     # --- 等待 TE 上升沿 ---
    #     while zxc.value() == 0:
    #         pass

    #     # --- 等待 TE 下降沿（表示可以写入） ---
    #     while zxc.value() == 1:
    #         pass

    #     st._spi.write(黄色)  # 写入第一帧（黄色）

    #     # --- 再次等待 TE 上升沿 ---
    #     while zxc.value() == 0:
    #         pass

    #     # --- 再次等待 TE 下降沿 ---
    #     while zxc.value() == 1:
    #         pass

    #     st._spi.write(青色)  # 写入第二帧（青色）

    # st._spi.write(mv)

    for o_m in mv_z:
        st._write_data_bytes(o_m)
        # while  True:
        # if zxc.value() == 1:
        # st._write_data_bytes(o_m)
        # time.sleep_ms(69)
        # break
        # else:
        #     st._write_data_bytes(o_m)

    #     time.sleep_ms(69)
    # time.sleep(1)

udp.send("播放完成")

s.close()
