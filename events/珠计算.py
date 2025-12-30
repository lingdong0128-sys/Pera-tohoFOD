"""
珠计算系统
根据Pera幻想FOD设计思路实现珠的计算逻辑
"""
from utils.era_handler import EraKojoHandler


# ========================
# 珠计算常量配置
# ========================

# 各部位珠的最大等级
MAX_PALAM_LEVEL = 5

# 快感系珠ID映射
PALAM_PLEASURE = {
    'C': '0',   # 快C
    'V': '1',   # 快V
    'A': '2',   # 快A
    'B': '3',   # 快B
    'M': '4',   # 快M
}

# 润滑珠ID
PALAM_LUBRICATION = '9'

# 精神系珠ID
PALAM_MENTAL = {
    '恭順': '10',
    '欲情': '11',
    '屈服': '12',
    '習得': '13',
    '恥情': '14',
    '苦痛': '15',
    '恐怖': '16',
}

# 好意系珠ID
PALAM_GOODWILL = {
    '好意': '20',
}

# 负面珠ID
PALAM_NEGATIVE = {
    '反感': '30',
    '不快': '31',
    '抑鬱': '32',
}


def calculate_required_palam(level, climax_count=0):
    """
    计算指定等级所需的珠数
    使用指数增长公式：第一级500，每级翻倍，并根据高潮次数修正
    
    参数:
        level: 目标等级
        climax_count: 该部位已高潮次数（用于敏感度修正）
    
    返回:
        达到该等级所需的累计珠数
    """
    if level <= 0:
        return 0
    
    # 基础公式：500 * 2^(level-1)
    base_required = 500 * (2 ** (level - 1))
    
    # 高潮次数修正：每高潮一次，需求增加10%（变得更敏感）
    sensitivity_modifier = 1 + (climax_count * 0.1)
    
    return int(base_required * sensitivity_modifier)


def calculate_level_from_palam(current_palam, climax_count=0):
    """
    根据当前珠数计算等级
    
    参数:
        current_palam: 当前珠数
        climax_count: 该部位已高潮次数
    
    返回:
        当前等级（0-5）
    """
    level = 0
    while level < MAX_PALAM_LEVEL:
        required = calculate_required_palam(level + 1, climax_count)
        if current_palam >= required:
            level += 1
        else:
            break
    return level


def calculate_palam_gain(base_gain, current_level, climax_count=0):
    """
    计算行为获得的珠数
    随着等级和次数的增加，获得更多珠（更敏感）
    
    参数:
        base_gain: 基础获得珠数
        current_level: 当前等级
        climax_count: 该部位已高潮次数
    
    返回:
        实际获得的珠数
    """
    # 等级修正：每级增加20%获得量
    level_modifier = 1 + (current_level * 0.2)
    
    # 高潮次数修正：每高潮一次增加10%获得量
    sensitivity_modifier = 1 + (climax_count * 0.1)
    
    return int(base_gain * level_modifier * sensitivity_modifier)


def add_palam(this, target_id, palam_id, base_gain):
    """
    为指定角色增加珠
    
    参数:
        this: 事件上下文
        target_id: 目标角色ID
        palam_id: 珠ID（字符串）
        base_gain: 基础获得珠数
    
    返回:
        dict: {
            'current_palam': 当前珠数,
            'level': 当前等级,
            'is_climax': 是否触发高潮,
            'climax_count': 高潮次数
        }
    """
    # 创建handler访问角色数据
    context = {'TARGET': target_id}
    kojo = EraKojoHandler(this.console, context)
    
    # 获取当前珠数和高潮次数
    current_palam = int(kojo.JUEL.get(palam_id, 0))
    climax_count_key = f'{palam_id}_高潮次数'
    climax_count = int(kojo.CFLAG.get(climax_count_key, 0))
    
    # 计算当前等级
    current_level = calculate_level_from_palam(current_palam, climax_count)
    
    # 计算实际获得的珠数
    actual_gain = calculate_palam_gain(base_gain, current_level, climax_count)
    
    # 增加珠数
    new_palam = current_palam + actual_gain
    kojo.JUEL.set(palam_id, new_palam, target_id)
    
    # 计算新等级
    new_level = calculate_level_from_palam(new_palam, climax_count)
    
    # 判断是否触发高潮（达到5级）
    is_climax = False
    if new_level >= MAX_PALAM_LEVEL:
        is_climax = True
        
        # 清空该部位的珠
        kojo.JUEL.set(palam_id, 0, target_id)
        
        # 增加高潮次数
        new_climax_count = climax_count + 1
        kojo.CFLAG.set(climax_count_key, new_climax_count, target_id)
        
        # 记录总高潮次数
        total_climax_key = '总高潮次数'
        total_climax = int(kojo.CFLAG.get(total_climax_key, 0)) + 1
        kojo.CFLAG.set(total_climax_key, total_climax, target_id)
    
    return {
        'current_palam': kojo.JUEL.get(palam_id, 0),
        'level': new_level,
        'is_climax': is_climax,
        'climax_count': new_climax_count if is_climax else climax_count,
        'gain': actual_gain
    }


