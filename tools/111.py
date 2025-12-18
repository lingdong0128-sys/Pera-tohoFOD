from utils.era_handler import EraKojoHandler

def event_1_初期_未命名(this):
    """ 默认差分 """
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    # --- 常用变量定义 ---
    master_name = '你'
    if kojo.MASTER:
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('名前', '你')
    target_name = kojo.NAME
    call_name = kojo.CALLNAME
    # --------------------

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    this.console.PRINT(this.cs("[1] [1]11").click("1"), "   ", this.cs("[2] [2]22").click("2"))
    menu_res = this.console.INPUT()
    if menu_res == "1":
        this.console.PRINT(f"111", colors=COL_TALK)
        this.console.INPUT()
    elif menu_res == "2":
        this.console.PRINT(f"...222", colors=COL_TALK)
        this.console.INPUT()

event_1_初期_未命名.event_trigger = '1_初期_未命名'

# ----------------------------------------
