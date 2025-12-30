def event_移动菜单(this):
    """
    [UI事件] 显示地图移动菜单 - 使用纯数字ID
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
            
            # 遍历显示所有大地图，使用纯数字编号
            count = 1
            big_map_map = {} # 数字ID -> 地图名的映射
            
            for big_map_name, content in map_data.items():
                # 跳过特殊区域（如地牢实例）
                if big_map_name == 'DungeonInstance': continue
                
                # 检查腐化/封锁状态 (可选)
                status = content.get('状态', '日常')
                status_text = "(异变)" if status == '腐化' else ""
                color = (255, 100, 100) if status == '腐化' else (255, 255, 255)
                
                # 使用纯数字ID
                btn = this.cs(f"[{count}] {big_map_name} {status_text}").set_color(color).click(str(count))
                this.console.PRINT(btn,'    ')
                
                # 建立映射
                big_map_map[str(count)] = big_map_name
                count += 1
                
                if (count - 1) % 3 == 0: this.console.PRINT("") # 换行

            this.console.PRINT("")
            this.console.PRINT_DIVIDER("-")
            this.console.PRINT(this.cs("[0] 取消").click("0"))

        # --- 阶段 2: 选择房间 ---
        else:
            this.console.PRINT(f"【 {selected_big_map} - 选择地点 】", colors=(100, 255, 255))
            this.console.PRINT_DIVIDER("-")
            
            # 获取该区域下的房间
            area_content = map_data.get(selected_big_map, {})
            
            count = 1
            room_map = {} # 数字ID -> 房间名的映射
            
            for key, value in area_content.items():
                # 过滤掉非房间的配置键
                if key in ['状态', 'dungeon_level', 'description']: continue
                
                room_name = key
                # 使用纯数字ID
                btn = this.cs(f"[{count}] {room_name}").click(str(count))
                this.console.PRINT(btn,'    ')
                
                # 建立映射
                room_map[str(count)] = room_name
                count += 1
                
                if (count - 1) % 4 == 0: this.console.PRINT("")

            this.console.PRINT("")
            this.console.PRINT_DIVIDER("-")
            this.console.PRINT(this.cs("[0] 返回上一级").click("0"), "    ", this.cs("[99] 取消").click("99"))

        # --- 输入处理 ---
        user_input = this.console.INPUT()
        
        if user_input == '99' or user_input == '0':
            if selected_big_map:
                selected_big_map = None # 返回区域选择
            else:
                break # 退出菜单
            
        elif not selected_big_map and user_input in big_map_map:
            # 选中了大地图
            selected_big_map = big_map_map[user_input]
            
        elif selected_big_map and user_input in room_map:
            # 选中了房间 -> 执行移动
            target_room = room_map[user_input]
            
            # 调用移动逻辑
            event_强制移动(this, '0', selected_big_map, target_room)
            break

def event_强制移动(this, chara_id, big_map, small_map):
    """
    [工具函数] 执行强制移动 (带历史记录和时间消耗)
    
    Args:
        chara_id: 角色ID
        big_map: 目标大地图ID
        small_map: 目标小地图ID (如果为None，会自动选择该大地图下编号第一的小地图)
    """
    # 0. 获取角色状态引用
    chara_state = this.console.allstate.get(chara_id)
    if not chara_state: return

    # 1. 记录历史 (Record History)
    # 获取移动前的位置 (Current/Old Position)
    old_big = this.charater_pwds.get(chara_id, {}).get('大地图')
    old_small = this.charater_pwds.get(chara_id, {}).get('小地图')

    # 只有当位置真的发生变化，且当前位置有效时才记录
    if old_big and old_small and (old_big != big_map or old_small != small_map):
        # 确保 location_history 列表存在
        if 'location_history' not in chara_state:
            chara_state['location_history'] = []
            
        history = chara_state['location_history']
        
        # 记录条目
        entry = {
            'map': old_big,
            'submap': old_small,
            'scene': this.console.init.global_key['System'].get('SCENE', '日常')
        }
        
        # 追加并限制长度 (只记最近50步)
        history.append(entry)
        if len(history) > 50:
            history.pop(0)

    # 2. 获取地图数据
    map_data = getattr(this.console, 'map_data', {})
    target_area = map_data.get(big_map, {})
    
    # 3. 处理小地图自动选择逻辑
    # 如果目标小地图为None，自动选择该大地图下编号顺位第一的小地图
    if small_map is None:
        # 获取该大地图下所有的房间键，过滤掉非房间配置键
        room_keys = [key for key in target_area.keys() 
                     if key not in ['状态', 'dungeon_level', 'description']]
        
        # 按编号排序，选择第一个
        if room_keys:
            # 尝试按数字排序
            try:
                room_keys.sort(key=lambda x: int(x))
            except ValueError:
                # 如果无法转为数字，按字符串排序
                room_keys.sort()
            
            small_map = room_keys[0]
        else:
            # 如果没有房间，使用默认值
            small_map = '0'

    # 4. 计算并扣除时间消耗
    time_cost_minutes = 0
    move_type = ""
    
    # 判断移动类型并计算时间
    if old_big == big_map and old_small != small_map:
        # 同一大地图下的不同小地图间移动
        time_cost_minutes = 2  # 小地图间移动消耗2分钟
        move_type = "小地图间移动"
    elif old_big != big_map:
        # 不同大地图间移动
        # 可以根据不同大地图设置不同的时间消耗，这里暂时统一为10分钟
        time_cost_minutes = 10
        move_type = "大地图间移动"
    
    # 执行时间扣除
    if time_cost_minutes > 0:
        # 调用时间控制事件增加时间
        this.trigger_event('time_control', operation='add', minutes=time_cost_minutes)
        
        # 获取当前时间信息用于显示
        time_info = this.trigger_event('time_control', operation='get', format_type='string')

    # 5. 更新位置 (Update Position)
    this.charater_pwds[chara_id] = {
        '大地图': big_map,
        '小地图': small_map
    }
    
    # 6. 提示与后续处理
    if chara_id == '0':
        if move_type:
            # 显示移动信息和时间消耗
            this.console.PRINT(f"{move_type}：{old_big}({old_small}) -> {big_map}({small_map})", colors=(150, 200, 255))
            this.console.PRINT(f"时间消耗：{time_cost_minutes}分钟", colors=(255, 255, 100))
            this.console.PRINT(f"{time_info}", colors=(200, 200, 200))
        else:
            this.console.PRINT(f"你移动到了 {big_map} - {small_map}。", colors=(100, 255, 100))
        # 场景切换检测会在 start.py 的主循环开头自动触发

# 注册事件
event_移动菜单.event_trigger = "system_move"
event_移动菜单.is_main_event = True # 这是一个主要菜单，适合存档
