import datetime

def event_build_allstate(this):
    """
    初始化构建所有角色的状态字典 (allstate)
    通常在游戏启动(start.py)或读档后调用一次
    trigger: build_state
    """
    init = this.console.init
    allstate = {}

    # 遍历所有已注册的角色ID
    for chara_id in init.chara_ids:
        # 获取原始 CSV 数据引用
        raw_data = init.charaters_key.get(chara_id, {})
        
        # 1. 基础信息构建
        char_state = {
            'id': chara_id,
            'name': raw_data.get('名前', '未命名'),
            'callname': raw_data.get('呼び名', raw_data.get('名前', '未命名')),
            'fullname': raw_data.get('名前', ''), 
            'data': raw_data,  # 保留原始数据的引用 (这是联动的关键)
        }

        # 2. 才能系统 (素質 -> talents)
        talents = {}
        if '素質' in raw_data:
            for k, v in raw_data['素質'].items():
                try:
                    talents[k] = int(v)
                except ValueError:
                    talents[k] = v 
        char_state['talents'] = talents

        # 3. 属性值 (基础 + 能力 -> attributes)
        attributes = {}
        # 加载基础 (BASE)
        if '基础' in raw_data:
            for k, v in raw_data['基础'].items():
                try:
                    attributes[k] = int(v)
                except ValueError:
                    attributes[k] = 0
        # 加载能力 (ABL)
        if '能力' in raw_data:
            for k, v in raw_data['能力'].items():
                try:
                    attributes[k] = int(v)
                except ValueError:
                    attributes[k] = 0
        
        char_state['attributes'] = attributes

        # 4. CFLAG 系统
        cflags = {}
        if 'CFLAG' in raw_data:
            for k, v in raw_data['CFLAG'].items():
                key = int(k) if k.isdigit() else k
                try:
                    cflags[key] = int(v)
                except ValueError:
                    cflags[key] = v
        char_state['cflags'] = cflags

        # 5. 装备状态
        char_state['equip'] = {
            '上衣': raw_data.get('装备', {}).get('上衣', '无'),
            '下衣': raw_data.get('装备', {}).get('下衣', '无'),
            '内衣': raw_data.get('装备', {}).get('内衣', '无'),
            '装饰': raw_data.get('装备', {}).get('装饰', '无'),
        }

        # 6. 特殊状态 (运行时)
        char_state['states'] = {
            '怀孕': 0,
            '妊娠': 0,
            '発情': 0,
            '绝顶': 0,
        }

        loaded_images = this.console.chara_images.get(chara_id, {})
        
        # 将字典的键转换为列表 (例如 ['初始绘', '泳装绘'])
        available_types = list(loaded_images.keys())
        
        # 兜底：如果这人没图片，给个默认值
        if not available_types:
            available_types = ['初始绘']
            
        # ----------------------------------------

        draw_type = raw_data.get('draw_type')
        # 校验：如果当前设定的类型不在已加载的列表里，重置为第一个可用的
        # 这样能防止存档里记了"泳装"，但你删了图片包导致报错的情况
        if draw_type not in available_types:
            draw_type = available_types[0]
            raw_data['draw_type'] = draw_type
            
        default_face = '顔絵_服_通常' if draw_type == '初始绘' else '別顔_服_通常'
        face_name = raw_data.get('DrawName', default_face)
        if not face_name: face_name = default_face # 双重保险

        # 预先拼好图片 ID: 角色ID_类型_表情_角色ID
        full_img_key = f"{chara_id}_{draw_type}_{face_name}_{chara_id}"

        char_state['portrait'] = {
            'current_type': draw_type,
            'current_face': face_name,
            'full_key': full_img_key, # 前端直接读这个就行
            'available': available_types, 
        }
