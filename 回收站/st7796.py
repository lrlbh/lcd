
import time
import asyncio
from machine import Pin,SPI
import os
import struct



class ST7796:

    def __init__(self, 
                spi, cs, dc, rst, bl,
                color_bit=16):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.bl = Pin(bl, Pin.OUT, value=1)  # 背光开启
        self.width = 320
        self.height = 480
        self.__color_bit = color_bit 
        
        if self.__color_bit == 16:
            self.color_fn = self.color565
        elif self.__color_bit == 18:
            self.color_fn = self.color666
        elif self.__color_bit == 24:
            self.color_fn = self.color888
        else:
            raise  ValueError("色彩位数有误")
        
        self._char_block_cache = {}
        self.char ={}
        
        self.char_buf(64*64*3)
            
    async def init(self):
        
        
        
        # 显示器
        self.rst.value(0)
        await asyncio.sleep_ms(50)
        self.rst.value(1)
        await asyncio.sleep_ms(120)
        
        # 退出睡眠模式
        self.write_cmd(0x11)  # Sleep Out
        await asyncio.sleep_ms(120)
        
        # 开启扩展指令
        self.write_cmd(0xF0)  # Command Set control
        self.write_data(0xC3)  # Enable extension command 2 partI
        
        # 开启扩展指令
        self.write_cmd(0xF0)  # Command Set control
        self.write_data(0x96)  # Enable extension command 2 partII
        
        # 数据格式
        # 0x48 = 0b01001000
        # bit7 MY=0: 垂直刷新方向为从上到下
        # bit6 MX=1: 水平刷新方向为从右到左
        # bit5 MV=0: 不交换行列（不旋转90°）
        # bit4 ML=0: 垂直刷新顺序为上到下
        # bit3 BGR=0 RGB =1
        # bit2 MH=0: 水平刷新顺序正常
        # 作用：设定像素读取/写入的地址映射方式、颜色顺序和扫描方向
        #  第2位 RGB=1 左右交换
        #  第5位 RGB=1 BRG=0
        self.write_cmd(0x36)  # Memory Data Access Control
        self.write_data(0b01001000)
        
        
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
        
        
        # 色彩位
        # 0x55-16位
        # OX66-18位
        # 0X77-24位 假的
        self.write_cmd(0x3A)  # Interface Pixel Format
        await asyncio.sleep_ms(50)
        if self.__color_bit == 16:
            self.write_data(0x55) 
        elif self.__color_bit == 18:
            self.write_data(0x66)  
        elif self.__color_bit == 24:
            self.write_data(0x77)  
        else:
            raise ValueError("色彩位数有误")
        

        # 显示反相控制
        # 作用：反相驱动可减少残影和闪烁，1-dot 表示奇偶像素点交替反相???
        # self.write_cmd(0xB4)  # Display Inversion Control
        # self.write_data(0x01)  # 1-dot inversion
        
        # 输入模式
         # 作用：设定数据写入方向、扫描模式等。此值通常为出厂推荐值
        # self.write_cmd(0xB7)  # Entry Mode Set
        # self.write_data(0xC6)  # Normal display, Vsync disabled
        
        
        # 显示输出控制（扩展命令）
        # 各字节分别控制扫描门信号波形、驱动时序
        # 作用：这些值是厂家校准的驱动参数，控制行驱动的占空比、偏压、扫描频率等
        # 不同批次屏幕可能不同，通常直接使用厂家给的推荐值
        # self.write_cmd(0xE8)  # Display Output Ctrl Adjust
        # self.write_data(0x40)
        # self.write_data(0x8A)
        # self.write_data(0x00)
        # self.write_data(0x00)
        # self.write_data(0x29)
        # self.write_data(0x19)
        # self.write_data(0xA5)
        # self.write_data(0x33)
        
        # VCOM 电压设置
        # 设置 VCOM 电压幅值，影响对比度和闪烁
        # 数值过高会出现拖影/闪烁，过低会对比度不足
        # self.write_cmd(0xC5)  # VCOM Control
        # self.write_data(0x1A)  # VCOM voltage
        
        # Gamma 电压曲线（正向）
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
        
        # 关闭扩展指令
        self.write_cmd(0xF0)  # Command Set control
        self.write_data(0x3C)  # Disable extension command 2 partI
        
        # 关闭扩展指令
        self.write_cmd(0xF0)  # Command Set control
        self.write_data(0x69)  # Disable extension command 2 partII
        
        # 打开显示
        self.write_cmd(0x29)  # Display On
        await asyncio.sleep_ms(100)
        
        # 颜色反转
        self.write_cmd(0x21)  # Display Inversion On
        
        return self
    
    
        # --- 基本封装 ---
   
    def write_cmd(self,cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self,data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def write_data_bytes(self,buf):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(buf)
        self.cs.value(1)

    # --- 设置显示区域 ---
    def set_window(self,x0, y0, x1, y1):
        self.write_cmd(0x2A) # Column addr set
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)

        self.write_cmd(0x2B) # Row addr set
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)

        self.write_cmd(0x2C) # Memory write

    def color565(self, r, g=0, b=0):
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return bytes([(r & 0xF8) | (g >> 5), ((g & 0x1C) << 3) | (b >> 3)])

    def color666(self, r, g=0, b=0):  # 添加 self 参数
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return bytes([r & 0xFC, g & 0xFC, b & 0xFC])

    def color888(self, r, g=0, b=0):  # 添加 self 参数
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return bytes([r, g, b])

    def fill_screen(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        pixel = self.color_fn(color)
        buf = pixel * (self.width * self.height)
        self.write_data_bytes(buf)

    def draw_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            self.write_data_bytes(self.color_fn(color))

    def show_img(self, path):
        self.write_data_bytes(self.new_img_bmp(path))        

    def show_img_data_path(self, path):
        with open(path, "rb") as file:
            data = file.read()
            self.show_img_data(bytearray(data))

    def show_img_data(self, data):
        self.write_data_bytes( data)

    def write_img_data(self, img_path, data_path):
        # 获取要写入文件的数据
        data = self.new_img_bmp(img_path)

        # 确保目标文件所在的目录存在
        self.ensure_dir_exists(data_path)

        # 打开文件准备写入二进制数据
        with open(data_path, "wb") as f:
            f.write(data)
    
    @staticmethod
    def ensure_dir_exists(path):
        parts = path.split("/")
        for i in range(1, len(parts)):
            current_path = "/".join(parts[:i])
            try:
                os.mkdir(current_path)
            except OSError as e:
                if e.args[0] != 17:  # 目录已存在
                    pass
                
    def new_img_bmp(self, img_path):
        
        with open(img_path, "rb") as f:
            # --- BMP 文件头 ---
            file_header = f.read(14)
            offset_data = struct.unpack_from("<I", file_header, 10)[0]

            # --- BMP 信息头 ---
            info_header = f.read(40)
            width = struct.unpack_from("<I", info_header, 4)[0]
            height = struct.unpack_from("<i", info_header, 8)[0]
            planes = struct.unpack_from("<H", info_header, 12)[0]
            bit_count = struct.unpack_from("<H", info_header, 14)[0]
            compression = struct.unpack_from("<I", info_header, 16)[0]
            if not ((planes == 1) and (bit_count == 24) and (compression == 0)):
                raise ValueError("仅支持无压缩 24 位 BMP")

            # 先申请需要的内存
            if self.__color_bit == 16:
                t = bytearray(height * width * 2)
            elif self.__color_bit in (18, 24):
                t = bytearray(height * width * 3)
            t_mv = memoryview(t)# memoryview 提高写入效率


            # 根据色彩位深选择转换函数
            # BRG -- >  RGB
            # 888 阉割 565,666
            if self.__color_bit == 16:
                # RGB565 转换函数
                def convert_row(row_data, row_buf):
                    for i in range(width):
                        b = row_data[i*3]
                        g = row_data[i*3 + 1]
                        r = row_data[i*3 + 2]
                        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        row_buf[i*2] = (rgb565 >> 8) & 0xFF
                        row_buf[i*2 + 1] = rgb565 & 0xFF
            elif self.__color_bit == 18:
                # 18位色转换函数
                def convert_row(row_data, row_buf):
                    for i in range(width):
                        b = row_data[i*3]
                        g = row_data[i*3 + 1]
                        r = row_data[i*3 + 2]
                        row_buf[i*3] = r & 0xFC
                        row_buf[i*3 + 1] = g & 0xFC
                        row_buf[i*3 + 2] = b & 0xFC
            else:
                # 24位色 BGR -> RGB
                def convert_row(row_data, row_buf):
                    for i in range(width):
                        b = row_data[i*3]
                        g = row_data[i*3 + 1]
                        r = row_data[i*3 + 2]
                        row_buf[i*3] = r
                        row_buf[i*3 + 1] = g
                        row_buf[i*3 + 2] = b


            # 从最后一行开始读取图片
            for row in range(height):
                f.seek(offset_data + (height - 1 - row) * width * 3)
                row_data = f.read(width * 3)
                
                if self.__color_bit == 16:
                    convert_row(row_data, t_mv[row*width*2 : (row+1)*width*2])
                else:
                    convert_row(row_data, t_mv[row*width*3 : (row+1)*width*3])


        return t

    # --- BMF 载入：与之前的 load_char 一致，这里命名为 load_bmf ---
    def load_bmf(self, filename):
        """
        读取由本程序生成的 BMF 文件，并解析到 self.char：
        self.char = { size: { ch: (w, h, data_bytes) } }
        """
        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b"BMF1":
                raise ValueError("Invalid BMF file header")
            num_sizes = struct.unpack('<H', f.read(2))[0]

            self.char = {}
            for _ in range(num_sizes):
                size = struct.unpack('<H', f.read(2))[0]
                num_chars = struct.unpack('<H', f.read(2))[0]
                t = {}
                for _ in range(num_chars):
                    codepoint, w, h = struct.unpack('<HBB', f.read(4))
                    bpr = (w + 7) // 8
                    data = f.read(bpr * h)
                    try:
                        ch = chr(codepoint)
                    except ValueError:
                        ch = f"\\u{codepoint:04x}"
                    t[ch] = (w, h, data)
                self.char[size] = t

    # --- 绘制：把单个字符点阵“贴”到目标缓冲区 ---
    @staticmethod
    def _blit_mono_to_buf(dst_buf, dst_w, dst_h, bytes_per_pixel,
                          x_off, y_off, glyph_w, glyph_h, glyph_data, color_bytes):
        """
        将一个 1bpp 的 glyph（按行、MSB-first 打包）绘制到 RGB/RGB565 目标缓冲区。
        不做裁剪（由上层保证范围合法）。
        """
        if glyph_w == 0 or glyph_h == 0:
            return
        bpr = (glyph_w + 7) // 8  # bytes per row in glyph
        for gy in range(glyph_h):
            row_base = gy * bpr
            dst_row_start = ( (y_off + gy) * dst_w + x_off ) * bytes_per_pixel
            bit_x = 0
            for byte in range(bpr):
                val = glyph_data[row_base + byte]
                # MSB -> LSB
                for b in range(8):
                    if bit_x >= glyph_w:
                        break
                    if (val >> (7 - b)) & 0x01:
                        idx = dst_row_start + bit_x * bytes_per_pixel
                        # 写入前景色字节
                        dst_buf[idx:idx+bytes_per_pixel] = color_bytes
                    bit_x += 1

    @staticmethod
    def _fill_rect(dst_buf, dst_w, dst_h, bytes_per_pixel, x0, y0, x1, y1, color_bytes):
        """
        在目标缓冲区填充一个矩形（闭区间坐标）。
        已假定坐标符合缓冲区范围。
        """
        if x0 > x1 or y0 > y1:
            return
        row_span = (x1 - x0 + 1) * bytes_per_pixel
        one_row = color_bytes * (x1 - x0 + 1)
        for yy in range(y0, y1 + 1):
            start = (yy * dst_w + x0) * bytes_per_pixel
            dst_buf[start:start+row_span] = one_row

    def draw_text_bmf(self, x, y, text, size,
                      color=(0, 0, 0),
                      bg=None,
                      char_bg=(255, 240, 200),
                      spacing=1,
                      align='left'):
        """
        使用已加载的 BMF 字体在屏幕上绘制一行文本。

        参数：
          x, y      : 左上起点（屏幕坐标）
          text      : 要绘制的字符串
          size      : 字号（需与 self.char 中的 key 对应）
          color     : 前景色（文字颜色）
          bg        : 整体背景色；为 None 则不额外涂底，保持默认（黑/白屏）
          char_bg   : 每个字符块的背景色；为 None 则不绘制字符独立背景
          spacing   : 字符间距像素
          align     : 'left'/'center'/'right' 影响起始 x 偏移
        """
        # 1) 准备字库
        size_table = self.char.get(size)
        if not size_table:
            raise ValueError("未找到该字号的 BMF 数据，请先 load_bmf 并确保该 size 存在。")

        # 2) 统计整体尺寸（每个字符用自身裁剪后的宽高，行高取该行最大 h）
        glyphs = []
        max_h = 0
        total_w = 0
        for ch in text:
            g = size_table.get(ch)
            if g is None:
                # 若无该字符，使用宽=0的占位（或者可以给一个固定空白宽度）
                w, h, data = 0, 0, b""
            else:
                w, h, data = g
            glyphs.append((ch, w, h, data))
            max_h = max(max_h, h)
            total_w += w
        if len(text) > 1:
            total_w += spacing * (len(text) - 1)
        if total_w <= 0 or max_h <= 0:
            return  # 没有可绘制的内容

        # 3) 计算对齐偏移
        if align == 'left':
            x0 = x
        elif align == 'center':
            x0 = x - total_w // 2
        elif align == 'right':
            x0 = x - total_w
        else:
            x0 = x

        # 4) 屏幕裁剪（简单版：若完全在屏外就返回）
        if x0 >= self.width or y >= self.height or (x0 + total_w) <= 0 or (y + max_h) <= 0:
            return

        # 裁剪到屏幕可见区域，避免 set_window 溢出
        vis_x0 = max(0, x0)
        vis_y0 = max(0, y)
        vis_x1 = min(self.width - 1, x0 + total_w - 1)
        vis_y1 = min(self.height - 1, y + max_h - 1)

        vis_w = vis_x1 - vis_x0 + 1
        vis_h = vis_y1 - vis_y0 + 1
        if vis_w <= 0 or vis_h <= 0:
            return

        # 5) 在内存中拼一块行缓冲，然后一次性写入LCD
        px_bytes = len(self.color_fn(0, 0, 0))  # 每像素字节数：2或3
        buf = bytearray(vis_w * vis_h * px_bytes)

        # 5.1 如果有整体背景色则先铺底
        if bg is not None:
            bg_bytes = self.color_fn(bg)
            buf[:] = bg_bytes * (vis_w * vis_h)

        # 6) 绘制每个字符：可选字符背景 + 前景点阵
        fg_bytes = self.color_fn(color)
        cursor_x = x0

        for _, gw, gh, gdata in glyphs:
            # 字符在整个行图中的 x 范围
            ch_x0 = cursor_x
            ch_x1 = cursor_x + gw - 1
            # 与可见窗口相交的范围（避免越界绘制）
            ix0 = max(ch_x0, vis_x0)
            ix1 = min(ch_x1, vis_x1)
            if gw > 0 and gh > 0 and ix0 <= ix1:
                # 6.1 字符块背景：统一以行高 max_h 为块高，便于观察偏移
                if char_bg is not None:
                    cb = self.color_fn(char_bg)
                    # 行中相对坐标
                    rx0 = ix0 - vis_x0
                    rx1 = ix1 - vis_x0
                    ry0 = 0
                    ry1 = vis_h - 1  # 整个行块
                    self._fill_rect(buf, vis_w, vis_h, px_bytes, rx0, ry0, rx1, ry1, cb)

                # 6.2 绘制前景：把 glyph 的黑点贴到 buf
                # 垂直方向：将 glyph 置于行块的“顶对齐”（也可改成居中：y_off = (max_h - gh)//2）
                y_off_in_row = 0  # 顶对齐，便于观察上下偏移；若需居中改为：(max_h - gh) // 2
                # 计算在可见窗口中的有效绘制起点与裁剪
                draw_x = max(ch_x0, vis_x0)
                draw_y = max(y + y_off_in_row, vis_y0)
                # 在行缓冲的相对坐标
                rx = draw_x - vis_x0
                ry = draw_y - vis_y0

                # 若 glyph 在可见窗口内发生了左侧/顶部裁剪，需要跳过相应列/行
                skip_left = max(0, vis_x0 - ch_x0)
                skip_top = max(0, vis_y0 - (y + y_off_in_row))

                # 可见范围内的 glyph 尺寸
                vis_gw = gw - skip_left - max(0, (ch_x1 - vis_x1))
                vis_gh = gh - skip_top - max(0, (y + y_off_in_row + gh - 1 - vis_y1))

                if vis_gw > 0 and vis_gh > 0:
                    # 需要把裁剪后的 glyph 数据一行行取出再贴
                    bpr = (gw + 7) // 8
                    # 针对裁剪后的“左跳过列”，我们在读取位时跳过对应的 bit
                    for gy in range(vis_gh):
                        src_row = skip_top + gy
                        row_base = src_row * bpr
                        dst_row_start = ((ry + gy) * vis_w + rx) * px_bytes

                        # 从 skip_left 列开始，到 skip_left + vis_gw 列结束
                        sx = skip_left
                        di = dst_row_start
                        remain = vis_gw
                        while remain > 0:
                            byte_index = row_base + (sx // 8)
                            bit_in_byte = sx % 8
                            val = gdata[byte_index]
                            # 逐位取（从 MSB 开始）
                            for b in range(bit_in_byte, 8):
                                if remain <= 0:
                                    break
                                bit = (val >> (7 - b)) & 0x01
                                if bit:
                                    buf[di:di+px_bytes] = fg_bytes
                                di += px_bytes
                                sx += 1
                                remain -= 1
                                if (sx % 8) == 0 and remain > 0:
                                    # 跳到下一个字节
                                    if (row_base + (sx // 8)) < (row_base + bpr):
                                        val = gdata[row_base + (sx // 8)]
                                    break  # 退出内层 for，回到 while 以装载新字节

            cursor_x += gw + spacing

        # 7) 把整行缓冲写到屏幕
        self.set_window(vis_x0, vis_y0, vis_x1, vis_y1)
        self.write_data_bytes(buf)



spi = SPI(1, baudrate=40000000, polarity=0, phase=0,
          sck=Pin(6), mosi=Pin(5), miso=Pin(8)) 


async def main():
    st =  ST7796(spi,cs=1,dc=4,rst=2,bl=7,color_bit=16)
    st =  await st.init()
    st.load_bmf("TT.bmf")
    st.fill_screen((255,255,255))
    
        # 3) 画一行文字（每个字符带浅黄背景块，便于观察偏移）
    st.draw_text_bmf(
        x=10, y=40,
        # text="你好, Hello!",
        text="SA.mM式mjJ撒m电DF",
        size=16,
        color=(255,255,255),
        bg=None,                 # 不铺整行底色
        char_bg=(0,0,0),   # 每个字符独立背景；若不想要设为 None
        spacing=1,
        align='left'
    )


    # 4) 居中对齐示例
    st.draw_text_bmf(
        x=st.width//2, y=120,
        text="mM式mjJ撒m电DF",
        size=32,
        color=(0,0,0),
        char_bg=(255,255,255),
        spacing=2,
        align='center'
    )
    
        
        # 4) 居中对齐示例
    st.draw_text_bmf(
        x=st.width//2, y=240,
        text="mM式mjJ撒m电DF",
        size=48,
        color=(0,0,0),
        char_bg=(255,255,255),
        spacing=1,
        align='center'
    )
    
            
        # 4) 居中对齐示例
    st.draw_text_bmf(
        x=st.width//2, y=320,
        text="mM式m撒m电DF",
        size=8,
        color=(0,0,0),
        char_bg=(255,255,255),
        spacing=1,
        align='center'
    )
        
    # s =time.ticks_ms()
    # st.draw_text_bmf("电流: 0.8520A",scale=0.5,y=150,spacing=1)
    # print( (time.ticks_ms() -s) /1000)
    # s =time.ticks_ms()
    # st.draw_text_high_quality("电压: 03.4567V",scale=1,y=350,spacing=1)
    # print( (time.ticks_ms() -s) /1000)
    # s =time.ticks_ms()
    # st.draw_text_high_quality("功率: 2346W",scale=1,y=0,spacing=1,color=(255,255,0))
    # print( (time.ticks_ms() -s) /1000)
    # s =time.ticks_ms()
    # st.draw_text_high_quality("电流",scale=1,y=200,spacing=3,color=(255,255,0))
    # print((time.ticks_ms()-s)/1000)

    
    
    await asyncio.sleep(1000)
    
    
    

    
    
    
    
    
    
    
    
    
    
    # # st.set_window(0,0,320,480)
    # data =bytearray()
    # for i in range(480):
    #     st.fill_screen((255,0,0))
    #     # data.extend(st.color_fn(i%256,i%256,i%256)*320)
    # st.write_data_bytes(data)
    # print(1)
    
    
    
    
    
    
    
    
    
    
    
    
    
    await asyncio.sleep(1000)
    st.draw_text_high_quality(0, 320, "撒", scale=1, color=(255, 0, 0))
    st.draw_text_high_quality(0, 350, "撒打发士", scale=1.5, color=(255, 0, 0))
    st.draw_text_high_quality(0, 400, "撒打发士", scale=2, color=(255, 0, 0))
    await asyncio.sleep(100)



    st.fill_screen((0,0,0))  # 清屏

    text = "撒大ABCCC"  # 循环显示的测试文字
    scale = 5      # 16x16 字符
    spacing = 1      # 字符间距

    # 计算每行可显示的字符数和行数
    cols = st.width // (8*scale + spacing)
    rows = st.height // (16*scale)

    # 生成每行文字
    line_text = (text * ((cols // len(text)) + 1))[:cols]
    # print(line_text)

    start = time.ticks_ms()
    # print(rows)
    # 按行显示，每行一次性写 SPI
    for r in range(rows):
        start = time.ticks_ms()
        y = r * 16 * scale
        st.draw_text(0, y, line_text, scale, (255,0,0), spacing)

    end = time.ticks_ms()
    print("整屏文字绘制耗时(ms):", time.ticks_diff(end, start))


    await asyncio.sleep(10)

    # 遍历 /image 目录下所有文件
    image_dir = "../image"
    img_data_dir = "/img_data"
    img = []
    img_data = []
    st.fill_screen((0,0,0))
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(".bmp"):
            src_path = f"{image_dir}/{filename}"
            dst_path = f"{img_data_dir}/{filename.split('.')[0]}.img"  # 生成处理后的文件名
            img_data.append(dst_path)
            img.append(src_path)
            # st.write_img(src_path, dst_path)
            print(f"已处理: {src_path} -> {dst_path}")
            
    while True:
        for i in img:
            s = time.ticks_ms()
            st.show_img(i)
            print((time.ticks_ms()-s ) / 1000)
            # await asyncio.sleep_ms(100)

    # st.show_img_data_path(img_data[3])
    # st.show_img(img[3])
    
asyncio.run(main())