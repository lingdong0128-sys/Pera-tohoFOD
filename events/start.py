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
            event_handle_dungeon_crawling(this, ctx)
            running=False
        elif current_scene == '战斗':
             # 如果以后做回合制战斗，也可以分流到这里
             pass
def handle_daily_routine(this, ctx):
    """原本 start.py 里的逻辑封装到这里"""
    import os
    running = True
    while running:
        input = this.console.INPUT()
        # 1. 调用对象选择 (现在 EventManager 修复后，这里能收到数据了)
        result = this.event_manager.trigger_event('对象选择', this)

        # 安全检查：防止对象选择出错返回 None 导致崩溃
        if result:
            InOneMapCharater, InOneMapCharaterImg, CharaList = result
        else:
            InOneMapCharater, InOneMapCharaterImg, CharaList = ("", [], [])

        # 2. [修复] 图片列表构建逻辑
        CharaterImgList = []
        Tmp = 0  # [修复] 计数器要在循环外面初始化！
        for i in InOneMapCharaterImg:
            # [修复] 必须在循环内部创建新字典，否则所有图片都会变成最后一张
            CharaterImgDict = {}

            CharaterImgDict['img'] = i  # 注意：这里最好用 img 键名，对应 PRINTIMG 的参数
            CharaterImgDict['offset'] = (Tmp * 180, 0)

            # 如果需要指定类型和ID，最好也在对象选择里传出来，或者这里写死
            # CharaterImgDict['draw_type'] = '...'

            CharaterImgList.append(CharaterImgDict)
            Tmp += 1  # 计数器递增
        this.event_manager.trigger_event('初会面检查', this)
        this.console.PRINTIMG("", img_list=CharaterImgList, size=(180, 180))
        this.console.PRINT(InOneMapCharater)
        this.console.PRINT(this.cs("[1]测试文本").click("1"), "         ", this.cs("[2]查询位置").click(
            "2"), "         ", this.cs("[3]商店").click("3"), "         ", this.cs("[4]音乐控制").click("4"))
        this.console.PRINT(this.cs("[5]显示当前音乐").click("5"), "     ", this.cs("[99]退出").click(
            "99"), "            ", this.cs("[10]查看当前加载事件").click("10"), "           ", this.cs("[8]helloworld！").click("8"))
        this.console.PRINT(this.cs("[100]四处张望").click("100"), "         ", this.cs("[200]badapple？").click(
            "200"), "         ", this.cs("[22]聊天").click("22"), "          ", this.cs('[33]测试伪3D').click('33'),"       ",this.cs('[11]物品栏').click('11'))
        this.console.PRINT(this.cs("[44]重载事件").click("44"),'        ',this.cs('[20]保存世界').click('20'),'     ',this.cs('[12]移动').click('12'))

        if input == '99':
            running = False
        elif input:
            # [必须有这一段逻辑]
            # 只有当 start.py 识别到 c_ 开头的输入，才会执行赋值！
            if input.startswith("c_"):
                # 提取真实ID (去掉 c_)
                target_id = input.split('_')[1]

                # 存入字典！这一步做了，聊天.py 才能读到东西
                this.console.init.charaters_key['0']['选择对象'] = target_id

                # 获取名字用于提示
                t_name = this.console.init.charaters_key[target_id].get('名前')
                this.console.PRINT(f"已选择对象：{t_name}")
                this.console.PRINT(f"已选择对象：{input}")
            elif input=='20':
                this.event_manager.trigger_event('save_menu', this)
            elif input=='11':
                this.event_manager.trigger_event('menu_inventory',this)
            elif input=='12':
                this.event_manager.trigger_event('移动菜单',this)
            elif input == '44':
                this.event_manager.trigger_event('reload', this)
            elif input == '33':
                this.event_manager.trigger_event('water_demo', this)
            elif input == '1':
                this.event_manager.trigger_event('text', this)
            elif input == '22':
                this.event_manager.trigger_event('聊天', this)
            elif input == '2':
                this.event_manager.trigger_event('getpwd', this)
            elif input == '3':
                this.event_manager.trigger_event('shop', this)
            elif input == '4':
                this.event_manager.trigger_event('music_control', this)
            elif input == '5':
                if this.console.music_box:
                    status = this.console.music_box.get_status()
                    current_volume = this.console.music_box.get_volume()
                    this.console.PRINT(f"音乐状态: {status}")
                    this.console.PRINT(f"当前音量: {current_volume:.2f}")
                    if this.console.current_music_name:
                        this.console.PRINT(
                            f"当前音乐: {this.console.current_music_name}")
                    elif this.console.music_box.url:
                        music_name = os.path.basename(
                            this.console.music_box.url)
                        this.console.PRINT(f"当前音乐: {music_name}")
                else:
                    this.console.PRINT("音乐系统未初始化", colors=(255, 200, 200))
                this.console.PRINT("按任意键继续...")
                this.console.INPUT()
            elif input == '10':
                this.event_manager.trigger_event('logevent', this)
            elif input == '8':
                this.event_manager.trigger_event('helloworld', this)
            elif input == '100':
                this.event_manager.trigger_event('findthem', this)
            elif input == '200':
                this.event_manager.trigger_event('bad_apple', this)
            this.console.PRINT("")
