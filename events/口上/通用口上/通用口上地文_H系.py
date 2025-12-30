"""
通用口上地文 - H系
包含各种H场景的默认口上
当找不到特定角色的H口上时会回退到这里
集成珠计算系统，H行为会增加珠并触发高潮判定
"""
from utils.era_handler import EraKojoHandler
from events.珠计算 import (
    add_pleasure_palam,
    add_mental_palam,
    add_goodwill_palam,
    get_palam_info,
    PALAM_PLEASURE
)


def event_common_H_开始(this):
    """
    通用H开始口上
    初始化H场景，重置相关状态
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)
    COL_DESC = (170, 170, 170)

    favor = kojo.CFLAG.get('好感度', 0)
    love = kojo.CFLAG.get('爱意', 0)

    if love >= 100:
        this.console.PRINT(f"{call_name}脸颊泛红：「{master_name}...我、我已经准备好了...」", colors=COL_TALK)
    elif favor >= 200:
        this.console.PRINT(f"{call_name}有些害羞：「{master_name}，那个...可以吗？」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}轻声说道：「{master_name}...请温柔一点...」", colors=COL_TALK)
    
    # 显示当前快感状态
    this.console.PRINT("")
    this.console.PRINT_DIVIDER("-")
    this.console.PRINT("【当前快感状态】", colors=(255, 255, 150))
    
    # 显示各部位珠信息
    for part, palam_id in PALAM_PLEASURE.items():
        info = get_palam_info(this, kojo.TARGET, palam_id)
        next_display = info['next_level_required'] if info['next_level_required'] is not None else info['current_palam']
        this.console.PRINT(f"  {part}部位: Lv.{info['level']} ({info['current_palam']}/{next_display})", 
                          colors=(200, 200, 255))
    
    this.console.INPUT()


event_common_H_开始.event_trigger = 'common_H_开始'


def event_common_H_高潮(this):
    """
    通用高潮口上
    触发高潮时的表现，增加恥情和欲情珠
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 150, 150)

    # 增加精神系珠（高潮时增加恥情和欲情）
    add_mental_palam(this, kojo.TARGET, '恥情', 100)
    add_mental_palam(this, kojo.TARGET, '欲情', 50)

    this.console.PRINT(f"{call_name}：「啊...啊啊...！」", colors=COL_TALK)
    this.console.PRINT(f"{call_name}整个人都颤抖着。", colors=(170, 170, 170))
    this.console.INPUT()


event_common_H_高潮.event_trigger = 'common_H_高潮'


def event_common_H_接吻(this):
    """
    通用接吻口上
    增加好意珠和恭順珠
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)

    favor = kojo.CFLAG.get('好感度', 0)

    # 增加好意珠和恭順珠
    add_goodwill_palam(this, kojo.TARGET, '好意', 30)
    add_mental_palam(this, kojo.TARGET, '恭順', 20)

    if favor >= 200:
        this.console.PRINT(f"{call_name}闭上眼睛，温柔地回应着。", colors=(170, 170, 170))
        this.console.PRINT("（好意+30，恭順+20）", colors=(150, 255, 150))
    else:
        this.console.PRINT(f"{call_name}有些不知所措。", colors=(170, 170, 170))
        this.console.PRINT("（好意+20，恭順+10）", colors=(150, 255, 150))

    this.console.INPUT()


event_common_H_接吻.event_trigger = 'common_H_接吻'


def event_common_H_爱抚(this):
    """
    通用爱抚口上
    增加各部位快感珠（根据当前爱抚的部位）
    增加恥情珠
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)
    COL_GAIN = (150, 255, 150)

    # 增加恥情珠
    shame_result = add_mental_palam(this, kojo.TARGET, '恥情', 30)
    
    # 默认增加C部位珠（可根据TEQUIP判断实际爱抚部位）
    # 这里简化处理，统一增加C部位珠
    pleasure_result = add_pleasure_palam(this, kojo.TARGET, 'C', 50)

    this.console.PRINT(f"{call_name}：「嗯...{call_name}...」", colors=COL_TALK)
    
    # 显示珠的获得信息
    if pleasure_result:
        part_name = 'C'
        gain_text = f"快{part_name}+{pleasure_result['gain']} (Lv.{pleasure_result['level']})"
        this.console.PRINT(f"  {gain_text}", colors=COL_GAIN)
        
        # 如果触发高潮
        if pleasure_result['is_climax']:
            this.console.PRINT(f"  ⚠ 触发高潮！", colors=(255, 100, 100))
            this.console.PRINT(f"  该部位第 {pleasure_result['climax_count']} 次高潮", colors=(255, 150, 150))

    this.console.INPUT()


event_common_H_爱抚.event_trigger = 'common_H_爱抚'


def event_common_H_结束(this):
    """
    通用H结束口上
    显示本次H的最终状态
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)
    COL_DESC = (170, 170, 170)

    love = kojo.CFLAG.get('爱意', 0)

    # 增加恭順珠（H结束时的余韵）
    add_mental_palam(this, kojo.TARGET, '恭順', 40)
    add_goodwill_palam(this, kojo.TARGET, '好意', 20)

    if love >= 100:
        this.console.PRINT(f"{call_name}依偎在你怀里：「{master_name}...我好幸福...」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}喘息着：「哈...哈...{master_name}...」", colors=COL_TALK)
    
    # 显示最终状态
    this.console.PRINT("")
    this.console.PRINT_DIVIDER("-")
    this.console.PRINT("【本次H后的状态】", colors=(255, 255, 150))
    
    # 显示各部位珠信息
    for part, palam_id in PALAM_PLEASURE.items():
        info = get_palam_info(this, kojo.TARGET, palam_id)
        climax_count = info['climax_count']
        this.console.PRINT(f"  快{part}: Lv.{info['level']} (高潮{climax_count}次)", 
                          colors=(200, 200, 255))
    
    # 显示总高潮次数
    total_climax = kojo.CFLAG.get('总高潮次数', 0)
    this.console.PRINT(f"  总高潮次数: {total_climax}", colors=(255, 200, 200))

    this.console.INPUT()


event_common_H_结束.event_trigger = 'common_H_结束'
