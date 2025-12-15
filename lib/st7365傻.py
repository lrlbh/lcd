import time
import lcd


# 默认初始化可用，不过下次打算使用这款屏幕，所以测试商家校准参数
# code里面找到的都是ili9488，st7796之类的乱七八糟的初始化，随便试一个看看
class ST7365傻(lcd.LCD):
    def _init(self):

        # === 1. 硬件复位 ===
        if self._rst is None:
            self._write_cmd(0x01)  # 软件复位
        else:
            self._rst.value(0)
            time.sleep_ms(20)
            self._rst.value(1)
            time.sleep_ms(20)
            self._rst.value(0)
            time.sleep_ms(20)
            self._rst.value(1)
        time.sleep_ms(200)

        # === 2. 退出睡眠模式 ===
        self._write_cmd(0x11)  # Sleep Out
        time.sleep_ms(120)

        # === 3. 【整合】内存访问控制（屏幕旋转） ===
        # 应用您自定义的旋转映射逻辑
        val = [0x00, 0x60, 0xC0, 0xA0][self._旋转]
        val ^= 0x40  # 修正左右镜像
        val |= 0x08  # 修正颜色顺序（R/B 反）
        self._write_cmd(0x36)  # Memory Data Access Control
        self._write_data(val)

        # === 4. 【整合】像素格式（颜色位深判断） ===
        self._write_cmd(0x3A)  # Interface Pixel Format
        if self.__color_bit == 16:
            self._write_data(0x55)  # RGB565
        elif self.__color_bit == 18:
            self._write_data(0x66)  # RGB666
        else:
            self._write_data(0x77)  # RGB888

        # === 5. 进入扩展命令集（配置核心参数） ===
        self._write_cmd(0xF0)
        self._write_data(0xC3)
        self._write_cmd(0xF0)
        self._write_data(0x96)

        # === 6. 显示与门控配置 ===
        self._write_cmd(0xB4)  # Display Function Control
        self._write_data(0x01)
        self._write_cmd(0xB7)  # Gate Control
        self._write_data(0xC6)

        # === 7. 电源与VCOM控制 ===
        self._write_cmd(0xB9)  # VCOM Control (2字节)
        self._write_data(0x02)
        self._write_data(0xE0)
        self._write_cmd(0xC0)  # Power Control 1 (2字节)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_cmd(0xC1)  # Power Control 2
        self._write_data(0x1B)
        self._write_cmd(0xC2)  # Power Control 3
        self._write_data(0xA7)
        self._write_cmd(0xC5)  # VCOM Control
        self._write_data(0x00)

        # === 8. 驱动时序控制 ===
        self._write_cmd(0xE8)
        self._write_data_bytes(b"\x40\x8a\x00\x00\x33\x19\xa5\x33")

        # === 9. Gamma 校正 ===
        self._write_cmd(0xE0)  # Positive Gamma
        self._write_data_bytes(
            b"\xf0\x09\x0f\x0d\x0d\x1c\x3d\x44\x55\x39\x18\x18\x36\x39"
        )
        self._write_cmd(0xE1)  # Negative Gamma
        self._write_data_bytes(
            b"\xf0\x09\x0f\x09\x08\x01\x31\x33\x46\x09\x13\x13\x2a\x31"
        )

        # === 10. 退出扩展命令集 ===
        self._write_cmd(0xF0)
        self._write_data(0x3C)
        self._write_cmd(0xF0)
        self._write_data(0x69)
        time.sleep_ms(120)

        # === 11. 显示控制 ===
        self._write_cmd(0x35)  # 撕裂效应控制 (Tearing Effect)
        self._write_data(0x00)  # 禁用
        self._write_cmd(0x21)  # 显示反转 (Display Inversion ON)，按需启用

        self._write_cmd(0x29)  # Display ON
        time.sleep_ms(50)

        # === 12. 设置显示区域 (480x320) ===
        self._write_cmd(0x2A)  # 列地址设置 (X方向: 0-319)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x01)
        self._write_data(0x3F)  # 319 = 0x013F

        self._write_cmd(0x2B)  # 行地址设置 (Y方向: 0-479)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x01)
        self._write_data(0xDF)  # 479 = 0x01DF

        self._write_cmd(0x2C)  # Memory Write，准备写入数据

        # === 初始清屏 ===
        self.fill(self.color.黑)
        return self