# 8. [新增] 物品栏 (Inventory) - 竖线分隔版
        # 支持格式: "1:5|2:1|3" (ID:数量 | ID:数量 | ID)
        inventory = {}
        raw_items = raw_data.get('物品栏')
        
        if raw_items:
            # 1. 统一转为字符串并清洗
            # 无论 init.py 读成什么样，先转成字符串
            if isinstance(raw_items, list):
                item_str = "".join(str(x) for x in raw_items)
            else:
                item_str = str(raw_items)
            
            # 去掉可能的方括号、引号和首尾空格
            clean_str = item_str.replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip()
            
            if clean_str:
                # 2. 按 '|' 分割不同物品
                # 如果用户还是用了逗号，这里做一个兼容替换
                if '|' not in clean_str and ',' in clean_str:
                    clean_str = clean_str.replace(',', '|')
                
                item_groups = clean_str.split('|')
                
                for group in item_groups:
                    group = group.strip()
                    if not group: continue
                    
                    # 3. 解析 "ID:数量"
                    if ':' in group:
                        # 格式: "2:5" -> ID=2, Count=5
                        parts = group.split(':')
                        item_id = parts[0].strip()
                        try:
                            count = int(parts[1].strip())
                        except ValueError:
                            count = 1
                    else:
                        # 格式: "3" -> ID=3, Count=1 (默认)
                        item_id = group.strip()
                        count = 1
                    
                    # 4. 存入字典
                    if item_id:
                        # 累加逻辑（防止写了两次 "1:1|1:2"）
                        inventory[item_id] = inventory.get(item_id, 0) + count
        
        # 存入角色状态
        char_state['inventory'] = inventory
        
        # 存入角色状态
        # 因为 allstate 会被存档，所以这里面的变动会自动保存
        char_state['inventory'] = inventory
        # 将构建好的单人状态存入总字典
        allstate[chara_id] = char_state

    # 将 allstate 挂载到 console 上
    this.console.allstate = allstate
    
    # this.console.PRINT(f"已构建 {len(allstate)} 名角色的状态字典。", colors=(100, 255, 100))
    return allstate

def event_get_context_state(this):
    """
    获取当前的完整上下文快照
    trigger: get_context
    """
    # 如果 console.allstate 是 None，说明还没构建过
    if not getattr(this.console, 'allstate', None):
        event_build_allstate(this)

    # 快捷引用
    init = this.console.init
    all_chars = this.console.allstate # 现在肯定有了
    
    target_id = init.charaters_key['0'].get('选择对象')
    if not target_id:
        target_id = '0'
    
    master_id = '0'
    now = datetime.datetime.now()
    # 构建大字典
    context = {
        # --- 核心引用 (不可存档) ---
        'console': this.console,
        'init': init,
        'event_manager': this.event_manager,
        'loader': this.console.loader,
        # =======================================================
        # [核心修改] 这里就是保存"所有角色数据"的关键！
        # 把整个 allstate 字典放进去，存档时 SaveSystem 会把它递归写入 JSON
        # =======================================================
        'world_state': this.console.allstate,
        # [新增] 存档时，把当前的地图状态存进去
        # 这包含了 'status': 'corrupted' 这种动态变化
        'map_state': getattr(this.console, 'map_data', {}), 
        # --- 会话状态 ---
        'session': {
            'chara_id': target_id,
            'master_id': master_id,
            'location': init.charaters_key['0'].get('小地图', '未知'),
            # 这里假设 global_key 里有这些变量，如果没有会返回默认值
            'scene_type': init.global_key.get('System', {}).get('SCENE', '日常'),
            'time_of_day': init.global_key.get('System', {}).get('TIME', '昼'),
        },

        # --- 角色数据 (引用) ---
        'master': all_chars.get(master_id, {}),
        'chara': all_chars.get(target_id, {}),

        # --- 全局数据 ---
        'globals': {
            'variables': init.global_key.get('Variable', {}), 
            'flags': init.global_key.get('Flag', {}),
            'settings': init.global_key.get('System', {}),
        },

        # --- 系统状态 ---
        'system': {
            'time': {'year': now.year, 'month': now.month, 'day': now.day},
            'ui': {'width': this.console.screen_width, 'height': this.console.screen_height},
            # 使用 list() 或 copy() 创建副本，防止后续变化影响快照
            'event_stack': list(this.event_manager.get_save_stack()),
        }
    }

    return context

