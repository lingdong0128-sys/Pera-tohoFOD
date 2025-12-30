"""
AI核心决策模块
实现Pera幻想FOD中的角色AI决策系统

根据设计思路：
- 每次master执行操作的时候，角色们也会进行行动计算
- 根据当前花销计算当前花销最小的行为是什么
- 角色也可以和真人一样行动
- 主角执行操作时，其他角色也在进行行动计算
"""

import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import copy

# 导入花销计算器
from .cost_calculator import CostCalculator, get_cost_calculator


@dataclass
class AIDecision:
    """AI决策数据类"""
    chara_id: str           # 角色ID
    chara_name: str         # 角色名称
    action_id: str          # 选择的行为ID
    action_name: str        # 行为名称
    cost_score: float       # 花销评分（越低越好）
    time_cost: float        # 时间消耗
    reasoning: str          # 决策理由
    priority: int           # 优先级（0-100）


class AICore:
    """AI核心类 - 负责角色的行为决策"""
    
    def __init__(self, console, cost_calculator: CostCalculator):
        """
        初始化AI核心
        
        Args:
            console: 控制台对象
            cost_calculator: 花销计算器实例
        """
        self.console = console
        self.init = console.init
        self.cost_calculator = cost_calculator
        
        # 角色行为偏好权重
        self.behavior_weights = {
            '探索': {'探索': 1.0, '战斗': 0.8, '社交': 0.3},
            '战斗': {'探索': 0.7, '战斗': 1.2, '社交': 0.2},
            '社交': {'探索': 0.5, '战斗': 0.3, '社交': 1.0},
            '保守': {'探索': 0.4, '战斗': 0.2, '社交': 0.6},
        }
        
        # 时间段行为修正
        self.time_modifiers = {
            'morning': (6, 9, {'探索': 1.2, '战斗': 0.8, '社交': 0.7, '休息': 0.5}),
            'day': (9, 18, {'探索': 1.0, '战斗': 1.0, '社交': 1.0, '休息': 0.6}),
            'evening': (18, 21, {'探索': 0.8, '战斗': 0.7, '社交': 1.2, '休息': 0.8}),
            'night': (21, 6, {'探索': 0.4, '战斗': 0.5, '社交': 0.3, '休息': 1.5}),
        }
        
        # 地牢内的行为修正
        self.dungeon_modifiers = {
            '探索': 1.5,    # 地牢内探索优先
            '战斗': 1.3,
            '社交': 0.5,
            '休息': 0.7,
        }
    
    def decide_action(self, chara_id: str, context: Optional[Dict[str, Any]] = None) -> AIDecision:
        """
        为角色决定最优行为
        
        根据设计思路：根据当前花销计算当前花销最小的行为是什么
        
        Args:
            chara_id: 角色ID
            context: 上下文信息
        
        Returns:
            AI决策对象
        """
        # 获取角色状态
        chara_state = self.console.allstate.get(chara_id)
        if not chara_state:
            raise ValueError(f'角色{chara_id}不存在')
        
        # 获取可执行的行为列表
        available_actions = self.cost_calculator.get_available_actions(chara_id)
        
        if not available_actions:
            # 如果没有可执行行为，强制休息
            return self._force_rest_decision(chara_id, chara_state)
        
        # 获取角色当前位置和场景
        location = chara_state.get('data', {}).get('小地图', '')
        is_in_dungeon = self._check_if_in_dungeon(location)
        
        # 计算每个行为的评分
        scored_actions = []
        for action_info in available_actions:
            score = self._calculate_action_score(
                chara_state, action_info, context, is_in_dungeon
            )
            
            scored_actions.append({
                'action_info': action_info,
                'score': score
            })
        
        # 按评分排序（分数越高越好，但我们计算的是成本，所以要反转）
        scored_actions.sort(key=lambda x: x['score'], reverse=True)
        
        # 选择最优行为
        best_action = scored_actions[0]['action_info']
        
        # 构建决策对象
        return AIDecision(
            chara_id=chara_id,
            chara_name=chara_state.get('name', '未知'),
            action_id=best_action['action_id'],
            action_name=best_action['action_name'],
            cost_score=scored_actions[0]['score'],
            time_cost=best_action['time_cost'],
            reasoning=self._generate_reasoning(chara_state, best_action),
            priority=self._calculate_priority(chara_state, best_action)
        )
    
    def _force_rest_decision(self, chara_id: str, chara_state: Dict) -> AIDecision:
        """强制休息决策（当没有可执行行为时）"""
        return AIDecision(
            chara_id=chara_id,
            chara_name=chara_state.get('name', '未知'),
            action_id='rest',
            action_name='休息',
            cost_score=100.0,
            time_cost=30,
            reasoning='无法执行任何其他行为，被迫休息',
            priority=100
        )
    
    def _calculate_action_score(self, chara_state: Dict, action_info: Dict, 
                                 context: Optional[Dict], is_in_dungeon: bool) -> float:
        """
        计算行为的评分
        
        评分考虑因素：
        1. 花销成本（体力、精力、灵力消耗）
        2. 时间成本
        3. 角色当前状态
        4. 角色行为偏好
        5. 时间段修正
        6. 地牢修正
        
        Args:
            chara_state: 角色状态
            action_info: 行为信息
            context: 上下文信息
            is_in_dungeon: 是否在地牢中
        
        Returns:
            评分（越高越好）
        """
        score = 0.0
        
        # 1. 基础评分：根据花销计算（花销越少，评分越高）
        stamina_cost = action_info.get('stamina_cost', 0)
        energy_cost = action_info.get('energy_cost', 0)
        spirit_cost = action_info.get('spirit_cost', 0)
        
        # 如果是恢复类行为（负花销），给予加分
        if stamina_cost < 0 or energy_cost < 0 or spirit_cost < 0:
            recovery_bonus = abs(stamina_cost + energy_cost + spirit_cost) / 100.0
            score += recovery_bonus
        else:
            # 消耗类行为，花销越少越好
            total_cost = stamina_cost + energy_cost + spirit_cost
            score -= total_cost / 100.0
        
        # 2. 时间成本（时间越短，评分略高）
        time_cost = action_info.get('time_cost', 0)
        score -= time_cost / 200.0
        
        # 3. 角色当前状态修正
        attributes = chara_state.get('attributes', {})
        stamina_ratio = attributes.get('体力', 100) / max(attributes.get('体力上限', 100), 1)
        energy_ratio = attributes.get('精力', 100) / max(attributes.get('精力上限', 100), 1)
        
        # 体力/精力低时，优先选择恢复类行为
        if stamina_ratio < 0.3 and stamina_cost < 0:
            score += 50.0
        if energy_ratio < 0.3 and energy_cost < 0:
            score += 50.0
        
        # 体力/精力高时，优先选择消耗类行为
        if stamina_ratio > 0.8 and stamina_cost > 0:
            score += 10.0
        if energy_ratio > 0.8 and energy_cost > 0:
            score += 10.0
        
        # 4. 角色行为偏好修正
        personality = self._get_character_personality(chara_state)
        weights = self.behavior_weights.get(personality, self.behavior_weights['探索'])
        
        action_name = action_info.get('action_name', '')
        for behavior_type, weight in weights.items():
            if behavior_type in action_name:
                score *= weight
                break
        
        # 5. 时间段修正
        if context:
            hour = context.get('hour', 12)
            for period, (start, end, modifiers) in self.time_modifiers.items():
                if (start <= hour < end) or (period == 'night' and (hour >= 21 or hour < 6)):
                    for behavior_type, modifier in modifiers.items():
                        if behavior_type in action_name:
                            score *= modifier
                    break
        
        # 6. 地牢修正
        if is_in_dungeon:
            for behavior_type, modifier in self.dungeon_modifiers.items():
                if behavior_type in action_name:
                    score *= modifier
                    break
        
        # 添加随机性（让AI不完全 deterministic）
        score += random.uniform(-5, 5)
        
        return score
    
    def _get_character_personality(self, chara_state: Dict) -> str:
        """
        获取角色性格类型
        
        根据角色的CFLAG或属性值判断性格类型
        
        Args:
            chara_state: 角色状态
        
        Returns:
            性格类型
        """
        # 从CFLAG获取性格（如果有）
        cflags = chara_state.get('cflags', {})
        personality = cflags.get(10, '探索')  # CFLAG:10 表示性格类型
        
        # 如果没有定义，根据属性推断
        if personality not in self.behavior_weights:
            attributes = chara_state.get('attributes', {})
            # 灵力高且体力高 -> 战斗型
            if attributes.get('灵力', 0) > 80 and attributes.get('体力', 0) > 80:
                return '战斗'
            # 体力低且精力高 -> 保守型
            elif attributes.get('体力', 0) < 50 and attributes.get('精力', 0) > 80:
                return '保守'
            # 灵力高 -> 社交型
            elif attributes.get('灵力', 0) > 80:
                return '社交'
            else:
                return '探索'
        
        return personality
    
    def _check_if_in_dungeon(self, location: str) -> bool:
        """
        检查角色是否在地牢中
        
        Args:
            location: 角色当前位置
        
        Returns:
            是否在地牢中
        """
        # 如果位置ID以'D'开头或包含'dungeon'，则认为在地牢中
        return location.startswith('D') or 'dungeon' in location.lower()
    
    def _generate_reasoning(self, chara_state: Dict, action_info: Dict) -> str:
        """
        生成决策理由
        
        Args:
            chara_state: 角色状态
            action_info: 行为信息
        
        Returns:
            决策理由
        """
        action_name = action_info.get('action_name', '未知行为')
        
        attributes = chara_state.get('attributes', {})
        stamina = attributes.get('体力', 0)
        stamina_max = attributes.get('体力上限', 100)
        energy = attributes.get('精力', 0)
        energy_max = attributes.get('精力上限', 100)
        
        reasoning_parts = [f'选择{action_name}']
        
        # 根据当前状态生成理由
        if stamina < stamina_max * 0.3:
            reasoning_parts.append('体力不足，需要恢复')
        elif stamina > stamina_max * 0.8:
            reasoning_parts.append('体力充沛')
        
        if energy < energy_max * 0.3:
            reasoning_parts.append('精力不足')
        elif energy > energy_max * 0.8:
            reasoning_parts.append('精力充足')
        
        # 根据行为类型生成理由
        if '休息' in action_name or '睡觉' in action_name:
            reasoning_parts.append('恢复状态')
        elif '探索' in action_name:
            reasoning_parts.append('寻找机会')
        elif '战斗' in action_name:
            reasoning_parts.append('提升实力')
        elif '社交' in action_name:
            reasoning_parts.append('建立关系')
        
        return '，'.join(reasoning_parts)
    
    def _calculate_priority(self, chara_state: Dict, action_info: Dict) -> int:
        """
        计算决策优先级
        
        Args:
            chara_state: 角色状态
            action_info: 行为信息
        
        Returns:
            优先级（0-100）
        """
        priority = 50  # 默认优先级
        
        attributes = chara_state.get('attributes', {})
        stamina_ratio = attributes.get('体力', 100) / max(attributes.get('体力上限', 100), 1)
        energy_ratio = attributes.get('精力', 100) / max(attributes.get('精力上限', 100), 1)
        
        action_name = action_info.get('action_name', '')
        
        # 状态危急时，提高恢复类行为优先级
        if stamina_ratio < 0.2 and '休息' in action_name:
            priority = 100
        elif energy_ratio < 0.2 and '休息' in action_name:
            priority = 95
        
        # 状态良好时，提高探索类行为优先级
        elif stamina_ratio > 0.8 and energy_ratio > 0.8 and '探索' in action_name:
            priority = 80
        
        return priority
    
    def process_all_characters(self, context: Optional[Dict[str, Any]] = None,
                                exclude_ids: Optional[List[str]] = None) -> List[AIDecision]:
        """
        处理所有角色的AI决策
        
        根据设计思路：每次master执行操作的时候，角色们也会进行行动计算
        
        Args:
            context: 上下文信息
            exclude_ids: 排除的角色ID列表（如主角）
        
        Returns:
            所有角色的决策列表
        """
        if exclude_ids is None:
            exclude_ids = ['0']  # 默认排除主角
        
        decisions = []
        
        # 遍历所有角色
        for chara_id in self.init.chara_ids:
            if chara_id in exclude_ids:
                continue
            
            try:
                decision = self.decide_action(chara_id, context)
                decisions.append(decision)
            except Exception as e:
                # 跳过决策失败的角色
                print(f'角色{chara_id}决策失败: {e}')
                continue
        
        return decisions
    
    def execute_character_action(self, chara_id: str, action_id: str) -> Dict[str, Any]:
        """
        执行角色的行为
        
        Args:
            chara_id: 角色ID
            action_id: 行为ID
        
        Returns:
            执行结果
        """
        # 获取角色状态
        chara_state = self.console.allstate.get(chara_id)
        if not chara_state:
            return {'success': False, 'message': f'角色{chara_id}不存在'}
        
        # 处理移动类行为
        if action_id in ['move_small_map', 'move_big_map']:
            move_result = self._handle_character_move(chara_id, action_id)
            if move_result.get('success'):
                # 移动成功后应用花销
                cost_result = self.cost_calculator.apply_cost_to_character(chara_id, action_id)
                return {
                    'success': True,
                    'message': f'角色{chara_id}移动成功',
                    'move_result': move_result,
                    'cost_applied': cost_result
                }
            return move_result
        
        # 处理地牢探索行为
        elif action_id == 'dungeon_explore':
            dungeon_result = self._handle_dungeon_explore(chara_id)
            if dungeon_result.get('success'):
                cost_result = self.cost_calculator.apply_cost_to_character(chara_id, action_id)
                return {
                    'success': True,
                    'message': f'角色{chara_id}地牢探索成功',
                    'dungeon_result': dungeon_result,
                    'cost_applied': cost_result
                }
            return dungeon_result
        
        # 处理地牢战斗行为
        elif action_id == 'dungeon_combat':
            combat_result = self._handle_dungeon_combat(chara_id)
            if combat_result.get('success'):
                cost_result = self.cost_calculator.apply_cost_to_character(chara_id, action_id)
                return {
                    'success': True,
                    'message': f'角色{chara_id}地牢战斗成功',
                    'combat_result': combat_result,
                    'cost_applied': cost_result
                }
            return combat_result
        
        # 处理社交行为
        elif action_id == 'social':
            social_result = self._handle_social_action(chara_id)
            if social_result.get('success'):
                cost_result = self.cost_calculator.apply_cost_to_character(chara_id, action_id)
                return {
                    'success': True,
                    'message': f'角色{chara_id}社交成功',
                    'social_result': social_result,
                    'cost_applied': cost_result
                }
            return social_result
        
        # 默认行为：直接应用花销
        result = self.cost_calculator.apply_cost_to_character(chara_id, action_id)
        
        if result.get('success'):
            # 这里可以添加更多的行为执行逻辑
            # 例如：触发特定事件、更新位置等
            pass
        
        return result
    
    def process_time_step(self, time_cost: float, 
                          context: Optional[Dict[str, Any]] = None,
                          exclude_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        处理一个时间步长的所有角色行动
        
        根据设计思路：
        - 把时间拆分成基础时间单位
        - 一个时间单位的消耗看作是一次时间迭代
        - 主角执行操作时，其他角色也在进行行动计算
        
        Args:
            time_cost: 主角操作消耗的时间（分钟）
            context: 上下文信息
            exclude_ids: 排除的角色ID列表
        
        Returns:
            所有角色的行动结果列表
        """
        # 从time.csv读取基础时间单位（默认为5分钟）
        # time.csv中定义了"时,60"，即一时60分，基础时间单位就是分
        # 我们可以通过读取配置来确定基础时间单位
        try:
            time_data = self.console.init.global_key.get('time', {})
            # 尝试从time.csv获取"时"的值（一时多少分）
            minutes_per_hour = int(time_data.get('时', 60))
            # 基础时间单位可以设置为分钟，或者按比例设置
            # 这里设置为5分钟作为默认基础时间单位
            base_time_unit = 5
        except (ValueError, TypeError, AttributeError):
            # 读取失败时使用默认值5分钟
            base_time_unit = 5
        
        # 计算需要执行的迭代次数
        iterations = int(time_cost / base_time_unit)
        
        all_results = []
        
        # 每个迭代执行一次角色决策
        for _ in range(iterations):
            # 获取所有角色的决策
            decisions = self.process_all_characters(context, exclude_ids)
            
            # 执行决策
            for decision in decisions:
                result = self.execute_character_action(decision.chara_id, decision.action_id)
                all_results.append({
                    'decision': decision,
                    'result': result
                })
            
            # 每次迭代后调用time_control事件更新全局时间
            try:
                # 创建模拟的this对象用于事件调用
                mock_this = type('this', (object,), {
                    'console': self.console,
                    'event_manager': self.console.event_manager
                })
                
                # 调用time_control事件的add操作，增加基础时间单位
                self.console.event_manager.trigger_event(
                    'time_control',
                    mock_this,
                    'add',
                    minutes=base_time_unit
                )
            except Exception as e:
                # 如果时间更新失败，记录错误但不中断流程
                print(f'时间更新失败: {e}')
        
        return all_results


    def _handle_character_move(self, chara_id: str, action_id: str) -> Dict[str, Any]:
        """
        处理角色自动移动
        
        Args:
            chara_id: 角色ID
            action_id: 移动行为ID
        
        Returns:
            移动结果
        """
        try:
            # 获取角色当前位置
            current_big = self.console.charater_pwds.get(chara_id, {}).get('大地图')
            current_small = self.console.charater_pwds.get(chara_id, {}).get('小地图')
            
            if not current_big or not current_small:
                return {'success': False, 'message': '角色位置信息不完整'}
            
            # 获取地图数据
            map_data = getattr(self.console, 'map_data', {})
            
            if action_id == 'move_small_map':
                # 小地图间移动：随机选择同大地图下的其他小地图
                area_content = map_data.get(current_big, {})
                room_keys = [key for key in area_content.keys() 
                            if key not in ['状态', 'dungeon_level', 'description'] and key != current_small]
                
                if room_keys:
                    # 随机选择目标
                    import random
                    target_small = random.choice(room_keys)
                    
                    # 调用移动事件
                    from events.移动 import event_强制移动
                    
                    # 创建模拟this对象
                    mock_this = type('this', (object,), {
                        'console': self.console,
                        'trigger_event': self.console.event_manager.trigger_event,
                        'charater_pwds': self.console.charater_pwds,
                        'cs': self.console.cs
                    })
                    
                    event_强制移动(mock_this, chara_id, current_big, target_small)
                    
                    return {
                        'success': True,
                        'from': f'{current_big}_{current_small}',
                        'to': f'{current_big}_{target_small}',
                        'move_type': '小地图间移动'
                    }
                
                return {'success': False, 'message': '没有可移动的目标'}
            
            elif action_id == 'move_big_map':
                # 大地图间移动：随机选择其他大地图
                big_map_keys = [key for key in map_data.keys() 
                               if key != 'DungeonInstance' and key != current_big]
                
                if big_map_keys:
                    import random
                    target_big = random.choice(big_map_keys)
                    
                    # 获取目标大地图下的第一个小地图
                    target_area = map_data.get(target_big, {})
                    room_keys = [key for key in target_area.keys() 
                               if key not in ['状态', 'dungeon_level', 'description']]
                    
                    if room_keys:
                        target_small = room_keys[0]
                        
                        # 调用移动事件
                        from events.移动 import event_强制移动
                        
                        mock_this = type('this', (object,), {
                            'console': self.console,
                            'trigger_event': self.console.event_manager.trigger_event,
                            'charater_pwds': self.console.charater_pwds,
                            'cs': self.console.cs
                        })
                        
                        event_强制移动(mock_this, chara_id, target_big, target_small)
                        
                        return {
                            'success': True,
                            'from': f'{current_big}_{current_small}',
                            'to': f'{target_big}_{target_small}',
                            'move_type': '大地图间移动'
                        }
                
                return {'success': False, 'message': '没有可移动的目标'}
        
        except Exception as e:
            return {'success': False, 'message': f'移动失败: {str(e)}'}
    
    def _handle_dungeon_explore(self, chara_id: str) -> Dict[str, Any]:
        """
        处理地牢探索行为
        
        Args:
            chara_id: 角色ID
        
        Returns:
            探索结果
        """
        try:
            # 获取角色当前位置
            current_small = self.console.charater_pwds.get(chara_id, {}).get('小地图', '')
            
            # 检查是否在地牢中
            if not self._check_if_in_dungeon(current_small):
                return {'success': False, 'message': '角色不在地牢中'}
            
            # 获取地牢实例数据
            dungeon_data = self.console.init.global_key.get('DungeonInstance', {})
            current_room = dungeon_data.get('rooms', {}).get(current_small, {})
            
            if not current_room:
                return {'success': False, 'message': '地牢房间数据不存在'}
            
            # 检查房间出口
            exits = current_room.get('exits', {})
            if '前' in exits:
                next_room = exits['前']
                
                # 移动到下一个房间
                from events.移动 import event_强制移动
                
                mock_this = type('this', (object,), {
                    'console': self.console,
                    'trigger_event': self.console.event_manager.trigger_event,
                    'charater_pwds': self.console.charater_pwds,
                    'cs': self.console.cs
                })
                
                event_强制移动(mock_this, chara_id, 'DungeonInstance', next_room)
                
                return {
                    'success': True,
                    'from': current_small,
                    'to': next_room,
                    'found_items': [],  # 可以扩展为随机发现物品
                    'encountered_enemy': False  # 可以扩展为遭遇敌人判定
                }
            else:
                return {'success': False, 'message': '没有前进的道路'}
        
        except Exception as e:
            return {'success': False, 'message': f'地牢探索失败: {str(e)}'}
    
    def _handle_dungeon_combat(self, chara_id: str) -> Dict[str, Any]:
        """
        处理地牢战斗行为
        
        Args:
            chara_id: 角色ID
        
        Returns:
            战斗结果
        """
        try:
            # 获取角色当前位置
            current_small = self.console.charater_pwds.get(chara_id, {}).get('小地图', '')
            
            # 检查是否在地牢中
            if not self._check_if_in_dungeon(current_small):
                return {'success': False, 'message': '角色不在地牢中'}
            
            # 获取角色状态
            chara_state = self.console.allstate.get(chara_id)
            if not chara_state:
                return {'success': False, 'message': '角色不存在'}
            
            attributes = chara_state.get('attributes', {})
            stamina = attributes.get('体力', 0)
            spirit = attributes.get('灵力', 0)
            
            # 简单的战斗判定（后续可以扩展为更复杂的战斗系统）
            # 根据体力和灵力计算胜率
            win_rate = (stamina + spirit) / 200.0
            win_rate = max(0.2, min(0.9, win_rate))  # 限制在20%-90%之间
            
            import random
            is_victory = random.random() < win_rate
            
            if is_victory:
                # 战斗胜利
                # 增加经验值
                exp_data = chara_state.get('exp', {})
                exp_data['战斗经验'] = exp_data.get('战斗经验', 0) + 10
                
                # 可能获得战利品（简化处理）
                loot_found = random.random() < 0.3  # 30%概率获得物品
                
                return {
                    'success': True,
                    'result': 'victory',
                    'message': '战斗胜利',
                    'exp_gained': 10,
                    'loot_found': loot_found,
                    'damage_taken': random.randint(0, 20)
                }
            else:
                # 战斗失败
                # 扣除额外体力
                damage = random.randint(20, 50)
                attributes['体力'] = max(0, attributes['体力'] - damage)
                
                return {
                    'success': True,
                    'result': 'defeat',
                    'message': '战斗失败',
                    'damage_taken': damage
                }
        
        except Exception as e:
            return {'success': False, 'message': f'地牢战斗失败: {str(e)}'}
    
    def _handle_social_action(self, chara_id: str) -> Dict[str, Any]:
        """
        处理社交行为
        
        Args:
            chara_id: 角色ID
        
        Returns:
            社交结果
        """
        try:
            # 获取当前区域的所有角色
            current_big = self.console.charater_pwds.get(chara_id, {}).get('大地图')
            current_small = self.console.charater_pwds.get(chara_id, {}).get('小地图')
            
            if not current_big or not current_small:
                return {'success': False, 'message': '角色位置信息不完整'}
            
            # 查找同一区域的其他角色
            other_characters = []
            for other_id, other_state in self.console.allstate.items():
                if other_id == chara_id:
                    continue
                
                other_big = self.console.charater_pwds.get(other_id, {}).get('大地图')
                other_small = self.console.charater_pwds.get(other_id, {}).get('小地图')
                
                if other_big == current_big and other_small == current_small:
                    other_characters.append({
                        'id': other_id,
                        'name': other_state.get('name', '未知')
                    })
            
            if not other_characters:
                return {'success': False, 'message': '当前区域没有其他角色'}
            
            # 随机选择一个角色进行交互
            import random
            target = random.choice(other_characters)
            
            # 提升好感度/信赖度（简化处理）
            # 这里可以扩展为更复杂的关系系统
            affection_increase = random.randint(1, 5)
            
            return {
                'success': True,
                'target_id': target['id'],
                'target_name': target['name'],
                'interaction_type': '聊天',
                '好感度提升': affection_increase
            }
        
        except Exception as e:
            return {'success': False, 'message': f'社交行为失败: {str(e)}'}
    
    def to_save_data(self) -> Dict[str, Any]:
        """
        生成可存档的数据
        
        Returns:
            可序列化的数据字典
        """
        return {}  # AICore状态无持久化需求


# 全局实例（在初始化时创建）
_ai_core_instance: Optional[AICore] = None


def get_ai_core(this) -> AICore:
    """
    获取AI核心实例
    
    Args:
        this: 事件上下文对象
    
    Returns:
        AICore实例
    """
    global _ai_core_instance
    
    if _ai_core_instance is None:
        calculator = get_cost_calculator(this)
        _ai_core_instance = AICore(this.console, calculator)
    
    return _ai_core_instance


def event_ai_core(this, operation: str, **kwargs):
    """
    AI核心事件
    
    Trigger ID: ai_core
    
    支持的操作:
        - 'decide': 为角色决定行为
        - 'process_all': 处理所有角色的决策
        - 'execute': 执行角色行为
        - 'time_step': 处理一个时间步长的所有角色行动
    
    Args:
        this: 事件上下文对象
        operation: 操作类型
        **kwargs: 操作参数
    
    Returns:
        操作结果
    """
    ai_core = get_ai_core(this)
    
    if operation == 'decide':
        # 为角色决定行为
        chara_id = kwargs.get('chara_id', '0')
        context = kwargs.get('context')
        
        decision = ai_core.decide_action(chara_id, context)
        
        # 转换为可序列化的字典
        return {
            'chara_id': decision.chara_id,
            'chara_name': decision.chara_name,
            'action_id': decision.action_id,
            'action_name': decision.action_name,
            'cost_score': decision.cost_score,
            'time_cost': decision.time_cost,
            'reasoning': decision.reasoning,
            'priority': decision.priority
        }
    
    elif operation == 'process_all':
        # 处理所有角色的决策
        context = kwargs.get('context')
        exclude_ids = kwargs.get('exclude_ids', ['0'])
        
        decisions = ai_core.process_all_characters(context, exclude_ids)
        
        # 转换为可序列化的字典列表
        return [
            {
                'chara_id': d.chara_id,
                'chara_name': d.chara_name,
                'action_id': d.action_id,
                'action_name': d.action_name,
                'cost_score': d.cost_score,
                'time_cost': d.time_cost,
                'reasoning': d.reasoning,
                'priority': d.priority
            }
            for d in decisions
        ]
    
    elif operation == 'execute':
        # 执行角色行为
        chara_id = kwargs.get('chara_id', '0')
        action_id = kwargs.get('action_id', 'rest')
        
        return ai_core.execute_character_action(chara_id, action_id)
    
    elif operation == 'time_step':
        # 处理一个时间步长的所有角色行动
        time_cost = kwargs.get('time_cost', 5)
        context = kwargs.get('context')
        exclude_ids = kwargs.get('exclude_ids', ['0'])
        
        results = ai_core.process_time_step(time_cost, context, exclude_ids)
        
        # 转换为可序列化的字典列表
        return [
            {
                'decision': {
                    'chara_id': r['decision'].chara_id,
                    'chara_name': r['decision'].chara_name,
                    'action_id': r['decision'].action_id,
                    'action_name': r['decision'].action_name,
                    'reasoning': r['decision'].reasoning,
                },
                'result': r['result']
            }
            for r in results
        ]
    
    else:
        return {'error': f'未知操作: {operation}'}


# 注册事件触发器
event_ai_core.event_trigger = "ai_core"
