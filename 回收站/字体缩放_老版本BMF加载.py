    # 效率高，缩放效果稍差
    # def draw_text_high_quality(self, 
    #                         text, x=0, y=0, 
    #                         font_size=40, scale=1.0, 
    #                         color=(255, 255, 255), 
    #                         background=None,
    #                         spacing=1):
    #     """
    #     优化后的高质量文本渲染函数
    #     - 使用增强型缓存机制
    #     - 优化背景色处理
    #     - 改进渲染算法
    #     """
    #     # 获取前景色字节
    #     fg_bytes = self.color_fn(color)
    #     bytes_per_pixel = len(fg_bytes)
        
    #     # 获取背景色字节（如果有）
    #     bg_bytes = self.color_fn(background) if background is not None else None
        
    #     # 获取字体集
    #     font_set = self.char.get(font_size, self.char.get(32))
    #     if font_set is None:
    #         raise ValueError(f"Font size {font_size} not available")
        
    #     # 计算行高
    #     char_height = int(font_size * scale)
        
    #     # 批量数据存储
    #     batch_data = bytearray()
    #     batch_regions = []  # (x, y, width, height, data_start, data_end)
        
    #     # 初始化光标
    #     cursor_x = x
        
    #     # 预处理所有字符
    #     for char in text:
    #         # 获取字符数据
    #         char_data = font_set.get(char, font_set.get(" "))
    #         if char_data is None:
    #             bytes_per_row = (font_size + 7) // 8
    #             char_data = b'\x00' * (bytes_per_row * font_size)
            
    #         # 判断是否为ASCII字符
    #         is_ascii = ord(char) < 128
            
    #         # 设置字符宽度和间距
    #         base_width = font_size
    #         char_spacing = spacing - 1 if is_ascii else spacing
    #         char_width = int(base_width * scale)
            
    #         # 边界检查
    #         if cursor_x + char_width > self.width or y + char_height > self.height:
    #             break
            
    #         # 唯一缓存键（包含所有渲染参数）
    #         cache_key = (char, font_size, scale, color, background)
            
    #         # 检查缓存或创建新字符块
    #         if cache_key in self._char_block_cache:
    #             char_block, display_width = self._char_block_cache[cache_key]
    #         else:
    #             char_block, display_width = self._generate_char_block(
    #                 char_data, font_size, char_width, char_height, 
    #                 scale, fg_bytes, bg_bytes, bytes_per_pixel, is_ascii
    #             )
    #             self._char_block_cache[cache_key] = (char_block, display_width)
            
    #         # 添加到批量数据
    #         start_idx = len(batch_data)
    #         batch_data.extend(char_block)
    #         end_idx = len(batch_data)
            
    #         # 存储区域信息
    #         batch_regions.append((
    #             cursor_x, y,
    #             display_width, char_height,
    #             start_idx, end_idx
    #         ))
            
    #         cursor_x += display_width + char_spacing
        
    #     # 批量发送所有字符数据
    #     for region in batch_regions:
    #         x_start, y_start, width, height, start_idx, end_idx = region
    #         self.set_window(x_start, y_start, x_start + width - 1, y_start + height - 1)
    #         self.write_data_bytes(batch_data[start_idx:end_idx])

    # def _generate_char_block(self, char_data, font_size, char_width, char_height, 
    #                         scale, fg_bytes, bg_bytes, bpp, is_ascii):
    #     """
    #     优化后的字符块生成函数
    #     - 使用预计算表加速插值
    #     - 优化背景处理
    #     - 减少内存分配
    #     """
    #     # 计算实际显示宽度（ASCII字符减半）
    #     display_width = char_width // 2 if is_ascii else char_width
        
    #     # 创建字符缓冲区
    #     block_size = display_width * char_height * bpp
    #     char_block = bytearray(block_size)
        
    #     # 如果没有内容，直接返回
    #     if block_size == 0:
    #         return char_block, display_width
        
    #     char_mv = memoryview(char_block)
        
    #     # 如果有背景色，直接填充整个区域
    #     if bg_bytes is not None:
    #         # 优化：一次性填充整个区域
    #         bg_block = bg_bytes * (display_width * char_height)
    #         char_mv[:] = bg_block
        
    #     # 计算每行字节数
    #     bytes_per_row = (font_size + 7) // 8
        
    #     # 预计算权重和索引（加速插值计算）
    #     weight_table = []
    #     for dst_y in range(char_height):
    #         src_y = dst_y / scale
    #         y1 = int(src_y)
    #         y2 = min(y1 + 1, font_size - 1)
    #         y_weight = src_y - y1
    #         weight_table.append((y1, y2, y_weight))
        
    #     # 仅处理需要渲染前景色的像素
    #     for dst_y, (y1, y2, y_weight) in enumerate(weight_table):
    #         # 计算行偏移
    #         row_offset = dst_y * display_width * bpp
            
    #         for dst_x in range(display_width):
    #             # 如果是ASCII字符且超出左半部分，跳过
    #             if is_ascii and dst_x >= char_width // 2:
    #                 continue
                    
    #             # 计算源位置
    #             src_x = dst_x / scale
    #             x1 = int(src_x)
    #             x2 = min(x1 + 1, font_size - 1)
    #             x_weight = src_x - x1
                
    #             # 获取4个相邻像素
    #             pixels = self._get_interpolation_pixels(
    #                 char_data, bytes_per_row, y1, y2, x1, x2)
                
    #             # 双线性插值
    #             top = pixels[0] * (1 - x_weight) + pixels[1] * x_weight
    #             bottom = pixels[2] * (1 - x_weight) + pixels[3] * x_weight
    #             value = top * (1 - y_weight) + bottom * y_weight
                
    #             # 如果值大于阈值，设置前景色
    #             if value > 0.5:
    #                 idx = row_offset + dst_x * bpp
    #                 char_mv[idx:idx+bpp] = fg_bytes
        
    #     return char_block, display_width

    # def _get_interpolation_pixels(self, char_data, bytes_per_row, y1, y2, x1, x2):
    #     """
    #     高效获取插值所需的4个像素值
    #     - 减少重复计算
    #     - 优化边界检查
    #     """
    #     pixels = bytearray(4)  # 预分配空间
        
    #     # 计算4个点的位置
    #     points = [(y1, x1), (y1, x2), (y2, x1), (y2, x2)]
        
    #     for i, (py, px) in enumerate(points):
    #         byte_idx = py * bytes_per_row + (px // 8)
            
    #         if byte_idx < len(char_data):
    #             bit_idx = 7 - (px % 8)
    #             pixels[i] = (char_data[byte_idx] >> bit_idx) & 1
    #         else:
    #             pixels[i] = 0
        
    #     return pixels



    # 效率低一点，缩放效果好一点
    # def draw_text_high_quality(self, 
    #                        text, x=0, y=0, 
    #                        font_size=40, scale=1.0, 
    #                        color=(255, 255, 255), 
    #                        background=None,  # 新增背景色参数
    #                        spacing=1):
    #     """
    #     绘制高质量文本，支持多字体大小和批量发送优化
    #     优化了中英文混合显示时的间距问题
    #     支持前景色和背景色
        
    #     参数:
    #         text: 要绘制的文本
    #         x, y: 文本起始坐标
    #         font_size: 字体大小 (默认为32)
    #         scale: 缩放比例
    #         color: 文本颜色 (前景色, RGB元组)
    #         background: 背景颜色 (RGB元组, None表示透明)
    #         spacing: 字符间距
    #     """
    #     # 获取前景像素字节表示
    #     fg_pixel_bytes = self.color_fn(color)
    #     bytes_per_pixel = len(fg_pixel_bytes)
        
    #     # 获取背景像素字节表示（如果有背景色）
    #     bg_pixel_bytes = self.color_fn(background) if background is not None else None
        
    #     # 获取指定大小的字体集，如果不存在则使用默认32号字体
    #     font_set = self.char.get(font_size, self.char.get(32))
    #     if font_set is None:
    #         raise ValueError(f"Font size {font_size} not available")
        
    #     # 计算行高（基于字体大小）
    #     char_height = int(font_size * scale)
        
    #     # 批量数据存储
    #     batch_data = bytearray()
    #     batch_regions = []  # 存储元组: (x_start, y_start, x_end, y_end, start_idx, end_idx)
        
    #     # 初始化光标位置
    #     cursor_x = x
        
    #     # 预处理所有字符
    #     for char in text:
    #         # 获取字符数据 - 确保不会返回 None
    #         char_data = font_set.get(char, font_set.get(" "))
    #         if char_data is None:
    #             # 如果连空格都没有，创建一个空字符数据
    #             bytes_per_row = (font_size + 7) // 8
    #             char_data = b'\x00' * (bytes_per_row * font_size)
            
    #         # 判断是否为ASCII字符
    #         is_ascii = ord(char) < 128
            
    #         # 为ASCII字符使用更紧凑的宽度
    #         if is_ascii:
    #             # 保持完整宽度但使用更小的间距
    #             base_width = font_size
    #             char_spacing = max(0, spacing )
    #         else:
    #             base_width = font_size
    #             char_spacing = spacing
            
    #         char_width = int(base_width * scale)
            
    #         # 边界检查 - 跳过超出屏幕的字符
    #         if cursor_x + char_width > self.width:
    #             break
    #         if y + char_height > self.height:
    #             break
            
    #         # 唯一缓存键（包含字体大小、前景色和背景色）
    #         cache_key = (char, font_size, scale, color, background)
            
    #         # 检查缓存或创建新字符块
    #         if cache_key in self._char_block_cache:
    #             char_block = self._char_block_cache[cache_key]
    #         else:
    #             char_block = self._generate_char_block(
    #                 char_data, font_size, char_width, char_height, 
    #                 scale, fg_pixel_bytes, bg_pixel_bytes, bytes_per_pixel
    #             )
    #             self._char_block_cache[cache_key] = char_block
            
    #         # 对于ASCII字符，仅渲染左半部分区域
    #         if is_ascii:
    #             # 计算实际显示的宽度（原宽度的一半）
    #             display_width = char_width // 2
    #             # 裁剪字符块数据
    #             cropped_block = bytearray()
    #             for row in range(char_height):
    #                 start = row * char_width * bytes_per_pixel
    #                 end = start + display_width * bytes_per_pixel
    #                 cropped_block.extend(char_block[start:end])
    #             char_block = cropped_block
    #             char_width = display_width
            
    #         # 添加到批量数据
    #         start_idx = len(batch_data)
    #         batch_data.extend(char_block)
    #         end_idx = len(batch_data)
            
    #         # 存储区域信息 (x_start, y_start, x_end, y_end, start_idx, end_idx)
    #         batch_regions.append((
    #             cursor_x, y,
    #             cursor_x + char_width - 1,
    #             y + char_height - 1,
    #             start_idx,
    #             end_idx
    #         ))
            
    #         cursor_x += char_width + char_spacing
        
    #     # 批量发送所有字符数据
    #     for region in batch_regions:
    #         x_start, y_start, x_end, y_end, start_idx, end_idx = region
    #         self.set_window(x_start, y_start, x_end, y_end)
    #         self.write_data_bytes(batch_data[start_idx:end_idx])
    # def _generate_char_block(self, char_data, font_size, char_width, char_height, 
    #                         scale, fg_pixel_bytes, bg_pixel_bytes, bytes_per_pixel):
    #     """
    #     生成高质量字符块（使用双线性插值）
    #     支持前景色和背景色
    #     """
    #     # 创建字符缓冲区
    #     char_block = bytearray(char_width * char_height * bytes_per_pixel)
    #     if not char_block:  # 空字符块检查
    #         return char_block
            
    #     char_mv = memoryview(char_block)
        
    #     # 如果有背景色，先用背景色填充整个区域
    #     if bg_pixel_bytes is not None:
    #         for i in range(0, len(char_block), bytes_per_pixel):
    #             char_mv[i:i+bytes_per_pixel] = bg_pixel_bytes
        
    #     # 计算每行字节数（用于位图访问）
    #     bytes_per_row = (font_size + 7) // 8
        
    #     # 高质量缩放算法（双线性插值）
    #     for dst_y in range(char_height):
    #         # 计算源位置（带小数）
    #         src_y = dst_y / scale
    #         y1 = int(src_y)
    #         y2 = min(y1 + 1, font_size - 1)
    #         y_weight = src_y - y1
            
    #         for dst_x in range(char_width):
    #             # 计算源位置（带小数）
    #             src_x = dst_x / scale
    #             x1 = int(src_x)
    #             x2 = min(x1 + 1, font_size - 1)
    #             x_weight = src_x - x1
                
    #             # 获取4个相邻像素（使用实际的字体大小）
    #             pixels = []
    #             for py, px in [(y1, x1), (y1, x2), (y2, x1), (y2, x2)]:
    #                 byte_idx = py * bytes_per_row + (px // 8)
                    
    #                 # 确保 byte_idx 在有效范围内
    #                 if byte_idx < len(char_data):
    #                     bit_idx = 7 - (px % 8)
    #                     pixel_val = (char_data[byte_idx] >> bit_idx) & 1
    #                 else:
    #                     pixel_val = 0  # 超出数据范围视为0
                    
    #                 pixels.append(pixel_val)
                
    #             # 双线性插值
    #             top = pixels[0] * (1 - x_weight) + pixels[1] * x_weight
    #             bottom = pixels[2] * (1 - x_weight) + pixels[3] * x_weight
    #             value = top * (1 - y_weight) + bottom * y_weight
                
    #             # 阈值处理（>0.5视为点亮）
    #             if value > 0.5:
    #                 idx = (dst_y * char_width + dst_x) * bytes_per_pixel
    #                 char_mv[idx:idx+bytes_per_pixel] = fg_pixel_bytes
        
    #     return char_block


    # 老版本bmf文件加载
    # # @timeit
    # def new_find_key(self,需要的字符):
    #     self.char = {}
    #     for i in 需要的字符:
    #         字号byte = i.to_bytes(2, "little")
    #         点阵长度 = (i*i//8).to_bytes(2, "little")
    #         ascii字号 = (i//2).to_bytes(2, "little")
    #         ascii点阵长度 = (i*(i //2)//8).to_bytes(2, "little")
    #         # 字符编码 + 字体宽 + 字体高 + adv不知道什么 + 点阵字符长度
    #         字符_key = 字号byte + 字号byte + 字号byte + 点阵长度
    #         ascii_key = ascii字号 + 字号byte + ascii字号 + ascii点阵长度
    #         self.char[i] = {}
    #         for 字符 in 需要的字符[i]:
    #             if ord(字符)<128:
    #                 self.char[i][字符] = ord(字符).to_bytes(4, "little") + ascii_key
    #                 # print(""self.char[i][字符])
    #                 # return
    #             else:
    #                 self.char[i][字符] = ord(字符).to_bytes(4, "little") + 字符_key
    
    # @timeit
    # def load_bmf(self, path, 需要的字符):
    #     size = os.stat(path)[6]
    #     buf  = bytearray(size)
    #     with open(path, "rb") as f:
    #         f.readinto(buf)  # **不改读取方式**
            
    #     self.new_find_key(需要的字符)

    #     # 头
    #     if buf[0:4] != b"BMF3":
    #         raise "格式有误"
    #     # buf[4:6] # 版本 没用
    #     字号数量 = buf[6] | (buf[7] << 8) # 存储了多少种字号
    #     print("字号数量:",字号数量)
        
    #     # mv = memoryview(buf)
    #     # 优化使用memoryview来索引?
    #     # 优化buf使用自己字号的位置 耗时 5.28 耗时2 5.275979     
    #     tt =0
    #     zz = 0
    #     s = time.ticks_ms() 
    #     # 查找字体
    #     for 字号 in self.char:
    #         for 字符 in self.char[字号]:   
    #             if ord(字符)<128:
    #                 点阵长度 = 字号*字号//8//2
    #             else:
    #                 点阵长度 = 字号*字号//8   
    #             t =time.ticks_us()
    #             index = buf.find(self.char[字号][字符])
    #             tt += (time.ticks_us()-t)
                
    #             if index:
    #                 index = index+14
    #                 z = time.ticks_us()
    #                 self.char[字号][字符]= bytes(buf[index:index+点阵长度])
    #                 zz += (time.ticks_us()-z)
    #             else:
    #                 print("没有找到字符",self.char[字号][字符])
    #     print("耗时",(time.ticks_ms()-s)/1000)
    #     print("耗时2",tt/1000/1000)
    #     print("耗时3",zz/1000/1000)
    #     # # 单个字体头
    #     # 字体大小 = buf[8] | (buf[9] << 8)
    #     # 字体数量 = (buf[10]
    #     # | (buf[11] << 8)
    #     # | (buf[12] << 16)
    #     # | (buf[13] << 24))
    #     # print("字体大小:",字体大小)
    #     # print("字体数量:",字体数量)
    #     bytearray().extend
        
        
    #     # # 单个字符头
    #     # # 什么字符
    #     # print(str(buf[14:18]))
    #     # print("字体宽",buf[18] | (buf[19] << 8))
    #     # print("字体高",buf[20] | (buf[21] << 8))
    #     # print("adv",buf[22] | (buf[23] << 8))
    #     # print("点位数据数量",(buf[24]
    #     # | (buf[25] << 8)
    #     # | (buf[26] << 16)
    #     # | (buf[27] << 24)))
    #     # print("位图", buf[28:28+8])
    #     # self.char[32] = {} 
    #     # self.char[32]["电"]= bytes( buf[28:28+288])
        
    #     # print(str(buf[36:40]))


