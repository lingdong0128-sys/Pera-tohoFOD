"""
腐化妖精房间事件
触发方式：进入房间时自动触发
"""


def event_腐化妖精战斗(this, room_data):
    """
    腐化妖精房间事件
    
    参数:
        room_data: 房间数据，包含怪物信息
    """
    # 调用地牢战斗系统的被动遇敌事件
    result = this.event_manager.trigger_event('进入房间_遇敌', this, room_data)
    
    # 根据战斗结果进行处理
    if result == 'victory':
        # 战斗胜利
        this.console.PRINT("\n腐化妖精被打败了，化作点点星光消散...", colors=(200, 200, 100))
        this.console.PRINT("你妖精消散的地方留下了一些东西！", colors=(100, 255, 100))
        
        # 50%概率掉落妖精之尘
        import random
        if random.random() < 0.5:
            from utils.era_handler import EraKojoHandler
            kojo = EraKojoHandler(this.console, {'TARGET': '0'})
            kojo.ITEM_ADD('1002', 1)
            this.console.PRINT("获得了【妖精之尘】！", colors=(255, 255, 100))
    
    elif result == 'defeat':
        # 战斗失败
        this.console.PRINT("\n被腐化妖精彻底魅惑了...", colors=(255, 100, 100))
        this.event_manager.trigger_event('战斗失败', this)
    
    # 如果result是None，表示逃跑或没有发生战斗，正常返回


# 注册事件
event_腐化妖精战斗.event_trigger = "腐化妖精战斗"
event_腐化妖精战斗.is_main_event = True
