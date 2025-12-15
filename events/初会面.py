def event_初会面检查(this):
    # 1. 确保状态已构建
    if not getattr(this.console, 'allstate', None):
        this.event_manager.trigger_event('build_state', this)
        
    # 2. 调用对象选择获取当前地图的角色
    result = this.event_manager.trigger_event('对象选择', this)
    
    # 安全检查
    if result:
        # 对象选择现在返回3个值: 文本, 图片列表, ID列表
        InOneMapCharater, InOneMapCharaterImg, CharaList = result
    else:
        CharaList = []

    # 3. 遍历当前地图的角色
    for i in CharaList:
        if i == '0': continue
        
        # 获取数据源
        # 建议统一使用 allstate，因为它是最新的状态
        chara_state = this.console.allstate[i]
        data_source = chara_state['data'] 
        
        # [调试代码] 看看这里面到底有啥
        #flag_value = data_source.get('初会面', '未找到')
        #this.console.PRINT(f"DEBUG: 角色{i} 的初会面标志是: {flag_value} (类型: {type(flag_value)})")
        
        # 逻辑判断
        # 必须确保 1 也是 True
        if not data_source.get('初会面'):
            #this.console.PRINT(f"DEBUG: 判定为第一次见面，触发事件...") # 调试用
            
            # 触发事件
            event_name = f"{i}_{data_source.get('口上类型', '初期口上')}_初会面"
            this.event_manager.trigger_event(event_name, this, silent=True)
            
            # [关键] 写入数据
            data_source['初会面'] = 1
            # 同时保险起见，打印一下写入后的结果
            #print(f"已写入: {this.console.allstate[i]['data']['初会面']}")
        else:
            #this.console.PRINT("DEBUG: 已见过面，跳过")
            continue

# 注册触发器
event_初会面检查.event_trigger = "初会面检查"