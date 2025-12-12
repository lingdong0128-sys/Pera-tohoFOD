# --- 修改后的 对象选择.py ---

def event_对象选择(self):
    charalist = []
    gradient_text = "       "  # 稍微调整了下空格
    ImgList = []
    
    # 筛选同地图角色
    for i in self.console.init.chara_ids:
        # 建议加个容错，防止'小地图'不存在报错
        p_map = self.charater_pwds.get('0', {}).get('小地图')
        t_map = self.charater_pwds.get(i, {}).get('小地图')
        if p_map == t_map:
            charalist.append(i)
            
    for i in charalist:
        chara_data = self.console.init.charaters_key[i]

        # 2. 计算默认值：如果是初始绘就用 A，否则用 B
        # 注意：这里用了 .get('draw_type') 防止 draw_type 不存在报错
        

        # 3. 获取 DrawName，如果没有就使用上面算出来的默认值
        
        img = ''
        # 获取名字
        charaname = self.console.init.charaters_key.get(i).get('名前', '未知')
        
        # [核心修改] click 里面必须传 ID，且建议加上前缀 c_
        # 之前你传的是 charaname，导致 start.py 无法识别
        gradient_text += self.cs(charaname).click(f"c_{i}") + "                 "
        
        # 图片逻辑 (保持你的原样，稍微整理了下)
        draw_type = self.console.init.charaters_key[i].get('draw_type')
        if not draw_type:
            self.console.init.charaters_key[i]['draw_type'] = '初始绘'
            draw_type = '初始绘'
        default_name = '顔絵_服_通常' if chara_data.get('draw_type') == '初始绘' else '别顔_服_通常'
        DrawName = chara_data.get('DrawName', default_name)
        img = f"{img}{i}_{draw_type}_{DrawName}_{i}"
        print(img)
        ImgList.append(img)
        
    return gradient_text, ImgList, charalist