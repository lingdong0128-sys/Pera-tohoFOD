"""
通用口上地文 - 地牢系
包含各种地牢/战斗场景的默认口上
当找不到特定角色的地牢口上时会回退到这里
"""
from utils.era_handler import EraKojoHandler


def event_common_地牢_遭遇敌人(this):
    """通用遭遇敌人口上"""
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    call_name = kojo.CALLNAME

    COL_TALK = (255, 255, 100)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(f"{call_name}进入了警戒状态！", colors=COL_DESC)
    this.console.PRINT(f"{call_name}：「小心！有敌人！」", colors=COL_TALK)
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
