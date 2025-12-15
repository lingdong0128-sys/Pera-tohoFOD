def event_reload(things):
    """
    重载所有事件脚本
    """
    things.console.PRINT_DIVIDER()
    things.console.PRINT("正在执行热重载序列...", colors=(255, 255, 0))

    try:
        # 调用我们刚才修改过的 load_events，并传入 True
        things.event_manager.load_events(is_reload=True)

        things.console.PRINT("系统更新完毕。", colors=(0, 255, 0))
    except Exception as e:
        things.console.PRINT(f"致命错误: 重载失败 - {e}", colors=(255, 0, 0))
        import traceback
        traceback.print_exc()  # 在控制台打印详细报错

    things.console.PRINT_DIVIDER()
    things.console.INPUT()  # 暂停一下让你看结果


# 设置触发器，你可以设为 'reload' 或者 'debug'
event_reload.event_trigger = "reload"
