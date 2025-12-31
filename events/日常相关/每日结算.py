"""
每日结算事件
实现角色每日结算逻辑，包括睡眠判定、晕厥判定、进入次日等

根据设计思路：
- 正常来说角色在自宅时可以提供进入下一天选项
- 主角结算的时候其他角色也能活动
- 需要处理睡眠、晕厥判定
"""


def event_daily_settlement(this, **kwargs):
    """
    [事件] 每日结算
    
    Trigger ID: daily_settlement
    
    支持的操作:
        - 'check': 检查是否可以进行结算
        - 'settle': 执行每日结算
        - 'check_faint': 检查角色晕厥状态
        - 'check_sleep': 检查角色睡眠状态
    
    Args:
        this: 事件上下文对象
        **kwargs: 操作参数
    
    Returns:
        操作结果
    """
    operation = kwargs.get('operation', 'check')
    
    if operation == 'check':
        # 检查是否可以进行结算
        return _check_can_settle(this)
    
    elif operation == 'settle':
        # 执行每日结算
        return _execute_daily_settlement(this)
    
    elif operation == 'check_faint':
        # 检查角色晕厥状态
        chara_id = kwargs.get('chara_id', '0')
        return _check_character_faint(this, chara_id)
    
    elif operation == 'check_sleep':
        # 检查角色睡眠状态
        chara_id = kwargs.get('chara_id', '0')
        return _check_character_sleep(this, chara_id)
    
    else:
        return {'success': False, 'message': f'未知操作: {operation}'}


def _check_can_settle(this) -> dict:
    """
    检查是否可以进行结算
    
    结算条件：
    1. 主角在自宅位置
    2. 时间较晚（建议22:00之后）
    3. 没有正在进行的战斗或地牢探索
    
    Returns:
        结算可行性检查结果
    """
    console = this.console
    init = console.init
    
    # 获取主角位置
    current_big = console.charater_pwds.get('0', {}).get('大地图')
    current_small = console.charater_pwds.get('0', {}).get('小地图')
    
    # 获取当前时间
    try:
        time_info = console.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        current_hour = time_info.get('HOUR', 0) if isinstance(time_info, dict) else 0
    except Exception:
        current_hour = 0
    
    # 检查主角状态
    chara_state = console.allstate.get('0')
    if not chara_state:
        return {
            'can_settle': False,
            'reason': '主角数据不存在',
            'current_time': current_hour
        }
    
    # 检查是否在自宅（假设小地图0为自宅）
    is_at_home = (current_small == '0' or current_small == '自宅')
    
    # 检查时间（建议22:00之后）
    is_late_night = current_hour >= 22
    
    # 检查是否在地牢中
    is_in_dungeon = current_small.startswith('D') or 'dungeon' in current_small.lower()
    
    # 检查主角状态（体力是否过低）
    attributes = chara_state.get('attributes', {})
    stamina_ratio = attributes.get('体力', 100) / max(attributes.get('体力上限', 100), 1)
    is_exhausted = stamina_ratio < 0.1
    
    # 汇总结果
    can_settle = is_at_home and not is_in_dungeon
    
    # 生成提示信息
    messages = []
    if is_at_home:
        messages.append('当前在自宅')
    else:
        messages.append('当前不在自宅')
    
    if is_late_night:
        messages.append('时间较晚，建议休息')
    else:
        messages.append(f'当前时间为{current_hour}点')
    
    if is_in_dungeon:
        messages.append('在地牢中无法结算')
    
    if is_exhausted:
        messages.append('体力严重不足，建议立即休息')
    
    return {
        'can_settle': can_settle,
        'reason': '\n'.join(messages),
        'current_time': current_hour,
        'is_at_home': is_at_home,
        'is_late_night': is_late_night,
        'is_in_dungeon': is_in_dungeon,
        'is_exhausted': is_exhausted
    }


def _execute_daily_settlement(this) -> dict:
    """
    执行每日结算
    
    处理流程：
    1. 检查所有角色状态
    2. 处理晕厥判定
    3. 处理睡眠判定
    4. 更新日期
    5. 更新天气
    6. 主线剧情判定
    
    Returns:
        结算结果
    """
    console = this.console
    init = console.init
    
    # 1. 检查所有角色状态
    faint_list = []
    sleep_list = []
    
    for chara_id in init.chara_ids:
        chara_state = console.allstate.get(chara_id)
        if not chara_state:
            continue
        
        # 检查晕厥
        faint_result = _check_character_faint(this, chara_id)
        if faint_result.get('is_fainted'):
            faint_list.append({
                'id': chara_id,
                'name': chara_state.get('name', '未知'),
                'reason': faint_result.get('reason')
            })
            # 执行晕厥处理
            _handle_faint(this, chara_id)
        
        # 检查睡眠
        sleep_result = _check_character_sleep(this, chara_id)
        if sleep_result.get('should_sleep'):
            sleep_list.append({
                'id': chara_id,
                'name': chara_state.get('name', '未知'),
                'reason': sleep_result.get('reason')
            })
            # 执行睡眠恢复
            _handle_sleep(this, chara_id)
    
    # 2. 更新日期
    _advance_to_next_day(this)
    
    # 3. 更新天气
    _update_weather(this)
    
    # 4. 珠转换：将好意珠转换为好感信赖
    _convert_palam(this)
    
    # 5. 主线剧情判定（简化处理，后续扩展）
    story_event = _check_main_story(this)
    
    return {
        'success': True,
        'message': '每日结算完成',
        'fainted_characters': faint_list,
        'slept_characters': sleep_list,
        'story_event': story_event
    }


