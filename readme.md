# 🐱 Pera Framework 开发指南 (Demo版)


**注意：** 本项目目前正在施工中！

## 📖 简介

大家好，这里是 **凌冬**。众所周知，使用原版 ERB 开发 Era 游戏时，我们经常会遇到各种问题（看代码像天书、变量裸奔等）。为了让想开发 Era 游戏但在 ERB 面前却步的朋友们有更多选择，我开发了 **Pera** 框架。

### 什么是 Pera？

Pera 是一个基于 **Python** 和 **Pygame** 构建的前端框架，旨在让 Era 系游戏的开发变得更加方便。

### 为什么选择 Pera？

*   **CSV 搬运友好**：虽然不能直接转码 ERB，但可以直接搬迁 CSV 文件。
*   **自动导入**：框架初始化时会自动导入 `./csv` 下的所有 .csv 文件，并自动分类为 **角色数据** 和 **全局变量**。
*   **Python 语法简单**，入门轻松。
*   **强大的开发工具**：内置可视化的**口上制作工坊**，无需写代码即可创作剧情。

## 📚 开发者文档导航

为了方便查阅，我们将文档分为了几个部分：

*   🚀 **[核心指南](#-快速开始)**: 本页下方包含了快速开始、基础概念和 API 速查。
*   🛠️ **[口上制作器指南](./doc/口上制作器使用手册.md)**: **强烈推荐！** 即使不会编程也能用它写出口上，像搭积木一样简单。
*   📚 **[变量调用指南](./doc/变量调用.md)**: 详细介绍了 `allstate` 状态字典的结构和使用方法。
*   🗺️ **[变量映射手册 (ERB ⟺ Python)](./doc/变量映射文档.md)**: 专为 ERB 转 Python 开发者准备，详细列出了如何使用 `EraKojoHandler` 来模拟 ERB 的变量操作。
*   🔄 **[转换器文档](./doc/转化器.md)**: 如果您有将 ERB 口上转换为 Pera 框架的需求，请参考此文档。

---

## 🛠️ 快速开始

### 环境需求

*   使用 pip 安装 requirements 中的库:
    ```Shell
    pip install -r ./requirements.txt
    ```
*   使用 **Python 3.13.x**。

### 启动方式

```shell
python main.py
```

---

## 📘 小白请看这里！！

*   **什么是 self / this / thethings？**
    *   它们都代表 **"游戏主程序自己"**。你可以把它想象成一个百宝箱，里面装了所有的功能（打印文字、播放音乐、管理事件）。
    *   在事件函数里，你必须通过这个参数来指挥游戏做事。例如 `this.console.PRINT("你好")` 就是告诉游戏主程序：“请在你的控制台上打印这行字”。

*   **什么是 console？**
    *   `console` 是主程序里的一个 **"控制台盒子"**。所有跟显示、输入有关的功能都在这里面。
    *   你想说话？找 `console.PRINT`。你想听玩家说什么？找 `console.INPUT`。

*   **API 是什么？**
    *   API 就是框架给你准备好的 **"按钮"**。你不需要知道按钮后面是怎么接线的，你只要知道按下 `PRINT` 按钮屏幕上就会出字就行了。

*   **INPUT 的注意事项 (重要！)**
    *   INPUT 接口很 **"专一"**。在你的事件里调用 `input = this.console.INPUT()`，这个 `input` 变量只属于你的事件。
    *   **千万不要** 试图去读取主循环里的 input 变量，那是上一层的事，跟你没关系。
    *   **赋值调用**：`a = INPUT()` -> 程序暂停，等待玩家输入，然后把输入的内容给 `a`。
    *   **直接调用**：`INPUT()` -> 程序暂停，等待玩家按回车，不保存输入内容（常用于“按任意键继续”）。

---

## ⚡ API 快速查找

### 1. PRINT (文本输出)
*   **普通输出**：
    ```python
    self.console.PRINT("Hello World!")
    self.console.PRINT("蓝色文字", colors=(0,0,255))
    ```
*   **点击交互** (用户点击后相当于输入了 "next")：
    ```python
    self.console.PRINT("点击继续", click="next")
    ```
*   **高级输出** (使用 `cs` 快捷函数，同一行显示不同颜色/点击)：
    ```python
    # 需要在事件中引入 cs 或者使用 self.cs
    self.console.PRINT(
        cs("红色").set_color((255,0,0)).click("red"),
        " | ",
        cs("蓝色").set_color((0,0,255)).click("blue")
    )
    ```

### 2. INPUT (获取输入)
*   **获取输入**：
    ```python
    user_input = self.console.INPUT()
    if user_input == "1":
        ...
    ```
*   **暂停等待**：
    ```python
    self.console.PRINT("按任意键继续...")
    self.console.INPUT()
    ```

### 3. PRINTIMG (图片显示)
*   **全名调用**：
    ```python
    # 格式：角色ID_立绘类型_图片名_角色ID
    PRINTIMG("0_玩家立绘_顔絵_服_通常_0")
    ```
*   **列表叠加模式 (推荐)**：
    这是 Pera 最强大的功能，用于实现 **表情差分**（身体+衣服+表情）。
    ```python
    img_list = [
        {"img": "0_身体", "offset": (0,0)},
        {"img": "0_衣服", "offset": (0,0)},
        {"img": "0_表情", "offset": (0,0)}
    ]
    # 第一个参数传 None
    self.console.PRINTIMG(None, img_list=img_list)
    ```

### 4. event_manager (事件管理器)
*   **触发事件**：
    ```python
    self.event_manager.trigger_event('事件ID', self)
    ```

---

## 📂 数据结构与调用

### 1. 角色数据 (`charaters_key`)
*   **说明**：存储所有角色的原始 CSV 数据。
*   **结构**：`{ '角色ID': { '属性分类': { '属性名': '值' } } }`
*   **获取**：
    ```python
    # 获取 0 号角色的名字
    name = self.console.init.charaters_key['0'].get('名前')
    ```

### 2. 全局变量 (`global_key`)
*   **说明**：存储 `csv/global/` 下的全局配置（如物品、配置）。
*   **结构**：`{ '文件名': { 'ID': '值' } }`
*   **获取**：
    ```python
    # 获取 Item.csv 中 ID 为 1 的物品名
    item = self.console.init.global_key['Item']['1'].get('name')
    ```

### 3. 图像数据 (`image_data` & `chara_images`)
*   **image_data**：存储所有已注册图片的详细信息（路径、坐标、大小）。可以通过图片全名索引。
*   **chara_images**：按角色分类的图片索引，结构为 `{角色ID: {立绘类型: [图片列表]}}`。

---

## 🎵 音乐控制

*   将音频文件放入 `Musicbox` 文件夹。
*   在全局变量 `musicbox.csv` 中添加键值对：`显示名称, 路径`。
*   使用 `events/music_control.py` 进行控制。

---

## 💻 开发指南

### 游戏事件链 (Event Chain)
在 Pera 中，建议建立清晰的“主事件”结构：
1.  **主事件** (如 `start.py`)：包含 `while` 循环和 `INPUT` 等待。它是游戏的一个“场景”。
2.  **子事件**：由主事件触发，执行完功能后返回。
3.  **存档机制**：存档系统会自动记录当前的“主事件”栈，读档时会回到最近的一个主事件（例如回到商店界面，而不是购买结算的中间状态）。

### 口上制作工坊 (Kojo Maker)
如果你觉得写代码太麻烦，请在游戏里输入 **`kojo_maker`**！
*   **可视化编辑**：像拼积木一样写剧情。
*   **自动生成代码**：导出为标准的 `.py` 文件。
*   **无需记忆变量**：所有属性、立绘、事件都会自动列在下拉菜单里。
*   详细教程请见 [口上制作器指南](./doc/口上制作器使用手册.md)。

---

## 📄 License

本项目采用 **Mozilla Public License 2.0 (MPL-2.0)** 开源协议。