def get_palam_info(this, target_id, palam_id):
    """
    获取指定角色的珠信息
    
    参数:
        this: 事件上下文
        target_id: 目标角色ID
        palam_id: 珠ID
    
    返回:
        dict: {
            'current_palam': 当前珠数,
            'level': 当前等级,
            'climax_count': 高潮次数,
            'next_level_required': 下一级所需珠数
        }
    """
    context = {'TARGET': target_id}
    kojo = EraKojoHandler(this.console, context)
    
    current_palam = int(kojo.JUEL.get(palam_id, 0))
    climax_count_key = f'{palam_id}_高潮次数'
    climax_count = int(kojo.CFLAG.get(climax_count_key, 0))
    
    level = calculate_level_from_palam(current_palam, climax_count)
    
    # 计算下一级所需珠数
    if level < MAX_PALAM_LEVEL:
        next_level_required = calculate_required_palam(level + 1, climax_count)
    else:
        next_level_required = None  # 已达到最大等级
    
    return {
        'current_palam': current_palam,
        'level': level,
        'climax_count': climax_count,
        'next_level_required': next_level_required
    }


def check_negative_palam_limit(this, target_id):
    """
    检查负面珠是否超过限制（超过5级）
    
    参数:
        this: 事件上下文
        target_id: 目标角色ID
    
    返回:
        list: 超过限制的负面珠ID列表
    """
    context = {'TARGET': target_id}
    kojo = EraKojoHandler(this.console, context)
    
    over_limit_list = []
    
    for name, palam_id in PALAM_NEGATIVE.items():
        info = get_palam_info(this, target_id, palam_id)
        if info['level'] >= MAX_PALAM_LEVEL:
            over_limit_list.append(palam_id)
    
    return over_limit_list


# ========================
# 便捷接口函数
# ========================

def add_pleasure_palam(this, target_id, part, base_gain):
    """
    增加快感系珠的便捷接口
    
    参数:
        part: 部位 ('C', 'V', 'A', 'B', 'M')
    """
    if part not in PALAM_PLEASURE:
        print(f"警告：未知部位 {part}")
        return None
    
    palam_id = PALAM_PLEASURE[part]
    return add_palam(this, target_id, palam_id, base_gain)


def add_mental_palam(this, target_id, name, base_gain):
    """
    增加精神系珠的便捷接口
    
    参数:
        name: 珠名称（如 '恭順', '欲情'）
    """
    if name not in PALAM_MENTAL:
        print(f"警告：未知精神珠 {name}")
        return None
    
    palam_id = PALAM_MENTAL[name]
    return add_palam(this, target_id, palam_id, base_gain)


def add_goodwill_palam(this, target_id, name, base_gain):
    """
    增加好意系珠的便捷接口
    
    参数:
        name: 珠名称（如 '好意'）
    """
    if name not in PALAM_GOODWILL:
        print(f"警告：未知好意珠 {name}")
        return None
    
    palam_id = PALAM_GOODWILL[name]
    return add_palam(this, target_id, palam_id, base_gain)


