# 音色库目录

把 SF2/SF3 音色库文件放进本目录，`tools/mid渲染.py` 会自动使用找到的第一个。

**为什么需要**：pygame 播放 `.mid` 会使用 Windows 自带的 GS Wavetable Synth（祖传 2MB 音色库，
效果差且有延迟）。预渲染管线用 FluidSynth + 音色库把 mid 转成 ogg，游戏直接播放音频文件。

**推荐音源**：

| 音色库 | 大小 | 说明 |
|---|---|---|
| [SGM-V2.01](https://archive.org/download/SGM-V2.01) | ~236MB | 雅马哈系风格，免费（CC 授权），东方编曲社区常用，综合推荐 |
| FluidR3_GM | ~140MB | 免费（MIT），通用 GM，干净但不够"东方" |
| SC-88Pro 转制 SF2 | 不等 | **最接近 ZUN MIDI 时代（红魔乡～花映冢）的原味音源**（Roland Sound Canvas 系）；社区流通的硬件 ROM 转制版，法律灰色，请自行获取 |

**使用**：

```shell
.venv/Scripts/python tools/mid渲染.py          # 渲染 Musicbox/*.mid → 同名 .ogg
```

渲染后无需任何配置：`MusicBox.load_music` 会自动优先加载同名 `.ogg/.wav`。
