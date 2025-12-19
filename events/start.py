def event_start(this):
    print(this.console.init.global_key['DungeonRooms'])
    # 这是一个示例，如果你们也有这种需要进入的循环的话请把每一个循环中需要使用的事件id加入这种列表中并初始化
    loadidlist = ['1', '2', '3', '4', '5', '99', '10', '8']
    # 当然这是作为机械加载文本位置的预备功能，现在这个列表还没什么用
    start_eventid = {}
    for i in this.event_manager.eventid:
        if i in loadidlist:
            start_eventid[i] = this.event_manager.eventid[i]
    this.console.PRINT("是否要进行全角色立绘检查？")
    this.console.PRINT(this.cs("[1]是").click(
        "1"), "      ", this.cs("[2]否").click("2"))
    coice = this.console.INPUT()
    if coice == '1':
        this.event_manager.trigger_event('设置立绘类型选择', this)
    if coice == '2':
        this.console.PRINT("已跳过立绘检查,所有角色默认设置为初始绘")
    running = True
    while running:
        # 1. 获取当前上下文
        ctx = this.event_manager.trigger_event('get_context_state', this)
        current_scene = ctx['session']['scene_type']

        # =================================================
        #  逻辑分流中心
        # =================================================
        
        if current_scene == '日常':
            # 执行原本的地图移动、聊天、商店逻辑
            handle_daily_routine(this, ctx)
            running=False
        elif current_scene == '地牢':
            # 执行地图逻辑完全独立的地牢
            handle_dungeon_crawling(this)
        elif current_scene == '战斗':
             # 如果以后做回合制战斗，也可以分流到这里
             pass
