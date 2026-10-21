import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(25)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [130.8, 196.0, 261.6, 311.1]), (6.4, [146.8, 220.0, 293.7, 370.0]), (14.8, [130.8, 196.0, 261.6, 329.6]),
      (27.6, [116.5, 174.6, 233.1, 293.7]), (36.2, [110.0, 164.8, 220.0, 261.6]), (48.8, [146.8, 220.0, 293.7, 370.0]),
      (53.2, [130.8, 196.0, 261.6, 329.6]), (66.0, [146.8, 220.0, 293.7, 349.2]), (74.6, [164.8, 246.9, 329.6, 415.3]),
      (87.4, [174.6, 261.6, 349.2, 440.0]), (96.0, [130.8, 196.0, 261.6, 311.1]), (104.6, [110.0, 164.8, 220.0, 261.6]),
      (108.8, [130.8, 196.0, 261.6, 329.6]), (113.0, [146.8, 220.0, 293.7, 370.0]), (117.4, [164.8, 246.9, 329.6, 415.3]), (121.6, [174.6, 261.6, 349.2, 440.0])]
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
crk = band(2500, 2000)
fire = lambda a, b: ss(a, a + 0.6, t) * (1 - ss(b - 0.6, b, t))
fx += 0.12 * crk * (np.abs(np.sin(2 * np.pi * 7.3 * t)) ** 6) * (fire(6.0, 14.8) + fire(66.0, 74.6))
for k in range(12): blip(23.6 + k * 0.25, 880 + 60 * (k % 4), 0.08, 0.2)
for k in range(10): blip(28.0 + k * 0.3, 1200, 0.05, 0.05)
for f0 in (523, 659, 784): blip(49.4, f0, 0.16, 1.4)
for tt in (53.6, 57.8, 62.0): blip(tt, 440, 0.15, 0.8)
for k in range(6): blip(83.4 + k * 0.5, 660 + 110 * k, 0.12, 0.5)
for f0 in (523, 659, 784, 1046): blip(121.9, f0, 0.2, 2.5)
np.save('bed24.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
