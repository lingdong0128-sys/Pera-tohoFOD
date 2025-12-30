"""
花销计算器模块
实现Pera幻想FOD中的角色花销计算系统

根据设计思路：
- 根据角色基础值计算每天花销
- 每个操作的花销需要存储在新的全局变量下
- 花销会根据状态、天气、相性等因素动态变化
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class ActionCost:
    """行为花销数据类"""
    action_id: str          # 行为ID
    action_name: str        # 行为名称
    base_cost: float        # 基础花销（分钟）
    stamina_cost: int       # 体力消耗
    energy_cost: int        # 精力消耗
    spirit_cost: int        # 灵力消耗
    体力消耗: int           # 体力消耗（兼容中文）
    精力消耗: int           # 精力消耗（兼容中文）
    灵力消耗: int           # 灵力消耗（兼容中文）
    required_stats: Dict[str, int]  # 需要的属性值
    effects: List[str]      # 行为效果列表


class CostCalculator:
    """花销计算器类 - 负责计算角色的各种花销"""
    
    def __init__(self, console):
        """
        初始化花销计算器
        
        Args:
            console: 控制台对象，用于访问全局变量和角色数据
        """
        self.console = console
        self.init = console.init
        
        # 行为花销数据库（从全局变量加载）
        self.action_costs = {}
        
        # 天气加成系数
        self.weather_modifiers = {
            '晴': {'体力': 1.0, '精力': 1.0, '灵力': 1.0},
            '阴': {'体力': 1.1, '精力': 0.9, '灵力': 1.0},
            '雨': {'体力': 1.3, '精力': 0.8, '灵力': 0.9},
            '雪': {'体力': 1.5, '精力': 0.7, '灵力': 1.2},
        }
        
        # 状态加成系数
        self.status_modifiers = {
            '健康': {'体力': 1.0, '精力': 1.0, '灵力': 1.0},
            '轻伤': {'体力': 1.5, '精力': 1.2, '灵力': 0.8},
            '重伤': {'体力': 2.0, '精力': 1.5, '灵力': 0.6},
            '疲劳': {'体力': 1.3, '精力': 1.8, '灵力': 0.7},
            '极度疲劳': {'体力': 2.0, '精力': 2.5, '灵力': 0.5},
            '要睡觉': {'体力': 2.0, '精力': 2.0, '灵力': 1.0},  # 所有花销*2
        }
        
        # 加载行为花销数据
        self.load_action_costs()
    
    def load_action_costs(self):
        """从全局变量加载行为花销数据"""
        # 从全局变量中获取花销定义
        action_data = self.init.global_key.get('ActionCost', {})
        
        # 如果没有数据，使用默认配置
        if not action_data:
            self._load_default_actions()
            return
        
        # 解析行为花销数据
        for action_id, cost_info in action_data.items():
            if isinstance(cost_info, dict):
                self.action_costs[action_id] = ActionCost(
                    action_id=action_id,
                    action_name=cost_info.get('name', '未知行为'),
                    base_cost=float(cost_info.get('time_cost', 5)),  # 默认5分钟
                    stamina_cost=int(cost_info.get('体力消耗', 0)),
                    energy_cost=int(cost_info.get('精力消耗', 0)),
                    spirit_cost=int(cost_info.get('灵力消耗', 0)),
                    体力消耗=int(cost_info.get('体力消耗', 0)),
                    精力消耗=int(cost_info.get('精力消耗', 0)),
                    灵力消耗=int(cost_info.get('灵力消耗', 0)),
                    required_stats=cost_info.get('required_stats', {}),
                    effects=cost_info.get('effects', [])
                )
    
    def _load_default_actions(self):
        """加载默认的行为花销配置"""
        default_actions = {
            'rest': {
                'name': '休息',
                'time_cost': 30,
                '体力消耗': -50,
                '精力消耗': -30,
                '灵力消耗': 0,
                'required_stats': {},
                'effects': ['恢复体力', '恢复精力']
            },
            'explore': {
                'name': '探索',
                'time_cost': 15,
                '体力消耗': 20,
                '精力消耗': 10,
                '灵力消耗': 5,
                'required_stats': {},
                'effects': ['获得经验', '可能发现物品']
            },
            'combat': {
                'name': '战斗',
                'time_cost': 10,
                '体力消耗': 40,
                '精力消耗': 30,
                '灵力消耗': 20,
                'required_stats': {},
                'effects': ['获得经验', '可能受伤']
            },
            'social': {
                'name': '社交',
                'time_cost': 20,
                '体力消耗': 5,
                '精力消耗': 10,
                '灵力消耗': 5,
                'required_stats': {},
                'effects': ['提升好感', '提升信赖']
            },
            'dungeon_explore': {
                'name': '地牢探索',
                'time_cost': 20,
                '体力消耗': 30,
                '精力消耗': 25,
                '灵力消耗': 15,
                'required_stats': {},
                'effects': ['可能获得战利品', '可能遭遇怪物']
            },
            'dungeon_combat': {
                'name': '地牢战斗',
                'time_cost': 15,
                '体力消耗': 50,
                '精力消耗': 40,
                '灵力消耗': 30,
                'required_stats': {},
                'effects': ['获得战利品', '可能受伤']
            },
            'move_small_map': {
                'name': '小地图移动',
                'time_cost': 2,
                '体力消耗': 2,
                '精力消耗': 1,
                '灵力消耗': 0,
                'required_stats': {},
                'effects': ['移动到邻近地点']
            },
            'move_big_map': {
                'name': '大地图移动',
                'time_cost': 10,
                '体力消耗': 10,
                '精力消耗': 5,
                '灵力消耗': 0,
                'required_stats': {},
                'effects': ['移动到大地图']
            },
            'shop': {
                'name': '商店交易',
                'time_cost': 15,
                '体力消耗': 2,
                '精力消耗': 5,
                '灵力消耗': 0,
                'required_stats': {},
                'effects': ['购买物品', '出售物品']
            },
            'sleep': {
                'name': '睡觉',
                'time_cost': 480,  # 8小时
                '体力消耗': -1000,
                '精力消耗': -1000,
                '灵力消耗': -500,
                'required_stats': {},
                'effects': ['恢复所有状态', '进入次日']
            },
        }
        
        # 转换为ActionCost对象
        for action_id, cost_info in default_actions.items():
            self.action_costs[action_id] = ActionCost(
                action_id=action_id,
                action_name=cost_info['name'],
                base_cost=float(cost_info['time_cost']),
                stamina_cost=int(cost_info['体力消耗']),
                energy_cost=int(cost_info['精力消耗']),
                spirit_cost=int(cost_info['灵力消耗']),
                体力消耗=int(cost_info['体力消耗']),
                精力消耗=int(cost_info['精力消耗']),
                灵力消耗=int(cost_info['灵力消耗']),
                required_stats=cost_info['required_stats'],
                effects=cost_info['effects']
            )
    
    def calculate_action_cost(self, chara_id: str, action_id: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        计算特定角色执行特定行为的花销
        
        Args:
            chara_id: 角色ID
            action_id: 行为ID
            context: 上下文信息（天气、时间等）
        
        Returns:
            包含时间、体力、精力、灵力消耗的字典
        """
        # 获取角色数据
        chara_state = self.console.allstate.get(chara_id)
        if not chara_state:
            return {
                'error': f'角色{chara_id}不存在',
                'time_cost': 0,
                'stamina_cost': 0,
                'energy_cost': 0,
                'spirit_cost': 0
            }
        
        # 获取行为花销定义
        action_cost = self.action_costs.get(action_id)
        if not action_cost:
            return {
                'error': f'行为{action_id}未定义',
                'time_cost': 0,
                'stamina_cost': 0,
                'energy_cost': 0,
                'spirit_cost': 0
            }
        
        # 获取角色属性
        attributes = chara_state.get('attributes', {})
        stamina = attributes.get('体力', 0)
        stamina_max = attributes.get('体力上限', 100)
        energy = attributes.get('精力', 0)
        energy_max = attributes.get('精力上限', 100)
        spirit = attributes.get('灵力', 0)
        spirit_max = attributes.get('灵力上限', 100)
        
        # 获取角色状态
        cflags = chara_state.get('cflags', {})
        abnormal_states = chara_state.get('abnormal_states', {})
        
        # 初始花销
        final_time_cost = action_cost.base_cost
        final_stamina_cost = action_cost.stamina_cost
        final_energy_cost = action_cost.energy_cost
        final_spirit_cost = action_cost.spirit_cost
        
        # 应用状态修正
        final_stamina_cost, final_energy_cost, final_spirit_cost = \
            self._apply_status_modifiers(
                final_stamina_cost, final_energy_cost, final_spirit_cost,
                chara_state, cflags, abnormal_states
            )
        
        # 应用天气修正（从天气系统事件获取）
        try:
            weather_info = self.console.event_manager.trigger_event(
                'weather_system',
                type('this', (object,), {'console': self.console, 'event_manager': self.console.event_manager})(),
                'get'
            )
            if weather_info:
                final_stamina_cost, final_energy_cost, final_spirit_cost = \
                    self._apply_weather_modifiers(
                        final_stamina_cost, final_energy_cost, final_spirit_cost,
                        weather_info.get('weather', '晴')
                    )
        except Exception:
            # 如果天气系统不可用，默认使用晴天修正
            pass
        
        # 应用角色能力修正（根据角色能力等级调整花销）
        final_time_cost, final_stamina_cost, final_energy_cost, final_spirit_cost = \
            self._apply_character_modifiers(
                final_time_cost, final_stamina_cost, final_energy_cost, final_spirit_cost,
                attributes, chara_state
            )
        
        # 确保花销不会超过当前值（对于恢复类行为则相反）
        # 计算实际消耗/恢复量
        actual_stamina_cost = self._clamp_cost(final_stamina_cost, stamina, stamina_max)
        actual_energy_cost = self._clamp_cost(final_energy_cost, energy, energy_max)
        actual_spirit_cost = self._clamp_cost(final_spirit_cost, spirit, spirit_max)
        
        return {
            'action_id': action_id,
            'action_name': action_cost.action_name,
            'time_cost': final_time_cost,  # 分钟
            'stamina_cost': actual_stamina_cost,
            'energy_cost': actual_energy_cost,
            'spirit_cost': actual_spirit_cost,
            'effects': action_cost.effects,
            'can_execute': self._check_can_execute(
                chara_state, action_cost, actual_stamina_cost, 
                actual_energy_cost, actual_spirit_cost
            )
        }
    
    def _apply_status_modifiers(self, stamina_cost: int, energy_cost: int, spirit_cost: int,
                                chara_state: Dict, cflags: Dict, 
                                abnormal_states: Dict) -> Tuple[int, int, int]:
        """
        应用状态修正系数
        
        根据设计思路：要睡觉状态所有行动的精力啊什么的别的花销都会*2
        """
        # 检查是否在要睡觉状态
        # 通过CFLAG判断
        sleep_status = cflags.get(1, 0)  # 假设CFLAG:1是睡眠状态
        if sleep_status >= 1:
            # 要睡觉状态，所有花销*2
            return stamina_cost * 2, energy_cost * 2, spirit_cost * 2
        
        # 检查异常状态
        for state_id, state_value in abnormal_states.items():
            if state_value > 0:
                # 根据状态应用修正
                if state_id == '轻伤':
                    return int(stamina_cost * 1.5), int(energy_cost * 1.2), int(spirit_cost * 0.8)
                elif state_id == '重伤':
                    return int(stamina_cost * 2.0), int(energy_cost * 1.5), int(spirit_cost * 0.6)
                elif state_id == '疲劳':
                    return int(stamina_cost * 1.3), int(energy_cost * 1.8), int(spirit_cost * 0.7)
                elif state_id == '极度疲劳':
                    return int(stamina_cost * 2.0), int(energy_cost * 2.5), int(spirit_cost * 0.5)
        
        return stamina_cost, energy_cost, spirit_cost
    
    def _apply_weather_modifiers(self, stamina_cost: int, energy_cost: int, spirit_cost: int,
                                 weather: str) -> Tuple[int, int, int]:
        """应用天气修正系数"""
        modifiers = self.weather_modifiers.get(weather, self.weather_modifiers['晴'])
        
        return (
            int(stamina_cost * modifiers['体力']),
            int(energy_cost * modifiers['精力']),
            int(spirit_cost * modifiers['灵力'])
        )
    
    def _apply_character_modifiers(self, time_cost: float, stamina_cost: int, 
                                    energy_cost: int, spirit_cost: int,
                                    attributes: Dict, chara_state: Dict) -> Tuple[float, int, int, int]:
        """
        应用角色能力修正
        
        根据角色的能力等级调整花销
        """
        # 获取能力等级
        ability_levels = chara_state.get('exp', {})
        
        # 体力等级越高，体力消耗越少
        stamina_level = ability_levels.get('体力Lv', 1)
        if stamina_level > 1:
            stamina_cost = int(stamina_cost * (1.0 - (stamina_level - 1) * 0.05))  # 每级减少5%
        
        # 灵力等级越高，灵力消耗越少
        magic_level = ability_levels.get('灵力Lv', 1)
        if magic_level > 1:
            spirit_cost = int(spirit_cost * (1.0 - (magic_level - 1) * 0.05))
        
        return time_cost, stamina_cost, energy_cost, spirit_cost
    
    def _clamp_cost(self, cost: int, current: int, max_value: int) -> int:
        """
        限制花销值
        
        Args:
            cost: 花销值（正数表示消耗，负数表示恢复）
            current: 当前值
            max_value: 最大值
        
        Returns:
            限制后的花销值
        """
        if cost >= 0:
            # 消耗：不能超过当前值
            return min(cost, current)
        else:
            # 恢复：不能超过最大值
            return max(cost, current - max_value)
    
    def _check_can_execute(self, chara_state: Dict, action_cost: ActionCost,
                           stamina_cost: int, energy_cost: int, spirit_cost: int) -> bool:
        """
        检查角色是否能执行该行为
        
        Args:
            chara_state: 角色状态
            action_cost: 行为花销
            stamina_cost: 实际体力消耗
            energy_cost: 实际精力消耗
            spirit_cost: 实际灵力消耗
        
        Returns:
            是否能执行
        """
        attributes = chara_state.get('attributes', {})
        
        # 检查必需的属性值
        for stat_name, min_value in action_cost.required_stats.items():
            current_value = attributes.get(stat_name, 0)
            if current_value < min_value:
                return False
        
        # 检查是否有足够的资源
        if stamina_cost > attributes.get('体力', 0):
            return False
        if energy_cost > attributes.get('精力', 0):
            return False
        if spirit_cost > attributes.get('灵力', 0):
            return False
        
        return True
    
    def calculate_daily_cost(self, chara_id: str) -> Dict[str, Any]:
        """
        计算角色的每日基础花销
        
        根据设计思路：根据每个角色的基础值计算其每天花销
        
        Args:
            chara_id: 角色ID
        
        Returns:
            每日花销信息字典
        """
        chara_state = self.console.allstate.get(chara_id)
        if not chara_state:
            return {'error': f'角色{chara_id}不存在'}
        
        attributes = chara_state.get('attributes', {})
        
        # 基础每日花销计算
        # 根据角色基础值计算
        stamina_max = attributes.get('体力上限', 100)
        stamina_max_actual = attributes.get('体力', stamina_max)
        
        # 每日基础消耗约为最大体力的10%
        daily_stamina_cost = int(stamina_max * 0.1)
        
        # 每日精力消耗约为最大精力的15%
        energy_max = attributes.get('精力上限', 100)
        energy_actual = attributes.get('精力', energy_max)
        daily_energy_cost = int(energy_max * 0.15)
        
        # 每日灵力消耗约为最大灵力的5%
        spirit_max = attributes.get('灵力上限', 100)
        spirit_actual = attributes.get('灵力', spirit_max)
        daily_spirit_cost = int(spirit_max * 0.05)
        
        return {
            'chara_id': chara_id,
            'chara_name': chara_state.get('name', '未知'),
            'daily_stamina_cost': daily_stamina_cost,
            'daily_energy_cost': daily_energy_cost,
            'daily_spirit_cost': daily_spirit_cost,
            'current_stamina': stamina_max_actual,
            'current_energy': energy_actual,
            'current_spirit': spirit_actual
        }
    
    def get_available_actions(self, chara_id: str, 
                              location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取角色当前可执行的所有行为
        
        Args:
            chara_id: 角色ID
            location: 当前位置（可选，用于过滤行为）
        
        Returns:
            可执行行为列表
        """
        available_actions = []
        
        # 获取当前上下文
        context = self._get_current_context()
        
        for action_id, action_cost in self.action_costs.items():
            # 计算该行为的花销
            cost_result = self.calculate_action_cost(chara_id, action_id, context)
            
            # 如果可以执行，加入列表
            if cost_result.get('can_execute', False):
                available_actions.append(cost_result)
        
        return available_actions
    
    def _get_current_context(self) -> Dict[str, Any]:
        """
        获取当前游戏上下文
        
        Returns:
            包含天气、时间等信息的字典
        """
        # 从全局System中获取信息
        system_key = self.console.init.global_key.get('System', {})
        
        # 尝试从时间控制事件获取准确的时间信息
        try:
            time_info = self.console.event_manager.trigger_event(
                'time_control',
                type('this', (object,), {'console': self.console, 'event_manager': self.console.event_manager})(),
                'get',
                format_type='standard'
            )
            if time_info and isinstance(time_info, dict):
                hour = time_info.get('HOUR', 0)
                weekday = time_info.get('WEEKDAY', 1)
            else:
                hour = system_key.get('HOUR', 0)
                weekday = system_key.get('WEEKDAY', 1)
        except Exception:
            hour = system_key.get('HOUR', 0)
            weekday = system_key.get('WEEKDAY', 1)
        
        return {
            'weather': system_key.get('WEATHER', '晴'),
            'hour': hour,
            'weekday': weekday
        }
    
    def apply_cost_to_character(self, chara_id: str, action_id: str) -> Dict[str, Any]:
        """
        应用花销到角色
        
        Args:
            chara_id: 角色ID
            action_id: 行为ID
        
        Returns:
            应用结果
        """
        # 计算花销
        cost_result = self.calculate_action_cost(chara_id, action_id)
        
        if not cost_result.get('can_execute', False):
            return {
                'success': False,
                'message': f'角色{chara_id}无法执行行为{action_id}',
                'reason': cost_result.get('error', '资源不足')
            }
        
        # 获取角色数据
        chara_state = self.console.allstate.get(chara_id)
        if not chara_state:
            return {'success': False, 'message': f'角色{chara_id}不存在'}
        
        attributes = chara_state['attributes']
        
        # 应用花销
        attributes['体力'] -= cost_result['stamina_cost']
        attributes['精力'] -= cost_result['energy_cost']
        attributes['灵力'] -= cost_result['spirit_cost']
        
        return {
            'success': True,
            'message': f'角色{chara_id}成功执行{cost_result["action_name"]}',
            'cost_applied': cost_result
        }


    def to_save_data(self) -> Dict[str, Any]:
        """
        生成可存档的数据
        
        Returns:
            可序列化的数据字典
        """
        return {}  # CostCalculator状态无持久化需求


# 全局实例（在初始化时创建）
_cost_calculator_instance: Optional[CostCalculator] = None


def get_cost_calculator(this) -> CostCalculator:
    """
    获取花销计算器实例
    
    Args:
        this: 事件上下文对象
    
    Returns:
        CostCalculator实例
    """
    global _cost_calculator_instance
    
    if _cost_calculator_instance is None:
        _cost_calculator_instance = CostCalculator(this.console)
    
    return _cost_calculator_instance


def event_cost_calculator(this, operation: str, **kwargs):
    """
    花销计算器事件
    
    Trigger ID: cost_calculator
    
    支持的操作:
        - 'calculate': 计算行为花销
        - 'daily': 计算每日花销
        - 'available': 获取可执行行为
        - 'apply': 应用花销到角色
        - 'reload': 重新加载花销配置
    
    Args:
        this: 事件上下文对象
        operation: 操作类型
        **kwargs: 操作参数
    
    Returns:
        操作结果
    """
    calculator = get_cost_calculator(this)
    
    if operation == 'calculate':
        # 计算行为花销
        chara_id = kwargs.get('chara_id', '0')
        action_id = kwargs.get('action_id', 'rest')
        context = kwargs.get('context')
        
        return calculator.calculate_action_cost(chara_id, action_id, context)
    
    elif operation == 'daily':
        # 计算每日花销
        chara_id = kwargs.get('chara_id', '0')
        return calculator.calculate_daily_cost(chara_id)
    
    elif operation == 'available':
        # 获取可执行行为
        chara_id = kwargs.get('chara_id', '0')
        location = kwargs.get('location')
        
        return calculator.get_available_actions(chara_id, location)
    
    elif operation == 'apply':
        # 应用花销到角色
        chara_id = kwargs.get('chara_id', '0')
        action_id = kwargs.get('action_id', 'rest')
        
        return calculator.apply_cost_to_character(chara_id, action_id)
    
    elif operation == 'reload':
        # 重新加载花销配置
        calculator.load_action_costs()
        return {'status': 'reloaded'}
    
    else:
        return {'error': f'未知操作: {operation}'}


# 注册事件触发器
event_cost_calculator.event_trigger = "cost_calculator"
