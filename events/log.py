import time
import colorsys
import os
import pygame

def event_show_cool_logo(this):
    """
    以彩虹渐变特效输出 超高清 ASCII LOGO
    trigger: show_logo
    """
    
    # 1. 准备工作：清屏
    this.console.clear_screen()
    
    # [核心关键] 切换字体！！！
    # 想要"细"、"对齐"，必须用等宽字体。
    # Windows自带 simhei.ttf (黑体) 或 simsun.ttc (宋体) 效果最好。
    # 如果你的 font 文件夹里没有，请去 C:/Windows/Fonts/ 复制一个出来，或者暂时用系统路径
    
    # 尝试加载高精度字体
    font_path = './font/consola.ttc' # 微软雅黑 (推荐，线条细腻)
    if not os.path.exists(font_path):
        font_path = './font/consola.ttf' # 黑体 (备选)
    
    # 如果都没有，回退到默认，但效果会打折
    if not os.path.exists(font_path):
        font_path = this.console.font_path if hasattr(this.console, 'font_path') else './font/luoli.ttf'
    
    # 设置极小字号，这样才能放下巨大的图，并且看起来很"细"
    this.console.set_font(font_path, 24) 

    # 2. LOGO 数据：巨型高密度风格
    # 使用了 ░ ▒ ▓ █ 和 / \ _ 等符号混合，制造纹理感
    logo_data = r"""
                                                                                                                                            
                                                                                                                                            
                        ########  ######## ########     ###          
                        ##     ## ##       ##     ##   ## ##         
                        ##     ## ##       ##     ##  ##   ##        
                        ########  ######   ########  ##     ##       
                        ##        ##       ##   ##   #########       
                        ##        ##       ##    ##  ##     ##       
                        ##        ######## ##     ## ##     ##       
                                                                    
                                                                                                                                            
                                ..   ...      ..  ...           ..   ...      ..  ...           ..   ...      ..  ...                    
                                .:::. .:::.   .:::. .:::.       .:::. .:::.   .:::. .:::.       .:::. .:::.   .:::. .:::.                  
                                ::::::.:::::. ::::::.:::::.     ::::::.:::::. ::::::.:::::.     ::::::.:::::. ::::::.:::::.                 
                                ::::::::::::: :::::::::::::     ::::::::::::: :::::::::::::     ::::::::::::: :::::::::::::                 
                                ':::::::::::' ':::::::::::'     ':::::::::::' ':::::::::::'     ':::::::::::' ':::::::::::'                 
                                ':::::::'     ':::::::'         ':::::::'     ':::::::'         ':::::::'     ':::::::'                   
                                    ':::'         ':::'             ':::'         ':::'             ':::'         ':::'                     
                                    '             '                 '             '                 '             '                       
                                                                                                                                            
                        ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄       ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
                        ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
                        ▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌     ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ 
                        ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          
                        ▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ 
                        ▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌
                        ▐░█▀▀▀▀▀▀▀▀▀      ▐░▌     ▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀█░█▀▀      ▐░█▀▀▀▀▀▀▀▀▀ ▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ 
                        ▐░▌               ▐░▌     ▐░▌     ▐░▌  ▐░▌     ▐░▌       ▐░▌          ▐░▌       ▐░▌▐░▌          
                        ▐░▌           ▄▄▄▄█░█▄▄▄▄ ▐░▌      ▐░▌ ▐░▌      ▐░▌      ▐░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░▌          
                        ▐░▌          ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌          ▐░░░░░░░░░░░▌▐░▌          
                        ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀         ▀       ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀           
                                                                                                                                            
                                                                                                                                            
                            [ P A T H ]              [ O F ]              [ F A N T A S Y ]
                                                                                                                                            
"""

    # 彩虹色生成器 (增加饱和度，让颜色更锐利)
    def get_neon_color(x, y, t):
        # 垂直渐变频率
        freq_y = 0.08
        # 水平渐变频率 (让它有点斜向的流动感)
        freq_x = 0.02
        
        hue = (x * freq_x + y * freq_y + t) % 1.0
        # 饱和度(S) 0.9, 亮度(V) 1.0 -> 这种颜色在黑色背景下最"亮"
        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    # 3. 渲染循环
    # 为了防止卡顿，我们预先计算每一行的颜色对象，然后一次性打印
    lines = logo_data.strip('\n').split('\n')
    
    # 顶部装饰
    this.console.PRINT_DIVIDER("=", colors=(0, 255, 255))
    
    start_time = time.time()
    
    for row_idx, line in enumerate(lines):
        line_cs = this.cs("")
        
        for col_idx, char in enumerate(line):
            # 跳过纯空格，减少计算量
            if char == ' ':
                line_cs += this.cs(" ")
                continue
                
            # 根据字符类型决定颜色策略
            # 这里的逻辑是：特殊符号用暗色，主体块用亮色，形成立体感
            
            base_color = get_neon_color(col_idx, row_idx, 0)
            
            if char in "░▒▓": 
                # 纹理部分：稍微暗一点，做底色
                r, g, b = base_color
                color = (int(r*0.6), int(g*0.6), int(b*0.6))
            elif char in "█":
                # 实体部分：高亮
                color = base_color
            elif char in "#@":
                # 标题部分：金色/橙色系
                color = (255, 200, 50)
            elif char in ".:'":
                # 装饰点：灰色/白色
                color = (150, 150, 150)
            elif char in "▄▀▌▐":
                # 汉字轮廓：青色系
                color = (50, 255, 255)
            else:
                color = base_color
            
            line_cs += this.cs(char).set_color(color)
            
        this.console.PRINT(line_cs)
        # 极速扫描效果：几乎不等待，或者非常短
        time.sleep(0.005) 

    this.console.PRINT_DIVIDER("=", colors=(0, 255, 255))
    this.console.PRINT("")
    
    # 4. 底部信息
    this.console.PRINT(
        this.cs("   >>> SYSTEM ONLINE <<<   ").set_color((0, 255, 100)),
        "    ",
        this.cs("   [ VER 0.5.0 ]   ").set_color((100, 200, 255))
    )
    this.console.PRINT("")
    this.console.PRINT("Press [ENTER] to Dive...", colors=(128, 128, 128))
    
    this.console.INPUT()
    
    # 恢复原来的大字体 (假设原字体是 luoli.ttf, 24px)

# 注册
event_show_cool_logo.event_trigger = "show_logo"
event_show_cool_logo.is_main_event = False