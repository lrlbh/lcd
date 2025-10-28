from lib import st7796
from lib import udp
import time
from machine import SPI


spi = SPI(
    1,
    baudrate=60_000_000,
    polarity=0,
    phase=0,
    sck=38,
    mosi=17,
    miso=None,
)


st = st7796.ST7796(
    spi,
    cs=16,
    dc=48,
    rst=18,
    bl=11,
    旋转=3,
    color_bit=24,
)

st.def_字符.all += "123sdf电压:-：Ds"
st._init().load_bmf("/no_delete/270度左旋转几个字符.bmf")

t = 16
tt = 0
for size in range(8):
    st.txt(
        "123sdf电压：:1-：Dsi",
        0,
        tt,
        t,
        st.color.基础灰阶.白,
        st.color.基础灰阶.黑,
        True,
    )
    t += 8
    tt += t
    
time.sleep(3)

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

    # if t1 >= 33:
    #     break

while True:
    pass


st.fill(st.color.亮彩.天蓝)
st.def_字符.all += "123sdf电压：:-：Dsii"
# st.load_bmf("/no_delete/字体.bmf")
st.load_bmf("/270度左旋转几个字符.bmf")
# st.txt("电压", 100, 0, 32,
#     st.color.基础灰阶.白,
#     st.color.基础灰阶.黑, True)
st.fill(st.color.亮彩.天蓝)
# udp.send(1)
# st._rotate_char_left_90(("电",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("压",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("电",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("压",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("电",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("压",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))

# st._rotate_char_left_90(("1",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("1",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("1",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))

# st._rotate_char_left_90(("电",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# st._rotate_char_left_90(("电",32,st.color.基础灰阶.白,st.color.基础灰阶.黑))
# udp.send(1)

st.txt(
    "123sdf电压：:1-：Dsi", 0, 0, 32, st.color.基础灰阶.白, st.color.基础灰阶.黑, True
)
st.txt("123sdf电压:-：Ds", 0, 32, 32, st.color.亮彩.红, st.color.亮彩.橙, True)
st.txt("123sdf电压:-：Ds", 0, 64, 32, st.color.基础灰阶.白, st.color.基础灰阶.黑, True)

t = st.color.基础灰阶.黑 * 50
t += st.color.亮彩.金黄 * 1
t += st.color.基础灰阶.黑 * 49


# import random

# def generate_colors():
#     # 定义颜色的 RGB 数值
#     black_rgb = [0, 0, 0]  # 基础灰阶.黑
#     gold_rgb = [255, 223, 0]  # 亮彩.金黄

#     # 初始化数据，99个黑色，1个金黄
#     colors = [black_rgb] * 99

#     # 在随机位置放置金黄
#     gold_position = random.randint(0, 99)
#     colors.insert(gold_position, gold_rgb)  # 使用 insert 方法确保有 100 个元素

#     # 确保最终颜色数为 100
#     if len(colors) > 100:
#         colors = colors[:100]

#     # 将每个颜色转换为 3 个字节的字节对象
#     byte_colors = [bytes(color) for color in colors]

#     # 合并所有字节对象，返回一个包含 300 字节的字节串
#     return b''.join(byte_colors)

# --- 配置 ---
N = 100  # 灯珠数量

# 尝试兼容 MicroPython 的随机
try:
    import random as _rnd
except:
    import urandom as _rnd


# 预计算字节
BLACK_B = b"\x00\x00\x00"  # 黑
GOLD_B = b"\xff\xdf\x00"  # 金黄 (255,223,0)

# --- 状态：随机起点，初始向右 ---
_POS = _rnd.randint(0, N - 1)
_DIR = -1  # 1 向右，-1 向左


def generate_colors():
    """
    返回 300 字节（100 * RGB），只有一个像素为金黄，其余为黑。
    位置以三角波在 [0, N-1] 间来回移动。
    函数内无循环。
    """
    global _POS, _DIR

    # 构造当前帧：黑*_POS + 金 + 黑*(N-_POS-1)
    frame = BLACK_B * _POS + GOLD_B + BLACK_B * (N - _POS - 1)

    # 更新方向与位置（到边界折返，不回环）
    if _POS == 0:
        _DIR = 1
    elif _POS == N - 1:
        _DIR = -1
    _POS += _DIR

    return frame  # bytes，长度应为 3*N = 300


