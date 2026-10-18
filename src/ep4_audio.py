import subprocess, os, glob, wave, numpy as np

B = glob.glob('dl/bin/*/bin')[0]; LIB = glob.glob('dl/bin/*/lib')[0]
M = [d for d in glob.glob('dl/model/*') if os.path.isdir(d)]; M = M[0] if M else 'dl/model'
SR, DUR = 44100, 80.0
LINES = [
    (1.3, '三十八亿年家谱。第零季，第四集，会复制的分子。'),
    (6.5, '今天的细胞里，DNA存储信息，'),
    (10.5, '蛋白质负责干活。'),
    (14.5, '可它们，谁也离不开谁。'),
    (18.7, '那最早，到底先有谁？'),
    (22.9, '科学家找到了一个两面手，RNA。'),
    (27.1, '它能像DNA一样，存储信息，'),
    (31.1, '又能像蛋白质一样，催化反应。'),
    (35.5, '一条RNA，可以当作模板，'),
    (39.7, '吸来散落的零件，按规则配对，'),
    (43.9, '拼出新链，再分开。'),
    (47.9, '一变二，二变四，越来越多。'),
    (52.3, '复制时，偶尔会出错。'),
    (56.3, '复制得更快的，后代就更多。'),
    (60.1, '自然选择，从这一刻开始了。'),
    (64.0, '下一集，第一个细胞。'),
]
env = dict(os.environ, LD_LIBRARY_PATH=LIB); os.makedirs('vo4', exist_ok=True)
t = np.arange(int(SR * DUR)) / SR
vo = np.zeros(t.size, np.float32)
for i, (t0, s) in enumerate([] if os.environ.get('BEDONLY') else LINES):
    p = f'vo4/{i:02d}.wav'; q = p.replace('.wav', '_44.wav')
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
CH = [(0, [146.8, 220.0, 293.7, 349.2]), (14.4, [116.5, 233.1, 293.7, 349.2]),
      (18.6, [130.8, 196.0, 261.6, 311.1]), (22.6, [146.8, 220.0, 293.7, 370.0]),
      (35.2, [130.8, 196.0, 261.6, 329.6]), (47.6, [146.8, 220.0, 293.7, 370.0]),
      (52.2, [116.5, 233.1, 293.7, 349.2]), (56.2, [130.8, 196.0, 261.6, 329.6]), (60, [146.8, 220.0, 293.7, 370.0])]
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = (ss(st - 1.5, st + 1.5, t) if st > 0 else 1) * (1 - ss(en - 1.5, en + 1.5, t))
    for j, f in enumerate(fs):
        music += tone(f * (1 + 0.0015 * j), 0.08) * (0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)) * w
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(47, 50, t)

r = np.random.default_rng(8); n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
rain = band(4000, 3000); hiss = band(2500, 2000); low = band(120, 100); mid = band(500, 400); hi = band(6000, 2500)
fx = np.zeros_like(t)
def blip(tt, f0, amp, dec=0.08):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * dd) * np.exp(-dd / dec)
for i in range(12): blip(22.8 + i * 0.25, 660 + 40 * i, 0.25)
for i in range(12): blip(40.3 + i * 0.32, 880, 0.35, 0.06); blip(40.3 + i * 0.32, 1320, 0.2, 0.04)
for e in range(7): blip(47.6 + e * 0.62, 523.3 * 2 ** (e / 12 * 2), 0.35, 0.25)
for f0 in (1046, 1318, 1568): blip(53.1, f0, 0.25, 0.5)
fx += 0.12 * low * (1 - ss(66, 68, t))
for k in range(30):
    tt = 1 + k * 2.1 + r.random(); d = t - tt; f0 = 300 + r.random() * 400
    fx += (d >= 0) * 0.1 * np.sin(2 * np.pi * f0 * (1 + 3 * np.clip(d, 0, None)) * np.clip(d, 0, None)) * np.exp(-np.clip(d, 0, None) / 0.05)
if os.environ.get('BEDONLY'):
    np.save('bed4.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); raise SystemExit
venv = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.5 * np.clip(venv / 0.05, 0, 1)
mix = (music / np.abs(music).max() * 0.3 + fx * 0.45) * duck + vo
mix *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix = mix / np.abs(mix).max() * 0.95
with wave.open('ep4_mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
