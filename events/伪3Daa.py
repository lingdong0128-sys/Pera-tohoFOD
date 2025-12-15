import math
import random


class VectorAACanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # buffer存储: (vx, vy, intensity)
        self.buffer = [[(0.0, 0.0, 0.0) for _ in range(width)]
                       for _ in range(height)]

        # 字符向量映射表
        # 这里的向量代表“线条的走向”
        self.char_map = {
            " ": (0, 0, 0),
            "~": (1, 0.2, 0.4),   # 微波 (略微倾斜的横向)
            "-": (1, 0, 0.5),     # 平静水面
            "=": (1, 0, 0.6),     # 较强的水面
            "|": (0, 1, 0.5),     # 竖直 (水花飞溅)
            "/": (0.7, -0.7, 0.5),  # 右上 (水花)
            "\\": (0.7, 0.7, 0.5),  # 右下
            "^": (0, -1, 0.5),    # 尖端
            "o": (0, 0, 0.6),     # 泡沫 (无方向)
            "█": (0, 0, 1.0),     # 实体
        }

    def clear(self):
        self.buffer = [[(0.0, 0.0, 0.0) for _ in range(self.width)]
                       for _ in range(self.height)]

    def add_layer(self, layer_data, offset_x=0, offset_y=0):
        for r, row in enumerate(layer_data):
            for c, cell in enumerate(row):
                if not cell:
                    continue

                in_vx, in_vy, in_int = cell
                ay, ax = int(r + offset_y), int(c + offset_x)

                if 0 <= ay < self.height and 0 <= ax < self.width:
                    old_vx, old_vy, old_int = self.buffer[ay][ax]

                    # --- 核心混合逻辑 ---
                    # 1. 实体遮挡：如果新图层强度极高(>0.9)，直接覆盖
                    if in_int > 0.9:
                        self.buffer[ay][ax] = (in_vx, in_vy, in_int)
                    # 2. 向量叠加：模拟力的相互作用 (例如：水流 + 冲击力)
                    else:
                        # 简单的向量相加，模拟波叠加
                        # 权重取决于强度
                        total_int = max(old_int, in_int)
                        res_vx = old_vx + in_vx
                        res_vy = old_vy + in_vy
                        self.buffer[ay][ax] = (res_vx, res_vy, total_int)

    def _resolve_char(self, vx, vy, intensity):
        if intensity < 0.2:
            return "　"
        if intensity >= 0.95:
            return "█"  # 绝对实体

        # 归一化
        mag = math.sqrt(vx*vx + vy*vy)
        if mag < 0.1:
            return "o"  # 有强度但无方向 -> 泡沫/圆点

        nX, nY = vx/mag, vy/mag

        best_char = "?"
        max_score = -999

        for char, (cvx, cvy, c_int) in self.char_map.items():
            if intensity < c_int - 0.2:
                continue  # 强度不够就不显示这个字符

            # 计算方向相似度 (点积)
            c_mag = math.sqrt(cvx**2 + cvy**2)
            if c_mag == 0:
                continue

            # 我们比较的是“线条走向”，所以方向相反也是同一个字符 (1,0) 和 (-1,0) 都是 "-"
            score = abs(nX * (cvx/c_mag) + nY * (cvy/c_mag))

            if score > max_score:
                max_score = score
                best_char = char

        return best_char

    def render(self):
        res = ""
        for row in self.buffer:
            line = ""
            for cell in row:
                line += self._resolve_char(*cell)
            res += line + "\n"
        return res
# 生成动态水面向量场


def get_water_waves(width, height, time_t):
    data = [[None for _ in range(width)] for _ in range(height)]
    water_level = height // 2 + 2

    for y in range(height):
        for x in range(width):
            if y >= water_level:
                # 计算波浪
                # 越深的地方波浪越小
                depth_factor = 1.0 / (y - water_level + 1)
                # 使用 sin 函数模拟波浪起伏
                wave = math.sin(x * 0.5 + time_t) * depth_factor

                # 向量生成：
                # vx = 1.0 (主要横向流动)
                # vy = wave (根据波浪上下波动)
                # intensity = 0.5 (水的基准强度)
                data[y][x] = (1.0, wave * 0.8, 0.5)
    return data

