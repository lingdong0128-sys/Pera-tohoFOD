"""
通用口上地文 - 日常系
包含各种日常场景的默认口上
当找不到特定角色的口上时会回退到这里
"""
from utils.era_handler import EraKojoHandler


def event_common_日常_聊天(this):
    """通用日常聊天口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    # 常用变量定义
    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    target_name = kojo.NAME
    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    # 根据好感度/亲密度选择不同的通用回复
    favor = kojo.CFLAG.get('好感度', 0)

    if favor >= 300:
        this.console.PRINT(f"{call_name}微笑着对你说：「{master_name}，有什么话想跟我说吗？」", colors=COL_TALK)
    elif favor >= 100:
        this.console.PRINT(f"{call_name}看着你：「嗯？{master_name}，找我有事吗？」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}淡淡地说道：「你好，{master_name}。」", colors=COL_TALK)

    this.console.INPUT()


event_common_日常_聊天.event_trigger = 'common_日常_聊天'


def event_common_日常_问候(this):
    """通用问候口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)

    # 根据时间选择不同问候语
    time_of_day = context.get('TIME', '昼')

    if time_of_day == '早晨':
        this.console.PRINT(f"{call_name}：「早安，{master_name}！」", colors=COL_TALK)
    elif time_of_day == '昼':
        this.console.PRINT(f"{call_name}：「你好，{master_name}。」", colors=COL_TALK)
    elif time_of_day == '夜':
        this.console.PRINT(f"{call_name}：「晚上好，{master_name}。」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}：「嗨，{master_name}。」", colors=COL_TALK)

    this.console.INPUT()


event_common_日常_问候.event_trigger = 'common_日常_问候'


def event_common_日常_告别(this):
    """通用告别口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)

    this.console.PRINT(f"{call_name}：「再见了，{master_name}。」", colors=COL_TALK)
    this.console.INPUT()


event_common_日常_告别.event_trigger = 'common_日常_告别'


def event_common_日常_触摸(this):
    """通用触摸口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}：「...诶？突然...」", colors=COL_TALK)
    this.console.INPUT()


event_common_日常_触摸.event_trigger = 'common_日常_触摸'


def event_common_日常_抱住(this):
    """通用抱住口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    favor = kojo.CFLAG.get('好感度', 0)

    if favor >= 200:
        this.console.PRINT(f"{call_name}脸红了，没有推开你：「{master_name}...」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}有些困惑：「{master_name}？这是...？」", colors=COL_TALK)

    this.console.INPUT()


event_common_日常_抱住.event_trigger = 'common_日常_抱住'


def event_common_日常_询问(this):
    """通用询问口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)

    this.console.PRINT(f"{call_name}：「嗯？你想知道什么？」", colors=COL_TALK)
    this.console.INPUT()


event_common_日常_询问.event_trigger = 'common_日常_询问'


def event_common_日常_观察(this):
    """通用观察口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}似乎注意到了你的目光。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「...怎么了？一直看着我。」", colors=COL_TALK)
    this.console.INPUT()


event_common_日常_观察.event_trigger = 'common_日常_观察'


def event_common_日常_邀请(this):
    """通用邀请口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 255)

    favor = kojo.CFLAG.get('好感度', 0)

    if favor >= 200:
        this.console.PRINT(f"{call_name}：「好啊，{master_name}，我们去哪？」", colors=COL_TALK)
    elif favor >= 50:
        this.console.PRINT(f"{call_name}：「嗯...让我考虑一下。好的，走吧。」", colors=COL_TALK)
    else:
        this.console.PRINT(f"{call_name}：「{master_name}，要一起去吗？」", colors=COL_TALK)

    this.console.INPUT()


event_common_日常_邀请.event_trigger = 'common_日常_邀请'
