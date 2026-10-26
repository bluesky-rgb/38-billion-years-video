"""抖音版：原版不动，另出一份。
  - 开头 3 秒：一句提问（大字 + 旁白），下方小字标明系列和集数
  - 跳过"上集回顾"和完整片头，提问后直接进入正题
  - 字幕位置与原版相同
用法：python3 douyin.py 1 2 3 ...   （输出到 douyin/ 目录）
     python3 douyin.py stills 1     （预览开头）
"""
import os, sys, subprocess, wave, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import series
from PIL import Image, ImageFilter
from ep1 import W, H, FPS, text_img, put, ss, FB, FM

HOOK = 3.2; XFD = 0.3
CUT = series.R + 5.4      # 从原片这一刻接上（片名正在淡出，正题马上开始）
HOOKS = {
 1: ('今晚的月亮', '是怎么来的？', 30.0), 2: ('地球上的海水', '是从哪来的？', 40.0), 3: ('生命的零件', '能在瓶子里造出来吗？', 20.0),
 4: ('第一个会复制自己的', '是什么？', 40.0), 5: ('你身上每个细胞', '为什么都裹着一层油？', 35.0), 6: ('你吸的每一口氧气', '最早是谁造的？', 60.0),
 7: ('你的细胞里', '住着一个被吞掉的细菌', 30.0), 8: ('整个地球', '曾经冻成一个雪球', 95.0), 9: ('一个细胞', '怎么变成了你？', 60.0),
 10: ('为什么你的眼睛、嘴巴', '都长在前面？', 40.0), 11: ('你的脊椎', '最早是一根软棒', 50.0), 12: ('你的下巴', '原来是鱼的鳃', 30.0),
 13: ('鱼', '是怎么爬上岸的？', 60.0), 14: ('你在妈妈肚子里', '泡的是什么水？', 50.0), 15: ('九成生命', '一起消失了', 95.0),
 16: ('你的祖先', '曾经躲在恐龙脚下', 30.0), 17: ('恐龙统治地球一亿多年', '为什么一夜消失？', 30.0), 18: ('你的手为什么能握笔？', '答案在树上', 40.0),
 19: ('你的尾巴', '去哪了？', 30.0), 20: ('人类为什么', '要站起来走路？', 40.0), 21: ('第一把刀', '是怎么做出来的？', 25.0),
 22: ('火', '怎样改变了人类的大脑？', 75.0), 23: ('无论你是哪里人', '祖先都来自非洲', 30.0), 24: ('几十亿陌生人', '为什么能一起生活？', 85.0),
 25: ('人类为什么开始种地？', '其实种地更累', 50.0), 26: ('"这是我的"', '这句话是什么时候出现的？', 25.0), 27: ('最早的文字', '写的竟然是账本', 55.0),
 28: ('一张纸', '为什么能换来真东西？', 80.0), 29: ('你为什么', '会在红灯前停下？', 30.0), 30: ('你手里的手机', '连着两千年前的一条路', 72.0)}

def label(n):
    e = series.EPS[n]; s = e.get('season', 0); i = e.get('idx', n)
    return f'38 亿年家谱 · 第二部 · 第 {i} 集' if s >= 4 else f'38 亿年家谱 · 第 {s} 季 · 第 {i} 集'
def fitw(im, mw=940):
    return im if im.width <= mw else im.resize((mw, int(im.height * mw / im.width)), Image.LANCZOS)
def hook_layers(n):
    q1, q2, bt = HOOKS[n]; e = series.Ep(n)
    return e, e.mod.render(bt).filter(ImageFilter.GaussianBlur(7)), fitw(text_img(q1, FB, 84, (255, 255, 255), 6)), fitw(text_img(q2, FB, 96, (255, 215, 130), 6)), \
        text_img(label(n), FM, 40, (230, 230, 230), 3), fitw(text_img(f'《{e.c["title"]}》', FB, 56, (255, 235, 200), 4))
def hook_frame(t, base, L1, L2, Ls, Lt):
    k = 0.42 + 0.08 * ss(0, HOOK, t)
    img = Image.fromarray((np.asarray(base, np.float32) * k).astype(np.uint8))
    put(img, L1, W / 2, 820, ss(0.0, 0.3, t)); put(img, L2, W / 2, 960, ss(0.45, 0.8, t))
    put(img, Lt, W / 2, 1180, ss(1.0, 1.4, t)); put(img, Ls, W / 2, 1260, ss(1.0, 1.4, t))
    return img

def build(n):
    e, base, L1, L2, Ls, Lt = hook_layers(n)
    q1, q2, _ = HOOKS[n]
    os.makedirs('douyin', exist_ok=True)
    main = f'douyin/_main{n}.wav'; e.audio(main, drop_intro=True, quiet=True)
    with wave.open(main) as w: m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    SR = series.SR
    m = m[int(CUT * SR):].copy(); m[:int(0.4 * SR)] *= np.linspace(0, 1, int(0.4 * SR))
    q = series.tts(q1.strip('"') + '，' + q2)
    hook = np.zeros(int(HOOK * SR), np.float32); i0 = int(0.1 * SR); hook[i0:i0 + q.size] += q[:hook.size - i0]
    mix = np.concatenate([hook, m]); mix = mix / max(1e-6, np.abs(mix).max()) * 0.95
    aw = f'douyin/_mix{n}.wav'
    with wave.open(aw, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    out = f'douyin/抖音版_{n:02d}_{e.c["title"]}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', aw, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
                          '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', '-ac', '2',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    nh = int(HOOK * FPS); nf = int((e.D - CUT) * FPS); nx = int(XFD * FPS)
    for i in range(nh):
        fr = hook_frame(i / FPS, base, L1, L2, Ls, Lt)
        if i >= nh - nx:
            k = (i - (nh - nx)) / nx
            fr = Image.fromarray((np.asarray(fr, np.float32) * (1 - k) + np.asarray(e.frame(CUT), np.float32) * k).astype(np.uint8))
        p.stdin.write(fr.tobytes())
    for i in range(nf):
        p.stdin.write(e.frame(CUT + i / FPS).tobytes())
        if i % 900 == 0: print(n, i, nf, flush=True)
    p.stdin.close(); p.wait(); print('done', out, flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        ims = []
        for x in sys.argv[2:]:
            e, base, L1, L2, Ls, Lt = hook_layers(int(x)); ims.append(hook_frame(2.0, base, L1, L2, Ls, Lt))
        sheet = Image.new('RGB', (360 * len(ims), 640))
        for i, im in enumerate(ims): sheet.paste(im.resize((360, 640)), (360 * i, 0))
        os.makedirs('douyin', exist_ok=True); sheet.save('douyin/hooks.png'); print('ok')
    else:
        for x in sys.argv[1:]: build(int(x))
