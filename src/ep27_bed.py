import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(28)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [130.8, 196.0, 261.6, 311.1]), (10.6, [146.8, 220.0, 293.7, 370.0]), (19.0, [130.8, 196.0, 261.6, 329.6]),
      (36.0, [146.8, 220.0, 293.7, 370.0]), (49.0, [164.8, 246.9, 329.6, 415.3]), (61.8, [174.6, 261.6, 349.2, 440.0]),
      (70.4, [146.8, 220.0, 293.7, 370.0]), (87.4, [174.6, 261.6, 349.2, 440.0]), (95.8, [196.0, 293.7, 392.0, 493.9]),
      (100.2, [146.8, 220.0, 293.7, 370.0]), (108.8, [130.8, 196.0, 261.6, 311.1]), (117.2, [164.8, 246.9, 329.6, 415.3])]
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
fx += 0.05 * band(800, 600) * ss(15, 16, t) * (1 - ss(18.4, 19.0, t))
for k in range(5): blip(19.4 + k * 0.4, 700, 0.1, 0.08)
for k in range(5): blip(32.0 + k * 0.4, 400, 0.12, 0.06)
blip(36.4, 900, 0.2, 0.2, -0.5)
for k in range(40): blip(53.4 + k * 0.165, 1600 + 150 * (k % 3), 0.06, 0.03)
for f0 in (523, 659, 784, 1046): blip(96.0, f0, 0.18, 1.8)
for k in range(3): blip(109.2 + k * 0.5, 600, 0.12, 0.3)
for k in range(5): blip(117.6 + k * 0.3, 2400, 0.1, 0.25)
np.save('bed27.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
