def event_对象选择(this):
    # 1. 确保状态字典已构建 (通用非空检查)
    # 使用 getattr + None 判断，兼容你初始化为 None 或 {} 的情况
    if not getattr(this.console, 'allstate', None):
        # 如果没有状态，先构建 (懒加载)
        this.event_manager.trigger_event('build_state', this)

    # 快捷引用
    all_states = this.console.allstate
    
    # 获取玩家当前位置 (保持原有的位置判断逻辑)
    # 注意：位置数据必须从实时数据源(charater_pwds)获取，因为 state 里的 location 可能是旧的
    player_map = this.charater_pwds.get('0', {}).get('小地图')

    charalist = []
    gradient_text = "       "
    img_list = []

    # 2. 遍历所有角色状态
    for chara_id, state in all_states.items():
        # 获取目标位置
        target_map = this.charater_pwds.get(chara_id, {}).get('小地图')

        # 筛选：只有在同一地图的角色才显示
        if player_map == target_map:
            charalist.append(chara_id)

            # --- 文本部分 ---
            # 直接从 state 获取名字，无需再查 init.charaters_key
            name = state.get('name', '未知')
            
            # [关键] 点击事件返回 c_ID 格式，配合 start.py 的拦截逻辑
            gradient_text += this.cs(name).click(f"c_{chara_id}") + "                 "

            # --- 图片部分 (核心简化) ---
            # 直接读取 state_builder 预计算好的 full_key
            # 这里的 full_key 已经是 "1_初始绘_顔絵_服_通常_1" 这种完整格式了
            if 'portrait' in state and 'full_key' in state['portrait']:
                img_key = state['portrait']['full_key']
            else:
                # 容错：万一 state 没构建好，给个默认值防止报错
                img_key = f"{chara_id}_初始绘_顔絵_服_通常_{chara_id}"
            
            img_list.append(img_key)

    return gradient_text, img_list, charalist