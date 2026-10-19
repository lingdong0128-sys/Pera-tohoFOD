# Pera东方FOD：
## 一个基于Pera的肉鸽地牢探险黄油
* 不止于地牢：
  * 您可以在地牢外和大家进行各种互动
* 主线剧情：
  * 您的地牢探险的主要目的是收集各种线索推进主线进度，注意，无论您有没有去推动主线剧情，主线剧情的时间线都会随着您的游玩的时间而推进
* 大家的灵魂：
  * 大家不是淫乱的，被各种事件困的时候，会向您求助，但是如果主线剧情向着不得了的地步发展了....说不定也会改变呢
* 关于人员招募：
  * 游戏制作：
    * 您需要熟悉Python基础语法和Pera框架运用
  * 口上制作：
    * 会用口上编辑器

## 运行与部署

```shell
# Python 3.13 + Windows
pip install -r requirements.txt    # win64 + py3.13 会自动装到本仓库的特化版 pygame（见下节）
python main.py                     # 主菜单输 0 开新游戏
```

音色库不入库（约 240MB）：自行下载 SF2/SF3 放到 `tools/soundfonts/` 即可
（推荐 SGM-V2.01，获取方式见该目录内 README；不放也能玩，mid 会走 ogg 预渲染缓存兜底）。

## 特化版 pygame：`music.load(filename, sf2url)` 新参数

本仓库维护了一个特化版 pygame（`2.6.1+sf2.2`，wheel 见
[Releases · pygame-sf2-2](https://github.com/lingdong0128-sys/Pera-tohoFOD/releases/tag/pygame-sf2-2)，
requirements.txt 会自动安装）：SDL2_mixer 换成了**带 FluidSynth 后端**的自制构建，
全部转接逻辑内建在 wheel 里，用法只有一个新参数：

```python
import pygame

pygame.mixer.init()
pygame.mixer.music.load('Musicbox/xxx.mid', sf2url=r'tools/soundfonts/SGM-V2.01.sf2')
pygame.mixer.music.play()
```

* `.mid` **带** `sf2url` → SDL 内部用 FluidSynth + 指定 SF2 音色库合成直通，
  不经过 Windows GS Wavetable，也不需要预渲染缓存
* `.mid` **不带** `sf2url` → 走 Windows 原生 MIDI（行为同官方 pygame）
* 其他格式与官方 pygame 完全一致；`pygame.mixer.music._sf2_load` 标记可探测是否特化版
* 游戏内的 [Musicbox.py](Musicbox.py) 已内置策略：特化版 + 有音色库时 mid 自动直通，
  否则用同名 `.ogg/.wav` 预渲染缓存（`tools/mid渲染.py` 生成）兜底——任何环境都不用改代码
* 特化版源码（打补丁的 `__init__.py` 全文 + 对官方 diff）：
  [pygame-2.6.1+sf2.2-pera/](pygame-2.6.1+sf2.2-pera/README.md)
* 想自己构建 DLL / 给其他 Python 版本出 wheel / 了解原理：
  详见 [doc/音乐渲染管线.md](doc/音乐渲染管线.md) 与 [SoundFont_c_dll/README.md](SoundFont_c_dll/README.md)