# udp.send(machine.freq(20000000))
data = tt.环形内存(3 * 320 * 100)
data1 = tt.环形内存(3 * 320 * 100)
data2 = tt.环形内存(3 * 320 * 100)
data3 = tt.环形内存(3 * 320 * 100)
data4 = tt.环形内存(3 * 320 * 100)
data5 = tt.环形内存(3 * 320 * 100)
# data6 = tt.环形内存(3 * 320 * 100)
# data7 = tt.环形内存(3 * 320 * 100)
# data8 = tt.环形内存(3 * 320 * 100)
# data9 = tt.环形内存(3 * 320 * 100)
# data10 = tt.环形内存(3 * 320 * 100)
# data11 = tt.环形内存(3 * 320 * 100)
# data12 = tt.环形内存(3 * 320 * 100)
# data13 = tt.环形内存(3 * 320 * 100)

# data1 = tt.环形内存(3 * 320 * 100)
# data11 = tt.环形内存(3 * 320 * 100)
# data21 = tt.环形内存(3 * 320 * 100)
# data31 = tt.环形内存(3 * 320 * 100)
# data41 = tt.环形内存(3 * 320 * 100)
# data51 = tt.环形内存(3 * 320 * 100)
# data61 = tt.环形内存(3 * 320 * 100)
# data71 = tt.环形内存(3 * 320 * 100)
# data81 = tt.环形内存(3 * 320 * 100)
# data91 = tt.环形内存(3 * 320 * 100)
# data110 = tt.环形内存(3 * 320 * 100)
# data111 = tt.环形内存(3 * 320 * 100)
# data112 = tt.环形内存(3 * 320 * 100)
# data113 = tt.环形内存(3 * 320 * 100)

import gc


def mem_info_str():
    # gc.collect()  # 先执行一次垃圾回收，保证数值更准确
    free = gc.mem_free()  # 可用内存（字节）
    alloc = gc.mem_alloc()  # 已分配内存（字节）
    total = free + alloc  # 总内存
    used_mib = alloc / 1048576  # 转 MiB
    total_mib = total / 1048576
    free_mib = free / 1048576
    used_percent = alloc * 100 / total
    return "{:.2f}/{:.2f}MiB 剩余 {:.2f}MiB {:.1f}%".format(
        used_mib, total_mib, free_mib, used_percent
    )


while True:
    for i in range(1):
        zz = generate_colors()
        data.append(zz)
        data1.append(zz)
        data2.append(zz)
        data3.append(zz)
    st._set_window(0, 100, 319, 199)
    t1, t2 = data.get_all_data()
    if len(t1) != 0:
        st._write_data_bytes(t1)
    if len(t2) != 0:
        st._write_data_bytes(t2)

    st._set_window(0, 210, 319, 309)
    t1, t2 = data1.get_all_data()
    if len(t1) != 0:
        st._write_data_bytes(t1)
    if len(t2) != 0:
        st._write_data_bytes(t2)

    st._set_window(0, 320, 319, 419)
    t1, t2 = data1.get_all_data()
    if len(t1) != 0:
        st._write_data_bytes(t1)
    if len(t2) != 0:
        st._write_data_bytes(t2)
    udp.send(mem_info_str())
    # st._set_window(0,200,319,299)
    # t1,t2 = data1.get_all_data()
    # if len(t1) != 0:
    #     st._write_data_bytes(t1)
    # if len(t2) != 0:
    #     st._write_data_bytes(t2)

    # st._set_window(0,480-19,0,480)
    # st._write_data_bytes(st.color.亮彩.洋红 * 200)
    # time.sleep(1)
    # st._set_window(0,0,9,19)
    # st._write_data_bytes(st.color.亮彩.洋红 * 200)

    # time.sleep(1)
    # st.txt("压电", 0, 0,  32,
    # st.color.基础灰阶.白,
    # st.color.基础灰阶.黑, True)
    # time.sleep(3)
