"""
触手房间事件
触发方式：进入房间时自动触发
"""


def event_触手战斗(this, room_data):
    """
    触手房间事件
    
    参数:
        room_data: 房间数据，包含怪物信息
    """
    # 调用地牢战斗系统的被动遇敌事件
    result = this.event_manager.trigger_event('进入房间_遇敌', this, room_data)
    
    # 根据战斗结果进行处理
    if result == 'victory':
        # 战斗胜利
        this.console.PRINT("\n触手退去了，但房间里还有触手的残肢...", colors=(200, 200, 100))
        this.console.PRINT("你在角落里发现了一些奇怪的材料！", colors=(100, 255, 100))
        
        # 50%概率掉落触手碎片
        import random
        if random.random() < 0.5:
            from utils.era_handler import EraKojoHandler
            kojo = EraKojoHandler(this.console, {'TARGET': '0'})
            kojo.ITEM_ADD('1001', 1)
            this.console.PRINT("获得了【触手碎片】！", colors=(255, 255, 100))
    
    elif result == 'defeat':
        # 战斗失败
        this.console.PRINT("\n被触手彻底缠绕住了...", colors=(255, 100, 100))
        this.event_manager.trigger_event('战斗失败', this)
    
    # 如果result是None，表示逃跑或没有发生战斗，正常返回


# 注册事件
event_触手战斗.event_trigger = "触手战斗"
event_触手战斗.is_main_event = True
