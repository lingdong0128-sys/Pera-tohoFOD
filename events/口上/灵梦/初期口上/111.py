from utils.era_handler import EraKojoHandler

def event_1_初期_未命名(this):
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

    if int(kojo.ABL.get('Ｃ感覚', 0)) > 0 and int(kojo.ABL.get('Ｃ感覚', 0)) > 0 and int(kojo.ABL.get('Ｃ感覚', 0)) > 0:
        pass

event_1_初期_未命名.event_trigger = '1_初期_未命名'

# ----------------------------------------
