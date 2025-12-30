"""
通用口上地文 - H系
包含各种H场景的默认口上
当找不到特定角色的H口上时会回退到这里
"""
from utils.era_handler import EraKojoHandler


def event_common_H_开始(this):
    """通用H开始口上"""
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

    this.console.INPUT()


event_common_H_开始.event_trigger = 'common_H_开始'


def event_common_H_高潮(this):
    """通用高潮口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 150, 150)

    this.console.PRINT(f"{call_name}：「啊...啊啊...！」", colors=COL_TALK)
    this.console.PRINT(f"{call_name}整个人都颤抖着。", colors=(170, 170, 170))
    this.console.INPUT()


event_common_H_高潮.event_trigger = 'common_H_高潮'


def event_common_H_接吻(this):
    """通用接吻口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)

    favor = kojo.CFLAG.get('好感度', 0)

    if favor >= 200:
        this.console.PRINT(f"{call_name}闭上眼睛，温柔地回应着。", colors=(170, 170, 170))
    else:
        this.console.PRINT(f"{call_name}有些不知所措。", colors=(170, 170, 170))

    this.console.INPUT()


event_common_H_接吻.event_trigger = 'common_H_接吻'


def event_common_H_爱抚(this):
    """通用爱抚口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)

    this.console.PRINT(f"{call_name}：「嗯...{call_name}...」", colors=COL_TALK)
    this.console.INPUT()


event_common_H_爱抚.event_trigger = 'common_H_爱抚'


def event_common_H_结束(this):
    """通用H结束口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 200)
    COL_DESC = (170, 170, 170)

    love = kojo.CFLAG.get('爱意', 0)

    if love >= 100:
        this.console.PRINT(f"{call_name}依偎在你怀里：「{master_name}...我好幸福...」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}喘息着：「哈...哈...{master_name}...」", colors=COL_TALK)

    this.console.INPUT()


event_common_H_结束.event_trigger = 'common_H_结束'
