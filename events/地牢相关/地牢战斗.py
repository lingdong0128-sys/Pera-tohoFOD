"""
地牢战斗事件系统
根据Pera幻想FOD设计思路实现地牢战斗逻辑
- 被动遇敌和主动攻击
- 回合制战斗系统
- 情欲值计算（使用珠计算系统）
- 异常状态处理
- 战斗结算
"""

from utils.era_handler import EraKojoHandler
from .地牢数值化 import event_dungeon_get_stat
from .异常状态处理 import event_abnormal_add, event_abnormal_apply_end_effects
from events.珠计算 import add_pleasure_palam, get_palam_info


# ========================
# 战斗状态管理
# ========================

def event_battle_initialize(this, monster_data, chara_id=None):
    """
    初始化战斗状态
    
    参数:
        this: 事件上下文
        monster_data: 怪物数据字典
        chara_id: 参与战斗的角色ID，默认为当前选择的目标角色
    
    返回:
        bool: 初始化是否成功
    """
    # 确定参与战斗的角色
    if chara_id is None:
        # 从当前选择的目标角色获取
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 初始化战斗状态存储在全局
    if 'dungeon_battle' not in this.console.allstate:
        this.console.allstate['dungeon_battle'] = {}
    
    # 创建kojo上下文用于获取ASSI等信息
    from utils.era_handler import EraKojoHandler
    context = {'TARGET': chara_id}
    kojo = EraKojoHandler(this.console, context)
    
    # 获取同行角色（助手）
    assi_list = kojo.ASSI if kojo.ASSI else []
    
    # 构建战斗状态
    battle_state = {
        'turn': 1,
        'chara_id': chara_id,
        'assi_list': assi_list,
        'monster': {
            'id': monster_data['id'],
            'name': monster_data['name'],
            'type': monster_data['type'],
            'trait': monster_data['trait'],
            'attack_power': monster_data['attack_power'],
            'defense': monster_data['defense'],
            'stamina': monster_data['current_stamina'],
            'max_stamina': monster_data['stamina'],
            'skills': monster_data['skills'],
            'drops': monster_data['drops'],
            'abnormal_states': monster_data.get('abnormal_states', [])
        },
        'is_player_turn': True,
        'battle_log': []
    }
    
    # 存储战斗状态
    this.console.allstate['dungeon_battle'][chara_id] = battle_state
    
    # 添加战斗日志
    this.console.PRINT(f"\n====== 战斗开始 ======", colors=(255, 255, 255))
    this.console.PRINT(f"遭遇 {monster_data['name']}！", colors=(255, 100, 100))
    this.console.PRINT(f"怪物体力: {monster_data['current_stamina']}/{monster_data['stamina']}", colors=(200, 200, 200))
    
    return True


def event_battle_get_state(this, chara_id=None):
    """
    获取战斗状态
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        dict: 战斗状态，如果不存在则返回None
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    return this.console.allstate.get('dungeon_battle', {}).get(chara_id)


def event_battle_end(this, chara_id=None):
    """
    结束战斗，清除战斗状态
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if battle_state:
        this.console.PRINT(f"\n====== 战斗结束 ======", colors=(255, 255, 255))
        del this.console.allstate['dungeon_battle'][chara_id]


# ========================
# 战斗行动
# ========================

