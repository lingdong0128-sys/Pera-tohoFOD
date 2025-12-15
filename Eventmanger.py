class EventManager:
    def __init__(self, console_instance):
        self.console = console_instance
        self.events = {}
        self.eventid = {}
        self.call_stack = []
        
        # [新增] 存储事件的元数据（比如是否为主事件）
        # 结构: {'事件名': {'is_main': True, ...}}
        self.events_meta = {} 
        
        self.load_events()

    def load_events(self, is_reload=False):  # [修改1] 增加参数
        """动态加载事件文件"""
        import importlib
        import os
        import sys

        events_dir = "./events"
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)

        if events_dir not in sys.path:
            sys.path.insert(0, events_dir)

        # [修改2] 如果是重载模式，先清空旧的事件字典，防止残留
        if is_reload:
            self.events = {}
            self.eventid = {}
            self.console.PRINT("正在清理旧事件缓存...", colors=(150, 150, 150))

        # 遍历文件
        for root, dirs, files in os.walk(events_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    relative_path = os.path.relpath(root, events_dir)

                    if relative_path == ".":
                        module_name = f"events.{file[:-3]}"
                    else:
                        module_path = relative_path.replace(os.sep, ".")
                        module_name = f"events.{module_path}.{file[:-3]}"

                    try:
                        # [修改3] 核心重载逻辑
                        if is_reload and module_name in sys.modules:
                            # 如果模块已存在，强制重载！
                            module = sys.modules[module_name]
                            module = importlib.reload(module)
                        else:
                            # 第一次加载
                            module = importlib.import_module(module_name)

                        # 重新注册事件函数
                        for attr_name in dir(module):
                            if attr_name.startswith("event_"):
                                event_func = getattr(module, attr_name)
                                event_key = attr_name[6:]
                                event_id = getattr(event_func, 'event_trigger', event_key)
                                
                                # [新增] 读取是否为主事件标记，默认为 False
                                is_main = getattr(event_func, 'is_main_event', False)
                                
                                self.events[event_key] = event_func
                                self.eventid[event_id] = event_key
                                
                                # 存储元数据
                                self.events_meta[event_key] = {
                                    'is_main': is_main
                                }

                                if not is_reload:
                                    # 可以打印出来方便调试
                                    tag = "[主]" if is_main else ""
                                    self.console.PRINT(f"已加载事件: {event_key} {tag}")

                    except Exception as e:
                        self.console.PRINT(
                            f"加载事件失败 {module_name}: {e}", colors=(255, 200, 200))

        if is_reload:
            self.console.PRINT(
                f"重载完成，当前共有 {len(self.events)} 个事件。", colors=(100, 255, 100))

    def trigger_event(self, event_name, things_instance,silent=False):
            if event_name in self.events:
                try:
                    # 记录调用栈
                    self.call_stack.append(event_name)
                    return self.events[event_name](things_instance)
                except Exception as e:
                    # [关键] 打印详细堆栈，而不是简单的“未找到”
                    import traceback
                    error_msg = traceback.format_exc()
                    print(f"❌ 事件 [{event_name}] 运行崩溃:\n{error_msg}") # 打印到终端
                    self.console.PRINT(f"事件运行出错: {e}", colors=(255, 0, 0)) # 打印到游戏
                    return None
                finally:
                    if self.call_stack: self.call_stack.pop()
            else:
                # 只有真的不在字典里，才报未找到
                if not silent:
                    self.console.PRINT(f"未找到事件: {event_name}", colors=(255, 100, 100))
                return None
    def get_save_stack(self):
        """
        [新增] 获取用于存档的事件栈
        只返回那些被标记为 is_main_event=True 的事件
        """
        # 使用列表推导式进行过滤
        # 只有在 events_meta 中记录为 is_main 的事件才会被保留
        return [
            evt for evt in self.call_stack 
            if self.events_meta.get(evt, {}).get('is_main', False)
        ]