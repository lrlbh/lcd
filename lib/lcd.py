import asyncio
import time
from machine import Pin, SPI


class LCD:

    class Size:
        
        # W -- H
        st7735 = (132, 162)

        # 推测是ili9163,排线上也没有引出读取脚
        # 不过有大量讨论证明，应该不是校准问题
        st7735假货_144 = (132, 132)
        # 推测也是ili9163,不过没查资料了，前面查1.44寸时
        # 有说明ili9163,出厂可以配置为多个分辨率，其中有128*160
        st7735假货_18 = (128, 160)

        st7789 = (240, 320)
        st7796 = (320, 480)

        ili9488 = (320, 480)

        gc9a01 = (240, 240)
        gc9107 = (128, 160)

    # 顺序上下左右
    # 上上下下左右左右ba...
    class 像素缺失:
        # 0.96寸 80 *160
        st7735_0_96 = (1, 1, 26, 26)

        # 1.44寸 128 * 128
        st7735假货_1_44 = (1, 3, 2, 2)

        # 1.8寸 128* 160
        st7735_1_8 = (1, 1, 2, 2)

        # 0.85寸 128* 128
        gc9107_0_85 = (32, 0, 0, 0)

        # 1.14寸 135 * 240
        st7789_1_14 = (40, 40, 52, 53)

        # 1.3寸240*240
        st7789_1_3 = (0, 80, 0, 0)

        # 1.54寸240*240
        st7789_1_54 = (0, 80, 0, 0)

        # 1.69寸 240 * 280
        st7789_1_69 = (20, 20, 0, 0)

        # 1.9寸 170 * 320
        st7789_1_9 = (0, 0, 35, 35)

    # 加速set_window
    _window缓存 = bytearray(4)

    # 像素数据
    # char_缓存[(背景色,字体色,字,字号)] = bytes
    _char_缓存 = {}

    # 点阵数据
    # 列刷新字体需要 --> 左旋270 || 右旋90
    # 字库：char[size][字] = 点位图
    _char = {}
    _char[32] = {}

    # 方便测试，随便预设几个字符
    _char[32]["阿"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x7F,
            0xFF,
            0xFF,
            0xF0,
            0x00,
            0x00,
            0x00,
            0x10,
            0x00,
            0x40,
            0x00,
            0x10,
            0x00,
            0x40,
            0x10,
            0x10,
            0x01,
            0xC0,
            0x2E,
            0x10,
            0x01,
            0xC0,
            0xC3,
            0x90,
            0x00,
            0xFF,
            0x80,
            0xF0,
            0x00,
            0x7E,
            0x00,
            0x38,
            0x00,
            0x00,
            0x00,
            0x10,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x20,
            0x00,
            0x7F,
            0xF8,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x3F,
            0xF8,
            0x20,
            0x08,
            0x1F,
            0xFC,
            0x20,
            0x10,
            0x00,
            0x08,
            0x20,
            0x10,
            0x00,
            0x00,
            0x20,
            0x30,
            0x00,
            0x00,
            0x20,
            0x30,
            0x00,
            0x00,
            0x20,
            0x3F,
            0xFF,
            0xFF,
            0xE0,
            0x1F,
            0xFF,
            0xFF,
            0xE0,
            0x00,
            0x00,
            0x00,
            0x30,
            0x00,
            0x00,
            0x00,
            0x38,
            0x00,
            0x00,
            0x00,
            0x20,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32]["斯"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x80,
            0x20,
            0x10,
            0x00,
            0x80,
            0x18,
            0x10,
            0x00,
            0x80,
            0x0C,
            0x10,
            0x00,
            0x80,
            0x06,
            0x1F,
            0xFF,
            0xFC,
            0x03,
            0x9F,
            0xFF,
            0xF8,
            0x01,
            0x91,
            0x08,
            0x88,
            0x00,
            0x11,
            0x08,
            0x80,
            0x00,
            0x11,
            0x08,
            0x80,
            0x00,
            0x51,
            0x08,
            0x80,
            0x00,
            0x91,
            0x08,
            0x80,
            0x41,
            0x9F,
            0xFF,
            0xFC,
            0x2F,
            0x10,
            0x00,
            0x88,
            0x36,
            0x10,
            0x00,
            0x80,
            0x18,
            0x18,
            0x00,
            0xC0,
            0x0E,
            0x10,
            0x00,
            0x80,
            0x03,
            0x80,
            0x00,
            0x00,
            0x01,
            0xFF,
            0xFF,
            0xE0,
            0x00,
            0x1F,
            0xFF,
            0xE0,
            0x00,
            0x00,
            0x20,
            0x20,
            0x00,
            0x00,
            0x20,
            0x20,
            0x00,
            0x00,
            0x20,
            0x20,
            0x00,
            0x00,
            0x20,
            0x20,
            0x7F,
            0xFF,
            0xE0,
            0x10,
            0x3F,
            0xFF,
            0xE0,
            0x10,
            0x00,
            0x00,
            0x20,
            0x18,
            0x00,
            0x00,
            0x30,
            0x18,
            0x00,
            0x00,
            0x20,
            0x10,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32]["顿"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x04,
            0x01,
            0x00,
            0x00,
            0x0F,
            0xF9,
            0x00,
            0x00,
            0x04,
            0x01,
            0x00,
            0x00,
            0x04,
            0x01,
            0x00,
            0x00,
            0x04,
            0x01,
            0x00,
            0x0F,
            0xFF,
            0xFF,
            0xFC,
            0x1F,
            0xFF,
            0xFF,
            0xF8,
            0x0C,
            0x04,
            0x01,
            0x00,
            0x06,
            0x04,
            0x01,
            0x00,
            0x02,
            0x04,
            0x01,
            0x00,
            0x41,
            0x0F,
            0xF9,
            0x00,
            0x41,
            0x07,
            0xF9,
            0x80,
            0x20,
            0x80,
            0x01,
            0x08,
            0x20,
            0x00,
            0x00,
            0x08,
            0x10,
            0xFF,
            0xFF,
            0x08,
            0x10,
            0x7F,
            0xFE,
            0x08,
            0x08,
            0x00,
            0x02,
            0x08,
            0x0C,
            0x00,
            0x02,
            0x08,
            0x07,
            0x00,
            0x03,
            0x08,
            0x01,
            0xFE,
            0x12,
            0xF8,
            0x00,
            0x7F,
            0xE2,
            0x38,
            0x01,
            0x00,
            0x22,
            0x08,
            0x01,
            0x00,
            0x02,
            0x08,
            0x02,
            0x00,
            0x02,
            0x08,
            0x06,
            0x00,
            0x02,
            0x08,
            0x0C,
            0x7F,
            0xFF,
            0x08,
            0x38,
            0x00,
            0x02,
            0x0C,
            0x78,
            0x00,
            0x00,
            0x08,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32]["a"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x03,
            0xC0,
            0x00,
            0x00,
            0x07,
            0xE3,
            0x80,
            0x00,
            0x0C,
            0x33,
            0xC0,
            0x00,
            0x08,
            0x10,
            0x40,
            0x00,
            0x08,
            0x18,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x08,
            0x08,
            0x20,
            0x00,
            0x04,
            0x08,
            0x20,
            0x00,
            0x04,
            0x04,
            0x60,
            0x00,
            0x07,
            0xFF,
            0xC0,
            0x00,
            0x0F,
            0xFF,
            0x80,
            0x00,
            0x08,
            0x00,
            0x00,
            0x00,
            0x08,
            0x00,
            0x00,
            0x00,
            0x06,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32]["s"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x0F,
            0x80,
            0x00,
            0x00,
            0x06,
            0x07,
            0x80,
            0x00,
            0x04,
            0x0F,
            0xC0,
            0x00,
            0x08,
            0x0C,
            0x60,
            0x00,
            0x08,
            0x18,
            0x20,
            0x00,
            0x08,
            0x18,
            0x20,
            0x00,
            0x08,
            0x38,
            0x20,
            0x00,
            0x08,
            0x30,
            0x20,
            0x00,
            0x0C,
            0x70,
            0x40,
            0x00,
            0x07,
            0xE0,
            0xC0,
            0x00,
            0x03,
            0xC3,
            0xE0,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32]["d"] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0xFE,
            0x00,
            0x00,
            0x03,
            0xFF,
            0x80,
            0x00,
            0x06,
            0x01,
            0xC0,
            0x00,
            0x0C,
            0x00,
            0x60,
            0x00,
            0x08,
            0x00,
            0x20,
            0x00,
            0x08,
            0x00,
            0x20,
            0x00,
            0x08,
            0x00,
            0x20,
            0x00,
            0x04,
            0x00,
            0x20,
            0x40,
            0x02,
            0x00,
            0x40,
            0x40,
            0x0F,
            0xFF,
            0xFF,
            0xC0,
            0x07,
            0xFF,
            0xFF,
            0xE0,
            0x04,
            0x00,
            0x00,
            0x00,
            0x04,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    _char[32][" "] = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )

    def __init__(
        self,
        spi: SPI,
        dc,
        size=Size.st7789,
        bl=None,
        rst=None,
        cs=None,
        旋转=3,
        color_bit=16,  # 7735 使用 18bit OR 16bit,实际应该是支持16bit
        像素缺失=(0, 0, 0, 0),
        逆CS=False,
    ):
        self._spi = spi

        if cs is None:
            self._cs = None
        else:
            self._cs = Pin(cs, Pin.OUT)

        self._dc = Pin(dc, Pin.OUT)

        # 复位
        if rst is not None:
            self._rst = Pin(rst, Pin.OUT)
        else:
            self._rst = None

        # 背光
        if bl is not None:
            self._bl = Pin(bl, Pin.OUT, value=1)
        else:
            self._bl = None

        # 像素bit
        self.__color_bit = color_bit
        self._byte = 3
        if self.__color_bit == 16:
            self._byte = 2

        self._size = size
        self._像素缺失_顶 = 像素缺失[0]
        self._像素缺失_底 = 像素缺失[1]
        self._像素缺失_左 = 像素缺失[2]
        self._像素缺失_右 = 像素缺失[3]

        # 通过选择角度设置w和h,逻辑列刷新
        # 像素补偿 = (1, 33, 2, 2)
        self._旋转 = 旋转
        if 旋转 == 1 or 旋转 == 3:
            self._width_驱动 = size[0]
            self._height_驱动 = size[1]
            self._width = size[0] - (self._像素缺失_右 + self._像素缺失_左)
            self._height = size[1] - (self._像素缺失_底 + self._像素缺失_顶)
        else:
            self._width_驱动 = size[1]
            self._height_驱动 = size[0]
            self._width = size[1] - (self._像素缺失_底 + self._像素缺失_顶)
            self._height = size[0] - (self._像素缺失_右 + self._像素缺失_左)

        if 旋转 == 0:
            self._列偏移 = self._像素缺失_顶
            self._行偏移 = self._像素缺失_右
        elif 旋转 == 1:
            self._列偏移 = self._像素缺失_右
            self._行偏移 = self._像素缺失_底
        elif 旋转 == 2:
            self._列偏移 = self._像素缺失_底
            self._行偏移 = self._像素缺失_左
        else:
            self._列偏移 = self._像素缺失_左
            self._行偏移 = self._像素缺失_顶

        # 不同色彩需要数据不同
        if self.__color_bit == 16:
            self.color_fn = self._color565
            self.color = 预设色16位
        elif self.__color_bit == 18:
            self.color_fn = self._color666
            self.color = 预设色24位
        elif self.__color_bit == 24:
            self.color_fn = self._color888
            self.color = 预设色24位
        else:
            raise ValueError("色彩位数有误")

        # 如果SPI只驱动了两个设备，可以省略CS
        self._cs_on = 0
        self._cs_off = 1
        if 逆CS:
            self._cs_on = 1
            self._cs_off = 0

    def _init(self, 反色=1, rgb=1, 左右镜像=1):
        # 复位
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)  # 等待 120ms 以上

        # 退出睡眠
        self._write_cmd(0x11)
        time.sleep_ms(120)

        # === 扫描方向 ===
        # 0: 正常 / 1: 90° / 2: 180° / 3: 270°
        # 参考 ST7796 寄存器 0x36（MADCTL）
        # 默认 val 数组对应 旋转角度下 MY/MX/MV 三位组合
        # === 扫描方向 ===
        # 0: 正常 / 1: 90° / 2: 180° / 3: 270°
        # 参考 ST7796 寄存器 0x36（MADCTL）
        # 默认 val 数组对应 旋转角度下 MY/MX/MV 三位组合
        self._write_cmd(0x36)
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        # 左右镜像（MX）控制
        if not 左右镜像:
            val ^= 0x40  # 取反 MX 位（D6）
        # RGB/BGR 控制
        if rgb:
            val &= ~0x08  # D3=0 表示 BGR
        else:
            val |= 0x08  # D3=1 表示 RGB
        self._write_data(val)


        # 像素格式  888 666 565
        self._write_cmd(0x3A)
        # self._write_data(0x33)
        if self.__color_bit == 16:
            self._write_data(0x55)
        elif self.__color_bit == 18:
            self._write_data(0x66)
        elif self.__color_bit == 24:
            self._write_data(0x77)



        # === 反色显示（可选）===
        # 命令 0x21：Inversion ON s
        if 反色:
            self._write_cmd(0x21)
        else:
            self._write_cmd(0x20)

        # === 开显示 ===
        # 命令 0x29：Display ON
        self._write_cmd(0x29)
        time.sleep_ms(60)

        # === 清屏 ===
        # 使用基础灰阶黑色填充整个屏幕
        self.fill(self.color.黑)
        return self

    async def _init_async(self, 反色=1, rgb=1, 左右镜像=1):
                # 复位
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            await asyncio.sleep_ms(50)
            self._rst.value(1)
        await asyncio.sleep_ms(150)  # 等待 120ms 以上

        # 退出睡眠
        self._write_cmd(0x11)
        await asyncio.sleep_ms(150)

        # === 扫描方向 ===
        # 0: 正常 / 1: 90° / 2: 180° / 3: 270°
        # 参考 ST7796 寄存器 0x36（MADCTL）
        # 默认 val 数组对应 旋转角度下 MY/MX/MV 三位组合
        self._write_cmd(0x36)
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        # 左右镜像（MX）控制
        if not 左右镜像:
            val ^= 0x40  # 取反 MX 位（D6）
        # RGB/BGR 控制
        if rgb:
            val &= ~0x08  # D3=0 表示 BGR
        else:
            val |= 0x08  # D3=1 表示 RGB
        self._write_data(val)

        # 像素格式  888 666 565
        self._write_cmd(0x3A)
        # self._write_data(0x33)
        if self.__color_bit == 16:
            self._write_data(0x55)
        elif self.__color_bit == 18:
            self._write_data(0x66)
        elif self.__color_bit == 24:
            self._write_data(0x77)



        # === 反色显示（可选）===
        # 命令 0x21：Inversion ON s
        if 反色:
            self._write_cmd(0x21)
        else:
            self._write_cmd(0x20)

        # === 开显示 ===
        # 命令 0x29：Display ON
        self._write_cmd(0x29)
        await asyncio.sleep_ms(60)

        # === 清屏 ===
        # 使用基础灰阶黑色填充整个屏幕
        self.fill(self.color.黑)
        return self

    # ------- 基本IO -------
    def _cs_open(self):
        # time.sleep_ms(10)
        if self._cs is None:
            return
        self._cs(self._cs_on)

    def _cs_close(self):
        # time.sleep_ms(10)
        if self._cs is None:
            return
        self._cs(self._cs_off)

    def _write_cmd(self, cmd):
        self._dc.value(0)
        self._cs_open()
        self._spi.write(bytearray([cmd]))
        self._cs_close()

    def _write_data(self, data):
        self._dc.value(1)
        self._cs_open()
        self._spi.write(bytearray([data]))
        self._cs_close()

    def _write_data_bytes(self, buf):
        self._dc.value(1)
        self._cs_open()
        self._spi.write(buf)
        self._cs_close()

    # 行刷新下，最严重的瓶颈，刷新一次屏幕动辄需要调用上千次
    # 此瓶颈可以转移到处理数据，不过mpy+PSRAM+数据处理，瓶颈更严重
    # 牺牲了可读,复用,代码量
    # 速度提升 1.5ms --> 0.4ms
    # 如果后续放弃多次频繁调用，这点提升屁用没有，改回来
    # 改成逻辑列刷新后这点速度完全没用了，不过改不改的也没意思
    # 最近又修改了很多次了，肯定有很多冗余操作了，什么时候优化一下
    def _set_window(self, x0, y0, x1, y1):
        # 部分屏幕阉割了一些分辨率，常见于st7735

        x0 += self._列偏移
        x1 += self._列偏移
        y0 += self._行偏移
        y1 += self._行偏移

        # 期望w = x1 - x0 + 1
        # 期望h = y1 - y0 + 1
        # 期望像素 = 期望w * 期望h

        # 逻辑列刷新核心逻辑
        # if self._旋转==0  or self._旋转==3:
        #     t = y0
        #     y0 = self._height_驱动 - y1 - 1
        #     y1 = self._height_驱动 - t - 1
        # else:
        #     t = y0
        #     y0 = self._width_驱动 - y1 - 1
        #     y1 = self._width_驱动 - t - 1

        # udp.send(f"旋转:{self._旋转}  高: {self._height_驱动}")
        t = y0
        y0 = self._height_驱动 - y1 - 1
        y1 = self._height_驱动 - t - 1

        # t = y0
        # y0 = self._height - 1 - y1
        # y1 = self._height - 1 - t

        # # 逻辑列刷新核心逻辑
        # t = x0
        # x0 = self._width_驱动 - x1
        # x1 = self._width_驱动 - t

        # t0, t1 = x0,x1
        # x0,x1 = y0,y1
        # y0,y1 = t0,t1

        # udp.send(f"{x0, x1, y0, y1}")
        # y0 = 0
        # y1 = 239

        self._cs_open()
        buf = LCD._window缓存

        # 列地址
        self._dc.value(0)
        self._spi.write(b"\x2a")
        self._dc.value(1)
        buf[0] = (y0 >> 8) & 0xFF
        buf[1] = y0 & 0xFF
        buf[2] = (y1 >> 8) & 0xFF
        buf[3] = y1 & 0xFF
        self._spi.write(buf)
        # udp.send(f"列设置: {buf}")

        # y0_val = int.from_bytes(buf[0:2], "big")
        # y1_val = int.from_bytes(buf[2:4], "big") + 1
        # 实际h = y1_val - y0_val

        # 行地址
        self._dc.value(0)
        self._spi.write(b"\x2b")
        self._dc.value(1)
        buf[0] = (x0 >> 8) & 0xFF
        buf[1] = x0 & 0xFF
        buf[2] = (x1 >> 8) & 0xFF
        buf[3] = x1 & 0xFF
        self._spi.write(buf)
        # udp.send(f"行设置: {buf}")

        # x0_val = int.from_bytes(buf[0:2], "big")
        # x1_val = int.from_bytes(buf[2:4], "big") + 1
        # 实际w = x1_val - x0_val

        # udp.send(
        #     f"实际w-h: {实际w, 实际h, 实际h * 实际w}  期望w-h: {期望w, 期望h, 期望像素}"
        # )

        # RAMWR (0x2C)
        self._dc.value(0)
        self._spi.write(b"\x2c")
        self._cs_close()

    def _set_window原始(self, x0, y0, x1, y1):
        buf = bytearray(4)

        # 设置列地址 CASET (0x2A)
        self._write_cmd(0x2A)
        buf[0] = (x0 >> 8) & 0xFF
        buf[1] = x0 & 0xFF
        buf[2] = (x1 >> 8) & 0xFF
        buf[3] = x1 & 0xFF
        # udp.send(f"列设置: {buf}")
        self._write_data_bytes(buf)

        # 设置行地址 RASET (0x2B)
        self._write_cmd(0x2B)
        buf[0] = (y0 >> 8) & 0xFF
        buf[1] = y0 & 0xFF
        buf[2] = (y1 >> 8) & 0xFF
        buf[3] = y1 & 0xFF
        # udp.send(f"行设置: {buf}")
        self._write_data_bytes(buf)

        # 准备写像素
        self._write_cmd(0x2C)

    def _set_window原始加偏移(self, x0, y0, x1, y1):
        buf = bytearray(4)

        if self._旋转 == 0:
            self._列偏移 = self._像素缺失_左
            self._行偏移 = self._像素缺失_顶
        # elif self.旋转 == 1:
        #     self._列偏移 = self._像素缺失_右
        #     self._行偏移 = self._像素缺失_底
        # elif self.旋转 == 2:
        #     self._列偏移 = self._像素缺失_底
        #     self._行偏移 = self._像素缺失_左
        # else:
        #     self._列偏移 = self._像素缺失_左
        #     self._行偏移 = self._像素缺失_顶

        x0 += self._列偏移
        x1 += self._列偏移
        y0 += self._行偏移
        y1 += self._行偏移

        # 设置列地址 CASET (0x2A)
        self._write_cmd(0x2A)
        buf[0] = (x0 >> 8) & 0xFF
        buf[1] = x0 & 0xFF
        buf[2] = (x1 >> 8) & 0xFF
        buf[3] = x1 & 0xFF
        # udp.send(f"列起始: {buf}")
        self._write_data_bytes(buf)

        # 设置行地址 RASET (0x2B)
        self._write_cmd(0x2B)
        buf[0] = (y0 >> 8) & 0xFF
        buf[1] = y0 & 0xFF
        buf[2] = (y1 >> 8) & 0xFF
        buf[3] = y1 & 0xFF
        # udp.send(f"行起始: {buf}")
        self._write_data_bytes(buf)

        # 准备写像素
        self._write_cmd(0x2C)

    def _test_像素裁剪(self):
        self.fill原始(self.color_fn(255, 255, 255))

        if self._旋转 != 0:
            raise ValueError("建议使用旋转0来裁剪，避免动脑。裁剪后可用于所有旋转角度")

        w, h = self._height, self._width
        b = b""
        背景色 = self.color_fn(255, 0, 0)  # 红
        边框色 = self.color_fn(0, 255, 0)  # 绿
        下边框色 = self.color_fn(255, 255, 255)
        箭头色 = self.color_fn(0, 0, 255)  # 蓝
        左上角色 = self.color_fn(255, 255, 255)
        if w % 2 != 0:
            b = 背景色
        左上角色 = 边框色 + 左上角色 * ((w - 2) // 2)
        左上角色 += 背景色 * ((w - 2) // 2) + b + 边框色

        t_h = h // 2
        buf = bytearray()
        for i in range(h):
            if i == 0 or i == h - 1:  # 上边框
                buf.extend(边框色 * w)
                continue
            if i == h - 1:
                buf.extend(下边框色 * w)
                continue
            if i < t_h:
                buf.extend(左上角色)
                continue
            if i == t_h:  # 宽箭头
                buf.extend(边框色 + 箭头色 * (w - 2) + 边框色)
                continue
            buf.extend(边框色 + 背景色 * (w - 2) + 边框色)

        # 列箭头
        mv = memoryview(buf)  # 避免索引不报错
        index = 0
        s = w * self._byte // 2  # 像素1/2
        for i in range(h - 2):
            index += w * self._byte  # 偏移一整行
            mv[index + s : index + s + self._byte] = 箭头色

        # 数据校验
        if w * h * self._byte != len(buf):
            raise ValueError(f"生成数据有误{len(buf) / self._byte}")

        # 清屏
        self._set_window原始加偏移(0, 0, w - 1, h - 1)
        self._write_data_bytes(buf)
        return (len(buf) / self._byte, w, h)

    # 方框测试
    def _test(self):
        self.fill原始(self.color.白)

        边框颜色 = self.color_fn(0, 255, 0)
        buf = bytearray()
        for i in range(self._width):
            if i == 0 or i == self._width - 1:
                buf.extend(边框颜色 * self._height)
                continue
            buf.extend(边框颜色 + self.color.红 * (self._height - 2) + 边框颜色)

        # 显示
        self._set_window(0, 0, self._width - 1, self._height - 1)
        # self._set_window(0, 0, self._width - 1, self._height - 1)
        self._write_data_bytes(buf)

        h = 1
        while h < self._height:
            self.txt(
                "阿",
                1,
                h,
                32,
                self.color.白,
                self.color.黑,
                缓存=True,
            )
            h += 32

    # 更新速度测试
    def _test_spi(self):
        ret = []

        # 测试SPI速率
        t1 = self.color.紫 * self._width * self._height
        t2 = self.color.粉 * self._width * self._height
        t3 = memoryview(t1)
        t4 = memoryview(t2)

        self._set_window(0, 0, self._width - 1, self._height - 1)
        self._cs_open()
        self._dc.value(1)
        for _ in range(20):
            s = time.ticks_ms()
            self._spi.write(t3)
            tt = time.ticks_ms() - s
            ret.append(tt)

            s = time.ticks_ms()
            self._spi.write(t4)
            tt = time.ticks_ms() - s
            ret.append(tt)

        self._cs_close()
        return ret

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

    # 清屏
    def fill(self, color):
        self._set_window(0, 0, self._width - 1, self._height - 1)
        # 一次性铺满
        self._write_data_bytes(color * (self._width * self._height))

    def fill原始(self, color):
        self._set_window原始(0, 0, self._height_驱动 - 1, self._width_驱动 - 1)
        self._write_data_bytes(color * (self._height_驱动 * self._width_驱动))

    def txt(
        self,
        字符串,
        x,
        y,
        size,
        字体色 = None,
        背景色 = None,
        缓存 = False,
    ):
        if 字体色 is None:
            字体色 = self.color.白
        if 背景色 is None:
            背景色 = self.color.黑
        
        # s = time.ticks_ms()
        # 终点字符，终点坐标
        new_str = []  # 处理非法数据后的字符串
        w = x - 1  # 终点坐标
        h = y + size - 1  # 终点坐标

        # 非法高度
        if h >= self._height:
            return

        # 计算终点字符，终点坐标
        for 字 in 字符串:
            # 字符不存在用空格
            if 字 not in LCD._char.get(size, {}):
                字 = " "

            # ascii 半宽
            t_w = size
            if ord(字) < 128:
                t_w = size // 2

            # 超出显示范围，截断字符串
            if w + t_w >= self._width:
                break
            w += t_w

            new_str.append(字)

        # 设置显示范围
        self._set_window(x, y, w, h)
        # return

        # 显示字符
        for 字 in new_str:
            key = (字, size, 字体色, 背景色)  # 缓存key

            # 有缓存,直接显示
            if key in LCD._char_缓存:
                self._write_data_bytes(LCD._char_缓存[key])
                continue

            # 像素数据
            zxc = bytearray()

            # 点阵字节转像素
            # 此处实现是单边批量添加
            # 实测双边批量添加效率稍低
            # mem操作效率最低
            t = 0
            for byte in LCD._char[size][字]:
                for bit in range(8):
                    if byte & (1 << (7 - bit)):
                        zxc.extend(背景色 * t + 字体色)
                        t = 0
                        # zxc.extend(字体色)
                    else:
                        t += 1
                        # zxc.extend(背景色)
            if t:
                zxc.extend(背景色 * t)
 
            # 点阵字节转像素，此法也不错甚至稍快
            # 数据存入列表，只调用一次 extend
            # 数据块 = []  # 暂存所有小片段的引用
            # t = 0

            # for byte in LCD._char[size][字符串[i]]:
            #     for bit in range(8):
            #         if byte & (1 << (7 - bit)):
            #             if t:
            #                 数据块.append(背景色 * t)
            #                 t = 0
            #             数据块.append(字体色)
            #         else:
            #             t += 1

            # if t:
            #     数据块.append(背景色 * t)
            # # udp.send(len(数据块))
            # zxc.extend(b"".join(数据块))

            # 显示和加入缓存
            # zxc = memoryview(zxc)  zxc
            # 是否加入缓存
            if 缓存:
                LCD._char_缓存[key] = zxc
            # 无缓存显示
            self._write_data_bytes(zxc)

        # udp.send(time.ticks_ms() - s)

    # ------- 字体 -------
    class def_字符:
        ascii = """ 1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ~·！@#￥%……&*（）——++-=、|【{}】；：‘“，《。》/？*~!@#$%^&*()-_=+[{}]\|;:'",<.>/?/*"""
        常用字符 = "温度电压流功率"
        all = ascii + 常用字符

    def _load_bmf(self, path, 需要的字符):
        LCD._char = {}
        # size = os.stat(path)[6]

        # f.readinto(buf)  # **不改读取方式**
        with open(path, "rb") as f:
            buf = f.read(12)

            if buf[0:4] != b"BMF3":
                raise ValueError("格式有误")
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
                LCD._char[当前字号] = {}
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
                        LCD._char[当前字号][ch] = buf[idx : idx + 点阵长度_ascii]
                        idx += 点阵长度_ascii
                    else:
                        LCD._char[当前字号][ch] = buf[idx : idx + 点阵长度]
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
            LCD._char = {}
            for 字号, 文本 in 需要的字符.items():
                if 字号 not in idx_range:
                    continue
                idx_start, idx_end = idx_range[字号]
                off_start, off_end = off_range[字号]
                LCD._char[字号] = {}

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
                        LCD._char[字号][字符] = f.read(ascii点阵长度)
                    else:
                        LCD._char[字号][字符] = f.read(点阵长度)

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

        return self


    def new_波形(
        self,
        w起点: int,
        h起点: int,
        size_w: int,
        size_h: int,
        多少格: int,
        波形像素: list,
        data_min: list,
        data_max: list,
        波形色: list,
        背景色: bytes,
    ):
        return 波形(
            self,
            w起点,
            h起点,
            size_w,
            size_h,
            多少格,
            波形像素,
            data_min,
            data_max,
            波形色,
            背景色,
        )


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
        多少格: int,
        波形像素: list,
        data_min: list,
        data_max: list,
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
        self._波形len = []
        for t in 波形像素:
            self._波形len.append(t * self._size_byte)
        self._波形色 = []
        for i, t in enumerate(波形色):
            self._波形色.append(t * 波形像素[i])
        self._背景色 = 背景色
        self._size = int(size_w * size_h * self._size_byte)
        self._buf = bytearray(self._size)
        self._mv = memoryview(self._buf)
        self._当前下标 = 0  # 最旧字节位置
        self._多少格 = 多少格
        self._min = data_min
        self._max = data_max
        self._允许的最大下标 = []
        for t in 波形像素:
            self._允许的最大下标.append(self._size_h - t)

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
        for 通道_i in range(len(data)):
            # 数据映射到下标
            index = (
                (data[通道_i] - self._min[通道_i])
                / (self._max[通道_i] - self._min[通道_i])
                * self._允许的最大下标[通道_i]
            )

            # # 限幅，防止传入数据超过幅值
            if index > self._允许的最大下标[通道_i]:
                index = self._允许的最大下标[通道_i]
            if index < 0:
                index = 0

            # 每个像素多少个字节做一下偏移
            index = int(index) * self._size_byte

            # 数据更新到背景色中
            td[index : index + self._波形len[通道_i]] = self._波形色[通道_i]

        # # 查看有无，不合理数据
        # if len(td) > self._size_h * self._size_byte:
        #     udp.send("ERROR")
        #     return

        self._append(td)

    # 单次追加数据越多越慢
    def _append(self, data: bytes) -> None:
        if self._当前下标 == self._size:
            self._当前下标 = 0

        for i in range(len(data)):
            self._buf[self._当前下标 + i] = data[i]

        self._当前下标 = self._当前下标 + len(data)
        # udp.send(self.当前下标 )

    # 非常快,不过未知原因当byteaary末尾数据越多越慢
    # 环形内存一次性申请460K+内存,分320还是480次添加忘了
    # 索引起步时添加数据20ms,索引末尾时添加数据0ms，线性降低
    # 上面方法稳定6~7ms，稳定的慢
    # 正常使用应该下面这个快
    # 万一性能不够，整合两个函数为一个
    def _append_mv(self, data: bytes) -> None:
        if self._当前下标 == self._size:
            self._当前下标 = 0
        下一次下标 = self._当前下标 + len(data)
        self._buf[self._当前下标 : 下一次下标] = data
        self._当前下标 = 下一次下标

    def _get_all_data(self):
        return self._mv[self._当前下标 : self._size], self._mv[0 : self._当前下标]


class 预设色16位:
    # ---- 基础灰阶 ----
    白 = b"\xff\xff"  # FFFF
    黑 = b"\x00\x00"  # 0000
    浅灰 = b"\xc6\x18"  # C618
    中灰 = b"\x84\x10"  # 8410
    深灰 = b"\x42\x08"  # 4208

    # ---- 功能语义 ----
    蓝 = b"\x23\xdd"  # 237D?（实际：23DD）
    绿 = b"\x35\x4b"  # 354B
    黄 = b"\xfe\x48"  # FE48
    红 = b"\xe9\xc8"  # E9C8
    青 = b"\x05\x59"  # 0559

    # ---- 高亮 / 强调 ----
    橙 = b"\xfc\x86"  # ← 正确橙色 FC86  (RGB 248,144,48)
    紫 = b"\x9a\xda"  # 9ADA
    粉 = b"\xfd\x98"  # FD98


class 预设色24位:
    # ---- 基础灰阶 ----
    白 = b"\xff\xff\xff"  # (255,255,255)
    黑 = b"\x00\x00\x00"  # (0,0,0)
    浅灰 = b"\xc0\xc0\xc0"  # (192,192,192)
    中灰 = b"\x80\x80\x80"  # (128,128,128)
    深灰 = b"\x40\x40\x40"  # (64,64,64)

    # ---- 功能语义 ----
    蓝 = b"\x20\x78\xe8"  # (32,120,232)
    绿 = b"\x30\xa8\x58"  # (48,168,88)
    黄 = b"\xf8\xc8\x40"  # (248,200,64)
    红 = b"\xe8\x38\x40"  # (232,56,64)
    青 = b"\x00\xa8\xc8"  # (0,168,200)

    # ---- 高亮 / 强调 ----
    橙 = b"\xf8\x90\x30"  # (248,144,48)
    紫 = b"\x98\x58\xd0"  # (152,88,208)
    粉 = b"\xf8\xb0\xc0"  # (248,176,192)




