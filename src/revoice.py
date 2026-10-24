"""把全部剧集换成 MiniMax 配音（画面不重渲染，只重新混音并替换音轨）。
用法：
  export MINIMAX_API_KEY=...            # 必填
  export MINIMAX_URL=https://api.minimaxi.com/v1/t2a_v2   # 国内账号（默认）；海外账号用 https://api.minimax.io/v1/t2a_v2
  python3 revoice.py sample             # 先生成试听：同一句话 3 种音色
  python3 revoice.py 1 2 3 ...          # 指定集数；不写则全部 30 集
"""
import os, sys, glob, subprocess, wave, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('VOICE_ENGINE', 'minimax')
import series

def sample():
    line = '四十六亿年前，一团巨大的气体尘埃云，在引力作用下，慢慢收缩、旋转。'
    for v in ('Chinese (Mandarin)_Gentleman', 'Chinese (Mandarin)_Male_Announcer', 'Chinese (Mandarin)_Sincere_Adult'):
        series.MM_VOICE = v
        a = series.tts(line)
        out = f'sample_{v.split("_", 1)[1]}.wav'
        with wave.open(out, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(series.SR); w.writeframes((a * 32767).astype(np.int16).tobytes())
        print('wrote', out)

def find_video(n):
    e = series.EPS[n]
    pat = f"第二部第{e['idx']}集_*.mp4" if e.get('season', 0) >= 4 else f"第{e.get('season', 0)}季第{e.get('idx', n)}集_*.mp4"
    hits = sorted(glob.glob(pat)) or [f'release/ep{n:02d}.mp4']
    return hits[0]

def revoice(n):
    e = series.Ep(n); wav = f'mm_s{n}.wav'
    e.audio(wav)
    src = find_video(n); tmp = f'_rv_{n}.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', '-ac', '2',
                    '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, src)
    subprocess.run(['cp', src, f'release/ep{n:02d}.mp4'], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', 'scale=720:1280', '-c:v', 'libx264', '-crf', '27', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', f'repo/site/videos/ep{n:02d}.mp4'], check=True)
    print('done', n, src, flush=True)

if __name__ == '__main__':
    if not os.environ.get('MINIMAX_API_KEY'): sys.exit('请先设置 MINIMAX_API_KEY')
    if sys.argv[1:] == ['sample']: sample()
    else:
        for n in ([int(x) for x in sys.argv[1:]] or sorted(series.EPS)): revoice(n)
