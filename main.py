from machine import SPI
from lib import st7796


# 初始化屏幕
st = st7796.ST7796(
    SPI(
        1,
        baudrate=40_000_000,
        polarity=0,
        phase=0,
        sck=38,
        mosi=17,
        miso=None,
    ),
    cs=16,
    dc=48,
    rst=18,
    bl=11,
    旋转=2,
    color_bit=24,
)
st._init()

# 加载字符
st.def_字符.all += "123sdf电压:-：Dsii"
st.load_bmf(
    "/0旋转几个字符.bmf",
)

# 显示文本
y = 0
for 字号 in [16, 24, 32, 40, 48, 56, 64, 72]:
    st.txt(
        "123sdf电压:-：Dsii",
        0,
        y,
        字号,
        st.color.亮彩.草绿,
        st.color.柔和.藕粉,
        True,
    )
    y += 字号 + 1

st.show_bmp("/320x480.bmp")