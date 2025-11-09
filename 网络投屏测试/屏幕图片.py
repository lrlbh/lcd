import cv2
from matplotlib.pylab import rand
import numpy as np
from PIL import ImageGrab
import socket
import time
import threading
import struct



# 截图并且处理数据
# 耗时主要是截图，平均应该要10多ms，有时20、30+ms
# 对了现在截图的是800 * 600,忘记尝试更好方便是否会耗时增加
def get_image(w,h,bit):
    
    # 截图
    img = ImageGrab.grab()

    # 图片转3维数组，最内层RGB,中间层单行数据，外层所有行
    img = np.array(img)

    # 缩放
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)

    if bit == 16:
        # 转 uint16 (为后续左移准备)
        img16 = img.astype(np.uint16)

        #  拆分通道
        r = img16[:, :, 0]  # R
        g = img16[:, :, 1]  # G
        b = img16[:, :, 2]  # B

        # 转换到 RGB565
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

        # 下面操作除了转bytes，都是为了适配特殊的逻辑列刷新使用的
        # 如果正常使用不需要操作
        # 翻转图片
        rgb565 = np.flipud(rgb565)

        # 大端，列增长，转bytes
        return rgb565.astype('>u2').ravel(order='F').tobytes()
        
    img = np.flipud(img)
    return  np.ascontiguousarray(img.transpose(1, 0, 2)).tobytes()

   



def handle_client(conn, addr):
    print(f"[PC] ✅ 已连接: {addr}")

    data = conn.recv(12)
    if len(data) < 12:
        raise ValueError("数据长度不足 12 字节")

    # 解包格式：H H B 7x
    # H=uint16, B=uint8, 7x=跳过7字节
    w, h, bit = struct.unpack(">HHB7x", data)   # > 表示大端 
    print(f"收到参数：w={w}, h={h}, bit={bit}")
    try:
        while True:
            s = time.time() * 1000
            data = get_image(w,h,bit)
            t = round( time.time() * 1000 - s)
            conn.sendall(data)
            fps = round(1000 / (time.time()*1000 -s), 2)
            print(f"{addr[0]} 帧率: {fps} 此帧截图浪费时间ms: {t}")
    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[PC] ⚠️ 连接异常，已断开: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


HOST = "0.0.0.0"   
PORT = 8848        

# 1️⃣ 创建 TCP 套接字
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
server.settimeout(0.1) # 简单兼容下，con+c


print(f"[PC] 等待客户端连接 {HOST}:{PORT} ...")


while True:
    try:
        conn, addr = server.accept()    
    except TimeoutError:    
        continue

    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.daemon = True 
    t.start()






server.close()