import random

def event_generate_dungeon(this):
    init = this.console.init
    all_rooms = init.global_key.get('DungeonRooms', {})
    
    if not all_rooms:
        this.console.PRINT("警告：未找到地牢房间定义数据！", colors=(255, 0, 0))
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
        # [核心修改] 根据新的索引读取
        
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

    dungeon_size = 10
    rooms = {}
    
    rooms['room_0'] = {
        'type_id': '0',
        'exits': {'前': 'room_1'}
    }
    
    for i in range(1, dungeon_size):
        type_id = random.choices(valid_ids, weights=weights, k=1)[0]
        current_id = f"room_{i}"
        next_id = f"room_{i+1}" if i < dungeon_size - 1 else None
        prev_id = f"room_{i-1}"
        
        rooms[current_id] = {
            'type_id': type_id,
            'exits': {
                '后': prev_id,
                '前': next_id
            },
            'cleared': False 
        }

    dungeon_instance = {
        'layer': 1,
        'rooms': rooms,
        'entry_point': 'room_0',
        'created_at': 'now'
    }
    
    return dungeon_instance

event_generate_dungeon.event_trigger = "generate_dungeon"