def event_handle_dungeon_crawling(this, ctx=None):
    """地牢模式主循环 - 修复版"""
    
    # 1. 检查/初始化地牢数据
    map_data = getattr(this.console, 'map_data', {})
    
    if 'DungeonInstance' not in map_data:
        this.console.PRINT("正在生成异变空间结构...", colors=(100, 255, 100))
        new_dungeon = this.event_manager.trigger_event('generate_dungeon', this)
        if new_dungeon:
            this.console.map_data['DungeonInstance'] = new_dungeon
            # 初始化玩家位置
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
        
        if not room_data:
            this.console.PRINT(f"错误：位置 {current_room_id} 无效，重置回入口。", colors=(255, 0, 0))
            this.charater_pwds['0']['地牢位置'] = dungeon['entry_point']
            continue

        # 获取房间定义 (列表)
        type_id = room_data['type_id']
        room_def_list = this.console.init.global_key['DungeonRooms'].get(type_id)
        
        if not room_def_list:
            this.console.PRINT(f"错误：房间定义丢失 (ID: {type_id})")
            return

        # [核心修复] 使用索引读取 CSV 列表数据 (去除空格)
        room_name = room_def_list[0].strip()   # Name
        room_event = room_def_list[1].strip()  # Event
        # room_music = room_def_list[4].strip() # Music (如果有)
        room_desc = room_def_list[5].strip()   # Desc

        # --- 触发房间事件 ---
        # 逻辑：如果事件存在，且房间未清理，则触发
        if room_event and room_event != 'None' and room_event != '':
            if not room_data.get('cleared'):
                this.console.PRINT_DIVIDER("!")
                # 触发事件
                this.event_manager.trigger_event(room_event, this)
                
                # [关键] 标记为已清理，防止死循环触发
                # 注意：如果像"初始之地"这种需要反复进入的，
                # 事件内部应该处理好循环，或者这里的逻辑需要改为"每次都触发"
                # 对于大多数房间（战斗/宝箱），触发一次就够了
                room_data['cleared'] = True
                
                # 如果事件导致场景切换（比如战败回家），退出循环
                if this.console.init.global_key['System'].get('SCENE') != '地牢':
                    crawling = False
                    continue

        # --- 显示界面 (移动模式) ---
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
            if this.console.INPUT() == "y":
                 this.console.init.global_key['System']['SCENE'] = '日常'
                 crawling = False
        
        elif user_input == "I":
            this.event_manager.trigger_event('menu_item', this)
event_start.event_id = "start"
event_start.event_name = "开始"
event_start.event_trigger = "0"
event_start.is_main_event = True
