import subprocess, os, glob, wave, numpy as np

B = glob.glob('dl/bin/*/bin')[0]; LIB = glob.glob('dl/bin/*/lib')[0]
M = [d for d in glob.glob('dl/model/*') if os.path.isdir(d)]; M = M[0] if M else 'dl/model'
SR, DUR = 44100, 80.0
LINES = [
    (1.3, '三十八亿年家谱。第零季，第三集，生命的原料。'),
    (6.5, '生命的零件，最初是从哪来的？'),
    (10.5, '一九五三年，学生米勒，做了一个著名的实验。'),
    (14.9, '他把早期地球的气体和水，封进玻璃瓶，'),
    (19.3, '再用电火花，模拟闪电。'),
    (23.5, '一周后，瓶里的水变成了褐色。'),
    (27.9, '里面出现了氨基酸，蛋白质的基本零件。'),
    (33.1, '天上，也在给地球送原料。'),
    (37.3, '一九六九年，一颗陨石坠落在澳大利亚。'),
    (41.9, '科学家在里面，找到了几十种氨基酸。'),
    (47.1, '这些小分子，在海水里漂荡、相遇。'),
    (51.3, '有些开始手拉手，连成长链。'),
    (55.7, '离一个会复制自己的分子，只差一步了。'),
    (62.4, '下一集，会复制的分子。'),
]
env = dict(os.environ, LD_LIBRARY_PATH=LIB); os.makedirs('vo3', exist_ok=True)
t = np.arange(int(SR * DUR)) / SR
vo = np.zeros(t.size, np.float32)
for i, (t0, s) in enumerate([] if os.environ.get('BEDONLY') else LINES):
    p = f'vo3/{i:02d}.wav'; q = p.replace('.wav', '_44.wav')
    subprocess.run([f'{B}/sherpa-onnx-offline-tts', f'--vits-model={M}/model.onnx', f'--vits-lexicon={M}/lexicon.txt',
                    f'--vits-tokens={M}/tokens.txt', f'--vits-dict-dir={M}/dict', '--sid=1',
                    f'--output-filename={p}', s], env=env, check=True, capture_output=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', p, '-ar', str(SR), '-ac', '1', q], check=True)
    with wave.open(q) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    a = a / (np.abs(a).max() + 1e-6) * 0.9
    st = int(t0 * SR); en = min(st + a.size, vo.size); vo[st:en] += a[:en - st]
    nxt = LINES[i + 1][0] if i + 1 < len(LINES) else DUR
    print(f'{t0:5.1f} {a.size / SR:4.1f}s / {nxt - t0:4.1f}s {s}')

def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6, [130.8, 196.0, 261.6, 329.6]),
      (19, [116.5, 233.1, 293.7, 349.2]), (32.6, [110.0, 220.0, 277.2, 329.6]),
      (46.6, [146.8, 220.0, 293.7, 370.0]), (55.6, [164.8, 246.9, 329.6, 392.0])]
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = (ss(st - 1.5, st + 1.5, t) if st > 0 else 1) * (1 - ss(en - 1.5, en + 1.5, t))
    for j, f in enumerate(fs):
        music += tone(f * (1 + 0.0015 * j), 0.08) * (0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)) * w
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(46, 49, t)

r = np.random.default_rng(8); n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
rain = band(4000, 3000); hiss = band(2500, 2000); low = band(120, 100); mid = band(500, 400); hi = band(6000, 2500)
fx = np.zeros_like(t)
for k in range(260):
    tt = 6.5 + k * 0.1 + r.random() * 0.08
    if tt > 32: break
    d = t - tt; f0 = 600 + r.random() * 900
    fx += (d >= 0) * 0.12 * np.sin(2 * np.pi * f0 * (1 + 2 * np.clip(d, 0, None)) * np.clip(d, 0, None)) * np.exp(-np.clip(d, 0, None) / 0.03)
zap = (np.floor(t * 30) % 5 < 3) * (t > 18.6) * (t < 32.2)
fx += 0.35 * hi * zap * (0.6 + 0.4 * np.sin(2 * np.pi * 50 * t))
for t0 in [33.6, 35.0, 36.3, 37.4, 38.5]:
    d = t - t0; dd = np.clip(d, 0, None)
    fx += (d >= 0) * (d < 1.3) * 0.5 * hiss * (dd / 1.3) ** 2
    e = t - t0 - 1.3; ee = np.clip(e, 0, None)
    fx += (e >= 0) * (0.7 * mid * np.exp(-ee / 0.15) + 0.6 * low * np.exp(-ee / 1.0))
fx += 0.25 * low * ss(46.6, 48, t) * (1 - ss(63, 66, t))
for k in range(40):
    tt = 47 + k * 0.38 + r.random() * 0.3
    d = t - tt; f0 = 300 + r.random() * 500
    fx += (d >= 0) * 0.15 * np.sin(2 * np.pi * f0 * (1 + 3 * np.clip(d, 0, None)) * np.clip(d, 0, None)) * np.exp(-np.clip(d, 0, None) / 0.05)
if os.environ.get('BEDONLY'):
    np.save('bed3.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); raise SystemExit
venv = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.5 * np.clip(venv / 0.05, 0, 1)
mix = (music / np.abs(music).max() * 0.3 + fx * 0.45) * duck + vo
mix *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix = mix / np.abs(mix).max() * 0.95
with wave.open('ep3_mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
