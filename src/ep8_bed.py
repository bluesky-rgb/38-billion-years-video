import numpy as np
SR, DUR = 44100, 150.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [130.8, 196.0, 261.6, 329.6]), (15.2, [110.0, 220.0, 261.6, 329.6]),
      (27.8, [116.5, 233.1, 293.7, 349.2]), (32.4, [146.8, 220.0, 293.7, 349.2]), (40.8, [130.8, 196.0, 261.6, 311.1]),
      (45.0, [116.5, 233.1, 277.2, 349.2]), (53.6, [146.8, 220.0, 293.7, 370.0]), (62.0, [130.8, 196.0, 261.6, 311.1]),
      (70.4, [116.5, 233.1, 293.7, 349.2]), (79.0, [110.0, 220.0, 261.6, 329.6]), (91.6, [103.8, 207.7, 246.9, 311.1]),
      (100.2, [103.8, 207.7, 246.9, 311.1]), (108.8, [116.5, 233.1, 293.7, 349.2]), (117.2, [130.8, 196.0, 261.6, 329.6]),
      (121.4, [146.8, 220.0, 293.7, 370.0]), (125.8, [164.8, 246.9, 329.6, 415.3])]
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
hi = band(5000, 2500); wind = band(900, 700)
fx += 0.25 * low * ss(15, 17, t) * (1 - ss(31, 32.2, t))
for k in range(4): blip(33.5 + k * 1.3, 85, 0.5, 0.5, -0.2)
blip(38.4, 60, 0.8, 0.8, -0.3)
fx += 0.3 * low * ss(40.8, 43, t) * (1 - ss(46, 48, t))
blip(45.2, 70, 0.9, 0.6, -0.3); blip(45.25, 900, 0.3, 0.08)
fx += 0.25 * hi * ss(57.8, 59, t) * (1 - ss(69.4, 70.2, t))
for k in range(18): blip(66.4 + k * 0.2, 500 + r.random() * 300, 0.08, 0.05)
fx += 0.35 * wind * ss(83, 86, t) * (1 - ss(98.8, 100, t)) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 4))
for k in range(30): blip(100.6 + k * 0.27 + r.random() * 0.2, 300 + r.random() * 300, 0.1, 0.05, 3)
fx += 0.3 * low * ss(108.8, 110.5, t) * (1 - ss(117.6, 119, t))
for k in range(12): blip(109.5 + k * 0.7, 70, 0.35, 0.4, -0.2)
for k in range(40): blip(117.4 + k * 0.1, 900 + r.random() * 900, 0.08, 0.05)
for f0 in (587, 740, 880, 1175): blip(125.9, f0, 0.2, 1.2)
music *= 1 - 0.4 * ss(96, 100, t) * (1 - ss(107, 110, t))
np.save('bed8.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
