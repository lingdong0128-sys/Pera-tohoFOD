"""
天气系统事件
实现天气对游戏的影响机制

根据设计思路：
- 天气影响角色花销（体力、精力、灵力消耗）
- 天气每日更新，根据季节调整概率
- 特定天气下可能有特殊事件或效果
"""

import random
from typing import Dict, Any, Optional, List


# 天气定义
WEATHER_TYPES = {
    '晴': {
        'name': '晴',
        'description': '天气晴朗，适合户外活动',
        'stamina_modifier': 1.0,    # 体力消耗修正
        'energy_modifier': 1.0,     # 精力消耗修正
        'spirit_modifier': 1.0,     # 灵力消耗修正
        'special_effects': []       # 特殊效果
    },
    '阴': {
        'name': '阴',
        'description': '阴天，心情略显低落',
        'stamina_modifier': 1.1,
        'energy_modifier': 0.9,
        'spirit_modifier': 1.0,
        'special_effects': ['精力消耗略微降低', '体力消耗略微增加']
    },
    '雨': {
        'name': '雨',
        'description': '雨天，出行不便',
        'stamina_modifier': 1.3,
        'energy_modifier': 0.8,
        'spirit_modifier': 0.9,
        'special_effects': ['精力消耗降低', '体力消耗增加', '灵力消耗降低']
    },
    '雪': {
        'name': '雪',
        'description': '下雪，寒冷的冬日',
        'stamina_modifier': 1.5,
        'energy_modifier': 0.7,
        'spirit_modifier': 1.2,
        'special_effects': ['体力消耗大幅增加', '精力消耗大幅降低', '灵力消耗增加']
    }
}


# 季节定义
SEASONS = {
    1: {'name': '春季', 'weather_weights': [50, 30, 20, 0]},     # 3-5月
    2: {'name': '夏季', 'weather_weights': [60, 20, 20, 0]},     # 6-8月
    3: {'name': '秋季', 'weather_weights': [50, 30, 20, 0]},     # 9-11月
    4: {'name': '冬季', 'weather_weights': [30, 30, 20, 20]}    # 12-2月
}


def event_weather_system(this, **kwargs):
    """
    [事件] 天气系统
    
    Trigger ID: weather_system
    
    支持的操作:
        - 'get': 获取当前天气
        - 'update': 更新天气
        - 'get_modifiers': 获取天气修正系数
        - 'get_all_weathers': 获取所有天气定义
        - 'set': 强制设置天气（调试用）
    
    Args:
        this: 事件上下文对象
        **kwargs: 操作参数
    
    Returns:
        操作结果
    """
    operation = kwargs.get('operation', 'get')
    
    if operation == 'get':
        # 获取当前天气
        return _get_current_weather(this)
    
    elif operation == 'update':
        # 更新天气
        return _update_weather(this)
    
    elif operation == 'get_modifiers':
        # 获取天气修正系数
        weather = kwargs.get('weather')
        if not weather:
            weather_info = _get_current_weather(this)
            weather = weather_info.get('weather', '晴')
        return _get_weather_modifiers(weather)
    
    elif operation == 'get_all_weathers':
        # 获取所有天气定义
        return _get_all_weathers()
    
    elif operation == 'set':
        # 强制设置天气（调试用）
        weather = kwargs.get('weather', '晴')
        return _set_weather(this, weather)
    
    else:
        return {'success': False, 'message': f'未知操作: {operation}'}


def _get_current_weather(this) -> Dict[str, Any]:
    """
    获取当前天气
    
    Args:
        this: 事件上下文对象
    
    Returns:
        当前天气信息
    """
    console = this.console
    init = console.init
    
    # 从全局System中获取天气
    system_key = init.global_key.get('System', {})
    weather = system_key.get('WEATHER', '晴')
    
    # 获取天气详细信息
    weather_info = WEATHER_TYPES.get(weather, WEATHER_TYPES['晴'])
    
    return {
        'weather': weather,
        'name': weather_info['name'],
        'description': weather_info['description'],
        'stamina_modifier': weather_info['stamina_modifier'],
        'energy_modifier': weather_info['energy_modifier'],
        'spirit_modifier': weather_info['spirit_modifier'],
        'special_effects': weather_info['special_effects']
    }


