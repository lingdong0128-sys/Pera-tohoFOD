import pygame
import sys
import time
import json
import os

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
        
        # 文本缓冲区
        self.output_lines = []
        self.max_lines = (self.screen_height - 40) // self.line_height  # 底部留出输入空间
        
        # 输入相关
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.running = True
        
        # 初始化音乐盒和音乐列表
        self.music_box = None
        self.music_list = {}  # 音乐列表 {音乐名: 音乐路径}
        self.current_music_name = None
        
        # 注意：这里不能直接调用init，因为init属性还不存在
        # 我们先初始化基本组件，然后在main中调用init_all
        
    def init_all(self):
        """初始化所有组件，包括数据和音乐"""
        try:
            from init import initall
            init = initall("./csv/")
            self.init = init  # 这里设置self.init属性
            
            self.PRINT("少女祈祷中...")
            for i in init.charaters_key:
                self.PRINT(f"已加载角色：{init.charaters_key[i].get('名前')}")
            time.sleep(1)
            self.PRINT("角色全部载入~")
            for i in init.global_key:
                self.PRINT(f"已加载全局设置：{i}")
            time.sleep(1)
            self.PRINT("全部载入~")
            
            # 初始化背景音乐
            self._init_background_music()
            
            return init
        except Exception as e:
            self.PRINT(f"初始化失败: {e}", colors=(255, 200, 200))
            self.PRINT("按任意键继续...")
            self.INPUT()
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
    
    def PRINT(self, text=None, colors=(255, 255, 255)):
        """输出文本到控制台 - 无输入时输出空行"""
        # 如果没有传入文本或文本为空，输出空行
        color_tuple = colors if isinstance(colors, tuple) and len(colors) >= 3 else (255, 255, 255)
        if text is None or text == "":
            self.output_lines.append(("", color_tuple))
            # 限制缓冲区大小
            if len(self.output_lines) > self.max_lines:
                self.output_lines = self.output_lines[-self.max_lines:]
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            return
        
        # 处理制表符
        text = text.replace('\t', '    ')  # 将制表符转换为4个空格
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
            
            # 如果超出屏幕宽度
            if text_width > self.screen_width - 20:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        # 将新行添加到输出缓冲区
        for line in lines:
            self.output_lines.append((line, color_tuple))
        
        # 限制缓冲区大小
        if len(self.output_lines) > self.max_lines:
            self.output_lines = self.output_lines[-self.max_lines:]
        
        # 刷新显示
        self._draw_display()
        pygame.display.flip()
    
    def INPUT(self):
        """获取用户输入"""
        self.input_text = ""
        waiting_for_input = True
        
        while waiting_for_input and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return None
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        user_input = self.input_text
                        self.input_text = ""
                        waiting_for_input = False
                        return user_input
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    
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
    
    def _draw_display(self):
        """绘制整个界面"""
        # 清屏
        self.screen.fill((0, 0, 0))
        
        # 绘制输出文本
        for i, (line, color) in enumerate(self.output_lines):
            text_surface = self.font.render(line, True, color)
            y_pos = 10 + i * self.line_height
            self.screen.blit(text_surface, (10, y_pos))
        
        # 绘制输入文本和光标（始终在左下角）
        input_y = self.screen_height - 30
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
    
    def quit(self):
        """退出程序"""
        # 停止音乐
        if self.music_box:
            self.music_box.stop()
        
        self.running = False
        pygame.quit()
        sys.exit()

