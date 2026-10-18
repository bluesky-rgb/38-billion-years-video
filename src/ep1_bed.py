import numpy as np, wave
SR, DUR, TC = 44100, 80.0, 31.5
t = np.arange(int(SR * DUR)) / SR
r = np.random.default_rng(3)

def ss(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)

def tone(f, amp):
    ph = 2 * np.pi * f * t
    return amp * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))

# chord progression (Hz), crossfaded by scene
CH = [(0, [146.8, 220.0, 293.7, 349.2]),      # Dm
      (15, [116.5, 233.1, 293.7, 349.2]),     # Bb
      (25, [130.8, 196.0, 261.6, 311.1]),     # Cm  tension
      (34, [110.0, 220.0, 277.2, 329.6]),     # A
      (44, [146.8, 220.0, 293.7, 370.0]),     # D
      (54, [116.5, 233.1, 293.7, 349.2])]     # Bb
music = np.zeros_like(t)
for i, (st, fs) in enumerate(CH):
    en = CH[i + 1][0] if i + 1 < len(CH) else DUR + 3
    w = ss(st - 1.5, st + 1.5, t) * (1 - ss(en - 1.5, en + 1.5, t)) if st > 0 else 1 - ss(en - 1.5, en + 1.5, t)
    for j, f in enumerate(fs):
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.06 + 0.02 * j) * t + j)
        music += tone(f * (1 + 0.0015 * j), 0.08) * lfo * w
# soft high shimmer
music += 0.025 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t)) * (1 - ss(24, 26, t) + ss(44, 46, t))

n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / SR)
def band(c, bw):
    x = np.fft.irfft(F * np.exp(-((fr - c) / bw) ** 2), t.size); return x / np.abs(x).max()
whoosh = band(1200, 900); crunch = band(600, 1500); rumble = band(150, 120)
dt = t - TC
fx = 0.45 * whoosh * np.clip((dt + 5) / 5, 0, 1) ** 2.5 * (dt < 0)
post = (dt >= 0).astype(float); d = np.clip(dt, 0, None)
fq = 55 + 120 * np.exp(-d * 2.5)
ph = 2 * np.pi * np.cumsum(fq) / SR
boom = (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph)) * np.exp(-d / 1.6)
fx += post * (0.75 * boom + 0.9 * crunch * np.exp(-d / 0.35) + 0.5 * rumble * np.exp(-d / 2.0))
# quiet music during impact build, swell after
music *= 1 - 0.6 * ss(29.5, 31.4, t) * (1 - ss(33, 36, t))

np.save('bed1.npy', (music / np.abs(music).max() * 0.32 + fx * 0.55).astype(np.float32)); raise SystemExit
vo = np.load('vo_track.npy')
venv = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.5 * np.clip(venv / 0.05, 0, 1)
bed = (music / np.abs(music).max() * 0.32) * duck + fx * 0.55
mix = bed + vo
mix *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.abs(mix).max() * 0.95
with wave.open('ep1_mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
