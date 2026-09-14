def event_bad_apple(this):
    """播放Bad Apple ASCII动画 - 优化版，无闪屏"""
    import time
    import sys
    import os
    import pygame
    # ==== 1. 初始化所有变量 ====
    start_time = None
    frame_interval = 1.0 / 30.0  # 默认30fps
    total_frames = 0
    is_playing = True
    
    # 添加events目录到模块搜索路径
    current_event_dir = os.path.dirname(os.path.abspath(__file__))
    if current_event_dir not in sys.path:
        sys.path.insert(0, current_event_dir)
    
    # ==== 2. 加载帧数据 ====
    this.console.clear_screen()
    this.console.PRINT("=== Bad Apple ASCII 演出 ===", colors=(200, 255, 200))
    this.console.PRINT("加载中...", colors=(200, 200, 200))
    
    try:
        from bad_apple_frames import FRAMES
        total_frames = len(FRAMES)
        
        # 检查帧数据
        if not FRAMES:
            this.console.PRINT("错误：帧数据为空", colors=(255, 100, 100))
            this.console.INPUT()
            return
        
        # 显示信息
        first_frame = FRAMES[0]
        lines = first_frame.split('\n')
        this.console.PRINT(f"总帧数: {total_frames}", colors=(200,200,255))
        this.console.PRINT(f"每帧尺寸: {len(lines[0]) if lines else 0}列 × {len(lines)}行", colors=(200,200,200))
        
        # 如果数据文件中有定义帧率，就使用它
        try:
            from bad_apple_frames import FRAME_RATE
            frame_interval = 1.0 / FRAME_RATE
            this.console.PRINT(f"帧率: {FRAME_RATE} FPS", colors=(200,200,255))
        except ImportError:
            this.console.PRINT("帧率: 30 FPS (默认)", colors=(200,200,200))
        
        this.console.PRINT("按回车开始播放...", colors=(255, 255, 200))
        this.console.INPUT()
        
    except ImportError as e:
        this.console.PRINT(f"错误：未找到动画数据文件: {e}", colors=(255, 100, 100))
        this.console.INPUT()
        return
    
    # ==== 3. 音频初始化 ====
    audio_started = False
    if this.console.music_box:
        this.console.music_box.stop()
        # 音频文件路径
        audio_paths = [
            "./Musicbox/bad-apple-audio.mp3",
            "./Musicbox/bad_apple.mp3",
            "./Musicbox/badapple.mp3",
            "./bad-apple-audio.mp3",
            "./bad_apple.mp3",
            "./badapple.mp3"
        ]
        
        for audio_path in audio_paths:
            if os.path.exists(audio_path):
                if this.console.music_box.newurl(audio_path):
                    this.console.music_box.play(loops=0)
                    start_time = time.time()
                    audio_started = True
                    this.console.PRINT(f"已加载音频: {os.path.basename(audio_path)}", colors=(200, 255, 200))
                    break
        
        if not audio_started:
            this.console.PRINT("音频文件未找到，将无声播放。", colors=(255, 200, 100))
    else:
        this.console.PRINT("音乐盒未初始化，将无声播放。", colors=(255, 200, 100))
    
    # 如果没有音频，使用当前时间作为开始时间
    if not audio_started:
        start_time = time.time()
    
    # ==== 4. 播放循环 - 优化版，避免闪屏 ====
    this.console.clear_screen()
    this.console.set_font('./font/consola.ttf', 20)  # 使用等宽字体，字体稍小
    
    # 创建时钟对象，用于控制帧率
    clock = pygame.time.Clock()
    
    try:
        # 准备第一个帧
        this.console.clear_screen()
        ascii_lines = FRAMES[0].split('\n')
        for line in ascii_lines:
            this.console.loader.add_text(line, (220, 220, 220))
        
        # 显示初始帧
        this.console._draw_display()
        pygame.display.flip()
        
        frame_index = 0
        last_frame_index = 0
        
        while frame_index < total_frames and is_playing:
            # 计算目标时间
            target_time = start_time + (frame_index * frame_interval)
            current_time = time.time()
            
            # 如果当前帧已过时，跳过
            if current_time > target_time + frame_interval:
                # 跳过滞后的帧，但不要跳太多
                while frame_index < total_frames and current_time > start_time + (frame_index * frame_interval) + frame_interval:
                    frame_index += 1
                if frame_index >= total_frames:
                    break
            
            # 等待到正确的帧时间
            if current_time < target_time:
                sleep_time = target_time - current_time
                if sleep_time > 0:
                    time.sleep(min(sleep_time, 0.05))  # 最多等待50ms
            
            # 获取当前帧
            ascii_frame = FRAMES[frame_index]
            
            # ==== 优化：使用增量更新，避免完全清屏 ====
            # 如果当前帧和上一帧相同，跳过重绘
            if frame_index != last_frame_index:
                # 获取上一帧内容，计算差异
                if frame_index > 0:
                    prev_frame = FRAMES[frame_index - 1]
                    prev_lines = prev_frame.split('\n')
                else:
                    prev_lines = []
                
                curr_lines = ascii_frame.split('\n')
                
                # 检查是否有必要更新
                need_update = True
                if prev_lines and len(prev_lines) == len(curr_lines):
                    # 逐行比较，只有不同时才更新
                    all_same = True
                    for i in range(len(curr_lines)):
                        if i < len(prev_lines) and prev_lines[i] != curr_lines[i]:
                            all_same = False
                            break
                    need_update = not all_same
                
                if need_update:
                    # 使用动态加载器的内部方法直接更新显示，而不是清屏
                    this.console.loader.clear_history()  # 只清除历史，不清除缓存

                    # 添加当前帧的每一行
                    for line in curr_lines:
                        this.console.loader.add_text(line, (220, 220, 220))

                    # 强制更新显示（[盒子模型] 置脏，下一 draw 重排）
                    this.console._draw_display()
                    pygame.display.flip()

                last_frame_index = frame_index

            # 显示进度信息（只在底部显示，不干扰动画）
            if frame_index % 10 == 0:  # 每10帧更新一次进度
                progress = f"帧: {frame_index+1}/{total_frames}"
                # 保存当前流（[盒子模型] 盒子由流重排得出，无需单独保存）
                temp_history = this.console.loader.history.copy()

                # 清除并显示进度
                this.console.loader.clear_history()
                ascii_lines = ascii_frame.split('\n')
                for line in ascii_lines:
                    this.console.loader.add_text(line, (220, 220, 220))
                this.console.loader.add_text(progress, (150, 150, 255))

                this.console._draw_display()
                pygame.display.flip()

                # 恢复显示状态：把流放回去并置脏重排
                this.console.loader.history = temp_history
                this.console.loader.box_dirty = True
            
            # 检查退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_playing = False
                    raise KeyboardInterrupt
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                        is_playing = False
                        raise KeyboardInterrupt
            
            # 控制帧率，避免CPU占用过高
            clock.tick(60)
            
            # 下一帧
            frame_index += 1
    
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
    this.console.set_font('./font/luoli.ttf', 24)
    this.console.clear_screen()
    this.console.PRINT("\n=== Bad Apple 演出结束 ===", colors=(100, 255, 100))
    this.console.PRINT("按任意键返回主菜单...", colors=(255, 255, 200))
    this.console.INPUT()

# 事件元数据
event_bad_apple.event_id = "bad_apple"
event_bad_apple.event_name = "Bad Apple演出"
event_bad_apple.event_trigger = "apple"