from utils.era_handler import EraKojoHandler

def event_1_text(this):
    context = getattr(this, 'current_kojo_context', {})
    kojo = EraKojoHandler(this.console, context)

    # --- 常用变量定义 (自动生成) ---
    master_name = '你'
    if kojo.MASTER:
        # 从原始数据获取主角名字
        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')
    target_name = kojo.NAME
    call_name = kojo.CALLNAME
    # -----------------------------

    COL_TALK = (255, 255, 255)
    COL_DESC = (170, 170, 170)

    if int(kojo.TALENT.get('处女', 0)) == 0:
        if int(kojo.ABL.get('親密', 0)) > 5000:
            this.console.PRINT(f"感觉好像有点喜欢上{master_name}了呢....", colors=COL_TALK)
            this.console.INPUT()

event_1_text.event_trigger = '1_text'