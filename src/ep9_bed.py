import numpy as np
SR, DUR = 44100, 125.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [130.8, 196.0, 261.6, 329.6]), (15.4, [146.8, 220.0, 293.7, 370.0]),
      (23.8, [116.5, 233.1, 277.2, 349.2]), (28.0, [146.8, 220.0, 293.7, 370.0]), (36.6, [130.8, 196.0, 261.6, 329.6]),
      (45.2, [164.8, 246.9, 329.6, 415.3]), (53.6, [130.8, 196.0, 261.6, 311.1]), (57.8, [146.8, 220.0, 293.7, 370.0]),
      (62.2, [116.5, 233.1, 293.7, 349.2]), (70.6, [130.8, 196.0, 261.6, 329.6]), (75.0, [110.0, 220.0, 261.6, 329.6]),
      (79.2, [146.8, 220.0, 293.7, 370.0]), (83.6, [164.8, 246.9, 329.6, 415.3]), (96.2, [146.8, 220.0, 293.7, 370.0])]
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
for k in range(60): blip(1 + k * 1.6 + r.random(), 300 + r.random() * 500, 0.1, 0.05, 3)
blip(18.4, 660, 0.3, 0.2); for_ = [blip(20.0 + k * 0.15, 990, 0.12, 0.05) for k in range(3)]
fx += 0.25 * low * ss(24, 25.5, t) * (1 - ss(29, 30, t)); blip(26.0, 150, 0.4, 0.3, -0.3)
for j in range(5): blip(32.8 + j * 0.6, 523 * 2 ** (j * 2 / 12), 0.25, 0.25)
for k in range(8): blip(41.0 + k * 0.12, 880 + k * 40, 0.12, 0.1)
for f0 in (659, 830, 988): blip(45.6, f0, 0.2, 0.9)
for k in range(8): blip(58.0 + k * 0.12, 1320 if k % 2 else 990, 0.15, 0.06)
blip(66.8, 300, 0.3, 0.5, -0.5)
for f0 in (523, 659, 784): blip(70.8, f0, 0.2, 1.0)
for f0 in (587, 740, 880, 1175): blip(83.8, f0, 0.2, 1.4)
music += 0.03 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * ss(83, 87, t)
np.save('bed9.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
