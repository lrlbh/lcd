import time
import lcd
import asyncio


class GC9A01(lcd.LCD):
 
    def _init(self):

        # === 复位 ===
        if self._rst is None:
            self._write_cmd(0x01)  # 软件复位
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)

        # === 页解锁 / 命令页切换区 ===
        self._write_cmd(0xEF)
        self._write_data_bytes(b"\xEB\x14")
        self._write_cmd(0xFE)
        self._write_cmd(0xEF)
        self._write_cmd(0xEB)
        self._write_data_bytes(b"\x14")

        # === 电压 / 放大器 / 偏置配置区 ===
        cfg = [
            (0x84, b"\x40"),
            (0x85, b"\xFF"),
            (0x86, b"\xFF"),
            (0x87, b"\xFF"),
            (0x88, b"\x0A"),
            (0x89, b"\x21"),
            (0x8A, b"\x00"),
            (0x8B, b"\x80"),
            (0x8C, b"\x01"),
            (0x8D, b"\x01"),
            (0x8E, b"\xFF"),
            (0x8F, b"\xFF"),
        ]
        for cmd, data in cfg:
            self._write_cmd(cmd)
            self._write_data_bytes(data)

        # === 接口控制 ===
        self._write_cmd(0xB6)
        self._write_data_bytes(b"\x00\x20")

        # === 显示方向 ===
        val = [0x08, 0xC8, 0x68, 0xA8][self._旋转]
        self._write_cmd(0x36)
        self._write_data(val)


        # === 像素格式 ===
        self._write_cmd(0x3A)
        if self.__color_bit == 16:
            self._write_data(0x05) 
        elif self.__color_bit in [18,24]:
            self._write_data(0x06)
        # self._write_data(0x03)  


        # === 驱动电流控制 ===
        self._write_cmd(0x90)
        self._write_data_bytes(b"\x08\x08\x08\x08")

        self._write_cmd(0xBD)
        self._write_data(0x06)
        self._write_cmd(0xBC)
        self._write_data(0x00)

        self._write_cmd(0xFF)
        self._write_data_bytes(b"\x60\x01\x04")

        self._write_cmd(0xC3)
        self._write_data(0x13)
        self._write_cmd(0xC4)
        self._write_data(0x13)
        self._write_cmd(0xC9)
        self._write_data(0x22)
        self._write_cmd(0xBE)
        self._write_data(0x11)
        self._write_cmd(0xE1)
        self._write_data_bytes(b"\x10\x0E")
        self._write_cmd(0xDF)
        self._write_data_bytes(b"\x21\x0C\x02")

        # === Gamma 控制 ===
        self._write_cmd(0xF0)
        self._write_data_bytes(b"\x45\x09\x08\x08\x26\x2A")

        self._write_cmd(0xF1)
        self._write_data_bytes(b"\x43\x70\x72\x36\x37\x6F")

        self._write_cmd(0xF2)
        self._write_data_bytes(b"\x45\x09\x08\x08\x26\x2A")

        self._write_cmd(0xF3)
        self._write_data_bytes(b"\x43\x70\x72\x36\x37\x6F")

        # === 电压偏置补偿 ===
        self._write_cmd(0xED)
        self._write_data_bytes(b"\x1B\x0B")
        self._write_cmd(0xAE)
        self._write_data(0x77)
        self._write_cmd(0xCD)
        self._write_data(0x63)

        # === 电压相关控制 ===
        self._write_cmd(0x70)
        self._write_data_bytes(b"\x07\x07\x04\x0E\x0F\x09\x07\x08\x03")

        self._write_cmd(0xE8)
        self._write_data(0x34)

        self._write_cmd(0x62)
        self._write_data_bytes(b"\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70")

        self._write_cmd(0x63)
        self._write_data_bytes(b"\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70")

        self._write_cmd(0x64)
        self._write_data_bytes(b"\x28\x29\xF1\x01\xF1\x00\x07")

        self._write_cmd(0x66)
        self._write_data_bytes(b"\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00")

        self._write_cmd(0x67)
        self._write_data_bytes(b"\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98")

        self._write_cmd(0x74)
        self._write_data_bytes(b"\x10\x85\x80\x00\x00\x4E\x00")

        self._write_cmd(0x98)
        self._write_data_bytes(b"\x3E\x07")

        # === TE/反显/开显示 ===
        self._write_cmd(0x35)  # TEON
        self._write_cmd(0x21)  # INVON

        self._write_cmd(0x11)  # 退出睡眠
        time.sleep_ms(120)

        self._write_cmd(0x29)  # 开显示
        time.sleep_ms(60)

        # === 清屏 ===
        self.fill(self.color.黑)
        return self


