"""
示例事件：H场景交互
展示如何调用各种H系口上接口
"""
from utils.era_handler import EraKojoHandler


def event_示例_H场景(this):
    """H场景交互 - 调用各种H系口上"""
    
    # 构建口上上下文
    state = this.event_manager.trigger_event('get_context_state', this)
    kojo_context = {
        'TARGET': this.console.init.charaters_key['0'].get('选择对象'),
        'PLAYER': state['session'].get('master_id', '0'),
        '_RAW_STATE': state
    }
    
    # 使用EraKojoHandler获取MASTER ID
    kojo = EraKojoHandler(this.console, kojo_context)
    master_id = kojo.MASTER
    
    # 获取当前选择对象
    target_id = this.console.init.charaters_key['0'].get('选择对象')
    if not target_id:
        this.console.PRINT("你还没有选择对象哦！", colors=(255, 100, 100))
        return
    
    # 检查不能选择MASTER作为对象
    if target_id == master_id:
        this.console.PRINT("不能选择自己作为互动对象！", colors=(255, 100, 100))
        return
    
    target_name = this.console.init.charaters_key[target_id].get('全名', '未知')
    
    # 开始H
    this.console.PRINT(f"开始与 {target_name} 的亲密时光...", colors=(255, 200, 200))
    this.event_manager.trigger_event('H_开始', this)
    
    while True:
        this.console.PRINT(f"\n=== H互动选项 ===", colors=(255, 200, 200))
        this.console.PRINT(
            this.cs("[1]接吻").click("1"), "      ",
            this.cs("[2]爱抚").click("2"), "      ",
            this.cs("[3]高潮").click("3"), "      ",
            this.cs("[0]结束").click("0")
        )
        
        choice = this.console.INPUT()
        
        if choice == '1':
            # 调用接吻口上
            this.event_manager.trigger_event('H_接吻', this)
        elif choice == '2':
            # 调用爱抚口上
            this.event_manager.trigger_event('H_爱抚', this)
        elif choice == '3':
            # 调用高潮口上
            this.event_manager.trigger_event('H_高潮', this)
        elif choice == '0':
            # 调用结束口上
            this.event_manager.trigger_event('H_结束', this)
            break


event_示例_H场景.event_trigger = '示例_H场景'
