def event_bad_apple(this):
    """播放Bad Apple ASCII动画 (场景事件)"""
    import time
    import sys
    import os
    
    # ==== 1. 初始化所有变量（关键修复）====
    start_time = None
    frame_interval = 1.0 / 30.0  # 默认帧率
    total_frames = 0
    
    # 添加events目录到模块搜索路径
    current_event_dir = os.path.dirname(os.path.abspath(__file__))
    if current_event_dir not in sys.path:
        sys.path.insert(0, current_event_dir)
    
    # ==== 2. 加载帧数据 ====
    this.console.clear_screen()
    this.console.PRINT("=== Bad Apple 演出 ===")
    this.console.PRINT("加载中...", colors=(200, 200, 200))
    
    try:
        from bad_apple_frames import FRAMES
        total_frames = len(FRAMES)
        
        # 调试：显示第一帧信息
        if FRAMES:
            first_frame = FRAMES[0]
            lines = first_frame.split('\n')
            this.console.PRINT(f"第一帧行数: {len(lines)}", colors=(200,200,255))
            this.console.PRINT(f"示例行: {lines[0][:50]}...", colors=(200,200,200))
            this.console.PRINT("按回车开始播放...")
            this.console.INPUT()
        
        # 如果数据文件中有定义帧率，就使用它
        try:
            from bad_apple_frames import FRAME_RATE
            frame_interval = 1.0 / FRAME_RATE
        except ImportError:
            pass  # 使用默认的30fps
    except ImportError as e:
        this.console.PRINT(f"错误：未找到动画数据文件: {e}", colors=(255, 100, 100))
        this.console.INPUT()
        return
    
    # ==== 3. 音频初始化（确保start_time被赋值）====
    audio_started = False
    if this.console.music_box:
        this.console.music_box.stop()
        # 假设音频文件路径，请根据实际情况修改
        audio_path = "./Musicbox/bad-apple-audio.mp3"
        if os.path.exists(audio_path):
            if this.console.music_box.newurl(audio_path):
                this.console.music_box.play(loops=0)
                start_time = time.time()  # 记录音频开始时间
                audio_started = True
            else:
                this.console.PRINT("音频文件加载失败，将无声播放。", colors=(255, 200, 100))
        else:
            this.console.PRINT(f"音频文件不存在: {audio_path}", colors=(255, 200, 100))
    
    # 如果没有成功启动音频，使用当前时间作为开始时间
    if not audio_started:
        this.console.PRINT("警告：将无声播放，按回车开始...", colors=(255, 200, 100))
        this.console.INPUT()  # 等待用户确认
        start_time = time.time()  # 现在肯定被赋值了
    
    # ==== 4. 播放循环 ====
    this.console.clear_screen()
    
    try:
        import pygame
        this.console.set_font('./font/consola.ttf', 24)
        for frame_index, ascii_frame in enumerate(FRAMES):
            # 现在start_time肯定有值，可以安全使用
            target_time = start_time + (frame_index * frame_interval)
            current_time = time.time()
            
            # 帧同步逻辑
            if current_time < target_time:
                time.sleep(target_time - current_time)
            elif current_time > target_time + frame_interval:
                continue  # 跳过滞后的帧
            
            # ==== 关键修复：逐行渲染ASCII帧 ====
            this.console.clear_screen()
            
            # 将ASCII帧按换行符分割成多行
            ascii_lines = ascii_frame.split('\n')
            
            # 替代逐行PRINT的方法
            for line in ascii_lines:
                this.console.loader.add_text(line, (220, 220, 220))
            this.console._draw_display()  # 手动触发重绘
            pygame.display.flip()
            
            # 显示进度信息
            progress = f"帧: {frame_index+1}/{total_frames}"
            this.console.PRINT(progress, colors=(150, 150, 255))
            
            # 检查退出（非阻塞）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                        raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        this.console.PRINT("\n播放被用户中断。", colors=(255, 150, 100))
    except Exception as e:
        this.console.PRINT(f"\n播放出错: {e}", colors=(255, 100, 100))
        import traceback
        this.console.PRINT(traceback.format_exc(), colors=(255, 150, 150))
    finally:
        # 确保停止音频
        if this.console.music_box:
            this.console.music_box.stop()
    
    # ==== 5. 播放结束 ====
    this.console.set_font('./font/luoli.ttf', 12)
    this.console.PRINT("\n=== 演出结束 ===", colors=(100, 255, 100))
    this.console.PRINT("按任意键返回主菜单...")
    this.console.INPUT()

# 事件元数据
event_bad_apple.event_id = "bad_apple"
event_bad_apple.event_name = "Bad Apple演出"
event_bad_apple.event_trigger = "apple"