def _check_character_faint(this, chara_id: str) -> dict:
    """
    检查角色是否晕厥
    
    晕厥条件：
    1. 体力归零
    2. 精力归零
    3. 特定异常状态（如重伤未治疗）
    
    Args:
        this: 事件上下文对象
        chara_id: 角色ID
    
    Returns:
        晕厥检查结果
    """
    chara_state = this.console.allstate.get(chara_id)
    if not chara_state:
        return {'is_fainted': False}
    
    attributes = chara_state.get('attributes', {})
    stamina = attributes.get('体力', 0)
    energy = attributes.get('精力', 0)
    
    # 检查异常状态
    abnormal_states = chara_state.get('abnormal_states', {})
    has_critical_state = any([
        abnormal_states.get('重伤', 0) > 0,
        abnormal_states.get('极度疲劳', 0) > 0
    ])
    
    reasons = []
    is_fainted = False
    
    if stamina <= 0:
        reasons.append('体力耗尽')
        is_fainted = True
    
    if energy <= 0:
        reasons.append('精力耗尽')
        is_fainted = True
    
    if has_critical_state:
        reasons.append('状态危急')
        is_fainted = True
    
    return {
        'is_fainted': is_fainted,
        'reason': '、'.join(reasons) if reasons else '无',
        'stamina': stamina,
        'energy': energy
    }


def _check_character_sleep(this, chara_id: str) -> dict:
    """
    检查角色是否需要睡眠
    
    睡眠条件：
    1. 时间较晚（22:00之后）
    2. 体力低于30%
    3. 精力低于30%
    4. CFLAG睡眠状态触发
    
    Args:
        this: 事件上下文对象
        chara_id: 角色ID
    
    Returns:
        睡眠检查结果
    """
    # 获取当前时间
    try:
        time_info = this.console.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        current_hour = time_info.get('HOUR', 0) if isinstance(time_info, dict) else 0
    except Exception:
        current_hour = 0
    
    chara_state = this.console.allstate.get(chara_id)
    if not chara_state:
        return {'should_sleep': False}
    
    attributes = chara_state.get('attributes', {})
    cflags = chara_state.get('cflags', {})
    
    stamina_max = attributes.get('体力上限', 100)
    stamina = attributes.get('体力', 100)
    energy_max = attributes.get('精力上限', 100)
    energy = attributes.get('精力', 100)
    
    stamina_ratio = stamina / max(stamina_max, 1)
    energy_ratio = energy / max(energy_max, 1)
    
    reasons = []
    should_sleep = False
    
    # 检查CFLAG睡眠状态
    sleep_flag = cflags.get(1, 0)  # 假设CFLAG:1是睡眠状态
    if sleep_flag >= 1:
        reasons.append('想要睡觉')
        should_sleep = True
    
    # 检查时间
    if current_hour >= 22:
        reasons.append('时间较晚')
        should_sleep = True
    
    # 检查体力精力
    if stamina_ratio < 0.3:
        reasons.append('体力不足')
        should_sleep = True
    
    if energy_ratio < 0.3:
        reasons.append('精力不足')
        should_sleep = True
    
    return {
        'should_sleep': should_sleep,
        'reason': '、'.join(reasons) if reasons else '无',
        'current_hour': current_hour,
        'stamina_ratio': stamina_ratio,
        'energy_ratio': energy_ratio
    }


def _handle_faint(this, chara_id: str):
    """
    处理角色晕厥
    
    晕厥效果：
    1. 传送回自宅
    2. 恢复部分状态
    3. 添加晕厥标记
    4. 扣除金钱或物品（作为惩罚）
    
    Args:
        this: 事件上下文对象
        chara_id: 角色ID
    """
    console = this.console
    chara_state = console.allstate.get(chara_id)
    
    if not chara_state:
        return
    
    # 1. 传送回自宅
    from events.移动 import event_强制移动
    event_强制移动(this, chara_id, '自宅', '0')
    
    # 2. 恢复部分状态
    attributes = chara_state.get('attributes', {})
    stamina_max = attributes.get('体力上限', 100)
    energy_max = attributes.get('精力上限', 100)
    spirit_max = attributes.get('灵力上限', 100)
    
    attributes['体力'] = int(stamina_max * 0.3)  # 恢复到30%
    attributes['精力'] = int(energy_max * 0.3)
    attributes['灵力'] = int(spirit_max * 0.3)
    
    # 3. 添加晕厥标记
    abnormal_states = chara_state.get('abnormal_states', {})
    abnormal_states['晕厥'] = 1
    
    # 4. 扣除金钱（简化处理）
    money = chara_state.get('money', 0)
    lost_money = min(money, 100)  # 最多损失100
    chara_state['money'] = money - lost_money
    
    # 5. 记录日志
    if chara_id == '0':
        console.PRINT(f"因{abnormal_states.get('晕厥原因', '体力耗尽')}而晕厥，被送回自宅", colors=(255, 100, 100))
        console.PRINT(f"恢复到最低状态，损失{lost_money}金钱", colors=(255, 200, 100))


