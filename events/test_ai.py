"""
AI机测试事件
用于测试和演示角色AI决策系统的功能

使用方法：
在游戏中触发test_ai事件即可看到AI决策效果
"""

def event_test_ai(this):
    """
    测试AI机功能
    
    Trigger ID: test_ai
    
    功能演示：
    1. 测试天气系统
    2. 计算角色的行为花销
    3. 为角色决定最优行为
    4. 处理所有角色的AI决策
    5. 执行角色行为
    """
    this.console.PRINT("=== 角色AI机测试 ===", colors=(255, 255, 100))
    
    # 测试0：天气系统
    this.console.PRINT("\n【测试0】天气系统", colors=(100, 255, 100))
    
    # 获取当前天气
    weather_info = this.event_manager.trigger_event('weather_system', this, 'get')
    this.console.PRINT(f"  当前天气: {weather_info.get('name', '晴')} ({weather_info.get('description', '')})")
    this.console.PRINT(f"  修正系数: 体力={weather_info.get('stamina_modifier', 1.0)}, "
                      f"精力={weather_info.get('energy_modifier', 1.0)}, "
                      f"灵力={weather_info.get('spirit_modifier', 1.0)}")
    
    # 获取所有天气类型
    all_weathers = this.event_manager.trigger_event('weather_system', this, 'get_all_weathers')
    this.console.PRINT(f"\n  可用天气类型: {', '.join(all_weathers.keys())}")
    
    # 获取当前上下文（从天气系统和时间控制获取）
    try:
        time_info = this.event_manager.trigger_event('time_control', this, 'get', format_type='standard')
        if time_info and isinstance(time_info, dict):
            hour = time_info.get('HOUR', 12)
            weekday = time_info.get('WEEKDAY', 1)
        else:
            hour = 12
            weekday = 1
    except Exception:
        hour = 12
        weekday = 1
    
    context = {
        'weather': weather_info.get('weather', '晴'),
        'hour': hour,
        'weekday': weekday
    }
    
    this.console.PRINT(f"\n当前上下文：天气={context['weather']}, 时间={context['hour']}时, 星期={context['weekday']}", 
                      colors=(200, 200, 255))
    
    # 测试1：计算行为花销
    this.console.PRINT("\n【测试1】计算主角执行各种行为的花销", colors=(100, 255, 100))
    test_actions = ['rest', 'explore', 'combat', 'social', 'dungeon_explore']
    
    for action_id in test_actions:
        result = this.event_manager.trigger_event('cost_calculator', this, 'calculate',
                                                   chara_id='0', action_id=action_id, context=context)
        
        action_name = result.get('action_name', action_id)
        time_cost = result.get('time_cost', 0)
        stamina_cost = result.get('stamina_cost', 0)
        energy_cost = result.get('energy_cost', 0)
        spirit_cost = result.get('spirit_cost', 0)
        can_execute = result.get('can_execute', False)
        
        status = "✓可执行" if can_execute else "✗不可执行"
        this.console.PRINT(f"  {action_name:12s} | 时间:{time_cost:4.0f}分 | "
                          f"体力:{stamina_cost:4d} | 精力:{energy_cost:4d} | "
                          f"灵力:{spirit_cost:4d} | {status}")
    
    # 测试2：计算每日花销
    this.console.PRINT("\n【测试2】计算主角的每日基础花销", colors=(100, 255, 100))
    daily_result = this.event_manager.trigger_event('cost_calculator', this, 'daily', chara_id='0')
    
    this.console.PRINT(f"  每日体力消耗: {daily_result.get('daily_stamina_cost', 0)}")
    this.console.PRINT(f"  每日精力消耗: {daily_result.get('daily_energy_cost', 0)}")
    this.console.PRINT(f"  每日灵力消耗: {daily_result.get('daily_spirit_cost', 0)}")
    
    # 测试3：为单个角色决定行为
    this.console.PRINT("\n【测试3】为角色决定最优行为", colors=(100, 255, 100))
    decision = this.event_manager.trigger_event('ai_core', this, 'decide',
                                                 chara_id='0', context=context)
    
    this.console.PRINT(f"  角色ID: {decision.get('chara_id', '0')}")
    this.console.PRINT(f"  角色名: {decision.get('chara_name', '未知')}")
    this.console.PRINT(f"  选择行为: {decision.get('action_name', '未知')}")
    this.console.PRINT(f"  时间消耗: {decision.get('time_cost', 0)}分")
    this.console.PRINT(f"  花销评分: {decision.get('cost_score', 0):.2f}")
    this.console.PRINT(f"  决策理由: {decision.get('reasoning', '')}")
    this.console.PRINT(f"  优先级: {decision.get('priority', 0)}")
    
    # 测试4：处理所有角色的AI决策
    this.console.PRINT("\n【测试4】处理所有角色的AI决策（除主角外）", colors=(100, 255, 100))
    
    all_decisions = this.event_manager.trigger_event('ai_core', this, 'process_all',
                                                      context=context, exclude_ids=['0'])
    
    if all_decisions:
        this.console.PRINT(f"  共处理了 {len(all_decisions)} 个角色的决策：")
        
        for i, decision in enumerate(all_decisions, 1):
            this.console.PRINT(f"  [{i}] {decision.get('chara_name', '未知'):8s} -> "
                              f"{decision.get('action_name', '未知'):12s} | "
                              f"时间:{decision.get('time_cost', 0):4.0f}分 | "
                              f"理由:{decision.get('reasoning', '')}")
    else:
        this.console.PRINT("  没有其他角色需要处理")
    
    # 测试5：处理时间步长
    this.console.PRINT("\n【测试5】模拟主角执行30分钟操作时，其他角色的行动", 
                      colors=(100, 255, 100))
    
    time_step_results = this.event_manager.trigger_event('ai_core', this, 'time_step',
                                                          time_cost=30, context=context, 
                                                          exclude_ids=['0'])
    
    if time_step_results:
        this.console.PRINT(f"  其他角色共执行了 {len(time_step_results)} 次行动：")
        
        # 统计每个角色的行为
        action_summary = {}
        for result in time_step_results:
            chara_name = result['decision'].get('chara_name', '未知')
            action_name = result['decision'].get('action_name', '未知')
            
            if chara_name not in action_summary:
                action_summary[chara_name] = {}
            if action_name not in action_summary[chara_name]:
                action_summary[chara_name][action_name] = 0
            action_summary[chara_name][action_name] += 1
        
        # 输出统计结果
        for chara_name, actions in action_summary.items():
            actions_str = ', '.join([f"{act}({count}次)" for act, count in actions.items()])
            this.console.PRINT(f"  {chara_name:8s}: {actions_str}")
    
    # 测试6：获取主角可执行的行为列表
    this.console.PRINT("\n【测试6】获取主角当前可执行的所有行为", colors=(100, 255, 100))
    
    available_actions = this.event_manager.trigger_event('cost_calculator', this, 'available',
                                                          chara_id='0')
    
    if available_actions:
        this.console.PRINT(f"  主角当前可执行 {len(available_actions)} 种行为：")
        
        for action in available_actions:
            this.console.PRINT(f"  - {action.get('action_name', '未知'):12s} | "
                              f"时间:{action.get('time_cost', 0):4.0f}分 | "
                              f"体力:{action.get('stamina_cost', 0):4d} | "
                              f"精力:{action.get('energy_cost', 0):4d} | "
                              f"灵力:{action.get('spirit_cost', 0):4d}")
    
    this.console.PRINT("\n=== AI机测试完成 ===", colors=(255, 255, 100))


