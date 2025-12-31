import random

def event_generate_dungeon(this):
    """
    生成地牢实例
    返回地牢字典结构，包含房间信息和怪物数据
    """
    init = this.console.init
    all_rooms = init.global_key.get('DungeonRooms', {})
    all_monsters = init.global_key.get('怪物', {})
    
    if not all_rooms:
        this.console.PRINT("警告：未找到地牢房间定义数据！", colors=(255, 0, 0))
        return None
    
    if not all_monsters:
        this.console.PRINT("警告：未找到怪物定义数据！", colors=(255, 0, 0))
        return None

    # 1. 确定腐化区域
    corrupted_regions = ['通用'] 
    map_data = getattr(this.console, 'map_data', {})
    for map_name, content in map_data.items():
        if content.get('状态') == '腐化':
            corrupted_regions.append(map_name)

    # 2. 筛选有效房间 ID 并计算权重
    valid_ids = []
    weights = []
    
    for r_id, r_data_list in all_rooms.items():
        # 索引 2: 所属区域 (去除可能存在的空格)
        region = r_data_list[2].strip()
        
        # 索引 3: 权重
        try:
            weight = int(r_data_list[3].strip())
        except ValueError:
            weight = 10
        
        if region in corrupted_regions:
            valid_ids.append(r_id)
            weights.append(weight)

    if not valid_ids:
        this.console.PRINT(f"警告：区域 {corrupted_regions} 无法生成房间！", colors=(255, 0, 0))
        return None

    # 3. 筛选有效怪物 ID 并计算权重
    monster_ids = []
    monster_weights = []
    
    for m_id, m_data_list in all_monsters.items():
        # 索引 2: 怪物类型 (0=普通, 1=精英, 2=Boss)
        monster_type = int(m_data_list[2].strip())
        
        # 索引 3: 怪物特点 (0=伪装, 1=善良, 2=邪恶)
        # 筛选特点为邪恶的怪物作为默认怪物
        monster_trait = int(m_data_list[3].strip())
        
        if monster_trait == 2:  # 只选择邪恶的怪物
            # Boss只在最后一层出现，精英在后半层出现
            if monster_type == 2:  # Boss
                continue  # 暂时不生成Boss，在专门事件中处理
            elif monster_type == 1:  # 精英
                weight = 5  # 精英怪物权重较低
            else:  # 普通
                weight = 20  # 普通怪物权重较高
            
            monster_ids.append(m_id)
            monster_weights.append(weight)

    if not monster_ids:
        this.console.PRINT("警告：没有可用的怪物！", colors=(255, 0, 0))
        return None

    # 4. 生成房间
    dungeon_size = 10
    rooms = {}
    
    # 第一个房间为安全区
    rooms['room_0'] = {
        'type_id': '0',
        'exits': {'前': 'room_1'},
        'monster': None,  # 安全区无怪物
        'cleared': False
    }
    
    for i in range(1, dungeon_size):
        type_id = random.choices(valid_ids, weights=weights, k=1)[0]
        current_id = f"room_{i}"
        next_id = f"room_{i+1}" if i < dungeon_size - 1 else None
        prev_id = f"room_{i-1}"
        
        # 随机生成怪物（60%概率有怪物）
        has_monster = random.random() < 0.6
        monster_data = None
        
        if has_monster:
            monster_id = random.choices(monster_ids, weights=monster_weights, k=1)[0]
            monster_info = all_monsters[monster_id]
            monster_data = {
                'id': monster_id,
                'name': monster_info[1].strip(),
                'type': int(monster_info[2].strip()),
                'trait': int(monster_info[3].strip()),
                'attack_power': int(monster_info[4].strip()),
                'defense': int(monster_info[5].strip()),
                'stamina': int(monster_info[6].strip()),
                'current_stamina': int(monster_info[6].strip()),  # 当前体力
                'skills': monster_info[7].strip().split('|') if len(monster_info) > 7 else [],
                'drops': monster_info[8].strip().split('|') if len(monster_info) > 8 else [],
                'abnormal_states': []  # 当前异常状态列表
            }
        
        rooms[current_id] = {
            'type_id': type_id,
            'exits': {
                '后': prev_id,
                '前': next_id
            },
            'monster': monster_data,
            'cleared': False,
            'visited': False
        }

    dungeon_instance = {
        'layer': 1,
        'rooms': rooms,
        'entry_point': 'room_0',
        'created_at': 'now',
        'current_room': 'room_0'
    }
    
    return dungeon_instance

event_generate_dungeon.event_trigger = "generate_dungeon"
