import asyncio
import time
import lcd

# 便宜的4寸屏幕第一行像素只有在从上往下看的时候能露出1/3，其他角度看不到
# 商家提供的校准代码，没啥鸟用参数也对不上，不知道他从哪里复制来的
class ST7796_便宜(lcd.LCD):
    """ST7796S + BOE 3.52寸 (Gamma2.2) 初始化版本"""

    def _init(self):
        """初始化显示驱动（固定参数版本，不对外暴露反色/RGB/镜像选项）"""

        # === 复位 ===
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(50)
            self._rst.value(1)
        time.sleep_ms(150)

        # === 退出睡眠模式 ===
        self._write_cmd(0x11)
        time.sleep_ms(120)

        # === 内存访问控制 ===
        # 对应 0x36, 数据 0x48
        # MY=0, MX=1, MV=0, ML=0, BGR=1, MH=0
        self._write_cmd(0x36)
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        # 左右镜像（MX）控制
        val ^= 0x40  # 取反 MX 位（D6）
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

        # === 命令页解锁 ===
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        # === 显示/电源配置 ===
        self._write_cmd(0xB4)
        self._write_data(0x01)

        self._write_cmd(0xB7)
        self._write_data(0xC6)

        self._write_cmd(0xC0)
        self._write_data(0x80)
        self._write_data(0x45)

        self._write_cmd(0xC1)
        self._write_data(0x0F)

        self._write_cmd(0xC2)
        self._write_data(0xA7)

        self._write_cmd(0xC5)
        self._write_data(0x0A)

        # === 时序控制 ===
        self._write_cmd(0xE8)
        self._write_data(0x40)
        self._write_data(0x8A)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x29)
        self._write_data(0x19)
        self._write_data(0xA5)
        self._write_data(0x33)

        # === Gamma 调整 ===
        # 正伽马 (E0)
        self._write_cmd(0xE0)
        for v in [0xD0, 0x08, 0x0F, 0x06, 0x06, 0x33, 0x30, 0x33, 
                  0x47, 0x17, 0x13, 0x13, 0x2B, 0x31]:
            self._write_data(v)

        # 负伽马 (E1)
        self._write_cmd(0xE1)
        for v in [0xD0, 0x0A, 0x11, 0x0B, 0x09, 0x07, 0x2F, 0x33,
                  0x47, 0x38, 0x15, 0x16, 0x2C, 0x32]:
            self._write_data(v)

        # === 命令页还原 ===
        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)

        time.sleep_ms(120)

        # === 反色显示开启 ===
        self._write_cmd(0x21)

        # === 打开显示 ===
        self._write_cmd(0x29)
        time.sleep_ms(60)

        # === 可选：清屏为黑 ===
        # self.fill(self.color.黑)
        return self

    async def _init_async(self):
        """初始化显示驱动（固定参数版本，不对外暴露反色/RGB/镜像选项）"""

        # === 复位 === 
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            await asyncio.sleep_ms(50)
            self._rst.value(1)
        await asyncio.sleep_ms(150)

        # === 退出睡眠模式 ===
        self._write_cmd(0x11)
        await asyncio.sleep_ms(120)

        # === 内存访问控制 ===
        # 对应 0x36, 数据 0x48
        # MY=0, MX=1, MV=0, ML=0, BGR=1, MH=0
        self._write_cmd(0x36)
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        # 左右镜像（MX）控制
        val ^= 0x40  # 取反 MX 位（D6）
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

        # === 命令页解锁 ===
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        # === 显示/电源配置 ===
        self._write_cmd(0xB4)
        self._write_data(0x01)

        self._write_cmd(0xB7)
        self._write_data(0xC6)

        self._write_cmd(0xC0)
        self._write_data(0x80)
        self._write_data(0x45)

        self._write_cmd(0xC1)
        self._write_data(0x0F)

        self._write_cmd(0xC2)
        self._write_data(0xA7)

        self._write_cmd(0xC5)
        self._write_data(0x0A)

        # === 时序控制 ===
        self._write_cmd(0xE8)
        self._write_data(0x40)
        self._write_data(0x8A)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x29)
        self._write_data(0x19)
        self._write_data(0xA5)
        self._write_data(0x33)

        # === Gamma 调整 ===
        # 正伽马 (E0)
        self._write_cmd(0xE0)
        for v in [0xD0, 0x08, 0x0F, 0x06, 0x06, 0x33, 0x30, 0x33, 
                  0x47, 0x17, 0x13, 0x13, 0x2B, 0x31]:
            self._write_data(v)

        # 负伽马 (E1)
        self._write_cmd(0xE1)
        for v in [0xD0, 0x0A, 0x11, 0x0B, 0x09, 0x07, 0x2F, 0x33,
                  0x47, 0x38, 0x15, 0x16, 0x2C, 0x32]:
            self._write_data(v)

        # === 命令页还原 ===
        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)

        await asyncio.sleep_ms(120)

        # === 反色显示开启 ===
        self._write_cmd(0x21)

        # === 打开显示 ===
        self._write_cmd(0x29)
        await asyncio.sleep_ms(60)

        # === 可选：清屏为黑 ===
        # self.fill(self.color.黑)
        return self