import random


class EraDataProxy:
    """
    辅助类：用于模拟 ERA 的数据访问方式。
    允许通过 handler.BASE['0'] (获取角色0的BASE字典)
    或者 handler.BASE.get('体力') (获取当前TARGET的体力)
    """

    def __init__(self, handler, data_category):
        self.handler = handler
        self.category = data_category  # 例如 '基础', '能力', '素质'

    def __getitem__(self, chara_id):
        """支持 handler.BASE['0'] 这种显式指定角色的访问"""
        return self.handler.get_chara_data(str(chara_id), self.category)

    def get(self, key, default=None):
        """支持 handler.BASE.get('体力') 这种默认读取 TARGET 的访问"""
        target_id = self.handler.TARGET
        if target_id is None:
            return default
        data = self.handler.get_chara_data(target_id, self.category)
        return data.get(str(key), default)

    def set(self, key, value, chara_id=None):
        """设置数值"""
        target = chara_id if chara_id is not None else self.handler.TARGET
        if target:
            # 这里直接修改内存中的 charaters_key
            if self.category not in self.handler.init.charaters_key[target]:
                self.handler.init.charaters_key[target][self.category] = {}
            self.handler.init.charaters_key[target][self.category][str(
                key)] = str(value)


class EraKojoHandler:
    def __init__(self, console, event_context=None):
        """
        :param console: Pera 的 console 对象 (包含 init 数据)
        :param event_context: 事件触发时传递的字典 (包含 TARGET, SELECTCOM 等)
        """
        self.console = console
        self.init = console.init
        self.ctx = event_context if event_context else {}

        # 结果变量
        self.RESULT = ""
        self.RESULTS = ""

    # ==========================
    # 基础变量映射
    # ==========================
    @classmethod
    def from_state(cls, state_dict):
        """
        [新增] 工厂方法：直接从 state_dict 大字典初始化 Handler
        """
        # 1. 提取核心对象
        console = state_dict['console']
        
        # 2. 提取会话信息
        session = state_dict.get('session', {})
        globals_vars = state_dict.get('globals', {}).get('variables', {})
        
        # 3. 构建 context (将 state_dict 的结构扁平化为 ERB 习惯的变量)
        context = {
            # --- ID 映射 ---
            'TARGET': session.get('chara_id'),
            'PLAYER': session.get('master_id'),
            'MASTER': session.get('master_id'),
            'ASSI': [], # 如果 state_dict 里有助手列表，在这里处理
            
            # --- 指令映射 ---
            # 注意转为字符串，因为 CSV 读取的数据通常是字符串
            'SELECTCOM': str(globals_vars.get('SELECTCOM', 0)),
            'PREVCOM': str(globals_vars.get('PREVCOM', 0)),
            
            # --- 参数映射 (PALAM/UP/DOWN) ---
            # 如果你的 state_dict 里有这些计算过程数据，在这里映射
            # 如果没有，给空字典防止报错
            'PALAM': {}, 
            'UP': {},
            'DOWN': {},
            
            # --- 原始 state 引用 (可选) ---
            # 如果你想在口上里访问 state_dict 里的特殊数据（如 ui, history）
            '_RAW_STATE': state_dict 
        }
        
        # 4. 返回初始化好的实例
        return cls(console, context)
    @property
    def MASTER(self):
        # 假设主角ID存储在 global_key 的 System 表或者直接约定为 '0'
        return self.init.global_key.get('System', {}).get('MASTER', '0')

    @property
    def TARGET(self):
        return self.ctx.get('TARGET')

    @property
    def ASSI(self):
        return self.ctx.get('ASSI', [])

    @property
    def PLAYER(self):
        return self.ctx.get('PLAYER', self.MASTER)

    @property
    def CHARANUM(self):
        return len(self.init.chara_ids)

    @property
    def SELECTCOM(self):
        return self.ctx.get('SELECTCOM')

    @property
    def PREVCOM(self):
        return self.ctx.get('PREVCOM')

    # ==========================
    # 角色数据访问 (2D 数组/字典模拟)
    # ==========================

    def get_chara_data(self, chara_id, category):
        """底层方法：安全获取角色特定类别的数据字典"""
        if chara_id not in self.init.charaters_key:
            return {}
        return self.init.charaters_key[chara_id].get(category, {})

    @property
    def NO(self):
        """反向查询：返回当前 TARGET 在 chara_ids 列表中的索引"""
        target = self.TARGET
        if target in self.init.chara_ids:
            return self.init.chara_ids.index(target)
        return -1

    # 映射 Pera 的 csv 分类到 ERA 概念
    # Pera里面建议您把刻印经验什么的都一股脑的加到角色的根字典下，您要相信python的数据处理能力
    # 注意：这里的 '基础', '能力' 等需要和keywords 对应
    @property
    def BASE(self): return EraDataProxy(self, '基础')

    @property
    def MAXBASE(self): return EraDataProxy(self, '基础上限')  # 需新增逻辑

    @property
    def ABL(self): return EraDataProxy(self, '能力')

    @property
    def TALENT(self): return EraDataProxy(self, '素质')

    @property
    def EXP(self): return EraDataProxy(self, '经验')  # 假设CSV里叫经验

    @property
    def MARK(self): return EraDataProxy(self, '刻印')  # 假设CSV里叫刻印

    @property
    def CFLAG(self): return EraDataProxy(self, 'CFLAG')  # 也就是直接访问角色根字典下的CFLAG键

    @property
    def JUEL(self): return EraDataProxy(self, '珠')
    @property
    def TCVAR(self): return EraDataProxy(self, 'TCVAR') # 如果你的CSV有这个分类
    @property
    def NAME(self):
        return self.init.charaters_key.get(self.TARGET, {}).get('全名', 'Unknown')
    @property
    def EQUIP(self): return EraDataProxy(self, '装备') # 假设CSV里叫装备
    @property
    def CALLNAME(self):
        return self.init.charaters_key.get(self.TARGET, {}).get('小名', self.NAME)

    # 关系相性 (特殊处理，因为它是嵌套字典)
    def RELATION(self, target_chara_id):
        """查询 TARGET 对 target_chara_id 的相性"""
        subject = self.TARGET
        if not subject:
            return 0

        relation_dict = self.init.charaters_key[subject].get('相性', {})
        # 默认相性为 100% (即 100)，如果没有定义
        return int(relation_dict.get(target_chara_id, 100))
    # ==========================
    # 物品操作接口 (Inventory API)
    # ==========================
    
    def ITEM_ADD(self, item_id, count=1, chara_id=None):
        """
        获得物品
        :param item_id: 物品ID (对应 Item.csv)
        :param count: 数量
        :param chara_id: 指定角色，默认为 TARGET
        """
        target = chara_id if chara_id is not None else self.TARGET
        if not target: return
        
        # 获取角色状态引用
        chara_state = self.console.allstate.get(target)
        if not chara_state: return

        # 确保 inventory 字典存在
        if 'inventory' not in chara_state:
            chara_state['inventory'] = {}
            
        inv = chara_state['inventory']
        item_id = str(item_id)
        
        # 增加数量
        inv[item_id] = inv.get(item_id, 0) + count
        
        # 获取物品名称用于提示
        item_name = self.ITEMNAME.get(item_id, f"未知物品({item_id})")
        self.console.PRINT(f"{chara_state['name']} 获得了 {item_name} x{count}", colors=(100, 255, 100))

    def ITEM_REMOVE(self, item_id, count=1, chara_id=None):
        """
        移除物品
        """
        target = chara_id if chara_id is not None else self.TARGET
        if not target: return
        
        chara_state = self.console.allstate.get(target)
        inv = chara_state.get('inventory', {})
        item_id = str(item_id)
        
        if item_id in inv:
            if inv[item_id] >= count:
                inv[item_id] -= count
                # 如果数量为0，可以选择删除键，或者留着显示0
                if inv[item_id] <= 0:
                    del inv[item_id]
                
                item_name = self.ITEMNAME.get(item_id, f"未知物品({item_id})")
                self.console.PRINT(f"{chara_state['name']} 失去了 {item_name} x{count}", colors=(255, 100, 100))
                return True
            else:
                self.console.PRINT(f"物品数量不足！", colors=(255, 0, 0))
                return False
        return False

    def ITEM_HAS(self, item_id, chara_id=None):
        """查询拥有数量"""
        target = chara_id if chara_id is not None else self.TARGET
        if not target: return 0
        
        inv = self.console.allstate.get(target, {}).get('inventory', {})
        return inv.get(str(item_id), 0)
    # ==========================
    # 临时/事件状态变量 (通常在 ctx 中)
    # ==========================
    @property
    def PALAM(self): return self.ctx.get('PALAM', {})

    @property
    def UP(self): return self.ctx.get('UP', {})

    @property
    def DOWN(self): return self.ctx.get('DOWN', {})

    @property
    def LOSEBASE(self): return self.ctx.get('LOSEBASE', {})

    @property
    def TEQUIP(self): return self.ctx.get('TEQUIP', {})  # 装备状态

    @property
    def EX(self): return self.ctx.get('EX', {'C': 0, 'V': 0, 'A': 0, 'B': 0})

    @property
    def STAIN(self): return self.ctx.get('STAIN', [])  # 污渍列表

    # ==========================
    # 名称/全局数据查找
    # ==========================
    @property
    def BASENAME(self): return self.init.global_key.get('Base', {})
    @property
    def ABLNAME(self): return self.init.global_key.get('Abl', {})

    @property
    def TALENTNAME(self): return self.init.global_key.get('Talent', {})

    @property
    def EXPNAME(self): return self.init.global_key.get('Exp', {})

    @property
    def ITEMNAME(self):
        # 这是一个动态构建的字典，根据 Item.csv
        item_data = self.init.global_key.get('Item', {})
        return {k: v.get('name') for k, v in item_data.items()}

    @property
    def ITEM(self):
        # 获取当前持有的物品数量，假设存储在 Global 的 Inventory 中
        # 结构：{'0':{'物品id':1,...},...}
        # 或者存储在 MASTER 的 CFLAG 中，这里假设是全局背包
        return self.init.global_key.get('Inventory', {})

    @property
    def STR(self): return self.init.global_key.get('Str', {})

    @property
    def SAVESTR(self): return self.init.global_key.get('SaveStr', {})
    # ==========================
    # 地牢相关
    # ==========================
    @property
    def DUNGEON(self):
        '''
        角色属性相关
        使用:kojo.DUNGEON.get('0')
        '''
        return EraDataProxy(self,'角色地牢属性')
    @property
    def ABNORMAL(self):
        '''
        异常属性
        使用:kojo.ABNORMAL.get('虚弱')
        '''
        return EraDataProxy(self,'异常状态')
    # ==========================
    # 辅助功能
    # ==========================

    def Rand(self, val):
        """
        Rand(10) -> 0~9
        Rand([1, 2, 3]) -> 随机选一个
        """
        if isinstance(val, int):
            return random.randint(0, val - 1)
        elif isinstance(val, list) or isinstance(val, tuple):
            return random.choice(val)
        return 0

    def print_kojo(self, text):
        """便捷输出口上"""
        self.console.PRINT(text)
