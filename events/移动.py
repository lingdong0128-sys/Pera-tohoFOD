def event_移动菜单(this):
    """
    [UI事件] 显示地图移动菜单
    trigger: system_move
    功能：列出大地图 -> 列出小地图 -> 确认移动
    """
    # 1. 获取地图数据
    map_data = getattr(this.console, 'map_data', {})
    if not map_data:
        this.console.PRINT("地图数据未加载！", colors=(255, 0, 0))
        return

    # 当前选择状态
    selected_big_map = None
    
    while True:
        this.console.clear_screen()
        this.console.PRINT_DIVIDER("=")
        
        # --- 阶段 1: 选择大区域 ---
        if not selected_big_map:
            this.console.PRINT("【 选 择 移 动 区 域 】", colors=(100, 255, 255))
            this.console.PRINT_DIVIDER("-")
            
            # 遍历显示所有大地图
            count = 0
            for big_map_name, content in map_data.items():
                # 跳过特殊区域（如地牢实例）
                if big_map_name == 'DungeonInstance': continue
                
                # 检查腐化/封锁状态 (可选)
                status = content.get('状态', '日常')
                status_text = "(异变)" if status == '腐化' else ""
                color = (255, 100, 100) if status == '腐化' else (255, 255, 255)
                
                # 点击返回 "area_区域名"
                btn = this.cs(f"[{big_map_name}] {status_text}").set_color(color).click(f"area_{big_map_name}")
                this.console.PRINT(btn,'    ')
                
                count += 1
                if count % 3 == 0: this.console.PRINT("") # 换行

            this.console.PRINT("")
            this.console.PRINT_DIVIDER("-")
            this.console.PRINT(this.cs("[99] 取消").click("99"))

        # --- 阶段 2: 选择房间 ---
        else:
            this.console.PRINT(f"【 {selected_big_map} - 选择地点 】", colors=(100, 255, 255))
            this.console.PRINT_DIVIDER("-")
            
            # 获取该区域下的房间
            area_content = map_data.get(selected_big_map, {})
            
            count = 0
            for key, value in area_content.items():
                # 过滤掉非房间的配置键
                if key in ['状态', 'dungeon_level', 'description']: continue
                
                room_name = key
                # 点击返回 "room_房间名"
                btn = this.cs(f"[{room_name}]").click(f"room_{room_name}")
                this.console.PRINT(btn,'    ')
                
                count += 1
                if count % 4 == 0: this.console.PRINT("")

            this.console.PRINT("")
            this.console.PRINT_DIVIDER("-")
            this.console.PRINT(this.cs("[0] 返回上一级").click("back"), "    ", this.cs("[99] 取消").click("99"))

        # --- 输入处理 ---
        user_input = this.console.INPUT()
        
        if user_input == '99':
            break # 退出菜单
            
        elif user_input == 'back':
            selected_big_map = None # 返回区域选择
            
        elif user_input and user_input.startswith("area_"):
            # 选中了大地图
            selected_big_map = user_input.split("_", 1)[1]
            
        elif user_input and user_input.startswith("room_"):
            # 选中了房间 -> 执行移动
            target_room = user_input.split("_", 1)[1]
            
            # 调用移动逻辑
            event_强制移动(this, '0', selected_big_map, target_room)
            break

def event_强制移动(this, chara_id, big_map, small_map):
    """
    [工具函数] 执行强制移动
    可以在任何事件代码中直接调用此函数
    """
    # 1. 验证目标是否存在 (可选)
    # map_data = this.console.map_data
    # if big_map not in map_data or small_map not in map_data[big_map]: ...
    
    # 2. 更新位置
    this.charater_pwds[chara_id] = {
        '大地图': big_map,
        '小地图': small_map
    }
    
    # 3. 如果是主角，打印提示
    if chara_id == '0':
        this.console.PRINT(f"你移动到了 {big_map} - {small_map}。", colors=(100, 255, 100))
        
        # 4. (可选) 这里可以处理场景切换逻辑
        # 比如如果移动到了 '被腐化' 的区域，自动切入地牢模式
        map_info = this.console.map_data.get(big_map, {})
        if map_info.get('状态') == '腐化':
            # 触发进入地牢事件
            this.event_manager.trigger_event('handle_dungeon_crawling',this)
            pass

# 注册事件
event_移动菜单.event_trigger = "system_move"
event_移动菜单.is_main_event = True # 这是一个主要菜单，适合存档