def handle_daily_routine(this, ctx):
    """
    [日常模式主循环]
    包含：UI渲染、立绘显示、状态栏、地图移动检测
    """
    import os
    
    # 辅助函数：生成彩色进度条字符串
    def get_ui_bar(label, current, max_val, length=10):
        try:
            current = int(current)
            max_val = int(max_val)
        except:
            current, max_val = 0, 1
        
        if max_val <= 0: max_val = 1
        percent = min(1.0, current / max_val) if max_val > 0 else 0
        filled_len = int(length * percent)
        
        # 动态颜色 (绿 -> 黄 -> 红)
        if percent > 0.5: color = (50, 255, 50)
        elif percent > 0.2: color = (255, 255, 50)
        else: color = (255, 50, 50)
        
        bar_text = "▒" * filled_len
        empty_text = "░" * (length - filled_len)
        
        return this.cs(f"{label} ").set_color((200, 200, 200)) + \
               this.cs(bar_text).set_color(color) + \
               this.cs(empty_text).set_color((60, 60, 60)) + \
               this.cs(f" {current}/{max_val}").set_color((200, 200, 200))

    running = True
    while running:
        # =================================================
        # 0. [核心] 每一帧重新获取最新状态快照
        # =================================================
        # 这样确保了每次循环都能读到最新的好感度、位置、属性变化
        ctx = this.event_manager.trigger_event('get_context_state', this)
        
        # 安全检查：如果状态丢失，强制退出防止崩溃
        if not ctx: break

        # =================================================
        # 1. [场景切换] 自动检测腐化区域 -> 切换地牢
        # =================================================
        current_location = ctx['session']['location'] # 从 ctx 获取当前小地图
        
        # 大地图判定逻辑 (这里假设位置结构是 '大地图' 键，或者从 allstate 获取)
        # 为了兼容之前的逻辑，我们还是去 charater_pwds 拿大地图ID
        current_big_map_id = this.charater_pwds['0'].get('大地图')
        
        map_data = getattr(this.console, 'map_data', {})
        current_map_info = map_data.get(current_big_map_id, {})
        
        if current_map_info.get('状态') == '腐化':
            this.console.PRINT(f"\n警告：[{current_big_map_id}] 已被异变吞噬！", colors=(255, 50, 50))
            this.console.PRINT("正在切入异变空间...", colors=(255, 100, 100))
            
            # 修改底层状态
            this.console.init.global_key['System']['SCENE'] = '地牢'
            
            # 确保有地牢入口坐标
            if '地牢位置' not in this.charater_pwds['0']:
                this.charater_pwds['0']['地牢位置'] = 'room_0'
                
            running = False
            continue 

        # =================================================
        # 2. [数据准备] 从 ctx 提取主角和目标
        # =================================================
        master_state = ctx['master']
        target_state = ctx['chara'] # 如果没选人，这里可能是主角自己或者 None
        
        # 原始数据源 (用于读取上限 MaxBase)
        # 注意：这里我们通过 ctx['master']['data'] 也能拿到原始 CSV 引用
        master_raw = master_state.get('data', {})
        target_raw = target_state.get('data', {}) if target_state else {}

        # 获取同地图角色列表
        result = this.event_manager.trigger_event('对象选择', this)
        if result:
            InOneMapCharater, InOneMapCharaterImg, CharaList = result
        else:
            InOneMapCharater, InOneMapCharaterImg, CharaList = ("", [], [])

        # =================================================
        # 3. [UI渲染] 立绘与信息
        # =================================================
        CharaterImgList = []
        Tmp = 0
        for i in InOneMapCharaterImg:
            if not i: continue
            CharaterImgDict = {'img': i, 'offset': (Tmp * 180, 0)}
            CharaterImgList.append(CharaterImgDict)
            Tmp += 1
        
        this.event_manager.trigger_event('初会面检查', this)
        if CharaterImgList:
            this.console.PRINTIMG(None, img_list=CharaterImgList, size=(180, 180))
        
        this.console.PRINT(InOneMapCharater) 
        this.console.PRINT_DIVIDER("·", length=60)

        # [状态栏] 玩家信息 (从 ctx 读取)
        m_attr = master_state.get('attributes', {})
        m_base_raw = master_raw.get('基础', {})
        
        m_hp = m_attr.get('体力', 0)
        m_hp_max = int(m_base_raw.get('体力', 1500))
        m_mp = m_attr.get('气力', 0)
        m_mp_max = int(m_base_raw.get('气力', 1000))
        
        master_bars = get_ui_bar("【你】体力", m_hp, m_hp_max) + "    " + \
                      get_ui_bar("气力", m_mp, m_mp_max)
        this.console.PRINT(master_bars)

        # [状态栏] 目标信息 (排除自己)
        if target_state and target_state['id'] != '0':
            t_attr = target_state.get('attributes', {})
            t_base_raw = target_raw.get('基础', {})
            t_cflag = target_state.get('cflags', {})
            
            t_hp = t_attr.get('体力', 0)
            t_hp_max = int(t_base_raw.get('体力', 1500))
            t_favor = t_cflag.get('好感度', 0)
            
            target_info = this.cs(f"【{target_state.get('name')}】").set_color((255, 200, 100)) + "  " + \
                          get_ui_bar("体力", t_hp, t_hp_max, length=8) + "  " + \
                          this.cs(f"好感: {t_favor}").set_color((255, 100, 150))
            this.console.PRINT(target_info)
        else:
            this.console.PRINT(" (尚未选择交互对象) ", colors=(100, 100, 100))

        this.console.PRINT_DIVIDER("=", length=60)

        # =================================================
        # 4. [菜单选项]
        # =================================================
        this.console.PRINT(
            this.cs("[1] 💬 对话/聊天").click("22"), "      ", 
            this.cs("[2] 🔍 观察环境").click("100"), "      ",
            this.cs("[3] 🛒 商店").click("3"), "      ",
            this.cs("[4] 🎒 物品栏").click("11")
        )
        this.console.PRINT(
            this.cs("[5] 🗺️ 移动/传送").click("12"), "      ",
            this.cs("[6] 🎵 音乐控制").click("4"), "      ",
            this.cs("[7] 💾 系统菜单").click("sys_menu"),"      ",
            this.cs("[8] 🛠️ 伪3D测试").click("33")
        )
        this.console.PRINT(
            this.cs("[99] 🚪 退出游戏").click("99")
        )

        # =================================================
        # 5. [输入处理]
        # =================================================
        input_val = this.console.INPUT()

        if input_val == '99':
            running = False
            
        elif input_val:
            # --- 角色选择 ---
            if input_val.startswith("c_"):
                target_id = input_val.split('_')[1]
                # 修改底层，下次循环 get_context 会自动更新 target_state
                this.console.init.charaters_key['0']['选择对象'] = target_id
                
                # 获取新名字用于提示
                new_target = this.console.allstate.get(target_id)
                t_name = new_target.get('name') if new_target else "未知"
                this.console.PRINT(f"已将目光锁定在：{t_name}", colors=(200, 255, 200))
            
            # --- 常用菜单 ---
            elif input_val == '22': this.event_manager.trigger_event('聊天', this)
            elif input_val == '100':this.event_manager.trigger_event('findthem', this)
            elif input_val == '3':  this.event_manager.trigger_event('shop', this)
            elif input_val == '11': this.event_manager.trigger_event('menu_inventory', this)
            elif input_val == '4':  this.event_manager.trigger_event('music_control', this)
            elif input_val == '12': 
                this.event_manager.trigger_event('移动菜单', this)
                continue
            
            # --- 系统菜单 ---
            elif input_val == 'sys_menu':
                this.event_manager.trigger_event('系统菜单', this)
            
            elif input_val == '33': this.event_manager.trigger_event('water_demo', this)
            
            this.console.PRINT("")