# 使用示例
class thethings:
    def __init__(self):
        self.console = SimpleERAConsole()
        # 在创建console后立即初始化所有组件
        self.console.init_all()
        self.input = ""
        self.charater_pwds = {}
        self.main()
    
    def text(self):
        self.console.PRINT('[1]测试文本')
        if self.input == '1':
            self.console.PRINT("GREEN", (0, 255, 0))
            self.console.PRINT("BLUE", (0, 0, 255))
            self.console.PRINT("RED", (255, 0, 0))
    
    def getpwd(self, id='0'):
        self.console.PRINT('[0]查询位置')
        # 检查charater_pwds中是否有该角色
        if id in self.charater_pwds:
            mypwd = self.charater_pwds[id]
            if self.input == '0':
                self.console.PRINT(f"{self.console.init.charaters_key[id].get('名前')}当前位置....")
                self.console.PRINT(f"[{self.console.init.global_key['map'][mypwd['大地图']]}]" + f"[{self.console.init.global_key['map'][mypwd['小地图']]}]")
        else:
            self.console.PRINT(f"角色ID {id} 不存在", colors=(255, 200, 200))
    
    def map(self):
        import json
        try:
            with open('./json/map/map.json', 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # 先为所有角色设置默认位置
            for i in self.console.init.chara_ids:
                self.charater_pwds[i] = {
                    '大地图': '10000',
                    '小地图': '10001'
                }
            
            # 根据map.json更新角色位置
            for big_map, small_maps in map_data.items():
                for small_map, charater_list in small_maps.items():
                    for charater_id in charater_list:
                        if charater_id in self.charater_pwds:
                            self.charater_pwds[charater_id] = {
                                '大地图': big_map,
                                '小地图': small_map
                            }
        except Exception as e:
            self.console.PRINT(f"加载地图数据失败: {e}", colors=(255, 200, 200))
    
    def shop(self):
        self.console.PRINT("[3]商店")
        if self.input == '3':
            running = True
            page = 0
            items_per_page = 12
            
            # 检查是否有物品数据
            if not hasattr(self.console.init, 'global_key') or 'Item' not in self.console.init.global_key:
                self.console.PRINT("商店数据未加载", colors=(255, 200, 200))
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
                return
            
            items_data = self.console.init.global_key['Item']
            item_ids = list(items_data.keys())
            
            while running:
                self.console.output_lines = []
                
                self.console.PRINT("════════════ 商店 ════════════")
                
                if len(item_ids) == 0:
                    self.console.PRINT("商店目前没有商品")
                else:
                    total_pages = (len(item_ids) + items_per_page - 1) // items_per_page
                    start_idx = page * items_per_page
                    end_idx = min(start_idx + items_per_page, len(item_ids))
                    
                    self.console.PRINT(f"第 {page + 1}/{total_pages} 页")
                    self.console.PRINT("─" * 40)
                    
                    for i in range(start_idx, end_idx):
                        item_id = item_ids[i]
                        item_info = items_data[item_id]
                        
                        item_name = item_info.get('name', f'物品{item_id}')
                        price = item_info.get('price', 0)
                        
                        display_num = i - start_idx + 1
                        self.console.PRINT(f"{display_num:2d}. {item_name:<20} {price:>5}金币")
                    
                    self.console.PRINT("─" * 40)
                    self.console.PRINT("n:下一页  p:上一页  数字:查看详情  e:退出")
                    self.console.PRINT("请输入选择:")
                    
                    thisinput = self.console.INPUT().lower()
                    
                    if thisinput == 'e':
                        running = False
                    elif thisinput == 'n':
                        if page < total_pages - 1:
                            page += 1
                        else:
                            self.console.PRINT("已经是最后一页了")
                            self.console.PRINT("按任意键继续...")
                            self.console.INPUT()
                    elif thisinput == 'p':
                        if page > 0:
                            page -= 1
                        else:
                            self.console.PRINT("已经是第一页了")
                            self.console.PRINT("按任意键继续...")
                            self.console.INPUT()
                    elif thisinput.isdigit():
                        selected = int(thisinput)
                        if 1 <= selected <= (end_idx - start_idx):
                            actual_index = start_idx + selected - 1
                            item_id = item_ids[actual_index]
                            item_info = items_data[item_id]
                            
                            self.console.output_lines = []
                            
                            item_name = item_info.get('name', f'物品{item_id}')
                            price = item_info.get('price', 0)
                            description = item_info.get('idn', '暂无简介')
                            
                            self.console.PRINT(f"════════════ 物品详情 ════════════")
                            self.console.PRINT(f"名称: {item_name}")
                            self.console.PRINT(f"价格: {price}金币")
                            self.console.PRINT("")
                            self.console.PRINT("简介:")
                            self.console.PRINT(f"  {description}")
                            self.console.PRINT("")
                            
                            other_keys = [k for k in item_info.keys() if k not in ['name', 'price', 'idn']]
                            if other_keys:
                                self.console.PRINT("其他属性:")
                                for key in other_keys:
                                    self.console.PRINT(f"  {key}: {item_info[key]}")
                            
                            self.console.PRINT("")
                            self.console.PRINT("1. 购买")
                            self.console.PRINT("2. 返回商店")
                            self.console.PRINT("请选择:")
                            
                            choice = self.console.INPUT()
                            
                            if choice == '1':
                                self.console.PRINT(f"购买了 {item_name}，花费 {price} 金币！")
                                self.console.PRINT("按任意键继续...")
                                self.console.INPUT()
                        else:
                            self.console.PRINT("无效的选择")
                            self.console.PRINT("按任意键继续...")
                            self.console.INPUT()
                    else:
                        self.console.PRINT("无效的命令")
                        self.console.PRINT("按任意键继续...")
                        self.console.INPUT()
    
    def music_control(self):
        """音乐控制功能"""
        if not self.console.music_box:
            self.console.PRINT("音乐系统未初始化", colors=(255, 200, 200))
            self.console.PRINT("按任意键继续...")
            self.console.INPUT()
            return
        
        running = True
        while running:
            self.console.output_lines = []
            
            self.console.PRINT("════════════ 音乐控制 ════════════")
            
            # 显示当前音乐状态
            status = self.console.music_box.get_status()
            current_volume = self.console.music_box.get_volume()
            current_pos = self.console.music_box.get_position()
            
            self.console.PRINT(f"状态: {status}")
            if self.console.current_music_name:
                self.console.PRINT(f"当前音乐: {self.console.current_music_name}")
            elif self.console.music_box.url:
                music_name = os.path.basename(self.console.music_box.url)
                self.console.PRINT(f"当前音乐: {music_name}")
            else:
                self.console.PRINT("当前音乐: 无")
            
            self.console.PRINT(f"音量: {current_volume:.2f}")
            if self.console.music_box.is_playing and not self.console.music_box.is_paused:
                self.console.PRINT(f"播放位置: {current_pos:.1f}秒")
            
            self.console.PRINT("─" * 40)
            self.console.PRINT("[1] 播放音乐")
            self.console.PRINT("[2] 暂停音乐")
            self.console.PRINT("[3] 继续播放")
            self.console.PRINT("[4] 停止音乐")
            self.console.PRINT("[5] 选择音乐")
            self.console.PRINT("[6] 增大音量")
            self.console.PRINT("[7] 减小音量")
            self.console.PRINT("[8] 设置音量")
            self.console.PRINT("[9] 显示音乐列表")
            self.console.PRINT("[0] 返回")
            self.console.PRINT("请输入选择:")
            
            choice = self.console.INPUT()
            
            if choice == '0':
                running = False
            elif choice == '1':
                if self.console.music_box.url:
                    self.console.music_box.play(loops=-1, fade_in=1000)
                    self.console.PRINT("音乐开始播放")
                else:
                    self.console.PRINT("请先选择音乐文件", colors=(255, 200, 200))
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '2':
                self.console.music_box.pause()
                self.console.PRINT("音乐已暂停")
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '3':
                self.console.music_box.countion()
                self.console.PRINT("音乐继续播放")
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '4':
                self.console.music_box.stop()
                self.console.PRINT("音乐已停止")
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '5':
                # 显示音乐列表供选择
                if not self.console.music_list:
                    self.console.PRINT("音乐列表为空", colors=(255, 200, 200))
                    self.console.PRINT("按任意键继续...")
                    self.console.INPUT()
                    continue
                
                self.console.output_lines = []
                self.console.PRINT("════════════ 音乐列表 ════════════")
                
                music_names = list(self.console.music_list.keys())
                for i, music_name in enumerate(music_names, 1):
                    self.console.PRINT(f"[{i}] {music_name}")
                
                self.console.PRINT("─" * 40)
                self.console.PRINT("请输入要播放的音乐编号（0返回）:")
                
                music_choice = self.console.INPUT()
                if music_choice and music_choice.isdigit():
                    choice_num = int(music_choice)
                    if 1 <= choice_num <= len(music_names):
                        selected_music_name = music_names[choice_num - 1]
                        selected_music_path = self.console.music_list[selected_music_name]
                        
                        if os.path.exists(selected_music_path):
                            success = self.console.music_box.newurl(selected_music_path)
                            if success:
                                self.console.current_music_name = selected_music_name
                                self.console.music_box.play(loops=-1)
                                self.console.PRINT(f"已切换到: {selected_music_name}")
                            else:
                                self.console.PRINT("切换音乐失败", colors=(255, 200, 200))
                        else:
                            self.console.PRINT(f"音乐文件不存在: {selected_music_path}", colors=(255, 200, 200))
                    elif choice_num == 0:
                        pass  # 返回
                    else:
                        self.console.PRINT("无效的选择", colors=(255, 200, 200))
                else:
                    self.console.PRINT("无效的输入", colors=(255, 200, 200))
                
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '6':
                new_volume = min(1.0, current_volume + 0.1)
                self.console.music_box.set_volume(new_volume)
                self.console.PRINT(f"音量增大到 {new_volume:.2f}")
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '7':
                new_volume = max(0.0, current_volume - 0.1)
                self.console.music_box.set_volume(new_volume)
                self.console.PRINT(f"音量减小到 {new_volume:.2f}")
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '8':
                self.console.PRINT("请输入音量 (0.0-1.0):")
                vol_input = self.console.INPUT()
                try:
                    vol_value = float(vol_input)
                    if 0.0 <= vol_value <= 1.0:
                        self.console.music_box.set_volume(vol_value)
                        self.console.PRINT(f"音量已设置为 {vol_value:.2f}")
                    else:
                        self.console.PRINT("音量值必须在0.0到1.0之间", colors=(255, 200, 200))
                except ValueError:
                    self.console.PRINT("请输入有效的数字", colors=(255, 200, 200))
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            elif choice == '9':
                # 显示音乐列表
                self.console.output_lines = []
                self.console.PRINT("════════════ 全部音乐 ════════════")
                
                if not self.console.music_list:
                    self.console.PRINT("音乐列表为空", colors=(255, 200, 200))
                else:
                    music_names = list(self.console.music_list.keys())
                    for i, music_name in enumerate(music_names, 1):
                        path = self.console.music_list[music_name]
                        exists = "✓" if os.path.exists(path) else "✗"
                        self.console.PRINT(f"{i:2d}. {music_name} [{exists}]")
                        self.console.PRINT(f"    路径: {path}", colors=(180, 180, 180))
                
                self.console.PRINT("─" * 40)
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
            else:
                self.console.PRINT("无效的选择", colors=(255, 200, 200))
                self.console.PRINT("按任意键继续...")
                self.console.INPUT()
    
    def start(self):
        self.console.PRINT("[0]start")
        if self.input == '0':
            running = True
            while running:
                self.input = self.console.INPUT()
                if self.input == '99':
                    running = False
                elif self.input:
                    self.console.PRINT("[99]退出")
                    self.console.PRINT("[1]测试文本")
                    self.console.PRINT("[2]查询位置")
                    self.console.PRINT("[3]商店")
                    self.console.PRINT("[4]音乐控制")
                    self.console.PRINT("[5]显示当前音乐")
                    
                    if self.input == '1':
                        self.text()
                    elif self.input == '2':
                        self.getpwd()
                    elif self.input == '3':
                        self.shop()
                    elif self.input == '4':
                        self.music_control()
                    elif self.input == '5':
                        if self.console.music_box:
                            status = self.console.music_box.get_status()
                            current_volume = self.console.music_box.get_volume()
                            self.console.PRINT(f"音乐状态: {status}")
                            self.console.PRINT(f"当前音量: {current_volume:.2f}")
                            if self.console.current_music_name:
                                self.console.PRINT(f"当前音乐: {self.console.current_music_name}")
                            elif self.console.music_box.url:
                                music_name = os.path.basename(self.console.music_box.url)
                                self.console.PRINT(f"当前音乐: {music_name}")
                        else:
                            self.console.PRINT("音乐系统未初始化", colors=(255, 200, 200))
                        self.console.PRINT("按任意键继续...")
                        self.console.INPUT()
                    
                    self.console.PRINT("")
    
    def main(self):
        # 首先初始化地图数据
        self.map()
        
        running = True
        while running:
            self.input = self.console.INPUT()
            
            if self.input and self.input.lower() == "quit":
                running = False
            elif self.input:
                self.start()
                self.console.PRINT("")
            
            # 处理退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    start = thethings()
    """     console = SimpleERAConsole()
    
    # 测试PRINT功能
    console.PRINT("\t\t\t\t\t\t\t\t欢迎来到Pera!")
    console.PRINT("\t\t\t\t\t\t\t\tpower by PYgame")
    console.PRINT("请输入您的命令:")
    
    # 主循环
    running = True
    while running:
        # 获取用户输入
        user_input = console.INPUT()
        if user_input =='350234':
            console.PRINT("真是一对苦命鸳鸯啊")
        # 处理用户输入
        if user_input.lower() == "quit":
            running = False
        elif user_input:
            console.PRINT(f"您输入了: {user_input}")
        
        # 处理退出事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()
    sys.exit() """