def event_0_初期口上_日常系(this):
    this.console.PRINTIMG("0_玩家立绘_別顔_服_笑顔_0", clip_pos=(0,0), size=(180,180))
    this.console.PRINT("嗯？不选择进入游戏反而选择和我搭话吗？")
    this.console.INPUT()
    
    while True:  # 真正的对话循环
        this.console.PRINTIMG("0_玩家立绘_別顔_服_憤怒_0", clip_pos=(0,0), size=(180,180))
        this.console.PRINT("不说话吗？你这家伙！")
        this.console.PRINT("[1]还是离开吧",click='1')
        this.console.PRINT("[2]继续搭话",click='2')
        this.console.PRINT("[3]问其他事情",click='3')
        this.console.PRINT("[4]想看点'好康的'",click='4')
        choice = this.console.INPUT()
        
        if choice == "1":
            this.console.PRINTIMG("0_玩家立绘_別顔_服_通常_0", clip_pos=(0,0), size=(180,180))
            this.console.PRINT("好吧，那我走了...")
            break  # 退出循环
        elif choice == "2":
            this.console.PRINT("还要继续吗？")
            this.console.INPUT()
            # 继续循环
        elif choice == "3":
            this.console.PRINT("你想问什么？")
            question = this.console.INPUT()
            this.console.PRINT(f"你问了：{question}")
            this.console.PRINT("这是个好问题...")
            this.console.INPUT()
        elif choice == "4":
            this.console.PRINT("真的要看吗？y/n")
            real= this.console.INPUT()
            if real== "y":
                img_list = ["別顔_裸_発情_0","別顔_汗_0",]
                this.console.PRINT("那就给你看吧...")
                this.console.PRINTIMG("", img_list=img_list, chara_id='0', draw_type='玩家立绘')
                this.console.INPUT()
            elif real=='n':
                this.console.PRINT("切~")
                this.console.INPUT()
        else:
            continue
event_0_初期口上_日常系.event_id = "isay"
event_0_初期口上_日常系.event_name = "和你小姐说话"
event_0_初期口上_日常系.event_trigger = "666"