import numpy as np
SR, DUR = 44100, 80.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [130.8, 196.0, 261.6, 329.6]), (6.4, [116.5, 233.1, 293.7, 349.2]), (14.8, [130.8, 196.0, 261.6, 311.1]),
      (19, [146.8, 220.0, 293.7, 370.0]), (27.4, [164.8, 246.9, 329.6, 415.3]), (36, [146.8, 220.0, 293.7, 370.0]),
      (44.4, [130.8, 196.0, 261.6, 329.6]), (48.6, [110.0, 220.0, 277.2, 329.6]), (53, [146.8, 220.0, 293.7, 370.0]),
      (57.2, [130.8, 196.0, 261.6, 329.6]), (61.8, [146.8, 220.0, 293.7, 370.0])]
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = (ss(st - 1.2, st + 1.2, t) if st > 0 else 1) * (1 - ss(en - 1.2, en + 1.2, t))
    for j, f in enumerate(fs):
        music += tone(f * (1 + 0.0015 * j), 0.08) * (0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)) * w
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(53, 57, t)
n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
low = band(150, 120); mid = band(700, 500)
fx = 0.14 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
for i in range(10): blip(7.0 + i * 0.75, 880, 0.25, 0.06); blip(8.0 + i * 0.75, 520, 0.12, 0.2, -0.6)
for k in range(45): blip(1 + k * 1.6 + r.random(), 300 + r.random() * 500, 0.1, 0.05, 3)
for i in range(16): blip(27.6 + i * 0.17, 440 * 2 ** (i / 8), 0.18, 0.12)
fx += 0.25 * mid * ss(31.6, 33.5, t) * (1 - ss(33.5, 35.2, t))
for f0 in (784, 988, 1175): blip(38.6, f0, 0.22, 0.6)
for i in range(4): blip(40.6 + i * 0.9, 660, 0.2, 0.15)
blip(51.2, 220, 0.6, 0.12, -0.5); blip(51.25, 1200, 0.2, 0.05)
for f0 in (523, 659, 784, 1046): blip(57.3, f0, 0.2, 0.9)
np.save('bed5.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
