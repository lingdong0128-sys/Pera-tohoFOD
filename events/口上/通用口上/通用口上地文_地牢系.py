"""
通用口上地文 - 地牢系
包含各种地牢/战斗场景的默认口上
当找不到特定角色的地牢口上时会回退到这里
"""
from utils.era_handler import EraKojoHandler
from events.珠计算 import (
    add_mental_palam,
    add_negative_palam,
    get_palam_info
)


def event_common_地牢_遭遇敌人(this):
    """通用遭遇敌人口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 100)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}进入了警戒状态！", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「小心！有敌人！」", colors=COL_TALK)

    # 遭遇敌人时增加少量恐怖
    add_mental_palam(this, kojo.TARGET, '恐怖', 10)
    this.console.PRINT(f"（恐怖+10）", colors=COL_DESC)

    this.console.INPUT()


event_common_地牢_遭遇敌人.event_trigger = 'common_地牢_遭遇敌人'


def event_common_地牢_胜利(this):
    """通用战斗胜利口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 100)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}松了一口气。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「太好了，赢了！」", colors=COL_TALK)

    # 胜利时降低恐怖，增加习得
    favor = kojo.CFLAG.get('好感度', 0)
    add_mental_palam(this, kojo.TARGET, '習得', 30)
    if favor >= 100:
        # 高好感时还会增加恭顺
        add_mental_palam(this, kojo.TARGET, '恭順', 10)
        this.console.PRINT(f"（习得+30，恭顺+10）", colors=COL_DESC)
    else:
        this.console.PRINT(f"（习得+30）", colors=COL_DESC)

    this.console.INPUT()


event_common_地牢_胜利.event_trigger = 'common_地牢_胜利'


def event_common_地牢_失败(this):
    """通用战斗失败口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 150, 150)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}瘫坐在地上，喘息着。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「可恶...不甘心...」", colors=COL_TALK)

    # 失败时增加恐怖和抑郁
    add_negative_palam(this, kojo.TARGET, '抑鬱', 30)
    add_mental_palam(this, kojo.TARGET, '恐怖', 20)
    this.console.PRINT(f"（抑郁+30，恐怖+20）", colors=(255, 150, 150))

    this.console.INPUT()


event_common_地牢_失败.event_trigger = 'common_地牢_失败'


def event_common_地牢_受伤(this):
    """通用受伤口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 200, 100)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}捂住伤口，眉头紧皱。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「痛...但我还能战斗！」", colors=COL_TALK)

    # 受伤时增加苦痛和恐怖
    add_mental_palam(this, kojo.TARGET, '苦痛', 25)
    add_mental_palam(this, kojo.TARGET, '恐怖', 15)
    this.console.PRINT(f"（苦痛+25，恐怖+15）", colors=(255, 200, 150))

    this.console.INPUT()


event_common_地牢_受伤.event_trigger = 'common_地牢_受伤'


def event_common_地牢_发现宝箱(this):
    """通用发现宝箱口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 100)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}兴奋地指着前方。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「看！那里有个宝箱！」", colors=COL_TALK)
    this.console.INPUT()


event_common_地牢_发现宝箱.event_trigger = 'common_地牢_发现宝箱'


def event_common_地牢_休息(this):
    """通用休息口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (200, 255, 200)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}坐下来休息。", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「呼...稍微恢复一下体力吧。」", colors=COL_TALK)
    this.console.INPUT()


event_common_地牢_休息.event_trigger = 'common_地牢_休息'


def event_common_地牢_同行属性判定(this):
    """
    地牢同行属性判定接口
    在地牢主事件每次操作时调用，用于赋予同行属性
    返回同行属性列表
    """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)
    
    # 默认无同行属性
    companion_attributes = []
    
    # 获取角色ID
    char_id = kojo.TARGET
    
    # 这里可以根据角色ID返回不同的同行属性
    # 具体实现由角色差分口上覆盖
    
    return companion_attributes


event_common_地牢_同行属性判定.event_trigger = 'common_地牢_同行属性判定'
