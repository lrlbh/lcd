from lib import st7796,st7789
from lib import udp
import time
from machine import SPI,Pin


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
    旋转=3,
    color_bit=24,
)._init().load_bmf("/no_delete/270度左旋转几个字符.bmf")


                      
# 字体测试
t = 16
tt = 0
for size in range(8):
    udp.send(3)
    st.txt( 
        "123sdf电压：:1-：Dsi", 
        0,
        tt,
        t,
        st.color.白,
        st.color.黑,
        True,
    )
    t += 8
    tt += t
      
time.sleep(3) 
  
 
# 波形测试
st.fill(st.color.基础灰阶.黑)
bx = st.new_波形(
    w起点=20,
    h起点=20,
    size_w=300, 
    size_h=100,
    波形像素=1,
    多少格=998,
    max=[33, 66, 99],
    波形色=[st.color.亮彩.海蓝, st.color.亮彩.橙, st.color.亮彩.红],
    背景色=st.color.基础灰阶.白,
)
 
 
bx1 = st.new_波形(
    w起点=20,
    h起点=140,
    size_w=300,
    size_h=100,
    波形像素=2,
    多少格=998,
    max=[33, 66, 99],
    波形色=[st.color.亮彩.海蓝, st.color.亮彩.橙, st.color.亮彩.红],
    背景色=st.color.基础灰阶.白,
)


bx3 = st.new_波形(
    w起点=20,
    h起点=260,
    size_w=300,
    size_h=100,
    波形像素=24,
    多少格=998,
    max=[33, 66, 99],
    波形色=[st.color.亮彩.红, st.color.语义.成功绿, st.color.语义.警告黄],
    背景色=st.color.基础灰阶.白,
)

bx2 = st.new_波形(
    w起点=20,
    h起点=380,
    size_w=300,
    size_h=100,
    波形像素=6,
    多少格=998,
    max=[33, 66, 99],
    波形色=[st.color.亮彩.海蓝, st.color.亮彩.橙, st.color.亮彩.红],
    背景色=st.color.基础灰阶.白,
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




