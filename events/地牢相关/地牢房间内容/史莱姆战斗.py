"""
史莱姆房间事件
触发方式：进入房间时自动触发
"""


def event_史莱姆战斗(this, room_data):
    """
    史莱姆房间事件
    
    参数:
        room_data: 房间数据，包含怪物信息
    """
    # 调用地牢战斗系统的被动遇敌事件
    result = this.event_manager.trigger_event('进入房间_遇敌', this, room_data)
    
    # 根据战斗结果进行处理
    if result == 'victory':
        # 战斗胜利，给予额外奖励
        this.console.PRINT("\n史莱姆被击败了，房间内布满了黏液...", colors=(200, 200, 100))
        this.console.PRINT("你在黏液中发现了一些有用的材料！", colors=(100, 255, 100))
        
        # 50%概率掉落史莱姆精华
        import random
        if random.random() < 0.5:
            from utils.era_handler import EraKojoHandler
            kojo = EraKojoHandler(this.console, {'TARGET': '0'})
            kojo.ITEM_ADD('1000', 1)
            this.console.PRINT("获得了【史莱姆精华】！", colors=(255, 255, 100))
    
    elif result == 'defeat':
        # 战斗失败
        this.console.PRINT("\n被史莱姆彻底压制了...", colors=(255, 100, 100))
        this.event_manager.trigger_event('战斗失败', this)
    
    # 如果result是None，表示逃跑或没有发生战斗，正常返回


# 注册事件
event_史莱姆战斗.event_trigger = "史莱姆战斗"
event_史莱姆战斗.is_main_event = True
