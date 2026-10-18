import subprocess, os, glob, wave, numpy as np

B = glob.glob('dl/bin/*/bin')[0]; LIB = glob.glob('dl/bin/*/lib')[0]
M = [d for d in glob.glob('dl/model/*') if os.path.isdir(d)]; M = M[0] if M else 'dl/model'
SR, DUR = 44100, 80.0
LINES = [
    (1.3, '三十八亿年家谱。第零季，第二集，第一场雨。'),
    (6.5, '地壳冷却后，空气里充满了水蒸气。'),
    (10.5, '温度一降，水汽开始凝结成雨。'),
    (15.7, '一场大雨，可能下了数百万年。'),
    (20.1, '雨点打在滚烫的岩石上，又化成蒸汽。'),
    (25.5, '岩石慢慢冷却，雨水终于留了下来。'),
    (29.7, '低洼处，越积越满。'),
    (33.9, '原始海洋，诞生了。'),
    (39.1, '那时的月亮，离地球近得多，'),
    (43.5, '在天上看起来，大好几倍。'),
    (48.7, '巨大的潮汐，日夜搅动着海洋。'),
    (53.7, '空气中几乎没有氧气，紫外线直射海面。'),
    (58.5, '但正是在这片海里，生命的原料开始聚集。'),
    (62.4, '下一集，生命的原料。'),
]
env = dict(os.environ, LD_LIBRARY_PATH=LIB); os.makedirs('vo2', exist_ok=True)
t = np.arange(int(SR * DUR)) / SR
vo = np.zeros(t.size, np.float32)
for i, (t0, s) in enumerate([] if os.environ.get('BEDONLY') else LINES):
    p = f'vo2/{i:02d}.wav'; q = p.replace('.wav', '_44.wav')
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
CH = [(0, [146.8, 220.0, 293.7, 349.2]), (15, [130.8, 196.0, 261.6, 311.1]),
      (26, [116.5, 233.1, 293.7, 349.2]), (38.4, [146.8, 220.0, 293.7, 370.0]),
      (53, [130.8, 196.0, 261.6, 329.6]), (58, [146.8, 220.0, 293.7, 370.0])]
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = (ss(st - 1.5, st + 1.5, t) if st > 0 else 1) * (1 - ss(en - 1.5, en + 1.5, t))
    for j, f in enumerate(fs):
        music += tone(f * (1 + 0.0015 * j), 0.08) * (0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)) * w
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(38, 41, t)

r = np.random.default_rng(8); n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
rain = band(4000, 3000); hiss = band(2500, 2000); low = band(120, 100); mid = band(500, 400)
fx = 0.45 * rain * ss(14.6, 16, t) * (1 - ss(37.4, 38.6, t))
fx += 0.25 * rain * ss(9, 14.5, t) * (1 - ss(14.6, 15.3, t))
for b in [17.6, 22.9, 27.4, 31.8, 35.2]:
    d = t - b; on = d >= 0; dd = np.clip(d, 0, None)
    fx += on * (0.9 * mid * np.exp(-dd / 0.12) + 0.8 * low * np.exp(-np.clip(dd - 0.3, 0, None) / 1.6) * ss(b + 0.1, b + 0.5, t)
                + 0.5 * mid * np.exp(-np.clip(dd - 0.3, 0, None) / 1.2) * ss(b + 0.1, b + 0.6, t))
waves = mid * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6.5)) ** 2
fx += 0.35 * waves * ss(38.4, 41, t) * (1 - ss(63, 66, t))
for k in range(60):
    tt = 20 + k * 0.08 + r.random() * 0.05
    d = t - tt; fx += (d >= 0) * 0.15 * hiss * np.exp(-np.clip(d, 0, None) / 0.25) * (k % 3 == 0)

if os.environ.get('BEDONLY'):
    np.save('bed2.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); raise SystemExit
venv = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.5 * np.clip(venv / 0.05, 0, 1)
mix = (music / np.abs(music).max() * 0.3 + fx * 0.45) * duck + vo
mix *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix = mix / np.abs(mix).max() * 0.95
with wave.open('ep2_mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
