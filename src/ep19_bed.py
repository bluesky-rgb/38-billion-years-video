import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(20)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [110.0, 164.8, 220.0, 261.6]), (6.4, [130.8, 196.0, 261.6, 329.6]), (19.0, [146.8, 220.0, 293.7, 349.2]),
      (27.4, [130.8, 196.0, 261.6, 329.6]), (44.2, [116.5, 174.6, 233.1, 293.7]), (52.6, [123.5, 185.0, 246.9, 311.1]),
      (65.6, [130.8, 196.0, 261.6, 329.6]), (74.0, [146.8, 220.0, 293.7, 370.0]), (82.8, [164.8, 246.9, 329.6, 415.3]),
      (95.6, [174.6, 261.6, 349.2, 440.0]), (104.2, [130.8, 196.0, 261.6, 311.1]), (112.8, [146.8, 220.0, 293.7, 370.0]), (117.0, [164.8, 246.9, 329.6, 392.0])]
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
fx += 0.06 * hi * ss(6, 7, t) * (1 - ss(43.6, 44.2, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t))
for k in range(10): blip(6.8 + k * 0.8, 900, 0.06, 0.06)
for k in range(3): blip(23.6 + k * 0.5, 120, 0.25, 0.3, -0.3)
for k in range(8): blip(28.0 + k * 1.0, 180, 0.15, 0.2)
for f0 in (659, 830, 988): blip(57.6, f0, 0.15, 1.0)
for f0 in (523, 659, 784): blip(62.6, f0, 0.15, 1.0)
for f0 in (523, 659, 784, 1046): blip(108.6, f0, 0.16, 1.4)
blip(119.6, 70, 0.4, 0.4)
np.save('bed19.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
