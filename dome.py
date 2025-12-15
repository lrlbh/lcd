import socket
import time
from machine import SPI
from lib import lcd, st7365傻, udp, st7796
from lib import nv3007


def get_st(旋转) -> lcd.LCD:
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

    # return lcd.LCD(
    #     spi,
    #     cs=47,
    #     dc=21,
    #     # rst=None,
    #     rst=14,
    #     bl=48,
    #     # size=(168, 428),
    #     size=(320, 480),
    #     # size=(240, 320),
    #     旋转=旋转,
    #     color_bit=18,
    #     # 像素缺失=(0, 0, 12,14),
    #     像素缺失=(0, 0, 0, 0),
    # )._init(左右镜像=0, rgb=0)

    return st7365傻.ST7365傻(
        spi,
        cs=47,
        dc=21,
        # rst=None,
        rst=14,
        bl=48,
        # size=(168, 428),
        size=(320, 480),
        # size=(240, 320),
        旋转=旋转,
        color_bit=18,
        # 像素缺失=(0, 0, 12,14),
        像素缺失=(0, 0, 0, 0),
    )._init()


# 1白色区域，3红色区域,白色区域在左上
# 十字线蓝色，边框绿色
# st = get_st(0)
# st._test_像素裁剪()
# while True:
#     pass

# 4角度旋转测试
while True:
    for i in range(0, 4):
        st = get_st(i)#反色=True, RGB=True)
        # udp.send(f"-----------------旋转{i}---------------------")
        # udp.send(f"驱动分辨率w-h{st._width_驱动, st._height_驱动}")
        # udp.send(f"逻辑分辨率w-h{st._width, st._height}")
        # udp.send("----------------------------------------------")
        # udp.send("")
        st._test()
        time.sleep(1)
        # time.sleep(1000000000)


# 波形测试
st = get_st(3)
st.fill(st.color.黑)
bx = st.new_波形(
    w起点=20,
    h起点=20,
    size_w=100,
    size_h=50,
    波形像素=[3, 3, 3],
    多少格=998,
    data_min=[0, 0, 0],
    data_max=[33, 66, 99],
    波形色=[st.color.红, st.color.绿, st.color.蓝],
    背景色=st.color.白,
)

bx1 = st.new_波形(
    w起点=20,
    h起点=90,
    size_w=100,
    size_h=100,
    波形像素=[32, 32, 32],
    多少格=998,
    data_min=[0, 0, 0],
    data_max=[33, 66, 99],
    波形色=[st.color.红, st.color.绿, st.color.蓝],
    背景色=st.color.白,
)


bx2 = st.new_波形(
    w起点=20,
    h起点=210,
    size_w=100,
    size_h=50,
    波形像素=[6, 6, 6],
    多少格=998,
    data_min=[0, 0, 0],
    data_max=[33, 66, 99],
    波形色=[st.color.红, st.color.绿, st.color.蓝],
    背景色=st.color.白,
)


bx3 = st.new_波形(
    w起点=20,
    h起点=280,
    size_w=100,
    size_h=40,
    波形像素=[8, 8, 8],
    多少格=998,
    data_min=[0, 0, 0],
    data_max=[33, 66, 99],
    波形色=[st.color.红, st.color.绿, st.color.蓝],
    背景色=st.color.白,
)


t1, t2, t3 = 0, 0, 0
tt1, tt2, tt3 = 1, 1, 1

while True:
    bx.append_data([t1, t2, t3])
    bx.更新()

    bx1.append_data([t1, t2, t3])
    bx1.更新()

    bx2.append_data([t1, t2, t3])
    bx2.更新()

    bx3.append_data([t1, t2, t3])
    bx3.更新()

    # udp.send(t1)
    # udp.send(t2)
    # udp.send(t3)
    if t1 >= 33:
        tt1 = -1
    if t2 >= 66:
        tt2 = -1
    if t3 >= 99:
        tt3 = -1
    if t1 <= 0:
        tt1 = 1
    if t2 <= 0:
        tt2 = 1
    if t3 <= 0:
        tt3 = 1
    t1 += tt1
    t2 += tt2
    t3 += tt3
