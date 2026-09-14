"""
同行属性判定系统
处理角色同行时提供的特殊属性加成

功能：
- 检查同行角色提供的属性
- 应用同行属性效果
"""

from typing import Dict, List, Tuple
from ERAconsole import EraKojoHandler


def event_check_companion_attributes(this, char_id: str = None) -> List[int]:
    """
    检查并返回当前同行的角色提供的属性加成
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        属性ID列表
    """
    # 创建EraKojoHandler实例以访问角色信息
    kojo = EraKojoHandler(this.console)
    
    if char_id is None:
        char_id = this.console.allstate.get('System', {}).get('选择对象', '0')
    
    companion_attributes = []
    
    # 检查ASSI（助手列表）中的角色
    # ASSI是EraKojoHandler提供的属性，返回助手ID列表
    if not hasattr(kojo, 'ASSI') or not kojo.ASSI:
        return companion_attributes
    
    for companion_id in kojo.ASSI:
        if companion_id == char_id:
            continue  # 跳过自己
        
        # 获取同伴角色的信息
        # 这里简化处理，实际应该从角色的口上或特殊标记读取同行属性
        companion_name = kojo.NAME if kojo.TARGET == companion_id else \
                       kojo.BASE.get(companion_id, {}).get('名前', '')
        
        # 根据角色名称判定同行属性
        if '恋' in companion_name or '古明地恋' in companion_name:
            # 古明地恋：无意识 - 无视3怪之内的被动战斗触发
            companion_attributes.append(20)
        
        elif '霊夢' in companion_name or '灵梦' in companion_name:
            # 灵梦：灵力充沛 - 灵力技能释放消耗-20%
            companion_attributes.append(21)
        
        elif '覚' in companion_name or '古明地觉' in companion_name:
            # 古明地觉：心路爆破 - 暴击率增加10%
            companion_attributes.append(22)
    
    return companion_attributes


def event_apply_companion_effects(this, char_id: str, stat_id: int, value: int) -> int:
    """
    应用同行属性效果到属性值
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID
        stat_id: 属性ID
        value: 原始属性值
    
    返回:
        应用加成后的属性值
    """
    companion_attributes = event_check_companion_attributes(this, char_id)
    
    final_value = value
    
    # 应用同行属性效果
    if 21 in companion_attributes:  # 灵力充沛 - 灵力技能消耗-20%
        if stat_id == 10:  # 灵力
            final_value = int(value * 0.8)
    
    if 22 in companion_attributes:  # 心路爆破 - 暴击率增加10%
        if stat_id == 0:  # 攻击 - 暴击加成在战斗中处理
            # 这里存储暴击率加成标记
            if 'dungeon_crit_bonus' not in this.console.allstate:
                this.console.allstate['dungeon_crit_bonus'] = {}
            this.console.allstate['dungeon_crit_bonus'][char_id] = 10
    
    # 无意识属性在被动遇敌判定时使用，不直接修改属性值
    
    return final_value


def event_has_companion_attribute(this, attribute_id: int, char_id: str = None) -> bool:
    """
    检查角色是否拥有指定的同行属性
    
    参数:
        this: 事件上下文对象
        attribute_id: 属性ID
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        如果拥有该属性返回True，否则返回False
    """
    # 创建EraKojoHandler实例以访问角色信息
    kojo = EraKojoHandler(this.console)
    
    if char_id is None:
        char_id = this.console.allstate.get('System', {}).get('选择对象', '0')
    
    companion_attributes = event_check_companion_attributes(this, char_id)
    return attribute_id in companion_attributes


def event_get_crit_bonus(this, char_id: str = None) -> int:
    """
    获取角色的暴击率加成（来自同行属性）
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        暴击率加成（百分比）
    """
    # 创建EraKojoHandler实例以访问角色信息
    kojo = EraKojoHandler(this.console)
    
    if char_id is None:
        char_id = this.console.allstate.get('System', {}).get('选择对象', '0')
    
    # 检查是否有心路爆破属性
    if event_has_companion_attribute(this, 22, char_id):
        return 10
    
    return 0


def event_can_ignore_passive_battle(this, char_id: str = None) -> bool:
    """
    检查是否可以无视被动战斗触发（无意识属性）
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        如果可以无视返回True，否则返回False
    """
    # 创建EraKojoHandler实例以访问角色信息
    kojo = EraKojoHandler(this.console)
    
    if char_id is None:
        char_id = this.console.allstate.get('System', {}).get('选择对象', '0')
    
    # 检查是否有无意识属性
    if event_has_companion_attribute(this, 20, char_id):
        # 还需要检查怪物距离（这个在战斗触发时判断）
        return True
    
    return False
