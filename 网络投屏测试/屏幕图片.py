import cv2
import numpy as np
from PIL import ImageGrab
import socket
import time
import threading
import struct
import dxcam


# 高速截图
camera = dxcam.create(output_idx=0)
camera.start(region=None, target_fps=360, video_mode=True) 
time.sleep(0.3)   # 等待启动

class 像素处理():
    def __init__(self,w,h,bit):
        self.old_img = None
        self.w= w
        self.h = h
        self.bit = bit
        self.byte = 3
        if self.bit == 16:
            self.byte = 2
    
    def 图像转目标像素(self,img,x,y,wl,hl):
        if self.bit == 16:
            # 转 uint16 (为后续左移准备)
            img16 = img.astype(np.uint16)

            #  拆分通道
            r = img16[:, :, 0]  # R
            g = img16[:, :, 1]  # G
            b = img16[:, :, 2]  # B
            

            # 转换到 RGB565
            rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


            # 翻转图片
            rgb565 = np.flipud(rgb565)

            # 大端，列增长，转bytes
            new = rgb565.astype('>u2').ravel(order='F').tobytes()
        else :
            
            img = np.flipud(img)
            new = np.ascontiguousarray(img.transpose(1, 0, 2)).tobytes()

        if len (new) != wl * hl* self.byte:
            print(f"临时查看，{len(new),wl*hl * self.byte}")
            
            
        # === 帧头：x, y, wl, hl（每个4字节，大端） ===
        header = struct.pack(">4I", x, y, wl, hl)

        new = header + new
        # === 帧头 + 像素数据 ===
        return new
    
    def get_image(self):
        while True:
            
            # 截图
            img = camera.get_latest_frame()
            # img = ImageGrab.grab()
            
                
            s = time.time() * 1000
            # 图片转3维数组，最内层RGB,中间层单行数据，外层所有行
            img = np.array(img)
            

            # 缩放
            img = cv2.resize(
                img, (self.w, self.h), interpolation=cv2.INTER_AREA)
            
    
            # 第一次进入，更新帧个帧
            if self.old_img is None:
                self.old_img = img
                return self.图像转目标像素(img,0,0,self.w,self.h) 
             
                               
            # 比较新老图片
            x, y, wl, hl = 0, 0, 0, 0
            # 返回三维RGB，绝对差值
            diff = cv2.absdiff(img, self.old_img)
            
            # 返回二维灰度，绝对差值
            gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            
            # 设置一个阈值，大于阈值表示像素变化了，阈值就是参数二
            _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            # 返回变化坐标
            coords = cv2.findNonZero(mask)
            # x=w变化起点，y=h变化起点
            # wl =w变化宽度，hl = h变化高度
            if coords is not None:
                self.old_img = img
                x, y, wl, hl = cv2.boundingRect(coords)
                # print(f"变化百分比: {(wl * hl) / (self.w * self.h) * 100:.2f}%")
                # 截取图片的变化区域
                img = img[y:y + hl, x:x + wl]
                img = self.图像转目标像素(img,x,y,wl,hl) 
                # print(time.time() * 1000  -s)
                
                return img
            else:
                
                continue    # print("无变化") 



def handle_client(conn, addr):
    print(f"[PC] ✅ 已连接: {addr}")

    data = conn.recv(12)
    if len(data) < 12:
        raise ValueError("数据长度不足 12 字节")

    # 解包格式：H H B 7x
    # H=uint16, B=uint8, 7x=跳过7字节
    w, h, bit = struct.unpack(">HHB7x", data)   # > 表示大端 
    print(f"收到参数：w={w}, h={h}, bit={bit}")

    像素 = 像素处理(w,h,bit)

    i = 0
    try:
        while True:
            i+=1
            s = time.time() * 1000
            data = 像素.get_image()
            # print("获取像素耗时: ",round( time.time() * 1000 - s,2))
            conn.sendall(data)
            print(f"帧率间隔: {time.time() * 1000 -s}")
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