import os

def event_draw_system_info(this, ctx=None):
    """
    [UI组件] 绘制系统信息区块
    对应 FOD日常菜单 方案一
    功能：读取并显示时间、音乐、腐化、天气、金钱等全局信息
    trigger: draw_system_info
    """
    
    # 1. 获取数据源
    # 如果外部传了 ctx 就用，没传就自己获取
    if not ctx:
        ctx = this.event_manager.trigger_event('get_context_state', this)
    
    # 提取全局变量引用
    g_vars = this.console.init.global_key.get('Variable', {}) # 存 MONEY 等
    g_sys  = this.console.init.global_key.get('System', {})   # 存 TIME, CORRUPTION 等
    
    # 2. 数据准备
    # --- 时间 ---
    year = g_sys.get('YEAR', '2025')
    month = g_sys.get('MONTH', '1')
    day = g_sys.get('DAY', '1')
    weekday = g_sys.get('WEEKDAY', '一') # 建议后续在结算逻辑里写个函数自动计算星期
    time_str = g_sys.get('TIME', '昼')   # 昼/夜/具体时间
    
    # --- 音乐 ---
    music_name = "----"
    if this.console.current_music_name:
        music_name = this.console.current_music_name
    elif this.console.music_box and this.console.music_box.url:
        # 如果没有存名字，从文件名提取
        music_name = os.path.basename(this.console.music_box.url)
        # 去掉扩展名
        music_name = os.path.splitext(music_name)[0]

    # --- 腐化进度 ---
    # 假设 key 为 CORRUPTION，范围 0-100
    try:
        corruption_val = int(g_sys.get('CORRUPTION', 0))
    except:
        corruption_val = 0
        
    # --- 天气 ---
    weather = g_sys.get('WEATHER', '晴')
    
    # --- 金钱 ---
    try:
        money = int(g_vars.get('MONEY', 0))
    except:
        money = 0
        
    # 3. 绘制 UI
    # |系统信息--------------------------------------------
    this.console.PRINT_DIVIDER("-", length=140, colors=(100, 100, 150))
    
    # 第一行：年月日: 音乐: 腐化进度: 星期 天气
    # 使用 this.cs() 进行富文本拼接
    
    # [日期]
    line1 = this.cs(f"{year}年{month}月{day}日").set_color((200, 200, 255)) + "  "
    
    # [音乐] (绿色)
    line1 += this.cs(f"🎵:{music_name}").set_color((150, 255, 150)) + "    "
    
    # [腐化进度] (根据数值变色：安全->警告->危险)
    if corruption_val < 30:
        c_color = (200, 200, 200) # 灰/白
    elif corruption_val < 70:
        c_color = (255, 200, 100) # 橙
    else:
        c_color = (255, 50, 50)   # 红
    line1 += this.cs(f"腐化:{corruption_val}%").set_color(c_color) + "    "
    
    # [星期]
    line1 += this.cs(f"星期{weekday}").set_color((220, 220, 220)) + "  "
    
    # [天气] (黄色)
    line1 += this.cs(f"☀{weather}").set_color((255, 255, 100)) + "  "
    
    # [时段]
    line1 += this.cs(f"[{time_str}]").set_color((100, 200, 255))
    
    this.console.PRINT(line1)
    
    # 第二行：钱持有
    # 格式化金钱：1,234,567
    money_str = f"{money:,}" 
    line2 = this.cs(f"💰持有金: {money_str}").set_color((255, 215, 0)) # 金色
    
    this.console.PRINT(line2)

    # 这里的分割线留给下一个模块（地图信息）去画，或者这里画也行
    # this.console.PRINT_DIVIDER("-", length=140, colors=(50, 50, 50))

# 注册事件
event_draw_system_info.event_trigger = "draw_system_info"