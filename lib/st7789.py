import time
import asyncio
import lcd


class ST7789(lcd.LCD):
    def __init__(self, spi, cs, dc, rst, bl,
                 旋转=3, color_bit=16, w=240, h=320, 逆CS=False):
        super().__init__(spi, cs, dc, rst, bl, 旋转, color_bit, w, h, 逆CS)

    def _init(self):
        """ST7789 同步初始化（严格按官方顺序）"""
        # --- 硬件复位 ---
        self._rst.value(0)
        time.sleep_ms(50)
        self._rst.value(1)
        time.sleep_ms(120)

        # --- 退出睡眠模式 ---
        self._write_cmd(0x11)  # Sleep Out
        time.sleep_ms(120)

        # --- Normal Display Mode ON (关键！) ---
        self._write_cmd(0x13)
        time.sleep_ms(10)

        # --- Porch control ---
        self._write_cmd(0xB2)
        self._write_data_bytes(b'\x0C\x0C\x00\x33\x33')

        # --- Gate control ---
        self._write_cmd(0xB7)
        self._write_data(0x35)

        # --- VCOMS setting ---
        self._write_cmd(0xBB)
        self._write_data(0x28)

        # --- Power control 1 ---
        self._write_cmd(0xC0)
        self._write_data(0x2C)

        # --- Power control 2 ---
        self._write_cmd(0xC2)
        self._write_data_bytes(b'\x01\xFF')

        # --- Power control 3 ---
        self._write_cmd(0xC3)
        self._write_data(0x10)

        # --- Power control 4 ---
        self._write_cmd(0xC4)
        self._write_data(0x20)

        # --- VCOM control 1 ---
        self._write_cmd(0xC6)
        self._write_data(0x0F)

        # --- Power control A ---
        self._write_cmd(0xD0)
        self._write_data_bytes(b'\xA4\xA1')

        # --- Gamma 正向 ---
        self._write_cmd(0xE0)
        self._write_data_bytes(b'\xD0\x00\x02\x07\x0A\x28\x32\x44\x42\x06\x0E\x12\x14\x17')

        # --- Gamma 反向 ---
        self._write_cmd(0xE1)
        self._write_data_bytes(b'\xD0\x00\x02\x07\x0A\x28\x31\x54\x47\x0E\x1C\x17\x1B\x1E')

        # --- 像素格式设置 ---
        self._write_cmd(0x3A)
        time.sleep_ms(40)
        self._write_data(
            0x55 if self.__color_bit == 16
            else (0x66 if self.__color_bit == 18 else 0x77)
        )
      
        # --- 显示方向 ---
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        self._write_cmd(0x36)
        self._write_data(val | 0x08)

        # --- 显示反转与显示开 ---
        self._write_cmd(0x29)  # Display on
        time.sleep_ms(120)


        self.fill(self.color.基础灰阶.黑)
        return self
  