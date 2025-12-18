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

    current_val = int(kojo.CFLAG[kojo.TARGET].get('好感度', 0))
    new_val = current_val + int(1)
    kojo.CFLAG.set('好感度', new_val, chara_id=kojo.TARGET)

event_1_初期_未命名.event_trigger = '1_初期_未命名'

# ----------------------------------------
