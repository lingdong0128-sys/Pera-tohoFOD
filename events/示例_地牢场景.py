"""
示例事件：地牢冒险场景
展示如何调用各种地牢系口上接口
"""
from utils.era_handler import EraKojoHandler


def event_示例_地牢场景(this):
    """地牢冒险场景 - 调用各种地牢系口上"""
    
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
    
    # 遭遇敌人
    this.console.PRINT(f"进入地牢深处...", colors=(255, 255, 100))
    this.event_manager.trigger_event('地牢_遭遇敌人', this)
    
    # 模拟战斗
    this.console.PRINT("\n战斗中...", colors=(200, 200, 200))
    this.console.PRINT(
        this.cs("[1]模拟胜利").click("1"), "      ",
        this.cs("[2]模拟失败").click("2"), "      ",
        this.cs("[3]模拟受伤").click("3"), "      ",
        this.cs("[4]模拟发现宝箱").click("4"), "      ",
        this.cs("[5]休息").click("5")
    )
    
    choice = this.console.INPUT()
    
    if choice == '1':
        # 调用胜利口上
        this.event_manager.trigger_event('地牢_胜利', this)
    elif choice == '2':
        # 调用失败口上
        this.event_manager.trigger_event('地牢_失败', this)
    elif choice == '3':
        # 调用受伤口上
        this.event_manager.trigger_event('地牢_受伤', this)
    elif choice == '4':
        # 调用发现宝箱口上
        this.event_manager.trigger_event('地牢_发现宝箱', this)
    elif choice == '5':
        # 调用休息口上
        this.event_manager.trigger_event('地牢_休息', this)


event_示例_地牢场景.event_trigger = '示例_地牢场景'


def event_示例_地牢战斗(this):
    """完整的地牢战斗流程示例"""
    
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
    
    target_id = this.console.init.charaters_key['0'].get('选择对象')
    if not target_id:
        this.console.PRINT("你还没有选择对象哦！", colors=(255, 100, 100))
        return
    
    # 检查不能选择MASTER作为对象
    if target_id == master_id:
        this.console.PRINT("不能选择自己作为互动对象！", colors=(255, 100, 100))
        return
    
    target_name = this.console.init.charaters_key[target_id].get('全名', '未知')
    
    # 1. 遭遇敌人
    this.console.PRINT(f"在黑暗的地牢中，{target_name}发现了敌人的踪迹！", colors=(255, 255, 100))
    this.event_manager.trigger_event('地牢_遭遇敌人', this)
    
    this.console.INPUT()
    
    # 2. 战斗过程
    this.console.PRINT("激烈的战斗开始了...", colors=(200, 200, 200))
    
    # 随机决定战斗结果
    import random
    result = random.randint(1, 3)
    
    if result == 1:
        # 胜利
        this.console.PRINT("你成功击败了敌人！", colors=(100, 255, 100))
        this.event_manager.trigger_event('地牢_胜利', this)
        
        # 可能发现宝箱
        if random.random() > 0.5:
            this.event_manager.trigger_event('地牢_发现宝箱', this)
    elif result == 2:
        # 受伤但获胜
        this.console.PRINT("你击败了敌人，但受了伤...", colors=(255, 200, 100))
        this.event_manager.trigger_event('地牢_受伤', this)
        this.event_manager.trigger_event('地牢_胜利', this)
    else:
        # 失败
        this.console.PRINT("你被敌人击败了...", colors=(255, 100, 100))
        this.event_manager.trigger_event('地牢_失败', this)
    
    this.console.INPUT()
    
    # 3. 战斗后可以选择休息
    this.console.PRINT("\n是否休息一下恢复体力？")
    this.console.PRINT(
        this.cs("[1]休息").click("1"), "      ",
        this.cs("[0]继续").click("0")
    )
    
    rest_choice = this.console.INPUT()
    
    if rest_choice == '1':
        this.event_manager.trigger_event('地牢_休息', this)
        this.console.PRINT("体力恢复了！", colors=(100, 255, 100))


event_示例_地牢战斗.event_trigger = '示例_地牢战斗'