def _handle_sleep(this, chara_id: str):
    """
    处理角色睡眠
    
    睡眠效果：
    1. 完全恢复体力、精力、灵力
    2. 消除疲劳状态
    3. 时间跳跃（8小时）
    
    Args:
        this: 事件上下文对象
        chara_id: 角色ID
    """
    console = this.console
    chara_state = console.allstate.get(chara_id)
    
    if not chara_state:
        return
    
    # 1. 完全恢复状态
    attributes = chara_state.get('attributes', {})
    stamina_max = attributes.get('体力上限', 100)
    energy_max = attributes.get('精力上限', 100)
    spirit_max = attributes.get('灵力上限', 100)
    
    attributes['体力'] = stamina_max
    attributes['精力'] = energy_max
    attributes['灵力'] = spirit_max
    
    # 2. 消除疲劳状态
    abnormal_states = chara_state.get('abnormal_states', {})
    abnormal_states['疲劳'] = 0
    abnormal_states['极度疲劳'] = 0
    
    # 3. 清除睡眠标记
    cflags = chara_state.get('cflags', {})
    cflags[1] = 0  # 清除睡眠状态
    
    # 4. 记录日志（仅主角）
    if chara_id == '0':
        console.PRINT("进入睡眠，状态完全恢复", colors=(100, 255, 100))


def _advance_to_next_day(this):
    """
    推进到下一天
    
    更新日期、星期等信息
    """
    # 调用time_control事件增加时间（跳过到次日）
    try:
        # 计算到次日的时间
        time_info = this.console.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        
        if isinstance(time_info, dict):
            current_hour = time_info.get('HOUR', 0)
            hours_to_next_day = 24 - current_hour
            
            # 增加时间到次日
            this.console.event_manager.trigger_event(
                'time_control',
                this,
                'add',
                hours=hours_to_next_day
            )
    except Exception as e:
        print(f'日期更新失败: {e}')


def _update_weather(this):
    """
    更新天气
    
    使用天气系统事件更新天气
    """
    # 调用天气系统事件更新天气
    try:
        weather_result = this.console.event_manager.trigger_event(
            'weather_system',
            this,
            'update'
        )
        
        if weather_result and weather_result.get('success'):
            # 记录天气变化
            if '0' in this.console.charater_pwds:
                # 仅当主角存在时显示天气信息
                this.console.PRINT(
                    f"天气变化：{weather_result.get('old_weather')} -> {weather_result.get('new_weather')} ({weather_result.get('weather_name')})",
                    colors=(100, 200, 255)
                )
            
            return weather_result
    except Exception as e:
        print(f'天气更新失败: {e}')
        return None


def _convert_palam(this):
    """
    珠转换：将好意珠转换为好感信赖
    
    根据设计思路：
    - 每日结算时将好意珠转换为好感信赖
    - 转换比例根据好意等级判断
    - 等级0-1：10:1，等级2-3：5:1，等级4+：3:1
    """
    try:
        # 调用珠计算事件的每日结算转换函数
        this.console.event_manager.trigger_event('每日结算_珠转换', this)
    except Exception as e:
        print(f'珠转换失败: {e}')


def _check_main_story(this) -> dict:
    """
    主线剧情判定
    
    根据当前日期、完成进度等触发主线剧情事件
    简化处理，后续扩展
    
    Args:
        this: 事件上下文对象
    
    Returns:
        主线剧情事件信息
    """
    # 获取当前日期
    try:
        time_info = this.console.event_manager.trigger_event(
            'time_control',
            this,
            'get',
            format_type='standard'
        )
        
        if isinstance(time_info, dict):
            day = time_info.get('DAY', 1)
            
            # 简化：在第7天、14天、21天触发特殊事件
            if day in [7, 14, 21]:
                return {
                    'triggered': True,
                    'type': 'main_story',
                    'day': day,
                    'message': f'第{day}天，可能发生了什么事...'
                }
        
    except Exception:
        pass
    
    return {
        'triggered': False
    }


# 注册事件触发器
event_daily_settlement.event_trigger = "daily_settlement"
