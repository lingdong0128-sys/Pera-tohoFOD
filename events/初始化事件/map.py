import json
import os

def event_map(this):
    """
    地图系统核心
    功能：
    1. 如果内存里没有地图数据，从 map.json 加载初始化。
    2. 根据当前的地图数据，刷新所有角色的位置信息(charater_pwds)。
    """
    
    # [步骤 1] 确保内存中有 map_data
    # 如果 console 里没有 map_data，说明是游戏刚启动，或者需要重置
    if not getattr(this.console, 'map_data', None):
        try:
            with open('./json/map/map.json', 'r', encoding='utf-8') as f:
                # 加载初始数据到内存
                this.console.map_data = json.load(f)
                # print("DEBUG: 已从 map.json 加载初始地图")
        except Exception as e:
            this.console.PRINT(f"加载地图文件失败: {e}", colors=(255, 200, 200))
            return

    # 获取内存中的地图数据（可能是刚读的，也可能是存档覆盖过的）
    map_data = this.console.map_data

    # [步骤 2] 刷新角色位置 (charater_pwds)
    
    # 先重置所有角色位置到默认点（防止有人在地图里消失）
    # 假设 '10000'/'10001' 是虚空或者默认房间
    for i in this.console.init.chara_ids:
        this.charater_pwds[i] = {
            '大地图': '10000',
            '小地图': '10001'
        }

    # 遍历地图数据，把角色放到正确的位置
    for big_map, content in map_data.items():
        # --- 检查腐化状态 ---
        # 如果这个大地图被标记为腐化，可能需要特殊处理
        # 比如跳过更新，或者将里面的角色全部移动到地牢入口
        if content.get('状态') == 'corrupted':
            # print(f"DEBUG: {big_map} 已腐化，跳过常规位置更新")
            continue 
        # --- 遍历房间 ---
        for key, value in content.items():
            # 过滤掉非房间的属性键 (status, dungeon_level 等)
            if key in ['状态', '腐化等级']:
                continue
                
            small_map = key
            charater_list = value # list: ['0', '1']
            
            for charater_id in charater_list:
                # 只有当角色ID有效时才更新
                if charater_id in this.charater_pwds:
                    this.charater_pwds[charater_id] = {
                        '大地图': big_map,
                        '小地图': small_map
                    }

event_map.event_trigger = "map"