# dynamic_loader.py - 更新版
import pygame
import os
import json
import time
from typing import List, Tuple, Dict, Optional
from enum import Enum
from collections import OrderedDict
# 在dynamic_loader.py中修改InlineFragment类


class InlineFragment:
    """行内片段 - 增强版，支持图片标记"""

    def __init__(self, text, color=(255, 255, 255), click_value=None,
                 is_image_mark=False, img_info=None, clip_pos=None, size=None):
        self.text = str(text)
        self.color = color
        self.click_value = click_value
        self.is_image_mark = is_image_mark  # 是否是图片标记
        self.img_info = img_info  # 图片信息（如果是图片标记）
        self.clip_pos = clip_pos  # 裁剪位置
        self.size = size  # 调整大小
        self.width = 0  # 将在绘制时计算（图片需要特殊处理）
        self.height = 0  # 图片高度

    def calculate_width(self, font):
        """计算片段宽度（设计分辨率坐标，无屏幕缩放概念）"""
        if self.is_image_mark and self.img_info:
            # 图片标记：宽度为图片目标宽度
            if self.size:
                self.width = self.size[0]
            else:
                self.width = self.img_info.get('original_width', 270)
        else:
            # 普通文本
            self.width = font.size(self.text)[0]

        return self.width

    def render_image(self):
        """渲染图片（如果是图片标记），按设计分辨率坐标输出"""
        if not self.is_image_mark or not self.img_info:
            return None

        try:
            img_path = os.path.join(self.img_info.get('base_dir', './'),
                                    self.img_info.get('filename', ''))

            if not os.path.exists(img_path):
                return None

            image = pygame.image.load(img_path).convert_alpha()

            # 裁剪 (裁剪是基于原图的，不需要缩放坐标，除非clip_pos本身是相对的)
            # 这里假设 clip_pos 是基于原图像素的，所以先裁剪
            clip_x, clip_y = self.clip_pos if self.clip_pos else (0, 0)
            clip_width = self.img_info.get('width', 270) # CSV里的width通常是裁剪宽
            clip_height = self.img_info.get('height', 270)

            img_width, img_height = image.get_size()
            
            # 安全裁剪
            safe_clip_w = min(clip_width, img_width - clip_x)
            safe_clip_h = min(clip_height, img_height - clip_y)
            
            if safe_clip_w > 0 and safe_clip_h > 0:
                clipped_image = image.subsurface(pygame.Rect(clip_x, clip_y, safe_clip_w, safe_clip_h))
            else:
                return None

            # 如果指定了 size，按 size 缩放到目标尺寸（设计分辨率坐标）
            if self.size:
                target_w, target_h = self.size
                if target_w > 0 and target_h > 0 and (target_w, target_h) != clipped_image.get_size():
                    clipped_image = pygame.transform.smoothscale(clipped_image, (target_w, target_h))

            return clipped_image

        except Exception as e:
            print(f"渲染行内图片失败: {e}")
            return None


class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    IMAGE_MARK = "image_mark"  # 图片标记类型
    IMAGE_STACK = "image_stack"  # 新增：图片叠加类型
    DIVIDER = "divider"
    MENU = "menu"


class ConsoleContent:
    """控制台内容项 - 支持行内片段"""

    def __init__(self, content_type: ContentType, data, color=(255, 255, 255), height=30,
                 metadata=None, fragments=None):
        self.type = content_type
        self.data = data  # 主文本内容（用于向后兼容）
        self.color = color
        self.height = height
        self.metadata = metadata or {}
        self.timestamp = time.time()

        # 行内片段（用于支持同一行内的多个部分）
        self.fragments = fragments or []
        if not self.fragments and self.data:
            # 如果没有片段但有数据，创建一个默认片段
            self.fragments = [InlineFragment(self.data, color)]

    def add_fragment(self, fragment: InlineFragment):
        """添加行内片段"""
        self.fragments.append(fragment)

    def get_full_text(self):
        """获取完整文本"""
        if self.fragments:
            return ''.join(f.text for f in self.fragments)
        return self.data

    def __repr__(self):
        return f"ConsoleContent(type={self.type}, text={self.get_full_text()[:50]})"


