def event_init_data_adapters(this):
    """
    [数据二次加工事件]
    用于将 init.py 读取的原始数据（String/List）转换为游戏系统所需的复杂结构（Dict）。
    这样 shop.py 等系统就可以直接使用标准化的数据，而不用关心 CSV 原始格式。
    trigger: init_data
    """
    init = this.console.init
    
    # ========================================================
    # 1. Item (物品) 数据适配
    # 原始数据可能是 List: ['苹果', '100', '好吃']
    # 目标格式: {'name': '苹果', 'price': 100, 'idn': '好吃', 'ex': ''}
    # ========================================================
    if 'Item' in init.global_key:
        raw_items = init.global_key['Item']
        formatted_items = {}
        
        # 遍历原始数据
        for key, val in raw_items.items():
            # A. 初始化全字段默认值 (保底策略)
            item_data = {
                'name': '未知物品',
                'price': 0,
                'idn': '暂无简介',
                'ex': ''
            }
            
            # B. 根据原始数据的类型进行填充
            if isinstance(val, list):
                # 列表结构: [Name, Price, Desc, Ex]
                # 使用 len 判断防止索引越界
                if len(val) > 0: item_data['name'] = str(val[0])
                if len(val) > 1: item_data['price'] = val[1]
                if len(val) > 2: item_data['idn'] = str(val[2])
                if len(val) > 3: item_data['ex'] = str(val[3])
                
            elif isinstance(val, str):
                # 只有一列字符串的情况: "物品名"
                if val.strip():
                    item_data['name'] = val.strip()
            
            # C. 类型转换 (确保价格是 Int)
            try:
                # 转为字符串并去空格，防止 " 100 " 报错
                p_str = str(item_data['price']).strip()
                # 简单的数字检查
                if p_str.lstrip('-').isdigit(): 
                    item_data['price'] = int(p_str)
                else:
                    item_data['price'] = 0
            except:
                item_data['price'] = 0

            # D. 存入结果
            formatted_items[key] = item_data
            
        # E. 将加工后的数据写回 global_key，替换原始数据
        init.global_key['Item'] = formatted_items
        this.console.PRINT(f">>> [System] Item 数据适配完成，加载了 {len(formatted_items)} 个物品。")

    # ==========================
    # 这里以后可以添加 Monster, Skill 等其他数据的适配逻辑
    # ==========================
# ============================
# 种族初始化
# ============================
def event_init_race_data(this):
    """
    [种族判定系统]
    遍历所有角色，根据素质(TALENT)解析出具体的种族和追加身份。
    执行后，会在 chara_state 中生成 'race' 字典。
    trigger: init_race
    """
    
    # 1. 确保状态已构建
    if not getattr(this.console, 'allstate', None):
        this.event_manager.trigger_event('build_state', this)
    
    all_states = this.console.allstate

    # ==========================================
    # 种族定义表 (Key: TALENT名, Value: {数值: 种族名})
    # ==========================================
    # 主种族定义 (互斥，通常一个人只有一个主种族)
    MAIN_RACE_MAP = {
        '人类': {1: '人类', 2: '仙人', 3: '天人', 4: '月人', 5: '魔界人', 6: '外界人'},
        '妖怪': {1: '妖怪', 2: '鬼', 3: '吸血鬼', 4: '河童', 5: '天狗', 6: '妖獣', 7: '妖鳥', 8: '妖蟲', 9: '悪魔', 10: '小人', 11: '座敷童子', 12: '山童'},
        '妖精': {1: '妖精'},
        '神灵': {1: '神灵', 2: '死神', 3: '閻魔'}, # 注意：CSV里可能是繁体'神霊'，这里做容错
        '神霊': {1: '神灵', 2: '死神', 3: '閻魔'},
        '幽灵': {1: '幽灵', 2: '騒霊', 3: '亡霊', 4: '悪霊'},
        '幽霊': {1: '幽灵', 2: '騒霊', 3: '亡霊', 4: '悪霊'},
        '付丧神': {1: '付丧神'},
        '付喪神': {1: '付丧神'},
        '人形': {1: '人形', 2: '机械', 3: '魔像', 4: '埴輪', 5: '僵尸', 99: '人形の乙女'},
    }

    # 追加种族 (可以叠加)
    EXTRA_RACE_MAP = {
        '追加种族': {1: '巫女', 2: '魔法使', 3: '女僕', 4: '蓬莱人'}
    }

    # ==========================================
    # 解析逻辑
    # ==========================================
    for chara_id, state in all_states.items():
        talents = state.get('talents', {})
        
        # 初始化种族信息字典
        race_info = {
            'main': '未知',       # 主种族 (大类，如 '妖怪')
            'species': '未知',    # 具体物种 (如 '吸血鬼')
            'extra': [],          # 追加种族列表 (如 ['魔法使', '蓬莱人'])
            'is_humanoid': False, # 是否人型 (人类/仙人/月人等)
            'is_immortal': False  # 是否不死
        }

        # 1. 判定主种族
        # 遍历所有可能的种族 Talent
        for talent_name, value_map in MAIN_RACE_MAP.items():
            # 获取该 Talent 的值 (默认为 0)
            # 注意兼容字符串和数字类型的键
            val = talents.get(talent_name, 0)
            if val > 0:
                race_info['main'] = talent_name
                race_info['species'] = value_map.get(val, f"未知{talent_name}({val})")
                
                # 特殊判定：人类大类
                if talent_name == '人类':
                    race_info['is_humanoid'] = True
                break # 找到主种族后停止 (假设主种族互斥)
        
        # 2. 判定追加种族
        for talent_name, value_map in EXTRA_RACE_MAP.items():
            val = talents.get(talent_name, 0)
            if val > 0:
                # 这种写法支持掩码或者单值，这里假设是单值对应
                # 如果追加种族是位运算 (Bitmask)，需要改写逻辑
                job = value_map.get(val)
                if job:
                    race_info['extra'].append(job)
                    
                    # 特殊属性判定
                    if job == '蓬莱人':
                        race_info['is_immortal'] = True

        # 3. 将解析结果存入角色状态
        state['race'] = race_info
        
        # [调试] 打印结果
        # print(f"角色 {state['name']}: {race_info['species']} / {race_info['extra']}")

    this.console.PRINT(f"已更新全员种族/职业信息。", colors=(100, 255, 200))

# 注册事件
event_init_race_data.event_trigger = "init_race"
event_init_data_adapters.event_trigger = "init_data"