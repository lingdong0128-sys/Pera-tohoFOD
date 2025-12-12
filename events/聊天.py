def event_聊天(this):
    choice=this.console.init.charaters_key['0'].get('选择对象')
    #口上选择应该有一个口上加载器去控制当前使用的口上，然后在使用的口上里面选择差分，比如说当前口上是初期口上然后看我们调用的是什么然后进行字符串拼接
    #口上事件字符串：str=选择角色+'_'+口上类型+'_'+当前状态
    if not choice:
        this.console.PRINT("你还没有选择对象哦！")
        return
    #这里应该再多来点东西加进来的，比如说当前的状态，是日常还是别的？然后根据状态来选择不同的对话事件
    else:
        str_event= choice + '_初期口上_日常系'
        try:
            this.event_manager.trigger_event(f"{str_event}", this)
            #应该给口上事件传参数的，当前状态什么的，然后口上文件根据传达的参数选择差分之类的，后面在做吧~
        except Exception as e:
            this.console.PRINT(f"口上文件 {str_event}不存在！！！", colors=(255, 200, 200))