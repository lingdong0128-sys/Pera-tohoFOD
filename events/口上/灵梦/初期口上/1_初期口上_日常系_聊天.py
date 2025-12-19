from utils.era_handler import EraKojoHandler

def event_1_初期_日常_聊天(this):
    """ 默认差分 """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    # --- 常用变量定义 ---
    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    target_name = kojo.NAME
    call_name = kojo.CALLNAME
    # --------------------

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    rand_1548923223360 = kojo.Rand(2)
    if rand_1548923223360 == 0:
        this.console.PRINT(f"{call_name}？怎么啦？", colors=COL_TALK)
        this.console.INPUT()
    elif rand_1548923223360 == 1:
        this.console.PRINT(f"怎么啦？{call_name}？", colors=COL_TALK)
        this.console.INPUT()

event_1_初期_日常_聊天.event_trigger = '1_初期_日常_聊天'

# ----------------------------------------
