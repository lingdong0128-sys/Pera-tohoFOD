# dynamic_loader.py
import pygame
import os
import json
import time
from typing import List, Tuple, Dict, Optional
from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    DIVIDER = "divider"
    MENU = "menu"

class ConsoleContent:
    """控制台内容项"""
    def __init__(self, content_type: ContentType, data, color=(255, 255, 255), height=30, 
                 metadata=None):
        self.type = content_type
        self.data = data  # 文本内容或图片路径
        self.color = color
        self.height = height  # 此项的高度（像素）
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
    def __repr__(self):
        return f"ConsoleContent(type={self.type}, data={self.data[:50] if isinstance(self.data, str) else self.data})"

class DynamicLoader:
    """动态加载器 - 支持滚动和日志记录"""
    
    def __init__(self, screen_width: int, screen_height: int, font, 
                 input_area_height: int = 40, log_file: str = "log.txt"):
        """
        初始化动态加载器
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            font: PyGame字体对象
            input_area_height: 输入区域高度
            log_file: 日志文件路径
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.input_area_height = input_area_height
        
        # 内容管理
        self.history: List[ConsoleContent] = []  # 完整的历史记录
        self.max_history_length = 10000  # 最大历史记录数
        self.current_display: List[ConsoleContent] = []  # 当前显示的内容
        self.max_visible_items = 30  # 最大可见项目数
        
        # 滚动控制
        self.scroll_offset = 0  # 滚动偏移（项目数）
        self.line_height = 30  # 每行高度
        self.content_area_height = screen_height - input_area_height - 20  # 内容区域高度
        
        # 滚动条
        self.scrollbar_width = 10
        self.scrollbar_visible = False
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_active_color = (150, 150, 150)
        
        # 日志文件
        self.log_file = log_file
        self._init_log_file()
        
        # 缓存
        self.text_surface_cache = {}  # 文本surface缓存
        self.image_cache = {}  # 图片缓存
        
    def _init_log_file(self):
        """初始化日志文件"""
        try:
            # 创建日志文件目录（如果不存在）
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # 写入初始信息
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"会话开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
        except Exception as e:
            print(f"初始化日志文件失败: {e}")
    
# dynamic_loader.py - 修复 add_text 方法

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
        
        # !!! 关键修复：正确处理空文本 !!!
        # 如果文本为None或空字符串，添加一个空行
        if text is None or text == "":
            item = ConsoleContent(ContentType.TEXT, "", color, self.line_height)
            self.history.append(item)
            self._write_to_log("")
            added_items.append(item)
            self._update_current_display()
            
            # 自动滚动到底部（如果已经在底部附近）
            if self.scroll_offset <= 5:  # 如果在底部5行以内
                self.scroll_to_bottom()
            
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
            max_width = self.screen_width - 40 - (self.scrollbar_width if self.scrollbar_visible else 0)
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
            item = ConsoleContent(ContentType.TEXT, line, color, self.line_height)
            self.history.append(item)
            self._write_to_log(line)
            added_items.append(item)
        
        # 限制历史记录长度
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]
        
        # 更新当前显示
        self._update_current_display()
        
        # 自动滚动到底部（如果已经在底部附近）
        if self.scroll_offset <= 5:  # 如果在底部5行以内
            self.scroll_to_bottom()
        
        return added_items
    
    def add_image(self, image_path: str, max_height: int = 200) -> Optional[ConsoleContent]:
        """
        添加图片到历史记录
        
        Args:
            image_path: 图片路径
            max_height: 图片最大高度
            
        Returns:
            添加的内容项或None
        """
        try:
            if os.path.exists(image_path):
                # 加载图片
                image = pygame.image.load(image_path).convert_alpha()
                
                # 调整大小
                img_width, img_height = image.get_size()
                if img_height > max_height:
                    scale_factor = max_height / img_height
                    new_width = int(img_width * scale_factor)
                    new_height = max_height
                    image = pygame.transform.smoothscale(image, (new_width, new_height))
                
                # 缓存图片
                self.image_cache[image_path] = image
                
                # 创建内容项
                item = ConsoleContent(
                    ContentType.IMAGE, 
                    image_path, 
                    height=new_height + 10,  # 图片高度 + 边距
                    metadata={"surface": image, "width": new_width, "height": new_height}
                )
                
                self.history.append(item)
                self._write_to_log(f"[图片: {os.path.basename(image_path)}]")
                self._update_current_display()
                return item
            else:
                error_msg = f"图片文件不存在: {image_path}"
                self.add_text(error_msg, (255, 100, 100))
                return None
        except Exception as e:
            error_msg = f"加载图片失败: {e}"
            self.add_text(error_msg, (255, 100, 100))
            return None
    
    def add_divider(self, char: str = "─", length: int = 40, color: Tuple[int, int, int] = (150, 150, 150)):
        """
        添加分割线
        
        Args:
            char: 分割线字符
            length: 分割线长度
            color: 颜色
        """
        divider_text = char * length
        item = ConsoleContent(ContentType.DIVIDER, divider_text, color, self.line_height)
        self.history.append(item)
        self._write_to_log(divider_text)
        self._update_current_display()
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
            content_item = ConsoleContent(ContentType.MENU, item, color, self.line_height)
            self.history.append(content_item)
            self._write_to_log(item)
            added_items.append(content_item)
        
        self._update_current_display()
        return added_items
    
    def _write_to_log(self, text: str):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("[%H:%M:%S] ")
                f.write(timestamp + text + "\n")
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def _update_current_display(self):
        """更新当前显示的内容（根据滚动偏移）"""
        start_idx = max(0, len(self.history) - self.max_visible_items - self.scroll_offset)
        end_idx = len(self.history) - self.scroll_offset
        
        if start_idx < 0:
            start_idx = 0
        
        self.current_display = self.history[start_idx:end_idx]
        
        # 更新滚动条可见性
        total_height = sum(item.height for item in self.history)
        self.scrollbar_visible = total_height > self.content_area_height
    
    def scroll_up(self, amount: int = 1):
        """向上滚动"""
        max_scroll = len(self.history) - self.max_visible_items
        if max_scroll < 0:
            max_scroll = 0
        
        self.scroll_offset = min(max_scroll, self.scroll_offset + amount)
        self._update_current_display()
    
    def scroll_down(self, amount: int = 1):
        """向下滚动"""
        self.scroll_offset = max(0, self.scroll_offset - amount)
        self._update_current_display()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.scroll_offset = 0
        self._update_current_display()
    
    def scroll_to_top(self):
        """滚动到顶部"""
        max_scroll = len(self.history) - self.max_visible_items
        if max_scroll > 0:
            self.scroll_offset = max_scroll
        else:
            self.scroll_offset = 0
        self._update_current_display()
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.current_display = []
        self.scroll_offset = 0
        
        # 在日志中记录清空操作
        self._write_to_log("[系统] 历史记录已清空")
    
    def get_visible_content(self) -> List[ConsoleContent]:
        """获取当前可见的内容"""
        return self.current_display
    
    def draw(self, screen: pygame.Surface, y_offset: int = 0):
        """
        绘制内容到屏幕
        
        Args:
            screen: PyGame屏幕Surface
            y_offset: Y轴偏移
        """
        current_y = 10 + y_offset
        
        # 绘制可见内容
        for item in self.current_display:
            if current_y + item.height > self.content_area_height + y_offset:
                break
                
            if item.type == ContentType.TEXT:
                # 绘制文本
                text_surface = self.font.render(item.data, True, item.color)
                screen.blit(text_surface, (10, current_y))
                current_y += item.height
                
            elif item.type == ContentType.IMAGE:
                # 绘制图片
                if item.data in self.image_cache:
                    image = self.image_cache[item.data]
                    img_x = (self.screen_width - item.metadata["width"]) // 2
                    screen.blit(image, (img_x, current_y))
                    current_y += item.height
                    
            elif item.type == ContentType.DIVIDER:
                # 绘制分割线
                text_surface = self.font.render(item.data, True, item.color)
                text_width = text_surface.get_width()
                x_pos = (self.screen_width - text_width) // 2
                screen.blit(text_surface, (x_pos, current_y))
                current_y += item.height
                
            elif item.type == ContentType.MENU:
                # 绘制菜单项
                text_surface = self.font.render(item.data, True, item.color)
                screen.blit(text_surface, (20, current_y))
                current_y += item.height
        
        # 绘制滚动条（如果需要）
        if self.scrollbar_visible and len(self.history) > 0:
            self._draw_scrollbar(screen, y_offset)
    
    def _draw_scrollbar(self, screen: pygame.Surface, y_offset: int):
        """绘制滚动条"""
        total_height = sum(item.height for item in self.history)
        visible_ratio = self.content_area_height / total_height
        
        # 滚动条轨道
        scrollbar_x = self.screen_width - self.scrollbar_width - 5
        pygame.draw.rect(
            screen, 
            self.scrollbar_color, 
            (scrollbar_x, y_offset + 10, self.scrollbar_width, self.content_area_height - 20),
            border_radius=3
        )
        
        # 滚动条滑块
        if visible_ratio < 1.0:
            scrollbar_height = max(20, self.content_area_height * visible_ratio)
            scrollbar_y = y_offset + 10 + (self.scroll_offset / len(self.history)) * (self.content_area_height - scrollbar_height - 20)
            
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
                self.scroll_up(10)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_down(10)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_to_top()
                return True
            elif event.key == pygame.K_END:
                self.scroll_to_bottom()
                return True
        
        return False
    
    def get_history_count(self) -> int:
        """获取历史记录数量"""
        return len(self.history)
    
    def get_scroll_info(self) -> Dict:
        """获取滚动信息"""
        total_items = len(self.history)
        visible_items = len(self.current_display)
        max_scroll = max(0, total_items - self.max_visible_items)
        
        return {
            "total_items": total_items,
            "visible_items": visible_items,
            "scroll_offset": self.scroll_offset,
            "max_scroll": max_scroll,
            "at_top": self.scroll_offset >= max_scroll and max_scroll > 0,
            "at_bottom": self.scroll_offset == 0
        }