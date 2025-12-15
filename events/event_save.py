from utils.save import SaveSystem

def event_save_menu(this):
    """
    显示存档菜单
    trigger: system_save
    """
    saver = SaveSystem()
    this.console.PRINT_DIVIDER("=")
    this.console.PRINT("【 存 档 菜 单 】", colors=(255, 255, 0))
    
    # 显示槽位信息
    for i in range(1, 6): # 5个槽位
        info = saver.get_save_info(i)
        if info:
            desc = f"[{i}] {info.get('save_time')} - {info.get('summary')}"
            this.console.PRINT(this.cs(desc).click(str(i)))
        else:
            this.console.PRINT(this.cs(f"[{i}] ---- 空档位 ----").click(str(i)), colors=(150, 150, 150))
    
    this.console.PRINT(this.cs("[99] 返回").click("99"))
    
    # 等待输入
    slot = this.console.INPUT()
    
    if slot == '99':
        return
    
    if slot.isdigit() and 1 <= int(slot) <= 5:
        # 1. 获取当前游戏状态
        current_state = this.event_manager.trigger_event('get_context_state', this)
        
        # 2. 执行保存
        this.console.PRINT("正在保存...", colors=(200, 200, 0))
        if saver.save_game(current_state, slot):
            this.console.PRINT(f"✅ 存档已保存至槽位 {slot}", colors=(100, 255, 100))
        else:
            this.console.PRINT("❌ 存档失败！请检查日志。", colors=(255, 100, 100))
            
    this.console.PRINT("")
    this.console.INPUT() # 按任意键继续

def event_load_menu(this):
    """
    显示读档菜单
    trigger: system_load
    """
    saver = SaveSystem()
    this.console.PRINT_DIVIDER("=")
    this.console.PRINT("【 读 档 菜 单 】", colors=(100, 255, 255))
    
    for i in range(1, 6):
        info = saver.get_save_info(i)
        if info:
            desc = f"[{i}] {info.get('save_time')} - {info.get('summary')}"
            this.console.PRINT(this.cs(desc).click(str(i)))
        else:
            this.console.PRINT(f"[{i}] ---- 空档位 ----", colors=(100, 100, 100))
            
    this.console.PRINT(this.cs("[99] 返回").click("99"))
    
    slot = this.console.INPUT()
    
    if slot == '99':
        return

    if slot.isdigit() and 1 <= int(slot) <= 5:
            raw_data = saver.load_game(slot)
            
            if raw_data:
                this.console.PRINT("正在读取...", colors=(200, 200, 0))
                
                # 1. 注入数据
                this.temp_save_data = raw_data
                this.event_manager.trigger_event('apply_save_data', this)
                
                # 2. [核心] 获取存档时的事件栈
                # 假设结构是 system -> event_stack
                saved_stack = raw_data.get('system', {}).get('event_stack', [])
                
                if saved_stack:
                    # 获取栈顶事件 (最后运行的那个)
                    last_event = saved_stack[-1]
                    
                    this.console.PRINT(f"正在跳转回事件: {last_event} ...", colors=(100, 255, 100))
                    
                    # 3. 强制跳转
                    # 注意：这会开启一个新的调用栈，旧的 start 循环会被抛弃
                    # 如果你想做的更完美，可以清空当前的 event_manager.call_stack
                    this.event_manager.call_stack = [] # 重置栈，防止叠加
                    this.event_manager.trigger_event(last_event, this)
                    
                    # 这里的代码理论上不会执行了，因为 trigger_event 可能会进入死循环
                else:
                    # 如果是旧存档没有栈，默认回 start
                    this.event_manager.trigger_event('start', this)
            else:
                this.console.PRINT("❌ 读取失败：存档文件损坏或为空。", colors=(255, 100, 100))
                this.console.INPUT()

# 注册触发器
event_save_menu.event_trigger = "system_save"
event_load_menu.event_trigger = "system_load"