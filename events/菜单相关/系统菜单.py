def event_系统菜单(this):
    """
    [系统菜单循环]
    """
    while True:
        this.console.PRINT_DIVIDER("=")
        this.console.PRINT("【 系 统 菜 单 】", colors=(100, 255, 255))
        this.console.PRINT_DIVIDER("-")
        
        this.console.PRINT(
            this.cs("[20] 💾 保存世界").click("20"), "    ", 
            this.cs("[21] 📂 读取世界").click("21")
        )
        this.console.PRINT(
            this.cs("[44] 🔄 重载事件").click("44"), "    ",
            this.cs("[99] ↩️ 返回").click("99")
        )
        this.console.PRINT("")
        
        # 独立的输入等待
        sys_input = this.console.INPUT()
        
        if sys_input == '99':
            break # 退出系统菜单循环
            
        elif sys_input == '20':
            this.event_manager.trigger_event('system_save', this)
            
        elif sys_input == '21':
            # 读档后通常需要直接跳出所有循环，重新加载
            # 但这里我们先做简单处理
            this.event_manager.trigger_event('system_load', this)
            break # 读档后退出菜单
            
        elif sys_input == '44':
            this.event_manager.trigger_event('reload', this)
            
        # 其他未定义输入
        else:
            pass
event_系统菜单.event_trigger = "系统菜单"