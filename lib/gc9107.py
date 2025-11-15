import time
import lcd
import asyncio


class GC9107(lcd.LCD):


    def _init(self, 反色=True, RGB=True):
        # --- 复位 ---
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(10)
            self._rst.value(1)
        time.sleep_ms(120)

        # --- 解锁内部页 (GC9107A 关键) ---
        self._write_cmd(0xFE)
        self._write_cmd(0xEF)

        # --- 按模组推荐值：帧率/时序/电压/伽马（示例值，沿用你贴的） ---
        for cmd, data in [
            (0xB0, b"\xc0"),
            (0xB2, b"\x2f"),
            (0xB3, b"\x03"),
            (0xB6, b"\x19"),
            (0xB7, b"\x01"),
            (0xAC, b"\xcb"),
            (0xAB, b"\x0e"),
            (0xB4, b"\x04"),
            (0xA8, b"\x19"),
            (0xB8, b"\x08"),
            (0xE8, b"\x24"),
            (0xE9, b"\x48"),
            (0xEA, b"\x22"),
            (0xC6, b"\x30"),
            (0xC7, b"\x18"),
        ]:
            self._write_cmd(cmd)
            self._write_data_bytes(data)

        # 伽马表
        self._write_cmd(0xF0)
        self._write_data_bytes(b"\x1f\x28\x04\x3e\x2a\x2e\x20\x00\x0c\x06\x00\x1c\x1f\x0f")
        self._write_cmd(0xF1)
        self._write_data_bytes(b"\x00\x2d\x2f\x3c\x6f\x1c\x0b\x00\x00\x00\x07\x0d\x11\x0f")

        # --- 像素格式 ---
        self._write_cmd(0x3A)
        if self.__color_bit == 16:
            self._write_data(0x05)  # 16bpp
        elif self.__color_bit == 18:
            self._write_data(0x06)  # 18bpp
        else:
            self._write_data(0x06) 

        # --- 扫描方向 ---
        mad = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        mad |= 0x08  # BGR
        self._write_cmd(0x36)
        self._write_data(mad)

        # --- 退出睡眠 & 开显示 ---
        self._write_cmd(0x11)
        time.sleep_ms(120)

        self._write_cmd(0x20)  
        self._write_cmd(0x29)
        time.sleep_ms(40)
        return self