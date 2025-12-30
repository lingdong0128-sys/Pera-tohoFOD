"""
口上调用助手模块
提供统一的口上调用接口，支持回退到通用口上
"""
from utils.era_handler import EraKojoHandler


def call_kojo_with_fallback(this, kojo_context, event_name, fallback_event_name):
    """
    调用口上事件，如果失败则回退到通用口上
    
    :param this: 当前对象
    :param kojo_context: 口上上下文字典
    :param event_name: 主要事件名（特定角色口上）
    :param fallback_event_name: 回退事件名（通用口上）
    :return: 是否成功调用
    """
    this.current_kojo_context = kojo_context
    
    try:
        # 使用静默模式调用特定角色口上，未找到时不报错
        result = this.event_manager.trigger_event(event_name, this, silent=True)
        
        # 如果找不到事件，回退到通用口上
        if result is None:
            this.event_manager.trigger_event(fallback_event_name, this)
            return False
        return True
        
    except Exception as e:
        this.console.PRINT(f"口上调用失败: {event_name}\n错误: {e}", colors=(255, 100, 100))
        return False
    finally:
        this.current_kojo_context = None


def call_daily_kojo(this, action, target_id, event_manager, console):
    """
    调用日常系口上
    
    :param this: 当前对象
    :param action: 动作类型 (聊天/问候/告别/触摸/抱住/询问/观察/邀请)
    :param target_id: 目标角色ID
    :param event_manager: 事件管理器
    :param console: 控制台对象
    """
    # 获取口上类型
    kojo_type = console.init.charaters_key[target_id].get('口上类型', '初期口上')
    
    # 构建口上上下文
    state = event_manager.trigger_event('get_context_state', this)
    kojo_context = {
        'TARGET': target_id,
        'PLAYER': state['session'].get('master_id', '0'),
        'ASSI': state['session'].get('assi_id', []),
        'SELECTCOM': '0',
        'MODE': state['session'].get('scene_type', '日常'),
        'TIME': state['session'].get('time_of_day', '昼'),
        'WEATHER': state['session'].get('weather', '晴'),
        'PALAM': state.get('calc', {}).get('PALAM', {}),
        'UP': state.get('calc', {}).get('UP', {}),
        'DOWN': state.get('calc', {}).get('DOWN', {}),
        'LOSEBASE': state.get('calc', {}).get('LOSEBASE', {}),
        'TEQUIP': state['chara'].get('equip', {}),
        'EX': state.get('calc', {}).get('EX', {'C':0, 'V':0, 'A':0, 'B':0}),
        'STAIN': state['chara'].get('stain', {}),
        '_RAW_STATE': state
    }
    
    # 构建事件名
    specific_event = f"{target_id}_{kojo_type}_日常_{action}"
    fallback_event = f"common_日常_{action}"
    
    # 调用
    return call_kojo_with_fallback(this, kojo_context, specific_event, fallback_event)


def call_h_kojo(this, action, target_id, event_manager, console):
    """
    调用H系口上
    
    :param this: 当前对象
    :param action: 动作类型 (开始/高潮/接吻/爱抚/结束)
    :param target_id: 目标角色ID
    :param event_manager: 事件管理器
    :param console: 控制台对象
    """
    kojo_type = console.init.charaters_key[target_id].get('H口上类型', 'H口上')
    
    # 构建口上上下文
    state = event_manager.trigger_event('get_context_state', this)
    kojo_context = {
        'TARGET': target_id,
        'PLAYER': state['session'].get('master_id', '0'),
        'ASSI': state['session'].get('assi_id', []),
        'SELECTCOM': '0',
        'MODE': 'H',
        'TIME': state['session'].get('time_of_day', '昼'),
        'WEATHER': state['session'].get('weather', '晴'),
        'PALAM': state.get('calc', {}).get('PALAM', {}),
        'UP': state.get('calc', {}).get('UP', {}),
        'DOWN': state.get('calc', {}).get('DOWN', {}),
        'LOSEBASE': state.get('calc', {}).get('LOSEBASE', {}),
        'TEQUIP': state['chara'].get('equip', {}),
        'EX': state.get('calc', {}).get('EX', {'C':0, 'V':0, 'A':0, 'B':0}),
        'STAIN': state['chara'].get('stain', {}),
        '_RAW_STATE': state
    }
    
    # 构建事件名
    specific_event = f"{target_id}_{kojo_type}_H_{action}"
    fallback_event = f"common_H_{action}"
    
    # 调用
    return call_kojo_with_fallback(this, kojo_context, specific_event, fallback_event)


