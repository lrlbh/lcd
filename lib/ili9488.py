import time

import lcd

class ILI9488(lcd.LCD):
    def __init__(
        self,
        spi,
        dc,
        size,
        bl=None,
        rst=None,
        cs=None,
        旋转=3,
        color_bit=18,  # 默认 18bit
        像素缺失=(0, 0, 0, 0),
        逆CS=False,
    ):
        super().__init__(
            spi, dc, size, bl, rst, cs, 旋转, color_bit, 像素缺失, 逆CS
        )

    def _init(self):
        if self.__color_bit == 16:
            raise ValueError("没有16bit")
        
        
        # === 复位 ===
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)

        # === 电源控制 ===
        self._write_cmd(0xC0)
        self._write_data_bytes(b"\x17\x15")  # Vreg1out, Verg2out

        self._write_cmd(0xC1)
        self._write_data(0x41)  # VGH/VGL

        self._write_cmd(0xC5)
        self._write_data_bytes(b"\x00\x12\x80")  # VCOM

        # === 帧率控制 ===
        self._write_cmd(0xB1)
        self._write_data(0xA0)  # 60Hz

        # === 显示反相控制 ===
        self._write_cmd(0xB4)
        self._write_data(0x02)  # 2-dot inversion

        # === RGB/MCU 接口控制 ===
        self._write_cmd(0xB6)
        self._write_data_bytes(b"\x02\x22\x3B")

        # === 内存访问方向 ===
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        # if not getattr(self, "_RGB", True):  # 允许控制RGB/BGR
        val |= 0x08
        self._write_cmd(0x36)
        self._write_data(val)

        # === 像素格式 ===
        self._write_cmd(0x3A)
        if self.__color_bit == 16:
            self._write_data(0x55)
        elif self.__color_bit in [18, 24]:
            self._write_data(0x66)  # 18bit 模式
 
        # === 接口模式控制 ===
        self._write_cmd(0xB0)
        self._write_data(0x00)

        # === 其它寄存器 ===
        self._write_cmd(0xB7)
        self._write_data(0xC6)

        self._write_cmd(0xF7) 
        self._write_data_bytes(b"\xA9\x51\x2C\x82")  # 调整控制

        # === Gamma 正极 ===
        self._write_cmd(0xE0)
        self._write_data_bytes(
            b"\x00\x08\x0C\x02\x0E\x04\x30\x45\x47\x04\x0C\x0A\x2E\x34\x0F"
        )

        # === Gamma 负极 ===
        self._write_cmd(0xE1)
        self._write_data_bytes(
            b"\x00\x11\x0D\x01\x0F\x05\x39\x36\x51\x06\x0F\x0D\x33\x37\x0F"
        )

        # === 其它辅助寄存器 ===
        self._write_cmd(0xBE)
        self._write_data_bytes(b"\x00\x04")

        self._write_cmd(0xE9)
        self._write_data(0x00)  # 禁止 24bit 输入

        # === 显示与电源控制 ===
        self._write_cmd(0x21)  # Normal black
        self._write_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        self._write_cmd(0x29)  # Display on
        time.sleep_ms(60)

        # === 清屏 ===
        self.fill(self.color.黑)
        return self
