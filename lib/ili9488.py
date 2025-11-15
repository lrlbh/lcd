import time

import lcd


class ILI9488(lcd.LCD):
    def _init(self):
        if self.__color_bit == 16:
            raise ValueError("好像没有16bit，忘记了 --> 18 or 24")

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
        self._write_data_bytes(b"\x02\x22\x3b")

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
        elif self.__color_bit == 18:
            self._write_data(0x66)
        elif self.__color_bit == 24:
            self._write_data(0x77)

        # === 接口模式控制 ===
        self._write_cmd(0xB0)
        self._write_data(0x00)

        # === 其它寄存器 ===
        self._write_cmd(0xB7)
        self._write_data(0xC6)

        self._write_cmd(0xF7)
        self._write_data_bytes(b"\xa9\x51\x2c\x82")  # 调整控制

        # === Gamma 正极 ===
        self._write_cmd(0xE0)
        self._write_data_bytes(
            b"\x00\x08\x0c\x02\x0e\x04\x30\x45\x47\x04\x0c\x0a\x2e\x34\x0f"
        )

        # === Gamma 负极 ===
        self._write_cmd(0xE1)
        self._write_data_bytes(
            b"\x00\x11\x0d\x01\x0f\x05\x39\x36\x51\x06\x0f\x0d\x33\x37\x0f"
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
