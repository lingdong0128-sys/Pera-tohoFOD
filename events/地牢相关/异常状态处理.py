"""
异常状态处理系统
管理战斗中的异常状态，包括添加、移除、效果应用等功能

功能：
- 添加异常状态
- 移除异常状态
- 立即应用异常状态效果
- 回合结束应用异常状态效果
- 查询异常状态
"""

from typing import Dict, List, Any, Tuple
import os


def event_abnormal_init(this, char_id: str = None) -> None:
    """
    初始化角色异常状态列表
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    # 使用全局状态存储异常状态
    if 'dungeon_abnormal_states' not in this.console.allstate:
        this.console.allstate['dungeon_abnormal_states'] = {}
    
    if char_id not in this.console.allstate['dungeon_abnormal_states']:
        this.console.allstate['dungeon_abnormal_states'][char_id] = []


def event_abnormal_add(this, state_id: int, char_id: str = None) -> bool:
    """
    添加异常状态到角色
    
    参数:
        this: 事件上下文对象
        state_id: 异常状态ID
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        添加成功返回True，已存在该状态返回False
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    event_abnormal_init(this, char_id)
    
    abnormal_states = this.console.allstate['dungeon_abnormal_states'][char_id]
    
    # 检查是否已存在该状态
    for state in abnormal_states:
        if state['id'] == state_id:
            return False
    
    # 添加新状态
    abnormal_states.append({
        'id': state_id,
        'turns': 0  # 持续回合数
    })
    
    return True


def event_abnormal_remove(this, state_id: int, char_id: str = None) -> bool:
    """
    从角色移除异常状态
    
    参数:
        this: 事件上下文对象
        state_id: 异常状态ID
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        移除成功返回True，不存在该状态返回False
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    if 'dungeon_abnormal_states' not in this.console.allstate:
        return False
    
    abnormal_states = this.console.allstate.get('dungeon_abnormal_states', {}).get(char_id, [])
    
    # 查找并移除状态
    for i, state in enumerate(abnormal_states):
        if state['id'] == state_id:
            abnormal_states.pop(i)
            return True
    
    return False


def event_abnormal_has(this, state_id: int, char_id: str = None) -> bool:
    """
    检查角色是否拥有指定异常状态
    
    参数:
        this: 事件上下文对象
        state_id: 异常状态ID
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        如果拥有该状态返回True，否则返回False
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    if 'dungeon_abnormal_states' not in this.console.allstate:
        return False
    
    abnormal_states = this.console.allstate.get('dungeon_abnormal_states', {}).get(char_id, [])
    
    for state in abnormal_states:
        if state['id'] == state_id:
            return True
    
    return False


def event_abnormal_get_all(this, char_id: str = None) -> List[Dict]:
    """
    获取角色所有异常状态
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        异常状态列表
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    if 'dungeon_abnormal_states' not in this.console.allstate:
        return []
    
    return this.console.allstate.get('dungeon_abnormal_states', {}).get(char_id, []).copy()


def event_abnormal_clear(this, char_id: str = None) -> None:
    """
    清除角色所有异常状态
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    if 'dungeon_abnormal_states' in this.console.allstate:
        if char_id in this.console.allstate['dungeon_abnormal_states']:
            this.console.allstate['dungeon_abnormal_states'][char_id].clear()


def _parse_effect(effect_str: str) -> Tuple[str, int, str, Any]:
    """
    解析效果字符串
    
    效果格式: [目标:属性ID:操作符|值]
    
    参数:
        effect_str: 效果字符串
    
    返回:
        (目标类型, 属性ID, 操作符, 值)
    """
    # 移除方括号
    effect_str = effect_str.strip('[]')
    
    # 按冒号分割
    parts = effect_str.split(':')
    
    if len(parts) < 3:
        return None, None, None, None
    
    target = parts[0]
    attr_id = int(parts[1])
    operator_part = parts[2]
    
    # 解析操作符和值
    # 格式可能是: -1, +10, end=+10
    if 'end=' in operator_part:
        timing = 'end'
        value_part = operator_part.split('=')[1]
    else:
        timing = 'immediate'
        value_part = operator_part
    
    # 解析操作符
    if value_part.startswith('+'):
        operator = '+'
        value = int(value_part[1:])
    elif value_part.startswith('-'):
        operator = '-'
        value = int(value_part[1:])
    elif value_part.startswith('*'):
        operator = '*'
        value = int(value_part[1:])
    elif value_part.startswith('/'):
        operator = '/'
        value = int(value_part[1:])
    elif value_part.startswith('%'):
        operator = '%'
        value = int(value_part[1:])
    elif value_part.startswith('='):
        operator = '='
        value = int(value_part[1:])
    else:
        operator = '+'
        value = int(value_part)
    
    return target, attr_id, timing, (operator, value)


