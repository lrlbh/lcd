import time
import asyncio
from machine import Pin

# import gc
import struct

from lib import udp


class LCD:
    def __init__(self, spi, cs, dc, rst, bl, w, h, 旋转=0, color_bit=16):
        self._spi = spi
        self._cs = Pin(cs, Pin.OUT)
        self._dc = Pin(dc, Pin.OUT)
        self._rst = Pin(rst, Pin.OUT)
        self._bl = Pin(bl, Pin.OUT, value=1)
        self.__color_bit = color_bit
        self._旋转 = 旋转
        if 旋转 == 1 or 旋转 == 3:
            self._width = w
            self._height = h
        else:
            self._width = h
            self._height = w

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

        # 加速显示字符，最大支持字体 72 * 72
        self._char_buf = bytearray(72 * 72 * len(self.color_fn(0, 0, 0)))

    def _init(self):
        raise ValueError("init未实现！")

    async def init_async(self):
        raise ValueError("init未实现！")

    # 简单图片显示，评估一下屏幕素质和全视角，前面的图片处理函数被不小心删了
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
    # 此瓶颈可以转移到处理数据，不过mpy+PSRAM+数据处理，瓶颈更严重
    # 牺牲了可读,复用,代码量
    # 速度提升 1.5ms --> 0.4ms
    # 如果后续放弃多次频繁调用，这点提升屁用没有，改回来
    # 改成逻辑列刷新后这点速度完全没用了，不过改不改的也没意思
    def _set_window(self, x0, y0, x1, y1):
        t = y0
        y0 = self._height - 1 - y1
        y1 = self._height - 1 - t

        self._cs.value(0)

        # CASET (0x2A)
        self._dc.value(0)
        self._spi.write(b"\x2a")
        self._dc.value(1)

        buf = self._window缓存  # 预分配好的 4 字节缓存
        buf[0] = (y0 >> 8) & 0xFF
        buf[1] = y0 & 0xFF
        buf[2] = (y1 >> 8) & 0xFF
        buf[3] = y1 & 0xFF
        self._spi.write(buf)

        # RASET (0x2B)
        self._dc.value(0)
        self._spi.write(b"\x2b")
        self._dc.value(1)
        buf[0] = (x0 >> 8) & 0xFF
        buf[1] = x0 & 0xFF
        buf[2] = (x1 >> 8) & 0xFF
        buf[3] = x1 & 0xFF
        self._spi.write(buf)

        # RAMWR (0x2C)
        self._dc.value(0)
        self._spi.write(b"\x2c")
        self._cs.value(1)

    def new_波形区域(x起点, x终点, y起点, y终点):
        pass

    # data和线条是列表
    def append(data, 线条色, 背景色):
        pass

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

    # 为了方便点出来的情况下兼容2字节或3字节的像素格式
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

    # 字符超出宽度有小bug
    # @timeit
    # 别忘了，列刷新可以加快速度，下次重写一下
    def txt(self, 字符串, x, y, size, 字体色, 背景色, 缓存):
        if y +size > self._height:
            return
        
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

            
            if x + w > self._width:
                return
            
            
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

    # 旋转像素
    def _rotate_char_left_90(self, key):
        src = self._char_缓存[key]

        # 根据 key 里的 size 推宽高（你这里自己写）
        size = key[1]
        w = size
        h = size  # 如果是等宽等高字体你就这样填，如果你有真实宽高，就换成你原来的取值

        pixel_size = len(src) // (w * h)  # 自动判断 2字节 or 3字节

        dst = bytearray(len(src))

        for y in range(h):
            for x in range(w):
                i_src = (y * w + x) * pixel_size
                i_dst = ((w - 1 - x) * h + y) * pixel_size
                dst[i_dst : i_dst + pixel_size] = src[i_src : i_src + pixel_size]

        self._char_缓存[key] = dst

    def new_波形( self,
        w起点: int,
        h起点: int,
        size_w: int,
        size_h: int,
        波形像素: int,
        多少格: int,
        max: list,
        波形色: list,
        背景色: bytes,):
        return 波形(self,w起点,h起点,size_w,size_h,波形像素,多少格,max,波形色,背景色)
        

