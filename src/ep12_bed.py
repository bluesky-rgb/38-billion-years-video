import numpy as np
SR, DUR = 44100, 100.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [110.0, 220.0, 261.6, 329.6]), (6.4, [116.5, 233.1, 277.2, 349.2]), (15.4, [146.8, 220.0, 293.7, 370.0]),
      (23.8, [130.8, 196.0, 261.6, 329.6]), (28.0, [164.8, 246.9, 329.6, 415.3]), (36.6, [146.8, 220.0, 293.7, 370.0]),
      (45.2, [110.0, 220.0, 261.6, 329.6]), (53.6, [103.8, 207.7, 246.9, 311.1]), (57.8, [116.5, 233.1, 277.2, 349.2]),
      (62.2, [146.8, 220.0, 293.7, 370.0]), (70.6, [164.8, 246.9, 329.6, 415.3])]
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = (ss(st - 1.2, st + 1.2, t) if st > 0 else 1) * (1 - ss(en - 1.2, en + 1.2, t))
    for j, f in enumerate(fs):
        music += tone(f * (1 + 0.0015 * j), 0.08) * (0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)) * w
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * 0
n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
low = band(150, 120); mid = band(700, 500)
fx = 0.14 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
for k in range(8): blip(7 + k * 0.5, 240, 0.12, 0.15)
for k in range(6): blip(16 + k * 0.4, 660 + k * 50, 0.15, 0.1)
fx += 0.2 * mid * ss(24, 26, t) * (1 - ss(29, 30, t))
for k in range(8): blip(28.4 + k * 1.0, 180, 0.4, 0.08)
for f0 in (784, 988, 1175): blip(32.6, f0, 0.2, 0.9)
for f0 in (523, 659, 784): blip(37.8, f0, 0.22, 1.1)
for k in range(10): blip(45.4 + k * 0.4, 160, 0.35, 0.06)
fx += 0.35 * low * ss(53.8, 54.8, t) * (1 - ss(57, 57.8, t))
for k in range(5): blip(54.2 + k * 0.8, 90, 0.5, 0.15, -0.3)
for f0 in (587, 740, 880, 1175): blip(70.8, f0, 0.2, 1.4)
np.save('bed12.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