def add_negative_palam(this, target_id, name, base_gain):
    """
    增加负面珠的便捷接口
    
    参数:
        name: 珠名称（如 '反感', '不快'）
    """
    if name not in PALAM_NEGATIVE:
        print(f"警告：未知负面珠 {name}")
        return None
    
    palam_id = PALAM_NEGATIVE[name]
    result = add_palam(this, target_id, palam_id, base_gain)
    
    # 检查是否超过限制
    over_limit = check_negative_palam_limit(this, target_id)
    if over_limit:
        print(f"警告：角色 {target_id} 的负面珠 {over_limit} 已达到限制")
    
    return result


def convert_goodwill_to_favor(this, target_id):
    """
    在每日结算时，将好意珠转换为好感信赖
    
    参数:
        this: 事件上下文
        target_id: 目标角色ID
    
    返回:
        int: 转换的好意珠数量
    """
    context = {'TARGET': target_id}
    kojo = EraKojoHandler(this.console, context)
    
    palam_id = PALAM_GOODWILL['好意']
    info = get_palam_info(this, target_id, palam_id)
    
    current_palam = info['current_palam']
    
    # 根据好意等级判断转换比例
    level = info['level']
    
    # 转换比例：
    # 等级0-1：10:1（低好感时转换效率低）
    # 等级2-3：5:1
    # 等级4+：3:1（高好感时转换效率高）
    if level <= 1:
        ratio = 10
    elif level <= 3:
        ratio = 5
    else:
        ratio = 3
    
    # 计算转换的好感和信赖
    converted_favor = current_palam // ratio
    converted_trust = current_palam // (ratio * 2)
    
    # 增加好感和信赖
    current_favor = int(kojo.CFLAG.get('好感度', 0))
    current_trust = int(kojo.CFLAG.get('信赖度', 0))
    
    kojo.CFLAG.set('好感度', current_favor + converted_favor, target_id)
    kojo.CFLAG.set('信赖度', current_trust + converted_trust, target_id)
    
    # 清空好意珠
    kojo.JUEL.set(palam_id, 0, target_id)
    
    return current_palam


# ========================
# 事件接口（供其他事件调用）
# ========================

def event_增加珠(this, target_id, palam_id, base_gain):
    """
    事件接口：为角色增加珠
    调用方式: this.event_manager.trigger_event('增加珠', this, '1', '0', 50)
    
    参数:
        target_id: 目标角色ID
        palam_id: 珠ID
        base_gain: 基础获得珠数
    
    返回:
        珠计算结果字典
    """
    return add_palam(this, target_id, palam_id, base_gain)

event_增加珠.event_trigger = '增加珠'


def event_获取珠信息(this, target_id, palam_id):
    """
    事件接口：获取珠信息
    调用方式: this.event_manager.trigger_event('获取珠信息', this, '1', '0')
    
    参数:
        target_id: 目标角色ID
        palam_id: 珠ID
    
    返回:
        珠信息字典
    """
    return get_palam_info(this, target_id, palam_id)

event_获取珠信息.event_trigger = '获取珠信息'


def event_每日结算_珠转换(this):
    """
    事件接口：每日结算时将好意珠转换为好感信赖
    调用方式: this.event_manager.trigger_event('每日结算_珠转换', this)
    """
    # 获取所有角色ID
    chara_ids = this.console.init.chara_ids
    
    total_converted = 0
    for chara_id in chara_ids:
        converted = convert_goodwill_to_favor(this, chara_id)
        if converted > 0:
            total_converted += converted
            chara_name = this.console.init.charaters_key[chara_id].get('全名', '未知')
            this.console.PRINT(f"{chara_name} 的好意珠已转换为好感信赖", colors=(200, 200, 255))
    
    if total_converted > 0:
        this.console.PRINT(f"\n本次结算共转换好意珠: {total_converted}", colors=(255, 255, 100))
    else:
        this.console.PRINT("本次结算没有好意珠需要转换", colors=(200, 200, 200))
    
    this.console.INPUT()

event_每日结算_珠转换.event_trigger = '每日结算_珠转换'
