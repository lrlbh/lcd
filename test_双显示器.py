from lib import st7789
from lib import udp
import time
from machine import SPI, Pin


# st7789.def_字符.all += "123sdf电压:-：Ds"

# SPI
spi = SPI(
    1,
    baudrate=100_000_000,
    polarity=0,
    phase=0,
    sck=38,
    mosi=39,
    miso=None,
)
udp.send(spi)

# 驱动对象1
st = st7789.ST7789(
    spi,
    cs=48,
    dc=47,
    rst=None,
    bl=9,
    旋转=1,
    color_bit=16,
)._init()  # .load_bmf("/no_delete/270度左旋转几个字符.bmf")


bx = st.new_波形(
    w起点=20,
    h起点=20,
    size_w=200, 
    size_h=100,
    多少格=998,
    波形像素=[21,21,8],
    min = [10,30,0],
    max=[33, 66, 99],
    波形色=[st.color.蓝, st.color.橙, st.color.红],
    背景色=st.color.白,
)
 
t1, t2, t3 = 10, 30, 0
tt1, tt2, tt3 = 1, 1, 1
# z = 0 
while True:
    bx.append_data([t1, t2, t3])
    bx.更新()

    if t1 >= 33:
        tt1 = -1
    if t2 >= 66:
        tt2 = -1
    if t3 >= 99:
        tt3 = -1
    if t1 <= 10:
        tt1 = 1
    if t2 <= 30:
        tt2 = 1
    if t3 <= 0:
        tt3 = 1
    t1 += tt1
    t2 += tt2
    t3 += tt3
    
    # z+=1
    # if z >= 200:
    #     break

# # 刷新屏幕速度测试
# udp.send(st._test_spi())

# # 边框测试
# st._test()

# # 字体测试
# st.txt(
#     "阿斯顿asdaaaadddd",
#     x=1,
#     y=0,
#     size=32,
#     字体色=st.color.白,
#     背景色=st.color.黑,
#     缓存=True,
# )

# st.txt(
#     "阿斯顿asdaaaadddd",
#     x=0,
#     y=32,
#     size=32,
#     字体色=st.color.白,
#     背景色=st.color.黑,
#     缓存=True,
# )

# st.txt(
#     "阿斯顿asdaaaadddd",
#     x=1,
#     y=320-32,
#     size=32,
#     字体色=st.color.白,
#     背景色=st.color.黑,
#     缓存=True,
# )


# # 驱动对象2
# TE = 21
# st1 = st7789.ST7789(
#     spi,
#     cs=48,
#     dc=47,
#     rst=None,
#     bl=9,
#     旋转=0,
#     color_bit=24,
#     逆CS=True,
# )._init()  # .load_bmf("/no_delete/270度左旋转几个字符.bmf")

# # 刷新屏幕速度测试
# udp.send(st1._test_spi())

# # 边框测试
# st1._test()
 
# # 字体测试
# st1.txt(
#     "阿斯顿asd",
#     x=10,
#     y=10,
#     size=32,
#     字体色=st1.color.白,
#     背景色=st1.color.黑,
#     缓存=True,
# )
 