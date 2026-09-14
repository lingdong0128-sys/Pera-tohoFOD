# -*- coding: utf-8 -*-
"""
MID 渲染管线：把 Musicbox/ 下的 .mid 用 FluidSynth + 音色库预渲染成 .ogg 缓存。

为什么：pygame.mixer 播 .mid 会甩给 Windows 自带的 GS Wavetable Synth（祖传 2MB 音色库，
效果差且有延迟）。预渲染后 MusicBox.load_music 会优先加载同名 .ogg/.wav，彻底绕开系统合成器，
玩家零依赖、打包 exe 无顾虑。

用法：
    .venv/Scripts/python tools/mid渲染.py            # 只渲染没有缓存的
    .venv/Scripts/python tools/mid渲染.py --force    # 全部重新渲染
    .venv/Scripts/python tools/mid渲染.py --sf2 某音源.sf2

依赖：
    - FluidSynth：自动在 PATH 和 tools/fluidsynth/ 下寻找
    - 音色库 SF2/SF3：放 tools/soundfonts/ 下即可（推荐 SGM-V2.01 或 SC-88 系转制）
    - ffmpeg（ogg 压缩）：优先用 .venv 里 moviepy 附带的 imageio-ffmpeg；找不到则保留 wav
"""
import argparse
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(ROOT, 'Musicbox')
SOUNDFONT_DIR = os.path.join(ROOT, 'tools', 'soundfonts')


def find_fluidsynth():
    """定位 fluidsynth.exe：PATH → tools/fluidsynth/**/bin/"""
    try:
        version = subprocess.run(['fluidsynth', '--version'], capture_output=True,
                                 text=True, timeout=10)
        if version.returncode == 0:
            return 'fluidsynth'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    for exe in glob.glob(os.path.join(ROOT, 'tools', 'fluidsynth', '**', 'bin', 'fluidsynth.exe'),
                         recursive=True):
        return exe
    return None


def find_soundfont(override=None):
    """定位音色库：--sf2 参数 → tools/soundfonts/ 下的第一个 sf2/sf3"""
    if override:
        return override if os.path.exists(override) else None
    candidates = sorted(glob.glob(os.path.join(SOUNDFONT_DIR, '*.sf2'))) + \
                 sorted(glob.glob(os.path.join(SOUNDFONT_DIR, '*.sf3')))
    return candidates[0] if candidates else None


def find_ffmpeg():
    """定位 ffmpeg（ogg 压缩用）：moviepy 附带的 imageio-ffmpeg → PATH"""
    try:
        sys.path.insert(0, ROOT)
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(exe):
            return exe
    except Exception:
        pass
    try:
        probe = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10)
        if probe.returncode == 0:
            return 'ffmpeg'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def render_mid(fs_exe, sf2, mid_path, ffmpeg_exe, force=False):
    """渲染单个 mid → 同名 .ogg（无 ffmpeg 则 .wav）。返回 (状态, 输出路径)。"""
    base = mid_path[: mid_path.rfind('.')]
    ogg_path, wav_path = base + '.ogg', base + '.wav'
    if not force and (os.path.exists(ogg_path) or os.path.exists(wav_path)):
        return 'skip', ogg_path if os.path.exists(ogg_path) else wav_path

    # 1. FluidSynth 渲染 wav（-ni 无界面不实时播放；-g 增益 0.5；44.1k 立体声）
    cmd = [fs_exe, '-ni', '-g', '0.5', '-r', '44100',
           '-F', wav_path, sf2, mid_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0 or not os.path.exists(wav_path):
        return 'fail', (result.stderr or result.stdout or '')[-200:]

    # 2. 有 ffmpeg 则压缩成 ogg，删中间 wav；否则保留 wav 作为缓存
    if ffmpeg_exe:
        conv = subprocess.run(
            [ffmpeg_exe, '-y', '-i', wav_path, '-vn', '-q:a', '5', ogg_path],
            capture_output=True, text=True, timeout=600)
        if conv.returncode == 0 and os.path.exists(ogg_path):
            os.remove(wav_path)
            return 'ok', ogg_path
    return 'ok', wav_path


def main():
    parser = argparse.ArgumentParser(description='MID→OGG 预渲染管线')
    parser.add_argument('--force', action='store_true', help='忽略缓存全部重渲')
    parser.add_argument('--sf2', default=None, help='指定音色库路径')
    args = parser.parse_args()

    fs_exe = find_fluidsynth()
    if not fs_exe:
        print('❌ 找不到 fluidsynth（PATH 和 tools/fluidsynth/ 都没有）')
        print('   下载：https://github.com/FluidSynth/fluidsynth/releases 解压到 tools/fluidsynth/')
        return 1

    sf2 = find_soundfont(args.sf2)
    if not sf2:
        print(f'❌ 找不到音色库（{SOUNDFONT_DIR} 下没有 sf2/sf3）')
        print('   推荐 SGM-V2.01（免费）：https://archive.org/download/SGM-V2.01')
        print('   追求原味可自行寻找 SC-88Pro 转制 SF2，放进该目录即可')
        return 1

    ffmpeg_exe = find_ffmpeg()
    print(f'FluidSynth: {fs_exe}')
    print(f'音色库: {os.path.basename(sf2)}')
    print(f'ffmpeg(ogg压缩): {ffmpeg_exe or "无，将保留wav"}')
    print()

    mids = sorted(glob.glob(os.path.join(MUSIC_DIR, '*.mid')) +
                  glob.glob(os.path.join(MUSIC_DIR, '*.midi')))
    if not mids:
        print('Musicbox/ 下没有 .mid 文件')
        return 0

    ok = skip = fail = 0
    for mid in mids:
        name = os.path.basename(mid)
        status, info = render_mid(fs_exe, sf2, mid, ffmpeg_exe, force=args.force)
        if status == 'ok':
            ok += 1
            print(f'  ✅ {name} -> {os.path.basename(info)}')
        elif status == 'skip':
            skip += 1
            print(f'  ⏭ {name}（已有缓存）')
        else:
            fail += 1
            print(f'  ❌ {name} 渲染失败: {info}')

    print(f'\n完成: {ok} 渲染 / {skip} 跳过 / {fail} 失败')
    print('游戏内 MusicBox 会自动优先播放同名 .ogg/.wav，无需其他配置。')
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
