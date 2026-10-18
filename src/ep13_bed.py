import numpy as np
SR, DUR = 44100, 105.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(15)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [164.8, 246.9, 329.6, 415.3]), (14.8, [146.8, 220.0, 293.7, 370.0]),
      (19.0, [174.6, 261.6, 349.2, 440.0]), (27.8, [130.8, 196.0, 261.6, 311.1]), (36.2, [146.8, 220.0, 293.7, 370.0]),
      (40.8, [130.8, 196.0, 261.6, 329.6]), (53.8, [164.8, 246.9, 329.6, 415.3]), (66.8, [146.8, 220.0, 293.7, 370.0]),
      (75.2, [116.5, 233.1, 277.2, 349.2]), (79.6, [164.8, 246.9, 329.6, 415.3])]
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
hi = band(5000, 2500)
fx += 0.12 * hi * ss(6, 8, t) * (1 - ss(26, 27.6, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6))
for k in range(16): blip(11 + k * 0.25, 1400 + 60 * k, 0.06, 0.05)
for f0 in (587, 740, 880, 1175): blip(19.2, f0, 0.2, 1.4)
for k in range(30): blip(23.6 + k * 0.12, 3000 + r.random() * 800, 0.05, 0.02)
fx += 0.18 * mid * ss(28, 30, t) * (1 - ss(39, 40.6, t))
for k in range(5): blip(33.0 + k * 1.3, 500, 0.25, 0.25, 1.5)
for j in range(3): blip(41.4 + j * 1.2, 523 * 2 ** (j * 4 / 12), 0.25, 0.4)
for k in range(8): blip(45.2 + k * 0.6, 120, 0.3, 0.12)
for f0 in (659, 830, 988): blip(54.0, f0, 0.2, 1.0)
for k in range(14): blip(67 + k * 0.5, 110, 0.25, 0.1)
for f0 in (523, 659, 784, 1046): blip(79.8, f0, 0.2, 1.3)
np.save('bed13.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
