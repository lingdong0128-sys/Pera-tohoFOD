def event_0_初期口上_日常系(this):
    #我们约定每个口上开头需要传入是什么绘，角色ID，传入的时候的状态，角色的状态应该存进一个字典，这样方便差分查找
    CharaID=this.console.init.charaters_key['0'].get("番号")
    DrawType=this.console.init.charaters_key['0'].get("draw_type")
    this.console.PRINTIMG(f"{CharaID}_{DrawType}_别颜_服_笑顔_0", clip_pos=(0,0), size=(180,180))
    this.console.PRINT("嗯？不选择进入游戏反而选择和我搭话吗？")
    this.console.INPUT()
    
    while True:  # 真正的对话循环
        this.console.PRINTIMG(f"{CharaID}_{DrawType}_别颜_服_笑顔_0", clip_pos=(0,0), size=(180,180))
        this.console.PRINT("不说话吗？你这家伙！")
        this.console.PRINT("[1]还是离开吧",click='1')
        this.console.PRINT("[2]继续搭话",click='2')
        this.console.PRINT("[3]问其他事情",click='3')
        this.console.PRINT("[4]想看点'好康的'",click='4')
        choice = this.console.INPUT()
        
        if choice == "1":
            this.console.PRINTIMG(f"{CharaID}_{DrawType}_别颜_服_笑顔_0", clip_pos=(0,0), size=(180,180))
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
                img_list = ["别颜_裸_発情_0","别颜_汗_0",]
                this.console.PRINT("那就给你看吧...")
                this.console.PRINTIMG("", img_list=img_list, chara_id=CharaID, draw_type=DrawType)
                this.console.INPUT()
            elif real=='n':
                this.console.PRINT("切~")
                this.console.INPUT()
        else:
            continue
event_0_初期口上_日常系.event_id = "isay"
event_0_初期口上_日常系.event_name = "和你小姐说话"
event_0_初期口上_日常系.event_trigger = "666"