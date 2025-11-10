import os
from lib import udp

def delete_all_except():
    keep_files = {'boot.py'}
    keep_dirs = {'no_delete'}

    udp.send("开始删除根目录下的文件与文件夹...")

    for name in os.listdir('/'):
        path = '/' + name

        try:
            if name in keep_files:
                udp.send(f"保留文件: {name}")
                continue
            if name in keep_dirs:
                udp.send(f"保留目录: {name}")
                continue

            # 判断是文件还是目录
            if os.stat(path)[0] & 0x4000:  # 目录
                udp.send(f"删除目录: {path}")
                delete_dir(path)
            else:  # 文件
                udp.send(f"删除文件: {path}")
                os.remove(path)

        except Exception as e:
            udp.send(f"⚠️ 删除失败: {path}, 错误: {e}")

    udp.send("✅ 删除完成")

def delete_dir(dir_path):
    """递归删除目录"""
    for name in os.listdir(dir_path):
        path = dir_path + '/' + name
        try:
            if os.stat(path)[0] & 0x4000:
                udp.send(f"递归进入目录: {path}")
                delete_dir(path)
            else:
                udp.send(f"删除文件: {path}")
                os.remove(path)
        except Exception as e:
            udp.send(f"⚠️ 删除文件失败: {path}, 错误: {e}")

    try:
        os.rmdir(dir_path)
        udp.send(f"删除空目录: {dir_path}")
    except Exception as e:
        udp.send(f"⚠️ 删除目录失败: {dir_path}, 错误: {e}")

delete_all_except()
