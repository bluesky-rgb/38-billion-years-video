import numpy as np
SR, DUR = 44100, 80.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [130.8, 196.0, 261.6, 329.6]), (15.2, [116.5, 233.1, 293.7, 349.2]),
      (23.6, [130.8, 196.0, 261.6, 311.1]), (27.8, [146.8, 220.0, 293.7, 370.0]), (36.2, [164.8, 246.9, 329.6, 415.3]),
      (40.4, [146.8, 220.0, 293.7, 370.0]), (48.8, [130.8, 196.0, 261.6, 329.6]), (53, [146.8, 220.0, 293.7, 370.0]),
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
for k in range(45): blip(1 + k * 1.6 + r.random(), 300 + r.random() * 500, 0.1, 0.05, 3)
for k in range(12): blip(11 + k * 0.33, 1200 + r.random() * 300, 0.08, 0.04)
fx += 0.2 * mid * ss(20.5, 22.5, t) * (1 - ss(22.5, 23.6, t))
blip(23.2, 180, 0.5, 0.2, -0.3)
for k in range(10): blip(23.8 + k * 0.4, 330, 0.12, 0.08)
for k in range(10): blip(28.2 + k * 0.4, 1320, 0.1, 0.05)
for f0 in (659, 830, 988): blip(36.4, f0, 0.2, 1.0)
for i, tt in enumerate([42.6, 43.8, 45.0]): blip(tt, 784 * 2 ** (i * 2 / 12), 0.3, 0.3)
for f0 in (523, 659, 784, 1046): blip(49.0, f0, 0.22, 1.2)
for f0 in (587, 740, 880): blip(58.8, f0, 0.2, 1.0)
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(48, 52, t)
np.save('bed7.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