class DynamicLoader:
    """动态加载器 - 支持滚动和日志记录"""

    def __init__(self, screen_width: int, screen_height: int, font,
                 input_area_height: int = 40, log_file: str = "log.txt"):
        """
        初始化动态加载器

        Args:
            screen_width: 设计分辨率宽（虚拟画布宽）
            screen_height: 设计分辨率高（虚拟画布高）
            font: PyGame字体对象
            input_area_height: 输入区域高度
            log_file: 日志文件路径
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.input_area_height = input_area_height

        # [虚拟画布] 本类所有坐标一律是设计分辨率坐标；
        # 真实窗口的缩放由 ERAconsole 的 pygame.SCALED 统一处理，这里不再感知缩放
        # 图片信息注册表
        self.image_registry = {}  # url -> 图片信息
        self.image_surface_cache = {}  # 缓存已渲染的图片Surface
        self.placeholder_color = (100, 100, 150)  # 图片加载前的占位符颜色
        # 内容管理
        self.history: List[ConsoleContent] = []  # 完整的历史记录（盒子模型中的"流"）
        self.max_history_length = 10000  # 最大历史记录数
        self.seq_counter = 0  # [MCP] 内容项单调序号：history 会截断，绝对下标会漂移，seq 是外部读取的稳定游标

        # [盒子模型] 视口状态：流(history) + 盒子位置(tail_gap) + 盒子缓存
        # 盒子是唯一被排版/渲染的实体；tail_gap 是盒底之下的流项数，0=在流尾（追更）
        self.tail_gap = 0
        self.box_dirty = True          # 三时机才重排：流追加且在流尾 / 盒子移动 / 容量变化
        self.new_content_below = False  # 回看中来了新内容（右下角提示）
        self.box_items = []            # [(预渲染surface, y)]，重排时生成
        self.box_hit_rects = []        # [(rect, click_value)]，重排时按"行坐标+片段坐标"一次算好
        self._box_line_count = 0       # 盒内项数（滚动条/信息用）
        self._new_content_hint = None  # "↓ 有新内容"提示的懒渲染缓存

        # 行高与容量
        self.line_height = font.get_linesize()  # 每行高度
        self.content_area_height = screen_height - input_area_height - 20  # 盒容量（像素）

        # 滚动条
        self.scrollbar_width = 10
        self.scrollbar_visible = False
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_active_color = (150, 150, 150)

        # 日志文件
        self.log_file = log_file
        self._init_log_file()
        # 缓存
        self.image_cache = OrderedDict()  # 图片LRU缓存
        self.CACHE_LIMIT = 50  # 限制内存中最多只保留 50 张最近使用的图片

    def _get_image_from_cache(self, img_path):
        """
        LRU 缓存获取图片：
        1. 如果在缓存里，移动到末尾（标记为最近使用），直接返回。
        2. 如果不在缓存里，从硬盘加载。
        3. 如果缓存满了，删除最久未使用的图片（第一个）。
        """
        if not img_path or not os.path.exists(img_path):
            return None

        # 情况 1: 图片已在缓存中
        if img_path in self.image_cache:
            # 将其移动到字典末尾，表示"最近刚刚用过"
            self.image_cache.move_to_end(img_path)
            return self.image_cache[img_path]

        # 情况 2: 图片不在缓存中，需要加载
        try:
            image = pygame.image.load(img_path).convert_alpha()

            # 检查缓存是否已满
            if len(self.image_cache) >= self.CACHE_LIMIT:
                # [核心逻辑] 弹出第一个元素（即最久没被用过的图片），释放内存
                removed_path, _ = self.image_cache.popitem(last=False)
                # print(f"释放图片内存: {removed_path}") # 调试用

            # 加入缓存
            self.image_cache[img_path] = image
            return image

        except Exception as e:
            print(f"加载图片失败: {img_path} - {e}")
            return None
    # 在DynamicLoader类中添加add_inline_fragments方法

    def _append_history(self, item: ConsoleContent):
        """统一的历史写入口：打上单调递增序号后写入（供 MCP 等外部读取做稳定游标）"""
        self.seq_counter += 1
        item.metadata['seq'] = self.seq_counter
        self.history.append(item)

    def add_inline_fragments(self, fragments):
        """
        添加行内片段到历史记录 - 支持自动换行

        Args:
            fragments: InlineFragment列表
        """
        if not fragments:
            return []

        # 计算最大允许宽度 (屏幕宽 - 边距 - 滚动条预留)
        max_width = self.screen_width - 40 - 15

        added_items = []
        current_line_fragments = []
        current_line_width = 0

        # 辅助函数：提交当前行
        def commit_line():
            nonlocal current_line_fragments, current_line_width
            if not current_line_fragments:
                return

            # 创建内容项
            # [盒子模型] 点击矩形不再登记注册表——重排时按"行的盒内y+片段的行内x"直接导出
            item = ConsoleContent(
                ContentType.TEXT,
                "",
                fragments=current_line_fragments,
                height=self.line_height
            )

            self._append_history(item)
            added_items.append(item)

            # 重置当前行
            current_line_fragments = []
            current_line_width = 0

        # --- 遍历所有片段 ---
        for frag in fragments:
            # 1. 计算片段总宽
            frag_width = frag.calculate_width(self.font)

            # 2. 如果是图片 (不可分割)
            if frag.is_image_mark:
                # 如果当前行放不下这张图，且当前行不是空的，先换行
                if current_line_width + frag_width > max_width and current_line_fragments:
                    commit_line()

                # 加入当前行
                current_line_fragments.append(frag)
                current_line_width += frag_width

                # 如果这张图本身就比屏幕宽（极少见），那也没办法，只能让它超出去或者强制再换行
                # 这里选择让它独占一行后，如果还超宽就不管了，因为图片很难切分
                if current_line_width > max_width:
                    commit_line()

            # 3. 如果是文本 (可以分割)
            else:
                # 如果整段文本能放下，直接加
                if current_line_width + frag_width <= max_width:
                    current_line_fragments.append(frag)
                    current_line_width += frag_width
                else:
                    # 放不下，需要切分文本
                    remaining_text = frag.text

                    while remaining_text:
                        # 尝试找出能在当前行放下的最大子字符串
                        # 这是一个字符级循环，确保中文也能正确换行
                        fit_text = ""
                        fit_width = 0

                        # 预计算剩余空间
                        space_left = max_width - current_line_width

                        # 快速检查：如果一个字都放不下，且当前行有东西，先换行
                        if space_left <= 0 and current_line_fragments:
                            commit_line()
                            space_left = max_width

                        # 逐字扫描 (优化：可以先估算，但逐字最准确)
                        # 为了性能，这里可以优化，但对于VN来说逐字扫描通常够快
                        split_index = 0
                        for char in remaining_text:
                            char_w = self.font.size(char)[0]
                            if fit_width + char_w <= space_left:
                                fit_width += char_w
                                split_index += 1
                            else:
                                break

                        # 如果是空的（连一个字都放不下），强制换行
                        if split_index == 0:
                            if current_line_fragments:
                                commit_line()
                                continue  # 换行后重试
                            else:
                                # 极端情况：这一行是空的，但第一个字就比屏幕宽（不太可能发生）
                                # 强制放入一个字防止死循环
                                split_index = 1
                                fit_width = self.font.size(
                                    remaining_text[0])[0]

                        # 切割文本
                        fit_text = remaining_text[:split_index]
                        remaining_text = remaining_text[split_index:]

                        # 创建新片段（继承颜色和点击属性）
                        new_frag = InlineFragment(
                            fit_text,
                            frag.color,
                            frag.click_value,
                            is_image_mark=False
                        )
                        # 只有当它是图片时才需要传 info，文本不需要，避免 calculate_width 报错
                        new_frag.width = fit_width

                        current_line_fragments.append(new_frag)
                        current_line_width += fit_width

                        # 如果还有剩余文本，说明这行满了，提交换行
                        if remaining_text:
                            commit_line()

        # 提交最后一行
        commit_line()

        # 记录日志
        full_text = ''.join(f.text for f in fragments)
        self._write_to_log(f"[TEXT] {full_text}")

        # [盒子模型] 在流尾则标脏重排（追更），回看中则提示有新内容
        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True

        return added_items
    # 在DynamicLoader类中添加_parse_params方法

    def _parse_params(self, param_str):
        """解析参数字符串为字典"""
        params = {}
        if not param_str:
            return params

        param_pairs = param_str.split(';')
        for pair in param_pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                params[key.strip()] = value.strip()

        return params

    def parse_image_stack_mark(self, text):
        import re
        """解析图片叠加标记字符串 - 全面修复版"""
        # 1. 基础检查
        if not text.startswith("[IMG_STACK:") or not text.endswith("]"):
            return [], {}

        # 2. 提取内容 (注意索引是11，跳过冒号)
        content = text[11:-1]
        if not content:
            return [], {}

        img_elements = []
        img_infos = {}

        # 3. 分割图片元素 (使用 | )
        elements = [elem.strip()
                    for elem in content.split('|') if elem.strip()]

        for element in elements:
            # 提取 图片名 和 参数块
            # 格式: 图片名{参数1:值1;参数2:值2}
            pattern = r'([^{]+)(?:\{([^}]+)\})?'
            match = re.match(pattern, element)

            if match:
                img_name = match.group(1).strip()
                param_str = match.group(2).strip() if match.group(2) else ""

                # 4. 解析参数 (使用 ; 分割)
                params = {}
                if param_str:
                    param_pairs = param_str.split(';')  # 关键：用分号分割
                    for pair in param_pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            params[key.strip()] = value.strip()

                # 5. 获取并合并信息
                img_info = self.get_registered_image_info(img_name)
                if img_info:
                    merged_info = img_info.copy()

                    # --- 解析 Offset (偏移) ---
                    if 'offset' in params:
                        try:
                            # 移除括号，按逗号分割
                            # 支持负数，如 (-10, 20)
                            clean_val = params['offset'].replace(
                                '(', '').replace(')', '')
                            ox, oy = map(int, clean_val.split(','))
                            merged_info['offset_x'] = ox
                            merged_info['offset_y'] = oy
                            # print(f"DEBUG: {img_name} offset set to {ox}, {oy}")
                        except ValueError:
                            print(f"解析offset失败: {params['offset']}")

                    # --- 解析 Clip (裁剪) ---
                    if 'clip' in params:
                        try:
                            clean_val = params['clip'].replace(
                                '(', '').replace(')', '')
                            cx, cy = map(int, clean_val.split(','))
                            merged_info['clip_x'] = cx
                            merged_info['clip_y'] = cy
                        except ValueError:
                            pass

                    # --- 解析 Size (缩放) ---
                    if 'size' in params:
                        try:
                            clean_val = params['size'].replace(
                                '(', '').replace(')', '')
                            tw, th = map(int, clean_val.split(','))
                            merged_info['target_width'] = tw
                            merged_info['target_height'] = th
                        except ValueError:
                            pass

                    # 其他简单参数
                    if 'click' in params:
                        merged_info['click_value'] = params['click']
                    if 'chara' in params:
                        merged_info['chara_id'] = params['chara']
                    if 'type' in params:
                        merged_info['draw_type'] = params['type']

                    img_elements.append({
                        'name': img_name,
                        'params': params,
                        'info': merged_info
                    })
                    img_infos[img_name] = merged_info
                else:
                    # 只有找不到图片信息时才打印错误，避免刷屏
                    print(f"警告: 注册表中找不到图片 '{img_name}'")

        return img_elements, img_infos

    def _parse_image_mark(self, text):
        """解析图片标记字符串"""
        if not text.startswith("[IMG:") or not text.endswith("]"):
            return None, {}

        content = text[5:-1]  # 移除 [IMG: 和 ]
        parts = content.split("|")

        if not parts:
            return None, {}

        img_url = parts[0]
        params = {}

        for param in parts[1:]:
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value

        return img_url, params

    def register_image_info(self, url, img_info):
        """注册图片信息"""
        if not hasattr(self, 'image_registry'):
            self.image_registry = {}

        self.image_registry[url] = img_info

    def get_registered_image_info(self, url):
        """获取已注册的图片信息"""
        if hasattr(self, 'image_registry') and url in self.image_registry:
            return self.image_registry[url]
        return None

    def add_image_mark(self, img_mark, click_value=None, template_width=None, template_height=None):
        """
        添加图片标记到历史记录 - 增强版，支持图片叠加

        Args:
            img_mark: 图片标记字符串，格式 [IMG:图片ID|参数] 或 [IMG_STACK:图片1|参数]
            click_value: 点击时输入的文本
        """
        # 检查是否是图片叠加标记
        if img_mark.startswith("[IMG_STACK:"):
            return self._add_image_stack_mark(img_mark, click_value)

        # 原有的单张图片处理逻辑
        img_url, params = self._parse_image_mark(img_mark)
        if not img_url:
            return self.add_text(img_mark)

        img_info = self.get_registered_image_info(img_url)

        if not img_info:
            item = ConsoleContent(
                ContentType.TEXT,
                f"[图片未找到: {img_url}]",
                color=(255, 100, 100),
                height=self.line_height
            )
            self._append_history(item)
            if self.tail_gap == 0:
                self.box_dirty = True
            else:
                self.new_content_below = True
            return item

        # 解析参数
        clip_pos = None
        size = None

        if 'clip' in params:
            clip_x, clip_y = map(int, params['clip'].split(','))
            clip_pos = (clip_x, clip_y)

        if 'size' in params:
            width, height = map(int, params['size'].split(','))
            size = (width, height)

        # 创建图片内容项
        item = ConsoleContent(
            ContentType.IMAGE_MARK,
            img_mark,
            height=size[1] +
            10 if size else img_info.get('original_height', 270) + 10,
            metadata={
                'img_url': img_url,
                'img_info': img_info,
                'clip_pos': clip_pos,
                'size': size,
                'template_width': template_width,
                'template_height': template_height,
                'click_value': click_value,
                'cached_surface': None,
                'needs_rendering': True
            }
        )

        if click_value:
            # [盒子模型] 只记元数据，命中矩形由重排按图片渲染尺寸导出
            item.metadata['clickable'] = True

        self._append_history(item)
        self._write_to_log(f"[IMAGE] {img_url}")

        # [盒子模型] 在流尾则标脏重排，回看中则提示有新内容
        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True

        return item

    def _add_image_stack_mark(self, img_mark, click_value=None, template_width=None, template_height=None):
        """
        添加图片叠加标记 - 新格式版本
        """
        # 1. 解析新格式的标记字符串
        img_elements, img_infos = self.parse_image_stack_mark(img_mark)

        if not img_elements:
            # 解析失败，显示错误文本
            return self.add_text(f"[图片叠加解析失败: {img_mark[:50]}...]", (255, 100, 100))

        # 2. 计算模板尺寸
        if template_width is None:
            template_width = self.screen_width - 20  # 默认屏幕宽减边距

        if template_height is None:
            # 自动计算高度：取所有图片中的最大高度
            template_height = 0
            for element in img_elements:
                info = element['info']
                # 优先使用target_height，否则使用original_height
                height = info.get(
                    'target_height', info.get('original_height', 270))
                template_height = max(template_height, height)

        # 3. 计算总高度（模板高度 + 边距）
        total_height = template_height + 10  # 上下各留5px边距

        # 4. 创建ConsoleContent对象
        item = ConsoleContent(
            ContentType.IMAGE_STACK,
            img_mark,
            height=total_height,
            metadata={
                'img_elements': img_elements,  # 图片元素列表（保持顺序）
                'img_infos': img_infos,        # 图片信息字典（快速查找）
                'template_width': template_width,
                'template_height': template_height,
                'global_click': click_value,    # 全局点击值（整个叠加区域）
                'cached_surface': None,
                'needs_rendering': True,

                # 这些字段在新的渲染器中可能不需要，但保留以兼容旧代码
                'img_list': [elem['name'] for elem in img_elements],  # 图片名列表
                'clip_pos': None,  # 不再使用全局clip_pos，每个图片独立
                'size': None,      # 不再使用全局size，每个图片独立
                'chara_id': None,  # 不再使用全局chara_id，每个图片独立
                'draw_type': None  # 不再使用全局draw_type，每个图片独立
            }
        )

        # 5. 点击标记（[盒子模型] 命中矩形由重排按渲染尺寸导出）
        if click_value:
            item.metadata['clickable'] = True

        # 6. 添加到历史记录
        self._append_history(item)
        self._write_to_log(f"[IMAGE_STACK] {len(img_elements)}张图片")

        # 7. [盒子模型] 在流尾则标脏重排，回看中则提示有新内容
        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True

        return item

    def set_font(self, font):
        self.font = font
        self.line_height = font.get_linesize()
        # [盒子模型] 字体变了，盒子需要用新字体重排重渲染
        self.box_dirty = True

    def handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        处理鼠标点击事件（[盒子模型] 直接查重排时算好的命中矩形）

        Args:
            mouse_pos: 鼠标位置 (x, y)，设计分辨率坐标（SCALED 已自动换算）

        Returns:
            点击的文本值，如果没有点击可点击区域则返回None
        """
        for rect, click_value in self.box_hit_rects:
            if rect.collidepoint(mouse_pos):
                return click_value

        return None

    def _init_log_file(self):
        """初始化日志文件"""
        try:
            # 创建日志文件目录（如果不存在）
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 写入初始信息
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"会话开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
        except Exception as e:
            print(f"初始化日志文件失败: {e}")

    def add_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> List[ConsoleContent]:
        """
        添加文本到历史记录

        Args:
            text: 要添加的文本
            color: 文本颜色

        Returns:
            添加的内容项列表
        """
        added_items = []

        # 处理空文本
        if text is None or text == "":
            item = ConsoleContent(ContentType.TEXT, "",
                                  color, self.line_height)
            self._append_history(item)
            self._write_to_log("")
            added_items.append(item)

            # [盒子模型] 在流尾则标脏重排，回看中则提示有新内容
            if self.tail_gap == 0:
                self.box_dirty = True
            else:
                self.new_content_below = True

            return added_items

        # 处理制表符
        text = text.replace('\t', '    ')

        # 分割文本为多行
        lines = []
        current_line = ""

        for char in text:
            # 处理换行符
            if char == '\n':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append("")  # 空行
                continue

            # 测试添加当前字符后的宽度
            test_line = current_line + char
            text_width = self.font.size(test_line)[0]

            # 如果超出屏幕宽度（减去滚动条和边距）
            max_width = self.screen_width - 40 - \
                (self.scrollbar_width if self.scrollbar_visible else 0)
            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line

        # 添加最后一行
        if current_line:
            lines.append(current_line)

        # 将新行添加到历史记录
        for line in lines:
            item = ConsoleContent(ContentType.TEXT, line,
                                  color, self.line_height)
            self._append_history(item)
            self._write_to_log(line)
            added_items.append(item)

        # 限制历史记录长度
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]

        # [盒子模型] 在流尾则标脏重排，回看中则提示有新内容
        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True

        return added_items

    def add_divider(self, char: str = "─", length: int = 40, color: Tuple[int, int, int] = (150, 150, 150)):
        """
        添加分割线

        Args:
            char: 分割线字符
            length: 分割线长度
            color: 颜色
        """
        divider_text = char * length
        item = ConsoleContent(ContentType.DIVIDER,
                              divider_text, color, self.line_height)
        self._append_history(item)
        self._write_to_log(divider_text)
        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True
        return item

    def add_menu(self, items: List[str], color: Tuple[int, int, int] = (200, 200, 255)):
        """
        添加菜单

        Args:
            items: 菜单项列表
            color: 颜色
        """
        added_items = []
        for item in items:
            content_item = ConsoleContent(
                ContentType.MENU, item, color, self.line_height)
            self._append_history(content_item)
            self._write_to_log(item)
            added_items.append(content_item)

        if self.tail_gap == 0:
            self.box_dirty = True
        else:
            self.new_content_below = True
        return added_items

    def _write_to_log(self, text: str):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("[%H:%M:%S] ")
                f.write(timestamp + text + "\n")
        except Exception as e:
            print(f"写入日志失败: {e}")

    def _compose_box(self):
        """
        [盒子模型] 重排盒子：唯一被排版/渲染的实体。
        盒底锚定在 history[len-1-tail_gap]，向更旧方向按像素容量贪心装填；
        装不下且盒非空 → 该项属于更老的盒位（图片不可切分由此天然成立）。
        重排时预渲染每项 surface，并按"行的盒内y + 片段的行内x"一次算好命中矩形。
        只在三种时机被触发：流追加且在流尾 / 盒子移动 / 容量变化。
        """
        self.box_dirty = False
        self.box_items = []      # [(surface, y)]
        self.box_hit_rects = []  # [(rect, click_value)]
        self._box_line_count = 0

        if not self.history:
            self.scrollbar_visible = False
            return

        # 钳位盒底锚点（流被清空/缩短时的兜底）
        max_gap = len(self.history) - 1
        if self.tail_gap > max_gap:
            self.tail_gap = max_gap
        bottom_idx = len(self.history) - 1 - self.tail_gap

        TOP_PAD = 10  # 与旧渲染的顶部边距保持一致
        capacity = self.content_area_height

        # 1. 自盒底向更旧方向贪心装填（按像素容量）
        packed = []  # [(item, y)]  y 为屏幕上的最终纵坐标
        used = 0
        idx = bottom_idx
        while idx >= 0:
            item = self.history[idx]
            h = item.height if item.height > 0 else self.line_height
            if h > capacity:
                h = capacity  # 单项超过整盒：钳制到盒高
            if used + h > capacity and packed:
                break  # 装不下：属于更老的盒位，等盒子移过去再进来（不切分）
            packed.append((item, TOP_PAD + capacity - used - h))
            used += h
            idx -= 1
        packed.reverse()  # 恢复从旧到新的显示顺序
        self._box_line_count = len(packed)

        # 2. 逐项预渲染 surface + 命中矩形
        max_w = max(1, self.screen_width - 20)
        for item, y in packed:
            surface, _content_w = self._render_item_surface(item, max_w)
            if surface is None:
                continue

            # 单项渲染结果比盒容量还高（巨图钳制）
            if surface.get_height() > capacity:
                ratio = capacity / surface.get_height()
                surface = pygame.transform.smoothscale(
                    surface, (max(1, int(surface.get_width() * ratio)), capacity))

            self.box_items.append((surface, y))

            # --- 命中矩形：行的盒内 y + 片段在行内的 x 累计导出 ---
            if item.type == ContentType.TEXT and item.fragments:
                x = 10
                for frag in item.fragments:
                    if frag.width == 0:
                        frag.calculate_width(self.font)
                    if frag.click_value:
                        self.box_hit_rects.append((
                            pygame.Rect(x, y, max(frag.width, 1), max(item.height, 1)),
                            frag.click_value))
                    x += frag.width
            elif item.metadata.get('clickable'):
                click_value = item.metadata.get('click_value') or item.metadata.get('global_click')
                if click_value:
                    self.box_hit_rects.append((
                        pygame.Rect(10, y, surface.get_width(), surface.get_height()),
                        click_value))

        # 3. 滚动条可见性：盒外还有内容（盒顶之上或盒底之下）
        self.scrollbar_visible = len(self.history) > self._box_line_count

    def _render_item_surface(self, item, max_w):
        """
        [盒子模型] 重排时把单个内容项渲染成 surface。
        返回 (surface, 内容宽度)；渲染失败返回 (None, 0)。
        draw() 从此零 font.render、零 smoothscale。
        """
        try:
            if item.type == ContentType.TEXT:
                # 文本行：fragment 逐个渲染到透明条上（含行内图片标记）
                height = max(item.height, 1)
                # 行内图片可能比记录行高更高，按实际内容撑高
                for frag in item.fragments:
                    if frag.is_image_mark and frag.width == 0:
                        frag.calculate_width(self.font)
                for frag in item.fragments:
                    if frag.is_image_mark:
                        img = frag.render_image()
                        if img and img.get_height() > height:
                            height = img.get_height()

                surface = pygame.Surface((max_w, height), pygame.SRCALPHA)
                x = 0
                for frag in item.fragments:
                    if frag.width == 0:
                        frag.calculate_width(self.font)
                    if frag.is_image_mark:
                        img = frag.render_image()
                        if img:
                            surface.blit(img, (x, 0))
                        else:
                            # 图片加载失败：占位符
                            pygame.draw.rect(surface, self.placeholder_color,
                                             (x, 0, max(frag.width, 1), height - 2))
                        x += frag.width
                    else:
                        text_surface = self.font.render(frag.text, True, frag.color)
                        surface.blit(text_surface,
                                     (x, (height - text_surface.get_height()) // 2))
                        x += frag.width
                return surface, x

            elif item.type == ContentType.IMAGE_MARK:
                img = self._render_image_mark_surface(item)
                if img is None:
                    img = self._placeholder_surface(270, max(item.height - 10, 10))
                return img, img.get_width()

            elif item.type == ContentType.IMAGE_STACK:
                img = self._render_image_stack_surface(item)
                if img is None:
                    img = self._placeholder_surface(270, max(item.height - 10, 10))
                return img, img.get_width()

            elif item.type == ContentType.IMAGE:
                # 旧图片类型（向后兼容）
                img = self._get_image_from_cache(item.data)
                if img is not None:
                    return img, img.get_width()
                return None, 0

            else:  # DIVIDER / MENU
                text_surface = self.font.render(item.data, True, item.color)
                surface = pygame.Surface((max_w, max(item.height, 1)), pygame.SRCALPHA)
                ty = (max(item.height, 1) - text_surface.get_height()) // 2
                if item.type == ContentType.DIVIDER:
                    surface.blit(text_surface,
                                 ((max_w - text_surface.get_width()) // 2, ty))
                else:
                    surface.blit(text_surface, (10, ty))
                return surface, text_surface.get_width()

        except Exception as e:
            print(f"盒内项渲染失败: {e}")
            return None, 0

    def _render_image_mark_surface(self, item):
        """[盒子模型] 单张图片标记 → surface（LRU缓存+裁剪+按size缩放，重排时跑一次）"""
        metadata = item.metadata
        img_url = metadata.get('img_url')
        img_info = metadata.get('img_info')

        if not img_url or not img_info:
            return None

        image = self._get_image_from_cache(img_info.get('path'))
        if not image:
            return None

        # 裁剪：优先 PRINTIMG 传入的 clip 参数，其次 CSV 默认值
        param_clip = metadata.get('clip_pos')
        if param_clip:
            clip_x, clip_y = param_clip
        else:
            clip_x = img_info.get('clip_x', 0)
            clip_y = img_info.get('clip_y', 0)

        clip_w = img_info.get('original_width', image.get_width())
        clip_h = img_info.get('original_height', image.get_height())

        img_w, img_h = image.get_size()
        needs_crop = (clip_x > 0 or clip_y > 0 or clip_w < img_w or clip_h < img_h)

        if needs_crop:
            safe_w = min(clip_w, img_w - clip_x)
            safe_h = min(clip_h, img_h - clip_y)
            if safe_w > 0 and safe_h > 0:
                image = image.subsurface(pygame.Rect(clip_x, clip_y, safe_w, safe_h))

        # 指定了 size 才缩放（设计分辨率坐标）
        size = metadata.get('size')
        if size:
            final_width, final_height = size
            if final_width > 0 and final_height > 0 and (final_width, final_height) != image.get_size():
                image = pygame.transform.smoothscale(image, (final_width, final_height))

        return image

    def _render_image_stack_surface(self, item):
        """[盒子模型] 图片叠加 → 合成 surface（重排时合成一次，不再每帧重建）"""
        metadata = item.metadata

        template_width = metadata.get('template_width', self.screen_width - 20)
        template_height = metadata.get('template_height', 300)

        img_elements = metadata.get('img_elements', [])
        if not img_elements:
            return None

        try:
            final_surface = pygame.Surface(
                (max(template_width, 1), max(template_height, 1)), pygame.SRCALPHA)

            for element in img_elements:
                info = element['info']
                img_path = info.get('path')

                # 1. [LRU] 从缓存获取原始图片（不要修改缓存里的对象!）
                image = self._get_image_from_cache(img_path)
                if not image:
                    continue

                # 2. [裁剪] 定义区域与原图不一致时裁剪
                csv_x = info.get('clip_x', 0)
                csv_y = info.get('clip_y', 0)
                csv_w = info.get('original_width', image.get_width())
                csv_h = info.get('original_height', image.get_height())
                img_w, img_h = image.get_size()

                needs_crop = (csv_x > 0 or csv_y > 0 or csv_w < img_w or csv_h < img_h)
                if needs_crop:
                    safe_w = min(csv_w, img_w - csv_x)
                    safe_h = min(csv_h, img_h - csv_y)
                    if safe_w > 0 and safe_h > 0:
                        image = image.subsurface(
                            pygame.Rect(csv_x, csv_y, safe_w, safe_h))

                # 3. [缩放] 定义了目标尺寸时缩放（设计分辨率坐标）
                target_w = info.get('target_width', image.get_width())
                target_h = info.get('target_height', image.get_height())
                if target_w > 0 and target_h > 0 and (target_w, target_h) != image.get_size():
                    image = pygame.transform.smoothscale(image, (target_w, target_h))

                # 4. [偏移并绘制]
                final_surface.blit(image,
                                   (info.get('offset_x', 0), info.get('offset_y', 0)))

            return final_surface

        except Exception as e:
            print(f"渲染图片叠加失败: {e}")
            return None

    def _placeholder_surface(self, w, h, mark="?"):
        """图片渲染失败的占位 surface"""
        surface = pygame.Surface((max(w, 1), max(h, 1)), pygame.SRCALPHA)
        surface.fill(self.placeholder_color)
        text = self.font.render(mark, True, (255, 200, 100))
        surface.blit(text, ((surface.get_width() - text.get_width()) // 2,
                            (surface.get_height() - text.get_height()) // 2))
        return surface

    def scroll_up(self, amount: int = 1):
        """向上滚动（查看更旧内容）：盒子沿流向旧侧移动"""
        max_gap = max(0, len(self.history) - 1)
        if self.tail_gap < max_gap:
            self.tail_gap = min(max_gap, self.tail_gap + amount)
            self.box_dirty = True

    def scroll_down(self, amount: int = 1):
        """向下滚动（查看更新内容）：盒子沿流向新侧移动，回到流尾即恢复追更"""
        if self.tail_gap > 0:
            self.tail_gap = max(0, self.tail_gap - amount)
            self.box_dirty = True
            if self.tail_gap == 0:
                self.new_content_below = False

    def scroll_to_bottom(self):
        """滚动到底部 - 回到流尾（追更状态）"""
        self.tail_gap = 0
        self.new_content_below = False
        self.box_dirty = True

    def scroll_to_top(self):
        """滚动到顶部 - 盒子移到流的最旧端"""
        self.tail_gap = max(0, len(self.history) - 1)
        self.box_dirty = True

    def clear_history(self):
        """清空历史（流）并重置盒子"""
        self.history = []
        self.tail_gap = 0
        self.new_content_below = False
        self.image_cache = OrderedDict()
        self.box_dirty = True
        # 在日志中记录清空操作
        self._write_to_log("[系统] 历史记录已清空")

    # dynamic_loader.py - 盒子模型的 draw

    def draw(self, screen: pygame.Surface):
        """
        [盒子模型] 绘制：盒脏才重排，帧内纯 blit 预渲染 surface。
        零 font.render、零 smoothscale、零逐帧命中重算。
        """
        if self.box_dirty:
            self._compose_box()

        for surface, y in self.box_items:
            screen.blit(surface, (10, y))

        # 回看中来了新内容：右下角提示（懒渲染一次，不逐帧渲染文字）
        if self.new_content_below and self.tail_gap > 0:
            if self._new_content_hint is None:
                text = self.font.render("↓ 有新内容", True, (100, 200, 255))
                hint = pygame.Surface((text.get_width() + 8, text.get_height() + 4),
                                      pygame.SRCALPHA)
                hint.blit(text, (4, 2))
                self._new_content_hint = hint
            screen.blit(self._new_content_hint,
                        (self.screen_width - self._new_content_hint.get_width() - 15,
                         10 + self.content_area_height - self._new_content_hint.get_height() - 5))

        # 绘制滚动条（如果盒外还有内容）
        if self.scrollbar_visible and self.history:
            self._draw_scrollbar(screen)

    def _draw_scrollbar(self, screen: pygame.Surface):
        """[盒子模型] 滚动条：滑块位置由 tail_gap（盒底之下的项数）决定，纯算术"""
        total = len(self.history)
        visible = max(1, self._box_line_count)
        ratio = min(1.0, visible / total)

        # 滚动条轨道
        scrollbar_x = self.screen_width - self.scrollbar_width - 5
        pygame.draw.rect(
            screen,
            self.scrollbar_color,
            (scrollbar_x, 10, self.scrollbar_width, self.content_area_height),
            border_radius=3
        )

        # 滚动条滑块：tail_gap=0（流尾）在底，最大 gap 在顶
        scrollbar_height = max(20, self.content_area_height * ratio)
        frac = self.tail_gap / max(1, total - visible)
        scrollbar_y = 10 + frac * (self.content_area_height - scrollbar_height)

        pygame.draw.rect(
            screen,
            self.scrollbar_active_color,
            (scrollbar_x, scrollbar_y, self.scrollbar_width, scrollbar_height),
            border_radius=3
        )

    def handle_event(self, event: pygame.event.Event):
        """
        处理PyGame事件

        Args:
            event: PyGame事件
        """
        if event.type == pygame.MOUSEWHEEL:
            # 处理鼠标滚轮
            if event.y > 0:  # 向上滚动
                self.scroll_up(3)
            elif event.y < 0:  # 向下滚动
                self.scroll_down(3)
            return True

        elif event.type == pygame.KEYDOWN:
            # 处理键盘滚动
            if event.key == pygame.K_UP:
                self.scroll_up(1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_down(1)
                return True
            elif event.key == pygame.K_PAGEUP:
                # [盒子模型] 整盒翻页：容量能装多少文本行
                self.scroll_up(max(1, self.content_area_height // self.line_height))
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_down(max(1, self.content_area_height // self.line_height))
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_to_top()
                return True
            elif event.key == pygame.K_END:
                self.scroll_to_bottom()
                return True

        return False

    def get_scroll_info(self) -> Dict:
        """[盒子模型] 滚动信息（字段兼容 ERAconsole 的滚动位置显示）"""
        total_items = len(self.history)
        visible_items = self._box_line_count
        at_bottom = self.tail_gap == 0
        at_top = (not at_bottom) and self.tail_gap >= max(0, total_items - visible_items)

        return {
            "total_items": total_items,
            "visible_items": visible_items,
            "scroll_offset": self.tail_gap,
            "at_top": at_top,
            "at_bottom": at_bottom
        }
