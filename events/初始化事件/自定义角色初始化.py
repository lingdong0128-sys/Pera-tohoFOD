from utils.era_handler import EraKojoHandler

# 辅助函数：获取地图显示名称（仅名称格式）
def get_map_display_name(this, map_id):
    """
    根据地图ID获取显示用的地图名称
    参数：
        map_id: 地图ID
    返回：
        地图名称字符串，如果找不到名称则返回原ID
    """
    # 从global_key中获取map数据（注意键名是小写'map'）
    map_data = this.console.init.global_key.get('map', {})
    # 确保map_id是字符串类型
    map_id_str = str(map_id)
    if map_id_str in map_data:
        map_name = map_data[map_id_str]
        # 兼容dict和str格式
        if isinstance(map_name, dict):
            map_name = map_name.get('name') or map_name.get('全名') or map_id_str
        return str(map_name)
    return map_id_str

def event_custom_chara_init(this):
    """
    [自定义角色创建 - 最终完整版]
    功能：
    1. 姓名/称呼设定
    2. 种族选择与基础属性加点
    3. 详细素质设定 (含性别互斥逻辑)
    4. 出生地选择
    trigger: custom_chara_init
    """
    # 0. 基础初始化：确保0号角色数据结构存在
    if '0' not in this.console.init.charaters_key:
        this.console.init.charaters_key['0'] = {}
        for k in ['基础', '素質', '能力', 'CFLAG', '装备', '物品栏']:
            this.console.init.charaters_key['0'][k] = {}

    # 1. 默认值预设
    raw_data = this.console.init.charaters_key['0']
    
    # 默认性别: 女 (TALENT:2 = 1)
    if '2' not in raw_data.get('素質', {}):
        if '素質' not in raw_data: raw_data['素質'] = {}
        raw_data['素質']['2'] = '1'
        
    # 默认处女 (TALENT:0 = 1)
    if '0' not in raw_data['素質']:
        raw_data['素質']['0'] = '1'

    # 初始化 Handler
    context = {'TARGET': '0'}
    kojo = EraKojoHandler(this.console, context)

    # ================= 配置区域 =================
    # 初始属性点
    bonus_points = 20
    
    # 基础属性ID: 体力, 气力, 精力, 理性
    BASE_IDS = ['0', '1', '6', '11'] 
    
    # 种族ID列表 (190-196)
    RACE_IDS = [str(i) for i in range(190, 197)]

    # 素质分类配置
    TALENT_CONFIG = {
        "身体特征": [
            {'id': '2', 'type': 'range', 'min': 1, 'max': 3, 'map': {'1':'女', '2':'男', '3':'扶他'}, 'name': '性别'},
            {'id': '100', 'type': 'range', 'min': -3, 'max': 3, 'map': {'-3':'小人','-2':'幼儿','-1':'矮小','0':'普通','1':'高挑','2':'巨大','3':'巨人'}, 'name': '体型'},
            {'id': '105', 'type': 'range', 'min': -2, 'max': 2, 'map': {'-2':'绝壁', '-1':'贫', '0':'普', '1':'巨', '2':'爆'}, 'name': '胸围'},
            {'id': '108', 'type': 'range', 'min': -2, 'max': 2, 'map': {'-2':'纤细', '-1':'小', '0':'普', '1':'丰满', '2':'安产'}, 'name': '臀围'},
            # 性别互斥项
            {'id': '0', 'type': 'bool', 'name': '处女'}, 
            {'id': '1', 'type': 'bool', 'name': '童贞'}, 
        ],
        "特殊素质": [
            {'id': '150', 'type': 'bool', 'name': '幼儿退行'},
            {'id': '151', 'type': 'bool', 'name': '幼稚'},
            {'id': '143', 'type': 'range', 'min': 0, 'max': 4, 'map': {'0':'无','1':'无','2':'兔耳','3':'犬耳','4':'猫耳'}, 'name': '动物耳'},
            {'id': '57', 'type': 'bool', 'name': '漏尿癖'},
            {'id': '60', 'type': 'bool', 'name': '自慰狂'},
        ],
        "性爱观念": [
            {'id': '81', 'type': 'range', 'min': -1, 'max': 3, 'map': {'-1':'双性恋','0':'普通','1':'恐男','2':'恐女','3':'恐人'}, 'name': '性取向'},
            {'id': '82', 'type': 'bool', 'name': '施虐狂'},
            {'id': '83', 'type': 'bool', 'name': '受虐狂'},
            {'id': '85', 'type': 'bool', 'name': '迷信'},
        ],
        "正直度": [
            {'id': '70', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'否定快感','0':'普通','1':'接受快感'}, 'name': '快感响应'},
            {'id': '71', 'type': 'bool', 'name': '容易中毒'},
            {'id': '72', 'type': 'bool', 'name': '容易高潮'},
        ],
        "技术": [
            {'id': '50', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'慢','0':'普','1':'快'}, 'name': '习得速度'},
            {'id': '51', 'type': 'bool', 'name': '手指灵活'},
            {'id': '52', 'type': 'bool', 'name': '舌头灵活'},
            {'id': '53', 'type': 'bool', 'name': '擅长用针'},
            {'id': '54', 'type': 'bool', 'name': '猫舌'},
            {'id': '55', 'type': 'bool', 'name': '调合知识'},
            {'id': '56', 'type': 'bool', 'name': '药毒耐性'},
        ],
        "洁癖度": [
            {'id': '61', 'type': 'range', 'min': -2, 'max': 2, 'map': {'-2':'洁癖','-1':'敏感','0':'普','1':'钝感','2':'无视'}, 'name': '污臭耐性'},
            {'id': '62', 'type': 'bool', 'name': '献身'},
        ],
        "乙女心": [
            {'id': '30', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'无所谓','0':'普通','1':'重视'}, 'name': '贞操观'},
            {'id': '33', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'不知耻','0':'普通','1':'害羞'}, 'name': '羞耻心'},
            {'id': '31', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'压抑','0':'普通','1':'解放'}, 'name': '自我爱'},
        ],
        "性兴趣": [
             {'id': '23', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'保守','0':'普通','1':'好奇'}, 'name': '性兴趣'},
             {'id': '24', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'阴郁','0':'普通','1':'开朗'}, 'name': '性格'},
             {'id': '26', 'type': 'bool', 'name': '引人注目'},
             {'id': '27', 'type': 'bool', 'name': '无知'},
        ],
        "性格基础": [
            {'id': '10', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'胆怯', '0':'普通', '1':'坚强'}, 'name': '胆量'},
            {'id': '11', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'坦率', '0':'普通', '1':'叛逆'}, 'name': '态度'},
            {'id': '12', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'老实', '0':'普通', '1':'傲慢'}, 'name': '应答'},
            {'id': '13', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'自卑', '0':'普通', '1':'自大'}, 'name': '自尊'},
            {'id': '14', 'type': 'bool', 'name': '傲娇'},
            {'id': '16', 'type': 'range', 'min': -1, 'max': 1, 'map': {'-1':'丑陋', '0':'普通', '1':'端丽'}, 'name': '容貌'},
        ]
    }

    # 流程控制
    STAGES = ["姓名", "种族与能力", "素质细节", "出生地"]
    current_stage_idx = 0
    selected_talent_category = None 

    # --- 辅助函数 ---
    def draw_toggle_btn(label, is_selected, cmd_key):
        color = (255, 215, 0) if is_selected else (150, 150, 150)
        prefix = "★" if is_selected else "☆"
        return this.cs(f"[{prefix} {label}]").click(cmd_key).set_color(color)

    # ================= 主循环 =================
    while True:
        this.console.clear_screen()
        
        # --- 顶部导航 ---
        nav_str = ""
        for i, title in enumerate(STAGES):
            if i == current_stage_idx:
                nav_str += f" ➤【{title}】 "
            else:
                nav_str += f"   {title}   "
        
        this.console.PRINT_DIVIDER("=")
        this.console.PRINT(nav_str, colors=(100, 255, 255))
        this.console.PRINT_DIVIDER("-")

        # ----------------------------------------------------
        # 阶段 1: 姓名设定
        # ----------------------------------------------------
        if current_stage_idx == 0:
            this.console.PRINT("首先，请在这个世界上留下你的名字。")
            this.console.PRINT("")
            
            curr_name = this.console.init.charaters_key['0'].get('全名', '未设定')
            curr_call = this.console.init.charaters_key['0'].get('称呼', '未设定')
            
            this.console.PRINT(this.cs(f" [1] 全名: {curr_name}").click("1"))
            this.console.PRINT(this.cs(f" [2] 称呼: {curr_call}").click("2"))
            this.console.PRINT("")
            this.console.PRINT(" (点击选项进行修改)")

        # ----------------------------------------------------
        # 阶段 2: 种族与属性
        # ----------------------------------------------------
        elif current_stage_idx == 1:
            this.console.PRINT(f"剩余点数: {bonus_points}", colors=(255, 215, 0))
            this.console.PRINT_DIVIDER("-")
            
            # --- 种族 ---
            this.console.PRINT("【 种 族 】")
            race_line = this.cs("")
            for rid in RACE_IDS:
                r_name = kojo.TALENTNAME.get(rid, f"Race{rid}")
                is_set = (kojo.TALENT.get(rid, 0) == '1')
                
                race_id_num = str(100 + int(rid) - 190)  # 将190-196映射为100-106
                if is_set:
                    race_line += this.cs(f"[★ {r_name}]").click(race_id_num).set_color((255, 255, 0)) + " "
                else:
                    race_line += this.cs(f"[  {r_name}]").click(race_id_num).set_color((150, 150, 150)) + " "
            this.console.PRINT(race_line)

            # --- 属性 ---
            this.console.PRINT("")
            this.console.PRINT("【 基 础 能 力 】")
            for bid in BASE_IDS:
                b_name = kojo.BASENAME.get(bid, f"Attr{bid}")
                val = int(kojo.BASE.get(b_name, 1000))
                
                attr_num_dec = str(200 + int(bid))  # 减少属性ID映射为200+
                attr_num_inc = str(300 + int(bid))  # 增加属性ID映射为300+
                line = this.cs(f"{b_name}: {val:>4}  ")
                line += this.cs("[-]").click(attr_num_dec).set_color((100, 200, 255) if val > 500 else (100, 100, 100))
                line += " / "
                line += this.cs("[+]").click(attr_num_inc).set_color((255, 100, 100) if bonus_points > 0 else (100, 100, 100))
                
                this.console.PRINT(line)

        # ----------------------------------------------------
        # 阶段 3: 素质细节 (分类菜单)
        # ----------------------------------------------------
        elif current_stage_idx == 2:
            this.console.PRINT("【 详 细 设 定 】")
            
            # 分类导航
            cat_line = this.cs("")
            cat_idx = 0
            for cat in TALENT_CONFIG.keys():
                cat_num = str(400 + cat_idx)  # 分类映射为400+
                if selected_talent_category == cat:
                    cat_line += this.cs(f"[{cat}]").set_color((100, 255, 255)) + " "
                else:
                    cat_line += this.cs(f" {cat} ").click(cat_num).set_color((150, 150, 150)) + " "
                cat_idx += 1
            this.console.PRINT(cat_line)
            this.console.PRINT_DIVIDER("-")

            if not selected_talent_category:
                selected_talent_category = list(TALENT_CONFIG.keys())[0]

            configs = TALENT_CONFIG[selected_talent_category]
            
            # [关键] 获取当前性别用于互斥判定
            curr_sex = int(kojo.TALENT.get('2', 1)) # 1=女, 2=男, 3=扶他
            
            count = 0
            row_str = this.cs("")
            
            for cfg in configs:
                tid = cfg['id']
                tname = cfg['name']
                curr_val = int(kojo.TALENT.get(tid, 0))
                
                # --- [新增] 互斥判定逻辑 ---
                is_disabled = False
                if tid == '0' and curr_sex == 2: is_disabled = True # 男性不可选处女
                if tid == '1' and curr_sex == 1: is_disabled = True # 女性不可选童贞
                
                # --- 渲染逻辑 ---
                item = None
                
                if is_disabled:
                    # [变灰且不可点击]
                    item = this.cs(f"🔒 {tname:<6}").set_color((80, 80, 80))
                
                else:
                    # [正常渲染]
                    # A. 开关型 (Bool)
                    if cfg['type'] == 'bool':
                        status = "✅" if curr_val else "⬜"
                        color = (100, 255, 100) if curr_val else (180, 180, 180)
                        bool_num = str(500 + int(tid))  # bool类型映射为500+
                        item = this.cs(f"{status} {tname:<6}").click(bool_num).set_color(color)
                    
                    # B. 数值/枚举型 (Range)
                    elif cfg['type'] == 'range':
                        val_display = str(curr_val)
                        if 'map' in cfg and val_display in cfg['map']:
                            val_display = cfg['map'][val_display]
                        
                        range_num = str(600 + int(tid))  # range类型映射为600+
                        item = this.cs(f"🔷 {tname}: <{val_display}>").click(range_num).set_color((100, 200, 255))

                row_str += item + "   "
                count += 1
                if count % 3 == 0:
                    this.console.PRINT(row_str)
                    row_str = this.cs("")
            
            if count % 3 != 0: this.console.PRINT(row_str)

        # ----------------------------------------------------
        # 阶段 4: 出生地
        # ----------------------------------------------------
        elif current_stage_idx == 3:
            this.console.PRINT("最后，请选择你的降生之地。")
            map_data = getattr(this.console, 'map_data', {})
            
            sel_big = getattr(this, 'temp_init_big', None)
            
            if not sel_big:
                # 显示大地图列表
                count = 0
                row = this.cs("")
                for big_map, content in map_data.items():
                    if big_map == 'DungeonInstance': continue
                    if not isinstance(content, dict): continue
                    
                    # 使用辅助函数获取地图显示名称（ID-名称格式）
                    display_name = get_map_display_name(this, big_map)
                    big_num = str(700 + int(big_map)) if big_map.isdigit() else f"700_{big_map}"
                    row += this.cs(f"[{display_name}]").click(big_num) + "  "
                    count += 1
                    if count % 4 == 0:
                        this.console.PRINT(row)
                        row = this.cs("")
                if count % 4 != 0: this.console.PRINT(row)
            else:
                # 显示当前选中大地图的区域名称
                big_display_name = get_map_display_name(this, sel_big)
                this.console.PRINT(f"区域: {big_display_name}", colors=(255, 215, 0))
                small_maps = map_data.get(sel_big, {})
                
                # 显示小地图列表
                count = 0
                row = this.cs("")
                for sm_map in small_maps.keys():
                    # 过滤掉非地图项
                    if sm_map in ['状态', 'dungeon_level', 'description', '音乐']: continue
                    
                    # 使用辅助函数获取小地图显示名称（ID-名称格式）
                    display_name = get_map_display_name(this, sm_map)
                    small_num = str(800 + int(sm_map)) if sm_map.isdigit() else f"800_{sm_map}"
                    row += this.cs(f"[{display_name}]").click(small_num) + "  "
                    count += 1
                    if count % 4 == 0:
                        this.console.PRINT(row)
                        row = this.cs("")
                if count % 4 != 0: this.console.PRINT(row)
                
                this.console.PRINT("")
                this.console.PRINT(this.cs("[999]<< 重选区域").click("999"))

        # ================= 底部导航 =================
        this.console.PRINT("")
        this.console.PRINT_DIVIDER("=")
        
        nav_btns = this.cs("")
        if current_stage_idx > 0:
            nav_btns += this.cs("[7] < 上一步").click("7") + "      "
        
        if current_stage_idx < len(STAGES) - 1:
            nav_btns += this.cs("[9] 下一步 >").click("9")
        else:
            if getattr(this, 'temp_init_ready', False):
                nav_btns += this.cs("[0] ★ 完成设定并开始游戏 ★").click("0").set_color((100, 255, 100))
            else:
                nav_btns += this.cs("请选择出生地").set_color((150, 150, 150))
                
        this.console.PRINT(nav_btns)

        # ================= 输入处理 =================
        inp = this.console.INPUT()

        # 导航
        if inp == '9': current_stage_idx += 1  # 下一步
        elif inp == '7': current_stage_idx -= 1  # 上一步
        
        # 阶段 0: 名字
        elif inp == '1':  # set_name
            this.console.PRINT("输入全名:")
            n = this.console.INPUT()
            if n: this.console.init.charaters_key['0']['全名'] = n
        elif inp == '2':  # set_call
            this.console.PRINT("输入称呼:")
            n = this.console.INPUT()
            if n: this.console.init.charaters_key['0']['称呼'] = n

        # 阶段 1: 种族与属性 (100-106种族, 200+减少属性, 300+增加属性)
        elif inp and inp.isdigit():
            inp_num = int(inp)
            
            # 种族选择 (100-106 -> 190-196)
            if 100 <= inp_num <= 106:
                rid = str(inp_num - 100 + 190)
                for r in RACE_IDS: kojo.TALENT.set(r, 0)
                kojo.TALENT.set(rid, 1)
            
            # 减少属性 (200-203 -> 0,1,6,11)
            elif 200 <= inp_num <= 211:
                bid = str(inp_num - 200)
                bname = kojo.BASENAME.get(bid)
                curr = int(kojo.BASE.get(bname, 1000))
                if curr > 500:
                    kojo.BASE.set(bname, curr - 100)
                    bonus_points += 1
            
            # 增加属性 (300-311 -> 0,1,6,11)
            elif 300 <= inp_num <= 311:
                bid = str(inp_num - 300)
                bname = kojo.BASENAME.get(bid)
                if bonus_points > 0:
                    kojo.BASE.set(bname, int(kojo.BASE.get(bname, 1000)) + 100)
                    bonus_points -= 1

            # 阶段 2: 素质分类选择 (400+)
            elif 400 <= inp_num < 500:
                cat_list = list(TALENT_CONFIG.keys())
                cat_idx = inp_num - 400
                if cat_idx < len(cat_list):
                    selected_talent_category = cat_list[cat_idx]

            # 阶段 2: Bool类型素质 (500+)
            elif 500 <= inp_num < 600:
                tid = str(inp_num - 500)
                curr = int(kojo.TALENT.get(tid, 0))
                kojo.TALENT.set(tid, 0 if curr else 1)

            # 阶段 2: Range类型素质 (600+)
            elif 600 <= inp_num < 700:
                tid = str(inp_num - 600)
                # 查找配置获取min和max
                curr = int(kojo.TALENT.get(tid, 0))
                for cfg in TALENT_CONFIG.get(selected_talent_category, []):
                    if cfg['id'] == tid and cfg['type'] == 'range':
                        min_v = cfg['min']
                        max_v = cfg['max']
                        # 循环逻辑：+1，如果超过最大值则回到最小值
                        next_val = curr + 1
                        if next_val > max_v: next_val = min_v
                        kojo.TALENT.set(tid, next_val)
                        break

            # 阶段 3: 大地图选择 (700+)
            elif 700 <= inp_num < 800:
                map_data = getattr(this.console, 'map_data', {})
                big_map = str(inp_num - 700)
                if big_map in map_data:
                    this.temp_init_big = big_map

            # 阶段 3: 小地图选择 (800+)
            elif 800 <= inp_num < 900:
                if hasattr(this, 'temp_init_big') and this.temp_init_big:
                    sm_map = str(inp_num - 800)
                    map_data = getattr(this.console, 'map_data', {})
                    if this.temp_init_big in map_data:
                        small_maps = map_data.get(this.temp_init_big, {})
                        if sm_map in small_maps:
                            this.console.init.charaters_key['0']['大地图'] = this.temp_init_big
                            this.console.init.charaters_key['0']['小地图'] = sm_map
                            this.temp_init_ready = True

            # 重选区域
            elif inp == '999':
                this.temp_init_big = None
                this.temp_init_ready = False

            # 完成
            elif inp == '0':
                if current_stage_idx == 3 and getattr(this, 'temp_init_ready', False):
                    this.console.PRINT("正在构建世界数据...", colors=(100, 255, 100))
                    #this.event_manager.trigger_event('build_state', this)
                    #this.event_manager.trigger_event('init_race', this)
                    
                    if hasattr(this, 'temp_init_big'): del this.temp_init_big
                    if hasattr(this, 'temp_init_ready'): del this.temp_init_ready
                    
                    break 

# 注册
event_custom_chara_init.event_trigger = "custom_chara_init"
event_custom_chara_init.is_main_event = True
