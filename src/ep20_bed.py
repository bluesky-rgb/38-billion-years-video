import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(21)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (10.6, [110.0, 164.8, 220.0, 261.6]), (19.0, [98.0, 146.8, 196.0, 246.9]),
      (27.4, [130.8, 196.0, 261.6, 329.6]), (40.2, [164.8, 246.9, 329.6, 415.3]), (53.0, [130.8, 196.0, 261.6, 329.6]),
      (74.2, [146.8, 220.0, 293.7, 370.0]), (86.8, [164.8, 246.9, 329.6, 415.3]), (95.4, [174.6, 261.6, 349.2, 440.0]),
      (103.8, [116.5, 174.6, 233.1, 293.7]), (112.4, [146.8, 220.0, 293.7, 370.0])]
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
fx += 0.25 * low * ss(15.0, 17, t) * (1 - ss(22.4, 23.0, t))
blip(19.3, 50, 0.6, 1.0, -0.2)
fx += 0.05 * hi * ss(32, 33, t) * (1 - ss(52.4, 53, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t))
for k in range(8): blip(40.6 + k * 0.5, 160, 0.15, 0.08)
for k in range(4): blip(57.6 + k * 4.2, 880, 0.12, 0.6)
for k in range(10): blip(87.4 + k * 0.48, 140, 0.2, 0.1)
for f0 in (523, 659, 784): blip(99.9, f0, 0.16, 1.2)
for k in range(10): blip(117.0 + k * 1.047, 1500, 0.12, 0.05)
np.save('bed20.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
