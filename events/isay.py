def event_isay(this):
    this.console.PRINTIMG("0_玩家立绘_顔絵_服_通常_0", clip_pos=(0,0), size=(180,180))
    this.console.PRINT("嗯？不选择进入游戏反而选择和我搭话吗？")
    this.console.INPUT()
    
    while True:  # 真正的对话循环
        this.console.PRINTIMG("0_玩家立绘_顔絵_服_通常_0", clip_pos=(0,0), size=(180,180))
        this.console.PRINT("不说话吗？你这家伙！")
        this.console.PRINT("[1]还是离开吧")
        this.console.PRINT("[2]继续搭话")
        this.console.PRINT("[3]问其他事情")
        
        choice = this.console.INPUT()
        
        if choice == "1":
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
        else:
            continue
event_isay.event_id = "isay"
event_isay.event_name = "和你小姐说话"
event_isay.event_trigger = "666"