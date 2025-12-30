"""
时间控制系统测试事件
用于验证时间控制功能是否正常工作
"""


def event_test_time(this):
    """
    时间控制测试事件
    Trigger ID: test_time
    
    提供交互式的时间控制测试界面
    """
    running = True
    
    while running:
        # 获取当前时间信息
        time_str = this.event_manager.trigger_event('time_control', this, 'get', format_type='string')
        weekday = this.event_manager.trigger_event('time_control', this, 'get', format_type='weekday')
        festival = this.event_manager.trigger_event('time_control', this, 'get', format_type='festival')
        total_minutes = this.event_manager.trigger_event('time_control', this, 'get_minutes')
        
        # 显示当前时间
        this.console.PRINT_DIVIDER("=")
        this.console.PRINT("【时间控制系统测试】", colors=(255, 200, 100))
        this.console.PRINT_DIVIDER("-")
        this.console.PRINT(f"当前时间：{time_str}")
        this.console.PRINT(f"节日信息：{festival}")
        this.console.PRINT(f"总分钟数：{total_minutes}")
        this.console.PRINT_DIVIDER("-")
        
        # 显示操作菜单
        this.console.PRINT(
            this.cs("[1] 增加30分钟").click("1"), "    ",
            this.cs("[2] 增加1小时").click("2"), "    ",
            this.cs("[3] 增加1天").click("3"), "    ",
            this.cs("[4] 增加到新年").click("4")
        )
        this.console.PRINT(
            this.cs("[5] 设置特定时间").click("5"), "    ",
            this.cs("[6] 查看标准格式").click("6"), "    ",
            this.cs("[7] 查看紧凑格式").click("7"), "    ",
            this.cs("[0] 退出测试").click("0")
        )
        this.console.PRINT_DIVIDER("=")
        
        # 获取输入
        choice = this.console.INPUT()
        
        if choice == '0':
            running = False
            this.console.PRINT("测试结束，返回主菜单。", colors=(100, 255, 100))
            
        elif choice == '1':
            # 增加30分钟
            result = this.event_manager.trigger_event('time_control', this, 'add', minutes=30)
            this.console.PRINT(f"已增加30分钟，当前时间：{result['YEAR']}年{result['MONTH']}月{result['DAY']}日 {result['HOUR']}时{result['MINUTE']}分", 
                              colors=(100, 255, 100))
            this.console.INPUT()
            
        elif choice == '2':
            # 增加1小时
            result = this.event_manager.trigger_event('time_control', this, 'add', hours=1)
            this.console.PRINT(f"已增加1小时，当前时间：{result['YEAR']}年{result['MONTH']}月{result['DAY']}日 {result['HOUR']}时{result['MINUTE']}分", 
                              colors=(100, 255, 100))
            this.console.INPUT()
            
        elif choice == '3':
            # 增加1天
            result = this.event_manager.trigger_event('time_control', this, 'add', days=1)
            this.console.PRINT(f"已增加1天，当前时间：{result['YEAR']}年{result['MONTH']}月{result['DAY']}日 {result['HOUR']}时{result['MINUTE']}分", 
                              colors=(100, 255, 100))
            this.console.INPUT()
            
        elif choice == '4':
            # 增加到新年（设置到第2年1月1日）
            result = this.event_manager.trigger_event('time_control', this, 'set', year=2, month=1, day=1, hour=0, minute=0)
            this.console.PRINT(f"已设置到新年，当前时间：{result['YEAR']}年{result['MONTH']}月{result['DAY']}日 {result['HOUR']}时{result['MINUTE']}分", 
                              colors=(255, 200, 100))
            # 检查是否是节日
            festival = this.event_manager.trigger_event('time_control', this, 'get', format_type='festival')
            this.console.PRINT(f"{festival}", colors=(255, 255, 100))
            this.console.INPUT()
            
        elif choice == '5':
            # 设置特定时间
            this.console.PRINT("请输入要设置的时间（格式：年-月-日-时-分，如：2-1-1-8-0）", colors=(200, 200, 255))
            time_input = this.console.INPUT()
            try:
                parts = time_input.split('-')
                if len(parts) == 5:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    hour = int(parts[3])
                    minute = int(parts[4])
                    result = this.event_manager.trigger_event('time_control', this, 'set', year=year, month=month, day=day, hour=hour, minute=minute)
                    this.console.PRINT(f"时间已设置：{result['YEAR']}年{result['MONTH']}月{result['DAY']}日 {result['HOUR']}时{result['MINUTE']}分", 
                                      colors=(100, 255, 100))
                    this.console.INPUT()
                else:
                    this.console.PRINT("格式错误，请使用 年-月-日-时-分 格式", colors=(255, 100, 100))
                    this.console.INPUT()
            except ValueError:
                this.console.PRINT("输入无效，请输入数字", colors=(255, 100, 100))
                this.console.INPUT()
            
        elif choice == '6':
            # 查看标准格式
            time_info = this.event_manager.trigger_event('time_control', this, 'get', format_type='standard')
            this.console.PRINT("【标准格式数据】", colors=(200, 200, 255))
            this.console.PRINT(f"年: {time_info['YEAR']}")
            this.console.PRINT(f"月: {time_info['MONTH']}")
            this.console.PRINT(f"日: {time_info['DAY']}")
            this.console.PRINT(f"时: {time_info['HOUR']}")
            this.console.PRINT(f"分: {time_info['MINUTE']}")
            this.console.PRINT(f"星期: {time_info['WEEKDAY']}")
            this.console.PRINT(f"总分钟数: {time_info['TOTAL_MINUTES']}")
            this.console.PRINT(f"当前节日: {time_info['CURRENT_FESTIVAL']}")
            this.console.INPUT()
            
        elif choice == '7':
            # 查看紧凑格式
            compact = this.event_manager.trigger_event('time_control', this, 'get', format_type='compact')
            this.console.PRINT(f"紧凑格式：{compact}", colors=(200, 200, 255))
            this.console.INPUT()


# 注册事件触发器
event_test_time.event_trigger = "test_time"
event_test_time.event_name = "时间控制测试"