# 注册事件触发器
event_test_ai.event_trigger = "test_ai"


def event_ai_status(this):
    """
    显示所有角色的AI状态
    
    Trigger ID: ai_status
    
    显示内容包括：
    - 角色当前状态（体力、精力、灵力）
    - 角色当前决定的行为
    - 角色行为的理由
    """
    this.console.PRINT("=== 角色AI状态 ===", colors=(255, 255, 100))
    
    # 获取当前上下文
    # 尝试从时间控制事件获取准确的时间信息
    try:
        time_info = this.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        if time_info and isinstance(time_info, dict):
            hour = time_info.get('HOUR', 12)
            weekday = time_info.get('WEEKDAY', 1)
        else:
            # 如果获取失败，从全局变量获取
            system_key = this.console.init.global_key.get('System', {})
            hour = system_key.get('HOUR', 12)
            weekday = system_key.get('WEEKDAY', 1)
    except Exception as e:
        # 如果调用失败，从全局变量获取
        system_key = this.console.init.global_key.get('System', {})
        hour = system_key.get('HOUR', 12)
        weekday = system_key.get('WEEKDAY', 1)
    
    # 从天气系统获取当前天气
    try:
        weather_info = this.event_manager.trigger_event('weather_system', this, 'get')
        current_weather = weather_info.get('weather', '晴') if weather_info else '晴'
    except Exception:
        system_key = this.console.init.global_key.get('System', {})
        current_weather = system_key.get('WEATHER', '晴')
    
    context = {
        'weather': current_weather,
        'hour': hour,
        'weekday': weekday
    }
    
    this.console.PRINT(f"当前时间: {context['hour']}时, 天气: {context['weather']}\n", 
                      colors=(200, 200, 255))
    
    # 获取所有角色的决策
    all_decisions = this.event_manager.trigger_event('ai_core', this, 'process_all',
                                                      context=context)
    
    if not all_decisions:
        this.console.PRINT("没有角色可显示状态", colors=(255, 100, 100))
        return
    
    # 显示每个角色的状态
    for decision in all_decisions:
        chara_id = decision.get('chara_id', '0')
        chara_name = decision.get('chara_name', '未知')
        action_name = decision.get('action_name', '未知')
        time_cost = decision.get('time_cost', 0)
        reasoning = decision.get('reasoning', '')
        
        # 获取角色属性
        chara_state = this.console.allstate.get(chara_id)
        if chara_state:
            attributes = chara_state.get('attributes', {})
            stamina = attributes.get('体力', 0)
            stamina_max = attributes.get('体力上限', 100)
            energy = attributes.get('精力', 0)
            energy_max = attributes.get('精力上限', 100)
            spirit = attributes.get('灵力', 0)
            spirit_max = attributes.get('灵力上限', 100)
            
            stamina_percent = int(stamina / stamina_max * 100) if stamina_max > 0 else 0
            energy_percent = int(energy / energy_max * 100) if energy_max > 0 else 0
            spirit_percent = int(spirit / spirit_max * 100) if spirit_max > 0 else 0
            
            # 根据百分比选择颜色
            stamina_color = (100, 255, 100) if stamina_percent > 50 else (255, 255, 100) if stamina_percent > 20 else (255, 100, 100)
            energy_color = (100, 255, 100) if energy_percent > 50 else (255, 255, 100) if energy_percent > 20 else (255, 100, 100)
            spirit_color = (100, 255, 100) if spirit_percent > 50 else (255, 255, 100) if spirit_percent > 20 else (255, 100, 100)
            
            this.console.PRINT(f"【{chara_name}】(ID: {chara_id})", colors=(200, 200, 255))
            this.console.PRINT(f"  状态: 体力 {stamina:3d}/{stamina_max:3d} ({stamina_percent:3d}%)", 
                              colors=stamina_color)
            this.console.PRINT(f"        精力 {energy:3d}/{energy_max:3d} ({energy_percent:3d}%)", 
                              colors=energy_color)
            this.console.PRINT(f"        灵力 {spirit:3d}/{spirit_max:3d} ({spirit_percent:3d}%)", 
                              colors=spirit_color)
            this.console.PRINT(f"  行为: {action_name} (预计消耗{time_cost}分钟)")
            this.console.PRINT(f"  理由: {reasoning}")
            this.console.PRINT("")
    
    this.console.PRINT("=== 角色AI状态结束 ===", colors=(255, 255, 100))


