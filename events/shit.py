import time
import pygame

def event_iron_man(this):
    frame_1 = [
        "   囧",
        "口 ◻  口",
        "    ◻ "
    ]
    frame_2 = [
        "   囧",
        " ◻ 口 ◻",
        "    口 "
    ]
    this.console.PRINT("随心所欲....", colors=(100, 255, 100))
    this.console.PRINT("（按 [空格键] 或 [点击鼠标] 停止）")
    time.sleep(1)
    running = True
    while running:
        this.console.clear_screen()
        this.console.PRINT_DIVIDER("=", colors=(255, 200, 0))
        this.console.PRINT("")
        for line in frame_1:
            this.console.PRINT(f"      {line}", colors=(255, 255, 255))
        pygame.display.flip()
        time.sleep(0.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys; sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    running = False
        if not running: break
        this.console.clear_screen()
        this.console.PRINT_DIVIDER("=", colors=(255, 200, 0))
        this.console.PRINT("")
        for line in frame_2:
            this.console.PRINT(f"      {line}", colors=(255, 255, 255))
        pygame.display.flip()
        time.sleep(0.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys; sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
    this.console.clear_screen()
    this.console.PRINT("动画已停止。")
event_iron_man.event_trigger = "iron_man"
event_iron_man.is_main_event = False