def event_apply_save_data(this):
    """
    [读档注入器 - 最终一致性版]
    流程：读取存档 -> 覆盖全局变量 -> 恢复世界状态 -> 反向绑定 init -> 更新上下文
    trigger: apply_save
    """
    save_data = getattr(this, 'temp_save_data', None)
    # [核心校准逻辑]
    if 'map_state' in save_data:
        # 1. 用存档里的地图（包含腐化状态）覆盖内存
        this.console.map_data = save_data['map_state']
        
        # 2. 重新触发 map 事件
        # 因为 map_data 变了，我们需要重新计算 charater_pwds
        # 这一步就是"校准"：让角色位置与载入的地图状态对齐
        this.event_manager.trigger_event('map', this)
        
        this.console.PRINT(">>> 地图状态已校准。", colors=(100, 255, 100))
    if not save_data: return None

    # 1. 获取基础模板 (用于填充那些存档里没有的临时数据)
    new_ctx = event_get_context_state(this)

    # ---------------------------------------------------------
    # 核心步骤 A: 恢复全局变量 (Global Key)
    # ---------------------------------------------------------
    if 'globals' in save_data:
        # 1. 更新上下文引用
        new_ctx['globals'] = save_data['globals']
        
        # 2. [反向映射] 将读出的数据写回 init.global_key
        # 这样以后调用 init.global_key['Variable'] 拿到的就是存档里的数据
        if 'variables' in save_data['globals']:
            this.console.init.global_key['Variable'] = save_data['globals']['variables']
        if 'flags' in save_data['globals']:
            this.console.init.global_key['Flag'] = save_data['globals']['flags']
        if 'settings' in save_data['globals']:
            this.console.init.global_key['System'] = save_data['globals']['settings']

    # ---------------------------------------------------------
    # 核心步骤 B: 恢复世界状态 (AllState) & 重建引用连接
    # ---------------------------------------------------------
    if 'world_state' in save_data:
        loaded_allstate = save_data['world_state']
        
        # [核心修复] 增强的连接逻辑
        for chara_id, chara_state in loaded_allstate.items():
            
            # 情况 A: 存档里有 data (正常情况，修复 save_system 后)
            if 'data' in chara_state:
                # 将存档里的数据覆盖到底层 init
                this.console.init.charaters_key[chara_id] = chara_state['data']
            
            # 情况 B: 存档里没 data (旧存档/坏档)
            # 我们必须手动补上这个键，否则后续代码会 KeyError
            else:
                # 指回游戏的初始数据，防止崩溃
                # 虽然会丢失存档里的初会面记录，但至少游戏能跑了
                chara_state['data'] = this.console.init.charaters_key.get(chara_id, {})
                # print(f"警告: 修复了角色 {chara_id} 缺失的 data 引用")

        # 3. [赋值] 将 console.allstate 指向这个加载好的大字典
        this.console.allstate = loaded_allstate
        new_ctx['world_state'] = loaded_allstate

        # 4. 更新当前 Context 里的快捷引用
        # 确保 new_ctx['master'] 指向的是新加载的 loaded_allstate 里的对象
        master_id = str(new_ctx['session'].get('master_id', '0'))
        chara_id = str(new_ctx['session'].get('chara_id', '0'))
        
        new_ctx['master'] = loaded_allstate.get(master_id, {})
        new_ctx['chara'] = loaded_allstate.get(chara_id, {})

        this.console.PRINT(">>> 数据流重定向完成 (Save -> Allstate -> Init)", colors=(100, 255, 100))

    # ---------------------------------------------------------
    # 核心步骤 C: 恢复其他 Session 信息
    # ---------------------------------------------------------
    for key in save_data:
        # 排除掉我们已经手动处理过的 key，剩下的直接覆盖
        if key not in ['console', 'init', 'event_manager', 'loader', 'world_state', 'globals']:
            new_ctx[key] = save_data[key]
            
    return new_ctx

# 注册触发器
event_build_allstate.event_trigger = "build_allstate"
event_get_context_state.event_trigger = "get_context_state"
event_apply_save_data.event_trigger = "apply_save"