def event_battle_player_attack(this, skill_id=None, chara_id=None):
    """
    玩家（或同行角色）攻击怪物
    
    参数:
        skill_id: 使用的技能ID，None表示普通攻击
        chara_id: 攻击者的角色ID，默认为当前选择的目标角色
    
    返回:
        dict: 攻击结果
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return {'success': False, 'message': '战斗不存在'}
    
    monster = battle_state['monster']
    
    # 获取角色地牢属性：攻击力
    attack_power = event_dungeon_get_stat(this, 0, chara_id)  # 0=攻击力
    
    # 获取技能倍率
    skill_multiplier = 1.0  # 默认普通攻击倍率
    if skill_id:
        skill_data = this.console.init.global_key.get('技能', {}).get(skill_id)
        if skill_data:
            # 技能数据格式：ID,名称,类型,消耗属性,消耗数值,情欲倍率,效果描述,异常状态ID
            # 情欲倍率在索引5
            skill_multiplier = int(skill_data[5].strip()) / 100.0
    
    # 计算伤害（对怪物体力的伤害）
    base_damage = attack_power * skill_multiplier
    damage = int(base_damage)
    
    # 应用伤害
    monster['stamina'] = max(0, monster['stamina'] - damage)
    
    # 构建攻击结果
    result = {
        'success': True,
        'damage': damage,
        'monster_stamina': monster['stamina'],
        'monster_max_stamina': monster['max_stamina'],
        'skill_id': skill_id
    }
    
    # 显示攻击结果
    chara_name = this.console.init.charaters_key.get(chara_id, {}).get('全名', '你')
    skill_name = "普通攻击" if not skill_id else this.console.init.global_key.get('技能', {}).get(skill_id, [skill_id])[1]
    
    this.console.PRINT(f"\n{chara_name} 使用 {skill_name}！", colors=(100, 200, 255))
    this.console.PRINT(f"对 {monster['name']} 造成了 {damage} 点伤害", colors=(255, 255, 100))
    this.console.PRINT(f"怪物剩余体力: {monster['stamina']}/{monster['max_stamina']}", colors=(200, 200, 200))
    
    # 判断是否击败怪物
    if monster['stamina'] <= 0:
        result['monster_defeated'] = True
        this.console.PRINT(f"{monster['name']} 被击败了！", colors=(100, 255, 100))
    else:
        result['monster_defeated'] = False
    
    return result


def event_battle_monster_attack(this, chara_id=None):
    """
    怪物攻击角色（造成情欲值增加）
    
    参数:
        chara_id: 被攻击的角色ID，默认为当前选择的目标角色
    
    返回:
        dict: 攻击结果
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return {'success': False, 'message': '战斗不存在'}
    
    monster = battle_state['monster']
    
    # 获取角色地牢属性：防御力
    defense = event_dungeon_get_stat(this, 1, chara_id)  # 1=防御力
    
    # 计算怪物攻击力（扣除防御）
    base_attack = max(10, monster['attack_power'] - defense // 2)
    
    # 随机浮动（0.8~1.2倍）
    import random
    multiplier = random.uniform(0.8, 1.2)
    actual_attack = int(base_attack * multiplier)
    
    # 转换为情欲值（H游戏风格，攻击转化为快感）
    pleasure_gain = actual_attack
    
    # 增加角色快感珠（C部位，基础获得量）
    palam_result = add_pleasure_palam(this, chara_id, 'C', pleasure_gain)
    
    # 构建攻击结果
    result = {
        'success': True,
        'attack_power': actual_attack,
        'pleasure_gain': pleasure_gain,
        'pleasure_level': palam_result['level'],
        'is_climax': palam_result['is_climax'],
        'climax_count': palam_result['climax_count']
    }
    
    # 显示攻击结果
    chara_name = this.console.init.charaters_key.get(chara_id, {}).get('全名', '你')
    this.console.PRINT(f"\n{monster['name']} 发起了攻击！", colors=(255, 100, 100))
    this.console.PRINT(f"对 {chara_name} 造成了快感！", colors=(255, 150, 200))
    this.console.PRINT(f"快C等级: {palam_result['level']}", colors=(255, 200, 200))
    
    # 判定是否高潮
    if palam_result['is_climax']:
        this.console.PRINT(f"{chara_name} 达到了高潮！", colors=(255, 100, 255))
        
        # 高潮后检查是否败北（情欲值过高）
        if palam_result['climax_count'] >= 3:  # 连续3次高潮则败北
            result['chara_defeated'] = True
            this.console.PRINT(f"{chara_name} 已经无法继续战斗了...", colors=(255, 0, 0))
        else:
            result['chara_defeated'] = False
    else:
        result['chara_defeated'] = False
    
    return result


def event_battle_monster_ai(this, chara_id=None):
    """
    怪物AI：决定怪物使用什么技能
    
    参数:
        chara_id: 当前角色ID
    
    返回:
        str: 使用的技能ID，None表示普通攻击
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return None
    
    monster = battle_state['monster']
    skills = monster.get('skills', [])
    
    # 如果没有技能，使用普通攻击
    if not skills:
        return None
    
    # 简单AI：随机选择技能
    import random
    return random.choice(skills)


# ========================
# 回合管理
# ========================

def event_battle_next_turn(this, chara_id=None):
    """
    进入下一回合
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        dict: 新回合状态
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return {'success': False, 'message': '战斗不存在'}
    
    # 增加回合数
    battle_state['turn'] += 1
    battle_state['is_player_turn'] = True
    
    # 回合开始：应用异常状态的持续效果
    this.console.PRINT(f"\n====== 第 {battle_state['turn']} 回合 ======", colors=(200, 200, 255))
    
    # 应用异常状态效果
    event_abnormal_apply_end_effects(this, chara_id)
    
    return {
        'success': True,
        'turn': battle_state['turn'],
        'is_player_turn': battle_state['is_player_turn']
    }


def event_battle_check_end_condition(this, chara_id=None):
    """
    检查战斗是否结束
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        dict: {
            'is_end': bool,  # 战斗是否结束
            'result': str,  # 'victory'/'defeat'/None
        }
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return {'is_end': True, 'result': None}
    
    monster = battle_state['monster']
    
    # 检查怪物是否被击败
    if monster['stamina'] <= 0:
        return {'is_end': True, 'result': 'victory'}
    
    # 检查角色是否败北（高潮3次或更多）
    chara_info = get_palam_info(this, chara_id, '0')  # '0'=快C的珠ID
    climax_count_key = '0_高潮次数'
    
    context = {'TARGET': chara_id}
    kojo = EraKojoHandler(this.console, context)
    climax_count = int(kojo.CFLAG.get(climax_count_key, 0))
    
    # 在单次战斗中，累计高潮次数超过3次则败北
    # 可以在战斗状态中记录本次战斗的高潮次数
    if 'battle_climax_count' not in battle_state:
        battle_state['battle_climax_count'] = 0
    
    if battle_state['battle_climax_count'] >= 3:
        return {'is_end': True, 'result': 'defeat'}
    
    return {'is_end': False, 'result': None}


# ========================
# 战斗主循环
# ========================

def event_dungeon_battle_main(this, monster_data, chara_id=None):
    """
    地牢战斗主事件（主循环）
    
    参数:
        monster_data: 怪物数据字典
        chara_id: 参与战斗的角色ID，默认为当前选择的目标角色
    
    返回:
        str: 战斗结果 'victory'/'defeat'/None（战斗未完成）
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 初始化战斗
    event_battle_initialize(this, monster_data, chara_id)
    
    # 战斗主循环
    while True:
        battle_state = event_battle_get_state(this, chara_id)
        
        # 检查战斗结束条件
        end_condition = event_battle_check_end_condition(this, chara_id)
        if end_condition['is_end']:
            event_battle_end(this, chara_id)
            return end_condition['result']
        
        # 玩家回合
        if battle_state['is_player_turn']:
            this.console.PRINT(f"\n【你的回合】", colors=(100, 255, 100))
            this.console.PRINT("1. 攻击", colors=(200, 200, 200))
            this.console.PRINT("2. 逃跑", colors=(200, 200, 200))
            
            # 获取玩家输入
            choice = this.console.INPUT("请选择行动: ", choices=['1', '2'])
            
            if choice == '1':
                # 攻击
                attack_result = event_battle_player_attack(this, None, chara_id)
                
                if attack_result['monster_defeated']:
                    event_battle_end(this, chara_id)
                    return 'victory'
                
                # 玩家攻击成功，增加战斗高潮计数（如果本轮高潮了）
                if 'is_climax' in attack_result and attack_result['is_climax']:
                    battle_state['battle_climax_count'] = battle_state.get('battle_climax_count', 0) + 1
            
            elif choice == '2':
                # 逃跑
                this.console.PRINT("你尝试逃跑...", colors=(200, 200, 200))
                import random
                if random.random() < 0.5:  # 50%逃跑成功率
                    this.console.PRINT("逃跑成功！", colors=(100, 255, 100))
                    event_battle_end(this, chara_id)
                    return None  # 中断战斗
                else:
                    this.console.PRINT("逃跑失败！", colors=(255, 100, 100))
        
        # 怪物回合
        else:
            this.console.PRINT(f"\n【怪物回合】", colors=(255, 100, 100))
            
            # 怪物AI决定技能
            skill_id = event_battle_monster_ai(this, chara_id)
            
            # 怪物攻击
            monster_result = event_battle_monster_attack(this, chara_id)
            
            if monster_result['chara_defeated']:
                event_battle_end(this, chara_id)
                return 'defeat'
            
            # 增加战斗高潮计数
            if monster_result['is_climax']:
                battle_state['battle_climax_count'] = battle_state.get('battle_climax_count', 0) + 1
        
        # 切换回合
        battle_state['is_player_turn'] = not battle_state['is_player_turn']
        
        # 如果轮到玩家回合，进入下一回合（应用异常状态效果）
        if battle_state['is_player_turn']:
            event_battle_next_turn(this, chara_id)


# ========================
# 被动遇敌和主动攻击
# ========================

def event_dungeon_passive_encounter(this, room_data, chara_id=None):
    """
    被动遇敌（进入房间时遭遇怪物）
    
    参数:
        room_data: 房间数据（包含monster字段）
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        str: 战斗结果 'victory'/'defeat'/None
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    # 检查房间是否有怪物
    if not room_data.get('monster'):
        return None
    
    monster_data = room_data['monster']
    
    # 判定怪物特点
    monster_trait = monster_data['trait']  # 0=伪装, 1=善良, 2=邪恶
    
    # 善良怪物可能不会攻击
    if monster_trait == 1:
        this.console.PRINT(f"你遇到了 {monster_data['name']}，它看起来没有敌意。", colors=(100, 255, 100))
        return None
    
    # 邪恶怪物直接进入战斗
    if monster_trait == 2:
        this.console.PRINT(f"你遇到了 {monster_data['name']}，它向你发起了攻击！", colors=(255, 100, 100))
        return event_dungeon_battle_main(this, monster_data, chara_id)
    
    # 伪装怪物需要判定
    if monster_trait == 0:
        import random
        if random.random() < 0.3:  # 30%概率识破伪装
            this.console.PRINT(f"你识破了 {monster_data['name']} 的伪装！", colors=(255, 255, 100))
            return event_dungeon_battle_main(this, monster_data, chara_id)
        else:
            this.console.PRINT(f"你遇到了 {monster_data['name']}，看起来很友善。", colors=(100, 255, 100))
            return None
    
    return None


def event_dungeon_active_attack(this, monster_data, chara_id=None):
    """
    主动攻击（玩家主动选择攻击房间里的怪物）
    
    参数:
        monster_data: 怪物数据字典
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        str: 战斗结果 'victory'/'defeat'/None
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    this.console.PRINT(f"你主动向 {monster_data['name']} 发起了攻击！", colors=(255, 255, 100))
    return event_dungeon_battle_main(this, monster_data, chara_id)


# ========================
# 战斗结算
# ========================

def event_battle_victory_rewards(this, chara_id=None):
    """
    战斗胜利结算（掉落物品）
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        list: 获得的物品ID列表
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return []
    
    monster = battle_state['monster']
    drops = monster.get('drops', [])
    
    received_items = []
    
    for item_id in drops:
        # 50%概率掉落
        import random
        if random.random() < 0.5:
            # 创建handler并添加物品
            context = {'TARGET': chara_id}
            kojo = EraKojoHandler(this.console, context)
            kojo.ITEM_ADD(item_id, 1, chara_id)
            received_items.append(item_id)
    
    if received_items:
        this.console.PRINT(f"战斗胜利！获得了物品。", colors=(100, 255, 100))
    else:
        this.console.PRINT("战斗胜利！但没有获得任何物品。", colors=(200, 200, 200))
    
    return received_items


def event_battle_defeat_hscene(this, chara_id=None):
    """
    战斗失败结算（触发H场景）
    
    参数:
        chara_id: 角色ID，默认为当前选择的目标角色
    
    返回:
        bool: 是否成功处理H场景
    """
    if chara_id is None:
        chara_id = this.console.init.charaters_key.get('0', {}).get('选择对象', '0')
    
    battle_state = event_battle_get_state(this, chara_id)
    if not battle_state:
        return False
    
    monster = battle_state['monster']
    
    this.console.PRINT(f"\n被 {monster['name']} 完全压制了...", colors=(255, 100, 100))
    this.console.PRINT("即将触发H场景...", colors=(255, 150, 200))
    this.console.INPUT()
    
    # TODO: 这里应该触发H场景事件
    # 可以根据怪物类型调用不同的H场景
    # 暂时只是提示
    
    this.console.PRINT(f"[H场景待实现] {monster['name']} 的H场景", colors=(255, 200, 255))
    
    return True


# ========================
# 事件接口（供其他事件调用）
# ========================

event_dungeon_battle_main.event_trigger = '地牢战斗'


def event_进入房间_遇敌(this, room_data, chara_id=None):
    """
    事件接口：进入房间时的被动遇敌判定
    调用方式: this.event_manager.trigger_event('进入房间_遇敌', this, room_data)
    
    参数:
        room_data: 房间数据字典
        chara_id: 角色ID
    
    返回:
        str: 战斗结果
    """
    return event_dungeon_passive_encounter(this, room_data, chara_id)

event_进入房间_遇敌.event_trigger = '进入房间_遇敌'


def event_主动攻击(this, monster_data, chara_id=None):
    """
    事件接口：主动攻击怪物
    调用方式: this.event_manager.trigger_event('主动攻击', this, monster_data)
    
    参数:
        monster_data: 怪物数据字典
        chara_id: 角色ID
    
    返回:
        str: 战斗结果
    """
    return event_dungeon_active_attack(this, monster_data, chara_id)

event_主动攻击.event_trigger = '主动攻击'


def event_战斗胜利(this, chara_id=None):
    """
    事件接口：战斗胜利结算
    调用方式: this.event_manager.trigger_event('战斗胜利', this)
    
    参数:
        chara_id: 角色ID
    
    返回:
        list: 获得的物品ID列表
    """
    return event_battle_victory_rewards(this, chara_id)

event_战斗胜利.event_trigger = '战斗胜利'


def event_战斗失败(this, chara_id=None):
    """
    事件接口：战斗失败结算（触发H场景）
    调用方式: this.event_manager.trigger_event('战斗失败', this)
    
    参数:
        chara_id: 角色ID
    
    返回:
        bool: 是否成功处理
    """
    return event_battle_defeat_hscene(this, chara_id)

event_战斗失败.event_trigger = '战斗失败'
