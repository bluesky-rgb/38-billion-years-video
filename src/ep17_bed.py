import numpy as np
SR, DUR = 44100, 145.0
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(18)
def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, amp):
    ph = 2 * np.pi * f * t; return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
CH = [(0, [130.8, 196.0, 261.6, 329.6]), (6.4, [146.8, 220.0, 293.7, 370.0]), (19.0, [110.0, 164.8, 220.0, 261.6]),
      (27.4, [103.8, 155.6, 207.7, 246.9]), (35.8, [98.0, 146.8, 196.0, 233.1]), (52.8, [87.3, 130.8, 174.6, 207.7]),
      (61.4, [92.5, 138.6, 185.0, 220.0]), (82.6, [110.0, 164.8, 220.0, 261.6]), (99.6, [130.8, 196.0, 261.6, 311.1]),
      (112.4, [146.8, 220.0, 293.7, 370.0]), (116.6, [164.8, 246.9, 329.6, 415.3]), (120.8, [174.6, 261.6, 349.2, 440.0])]
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
fx = 0.06 * low
def blip(tt, f0, amp, dec=0.08, sweep=0.0):
    global fx
    d = t - tt; dd = np.clip(d, 0, None)
    fx += (d >= 0) * amp * np.sin(2 * np.pi * f0 * (1 + sweep * dd) * dd) * np.exp(-dd / dec)
hi = band(5000, 2500)
for k in range(8): blip(6.6 + k * 0.5, 80, 0.3, 0.2)
fx += 0.15 * band(400, 300) * ss(19.4, 22, t) * (1 - ss(22.6, 23.0, t))
fx += 0.2 * band(300, 250) * ss(28.0, 29.6, t) * (1 - ss(29.6, 29.7, t))
blip(29.7, 40, 1.0, 1.8); fx += 0.6 * low * ss(29.6, 29.8, t) * np.exp(-np.clip(t - 29.8, 0, None) / 2.5)
blip(36.0, 35, 1.0, 2.2); fx += 0.6 * low * ss(35.9, 36.1, t) * np.exp(-np.clip(t - 36.1, 0, None) / 3.0)
for k in range(30): blip(40.4 + k * 0.27, 1200 - 30 * (k % 7), 0.07, 0.25, -0.5)
fx += 0.25 * band(900, 700) * ss(44.6, 46, t) * (1 - ss(48.2, 48.6, t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
fx += 0.45 * low * ss(49.0, 51.0, t) * (1 - ss(52.2, 52.8, t))
fx += 0.06 * band(250, 150) * ss(53, 56, t) * (1 - ss(98.6, 99.6, t))
for k in range(6): blip(66.0 + k * 1.0, 60, 0.3, 0.4)
blip(78.6, 45, 0.7, 1.2)
for f0 in (523, 659, 784): blip(95.6, f0, 0.15, 1.0)
for f0 in (440, 554, 659): blip(104.4, f0, 0.15, 1.0)
for f0 in (523, 659, 784, 1046): blip(112.6, f0, 0.2, 1.8)
for k in range(10): blip(117.0 + k * 0.4, 2000 + 200 * (k % 3), 0.05, 0.05)
np.save('bed17.npy', (music / np.abs(music).max() * 0.3 + fx * 0.45).astype(np.float32)); print('ok')
