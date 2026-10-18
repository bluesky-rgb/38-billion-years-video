import numpy as np
SR, DUR = 44100, 80.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [130.8, 196.0, 261.6, 329.6]), (15.4, [146.8, 220.0, 293.7, 370.0]),
      (23.8, [164.8, 246.9, 329.6, 415.3]), (33.2, [130.8, 196.0, 261.6, 311.1]), (41.6, [146.8, 220.0, 293.7, 370.0]),
      (45.8, [116.5, 233.1, 277.2, 349.2]), (54.6, [110.0, 220.0, 261.6, 329.6]), (58.8, [130.8, 196.0, 261.6, 329.6]),
      (67.2, [146.8, 220.0, 293.7, 370.0])]
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
for k in range(20): blip(6.6 + k * 0.4 + r.random() * 0.2, 700 + r.random() * 300, 0.12, 0.05)
for k in range(80): blip(24 + k * 0.38 + r.random() * 0.3, 400 + r.random() * 600, 0.1, 0.04, 4)
hi = band(5000, 2500)
fx += 0.12 * hi * ss(15.2, 17, t) * (1 - ss(53.8, 54.4, t)) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 5))
for k in range(30): blip(33.5 + k * 0.28, 250 + r.random() * 120, 0.12, 0.1)
fx += 0.3 * low * ss(45.8, 47.5, t) * (1 - ss(52.5, 54.4, t))
for f0 in (659, 830, 988, 1318): blip(58.9, f0, 0.2, 1.0)
for k in range(7): blip(63.4 + k * 0.5, 1500, 0.1, 0.06)
for f0 in (523, 659, 784, 1046): blip(67.3, f0, 0.22, 1.2)
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(58, 62, t)
np.save('bed6.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
