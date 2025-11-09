#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import socket
import struct
from PIL import Image, ImageSequence

def rgb888_to_rgb565_bytes(img_rgb):
    """
    将RGB888的Pillow图像转换为RGB565字节序列（大端）
    输出顺序改为：从上到下、一列一列增长（列优先）
    """
    w, h = img_rgb.size
    px = img_rgb.load()
    out = bytearray(w * h * 2)
    j = 0
    for x in range(w):          # 列优先
        for y in range(h):      # 每列从上到下
            r, g, b = px[x, y]
            v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out[j] = (v >> 8) & 0xFF
            out[j + 1] = v & 0xFF
            j += 2
    return bytes(out)

def load_gif_as_rgb565(gif_path, out_w, out_h, keep_aspect=False):
    """
    读取GIF全部帧，统一到 out_w x out_h，转为RGB565字节。
    keep_aspect=True时按等比例缩放并居中填充黑边；否则直接拉伸。
    返回: (frames_bytes_list, frame_count, each_frame_len_bytes)
    """
    frames = []
    with Image.open(gif_path) as im:
        for frame in ImageSequence.Iterator(im):
            # 转成RGB
            f = frame.convert("RGB")
            if (f.width, f.height) != (out_w, out_h):
                if keep_aspect:
                    # 等比缩放 + 黑边
                    f = f.copy()
                    f.thumbnail((out_w, out_h), Image.LANCZOS)
                    # 居中贴到黑底
                    canvas = Image.new("RGB", (out_w, out_h), (0, 0, 0))
                    x = (out_w - f.width) // 2
                    y = (out_h - f.height) // 2
                    canvas.paste(f, (x, y))
                    f = canvas
                else:
                    # 直接拉伸到目标分辨率
                    f = f.resize((out_w, out_h), Image.LANCZOS)
            frames.append(rgb888_to_rgb565_bytes(f))

    frame_count = len(frames)
    each_len = out_w * out_h * 2
    return frames, frame_count, each_len

def build_payload(frames):
    """
    将所有帧拼接成 payload，并构造 8 字节头：
    [4B 总数据长度] [4B 总图片数] [所有帧数据...]
    注意：总数据长度只计算“所有帧数据”的字节数，不含这8字节头本身。
    """
    data = b"".join(frames)
    total_len = len(data)
    count = len(frames)
    header = struct.pack(">II", total_len, count)  # 大端 uint32
    return header + data

def run_server(host, port, payload):
    """
    简单TCP服务器：单连接，收到任意数据后把payload一次性发送，然后关闭。
    """
    print(f"[TCP] Listening on {host}:{port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 提升复用性，脚本重启可立即绑定
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print(f"[TCP] Connected from {addr}")
            # 等待客户端发送任意请求字节
            _ = conn.recv(1024)
            print(f"[TCP] Sending {len(payload)} bytes ...")
            conn.sendall(payload)
            print("[TCP] Done, closing connection.")

def main():
    parser = argparse.ArgumentParser(
        description="将GIF转为RGB565并通过TCP发送：4字节总数据长度 + 4字节图片总数 + 所有帧数据"
    )
    parser.add_argument("gif", help="输入GIF路径")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9001, help="监听端口 (默认 9001)")
    parser.add_argument("--width", type=int, default=320, help="输出宽度 (默认 320)")
    parser.add_argument("--height", type=int, default=240, help="输出高度 (默认 240)")
    parser.add_argument("--keep-aspect", action="store_true",
                        help="保持纵横比并加黑边居中（默认关闭，直接拉伸）")
    args = parser.parse_args()

    frames, count, each_len = load_gif_as_rgb565(
        args.gif, args.width, args.height, keep_aspect=args.keep_aspect
    )

    if count == 0:
        raise SystemExit("未读取到任何帧。请确认GIF文件有效。")

    payload = build_payload(frames)

    # 打印关键信息，便于接收端解析
    print("========== 打包信息 ==========")
    print(f"帧数: {count}")
    print(f"分辨率: {args.width}x{args.height}")
    print(f"单帧字节: {each_len} (={args.width}*{args.height}*2)")
    print(f"总帧数据字节: {len(payload) - 8}")
    print(f"发送总字节(含8字节头): {len(payload)}")
    print("头格式: [4B 总数据长度] [4B 图片总数]   (均为大端uint32)")
    print("=============================")

    run_server(args.host, args.port, payload)

if __name__ == "__main__":
    main()
  