import threading
import tkinter as tk
from tools.口上制作器 import KojoEditorApp

def event_open_kojo_maker(this):
    """
    启动口上制作器 GUI (带调试和保底数据版)
    trigger: kojo_maker
    """
    this.console.PRINT("正在启动口上制作工坊...", colors=(100, 255, 100))
    
    init = this.console.init

    # [调试] 打印一下当前加载了哪些全局数据
    print("\n=== DEBUG: Global Keys ===")
    print(list(init.global_key.keys()))
    print("==========================\n")

    # --- [核心] 智能数据提取函数 ---
    def get_data_list(key_hint, default_list=None):
        """
        尝试从 global_key 中提取数据列表。
        如果提取失败，返回 default_list (保底数据)。
        """
        target_data = None
        
        # 1. 模糊查找键名 (忽略大小写)
        if key_hint in init.global_key:
            target_data = init.global_key[key_hint]
        else:
            for k in init.global_key:
                if k.upper() == key_hint.upper():
                    target_data = init.global_key[k]
                    break
        
        # 2. 如果没找到数据，使用保底列表
        if not target_data:
            print(f"⚠️ Warning: 未找到全局数据 '{key_hint}'，使用默认保底数据。")
            return default_list if default_list else []

        # 3. 提取名称列表
        result_list = []
        for val in target_data.values():
            if isinstance(val, dict):
                # 兼容 {ID: {name: 'xxx'}} 格式
                if 'name' in val: result_list.append(str(val['name']))
                elif '全名' in val: result_list.append(str(val['全名']))
            else:
                # 兼容 {ID: 'xxx'} 格式
                result_list.append(str(val))
        
        return list(result_list)

    # --------------------------------
    events_meta = {}
    for event_key, event_func in this.event_manager.events.items():
        events_meta[event_key] = {
            'is_main': getattr(event_func, 'is_main_event', False)
        }
    init.chara_ids=init.chara_ids if init.chara_ids else ['0']
    init.chara_name=[]
    for i in init.chara_ids:
        init.chara_name.append(init.charaters_key[i].get('全名'))
    # 1. 准备元数据 (加入硬编码的默认值，防止下拉框为空)
    game_meta = {
        'ABL': get_data_list('Abl', ['C感觉', 'V感觉', 'A感觉', '技巧', '顺从', '欲望']),
        'TALENT': get_data_list('Talent', ['处女', '恋慕', '淫乱', '性别']),
        'BASE': get_data_list('Base', ['体力', '气力', '理性']),
        'EXP': get_data_list('Exp', ['绝顶经验', '精液经验']),
        'MARK': get_data_list('Mark', ['反发刻印', '快乐刻印']),
        
        # 其他属性
        'CFLAG': ['好感度', '信赖度', '睡眠深度'], 
        'TEQUIP': ['眼罩', '绳子', '跳蛋'],
        'PALAM': ['润滑', '恭顺', '欲情', '屈服', '羞耻', '恐怖'],

        # 角色与图片
        'CHARAS': init.chara_name,
        'IMAGES': list(this.console.image_data.keys()),
        # 事件列表
        'EVENTS': list(this.event_manager.events.keys()),
        'EVENTS_META': events_meta,
    }
    
    # 2. 启动 GUI
    root = tk.Tk()
    # [关键] 窗口置顶，防止被全屏游戏遮挡
    #root.attributes('-topmost', True) 
    
    app = KojoEditorApp(root, game_meta)
    
    def on_close():
        root.destroy()
        this.console.PRINT("口上制作器已关闭。", colors=(150, 150, 150))
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

event_open_kojo_maker.event_trigger = "kojo_maker"
event_open_kojo_maker.is_main_event = False