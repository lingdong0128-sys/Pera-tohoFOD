from utils.era_handler import EraKojoHandler


def event_1_初期口上_初会面(this):
    # 1. 初始化处理器
    # 获取传递过来的上下文 (如果没有则为空字典)
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    # 2. 定义颜色常量 (模仿 ERA 风格)
    COL_TALK = (255, 255, 255)  # 对话：亮白
    COL_DESC = (170, 170, 170)  # 描述：灰色 (对应 PRINTFORMD)

    # 3. 获取常用变量
    # 获取主角名字 (%CALLNAME:MASTER%)
    master_id = kojo.MASTER
    # 注意：这里假设主角数据也在 charaters_key 中
    master_name = this.console.init.charaters_key.get(
        master_id, {}).get('呼び名', '你')

    # 获取 CFLAG:31 的值
    # 注意：从 CSV 读出来通常是字符串，需要转 int
    cflag_31 = int(kojo.CFLAG.get('31', 0))

    # 4. 实现 GETBIT 逻辑
    # 检查第 0 位和第 1 位
    has_met_0 = (cflag_31 >> 0) & 1
    has_met_1 = (cflag_31 >> 1) & 1

    # 5. 开始剧情逻辑
    # IF GETBIT(CFLAG:31, 0) || GETBIT(CFLAG:31, 1)
    if has_met_0 or has_met_1:
        # --- 强行开启周目/重逢分支 ---
        this.console.PRINT(f"「――啊啦、早上好」", colors=COL_TALK)

        this.console.PRINT(f"灵梦面无表情的说道。", colors=COL_DESC)

        this.console.PRINT(f"「……怎么了？　{master_name}？」", colors=COL_TALK)

        this.console.PRINT(f"见你没什么反应地站着、灵梦这样说道。", colors=COL_DESC)
        this.console.PRINT(f"啊、啊啊……早上好、灵梦。", colors=COL_DESC)

        this.console.PRINT(f"「……早上好」", colors=COL_TALK)

        this.console.PRINT(f"……发生了什么事吗？　灵梦？", colors=COL_DESC)

        this.console.PRINT(f"「……什么事也没有啊」", colors=COL_TALK)

        this.console.PRINT(f"……？", colors=COL_DESC)
        this.console.INPUT()  # WAIT

        this.console.PRINT(f"「……总觉得有些朦朦胧胧的」", colors=COL_TALK)

        this.console.PRINT(f"什么？", colors=COL_DESC)

        this.console.PRINT(f"「怎么说呢、有种奇怪的感觉」", colors=COL_TALK)
        this.console.PRINT(f"「明明还不是很亲密的朋友」", colors=COL_TALK)

        this.console.PRINT(f"………………。", colors=COL_DESC)

        this.console.PRINT(f"「……嘛、好吧」", colors=COL_TALK)
        this.console.INPUT()  # WAIT

        this.console.PRINT(f"「那么、有何贵干呢？」", colors=COL_TALK)

    else:
        # --- 初次见面分支 ---
        this.console.PRINT("")  # PRINTL

        this.console.PRINT(f"「――啊啦，没见过的脸呢」", colors=COL_TALK)
        this.console.INPUT()  # WAIT

        this.console.PRINT(f"那个少女看向{master_name}这么说道。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(
            f"「……紫说过的外来人吗？那么……算了无所谓了。你好、请多关照。」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT(f"这么说着，少女向你伸出了手。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(f"{master_name}握住了那只手。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(f"「我的名字是博丽灵梦。你是？」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT(f"{master_name}向灵梦报上了自己的名字", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(f"「……呼ー、{master_name}是吗……、我知道了」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT(f"灵梦顿了一顿、说道。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(f"「嘛，总之我们从今天开始就住在一个屋檐下了……」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT(f"「要是万一、你敢向其他的居民出手的话——」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT(
            f"灵梦一边加大握手的力量、一边面无表情地对着{master_name}说道。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(f"「――已经做好觉悟了吧？」", colors=COL_TALK)
        this.console.INPUT()

        this.console.PRINT("")  # PRINTDW 空行
        this.console.INPUT()

        this.console.PRINT(f"{master_name}因为这句话、反而升起了强烈的征服欲。", colors=COL_DESC)
        this.console.INPUT()

        this.console.PRINT(
            f"要说为什么的话、是因为{master_name}拥有着令幻想的少女们屈服的能力――", colors=COL_DESC)
        this.console.INPUT()

    # 可选：事件结束后设置标志位，防止下次重复触发初次见面
    # kojo.CFLAG.set('31', str(cflag_31 | 1)) # 将第0位置为1


# 注册事件触发器
# 这里的命名建议遵循：角色ID_口上类型_事件名
event_1_初期口上_初会面.event_trigger = "1_初期口上_初会面"