# 注册事件触发器
event_ai_status.event_trigger = "ai_status"


def event_ai_info(this):
    """
    显示AI机系统信息
    
    Trigger ID: ai_info
    
    显示AI机的工作原理和设计思路
    """
    this.console.PRINT("=== 角色AI机系统说明 ===", colors=(255, 255, 100))
    
    this.console.PRINT("\n【设计原理】", colors=(100, 255, 100))
    this.console.PRINT("根据Pera幻想FOD设计思路：")
    this.console.PRINT("- 每次master执行操作时，角色们也会进行行动计算")
    this.console.PRINT("- 根据当前花销计算当前花销最小的行为是什么")
    this.console.PRINT("- 角色也可以和真人一样行动")
    this.console.PRINT("- 把时间拆分成基础时间单位进行迭代计算")
    
    this.console.PRINT("\n【花销计算】", colors=(100, 255, 100))
    this.console.PRINT("- 根据角色基础值计算每天花销")
    this.console.PRINT("- 每个操作的花销存储在全局变量中")
    this.console.PRINT("- 花销根据状态、天气、相性等因素动态变化")
    this.console.PRINT("- 要睡觉状态所有行动花销×2")
    
    this.console.PRINT("\n【AI决策因素】", colors=(100, 255, 100))
    this.console.PRINT("- 花销成本（体力、精力、灵力消耗）")
    this.console.PRINT("- 时间成本")
    this.console.PRINT("- 角色当前状态")
    this.console.PRINT("- 角色行为偏好（探索/战斗/社交/保守）")
    this.console.PRINT("- 时间段修正（早晨/白天/傍晚/夜晚）")
    this.console.PRINT("- 地牢修正（地牢内探索优先）")
    
    this.console.PRINT("\n【可用行为】", colors=(100, 255, 100))
    this.console.PRINT("- 休息: 恢复体力精力")
    this.console.PRINT("- 探索: 获得经验，可能发现物品")
    this.console.PRINT("- 战斗: 获得经验，可能受伤")
    this.console.PRINT("- 社交: 提升好感信赖")
    this.console.PRINT("- 地牢探索: 可能获得战利品")
    this.console.PRINT("- 地牢战斗: 获得战利品")
    this.console.PRINT("- 小地图移动: 移动到邻近地点（2分钟）")
    this.console.PRINT("- 大地图移动: 移动到大地图（10分钟）")
    this.console.PRINT("- 商店交易: 购买或出售物品")
    this.console.PRINT("- 睡觉: 恢复所有状态，进入次日（8小时）")
    
    this.console.PRINT("\n【使用方法】", colors=(100, 255, 100))
    this.console.PRINT("1. 触发 test_ai 事件：查看AI决策演示")
    this.console.PRINT("2. 触发 ai_status 事件：查看所有角色当前状态")
    this.console.PRINT("3. 在其他事件中调用 AI系统：")
    this.console.PRINT("   - cost_calculator 事件：计算花销")
    this.console.PRINT("   - ai_core 事件：处理AI决策")
    
    this.console.PRINT("\n=== 角色AI机系统说明结束 ===", colors=(255, 255, 100))


# 注册事件触发器
event_ai_info.event_trigger = "ai_info"
