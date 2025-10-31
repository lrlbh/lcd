import time
import asyncio
from machine import Pin
# import gc
import struct
import lcd

# def timeit(func):
#     def wrapper(*args, **kwargs):
#         s = time.ticks_us()
#         result = func(*args, **kwargs)
#         e = time.ticks_us()
#         print("耗时(ms):", time.ticks_diff(e, s) / 1000)
#         return result

#     return wrapper


class ST7796(lcd.LCD):
    def __init__(self, spi, cs, dc, rst, bl,  旋转=3, 
                 color_bit=24,w=320, h=480,逆CS=False):
        super().__init__(spi, cs, dc, rst, bl,  旋转,
                         color_bit,w, h,逆CS)

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

        self.fill(self.color.基础灰阶.黑)

        return self

    # 加了些延迟，所以用async初始类
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

