import time
from machine import Pin
import lcd


class ST7796(lcd.LCD):
    def __init__(
        self,
        spi,
        dc,
        size,
        bl=None,
        rst=None,
        cs=None,
        旋转=3,
        color_bit=16,
        像素缺失=(0, 0, 0, 0),
        逆CS=False,
    ):
        super().__init__(
            spi, dc, size, bl, rst, cs, 旋转, color_bit, 像素缺失, 逆CS
        )

    def _init(self):
        """ST7796 初始化流程（逻辑列刷新版本）"""

        # === 复位 ===
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)

        # === 睡眠解除 ===
        self._write_cmd(0x11)
        time.sleep_ms(120)

        # === 内部命令页切换 ===
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        val ^= 0x40  # 修正左右镜像
        val |= 0x08  # 修正颜色顺序（R/B 反）
        self._write_cmd(0x36)
        self._write_data(val)

        # === 像素格式 === 
        self._write_cmd(0x3A)
        if self.__color_bit == 16:
            self._write_data(0x55)  # RGB565
        elif self.__color_bit in [18, 24]:
            self._write_data(0x66)  # RGB666
        else:
            self._write_data(0x55)

        # === 显示反相控制 ===
        self._write_cmd(0xB4)
        self._write_data(0x01)

        # === 显示功能控制 ===
        self._write_cmd(0xB7)
        self._write_data(0xC6)

        # === 电压控制 ===
        self._write_cmd(0xE8)
        self._write_data_bytes(b"\x40\x8A\x00\x00\x29\x19\xA5\x33")

        # === 电流控制 ===
        self._write_cmd(0xC1)
        self._write_data(0x06)

        self._write_cmd(0xC2)
        self._write_data(0xA7)

        self._write_cmd(0xC5)
        self._write_data(0x18)

        # === Gamma 正极 ===
        self._write_cmd(0xE0)
        self._write_data_bytes(
            b"\xF0\x09\x0B\x06\x04\x15\x2F\x54\x42\x3C\x17\x14\x18\x1B"
        )

        # === Gamma 负极 ===
        self._write_cmd(0xE1)
        self._write_data_bytes(
            b"\xF0\x09\x0B\x06\x04\x03\x2D\x43\x42\x3B\x16\x14\x17\x1B"
        )

        # === 恢复默认页 ===
        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)

        # === 延时后开显示 ===
        time.sleep_ms(120)
        self._write_cmd(0x21)  # 反显 ON
        self._write_cmd(0x29)  # 显示 ON
        time.sleep_ms(60)

        # === 清屏 ===
        self.fill(self.color.黑)
        return self