def event_abnormal_apply_effect(this, effect_str: str, char_id: str = None) -> None:
    """
    应用单个异常状态效果
    
    参数:
        this: 事件上下文对象
        effect_str: 效果字符串
        char_id: 角色ID，如果为None则使用当前目标角色
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    from events.地牢相关.地牢数值化 import event_dungeon_modify_stat, event_dungeon_get_stat, event_dungeon_set_stat
    
    target, attr_id, timing, (operator, value) = _parse_effect(effect_str)
    
    if target is None:
        return
    
    # 根据目标类型应用效果
    if target == '角色地牢属性':
        if operator == '+':
            event_dungeon_modify_stat(this, attr_id, value, char_id)
        elif operator == '-':
            event_dungeon_modify_stat(this, attr_id, -value, char_id)
        elif operator == '*':
            current_value = event_dungeon_get_stat(this, attr_id, char_id)
            event_dungeon_set_stat(this, attr_id, current_value * value, char_id)
        elif operator == '/':
            current_value = event_dungeon_get_stat(this, attr_id, char_id)
            if value != 0:
                event_dungeon_set_stat(this, attr_id, current_value // value, char_id)
        elif operator == '%':
            current_value = event_dungeon_get_stat(this, attr_id, char_id)
            event_dungeon_set_stat(this, attr_id, current_value * value // 100, char_id)
        elif operator == '=':
            event_dungeon_set_stat(this, attr_id, value, char_id)
    
    elif target == '异常状态':
        # 添加或移除异常状态
        if operator == '+':
            event_abnormal_add(this, attr_id, char_id)
        elif operator == '-':
            event_abnormal_remove(this, attr_id, char_id)


def event_abnormal_get_state_info(state_id: int) -> Dict:
    """
    获取异常状态信息（从CSV读取）
    
    参数:
        state_id: 异常状态ID
    
    返回:
        异常状态信息字典
    """
    # 读取异常状态CSV
    csv_path = os.path.join('csv', 'global', '异常状态.csv')
    
    if not os.path.exists(csv_path):
        return {'id': state_id, 'name': f'未知状态{state_id}', 'effects': []}
    
    state_info = {'id': state_id, 'name': f'未知状态{state_id}', 'effects': []}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            parts = line.split(',')
            if len(parts) >= 2:
                csv_id = int(parts[0].strip())
                if csv_id == state_id:
                    state_info['name'] = parts[1].strip()
                    # 解析效果列表
                    effects = []
                    for part in parts[2:]:
                        if part.strip():
                            effects.append(part.strip())
                    state_info['effects'] = effects
                    break
    
    return state_info


def event_abnormal_apply_immediate_effects(this, state_id: int, char_id: str = None) -> None:
    """
    应用异常状态的立即效果
    
    参数:
        this: 事件上下文对象
        state_id: 异常状态ID
        char_id: 角色ID，如果为None则使用当前目标角色
    """
    state_info = event_abnormal_get_state_info(state_id)
    
    for effect_str in state_info['effects']:
        target, attr_id, timing, (operator, value) = _parse_effect(effect_str)
        
        # 只应用立即效果
        if timing == 'immediate':
            event_abnormal_apply_effect(this, effect_str, char_id)


def event_abnormal_apply_end_effects(this, char_id: str = None) -> None:
    """
    应用所有异常状态的回合结束效果
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    """
    if char_id is None:
        char_id = this.kojo.TARGET
    
    if 'dungeon_abnormal_states' not in this.console.allstate:
        return
    
    abnormal_states = this.console.allstate.get('dungeon_abnormal_states', {}).get(char_id, []).copy()
    
    for state in abnormal_states:
        state_info = event_abnormal_get_state_info(state['id'])
        
        for effect_str in state_info['effects']:
            target, attr_id, timing, (operator, value) = _parse_effect(effect_str)
            
            # 只应用回合结束效果
            if timing == 'end':
                event_abnormal_apply_effect(this, effect_str, char_id)


def event_abnormal_format(this, char_id: str = None) -> str:
    """
    格式化角色异常状态为可读字符串
    
    参数:
        this: 事件上下文对象
        char_id: 角色ID，如果为None则使用当前目标角色
    
    返回:
        格式化的异常状态字符串
    """
    abnormal_states = event_abnormal_get_all(this, char_id)
    
    if not abnormal_states:
        return "无异常状态"
    
    lines = ["【异常状态】"]
    
    for state in abnormal_states:
        state_info = event_abnormal_get_state_info(state['id'])
        lines.append(f"- {state_info['name']}")
    
    return "\n".join(lines)


def event_abnormal_get_state_name(state_id: int) -> str:
    """
    获取异常状态名称
    
    参数:
        state_id: 异常状态ID
    
    返回:
        异常状态名称
    """
    state_info = event_abnormal_get_state_info(state_id)
    return state_info['name']
