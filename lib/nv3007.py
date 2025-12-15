import time
import lcd


class NV3007(lcd.LCD):
    def _init(self):
        """NV3006A1N/NV3007A 初始化流程"""

        # === 复位 ===
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)

        # === 初始化序列 ===
        self._write_cmd(0xFF)
        self._write_data(0xA5)

        self._write_cmd(0x9A)
        self._write_data(0x08)
        self._write_cmd(0x9B)
        self._write_data(0x08)
        self._write_cmd(0x9C)
        self._write_data(0xB0)
        self._write_cmd(0x9D)
        self._write_data(0x16)
        self._write_cmd(0x9E)
        self._write_data(0xC4)

        # 2字节数据
        self._write_cmd(0x8F)
        self._write_data(0x55)
        self._write_data(0x04)

        self._write_cmd(0x84)
        self._write_data(0x90)
        self._write_cmd(0x83)
        self._write_data(0x7B)
        self._write_cmd(0x85)
        self._write_data(0x33)

        # 一系列寄存器设置
        regs = [
            (0x60, 0x00),
            (0x70, 0x00),
            (0x61, 0x02),
            (0x71, 0x02),
            (0x62, 0x04),
            (0x72, 0x04),
            (0x6C, 0x29),
            (0x7C, 0x29),
            (0x6D, 0x31),
            (0x7D, 0x31),
            (0x6E, 0x0F),
            (0x7E, 0x0F),
            (0x66, 0x21),
            (0x76, 0x21),
            (0x68, 0x3A),
            (0x78, 0x3A),
            (0x63, 0x07),
            (0x73, 0x07),
            (0x64, 0x05),
            (0x74, 0x05),
            (0x65, 0x02),
            (0x75, 0x02),
            (0x67, 0x23),
            (0x77, 0x23),
            (0x69, 0x08),
            (0x79, 0x08),
            (0x6A, 0x13),
            (0x7A, 0x13),
            (0x6B, 0x13),
            (0x7B, 0x13),
            (0x6F, 0x00),
            (0x7F, 0x00),
            (0x50, 0x00),
            (0x52, 0xD6),
            (0x53, 0x08),
            (0x54, 0x08),
            (0x55, 0x1E),
            (0x56, 0x1C),
        ]
        for cmd, dat in regs:
            self._write_cmd(cmd)
            self._write_data(dat)

        # === GOA映射选择 ===
        self._write_cmd(0xA0)
        self._write_data(0x2B)
        self._write_data(0x24)
        self._write_data(0x00)

        goa_regs = [
            (0xA1, 0x87),
            (0xA2, 0x86),
            (0xA5, 0x00),
            (0xA6, 0x00),
            (0xA7, 0x00),
            (0xA8, 0x36),
            (0xA9, 0x7E),
            (0xAA, 0x7E),
            (0xB9, 0x85),
            (0xBA, 0x84),
            (0xBB, 0x83),
            (0xBC, 0x82),
            (0xBD, 0x81),
            (0xBE, 0x80),
            (0xBF, 0x01),
            (0xC0, 0x02),
            (0xC1, 0x00),
            (0xC2, 0x00),
            (0xC3, 0x00),
            (0xC4, 0x33),
            (0xC5, 0x7E),
            (0xC6, 0x7E),
        ]
        for cmd, dat in goa_regs:
            self._write_cmd(cmd)
            self._write_data(dat)

        # 多字节数据
        self._write_cmd(0xC8)
        self._write_data(0x33)
        self._write_data(0x33)

        self._write_cmd(0xC9)
        self._write_data(0x68)
        self._write_cmd(0xCA)
        self._write_data(0x69)
        self._write_cmd(0xCB)
        self._write_data(0x6A)
        self._write_cmd(0xCC)
        self._write_data(0x6B)

        self._write_cmd(0xCD)
        self._write_data(0x33)
        self._write_data(0x33)

        self._write_cmd(0xCE)
        self._write_data(0x6C)
        self._write_cmd(0xCF)
        self._write_data(0x6D)
        self._write_cmd(0xD0)
        self._write_data(0x6E)
        self._write_cmd(0xD1)
        self._write_data(0x6F)

        # 2字节数据
        self._write_cmd(0xAB)
        self._write_data(0x03)
        self._write_data(0x67)

        self._write_cmd(0xAC)
        self._write_data(0x03)
        self._write_data(0x6B)

        self._write_cmd(0xAD)
        self._write_data(0x03)
        self._write_data(0x68)

        self._write_cmd(0xAE)
        self._write_data(0x03)
        self._write_data(0x6C)

        # 继续单字节数据
        self._write_cmd(0xB3)
        self._write_data(0x00)
        self._write_cmd(0xB4)
        self._write_data(0x00)
        self._write_cmd(0xB5)
        self._write_data(0x00)
        self._write_cmd(0xB6)
        self._write_data(0x32)
        self._write_cmd(0xB7)
        self._write_data(0x7E)
        self._write_cmd(0xB8)
        self._write_data(0x7E)

        # E系列寄存器
        self._write_cmd(0xE0)
        self._write_data(0x00)

        self._write_cmd(0xE1)
        self._write_data(0x03)
        self._write_data(0x0F)

        self._write_cmd(0xE2)
        self._write_data(0x04)
        self._write_cmd(0xE3)
        self._write_data(0x01)
        self._write_cmd(0xE4)
        self._write_data(0x0E)
        self._write_cmd(0xE5)
        self._write_data(0x01)
        self._write_cmd(0xE6)
        self._write_data(0x19)
        self._write_cmd(0xE7)
        self._write_data(0x10)
        self._write_cmd(0xE8)
        self._write_data(0x10)
        self._write_cmd(0xEA)
        self._write_data(0x12)
        self._write_cmd(0xEB)
        self._write_data(0xD0)
        self._write_cmd(0xEC)
        self._write_data(0x04)
        self._write_cmd(0xED)
        self._write_data(0x07)
        self._write_cmd(0xEE)
        self._write_data(0x07)
        self._write_cmd(0xEF)
        self._write_data(0x09)
        self._write_cmd(0xF0)
        self._write_data(0xD0)
        self._write_cmd(0xF1)
        self._write_data(0x0E)

        # 配置参数
        self._write_cmd(0xF9)
        self._write_data(0x17)

        self._write_cmd(0xF2)
        self._write_data(0x2C)
        self._write_data(0x1B)
        self._write_data(0x0B)
        self._write_data(0x20)

        # 1 dot配置
        self._write_cmd(0xE9)
        self._write_data(0x29)
        self._write_cmd(0xEC)
        self._write_data(0x04)

        # TE配置
        self._write_cmd(0x35)
        self._write_data(0x00)

        self._write_cmd(0x44)
        self._write_data(0x00)
        self._write_data(0x10)

        self._write_cmd(0x46)
        self._write_data(0x10)

        self._write_cmd(0xFF)
        self._write_data(0x00)

        # === 像素格式 ===
        self._write_cmd(0x3A)
        if self.__color_bit == 16:
            self._write_data(0x05)  # RGB565
        elif self.__color_bit == 18:
            self._write_data(0x06)  # RGB666
        else:
            self._write_data(0x07)  # RGB888

        # === 显示控制 ===
        self._write_cmd(0x11)
        time.sleep_ms(320)

        self._write_cmd(0x29)
        time.sleep_ms(300)

        # 如果需要，添加旋转设置
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]

        self._write_cmd(0x36)
        self._write_data(val)

        # === 清屏 ===
        self.fill(self.color.黑)
        return self
