import numpy as np
SR, DUR = 44100, 110.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [164.8, 246.9, 329.6, 415.3]), (6.4, [146.8, 220.0, 293.7, 370.0]), (15.4, [130.8, 196.0, 261.6, 329.6]),
      (23.8, [116.5, 233.1, 293.7, 349.2]), (28.2, [146.8, 220.0, 293.7, 370.0]), (36.6, [164.8, 246.9, 329.6, 415.3]),
      (40.8, [130.8, 196.0, 261.6, 329.6]), (49.4, [146.8, 220.0, 293.7, 370.0]), (57.8, [164.8, 246.9, 329.6, 415.3]),
      (62.2, [130.8, 196.0, 261.6, 329.6]), (71.0, [116.5, 233.1, 277.2, 349.2]), (75.2, [110.0, 220.0, 261.6, 311.1]),
      (79.4, [103.8, 207.7, 246.9, 311.1]), (83.8, [146.8, 220.0, 293.7, 370.0])]
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
for k in range(40): blip(16 + k * 0.28, 180 + r.random() * 80, 0.08, 0.05)
blip(24.2, 140, 0.4, 0.6, -0.2)
for k in range(9): blip(32.8 + k * 0.15, 1100 + k * 60, 0.12, 0.06)
for f0 in (659, 830, 988): blip(36.8, f0, 0.2, 0.9)
for k in range(12): blip(42.8 + k * 0.5, 400, 0.1, 0.08)
for f0 in (523, 659, 784): blip(45.2, f0, 0.2, 0.9)
for k in range(10): blip(58.2 + k * 0.12, 1300, 0.12, 0.05)
for f0 in (784, 988, 1175): blip(59.6, f0, 0.2, 0.9)
for k in range(20): blip(66.8 + k * 0.18, 2500, 0.06, 0.03)
fx += 0.3 * low * ss(75.2, 76.5, t) * (1 - ss(83, 84, t))
for k in range(16): blip(75.6 + k * 0.5, 90, 0.3, 0.25, -0.2)
for f0 in (587, 740, 880, 1175): blip(84.0, f0, 0.2, 1.3)
np.save('bed10.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
