def event_初始之地(this):
    """
    地牢 ID: 0 - 初始之地
    功能：提供一个安全的休息点，或者搜刮一点初始物资
    """
    import time
    
    # 1. 检查是否是第一次进入 (可选，增加一点剧情感)
    # 使用地牢实例中的 memory 字典来存储房间状态
    dungeon = this.console.map_data.get('DungeonInstance', {})
    current_room_id = this.charater_pwds['0'].get('地牢位置')
    room_data = dungeon['rooms'].get(current_room_id, {})
    
    is_first_visit = not room_data.get('visited', False)
    context_state=this.event_manager.trigger_event('get_context_state', this)
    # 2. 设置界面氛围
    this.console.PRINT_DIVIDER("=")
    this.console.PRINT("【 异 变 的 起 点 】", colors=(255, 215, 0)) # 金色标题
    this.console.PRINT_DIVIDER("-")

    # 3. 场景描述
    if is_first_visit:
        this.console.PRINT("进入了地牢...", colors=(200, 200, 200))
        this.console.PRINT("四周的墙壁由不知名的灰色石块砌成，空气中弥漫着陈旧的尘土味。", colors=(200, 200, 200))
        this.console.PRINT("身后是唯一的退路，而前方则是深不见底的黑暗。", colors=(200, 100, 100))
        # 标记已访问
        room_data['visited'] = True
    else:
        this.console.PRINT("你回到了这个相对安全的入口区域。", colors=(150, 255, 150))
        this.console.PRINT("这里的光线比深处要明亮一些，让人稍感安心。", colors=(200, 200, 200))

    this.console.PRINT("") # 空行

    # 4. 房间内交互循环
    # 这是一个小循环，处理完房间内的动作后 break，返回主地牢循环以便移动
    in_room = True
    while in_room:
        this.console.PRINT_DIVIDER("-", colors=(100, 100, 100))
        this.console.PRINT("要做什么呢？")
        
        # --- 选项菜单 ---
        # 使用 cs (ClickableString)
        this.console.PRINT(
            this.cs("[0] 调查周围环境").click("0"), "    ",
            this.cs("[1] 稍微休息一下").click("1"), "    ",
            this.cs("[2] 整理物品").click("2")
        )
        this.console.PRINT(
            this.cs("[9] ➡ 准备出发 (移动)").click("9"), colors=(100, 255, 255)
        )

        # --- 输入处理 ---
        user_input = this.console.INPUT()

        if user_input == '0':
            this.console.PRINT("你仔细检查了房间的角落...")
            time.sleep(0.5)
            # 简单的随机掉落逻辑
            if not room_data.get('looted'):
                # 假设物品ID 1 是药水
                this.console.PRINT("在碎石堆里发现了一瓶【有些奇怪的精力剂】！", colors=(100, 255, 100))
                # 调用中间层添加物品 (假设你已经合并了 EraKojoHandler)
                from utils.era_handler import EraKojoHandler
                kojo = EraKojoHandler(this.console, {'TARGET': '0'})
                kojo.ITEM_ADD('1000', 1)
                
                room_data['looted'] = True
            else:
                this.console.PRINT("除了灰尘，什么也没有了。", colors=(150, 150, 150))
            
            this.console.PRINT("按任意键继续...")
            this.console.INPUT()

        elif user_input == '1':
            this.console.PRINT("你靠在墙边坐下，平复了一下呼吸...")
            # 简单的恢复逻辑
            # 获取主角属性引用
            master = context_state['master']
            current_hp = int(master['data']['基础'].get('体力', 0))
            max_hp = int(this.console.allstate['0']['data']['基础'].get('体力', 2000)) # 假设有最大值
            
            recover = 1000
            master['attributes']['体力'] = min(max_hp, current_hp + recover)
            
            time.sleep(0.5)
            this.console.PRINT(f"体力恢复了 {recover} 点。", colors=(100, 255, 100))
            this.console.INPUT()

        elif user_input == '2':
            # 调用物品栏事件
            this.event_manager.trigger_event('menu_inventory', this)

        elif user_input == '9':
            this.console.PRINT("你拍了拍身上的灰尘，准备继续探索。")
            in_room = False # 退出循环，交还控制权给 handle_dungeon_crawling

        else:
            # 默认返回，或者处理无效输入
            pass

    # 函数结束，返回 None，start.py 会继续执行显示移动箭头
    return

# 注册事件
event_初始之地.event_trigger = "初始之地"
event_初始之地.is_main_event = True