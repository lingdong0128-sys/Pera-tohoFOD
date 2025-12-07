# main.py 修改部分
import pygame
import sys
import time
import json
import os
from dynamic_loader import DynamicLoader, ContentType  # 导入动态加载器
class EventManager:
    def __init__(self, console_instance):
        self.console = console_instance
        self.events = {}  # 存储事件函数
        self.eventid={}#存事件的对应id，目前还没什么用
        self.load_events()
    def load_events(self):
        """动态加载事件文件"""
        import importlib
        import os
        events_dir = "./events"  # 事件文件目录
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)
        
        # 扫描事件文件
        for file in os.listdir(events_dir):
            if file.endswith(".py"):
                module_name = f"events.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # 查找事件函数（以 event_ 开头的函数）
                    for attr_name in dir(module):
                        if attr_name.startswith("event_"):
                            event_func = getattr(module, attr_name)
                            event_key = attr_name[6:]  # 去掉 "event_"
                            event_id=getattr(event_func,'event_trigger',event_key)#因为要把对应id读取进键值对应表所以这里直接读取他的触发按键
                            self.events[event_key] = event_func
                            self.eventid[event_id]=event_key
                            self.console.PRINT(f"已加载事件: {event_key}")
                except Exception as e:
                    self.console.PRINT(f"加载事件失败 {file}: {e}", (255, 200, 200))
    
    def trigger_event(self, event_name, things_instance):
        """触发指定事件"""
        if event_name in self.events:
            # 传递 thethings 实例给事件函数
            self.events[event_name](things_instance)
