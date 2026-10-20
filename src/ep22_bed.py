import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(23)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [110.0, 164.8, 220.0, 261.6]), (6.4, [130.8, 196.0, 261.6, 311.1]), (19.0, [146.8, 220.0, 293.7, 349.2]),
      (27.6, [130.8, 196.0, 261.6, 329.6]), (40.4, [146.8, 220.0, 293.7, 370.0]), (57.2, [164.8, 246.9, 329.6, 415.3]),
      (74.4, [130.8, 196.0, 261.6, 329.6]), (82.8, [146.8, 220.0, 293.7, 370.0]), (91.4, [110.0, 164.8, 220.0, 261.6]),
      (100.0, [164.8, 246.9, 329.6, 415.3]), (112.8, [146.8, 220.0, 293.7, 370.0]), (117.0, [174.6, 261.6, 349.2, 440.0])]
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
fx += 0.14 * crk * (np.abs(np.sin(2 * np.pi * 7.3 * t)) ** 6) * (fire(19.2, 40.4) + fire(74.4, 91.4) * 1.3 + fire(53, 57.2) * 0.7)
fx += 0.12 * band(300, 200) * (fire(19.2, 40.4) + fire(74.4, 91.4))
fx += 0.08 * hi * fire(91.4, 100.0)
for f0 in (523, 659, 784): blip(36.2, f0, 0.14, 1.2)
for f0 in (659, 830, 988): blip(49.2, f0, 0.14, 1.0)
for k in range(10): blip(53.6 + k * 0.12, 900, 0.06, 0.05)
blip(79.0, 90, 0.3, 0.6)
for f0 in (523, 659, 784, 1046): blip(100.2, f0, 0.18, 1.6)
np.save('bed22.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
