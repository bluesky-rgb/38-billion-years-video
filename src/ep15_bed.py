import numpy as np
SR, DUR = 44100, 115.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(16)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [110.0, 220.0, 261.6, 329.6]), (6.4, [130.8, 196.0, 261.6, 329.6]), (23.2, [146.8, 220.0, 261.6, 349.2]),
      (31.8, [130.8, 196.0, 261.6, 311.1]), (40.4, [110.0, 164.8, 220.0, 261.6]), (57.4, [103.8, 155.6, 207.7, 246.9]),
      (70.2, [98.0, 146.8, 196.0, 233.1]), (91.4, [87.3, 130.8, 174.6, 207.7]), (104.2, [110.0, 164.8, 220.0, 261.6]),
      (112.6, [130.8, 196.0, 261.6, 329.6]), (121.0, [116.5, 174.6, 233.1, 293.7])]
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
fx = 0.12 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
hi = band(5000, 2500)
fx += 0.35 * low * ss(44.6, 47, t) * (1 - ss(68.5, 70.2, t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))
fx += 0.18 * mid * ss(49, 51, t) * (1 - ss(56.5, 57.4, t))
for k in range(28): blip(58.6 + k * 0.4, 300 + 80 * (k % 5), 0.12, 0.06, 0.5)
for k in range(12): blip(70.6 + k * 0.33, 1400 + 120 * (k % 4), 0.06, 0.04, 0.8)
fx += 0.22 * hi * ss(87.2, 88, t) * (1 - ss(90.8, 91.4, t))
for k in range(16): blip(92.4 + k * 0.15, 70, 0.25, 0.15)
blip(97.4, 55, 0.6, 0.8)
for f0 in (220, 262, 330): blip(116.9, f0, 0.18, 1.6)
for tt in (123.0, 125.4): blip(tt, 45, 0.8, 0.5)
np.save('bed15.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
