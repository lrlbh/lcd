import time
import asyncio
from machine import Pin, SPI
# import gc
import struct

# def timeit(func):
#     def wrapper(*args, **kwargs):
#         s = time.ticks_us()
#         result = func(*args, **kwargs)
#         e = time.ticks_us()
#         print("耗时(ms):", time.ticks_diff(e, s) / 1000)
#         return result

#     return wrapper


class ST7796:
    def __init__(self, spi, cs, dc, rst, bl, 旋转=0, color_bit=16):
        self._spi = spi
        self._cs = Pin(cs, Pin.OUT)
        self._dc = Pin(dc, Pin.OUT)
        self._rst = Pin(rst, Pin.OUT)
        self._bl = Pin(bl, Pin.OUT, value=1)
        if 旋转 == 0 or 旋转 == 2:
            self._width = 320
            self._height = 480
        else:
            self._width = 480
            self._height = 320
        self.__color_bit = color_bit
        self._旋转 = 旋转

        if self.__color_bit == 16:
            self.color_fn = self._color565
        elif self.__color_bit == 18:
            self.color_fn = self._color666
        elif self.__color_bit == 24:
            self.color_fn = self._color888
        else:
            raise ValueError("色彩位数有误")
        self._init_color()

        # 字库：char[size][字] = 点位图
        self._char = {}

        # char_缓存[(背景色,字体色,字,字号)] = bytes
        self._char_缓存 = {}

        # 加速set_window
        self._window缓存 = bytearray(4)

        # 加速显示字符
        self._char_buf = bytearray(72 * 72 * len(self.color_fn(0, 0, 0)))

    def _init(self):
        # 复位
        self._rst.value(0)
        time.sleep_ms(50)
        self._rst.value(1)
        time.sleep_ms(120)

        # Sleep Out
        self._write_cmd(0x11)
        time.sleep_ms(120)

        # 一些常见初始化（不同面板可按需调整）
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        # 数据格式
        val = 0x48  # 默认 0 度
        if self._旋转 == 0:
            val = 0x48  # 竖屏
        elif self._旋转 == 1:
            val = 0x28  # 横屏（右转90）
        elif self._旋转 == 2:
            val = 0x88  # 竖屏翻转（180）
        elif self._旋转 == 3:
            val = 0xE8  # 横屏（左转90）
        self._write_cmd(0x36)
        self._write_data(val)

        # 像素格式
        self._write_cmd(0x3A)
        time.sleep_ms(40)
        self._write_data(
            0x55 if self.__color_bit == 16
            else (0x66 if self.__color_bit == 18 else 0x77)
        )

        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)

        # 显示开
        self._write_cmd(0x29)
        time.sleep_ms(60)

        self._write_cmd(0x21)  # Display Inversion On
        time.sleep_ms(60)
        self.fill(self.color.基础灰阶.黑)
        
        return self

    async def init_async(self):
        # 复位
        self._rst.value(0)
        await asyncio.sleep_ms(50)
        self._rst.value(1)
        await asyncio.sleep_ms(120)

        # Sleep Out
        self._write_cmd(0x11)
        await asyncio.sleep_ms(120)

        # 一些常见初始化（不同面板可按需调整）
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        # 数据格式
        #  第2位 RGB=1 左右交换
        #  第5位 RGB=1 BRG=0
        val = 0x48  # 默认 0 度
        if self._旋转 == 0:
            val = 0x48  # 竖屏
        elif self._旋转 == 1:
            val = 0x28  # 横屏（右转90）
        elif self._旋转 == 2:
            val = 0x88  # 竖屏翻转（180）
        elif self._旋转 == 3:
            val = 0xE8  # 横屏（左转90）
        self._write_cmd(0x36)
        self._write_data(val)

        # 像素格式
        self._write_cmd(0x3A)
        await asyncio.sleep_ms(40)
        self._write_data(
            0x55
            if self.__color_bit == 16
            else (0x66 if self.__color_bit == 18 else 0x77)
        )

        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)

        # # VCOM 电压设置
        # # 设置 VCOM 电压幅值，影响对比度和闪烁
        # # 数值过高会出现拖影/闪烁，过低会对比度不足
        # self.write_cmd(0xC5)  # VCOM Control
        # self.write_data(0x1A)  # VCOM voltage

        # # Gamma 电压曲线（正向）
        # self.write_cmd(0xE0)
        # self.write_data_bytes( bytearray([
        #     0xF0, 0x09, 0x0B, 0x06, 0x04, 0x15, 0x2F,
        #     0x54, 0x42, 0x3C, 0x17, 0x14, 0x18, 0x1B
        # ]))

        # #  Gamma 电压曲线（反向）
        # self.write_cmd(0xE1)  # Negative Voltage Gamma Control
        # self.write_data_bytes(bytearray([
        #     0xE0, 0x09, 0x0B, 0x06, 0x04, 0x03, 0x2B,
        #     0x43, 0x42, 0x3B, 0x16, 0x14, 0x17, 0x1B
        # ]))

        # 显示开
        self._write_cmd(0x29)
        await asyncio.sleep_ms(60)

        self._write_cmd(0x21)  # Display Inversion On

        await asyncio.sleep_ms(60)
        self.fill(self.color.基础灰阶.黑)
        return self

    # 简单图片显示，评估一下屏幕素质和全视角，前面的图片处理被不小心删了
    def show_bmp(self, path, x=0, y=0, max_w=None, max_h=None):
        
        with open(path, "rb") as f:
            # 读取 BMP 头
            if f.read(2) != b"BM":
                raise ValueError("不是 BMP 文件")

            f.seek(10)
            pixel_offset = struct.unpack("<I", f.read(4))[0]  # 图像数据偏移

            f.seek(18)
            width = struct.unpack("<I", f.read(4))[0]
            height = struct.unpack("<I", f.read(4))[0]

            f.seek(28)
            bpp = struct.unpack("<H", f.read(2))[0]
            if bpp != 24:
                raise ValueError("仅支持 24bit BMP")

            # 限制显示范围
            if max_w:
                width = min(width, max_w)
            if max_h:
                height = min(height, max_h)

            # 移动到像素区
            f.seek(pixel_offset)

            # BMP 按行从下到上，需要翻转
            self._set_window(x, y, x + width - 1, y + height - 1)
            self._dc.value(1)
            self._cs.value(0)

            line_bytes = ((width * 3 + 3) // 4) * 4  # 每行 4 字节对齐
            buf = bytearray(width * 3)
            for row in range(height - 1, -1, -1):
                f.seek(pixel_offset + row * line_bytes)
                f.readinto(buf)
                # BGR -> RGB
                for i in range(0, width * 3, 3):
                    b, g, r = buf[i], buf[i + 1], buf[i + 2]
                    if self.__color_bit == 16:
                        color = self._color565(r, g, b)
                    elif self.__color_bit == 18:
                        color = self._color666(r, g, b)
                    else:
                        color = self._color888(r, g, b)
                    self._spi.write(color)

            self._cs.value(1)

    # ------- 基本IO -------
    def _write_cmd(self, cmd):
        self._dc.value(0)
        self._cs.value(0)
        self._spi.write(bytearray([cmd]))
        self._cs.value(1)

    def _write_data(self, data):
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(bytearray([data]))
        self._cs.value(1)

    def _write_data_bytes(self, buf):
        self._dc.value(1)
        self._cs.value(0)

        self._spi.write(buf)
        self._cs.value(1)


    # 行刷新下，最严重的瓶颈，刷新一次屏幕动辄需要调用上千次
    # 此瓶颈可以转移到处理数据，PSRAM+数据处理，不过瓶颈更严重
    # 牺牲了可读,复用,代码量
    # 速度提升 1.5ms --> 0.4ms
    # 如果后续放弃多次频繁调用，这点提升屁用没有，改回来
    def _set_window(self, x0, y0, x1, y1):
        # s = time.ticks_us()
        self._cs.value(0)

        # CASET (0x2A)
        self._dc.value(0)
        self._spi.write(b"\x2a")
        self._dc.value(1)

        buf = self._window缓存  # 预分配好的 4 字节缓存
        buf[0] = (x0 >> 8) & 0xFF
        buf[1] = x0 & 0xFF
        buf[2] = (x1 >> 8) & 0xFF
        buf[3] = x1 & 0xFF
        self._spi.write(buf)

        # RASET (0x2B)
        self._dc.value(0)
        self._spi.write(b"\x2b")
        self._dc.value(1)
        buf[0] = (y0 >> 8) & 0xFF
        buf[1] = y0 & 0xFF
        buf[2] = (y1 >> 8) & 0xFF
        buf[3] = y1 & 0xFF
        self._spi.write(buf)
        # RAMWR (0x2C)
        self._dc.value(0)
        self._spi.write(b"\x2c")
        self._cs.value(1)
 
    # ------- 颜色 -------
    class color:
        # 基础明暗层次    背景、文字、边框
        class 基础灰阶:
            白 = None
            黑 = None
            雾灰 = None
            浅灰 = None
            中灰 = None
            深灰 = None
            石墨 = None

        # 功能状态反馈    按钮、状态灯、提示
        class 语义:
            主题蓝 = None
            成功绿 = None
            警告黄 = None
            危险红 = None
            信息青 = None
            链接蓝 = None

        # 高亮、视觉提示  图表、警示、临时高亮
        class 亮彩:
            红 = None
            橙 = None
            琥珀 = None
            金黄 = None
            柠黄 = None
            草绿 = None
            薄荷 = None
            青色 = None
            天青 = None
            天蓝 = None
            海蓝 = None
            紫 = None
            洋红 = None
            粉 = None

        # 背景与低对比主题    主界面、面板
        class 柔和:
            雾霾蓝 = None
            奶油白 = None
            豆沙绿 = None
            藕粉 = None
            葡萄紫 = None

        # 自然质感与工业风    专用主题、硬件UI
        class 大地:
            棕 = None
            巧克力 = None
            卡其 = None
            橄榄 = None

    def _init_color(self):
        # —— 基础与灰阶 ——
        self.color.基础灰阶.白 = self.color_fn(255, 255, 255)
        self.color.基础灰阶.黑 = self.color_fn(0, 0, 0)
        self.color.基础灰阶.雾灰 = self.color_fn(224, 224, 224)
        self.color.基础灰阶.浅灰 = self.color_fn(192, 192, 192)
        self.color.基础灰阶.中灰 = self.color_fn(128, 128, 128)
        self.color.基础灰阶.深灰 = self.color_fn(64, 64, 64)
        self.color.基础灰阶.石墨 = self.color_fn(32, 40, 48)

        # —— 语义 / UI 常用 ——
        self.color.语义.主题蓝 = self.color_fn(32, 120, 232)
        self.color.语义.成功绿 = self.color_fn(48, 168, 88)
        self.color.语义.警告黄 = self.color_fn(248, 200, 64)
        self.color.语义.危险红 = self.color_fn(232, 56, 64)
        self.color.语义.信息青 = self.color_fn(0, 168, 200)
        self.color.语义.链接蓝 = self.color_fn(40, 120, 232)

        # —— 亮彩（高清晰提示用） ——
        self.color.亮彩.红 = self.color_fn(232, 56, 56)
        self.color.亮彩.橙 = self.color_fn(248, 144, 48)
        self.color.亮彩.琥珀 = self.color_fn(240, 176, 48)
        self.color.亮彩.金黄 = self.color_fn(248, 208, 64)
        self.color.亮彩.柠黄 = self.color_fn(232, 232, 80)
        self.color.亮彩.草绿 = self.color_fn(88, 200, 88)
        self.color.亮彩.薄荷 = self.color_fn(144, 232, 200)
        self.color.亮彩.青色 = self.color_fn(0, 168, 168)
        self.color.亮彩.天青 = self.color_fn(64, 184, 232)
        self.color.亮彩.天蓝 = self.color_fn(72, 136, 248)
        self.color.亮彩.海蓝 = self.color_fn(16, 96, 200)
        self.color.亮彩.紫 = self.color_fn(152, 88, 208)
        self.color.亮彩.洋红 = self.color_fn(232, 64, 160)
        self.color.亮彩.粉 = self.color_fn(248, 176, 192)

        # —— 柔和 / 莫兰迪风 ——
        self.color.柔和.雾霾蓝 = self.color_fn(160, 176, 192)
        self.color.柔和.奶油白 = self.color_fn(248, 240, 224)
        self.color.柔和.豆沙绿 = self.color_fn(168, 184, 136)
        self.color.柔和.藕粉 = self.color_fn(232, 184, 192)
        self.color.柔和.葡萄紫 = self.color_fn(120, 72, 160)

        # —— 大地色 ——
        self.color.大地.棕 = self.color_fn(136, 88, 56)
        self.color.大地.巧克力 = self.color_fn(120, 72, 48)
        self.color.大地.卡其 = self.color_fn(200, 176, 120)
        self.color.大地.橄榄 = self.color_fn(128, 136, 56)

    def _color565(self, r, g=0, b=0):
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        return bytes([value >> 8, value & 0xFF])

    def _color666(self, r, g=0, b=0):
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return bytes([r & 0xFC, g & 0xFC, b & 0xFC])

    def _color888(self, r, g=0, b=0):
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return bytes([r, g, b])

    # ------- 显示 -------
    def fill(self, color):
        self._set_window(0, 0, self._width - 1, self._height - 1)
        # 一次性铺满
        self._write_data_bytes(color * (self._width * self._height))

    # @timeit
    def txt(self, 字符串, x, y, size, 字体色, 背景色, 缓存):
        
        for 字 in 字符串:
            # 字符不存在
            if 字 not in self._char.get(size, {}):
                字 = " "
                
            key = (字, size, 字体色, 背景色)  # 缓存key
            self._char_buf[:] = b""  # 清理buf
            if ord(字) < 128:  # 小写半半宽
                w = size // 2
            else:
                w = size

            self._set_window(x, y, x + w - 1, y + size - 1)
            x += w  # 下一次横轴偏移

            # 有缓存
            if key in self._char_缓存:
                self._write_data_bytes(self._char_缓存[key])
                continue

            # 无缓存
            for byte in self._char[size][字]:
                for bit in range(8):
                    if byte & (1 << (7 - bit)):
                        self._char_buf.extend(字体色)
                    else:
                        self._char_buf.extend(背景色)
            if 缓存:
                self._char_缓存[key] = bytes(self._char_buf[0 : w * size * len(字体色)])
            self._write_data_bytes(self._char_缓存[key])

            if x >= self._width-1:
                return

    def 波形():
        pass

    # ------- 字体 -------
    class def_字符:
        ascii = """ 1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ~·！@#￥%……&*（）——++-=、|【{}】；：‘“，《。》/？*~!@#$%^&*()-_=+[{}]\|;:'",<.>/?/*"""
        常用字符 = "温度电压流功率"
        all = ascii + 常用字符

    def _load_bmf(self, path, 需要的字符):
        self._char = {}
        # size = os.stat(path)[6]

        # f.readinto(buf)  # **不改读取方式**
        with open(path, "rb") as f:
            buf = f.read(12)

            if buf[0:4] != b"BMF3":
                raise "格式有误"
            # buf[4:6] # 版本 没用
            字号数量 = buf[6] | (buf[7] << 8)  # 存储了多少种字号
            数据区起始 = buf[8] | (buf[9] << 8) | (buf[10] << 16) | (buf[11] << 24)
            # f.seek(数据区起始)
            for _ in range(字号数量):
                f.seek(数据区起始)
                buf = f.read(8)
                当前字号 = buf[0] | (buf[1] << 8)
                字符数量 = buf[2] | (buf[3] << 8)
                下一个字号起始 = (
                    buf[4] | (buf[5] << 8) | (buf[6] << 16) | (buf[7] << 24)
                )
                当前字号数据大小 = 下一个字号起始 - 数据区起始 - 8
                数据区起始 = 下一个字号起始
                if [] != 需要的字符 and 当前字号 not in 需要的字符:
                    # print("字号",当前字号)
                    continue
                self._char[当前字号] = {}
                buf = bytearray(当前字号数据大小)
                f.readinto(buf)
                点阵长度 = 当前字号 * 当前字号 // 8
                点阵长度_ascii = 当前字号 * 当前字号 // 16
                idx = 0
                # print("字号",当前字号)
                for _ in range(字符数量):
                    ch = chr(int.from_bytes(buf[idx : idx + 4], "little"))
                    idx += 4
                    if ord(ch) < 128:
                        self._char[当前字号][ch] = buf[idx : idx + 点阵长度_ascii]
                        idx += 点阵长度_ascii
                    else:
                        self._char[当前字号][ch] = buf[idx : idx + 点阵长度]
                        idx += 点阵长度

    def _load_bmf_select(self, path, 需要的字符):
        # —— 读取固定上限（保留原 buf）——
        size = 4096 * 50
        buf = bytearray(size)
        with open(path, "rb") as f:
            n = f.readinto(buf)

            # —— 头校验（零拷贝）——
            if n < 12 or buf[0:4] != b"BMF3":
                raise ValueError("格式有误")
            字号数量 = buf[6] | (buf[7] << 8)

            # 不再切片，只用指针
            p = 12

            # 记录每个字号的“编码表区(start,end)”和“偏移表区(start,end)”
            idx_range = {}  # {字号: (start, end)}
            off_range = {}  # {字号: (start, end)}
            for _ in range(字号数量):
                if p + 4 > n:
                    raise ValueError("BMF 截断")
                字号 = buf[p] | (buf[p + 1] << 8)
                字符个数 = buf[p + 2] | (buf[p + 3] << 8)
                p += 4

                idx_bytes = 4 * 字符个数
                off_bytes = 4 * 字符个数
                if p + idx_bytes + off_bytes > n:
                    raise ValueError("BMF 索引越界/截断")

                idx_start = p
                idx_end = p + idx_bytes
                off_start = idx_end
                off_end = off_start + off_bytes
                p = off_end

                idx_range[字号] = (idx_start, idx_end)
                off_range[字号] = (off_start, off_end)

            # —— 遍历“需要的字符”，按需抽取 ——
            self._char = {}
            for 字号, 文本 in 需要的字符.items():
                if 字号 not in idx_range:
                    continue
                idx_start, idx_end = idx_range[字号]
                off_start, off_end = off_range[字号]
                self._char[字号] = {}

                ascii点阵长度 = (字号 * 字号) // 16
                点阵长度 = (字号 * 字号) // 8
                for 字符 in 文本:
                    idx = buf.find(ord(字符).to_bytes(4, "little"), idx_start, idx_end)

                    if idx < 0:
                        continue

                    # 读该 idx 的偏移（小端 4 字节）
                    p_off = off_start - idx_start + idx
                    偏移 = (
                        buf[p_off]
                        | (buf[p_off + 1] << 8)
                        | (buf[p_off + 2] << 16)
                        | (buf[p_off + 3] << 24)
                    )

                    # 跳到字形数据处读取
                    f.seek(偏移)

                    # 按你的规则：ASCII 半宽，其余全宽
                    if ord(字符) < 128:
                        self._char[字号][字符] = f.read(ascii点阵长度)
                    else:
                        self._char[字号][字符] = f.read(点阵长度)

    # 参数格式
    # {16:"sada",32:"asdas"}
    # @timeit
    def load_bmf(self, path, 需要的字符=None):
        
        # 默认加载  def_字符
        if 需要的字符 is None:
            all_text = self.def_字符.all
            需要的字符 = {s: all_text for s in (16, 24, 32, 40, 48, 56, 64, 72)}

        # 加载def字符
        if isinstance(需要的字符, dict):    
            self._load_bmf_select(path, 需要的字符)
        # 加载全部字符，速度快，但是几M的数据内存放不下
        elif 需要的字符 == "all":   
            raise TypeError("操了，快速加载全部字符被删除了，需要重新写一下")
            self._load_bmf(path)
        else:
            raise TypeError('load_bmf 参数有误！ 需要: "all" or {} ')
        