# 生成一个实心箱子


def get_box(w, h):
    # 箱子是实心的，强度 1.0
    return [[(0, 0, 1.0) for _ in range(w)] for _ in range(h)]

# 生成水花冲击向量 (向上喷射)


def get_splash_vectors(radius):
    size = radius * 2 + 1
    data = [[None for _ in range(size)] for _ in range(size)]
    center = radius

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx*dx + dy*dy)

            # 只在圆环区域生成向量
            if radius - 1 < dist < radius + 1:
                # 向量指向圆心外侧并向上
                # vx: 向外, vy: 向上强力 (-2.0)
                data[y][x] = (dx * 0.5, -2.0, 0.6)
    return data

# 放到你的工具文件或事件文件顶部


def get_splash_vectors(radius):
    # 扩大画布范围，防止大水花被截断
    size = int(radius * 2 + 6)
    data = [[None for _ in range(size)] for _ in range(size)]
    center = size // 2

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx*dx + dy*dy)

            # [修改点 1] 增加水花厚度
            # 以前是半径 ±1，现在改为 ±2.5，让水花更厚实
            if radius - 2.5 < dist < radius + 1.5:

                # [修改点 2] 增强向量力度
                # dx * 0.8: 向外的扩散力变大
                # -4.0: 向上的力大幅增加 (之前是 -2.0)，这会让字符强制变成 '|' 或 '/'
                # 0.8: 强度变大，确保能覆盖掉横向的水波
                vec_x = dx * 0.8
                vec_y = -4.0
                intensity = 0.8

                data[y][x] = (vec_x, vec_y, intensity)
    return data


def event_water_demo(this):
    import time
    import pygame

    W, H = 50, 25  # 画布稍微大一点
    canvas = VectorAACanvas(W, H)

    this.console.PRINT("按回车投掷 (慢动作版)...")
    this.console.INPUT()

    box_x = 22
    box_y = -5
    velocity = 0

    # [修改点 3] 物理变慢
    # 重力从 0.5 降到 0.15，下落会有漂浮感
    gravity = 0.15

    time_t = 0.0
    splash_frame = 0

    running = True
    while running:
        canvas.clear()
        # [修改点 4] 波浪流动变慢
        time_t += 0.2

        # --- 物理更新 ---
        velocity += gravity
        box_y += velocity

        # 水面高度
        water_level = 14

        if box_y > water_level:
            # 入水后阻力更大，减速更明显
            velocity *= 0.85

        # 循环重置
        if box_y > H + 5:
            box_y = -5
            velocity = 0
            splash_frame = 0

        # --- 图层绘制 ---

        # 1. 水面
        water_data = get_water_waves(W, H, time_t)
        canvas.add_layer(water_data, 0, 0)

        # 2. 巨大水花逻辑
        # [修改点 5] 扩大触发范围，让水花持续时间更长
        if water_level - 2 < box_y < water_level + 8:
            splash_frame += 1

            # [修改点 6] 水花扩散半径变大
            # * 1.2 让水花扩散得比以前快，范围更广
            radius = int(splash_frame * 1.2) + 3

            splash_vec = get_splash_vectors(radius)

            # 居中对齐水花
            s_size = len(splash_vec)
            offset_x = int(box_x + 2 - s_size // 2)
            offset_y = int(water_level + 1 - s_size // 2)  # 固定在水面上方一点炸开

            canvas.add_layer(splash_vec, offset_x, offset_y)

        # 3. 箱子
        box_data = get_box(4, 4)
        canvas.add_layer(box_data, box_x, int(box_y))

        # --- 渲染 ---
        frame_str = canvas.render()

        this.console.clear_screen()
        this.console.PRINT(f"Slow Motion Physics (Vel={velocity:.2f})")
        this.console.PRINT("----------------------------------------")
        this.console.PRINT(frame_str)

        # [修改点 7] 增加帧延迟，让肉眼更能看清变化
        time.sleep(0.08)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

    this.console.PRINT("演示结束")


event_water_demo.event_trigger = "water"
