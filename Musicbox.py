import pygame
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