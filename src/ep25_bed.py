import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(26)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [174.6, 261.6, 349.2, 440.0]), (6.4, [146.8, 220.0, 293.7, 370.0]), (15.0, [130.8, 196.0, 261.6, 329.6]),
      (23.4, [164.8, 246.9, 329.6, 415.3]), (32.0, [146.8, 220.0, 293.7, 370.0]), (44.8, [130.8, 196.0, 261.6, 329.6]),
      (61.6, [174.6, 261.6, 349.2, 440.0]), (66.0, [164.8, 246.9, 329.6, 415.3]), (78.8, [110.0, 164.8, 220.0, 261.6]),
      (91.6, [116.5, 174.6, 233.1, 293.7]), (100.0, [146.8, 220.0, 293.7, 370.0]), (104.4, [110.0, 164.8, 220.0, 261.6]),
      (108.6, [130.8, 196.0, 261.6, 329.6]), (117.2, [146.8, 220.0, 293.7, 370.0]), (121.4, [116.5, 174.6, 233.1, 293.7])]
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
fx = 0.03 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
hi = band(5000, 2500)
fx += 0.06 * hi * ss(32, 33, t) * (1 - ss(60.8, 61.4, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t))
for k in range(14): blip(45.6 + k * 0.18, 1400 + 200 * (k % 3), 0.05, 0.04)
for k in range(6): blip(53.6 + k * 0.6, 2200, 0.08, 0.06)
for f0 in (523, 659, 784): blip(61.8, f0, 0.15, 1.2)
for tt in (66.4, 70.6, 74.8): blip(tt, 660, 0.12, 0.6)
for k in range(4): blip(79.2 + k * 0.5, 70, 0.3, 0.4)
for k in range(8): blip(92.0 + k * 0.5, 150, 0.12, 0.1)
blip(106.0, 60, 0.4, 0.6)
for k in range(10): blip(117.6 + k * 0.28, 900, 0.06, 0.08)
np.save('bed25.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
