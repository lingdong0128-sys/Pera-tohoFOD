def event_聊天(this):
    # 1. 获取目标 ID
    target_id = this.console.init.charaters_key['0'].get('选择对象')
    if not target_id:
        this.console.PRINT("你还没有选择对象哦！")
        return

    # 2. [核心] 获取游戏大字典 (State Dict)
    # 这会返回当前游戏的一个完整快照
    state = this.event_manager.trigger_event('get_context_state', this)
    

    # 3. 从大字典提取数据构建上下文
    # 这样我们就不用手动写死 '昼' 或者 '日常' 了
    kojo_context = {
        # --- 核心定位 ---
        'TARGET': target_id,
        'PLAYER': state['session'].get('master_id', '0'),
        'ASSI': state['session'].get('assi_id', []), # 从 session 获取助手
        
        # --- 指令信息 ---
        'SELECTCOM': '22',  # 本次指令是固定的
        'COM_NAME': '聊天',
        # 从全局变量获取上一次指令，实现连续对话逻辑
        'PREVCOM': str(state['globals']['variables'].get('PREVCOM', 0)),
        
        # --- 状态与环境 (直接从 state 读取) ---
        'MODE': state['session'].get('scene_type', '日常'), # 比如 '日常', 'H', '战斗'
        'TIME': state['session'].get('time_of_day', '昼'),  # 比如 '昼', '夜'
        'WEATHER': state['session'].get('weather', '晴'),   # 甚至可以传天气
        
        # --- 计算用字典 ---
        # 如果你的游戏有先经过“参数计算过程”，这些数据应该存储在 state['temp'] 或类似的地方
        # 如果没有，给空字典即可
        'PALAM': state.get('calc', {}).get('PALAM', {}),
        'UP': state.get('calc', {}).get('UP', {}),
        'DOWN': state.get('calc', {}).get('DOWN', {}),
        'LOSEBASE': state.get('calc', {}).get('LOSEBASE', {}),
        'TEQUIP': state['chara'].get('equip', {}), # 可以传入装备状态
        'EX': state.get('calc', {}).get('EX', {'C':0, 'V':0, 'A':0, 'B':0}),
        'STAIN': state['chara'].get('stain', {}),
        
        # [高级] 把整个大字典的引用传进去
        # 这样如果在口上里想查一些奇怪的数据（比如系统分辨率、存档位置），也能查到
        '_RAW_STATE': state
    }

    # 4. 获取口上类型 (保持不变)
    kojo_type = this.console.init.charaters_key[target_id].get('口上类型', '初期口上')

    # 5. 拼接事件名称 (保持不变)
    str_event = f"{target_id}_{kojo_type}_日常系"

    # 6. 触发事件
    try:
        this.current_kojo_context = kojo_context # 挂载数据
        this.event_manager.trigger_event(str_event, this)
        this.current_kojo_context = None # 清理
        
        # [可选] 聊天结束后，更新 PREVCOM
        this.console.init.global_key['System']['PREVCOM'] = '22'
        
    except Exception as e:
        this.console.PRINT(f"口上响应失败: {str_event}\n错误: {e}", colors=(255, 100, 100))