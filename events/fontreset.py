def event_fontreset(this):
    """字体重置事件"""
    import os
    
    # 获取所有字体文件

    this.console.PRINT("fontreset",click="fontreset")
    if this.input=="fontreset":
        fontlist = []
        for root, dirs, files in os.walk("./font/"):
            for file in files:
                if file.lower().endswith(".ttf"):
                    fontlist.append(file)
                    this.console.PRINT(f"已加载字体: {file}")
        
        if not fontlist:
            this.console.PRINT("未找到任何.ttf字体文件", colors=(255, 200, 200))
            return
        running = True
        while running:
            # 显示字体列表
            this.console.PRINT_DIVIDER("=", 40)
            this.console.PRINT("请选择字体:", colors=(200, 200, 255))
            
            for i, font_name in enumerate(fontlist, 1):
                this.console.PRINT(f"[{i}] {font_name}", click=str(i))
            
            this.console.PRINT("输入字体编号或字体名称，输入 exit 退出:")
            this.console.PRINT_DIVIDER("-", 40)
            
            thisinput = this.console.INPUT()
            if not thisinput:
                continue
                
            thisinput = thisinput.lower()
            
            if thisinput == "exit":
                running = False
                this.console.PRINT("已退出字体设置", colors=(200, 255, 200))
                continue
            
            # 处理数字选择
            try:
                index = int(thisinput) - 1
                if 0 <= index < len(fontlist):
                    selected_font = fontlist[index]
                else:
                    this.console.PRINT(f"编号 {thisinput} 无效", colors=(255, 200, 200))
                    continue
            except ValueError:
                # 按名称选择
                if thisinput in fontlist:
                    selected_font = thisinput
                else:
                    # 尝试模糊匹配
                    matching_fonts = [f for f in fontlist if thisinput in f.lower()]
                    if len(matching_fonts) == 1:
                        selected_font = matching_fonts[0]
                    elif len(matching_fonts) > 1:
                        this.console.PRINT(f"找到多个匹配的字体:", colors=(255, 255, 200))
                        for font in matching_fonts:
                            this.console.PRINT(f"  {font}")
                        continue
                    else:
                        this.console.PRINT(f"未找到字体: {thisinput}", colors=(255, 200, 200))
                        continue
            
            # 尝试设置字体
            font_path = f"./font/{selected_font}"
            try:
                # 尝试加载字体测试
                import pygame
                test_font = pygame.font.Font(font_path, 24)
                
                # 更新控制台字体
                this.console.set_font(font_path)
                
                this.console.PRINT(f"字体已更改为: {selected_font}", colors=(100, 255, 100))
                this.console.PRINT("这是一段测试文字，用于展示新字体效果。")
                this.console.PRINT_DIVIDER("~", 40, (150, 200, 255))
                
            except Exception as e:
                this.console.PRINT(f"加载字体失败: {e}", colors=(255, 200, 200))
                this.console.PRINT(f"请检查字体文件: {font_path}", colors=(255, 200, 200))

# 设置事件元数据
event_fontreset.event_id = "fontreset"
event_fontreset.event_name = "更改字体"
event_fontreset.event_trigger = "fontreset"