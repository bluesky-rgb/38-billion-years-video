import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(19)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [164.8, 246.9, 329.6, 415.3]), (14.8, [174.6, 261.6, 349.2, 440.0]),
      (31.8, [146.8, 220.0, 293.7, 370.0]), (44.4, [164.8, 246.9, 329.6, 415.3]), (57.2, [130.8, 196.0, 261.6, 329.6]),
      (69.8, [174.6, 261.6, 349.2, 440.0]), (82.8, [164.8, 246.9, 329.6, 415.3]), (95.6, [196.0, 293.7, 392.0, 493.9]),
      (99.9, [130.8, 196.0, 261.6, 311.1]), (108.4, [116.5, 174.6, 233.1, 293.7]), (116.8, [110.0, 164.8, 220.0, 261.6])]
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
fx += 0.07 * hi * ss(15, 16, t) * (1 - ss(31.2, 31.8, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t))
for k in range(12): blip(15.6 + k * 1.3, 2400 + 300 * (k % 4), 0.06, 0.08, 0.3)
for k in range(8): blip(23.6 + k * 0.4, 300, 0.1, 0.05)
blip(34.0, 70, 0.4, 0.5)
for f0 in (523, 659, 784): blip(44.8, f0, 0.15, 1.0)
for f0 in (587, 740, 880): blip(70.0, f0, 0.15, 1.2)
blip(59.4, 90, 0.3, 0.3)
for f0 in (523, 659, 784, 1046): blip(83.0, f0, 0.18, 1.6)
fx += 0.12 * band(400, 300) * ss(100.4, 104, t) * (1 - ss(108, 108.4, t))
for k in range(3): blip(117.2 + k * 0.7, 60, 0.35, 0.4)
np.save('bed18.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
