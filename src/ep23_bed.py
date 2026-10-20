import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(24)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [146.8, 220.0, 293.7, 370.0]), (6.4, [130.8, 196.0, 261.6, 329.6]), (10.6, [110.0, 164.8, 220.0, 261.6]),
      (23.2, [146.8, 220.0, 293.7, 370.0]), (40.2, [164.8, 246.9, 329.6, 415.3]), (48.8, [174.6, 261.6, 349.2, 440.0]),
      (61.8, [130.8, 196.0, 261.6, 329.6]), (74.4, [146.8, 220.0, 293.7, 349.2]), (79.8, [164.8, 246.9, 329.6, 415.3]),
      (92.6, [130.8, 196.0, 261.6, 329.6]), (105.4, [146.8, 220.0, 293.7, 370.0]), (109.6, [174.6, 261.6, 349.2, 440.0]), (118.0, [130.8, 196.0, 261.6, 311.1])]
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
fx += 0.06 * band(400, 300) * ss(15, 16, t) * (1 - ss(18.6, 19.2, t))
for tt in (25.4, 51.0, 55.4, 59.6, 90.0): 
    for f0 in (659, 988): blip(tt, f0, 0.12, 0.8)
for k in range(8): blip(32.4 + k * 0.6, 160, 0.14, 0.08)
fx += 0.07 * hi * ss(49, 50, t) * (1 - ss(52.6, 53.2, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
for f0 in (523, 659, 784): blip(70.6, f0, 0.15, 1.2)
for f0 in (523, 659, 784, 1046): blip(110.0, f0, 0.16, 1.6)
fx += 0.1 * band(2500, 2000) * (np.abs(np.sin(2 * np.pi * 7.3 * t)) ** 6) * ss(118.4, 119.6, t)
np.save('bed23.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