class SimpleERAConsole:
    from init import initall
    
    def __init__(self):
        pygame.init()
        self.screen_width = 1600
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("ERA Console")
        
        # 字体设置
        self.font = pygame.font.Font('./font/luoli.ttf', 24)
        self.line_height = 30
        
        # 输入区域高度
        self.input_area_height = 40
        
        # 初始化动态加载器
        self.loader = DynamicLoader(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            font=self.font,
            input_area_height=self.input_area_height,
            log_file="./logs/game_log.txt"
        )
        
        # 输入相关
        self.input_text = ""
        self.input_history = []  # 输入历史记录
        self.input_history_index = -1  # 当前输入历史索引
        self.cursor_visible = True
        self.cursor_timer = 0
        self.running = True
        
        # 初始化音乐盒和音乐列表
        self.music_box = None
        self.music_list = {}
        self.current_music_name = None
        self.clickable_regions = []  # 存储所有可点击区域
        self.clickable_region_counter = 0  # 可点击区域计数器
        
        # 加载图片数据
        self.image_data = self._load_image_data()
        # 添加示例文本用于测试滚动
        #self._add_test_content()
    def PRINTIMG(self, url, clip_pos=None, size=None, click=None):
        """显示图片到控制台"""
        try:
            # 检查图片数据是否存在
            if url not in self.image_data:
                self.PRINT(f"图片 {url} 不存在于数据中", (255, 200, 200))
                return
            
            img_info = self.image_data[url]
            img_path = os.path.join("./img/13/", img_info['filename'])  # 假设图片在images目录
            
            # 检查图片文件是否存在
            if not os.path.exists(img_path):
                # 尝试其他路径
                img_path = os.path.join("./", img_info['filename'])
                if not os.path.exists(img_path):
                    self.PRINT(f"图片文件不存在: {img_info['filename']}", (255, 200, 200))
                    return
            
            # 加载图片
            try:
                image = pygame.image.load(img_path).convert_alpha()
            except Exception as e:
                self.PRINT(f"加载图片失败 {img_path}: {e}", (255, 200, 200))
                return
            
            # 获取裁剪区域
            if clip_pos is None:
                clip_x, clip_y = img_info['x'], img_info['y']
            else:
                clip_x, clip_y = clip_pos
            
            clip_width, clip_height = img_info['width'], img_info['height']
            
            # 确保裁剪区域在图片范围内
            img_width, img_height = image.get_size()
            if clip_x + clip_width > img_width:
                clip_width = img_width - clip_x
            if clip_y + clip_height > img_height:
                clip_height = img_height - clip_y
            
            # 裁剪图片
            if clip_width > 0 and clip_height > 0:
                clip_rect = pygame.Rect(clip_x, clip_y, clip_width, clip_height)
                clipped_image = image.subsurface(clip_rect)
            else:
                self.PRINT(f"裁剪区域无效: {clip_x}, {clip_y}, {clip_width}, {clip_height}", (255, 200, 200))
                return
            
            # 调整大小
            if size is not None:
                target_width, target_height = size
                clipped_image = pygame.transform.scale(clipped_image, (target_width, target_height))
            # 将图片添加到动态加载器
            # 如果设置了click参数，添加可点击区域
            if click is not None:
                item = self.loader.add_clickable_image(clipped_image, url, click)
            else:
                item = self.loader.add_image_surface(clipped_image, url)
            
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            
        except Exception as e:
            self.PRINT(f"显示图片失败 {url}: {e}", (255, 200, 200))

    def _load_image_data(self):
        """加载13.csv中的图片数据"""
        image_data = {}
        csv_path = "./img/13/13.csv"
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8-sig') as f:  # 使用utf-8-sig处理BOM
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(';'):  # 跳过注释行
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 2:
                                name = parts[0]
                                filename = parts[1]
                                if len(parts) >= 6:  # 有完整的裁剪信息
                                    try:
                                        x, y, width, height = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                                        image_data[name] = {
                                            'filename': filename,
                                            'x': x,
                                            'y': y,
                                            'width': width,
                                            'height': height
                                        }
                                    except ValueError:
                                        # 如果解析失败，使用默认值
                                        image_data[name] = {
                                            'filename': filename,
                                            'x': 0,
                                            'y': 0,
                                            'width': 270,
                                            'height': 270
                                        }
                                else:
                                    image_data[name] = {
                                        'filename': filename,
                                        'x': 0,
                                        'y': 0,
                                        'width': 270,
                                        'height': 270
                                    }
                self.PRINT(f"已加载图片数据: {len(image_data)} 条记录", (200, 200, 255))
            except Exception as e:
                self.PRINT(f"加载图片数据失败: {e}", (255, 200, 200))
        else:
            self.PRINT(f"图片数据文件不存在: {csv_path}", (255, 200, 200))
        
        return image_data
    # main.py - 修复 PRINT 方法
    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        # 委托给动态加载器处理
        click_value = self.loader.handle_mouse_click(pos)
        
        if click_value:
            # 模拟输入
            self.input_text = click_value
            
            # 显示用户输入
            self.loader.add_text(f"> {click_value}", (255, 255, 200))
            self.loader.add_text("")  # 空行
            
            # 清空点击区域（避免重复点击）
            self.loader.clear_clickable_regions()
            
            # 返回输入值
            return click_value
        
        return None
    
    def PRINT(self, text=None, colors=(255, 255, 255), click=None):
        """输出文本到控制台 - 支持点击功能"""
        # 处理空文本
        if text is None:
            text = ""
        
        # 使用加载器的新方法
        if click is not None:
            self.loader.add_clickable_text(text, colors, click)
        else:
            self.loader.add_text(text, colors)
        
        # 刷新显示
        self._draw_display()
        pygame.display.flip()
    def PRINT_MENU(self, items, colors=(200, 200, 255)):
        """输出菜单到控制台"""
        self.loader.add_menu(items, colors)
        self._draw_display()
        pygame.display.flip()
    
    def PRINT_DIVIDER(self, char="─", length=40, colors=(150, 150, 150)):
        """输出分割线"""
        self.loader.add_divider(char, length, colors)
        self._draw_display()
        pygame.display.flip()
    
    # main.py - 修复 INPUT 方法中的空行处理

    def INPUT(self):
            """获取用户输入 - 支持功能键和鼠标点击"""
            self.input_text = ""
            waiting_for_input = True
            
            while waiting_for_input and self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                        return None
                    
                    # 先处理动态加载器事件（滚动等）
                    if self.loader.handle_event(event):
                        self._draw_display()
                        pygame.display.flip()
                        continue
                    
                    # 处理鼠标点击（修改为使用动态加载器的方法）
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # 左键点击
                            clicked_input = self._handle_mouse_click(event.pos)
                            if clicked_input:
                                return clicked_input
                    
                    elif event.type == pygame.KEYUP:
                        # 功能键处理
                        if event.key == pygame.K_RETURN:
                            user_input = self.input_text.strip()
                            
                            if user_input:
                                # 保存到输入历史
                                self.input_history.append(user_input)
                                self.input_history_index = -1
                                
                                # 显示用户输入（不同颜色）
                                self.loader.add_text(f"> {user_input}", (255, 255, 200))
                            
                            # 总是添加一个空行，即使输入为空
                            self.loader.add_text("")  # 空行
                            
                            # 重置输入文本并返回
                            self.input_text = ""
                            waiting_for_input = False
                            return user_input
                        
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        
                        elif event.key == pygame.K_UP:
                            # 向上浏览输入历史
                            if self.input_history:
                                if self.input_history_index < len(self.input_history) - 1:
                                    self.input_history_index += 1
                                    self.input_text = self.input_history[-(self.input_history_index + 1)]
                        
                        elif event.key == pygame.K_DOWN:
                            # 向下浏览输入历史
                            if self.input_history_index > 0:
                                self.input_history_index -= 1
                                self.input_text = self.input_history[-(self.input_history_index + 1)]
                            elif self.input_history_index == 0:
                                self.input_history_index = -1
                                self.input_text = ""
                        
                        else:
                            # 只接受可打印字符
                            if event.unicode.isprintable():
                                self.input_text += event.unicode
                
                # 绘制界面
                self._draw_display()
                
                # 光标闪烁效果
                self.cursor_timer += 1
                if self.cursor_timer > 30:  # 每半秒切换一次
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_timer = 0
                
                pygame.display.flip()
                pygame.time.Clock().tick(60)
            
            return None
    def _init_background_music(self):
        """初始化背景音乐 - 从global_key['musicbox']获取音乐列表"""
        try:
            # 检查是否有init属性
            if not hasattr(self, 'init') or not self.init:
                self.PRINT("初始化数据未加载，无法初始化音乐", colors=(255, 200, 200))
                return
            
            # 从全局变量获取音乐列表
            if hasattr(self.init, 'global_key') and 'musicbox' in self.init.global_key:
                self.music_list = self.init.global_key['musicbox']
                self.PRINT(f"已加载音乐列表，共{len(self.music_list)}首音乐")
                
                # 如果有音乐，播放第一首
                if self.music_list:
                    first_music_name = list(self.music_list.keys())[0]
                    first_music_path = self.music_list[first_music_name]
                    
                    # 检查音乐文件是否存在
                    if os.path.exists(first_music_path):
                        self.music_box = MusicBox(first_music_path)
                        self.current_music_name = first_music_name
                        # 播放背景音乐（无限循环）
                        self.music_box.play(loops=-1)
                        self.PRINT(f"背景音乐已加载: {first_music_name}")
                    else:
                        self.PRINT(f"背景音乐文件不存在: {first_music_path}", colors=(255, 200, 200))
                        self.PRINT("请检查音乐文件路径", colors=(255, 200, 200))
                else:
                    self.PRINT("音乐列表为空，无法播放背景音乐", colors=(255, 200, 200))
            else:
                self.PRINT("全局变量中没有找到musicbox键", colors=(255, 200, 200))
        except Exception as e:
            self.PRINT(f"初始化音乐失败: {e}", colors=(255, 200, 200))
    
    def _draw_display(self):
        """绘制整个界面"""
        # 清屏
        self.screen.fill((0, 0, 0))
        
        # 绘制动态加载器的内容
        self.loader.draw(self.screen)
        
        # 绘制输入文本和光标（始终在左下角）
        input_y = self.screen_height - self.input_area_height + 10
        input_surface = self.font.render("> " + self.input_text, True, (255, 255, 255))
        self.screen.blit(input_surface, (10, input_y))
        
        # 绘制光标
        if self.cursor_visible:
            cursor_x = 10 + self.font.size("> " + self.input_text)[0]
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (cursor_x, input_y),
                (cursor_x, input_y + 20),
                2
            )
        
        # 绘制滚动提示
        scroll_info = self.loader.get_scroll_info()
        if scroll_info["total_items"] > scroll_info["visible_items"]:
            # 显示滚动位置信息
            scroll_text = f"行: {scroll_info['total_items'] - scroll_info['scroll_offset'] - scroll_info['visible_items'] + 1}-{scroll_info['total_items'] - scroll_info['scroll_offset']} / {scroll_info['total_items']}"
            info_surface = self.font.render(scroll_text, True, (150, 150, 150))
            info_x = self.screen_width - info_surface.get_width() - 20
            self.screen.blit(info_surface, (info_x, self.screen_height - 60))
            
            # 显示滚动提示
            if not scroll_info["at_bottom"]:
                hint_surface = self.font.render("↑ 滚动查看历史", True, (100, 150, 255))
                self.screen.blit(hint_surface, (self.screen_width - hint_surface.get_width() - 20, 10))
    
    def clear_screen(self):
        """清屏"""
        self.loader.clear_history()
        self.loader.clear_clickable_regions()  # 使用加载器的方法
        self.PRINT("控制台已清空", (200, 255, 200))
    
    def show_scroll_info(self):
        """显示滚动信息"""
        scroll_info = self.loader.get_scroll_info()
        self.PRINT_DIVIDER("=", 40)
        self.PRINT("滚动信息:", (200, 200, 255))
        self.PRINT(f"总行数: {scroll_info['total_items']}", (200, 200, 200))
        self.PRINT(f"可见行数: {scroll_info['visible_items']}", (200, 200, 200))
        self.PRINT(f"滚动偏移: {scroll_info['scroll_offset']}", (200, 200, 200))
        self.PRINT(f"是否在顶部: {'是' if scroll_info['at_top'] else '否'}", (200, 200, 200))
        self.PRINT(f"是否在底部: {'是' if scroll_info['at_bottom'] else '否'}", (200, 200, 200))
        self.PRINT_DIVIDER("=", 40)
    
    
    def init_all(self):
        """初始化所有组件，包括数据和音乐"""
        try:
            from init import initall
            init = initall("./csv/")
            self.init = init  # 这里设置self.init属性
            
            # 使用动态加载器输出
            self.loader.add_divider("=", 60, (100, 200, 100))
            self.loader.add_text("少女祈祷中...", (200, 255, 200))
            
            for i in init.charaters_key:
                chara_name = init.charaters_key[i].get('名前', '未知角色')
                self.loader.add_text(f"已加载角色：{chara_name}", (200, 220, 255))
            
            time.sleep(1)
            self.loader.add_text("角色全部载入~", (100, 255, 100))
            
            for i in init.global_key:
                self.loader.add_text(f"已加载全局设置：{i}", (200, 200, 255))
            
            time.sleep(1)
            self.loader.add_text("全部载入~", (100, 255, 100))
            self.loader.add_divider("=", 60, (100, 200, 100))
            
            # 初始化背景音乐
            self._init_background_music()
            
            # 滚动到底部
            self.loader.scroll_to_bottom()
            
            return init
        except Exception as e:
            self.PRINT(f"初始化失败: {e}", colors=(255, 200, 200))
            self.PRINT("按任意键继续...")
            self.INPUT()
            return None
    
    def quit(self):
        """退出程序"""
        # 停止音乐
        if self.music_box:
            self.music_box.stop()
        
        # 记录退出日志
        self.loader.add_divider("=", 60, (255, 100, 100))
        self.loader.add_text("游戏结束，感谢游玩！", (255, 200, 100))
        self.loader.add_text(f"会话日志已保存到: {self.loader.log_file}", (200, 200, 200))
        
        # 短暂显示退出信息
        self._draw_display()
        pygame.display.flip()
        pygame.time.delay(1000)
        
        self.running = False
        pygame.quit()
        sys.exit()
