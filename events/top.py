def event_top(this):
    this.console.PRINT('[44]点我到顶',click='44')
    if this.input == '44':
        this.console.loader.scroll_to_top()
event_top.event_id = "top"
event_top.event_name = "测试事件"
event_top.event_trigger = "44"