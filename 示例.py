import time
from machine import SPI
try:
    import lcd
except ImportError:
    from lib import lcd


def get_st(旋转):
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

    # lcd.def_字符.all = "的身份人格完善的法律就能很快就"
    return lcd.LCD(
        spi,
        cs=47,
        dc=21,
        # rst=None,
        rst=14,
        bl=48,
        size=lcd.LCD.Size.st7789,
        旋转=旋转,
        color_bit=16,
        逆CS=False,
        像素缺失=(0, 0, 0, 0),
    )._init(反色=1, 左右镜像=1, rgb=1)  # .load_bmf("/字库.bmf")

    # st.fill(st.color.白)

    # st.load_bmf(
    #     "/字库.bmf",
    #     {
    #         16: "caxzsdgfsdfgDADSZF撒法帝国",
    #         32: "zxcgvsedfg的说法是德国",
    #     },
    # )

# 显示字符
st = get_st(3)
st.txt(
    字符串="阿斯顿asd",
    x=20,
    y=20,
    size=32,
    字体色=st.color.白,
    背景色=st.color.黑,
    缓存=True,
)
time.sleep(4)

# 丢弃像素
# st._test_像素裁剪()
# while True:
#     pass


# 4角度旋转
for i in range(0, 4):
    st = get_st(i)
    st._test()
    time.sleep(3)
    # time.sleep(1000000000)


# 波形
st = get_st(3)
bx = st.new_波形(
    w起点=20,
    h起点=20,
    size_w=200,
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
    size_w=200,
    size_h=100,
    波形像素=[6, 6, 6],
    多少格=998,
    data_min=[0, 0, 0],
    data_max=[33, 66, 99],
    波形色=[st.color.红, st.color.绿, st.color.蓝],
    背景色=st.color.白,
)


bx2 = st.new_波形(
    w起点=20,
    h起点=210,
    size_w=200,
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
    size_w=200,
    size_h=40,
    波形像素=[4, 4, 4],
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
