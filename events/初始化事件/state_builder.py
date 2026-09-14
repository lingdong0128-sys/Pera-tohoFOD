import datetime

def event_build_allstate(this):
    """
    初始化构建所有角色的状态字典 (allstate) - 全量同步版 (含 Base, Abl, Talent, Exp, Mark, Cflag, Ex)
    """
    init = this.console.init
    allstate = {}

    # --- 0. 辅助函数：创建默认模板 ---
    def create_template(csv_name):
        template = {}
        # 尝试获取全局定义 (兼容大小写及首字母大写)
        def_dict = init.global_key.get(csv_name, {}) or \
                   init.global_key.get(csv_name.upper(), {}) or \
                   init.global_key.get(csv_name.capitalize(), {})

        for key, val in def_dict.items():
            # 获取属性名
            prop_name = str(val)
            if isinstance(val, dict):
                prop_name = val.get('name') or val.get('全名') or str(key)
            
            if prop_name:
                template[str(prop_name)] = 0 # 默认值 0
        return template

    # [预生成所有模板]
    base_template = create_template('Base')
    abl_template = create_template('Abl')
    talent_template = create_template('Talent')
    exp_template = create_template('exp')
    mark_template = create_template('Mark')
    cflag_template = create_template('Cflag') 
    ex_template = create_template('ex') # [新增] 对应 ex.csv
    # 获取装备定义
    equip_slots_def = init.global_key.get('Equip', {})
    clothing_db = init.global_key.get('Tequip', {})
    # 获取地牢属性定义
    dungeon_stat_template = create_template('角色地牢属性')

    # --- 遍历所有已注册的角色 ---
    for chara_id in init.chara_ids:
        raw_data = init.charaters_key.get(chara_id, {})
        print(raw_data)
        # 1. 基础信息
        char_state = {
            'id': chara_id,
            'name': raw_data.get('全名', '未命名'),
            'callname': raw_data.get('称呼', raw_data.get('全名', '未命名')),
            'fullname': raw_data.get('全名', ''), 
            'data': raw_data, 
        }

        # 2. 才能 (Talent)
        talents = talent_template.copy()
        if '素质' in raw_data:
            for k, v in raw_data['素质'].items():
                try: talents[k] = int(v)
                except: talents[k] = v 
        char_state['talents'] = talents

        # 3. [核心修改] 属性值校准 (Base + Abl -> attributes)
        # 逻辑：遍历所有可能的属性，如果角色CSV里有定义，就设为CSV里的值(最大值)；否则设为0
        attributes = {}
        
        # --- 处理 Base (基础数值：体力、气力等) ---
        # 1. 获取源数据 (兼容多种写法：基础/基础/BASE)
        # 这一步非常关键，解决了"体力为0"的 Bug
        source_base = raw_data.get('基础') or raw_data.get('基础') or raw_data.get('BASE') or {}
        
        # 2. 遍历全局定义的模板 (base_template 包含所有可能的属性名)
        for key in base_template.keys():
            # 检查角色是否有这个属性
            if key in source_base:
                try:
                    # [校准] 将当前值(attributes) 初始化为 CSV中的设定值(最大值)
                    attributes[key] = int(source_base[key])
                except ValueError:
                    attributes[key] = 0
            else:
                # 没定义则默认为 0
                attributes[key] = 0

        # --- 处理 Abl (能力等级：技巧、顺从等) ---
        # 1. 获取源数据 (兼容多种写法：能力/ABL)
        source_abl = raw_data.get('能力') or raw_data.get('ABL') or {}
        
        # 2. 遍历全局定义
        for key in abl_template.keys():
            if key in source_abl:
                try:
                    # [校准] 等级初始化为 CSV 中的设定值
                    attributes[key] = int(source_abl[key])
                except ValueError:
                    attributes[key] = 0
            else:
                attributes[key] = 0
        
        char_state['attributes'] = attributes

        # 4. [核心修改] 经验 (Exp)
        # 使用模板补全，防止 KeyError
        exps = exp_template.copy()
        source_exp = raw_data.get('经验') or raw_data.get('EXP') or {}
        for k, v in source_exp.items():
            try: exps[k] = int(v)
            except: pass
        char_state['exp'] = exps

        # 5. [核心修改] 绝顶/EX (Ex)
        # 通常用于记录当前的绝顶次数或积累值
        exs = ex_template.copy()
        source_ex = raw_data.get('EX') or raw_data.get('绝顶') or {}
        for k, v in source_ex.items():
            try: exs[k] = int(v)
            except: pass
        char_state['ex'] = exs

        # 6. 刻印 (Mark)
        marks = mark_template.copy()
        source_mark = raw_data.get('刻印') or raw_data.get('MARK') or {}
        for k, v in source_mark.items():
            try: marks[k] = int(v)
            except: pass
        char_state['mark'] = marks

        # 7. CFLAG 系统同步
        cflags = cflag_template.copy()
        if 'CFLAG' in raw_data:
            for k, v in raw_data['CFLAG'].items():
                key = int(k) if k.isdigit() else k
                try:
                    cflags[key] = int(v)
                except ValueError:
                    cflags[key] = v
        char_state['cflags'] = cflags

        # 8. 装备状态
        equip_state = {}
        chara_init_equip = raw_data.get('装备') or raw_data.get('EQUIP') or {}
        
        for slot_id, slot_val in equip_slots_def.items():
            slot_name = str(slot_val)
            if isinstance(slot_val, dict):
                slot_name = slot_val.get('name', str(slot_id))
            
            item_id = str(chara_init_equip.get(str(slot_id), '0'))
            item_name = "无"
            if item_id != '0' and item_id in clothing_db:
                item_data = clothing_db[item_id]
                if isinstance(item_data, dict):
                    item_name = item_data.get('name', '未知服装')
                else:
                    item_name = str(item_data)
            
            equip_state[str(slot_id)] = {
                'slot_name': slot_name,
                'item_id': item_id,
                'item_name': item_name
            }
        char_state['equip'] = equip_state

        # 9. 特殊状态 (运行时)
        char_state['states'] = {'怀孕': 0, '妊娠': 0, '発情': 0, '绝顶': 0}

        # 10. 立绘信息
        loaded_images = this.console.chara_images.get(chara_id, {})
        available_types = list(loaded_images.keys())
        if not available_types: available_types = ['初始绘']

        draw_type = raw_data.get('draw_type')
        if draw_type not in available_types:
            draw_type = available_types[0]
            raw_data['draw_type'] = draw_type
            
        default_face = '顔絵_服_通常' if draw_type == '初始绘' else '别颜_服_通常'
        face_name = raw_data.get('DrawName', default_face)
        if not face_name: face_name = default_face

        full_img_key = f"{chara_id}_{draw_type}_{face_name}_{chara_id}"

        char_state['portrait'] = {
            'current_type': draw_type,
            'current_face': face_name,
            'full_key': full_img_key,
            'available': available_types, 
        }

        # 11. 物品栏
        inventory = {}
        raw_items = raw_data.get('物品栏')
        if raw_items:
            if isinstance(raw_items, list):
                item_str = "".join(str(x) for x in raw_items)
            else:
                item_str = str(raw_items)
            
            clean_str = item_str.replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip()
            if clean_str:
                if '|' not in clean_str and ',' in clean_str:
                    clean_str = clean_str.replace(',', '|')
                for group in clean_str.split('|'):
                    group = group.strip()
                    if not group: continue
                    if ':' in group:
                        parts = group.split(':')
                        item_id = parts[0].strip()
                        try: count = int(parts[1].strip())
                        except: count = 1
                    else:
                        item_id = group.strip()
                        count = 1
                    if item_id:
                        inventory[item_id] = inventory.get(item_id, 0) + count
        char_state['inventory'] = inventory

        # 12. 历史
        char_state['location_history'] = []
        # 13. 地牢角色属性
        # 使用模板初始化
        dungeon_stats = dungeon_stat_template.copy()
        
        # 尝试从 raw_data 中读取已有的地牢数据 (如果存档或初始化过)
        source_dungeon = raw_data.get('角色地牢属性') or raw_data.get('DUNGEON') or {}
        
        if source_dungeon:
            # 如果源数据有，直接加载
            for k, v in source_dungeon.items():
                if k in dungeon_stats:
                    try: dungeon_stats[k] = int(v)
                    except: dungeon_stats[k] = v
        else:
            # 如果源数据没有，执行初始化逻辑 (根据设计思路映射 Base)
            # 逻辑：根据角色base中的体力上限等比映射
            # 这里先做简单的初值填充，具体的等比逻辑建议在地牢初始化事件中动态计算
            if '体力' in dungeon_stats and '体力' in attributes:
                dungeon_stats['体力'] = attributes['体力'] # 初始同步
            
            # 设置默认行动力
            if '行动力' in dungeon_stats:
                dungeon_stats['行动力'] = 3

        # 将构建好的字典放入 char_state 供实时操作
        char_state['dungeon_stats'] = dungeon_stats
        
        # [需求实现] 确保数据结构在 data 键中有键值对存在
        # 这将初始化的数据回写到 init.charaters_key 中
        if '角色地牢属性' not in raw_data:
            raw_data['角色地牢属性'] = dungeon_stats
        # 14.异常状态
        abnormal_states = {}
        source_abnormal = raw_data.get('异常状态') or raw_data.get('ABNORMAL') or {}
        
        if source_abnormal:
             for k, v in source_abnormal.items():
                 abnormal_states[k] = v
        
        # 放入 char_state
        char_state['abnormal_states'] = abnormal_states
        
        # [需求实现] 确保数据结构在 data 键中存在
        if '异常状态' not in raw_data:
            raw_data['异常状态'] = abnormal_states
        allstate[chara_id]=char_state

    # --- [allstate加冕] 保留 map 事件先行构建的 positions ---
    # 启动顺序是 main.py 先触发 'map' 再触发 'build_allstate'，
    # 所以重建角色字典时必须把已有的位置数据带过来，否则会被整体替换抹掉
    old_allstate = getattr(this.console, 'allstate', None)
    if isinstance(old_allstate, dict) and 'positions' in old_allstate:
        allstate['positions'] = old_allstate['positions']

    # --- [allstate加冕] 全局运行时标量的家：allstate['System'] ---
    # 以 CSV 静态键做种子（SCENE/MASTER/MONTH/DAY/TIME 等），补运行时默认值；
    # 时间8键（YEAR/HOUR/...）由时间控制事件随后写入
    system_state = dict(init.global_key.get('System', {}) or {})
    system_state.setdefault('SCENE', '日常')
    system_state.setdefault('选择对象', '0')
    system_state.setdefault('WEATHER', '晴')
    allstate['System'] = system_state

    this.console.allstate = allstate

    # --- [allstate加冕] 兼容别名重绑：物理上只有一个 dict ---
    # 旧代码读写 init.global_key['System'] / this.charater_pwds 依然生效（同一对象，永不漂移）；
    # 新代码一律使用 allstate['System'] / allstate['positions']
    init.global_key['System'] = allstate['System']
    this.charater_pwds = allstate.setdefault('positions', {})
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
    # [allstate加冕] 运行时状态统一从 allstate 读（System 经别名与 global_key['System'] 同源）
    system_state = all_chars.get('System', {})
    positions = all_chars.get('positions', {})

    target_id = system_state.get('选择对象')
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
            # [allstate加冕] 位置从运行时权威家读取（旧实现读 charaters_key['0'] 的陈旧值）
            'location': positions.get('0', {}).get('小地图', '未知'),
            'scene_type': system_state.get('SCENE', '日常'),
            'time_of_day': system_state.get('TIME', '昼'),
            # 时间系统数据（System 由时间控制事件维护）
            'year': system_state.get('YEAR', 1),
            'month': system_state.get('MONTH', 1),
            'day': system_state.get('DAY', 1),
            'hour': system_state.get('HOUR', 0),
            'minute': system_state.get('MINUTE', 0),
            'weekday': system_state.get('WEEKDAY', 1),
            'total_minutes': system_state.get('TOTAL_MINUTES', 0),
            'current_festival': system_state.get('CURRENT_FESTIVAL', None),
            # [allstate加冕] 天气读真值（旧实现写死 '晴'）
            'weather': system_state.get('WEATHER', '晴'),
            'temp': '20.5℃',
        },

        # --- 角色数据 (引用) ---
        'master': all_chars.get(master_id, {}),
        'chara': all_chars.get(target_id, {}),

        # --- 全局数据 ---
        'globals': {
            'variables': init.global_key.get('Variable', {}),
            'flags': init.global_key.get('Flag', {}),
            'settings': system_state,
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
    [读档注入器 - allstate加冕版]
    流程：读取存档 -> 恢复地图并校准位置 -> 恢复全局变量 -> 恢复 allstate -> 重绑兼容别名 -> 恢复时间 -> 重建上下文
    trigger: apply_save
    """
    save_data = getattr(this, 'temp_save_data', None)
    if not save_data:
        return None

    # ---------------------------------------------------------
    # 步骤 A: 恢复地图 + 校准位置
    # map 事件会把 allstate['positions'] 重置为 map_state 的推导值；
    # 若存档里带有真实 positions（新档），步骤 C 会再用它覆盖回来
    # ---------------------------------------------------------
    if 'map_state' in save_data:
        # 1. 用存档里的地图（包含腐化状态）覆盖内存
        this.console.map_data = save_data['map_state']

        # 2. 重新触发 map 事件，让位置与载入的地图状态对齐（旧档的兜底推导）
        this.event_manager.trigger_event('map', this)

        this.console.PRINT(">>> 地图状态已校准。", colors=(100, 255, 100))

    # ---------------------------------------------------------
    # 步骤 B: 恢复全局变量 (Variable / Flag；System 的家已在 allstate)
    # ---------------------------------------------------------
    saved_globals = save_data.get('globals', {}) or {}
    if 'variables' in saved_globals:
        this.console.init.global_key['Variable'] = saved_globals['variables']
    if 'flags' in saved_globals:
        this.console.init.global_key['Flag'] = saved_globals['flags']

    # ---------------------------------------------------------
    # 步骤 C: 恢复世界状态 (allstate，运行时状态的唯一家)
    # ---------------------------------------------------------
    loaded_allstate = save_data.get('world_state') or {}

    # [连接逻辑] 存档里的角色 data 覆盖底层 init.charaters_key；缺 data 的补引用防 KeyError
    for chara_id, chara_state in loaded_allstate.items():
        if not isinstance(chara_state, dict):
            continue
        if 'data' in chara_state:
            this.console.init.charaters_key[chara_id] = chara_state['data']
        else:
            chara_state['data'] = this.console.init.charaters_key.get(chara_id, {})

    # [allstate加冕] 旧档特征检测（按结构判断，不用版本号）：
    # 旧档 world_state 没有 'System'/'positions'，运行时状态散在 globals.settings / session 里
    if isinstance(loaded_allstate, dict) and 'System' not in loaded_allstate:
        legacy_settings = dict(saved_globals.get('settings', {}) or {})
        legacy_settings.setdefault('SCENE', '日常')
        legacy_settings.setdefault('选择对象', '0')
        legacy_settings.setdefault('WEATHER', '晴')
        # 旧档的 data 字典里可能存有 选择对象（经 charaters_key 引用间接入档）
        legacy_data = loaded_allstate.get('0', {}).get('data', {})
        if isinstance(legacy_data, dict) and legacy_data.get('选择对象'):
            legacy_settings['选择对象'] = legacy_data['选择对象']
        # 旧档 session.chara_id 优先
        old_session = save_data.get('session', {}) or {}
        if old_session.get('chara_id'):
            legacy_settings['选择对象'] = old_session['chara_id']
        loaded_allstate['System'] = legacy_settings

    if isinstance(loaded_allstate, dict) and 'positions' not in loaded_allstate:
        # 旧档没有 positions → 继承步骤 A 中 map 事件刚校准的推导结果
        # （必须在整体替换 allstate 之前从旧对象里捞出来，否则会被孤儿化）
        derived_positions = (getattr(this.console, 'allstate', None) or {}).get('positions', {})
        loaded_allstate['positions'] = derived_positions

    this.console.allstate = loaded_allstate

    # ---------------------------------------------------------
    # 步骤 D: [allstate加冕] 重绑兼容别名（物理同一 dict，见 build_allstate 注释）
    # ---------------------------------------------------------
    if isinstance(loaded_allstate, dict):
        this.console.init.global_key['System'] = loaded_allstate.setdefault('System', {})
    this.charater_pwds = loaded_allstate.setdefault('positions', {})

    this.console.PRINT(">>> 数据流重定向完成 (Save -> Allstate -> Init)", colors=(100, 255, 100))

    # ---------------------------------------------------------
    # 步骤 E: 恢复时间系统（System -> TimeManager；必须在别名重绑之后）
    # ---------------------------------------------------------
    this.event_manager.trigger_event('time_control', this, 'load_from_global')

    # ---------------------------------------------------------
    # 步骤 F: 基于恢复后的状态重建上下文，再用存档里的其余顶层键覆盖
    # ---------------------------------------------------------
    new_ctx = event_get_context_state(this)
    if 'globals' in save_data:
        new_ctx['globals'] = dict(save_data['globals'])
        # settings 指向恢复后的 System（同一对象）
        new_ctx['globals']['settings'] = loaded_allstate.get('System', {})
    for key in save_data:
        # 排除掉我们已经手动处理过的 key，剩下的直接覆盖
        if key not in ['console', 'init', 'event_manager', 'loader', 'world_state', 'globals']:
            new_ctx[key] = save_data[key]

    return new_ctx

# 注册触发器
event_build_allstate.event_trigger = "build_allstate"
event_get_context_state.event_trigger = "get_context_state"
event_apply_save_data.event_trigger = "apply_save"
