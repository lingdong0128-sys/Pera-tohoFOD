def event_start(this):
    import os
    loadidlist=['1','2','3','4','5','99','10','8']#这是一个示例，如果你们也有这种需要进入的循环的话请把每一个循环中需要使用的事件id加入这种列表中并初始化
    #当然这是作为机械加载文本位置的预备功能，现在这个列表还没什么用
    start_eventid={}
    for i in this.event_manager.eventid:
        if i in loadidlist:
            start_eventid[i]=this.event_manager.eventid[i]
    this.console.PRINT("是否要进行全角色立绘检查？")
    this.console.PRINT(this.cs("[1]是").click("1"),"      ",this.cs("[2]否").click("2"))
    coice=this.console.INPUT()
    if coice=='1':
        this.event_manager.trigger_event('设置立绘类型选择',this)
    if coice=='2':
        this.console.PRINT("已跳过立绘检查,所有角色默认设置为初始绘")
    running = True
    while running:
        input = this.console.INPUT()
        # 1. 调用对象选择 (现在 EventManager 修复后，这里能收到数据了)
        result = this.event_manager.trigger_event('对象选择', this)
        
        # 安全检查：防止对象选择出错返回 None 导致崩溃
        if result:
            InOneMapCharater, InOneMapCharaterImg,CharaList = result
        else:
            InOneMapCharater, InOneMapCharaterImg,CharaList = ("", [],[])

        # 2. [修复] 图片列表构建逻辑
        CharaterImgList = []
        Tmp = 0  # [修复] 计数器要在循环外面初始化！
        for i in InOneMapCharaterImg:
            # [修复] 必须在循环内部创建新字典，否则所有图片都会变成最后一张
            CharaterImgDict = {} 
            
            CharaterImgDict['img'] = i  # 注意：这里最好用 img 键名，对应 PRINTIMG 的参数
            CharaterImgDict['offset'] = (Tmp * 180, 0)
            
            # 如果需要指定类型和ID，最好也在对象选择里传出来，或者这里写死
            # CharaterImgDict['draw_type'] = '...' 
            
            CharaterImgList.append(CharaterImgDict)
            Tmp += 1 # 计数器递增
        this.console.PRINTIMG("",img_list=CharaterImgList,size=(180,180))
        this.console.PRINT(InOneMapCharater)
        this.console.PRINT(this.cs("[1]测试文本").click("1"),"         ",this.cs("[2]查询位置").click("2"),"         ",this.cs("[3]商店").click("3"),"         ",this.cs("[4]音乐控制").click("4"))
        this.console.PRINT(this.cs("[5]显示当前音乐").click("5"),"     ",this.cs("[99]退出").click("99"),"            ",this.cs("[10]查看当前加载事件").click("10"),"           ",this.cs("[8]helloworld！").click("8"))
        this.console.PRINT(this.cs("[100]四处张望").click("100"),"         ",this.cs("[200]badapple？").click("200"),"         ",this.cs("[22]聊天").click("22"))

        if input == '99':
            running = False
        elif input:
            # [必须有这一段逻辑]
            # 只有当 start.py 识别到 c_ 开头的输入，才会执行赋值！
            if input.startswith("c_"):
                # 提取真实ID (去掉 c_)
                target_id = input.split('_')[1]
                
                # 存入字典！这一步做了，聊天.py 才能读到东西
                this.console.init.charaters_key['0']['选择对象'] = target_id
                
                # 获取名字用于提示
                t_name = this.console.init.charaters_key[target_id].get('名前')
                this.console.PRINT(f"已选择对象：{t_name}")
                this.console.PRINT(f"已选择对象：{input}")
            elif input == '1':
                this.event_manager.trigger_event('text',this)
            elif input == '22':
                this.event_manager.trigger_event('聊天',this)
            elif input == '2':
                this.event_manager.trigger_event('getpwd',this)
            elif input == '3':
                this.event_manager.trigger_event('shop',this)
            elif input == '4':
                this.event_manager.trigger_event('music_control',this)
            elif input == '5':
                if this.console.music_box:
                    status = this.console.music_box.get_status()
                    current_volume = this.console.music_box.get_volume()
                    this.console.PRINT(f"音乐状态: {status}")
                    this.console.PRINT(f"当前音量: {current_volume:.2f}")
                    if this.console.current_music_name:
                        this.console.PRINT(f"当前音乐: {this.console.current_music_name}")
                    elif this.console.music_box.url:
                        music_name = os.path.basename(this.console.music_box.url)
                        this.console.PRINT(f"当前音乐: {music_name}")
                else:
                    this.console.PRINT("音乐系统未初始化", colors=(255, 200, 200))
                this.console.PRINT("按任意键继续...")
                this.console.INPUT()
            elif input == '10':
                this.event_manager.trigger_event('logevent',this)
            elif input=='8':
                this.event_manager.trigger_event('helloworld',this)
            elif input=='100':
                this.event_manager.trigger_event('findthem',this)
            elif input=='200':
                this.event_manager.trigger_event('bad_apple',this)
            this.console.PRINT("")
event_start.event_id = "start"
event_start.event_name = "开始"
event_start.event_trigger = "0"