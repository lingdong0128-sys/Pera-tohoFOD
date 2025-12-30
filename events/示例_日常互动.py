"""
示例事件：日常互动菜单
展示如何调用各种日常系口上接口
"""
from utils.era_handler import EraKojoHandler


def event_示例_日常互动(this):
    """日常互动菜单 - 调用各种日常系口上"""
    
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
    
    while True:
        this.console.PRINT(f"\n=== 与 {target_name} 互动 ===", colors=(255, 255, 200))
        this.console.PRINT(
            this.cs("[1]聊天").click("1"), "      ",
            this.cs("[2]问候").click("2"), "      ",
            this.cs("[3]触摸").click("3"), "      ",
            this.cs("[4]抱住").click("4"), "      ",
            this.cs("[5]询问").click("5"), "      ",
            this.cs("[6]观察").click("6"), "      ",
            this.cs("[7]邀请").click("7"), "      ",
            this.cs("[0]退出").click("0")
        )
        
        choice = this.console.INPUT()
        
        if choice == '1':
            # 调用聊天口上（已有事件，这里直接使用）
            this.event_manager.trigger_event('聊天', this)
        elif choice == '2':
            # 调用问候口上
            this.event_manager.trigger_event('日常_问候', this)
        elif choice == '3':
            # 调用触摸口上
            this.event_manager.trigger_event('日常_触摸', this)
        elif choice == '4':
            # 调用抱住口上
            this.event_manager.trigger_event('日常_抱住', this)
        elif choice == '5':
            # 调用询问口上
            this.event_manager.trigger_event('日常_询问', this)
        elif choice == '6':
            # 调用观察口上
            this.event_manager.trigger_event('日常_观察', this)
        elif choice == '7':
            # 调用邀请口上
            this.event_manager.trigger_event('日常_邀请', this)
        elif choice == '0':
            # 调用告别口上
            this.event_manager.trigger_event('日常_告别', this)
            break


event_示例_日常互动.event_trigger = '示例_日常互动'