def _update_weather(this) -> Dict[str, Any]:
    """
    更新天气
    
    根据当前季节调整天气概率，随机生成新天气
    
    Args:
        this: 事件上下文对象
    
    Returns:
        更新结果
    """
    console = this.console
    init = console.init
    
    # 获取当前季节
    season = _get_current_season(this)
    season_info = SEASONS.get(season, SEASONS[1])
    
    # 根据季节权重随机生成天气
    weather_list = list(WEATHER_TYPES.keys())
    weights = season_info['weather_weights']
    
    new_weather = random.choices(weather_list, weights=weights, k=1)[0]
    
    # 更新全局天气
    system_key = init.global_key.get('System', {})
    old_weather = system_key.get('WEATHER', '晴')
    system_key['WEATHER'] = new_weather
    
    # 获取新天气信息
    weather_info = WEATHER_TYPES.get(new_weather, WEATHER_TYPES['晴'])
    
    return {
        'success': True,
        'old_weather': old_weather,
        'new_weather': new_weather,
        'weather_name': weather_info['name'],
        'description': weather_info['description'],
        'season': season_info['name']
    }


def _get_weather_modifiers(weather: str) -> Dict[str, float]:
    """
    获取指定天气的修正系数
    
    Args:
        weather: 天气类型
    
    Returns:
        修正系数字典
    """
    weather_info = WEATHER_TYPES.get(weather, WEATHER_TYPES['晴'])
    
    return {
        'stamina_modifier': weather_info['stamina_modifier'],
        'energy_modifier': weather_info['energy_modifier'],
        'spirit_modifier': weather_info['spirit_modifier']
    }


def _get_all_weathers() -> Dict[str, Dict[str, Any]]:
    """
    获取所有天气定义
    
    Returns:
        天气定义字典
    """
    return WEATHER_TYPES


def _set_weather(this, weather: str) -> Dict[str, Any]:
    """
    强制设置天气（调试用）
    
    Args:
        this: 事件上下文对象
        weather: 天气类型
    
    Returns:
        设置结果
    """
    console = this.console
    init = console.init
    
    if weather not in WEATHER_TYPES:
        return {
            'success': False,
            'message': f'未知天气类型: {weather}'
        }
    
    # 设置全局天气
    system_key = init.global_key.get('System', {})
    system_key['WEATHER'] = weather
    
    weather_info = WEATHER_TYPES.get(weather)
    
    return {
        'success': True,
        'weather': weather,
        'weather_name': weather_info['name'],
        'description': weather_info['description']
    }


def _get_current_season(this) -> int:
    """
    获取当前季节
    
    根据月份判断季节：
    - 春季: 3-5月
    - 夏季: 6-8月
    - 秋季: 9-11月
    - 冬季: 12-2月
    
    Args:
        this: 事件上下文对象
    
    Returns:
        季节编号 (1-4)
    """
    # 尝试从time_control事件获取月份
    try:
        time_info = this.console.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        
        if isinstance(time_info, dict):
            month = time_info.get('MONTH', 1)
            
            # 判断季节
            if month in [3, 4, 5]:
                return 1  # 春季
            elif month in [6, 7, 8]:
                return 2  # 夏季
            elif month in [9, 10, 11]:
                return 3  # 秋季
            else:  # 12, 1, 2
                return 4  # 冬季
    
    except Exception:
        pass
    
    # 默认返回春季
    return 1


def calculate_weather_effect(this, chara_id: str, action_id: str, 
                             base_stamina_cost: int, base_energy_cost: int, 
                             base_spirit_cost: int) -> Dict[str, Any]:
    """
    计算天气对行为花销的影响
    
    Args:
        this: 事件上下文对象
        chara_id: 角色ID
        action_id: 行为ID
        base_stamina_cost: 基础体力消耗
        base_energy_cost: 基础精力消耗
        base_spirit_cost: 基础灵力消耗
    
    Returns:
        修正后的花销
    """
    # 获取当前天气
    weather_info = _get_current_weather(this)
    modifiers = _get_weather_modifiers(weather_info['weather'])
    
    # 应用天气修正
    modified_stamina = int(base_stamina_cost * modifiers['stamina_modifier'])
    modified_energy = int(base_energy_cost * modifiers['energy_modifier'])
    modified_spirit = int(base_spirit_cost * modifiers['spirit_modifier'])
    
    return {
        'weather': weather_info['weather'],
        'weather_name': weather_info['name'],
        'stamina_cost': modified_stamina,
        'energy_cost': modified_energy,
        'spirit_cost': modified_spirit,
        'stamina_modifier': modifiers['stamina_modifier'],
        'energy_modifier': modifiers['energy_modifier'],
        'spirit_modifier': modifiers['spirit_modifier'],
        'special_effects': weather_info['special_effects']
    }


# 注册事件触发器
event_weather_system.event_trigger = "weather_system"