def handle_dungeon_crawling(this):
    """地牢模式主循环 - 最终逻辑闭环版"""
    
    # 1. 检查/初始化地牢数据 (保持不变)
    map_data = getattr(this.console, 'map_data', {})
    if 'DungeonInstance' not in map_data:
        this.console.PRINT("正在生成异变空间结构...", colors=(100, 255, 100))
        new_dungeon = this.event_manager.trigger_event('generate_dungeon', this)
        if new_dungeon:
            this.console.map_data['DungeonInstance'] = new_dungeon
            this.charater_pwds['0']['地牢位置'] = new_dungeon['entry_point']
        else:
            this.console.PRINT("地牢生成失败，返回日常模式。", colors=(255, 0, 0))
            this.console.init.global_key['System']['SCENE'] = '日常'
            return

    # 获取引用
    dungeon = this.console.map_data['DungeonInstance']
    rooms = dungeon['rooms']
    
    crawling = True
    while crawling:
        # 获取位置
        current_room_id = this.charater_pwds['0'].get('地牢位置', 'room_0')
        room_data = rooms.get(current_room_id)
        
        # [检查1] 外部强制切换检测
        # 如果 ctx 或者底层数据变了，说明可能读档了，或者被某种机制踢出了
        ctx = this.event_manager.trigger_event('get_context_state', this)
        if ctx['session']['scene_type'] != '地牢':
            # 如果状态不是地牢，但人还在地牢循环里，说明需要执行撤离逻辑
            perform_dungeon_exit(this)
            crawling = False
            break

        if not room_data:
            this.console.PRINT(f"错误：位置 {current_room_id} 无效，紧急撤离。", colors=(255, 0, 0))
            perform_dungeon_exit(this)
            crawling = False
            break

        # 获取房间定义 (保持不变)
        type_id = room_data['type_id']
        room_def_list = this.console.init.global_key['DungeonRooms'].get(type_id)
        
        if not room_def_list:
            this.console.PRINT(f"错误：房间定义丢失 (ID: {type_id})")
            return

        room_name = room_def_list[0].strip()
        room_event = room_def_list[1].strip()
        room_desc = room_def_list[5].strip()

        # --- 触发房间事件 ---
        if room_event and room_event != 'None' and room_event != '':
            if not room_data.get('cleared'):
                this.console.PRINT_DIVIDER("!")
                
                # 触发事件 (比如战斗、陷阱)
                this.event_manager.trigger_event(room_event, this)
                
                # 标记清理
                room_data['cleared'] = True
                
                # [核心逻辑] 事件后检查：是否导致了场景切换？
                # 比如：战斗失败被送回家，或者使用了"逃脱绳"道具
                current_scene = this.console.init.global_key['System'].get('SCENE')
                if current_scene != '地牢':
                    # 事件已经修改了 SCENE，我们只需要确保坐标正确
                    perform_dungeon_exit(this) 
                    crawling = False
                    continue # 退出循环

        # --- 显示界面 (保持不变) ---
        this.console.PRINT_DIVIDER("-")
        this.console.PRINT(f"【{room_name}】 (区域: {current_room_id})", colors=(255, 200, 0))
        this.console.PRINT(room_desc)
        this.console.PRINT_DIVIDER("-")

        # 显示移动选项
        exits = room_data.get('exits', {})
        nav_text = ""
        valid_moves = {}
        
        if exits.get('前'):
            nav_text += this.cs(" [↑ 前进] ").click("move_前")
            valid_moves["move_前"] = exits['前']
            
        if exits.get('后'):
            nav_text += this.cs(" [↓ 后退] ").click("move_后")
            valid_moves["move_后"] = exits['后']
            
        nav_text += "    " + this.cs("[I] 物品栏").click("I")
        nav_text += "    " + this.cs("[Q] 撤退 (返回日常)").click("Q")

        this.console.PRINT(nav_text)
        
        # --- 输入处理 ---
        user_input = this.console.INPUT()
        
        if user_input in valid_moves:
            target_room = valid_moves[user_input]
            this.charater_pwds['0']['地牢位置'] = target_room
            this.console.PRINT("你移动到了下一个区域...")
            
        elif user_input == "Q":
            this.console.PRINT("确定要放弃探索吗？(y/n)", colors=(255, 0, 0))
            if this.console.INPUT().lower() == "y":
                 # [修改] 调用通用撤离函数
                 perform_dungeon_exit(this)
                 crawling = False
        
        elif user_input == "I":
            this.event_manager.trigger_event('menu_inventory', this)
# [新增] 辅助函数：安全撤离地牢
def perform_dungeon_exit(this):
    """
    执行从地牢返回日常的逻辑：
    1. 读取历史记录，找到最近的安全地点
    2. 移动角色
    3. 切换场景状态
    """
    master_state = this.console.allstate.get('0', {})
    history = master_state.get('location_history', [])
    
    # 默认保底位置 (防止没有历史记录)
    target_big = '博丽神社' 
    target_small = '大殿'
    
    # 倒序查找最近的一个"日常"位置
    for entry in reversed(history):
        if entry.get('scene') == '日常':
            target_big = entry.get('map')
            target_small = entry.get('submap')
            break
            
    # 执行移动 (修改坐标)
    this.charater_pwds['0'] = {
        '大地图': target_big,
        '小地图': target_small
    }
    
    # 确保状态切换为日常
    this.console.init.global_key['System']['SCENE'] = '日常'
    
    this.console.PRINT(f"脱离了异变区域，返回到了 {target_big}。", colors=(100, 255, 255))
    this.console.INPUT()
event_start.event_id = "start"
event_start.event_name = "开始"
event_start.event_trigger = "0"
event_start.is_main_event = True
