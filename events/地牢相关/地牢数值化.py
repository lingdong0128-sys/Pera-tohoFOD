"""
地牢数值化系统
将角色基础属性转换为地牢属性，提供地牢属性查询和修改接口

功能：
- 初始化角色地牢属性
- 地牢属性查询
- 地牢属性修改
"""

from typing import Dict, Any, List, Optional


def event_dungeon_initialize_stats(this, char_id: str = None) -> Dict[int, int]:
    """
    初始化角色地牢属性
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        地牢属性字典 {属性ID: 属性值}
    """
    # 获取目标角色ID
    if char_id is None:
        char_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 创建kojo上下文
    from utils.era_handler import EraKojoHandler
    context = {'TARGET': char_id}
    kojo = EraKojoHandler(this.console, context)
    
    # 地牢属性存储在全局状态中
    if 'dungeon_stats' not in this.console.allstate:
        this.console.allstate['dungeon_stats'] = {}
    
    if char_id not in this.console.allstate['dungeon_stats']:
        this.console.allstate['dungeon_stats'][char_id] = {}
    
    dungeon_stats = this.console.allstate['dungeon_stats'][char_id]
    
    # 获取角色基础属性
    # 注意：这里需要假设角色CSV中有相应的属性，如果不存在使用默认值
    base_stamina = int(kojo.BASE.get('体力', 100))
    base_attack = int(kojo.BASE.get('攻击', 10))
    base_defense = int(kojo.BASE.get('防御', 5))
    base_agility = int(kojo.BASE.get('敏捷', 10))
    role = kojo.CALLNAME if hasattr(kojo, 'CALLNAME') else ''
    
    # 转换基础属性到地牢属性
    # 0: 攻击
    dungeon_stats[0] = base_attack
    
    # 1: 防御
    dungeon_stats[1] = base_defense
    
    # 4: 情欲值 - 初始为0
    dungeon_stats[4] = 0
    
    # 5: 体力 - 基于角色体力上限的50%
    max_stamina = int(this.kojo.MAXBASE[char_id].get('体力', base_stamina))
    dungeon_stats[5] = max_stamina // 2
    
    # 6: 护盾 - 初始为0
    dungeon_stats[6] = 0
    
    # 7: 行动力 - 基于敏捷
    # 敏捷每20点增加1点行动力，最少1点，最多3点
    dungeon_stats[7] = min(3, max(1, base_agility // 20 + 1))
    
    # 技能资源属性 - 基于角色类型
    # 10: 灵力 - 巫女类角色
    if '巫女' in role or '霊夢' in this.kojo.CALLNAME:
        dungeon_stats[10] = 50
    else:
        dungeon_stats[10] = 0
    
    # 11: 魔力 - 魔法使类角色
    if '魔法使' in role or '魔' in role or '魔理沙' in this.kojo.CALLNAME:
        dungeon_stats[11] = 50
    else:
        dungeon_stats[11] = 0
    
    # 12: 妖力 - 妖怪&妖精类角色
    if '妖怪' in role or '妖精' in role:
        dungeon_stats[12] = 50
    else:
        dungeon_stats[12] = 0
    
    # 13: 精力 - 所有角色都有
    dungeon_stats[13] = 50
    
    return dungeon_stats


def event_dungeon_get_stat(this, stat_id: int, char_id: str = None) -> int:
    """
    获取角色地牢属性值
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        属性值，如果属性不存在返回0
    """
    if char_id is None:
        char_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 确保地牢属性已初始化
    if 'dungeon_stats' not in this.console.allstate:
        event_dungeon_initialize_stats(this, char_id)
    
    if char_id not in this.console.allstate.get('dungeon_stats', {}):
        event_dungeon_initialize_stats(this, char_id)
    
    return this.console.allstate['dungeon_stats'][char_id].get(stat_id, 0)


def event_dungeon_set_stat(this, stat_id: int, value: int, char_id: str = None) -> int:
    """
    设置角色地牢属性值
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        value: 要设置的值
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        设置后的属性值
    """
    if char_id is None:
        char_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 确保地牢属性已初始化
    if 'dungeon_stats' not in this.console.allstate:
        event_dungeon_initialize_stats(this, char_id)
    
    if char_id not in this.console.allstate.get('dungeon_stats', {}):
        event_dungeon_initialize_stats(this, char_id)
    
    # 应用同行属性效果
    from events.地牢相关.同行属性判定 import event_apply_companion_effects
    final_value = event_apply_companion_effects(this, char_id, stat_id, value)
    
    # 设置属性值
    this.console.allstate['dungeon_stats'][char_id][stat_id] = final_value
    
    return final_value


def event_dungeon_modify_stat(this, stat_id: int, delta: int, char_id: str = None) -> int:
    """
    修改角色地牢属性值（增加或减少）
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        delta: 变化量（正数增加，负数减少）
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        修改后的属性值
    """
    current_value = event_dungeon_get_stat(this, stat_id, char_id)
    new_value = current_value + delta
    
    # 某些属性不能为负
    non_negative_stats = [5, 6, 7, 10, 11, 12, 13]  # 体力、护盾、行动力、各种资源
    if stat_id in non_negative_stats:
        new_value = max(0, new_value)
    
    # 情欲值不能超过1000
    if stat_id == 4:
        new_value = min(1000, new_value)
    
    # 应用同行属性效果
    from events.地牢相关.同行属性判定 import event_apply_companion_effects
    final_value = event_apply_companion_effects(this, char_id, stat_id, new_value)
    
    # 设置属性值
    return event_dungeon_set_stat(this, stat_id, final_value, char_id)


def event_dungeon_get_all_stats(this, char_id: str = None) -> Dict[int, int]:
    """
    获取角色所有地牢属性
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        所有地牢属性字典
    """
    if char_id is None:
        char_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 确保地牢属性已初始化
    if 'dungeon_stats' not in this.console.allstate:
        event_dungeon_initialize_stats(this, char_id)
    
    if char_id not in this.console.allstate.get('dungeon_stats', {}):
        event_dungeon_initialize_stats(this, char_id)
    
    return this.console.allstate['dungeon_stats'][char_id].copy()


def event_dungeon_reset_stats(this, char_id: str = None) -> None:
    """
    重置角色地牢属性（退出地牢时调用）
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    """
    if char_id is None:
        char_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 清除地牢属性
    if 'dungeon_stats' in this.console.allstate:
        if char_id in this.console.allstate['dungeon_stats']:
            del this.console.allstate['dungeon_stats'][char_id]
    
    # 清除异常状态
    if 'dungeon_abnormal_states' in this.console.allstate:
        if char_id in this.console.allstate['dungeon_abnormal_states']:
            del this.console.allstate['dungeon_abnormal_states'][char_id]


def event_dungeon_check_stat(this, stat_id: int, threshold: int, char_id: str = None) -> bool:
    """
    检查角色地牢属性是否满足条件
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        threshold: 阈值
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        如果属性值 >= 阈值返回True，否则返回False
    """
    value = event_dungeon_get_stat(this, stat_id, char_id)
    return value >= threshold


def event_dungeon_consume_stat(this, stat_id: int, amount: int, char_id: str = None) -> bool:
    """
    消耗角色地牢属性（用于技能释放等）
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        amount: 要消耗的数量
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        如果消耗成功返回True，属性不足返回False
    """
    current_value = event_dungeon_get_stat(this, stat_id, char_id)
    
    if current_value >= amount:
        event_dungeon_modify_stat(this, stat_id, -amount, char_id)
        return True
    else:
        return False


def event_dungeon_restore_stat(this, stat_id: int, amount: int, char_id: str = None) -> int:
    """
    恢复角色地牢属性
    
    参数:
        this: 事件上下文对象
        stat_id: 地牢属性ID
        amount: 要恢复的数量
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        恢复后的属性值
    """
    return event_dungeon_modify_stat(this, stat_id, amount, char_id)


def event_dungeon_get_stat_name(stat_id: int) -> str:
    """
    获取地牢属性名称
    
    参数:
        stat_id: 地牢属性ID
    
    返回:
        属性名称字符串
    """
    stat_names = {
        0: "攻击",
        1: "防御",
        4: "情欲值",
        5: "体力",
        6: "护盾",
        7: "行动力",
        10: "灵力",
        11: "魔力",
        12: "妖力",
        13: "精力",
        20: "无意识",
        21: "灵力充沛",
        22: "心路爆破"
    }
    return stat_names.get(stat_id, f"未知属性({stat_id})")


def event_dungeon_format_stats(this, char_id: str = None) -> str:
    """
    格式化角色地牢属性为可读字符串
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前选择的目标角色
    
    返回:
        格式化的属性字符串
    """
    stats = event_dungeon_get_all_stats(this, char_id)
    
    lines = ["【地牢属性】"]
    
    # 基础战斗属性
    lines.append(f"攻击: {stats.get(0, 0)}")
    lines.append(f"防御: {stats.get(1, 0)}")
    lines.append(f"情欲值: {stats.get(4, 0)}/1000")
    lines.append(f"体力: {stats.get(5, 0)}")
    lines.append(f"护盾: {stats.get(6, 0)}")
    lines.append(f"行动力: {stats.get(7, 0)}")
    
    # 技能资源
    if stats.get(10, 0) > 0:
        lines.append(f"灵力: {stats.get(10, 0)}")
    if stats.get(11, 0) > 0:
        lines.append(f"魔力: {stats.get(11, 0)}")
    if stats.get(12, 0) > 0:
        lines.append(f"妖力: {stats.get(12, 0)}")
    if stats.get(13, 0) > 0:
        lines.append(f"精力: {stats.get(13, 0)}")
    
    return "\n".join(lines)
