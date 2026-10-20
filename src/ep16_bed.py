import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(17)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [130.8, 196.0, 261.6, 329.6]), (6.4, [146.8, 220.0, 293.7, 370.0]), (23.2, [164.8, 246.9, 329.6, 415.3]),
      (31.8, [130.8, 196.0, 261.6, 311.1]), (40.4, [110.0, 164.8, 220.0, 261.6]), (48.6, [130.8, 196.0, 261.6, 329.6]),
      (61.4, [116.5, 174.6, 233.1, 293.7]), (74.0, [130.8, 196.0, 261.6, 329.6]), (82.6, [146.8, 220.0, 293.7, 370.0]),
      (95.2, [174.6, 261.6, 349.2, 440.0]), (99.4, [110.0, 164.8, 220.0, 261.6]), (116.2, [130.8, 196.0, 261.6, 329.6]), (120.8, [116.5, 174.6, 233.1, 311.1])]
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
fx = 0.08 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
hi = band(5000, 2500)
for k in range(10): blip(10.8 + k * 0.42, 110, 0.18, 0.12)
for k in range(12): blip(23.6 + k * 0.33, 85, 0.25, 0.15)
for k in range(5): blip(27.2 + k * 0.9, 50, 0.4, 0.4)
fx += 0.08 * hi * ss(40.4, 42, t) * (1 - ss(60.8, 61.4, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
for f0 in (660, 880, 1320): blip(74.2, f0, 0.15, 1.2)
for k in range(8): blip(75 + k * 0.5, 2400, 0.05, 0.05)
for f0 in (523, 659, 784): blip(91.2, f0, 0.16, 1.4)
for f0 in (523, 659, 784, 1046): blip(95.4, f0, 0.18, 1.6)
for tt in (99.8, 101.0): blip(tt, 45, 0.6, 0.5)
fx += 0.15 * band(300, 200) * ss(121, 124.5, t) * (1 - ss(129, 131, t))
np.save('bed16.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
