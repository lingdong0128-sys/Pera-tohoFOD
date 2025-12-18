from utils.era_handler import EraKojoHandler

def event_menu_inventory(this):
    """
    显示物品栏
    trigger: menu_item
    """

    
    # 简单的交互循环
    while True:
        input = this.console.INPUT()
        if input == '999':
            break
            # 初始化 Handler (默认查看主角的背包)
        context = {'TARGET': '0'} # 0是主角
        kojo = EraKojoHandler(this.console, context)
        
        # 获取背包字典
        # 注意：这里直接读 allstate，因为我们已经在 build_state 里生成了
        inventory = this.console.allstate['0'].get('inventory', {})
        
        this.console.PRINT_DIVIDER("=")
        this.console.PRINT("【 背 包 一 览 】", colors=(255, 255, 0))
        
        if not inventory:
            this.console.PRINT("    (空空如也)", colors=(150, 150, 150))
        else:
            # 遍历背包
            for item_id, count in inventory.items():
                # 从全局 Item.csv 获取详情
                item_def = kojo.init.global_key['Item'].get(item_id, {})
                name = item_def.get('name', '未知物品')
                desc = item_def.get('ex', '...')
                
                # 显示格式：[ID] 名称 x数量 : 描述
                # 点击物品ID可以触发使用逻辑(use_item)
                text = f"[{item_id}] {name} x{count}"
                this.console.PRINT(this.cs(text).click(f"use_{item_id}"), f" : {desc}")

        this.console.PRINT_DIVIDER("-")
        this.console.PRINT(this.cs("[999] 返回").click("999"))
        if input.startswith("use_"):
            item_id = input.split('_')[1]
            this.console.PRINT(f"你使用了物品 {item_id} (使用效果功能待开发...)")
            # 这里可以扩展：调用 event_use_item_1 等事件
            break

event_menu_inventory.event_trigger = "menu_item"