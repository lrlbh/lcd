import os
from PIL import Image

def get_gif_info(gif_path):
    """读取 GIF 的帧率与分辨率"""
    with Image.open(gif_path) as im:
        width, height = im.size
        duration = im.info.get("duration", 0)
        fps = 0 if duration == 0 else round(1000 / duration, 2)
        return fps, (width, height)

def preview_gif_resized(gif_path, size=(240, 320)):
    """缩放 GIF 并预览"""
    try:
        with Image.open(gif_path) as im:
            frames = []
            for frame in range(im.n_frames):
                im.seek(frame)
                frame_img = im.copy().convert("RGBA")
                frame_img = frame_img.resize(size, Image.LANCZOS)
                frames.append(frame_img)
            # 临时保存为新文件用于预览（系统默认查看器打开）
            temp_path = "_preview.gif"
            frames[0].save(
                temp_path,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=im.info.get("duration", 100),
                disposal=2
            )
            Image.open(temp_path).show()
    except Exception as e:
        print(f"预览 {gif_path} 出错: {e}")

def list_gif_info(directory="."):
    """列出目录下所有GIF的帧率、分辨率，并可预览"""
    print(f"{'文件名':<30} {'帧率(fps)':<10} {'分辨率(宽x高)':<15}")
    print("-" * 60)
    gifs = [f for f in os.listdir(directory) if f.lower().endswith(".gif")]
    for i, filename in enumerate(gifs):
        path = os.path.join(directory, filename)
        fps, (w, h) = get_gif_info(path)
        print(f"{filename:<30} {fps:<10} {w}x{h}")
    print("-" * 60)
    # 预览功能
    if gifs:
        choice = input("是否预览第一个GIF (y/n)? ").strip().lower()
        if choice == "y":
            preview_gif_resized(os.path.join(directory, gifs[0]))

if __name__ == "__main__":
    folder = "."  # 可以改为你的目录
    list_gif_info(folder)
