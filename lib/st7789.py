import time
from machine import Pin
import lcd
import asyncio


class ST7789(lcd.LCD):
    def __init__(
        self,
        spi,
        cs,
        dc,
        rst,
        bl,
        旋转=3,
        color_bit=16,
        w=240,
        h=320,
        逆CS=False,
    ):
        # 初始化基类
        super().__init__(
            spi,
            cs,
            dc,
            rst,
            bl,
            旋转,
            color_bit,
            w,
            h,
            逆CS,
        )

    def _init(self):
        """
        ST7789 初始化流程（完全按官方推荐顺序）
        """

        # === 软件复位 ===
        # 命令 0x01：Software Reset
        # 将所有寄存器恢复为默认值（效果与硬件复位相同）
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            time.sleep_ms(10)
            self._rst.value(1)

        time.sleep_ms(120)  # 等待 120ms 以上

        # === 退出睡眠模式 ===
        # 命令 0x11：Sleep Out
        # 让内部偏压电路和时钟启动。
        self._write_cmd(0x11)
        time.sleep_ms(120)

        # === Porch 设置 ===
        # 命令 0xB2：设置前后消隐时序
        # self._write_cmd(0xB2)
        # self._write_data_bytes(b'\x0C\x0C\x00\x33\x33')
        # self._write_cmd(0xB2)
        # # 前后消隐都加大，比如从 0x0C → 0x14 或更大
        # self._write_data_bytes(b'\x14\x14\x00\x33\x33')

        # 1) 先关 TE
        # self._write_cmd(0x34)                   # TEOFF

        # # 2) 清/设置 TE 扫描线（可设为 0 行）
        # self._write_cmd(0x44)                   # SET_TEAR_SCANLINE
        # self._write_data_bytes(b'\x00\x00')     # line = 0（帧顶）

        # self._write_cmd(0x35)  # TEON，启用 TE 输出
        # self._write_data(0x00)

        # === Gate 控制 ===
        # 命令 0xB7：门极控制寄存器
        self._write_cmd(0xB7)
        self._write_data(0x35)

        # === VCOM 设置 ===
        # 命令 0xBB：设置液晶公共电压
        self._write_cmd(0xBB)
        self._write_data(0x19)

        # === LCM 控制 ===
        # 命令 0xC0：驱动能力控制
        self._write_cmd(0xC0)
        self._write_data(0x2C)

        # === 电源控制 ===
        # 命令 0xC2, 0xC3, 0xC4：设置偏置电压
        self._write_cmd(0xC2)
        self._write_data(0x01)
        self._write_cmd(0xC3)
        self._write_data(0x12)
        self._write_cmd(0xC4)
        self._write_data(0x20)

        # === 帧率控制 ===
        # 命令 0xC6：设置刷新率（一般 60Hz）
        self._write_cmd(0xC6)
        self._write_data(0x0F)

        # === Gamma 调整 ===
        # 命令 0xE0, 0xE1：正向 / 反向 Gamma 曲线
        # self._write_cmd(0xE0)
        # self._write_data_bytes(b'\xD0\x04\x0D\x11\x13\x2B\x3F\x54\x4C\x18\x0D\x0B\x1F\x23')
        # self._write_cmd(0xE1)
        # self._write_data_bytes(b'\xD0\x04\x0C\x11\x13\x2C\x3F\x44\x51\x2F\x1F\x1F\x20\x23')

        # === 显示方向控制 ===
        # 命令 0x36：控制扫描方向、RGB/BGR 顺序
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        self._write_cmd(0x36)
        self._write_data(val)

        # === 像素格式 ===
        # 命令 0x3A：设置颜色深度
        # 0x55 -> RGB565, 0x66 -> RGB666
        self._write_cmd(0x3A)
        self._write_data(0x55 if self.__color_bit == 16 else 0x66)

        # === 开显示 ===
        # 命令 0x29：Display ON
        self._write_cmd(0x29)
        time.sleep_ms(60)

        # === 反色显示（可选）===
        # 命令 0x21：Inversion ON
        self._write_cmd(0x21)

        # === 清屏 ===
        # 使用基础灰阶黑色填充整个屏幕
        self.fill(self.color.黑)
        return self

    async def init_async(self):
        """
        异步版本初始化流程（适配 asyncio）
        """
        # === 软件复位 ===
        if self._rst is None:
            self._write_cmd(0x01)
        else:
            self._rst.value(0)
            await asyncio.sleep_ms(10)
            self._rst.value(1)

        await asyncio.sleep_ms(120)

        # === 退出睡眠模式 ===
        self._write_cmd(0x11)
        await asyncio.sleep_ms(120)

        # === Porch 设置 ===
        self._write_cmd(0xB2)
        self._write_data_bytes(b"\x0c\x0c\x00\x33\x33")

        # === Gate 控制 ===
        self._write_cmd(0xB7)
        self._write_data(0x35)

        # === VCOM 设置 ===
        self._write_cmd(0xBB)
        self._write_data(0x19)

        # === LCM 控制 ===
        self._write_cmd(0xC0)
        self._write_data(0x2C)

        # === 电源控制 ===
        self._write_cmd(0xC2)
        self._write_data(0x01)
        self._write_cmd(0xC3)
        self._write_data(0x12)
        self._write_cmd(0xC4)
        self._write_data(0x20)

        # === 帧率控制 ===
        self._write_cmd(0xC6)
        self._write_data(0x0F)

        # === 显示方向控制 ===
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        self._write_cmd(0x36)
        self._write_data(val)

        # === 像素格式 ===
        self._write_cmd(0x3A)
        self._write_data(0x55 if self.__color_bit == 16 else 0x66)

        # === 开显示 ===
        self._write_cmd(0x29)
        await asyncio.sleep_ms(60)

        # === 反色显示 ===
        self._write_cmd(0x21)

        # === 清屏 ===
        self.fill(self.color.黑)
        return self