def call_dungeon_kojo(this, action, target_id, event_manager, console):
    """
    调用地牢系口上
    
    :param this: 当前对象
    :param action: 动作类型 (遭遇敌人/胜利/失败/受伤/发现宝箱/休息)
    :param target_id: 目标角色ID
    :param event_manager: 事件管理器
    :param console: 控制台对象
    """
    kojo_type = console.init.charaters_key[target_id].get('地牢口上类型', '地牢口上')
    
    # 构建口上上下文
    state = event_manager.trigger_event('get_context_state', this)
    kojo_context = {
        'TARGET': target_id,
        'PLAYER': state['session'].get('master_id', '0'),
        'ASSI': state['session'].get('assi_id', []),
        'SELECTCOM': '0',
        'MODE': '地牢',
        'TIME': state['session'].get('time_of_day', '昼'),
        'WEATHER': state['session'].get('weather', '晴'),
        'PALAM': state.get('calc', {}).get('PALAM', {}),
        'UP': state.get('calc', {}).get('UP', {}),
        'DOWN': state.get('calc', {}).get('DOWN', {}),
        'LOSEBASE': state.get('calc', {}).get('LOSEBASE', {}),
        'TEQUIP': state['chara'].get('equip', {}),
        'EX': state.get('calc', {}).get('EX', {'C':0, 'V':0, 'A':0, 'B':0}),
        'STAIN': state['chara'].get('stain', {}),
        '_RAW_STATE': state
    }
    
    # 构建事件名
    specific_event = f"{target_id}_{kojo_type}_地牢_{action}"
    fallback_event = f"common_地牢_{action}"
    
    # 调用
    return call_kojo_with_fallback(this, kojo_context, specific_event, fallback_event)


# ============================
# 下面是通用口上调用事件
# 可以直接在游戏中调用
# ============================

def event_通用口上_日常(this, action, target_id=None):
    """
    调用日常系通用口上的统一入口
    使用方法: this.event_manager.trigger_event('通用口上_日常', this, '聊天', '1')
    
    :param this: 当前对象
    :param action: 动作类型
    :param target_id: 目标角色ID，默认为当前选择对象
    """
    if target_id is None:
        target_id = this.console.init.charaters_key['0'].get('选择对象')
    
    if not target_id:
        this.console.PRINT("没有选择对象！", colors=(255, 100, 100))
        return
    
    # 挂载必要的属性供call函数使用
    this.event_manager = this.event_manager
    this.console = this.console
    
    call_daily_kojo(this, action, target_id, this.event_manager, this.console)


event_通用口上_日常.event_trigger = '通用口上_日常'


def event_通用口上_H(this, action, target_id=None):
    """
    调用H系通用口上的统一入口
    使用方法: this.event_manager.trigger_event('通用口上_H', this, '开始', '1')
    
    :param this: 当前对象
    :param action: 动作类型
    :param target_id: 目标角色ID，默认为当前选择对象
    """
    if target_id is None:
        target_id = this.console.init.charaters_key['0'].get('选择对象')
    
    if not target_id:
        this.console.PRINT("没有选择对象！", colors=(255, 100, 100))
        return
    
    call_h_kojo(this, action, target_id, this.event_manager, this.console)


event_通用口上_H.event_trigger = '通用口上_H'