# 在 main.py 的 thethings 类中添加新功能
class MusicBox:
    def __init__(self, url=None):
        """
        初始化音乐盒
        :param url: 音乐文件路径，可以是绝对路径或相对路径
        """
        # 初始化pygame mixer模块
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        self.url = url
        self.is_playing = False
        self.is_paused = False
        
        if url and os.path.exists(url):
            self.load_music(url)
    
    def load_music(self, url):
        """
        加载音乐文件
        :param url: 音乐文件路径
        :return: 成功加载返回True，否则返回False
        """
        try:
            if os.path.exists(url):
                pygame.mixer.music.load(url)
                self.url = url
                print(f"已加载音乐: {url}")
                return True
            else:
                print(f"错误: 文件不存在 - {url}")
                return False
        except pygame.error as e:
            print(f"加载音乐失败: {e}")
            return False
    
    def play(self, loops=0, start=0.0, fade_in=0):
        """
        播放音乐
        :param loops: 循环次数，0表示播放一次，-1表示无限循环
        :param start: 开始播放的位置（秒）
        :param fade_in: 淡入时间（毫秒）
        """
        if self.url and os.path.exists(self.url):
            if fade_in > 0:
                pygame.mixer.music.play(loops, start, fade_ms=fade_in)
            else:
                pygame.mixer.music.play(loops, start)
            self.is_playing = True
            self.is_paused = False
            print(f"开始播放: {self.url}")
        else:
            print("错误: 未加载有效的音乐文件")
    
    def stop(self):
        """停止音乐播放"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        print("音乐已停止")
    
    def pause(self):
        """暂停音乐播放"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            print("音乐已暂停")
    
    def unpause(self):
        """取消暂停，继续播放"""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print("继续播放音乐")
    
    def countion(self):
        """
        继续播放音乐（为保持与题目要求的兼容性）
        注意：方法名是countion而不是continue，因为continue是Python关键字
        """
        self.unpause()
    
    def newurl(self, url):
        """
        更换音乐文件并加载
        :param url: 新的音乐文件路径
        :return: 成功更换返回True，否则返回False
        """
        # 停止当前播放的音乐
        if self.is_playing:
            self.stop()
        
        # 加载新音乐
        return self.load_music(url)
    
    def is_loaded(self):
        """检查是否已加载音乐"""
        return self.url is not None and os.path.exists(self.url)
    
    def get_volume(self):
        """获取当前音量（0.0到1.0）"""
        return pygame.mixer.music.get_volume()
    
    def set_volume(self, volume):
        """
        设置音量
        :param volume: 音量值，范围0.0到1.0
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        print(f"音量已设置为: {volume:.2f}")
    
    def get_position(self):
        """获取当前播放位置（秒）"""
        return pygame.mixer.music.get_pos() / 1000.0
    
    def fadeout(self, duration):
        """
        淡出停止音乐
        :param duration: 淡出时间（毫秒）
        """
        pygame.mixer.music.fadeout(duration)
        self.is_playing = False
        self.is_paused = False
        print(f"音乐将在{duration}毫秒内淡出")
    
    def get_status(self):
        """获取音乐播放状态"""
        if not self.is_loaded():
            return "未加载音乐"
        elif self.is_paused:
            return "已暂停"
        elif self.is_playing:
            return "播放中"
        else:
            return "已停止"
class thethings:
    def __init__(self):
        self.console = SimpleERAConsole()
        # 在创建console后立即初始化所有组件
        self.console.init_all()
        self.input = ""
        self.event_manager = EventManager(self.console)
        self.charater_pwds = {}
        self.main()
    def main(self):
        # 首先初始化地图数据
        self.event_manager.trigger_event('map',self)
        running = True
        while running:
            self.input = self.console.INPUT()
            self.console.PRINTIMG("別立ち_服_睡衣_笑顔_13", clip_pos=(270,0))
            self.console.PRINT("[0]start",click='0')
            if self.input and self.input.lower() == "quit":
                running = False
            elif self.input:
                #在这里添加事件
                self.event_manager.trigger_event('start',self)
                self.console.PRINT("")
            # 处理退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    start = thethings()
"""    
这是为框架测试中用的一个，现在不需要了 
    def _add_test_content(self):
        添加测试内容以演示滚动功能
        colors = [
            (255, 255, 255),  # 白色
            (255, 200, 200),  # 淡红色
            (200, 255, 200),  # 淡绿色
            (200, 200, 255),  # 淡蓝色
            (255, 255, 200),  # 淡黄色
            (255, 200, 255),  # 淡紫色
        ]
        
        # 添加分割线
        self.loader.add_divider("=", 60, (100, 150, 255))
        self.loader.add_text("欢迎来到 ERA Console 动态加载器测试", (100, 200, 255))
        self.loader.add_text("使用鼠标滚轮或方向键滚动查看历史", (150, 150, 255))
        self.loader.add_divider("-", 50, (100, 100, 150))
        
        # 添加大量测试文本
        # 添加菜单示例
        self.loader.add_divider("=", 60, (150, 100, 255))
        self.loader.add_text("菜单示例:", (200, 150, 255))
        self.loader.add_menu([
            "[1] 开始游戏",
            "[2] 加载存档",
            "[3] 设置选项",
            "[4] 退出游戏"
        ])
        
        # 添加更多测试内容
        self.loader.add_divider("=", 60, (255, 150, 100))
        self.loader.add_text("滚动到底部以查看最新消息", (255, 200, 100))
        
        # 自动滚动到底部
        self.loader.scroll_to_bottom()
"""