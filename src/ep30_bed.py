import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(31)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [164.8, 246.9, 329.6, 415.3]), (10.6, [146.8, 220.0, 293.7, 370.0]), (23.4, [130.8, 196.0, 261.6, 329.6]),
      (36.2, [146.8, 220.0, 293.7, 370.0]), (48.8, [110.0, 164.8, 220.0, 261.6]), (53.2, [116.5, 174.6, 233.1, 293.7]),
      (66.0, [146.8, 220.0, 293.7, 370.0]), (78.8, [174.6, 261.6, 349.2, 440.0]), (87.4, [110.0, 164.8, 220.0, 261.6]),
      (91.6, [130.8, 196.0, 261.6, 329.6]), (95.8, [146.8, 220.0, 293.7, 370.0]), (100.0, [164.8, 246.9, 329.6, 415.3]),
      (104.4, [174.6, 261.6, 349.2, 440.0]), (108.6, [196.0, 293.7, 392.0, 493.9])]
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
for k in range(10): blip(16.0 + k * 0.7, 500, 0.08, 0.15)
for k in range(12): blip(24.0 + k * 0.3, 900, 0.1, 0.05)
for k in range(30): blip(32.2 + k * 0.11, 2200, 0.05, 0.03)
fx += 0.06 * band(300, 200) * ss(36.4, 37.4, t) * (1 - ss(52.6, 53.2, t))
fx += 0.2 * band(150, 100) * ss(53.4, 54.4, t) * (1 - ss(65.4, 66.0, t)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 2 * t)))
for k in range(16): blip(66.4 + k * 0.25, 1000, 0.08, 0.04)
for k in range(30): blip(70.6 + k * 0.25, 2400 + 300 * (k % 4), 0.05, 0.03)
for f0 in (523, 659, 784): blip(96.0, f0, 0.15, 1.6)
for f0 in (523, 659, 784, 1046): blip(108.8, f0, 0.2, 3.0)
for f0 in (392, 523, 659, 784): blip(118.2, f0, 0.2, 3.5)
np.save('bed30.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