class 波形:
    # size == 宽 * 高 * 单像素字节
    # 只为存储像素设置，所以不必当心单次append超出环形结构
    def __init__(
        self,
        st: LCD,
        w起点: int,
        h起点: int,
        size_w: int,
        size_h: int,
        波形像素: int,
        多少格: int,
        max: list,
        波形色: list,
        背景色: bytes,
    ):
        self._st = st
        self._size_byte = len(背景色)
        self._size_h = size_h
        self._size_w = size_w
        self._w起点 = w起点
        self._h起点 = h起点
        self._w终点 = w起点 + size_w - 1
        self._h终点 = h起点 + size_h - 1
        self._波形像素 = 波形像素
        self._波形len = 波形像素 * self._size_byte
        self._波形色 = []
        for t in 波形色:
            self._波形色.append(t * 波形像素)
        self._背景色 = 背景色
        self._size = int(size_w * size_h * self._size_byte)
        self._buf = bytearray(self._size)
        self._mv = memoryview(self._buf)
        self._当前下标 = 0  # 最旧字节位置
        self._多少格 = 多少格
        self._max = max
        self._允许的最大下标 = self._size_h - self._波形像素
        
    def 更新(self):
        self._st._set_window(self._w起点, self._h起点, self._w终点, self._h终点)
        if self._当前下标 != self._size:
            self._st._write_data_bytes(self._mv[self._当前下标 : self._size])
        if self._当前下标 > 0:
            self._st._write_data_bytes(self._mv[0 : self._当前下标])
    def append_data(self, data: list) -> None:
        # 生成背景色
        td = bytearray(self._背景色 * self._size_h)

        # 模拟网格，看看效果
        # for i in  range(5):
        #     if self._当前下标 ==  30 * i * 300:
        #         td = bytearray(self._st.color.基础灰阶.黑 * self._size_h)
        # for i in  range(4):
        #     i = i+1
        #     td[i*60:i*60+3] = self._st.color.基础灰阶.黑

        # 遍历多个输入通道
        for i in range(len(data)):
            # 数据映射到下标
            index = data[i] / self._max[i] * self._允许的最大下标
            
            # # 限幅，防止传入数据超过幅值
            # if index > self._允许的最大下标:
            #     index = self._允许的最大下标
            # if index < 0:
            #     index = 0

            # 每个像素多少个字节做一下偏移
            index = int(index)  * self._size_byte

            # 数据更新到背景色中
            td[index : index + self._波形len] = self._波形色[i]
        
        # # 查看有无，不合理数据
        # if len(td) > self._size_h * self._size_byte:
        #     udp.send("ERROR")
        #     return
        
        self._append(td)
        
    # 单次追加数据越多越慢
    # 波形显示一般宽大于高,直接用这个
    def _append(self, data: bytes) -> None:
        if self._当前下标 == self._size:
            self._当前下标 = 0

        for i in range(len(data)):
            self._buf[self._当前下标 + i] = data[i]

        self._当前下标 = self._当前下标 + len(data)
        # udp.send(self.当前下标 )

    # bytearray中 末尾数据越多越慢
    # 万一性能不够，整合两个函数为一个
    def _append_mv(self, data: bytes) -> None:
        if self._当前下标 == self._size:
            self._当前下标 = 0
        下一次下标 = self._当前下标 + len(data)
        self._buf[self._当前下标 : 下一次下标] = data
        self._当前下标 = 下一次下标

    def _get_all_data(self):
        return self._mv[self._当前下标 : self._size], self._mv[0 : self._当前下标]

# def test():
#     from time import ticks_ms, ticks_diff    
#     每列多少像素 =  b'a' * 3 * 200   # 高
#     波形区域多少列 =  50    # 宽
#     测试次数 =    2
    
#     t = 环形内存(波形区域多少列 * len(每列多少像素))
    
#     append耗时 = 0
#     get_all_data耗时 = 0

#     for i in range(测试次数):
#         for i in range(波形区域多少列):
#             t0 = ticks_ms()
#             t.append_mv(每列多少像素)  # 每次追加 940 字节数据
#             append耗时 += ticks_diff(ticks_ms(), t0)
#             t0 = ticks_ms()
#             _ = t.get_all_data()
#             get_all_data耗时 += ticks_diff(ticks_ms(), t0)
#         print(f"append_mv数据量、测试测数、耗时ms:{
#             len(每列多少像素),波形区域多少列,append耗时}")
#         append耗时 = 0

#     for i in range(测试次数):
#         for i in range(波形区域多少列):
#             t0 = ticks_ms()
#             t.append(每列多少像素)  # 每次追加 940 字节数据
#             append耗时 += ticks_diff(ticks_ms(), t0)
#             t0 = ticks_ms()
#             _ = t.get_all_data()
#             get_all_data耗时 += ticks_diff(ticks_ms(), t0)
#         print(f"append数据量、测试测数、耗时ms:{
#             len(每列多少像素),波形区域多少列,append耗时}")
#         append耗时 = 0


# test()