## 有问题，buf被拷贝
    # def _load_bmf_select(self, path, 需要的字符):
    #     t = 0
    #     # 读取120k，每个字符8字节，约15000字符索引
    #     s = time.ticks_ms()
    #     size = 4096 * 60
    #     # size = os.stat(path)[6]
    #     buf = bytearray(size)
    #     with open(path, "rb") as f:
    #         f.readinto(buf)  # **不改读取方式**
            
    #         # 头
    #         if buf[0:4] != b"BMF3":
    #             raise "格式有误"
    #         # buf[4:6] # 版本 没用
    #         字号数量 = buf[6] | (buf[7] << 8)  # 存储了多少种字号
    #         # 割掉头 性能瓶颈在此处，文件读的越大性能瓶颈越强
    #         buf = buf[12:]
    #         print("读文件耗时",time.ticks_ms()-s)
    #         字库查找 = {}
    #         字库索引 = {}
    #         for i in range(字号数量):
    #             字号 = buf[0] | (buf[1] << 8)
    #             # print(字号)
    #             字符个数 = buf[2] | (buf[3] << 8)
    #             buf = buf[4:]   # 割头
    #             字库查找[字号] =  buf[:4*字符个数]
    #             字库索引[字号] =  buf[4*字符个数:8*字符个数]
    #             buf = buf[8*字符个数:]
            
            
            
    #         for  字号 in 需要的字符:

                
    #             self.char[字号] ={}
    #             for 字符 in 需要的字符[字号]:
    #                 s = time.ticks_us()
    #                 字符位置 = 字库查找[字号].find(ord(字符).to_bytes(4, "little"))
    #                 t += time.ticks_us()-s
    #                 if 字符位置 == -1:
    #                     print("没有字符")
    #                     continue
    #                 偏移 = int.from_bytes( 字库索引[字号][字符位置:字符位置+4], "little")
    #                 f.seek(偏移) 
    #                 偏移 = int.from_bytes( 字库索引[字号][字符位置:字符位置+4], "little") 
    #                 f.seek(偏移) 
    #                 if ord(字符) < 128: 
    #                     self.char[字号][字符]=f.read(字号*字号//8//2) 
    #                 else: 
    #                     self.char[字号][字符]=f.read(字号*字号//8)
    #     print("find耗时",t / 1000 /1000)