def event_通用口上_地牢(this, action, target_id=None):
    """
    调用地牢系通用口上的统一入口
    使用方法: this.event_manager.trigger_event('通用口上_地牢', this, '胜利', '1')
    
    :param this: 当前对象
    :param action: 动作类型
    :param target_id: 目标角色ID，默认为当前选择对象
    """
    if target_id is None:
        target_id = this.console.init.charaters_key['0'].get('选择对象')
    
    if not target_id:
        this.console.PRINT("没有选择对象！", colors=(255, 100, 100))
        return
    
    call_dungeon_kojo(this, action, target_id, this.event_manager, this.console)


event_通用口上_地牢.event_trigger = '通用口上_地牢'


# ============================
# 便捷事件 - 具体动作的快捷调用
# ============================

def event_日常_问候(this, target_id=None):
    """日常问候快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '问候', target_id)
event_日常_问候.event_trigger = '日常_问候'

def event_日常_告别(this, target_id=None):
    """日常告别快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '告别', target_id)
event_日常_告别.event_trigger = '日常_告别'

def event_日常_触摸(this, target_id=None):
    """日常触摸快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '触摸', target_id)
event_日常_触摸.event_trigger = '日常_触摸'

def event_日常_抱住(this, target_id=None):
    """日常抱住快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '抱住', target_id)
event_日常_抱住.event_trigger = '日常_抱住'

def event_日常_询问(this, target_id=None):
    """日常询问快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '询问', target_id)
event_日常_询问.event_trigger = '日常_询问'

def event_日常_观察(this, target_id=None):
    """日常观察快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '观察', target_id)
event_日常_观察.event_trigger = '日常_观察'

def event_日常_邀请(this, target_id=None):
    """日常邀请快捷调用"""
    this.event_manager.trigger_event('通用口上_日常', this, '邀请', target_id)
event_日常_邀请.event_trigger = '日常_邀请'

# H系快捷事件
def event_H_开始(this, target_id=None):
    """H开始快捷调用"""
    this.event_manager.trigger_event('通用口上_H', this, '开始', target_id)
event_H_开始.event_trigger = 'H_开始'

def event_H_高潮(this, target_id=None):
    """H高潮快捷调用"""
    this.event_manager.trigger_event('通用口上_H', this, '高潮', target_id)
event_H_高潮.event_trigger = 'H_高潮'

def event_H_接吻(this, target_id=None):
    """H接吻快捷调用"""
    this.event_manager.trigger_event('通用口上_H', this, '接吻', target_id)
event_H_接吻.event_trigger = 'H_接吻'

def event_H_爱抚(this, target_id=None):
    """H爱抚快捷调用"""
    this.event_manager.trigger_event('通用口上_H', this, '爱抚', target_id)
event_H_爱抚.event_trigger = 'H_爱抚'

def event_H_结束(this, target_id=None):
    """H结束快捷调用"""
    this.event_manager.trigger_event('通用口上_H', this, '结束', target_id)
event_H_结束.event_trigger = 'H_结束'

# 地牢系快捷事件
def event_地牢_遭遇敌人(this, target_id=None):
    """地牢遭遇敌人快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '遭遇敌人', target_id)
event_地牢_遭遇敌人.event_trigger = '地牢_遭遇敌人'

def event_地牢_胜利(this, target_id=None):
    """地牢胜利快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '胜利', target_id)
event_地牢_胜利.event_trigger = '地牢_胜利'

def event_地牢_失败(this, target_id=None):
    """地牢失败快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '失败', target_id)
event_地牢_失败.event_trigger = '地牢_失败'

def event_地牢_受伤(this, target_id=None):
    """地牢受伤快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '受伤', target_id)
event_地牢_受伤.event_trigger = '地牢_受伤'

def event_地牢_发现宝箱(this, target_id=None):
    """地牢发现宝箱快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '发现宝箱', target_id)
event_地牢_发现宝箱.event_trigger = '地牢_发现宝箱'

def event_地牢_休息(this, target_id=None):
    """地牢休息快捷调用"""
    this.event_manager.trigger_event('通用口上_地牢', this, '休息', target_id)
event_地牢_休息.event_trigger = '地牢_休息'
