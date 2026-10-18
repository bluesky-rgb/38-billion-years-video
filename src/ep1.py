import numpy as np, math, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 66.0
CX, CY = 540, 820
TC = 31.5  # impact time
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FM = '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
FL = '/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc'

def ss(a, b, t):
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)

def lerp(a, b, k):
    return a + (b - a) * k

# ---------- textures ----------
TW, TH = 1024, 512
def fbm(octs, seed, base=4):
    r = np.random.default_rng(seed)
    out = np.zeros((TH, TW), np.float32); amp, tot = 1.0, 0.0
    for o in range(octs):
        gw = base * 2 ** o; gh = max(2, gw // 2)
        g = r.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((TW, TH), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255 * amp; tot += amp; amp *= 0.5
    out /= tot
    return (out - out.min()) / (out.max() - out.min())

N1, N2, CL, MN = fbm(6, 1), fbm(5, 2, 6), fbm(6, 3), fbm(6, 4, 8)
LV = np.array([-0.55, -0.45, 0.70]); LV /= np.linalg.norm(LV)

def geom(R, rot):
    S = int(2 * R + 4); c = S / 2
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    x = (xx + 0.5 - c) / R; y = (yy + 0.5 - c) / R
    rr = x * x + y * y
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    lat = np.arcsin(np.clip(y, -1, 1))
    lon = np.arctan2(x, np.maximum(z, 1e-4))
    u = ((lon + rot + np.pi) / (2 * np.pi) * TW).astype(np.int32) % TW
    v = ((lat + np.pi / 2) / np.pi * TH).astype(np.int32).clip(0, TH - 1)
    lam = np.clip(x * LV[0] + y * LV[1] + z * LV[2], 0, 1)
    alpha = np.clip((1 - np.sqrt(rr)) * R, 0, 1)
    return x, y, z, u, v, lam, alpha

def earth(R, rot, h, clouds, burn=0.0):
    x, y, z, u, v, lam, a = geom(R, rot)
    n1 = N1[v, u]; n2 = N2[v, u]
    crack = np.clip(1 - np.abs(n2 - 0.5) * 16, 0, 1)
    hot = lerp(np.array([70, 8, 0]), np.array([235, 80, 12]), (n1 ** 1.4)[..., None])
    hot = hot + crack[..., None] * np.array([255, 200, 90])
    crust = lerp(np.array([38, 34, 33]), np.array([105, 92, 82]), n1[..., None])
    crust = crust + crack[..., None] * np.array([170, 40, 0]) * 0.4
    col = hot * h + crust * (1 - h)
    emis = 0.5 * h + 0.08
    col = col * (emis + (1 - emis) * lam)[..., None]
    col = col + burn * np.array([255, 170, 80]) * (0.4 + 0.6 * crack[..., None])
    if clouds > 0:
        c = CL[v, u]
        ca = (np.clip((c - 0.52) * 4, 0, 1) * clouds)[..., None]
        cc = np.array([225, 225, 232]) * (0.15 + 0.85 * lam[..., None])
        col = col * (1 - ca) + cc * ca
    limb = ((1 - z) ** 3)[..., None]
    col = col + limb * (np.array([255, 110, 40]) * h * 0.6 + np.array([120, 160, 230]) * (1 - h) * 0.5)
    return col, a

def rocky(R, rot, seed_tex, tint, h):
    x, y, z, u, v, lam, a = geom(R, rot)
    n = seed_tex[v, u]
    col = lerp(np.array(tint[0]), np.array(tint[1]), n[..., None])
    col = col * (0.07 + 0.93 * lam[..., None]) + h * np.array([200, 60, 10]) * (n[..., None] ** 3)
    return col, a

def blend(f, col, a, cx, cy, k=1.0):
    S = col.shape[0]; x0 = int(round(cx - S / 2)); y0 = int(round(cy - S / 2))
    fx0, fy0 = max(x0, 0), max(y0, 0); fx1, fy1 = min(x0 + S, W), min(y0 + S, H)
    if fx1 <= fx0 or fy1 <= fy0: return
    sx0, sy0 = fx0 - x0, fy0 - y0
    cc = col[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0]
    aa = a[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0, None] * k
    reg = f[fy0:fy1, fx0:fx1]
    f[fy0:fy1, fx0:fx1] = reg * (1 - aa) + cc * aa

# ---------- background ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
D = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
vign = np.clip(1.15 - ((xx - W / 2) ** 2 / (W * 0.9) ** 2 + (yy - H / 2) ** 2 / (H * 0.75) ** 2), 0.3, 1)
bg = np.zeros((H, W, 3), np.float32)
bg[...] = np.array([4, 5, 12]) * vign[..., None]
neb = Image.fromarray((fbm(5, 9, 3) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
neb = np.asarray(neb, np.float32) / 255
bg += (np.clip(neb - 0.55, 0, 1) ** 1.5 * 70)[..., None] * np.array([0.6, 0.35, 0.9])
rs = np.random.default_rng(11)
for _ in range(1400):
    sx, sy = rs.integers(0, W), rs.integers(0, H); b = rs.random() ** 3 * 230 + 25
    bg[sy, sx] += b
    if rs.random() < 0.05:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= sy + dy < H and 0 <= sx + dx < W: bg[sy + dy, sx + dx] += b * 0.4

# ---------- text ----------
def text_img(s, font, size, fill=(255, 255, 255), stroke=5):
    fnt = ImageFont.truetype(font, size, index=2)
    bb = fnt.getbbox(s, stroke_width=stroke)
    im = Image.new('RGBA', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), s, font=fnt, fill=fill + (255,),
                            stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    return im

CAPS = [
    (6.4, 10.4, '46 亿年前，太阳刚刚点燃'),
    (10.4, 14.4, '周围的尘埃和岩石，不断碰撞、聚集'),
    (15.6, 19.8, '原始地球诞生了'),
    (19.8, 24.6, '表面是一片沸腾的岩浆海'),
    (25.4, 29.4, '不久，一颗火星大小的天体'),
    (29.4, 33.8, '猛烈地撞了上来'),
    (34.6, 39.0, '撞飞的碎片在轨道上重新聚拢'),
    (39.0, 44.0, '形成了月亮'),
    (44.6, 49.2, '又过了几千万年，地球慢慢冷却'),
    (49.2, 54.0, '岩浆凝固成最早的地壳，水汽升腾成云'),
    (54.6, 58.2, '如果没有那次撞击'),
    (58.2, 61.6, '地球可能是完全不同的模样'),
]
cap_imgs = [(a, b, text_img(s, FM, 54)) for a, b, s in CAPS]
ERAS = [(6.0, 25.0, '约 46 亿年前'), (25.0, 44.0, '约 45 亿年前'), (44.0, 61.5, '约 44 亿年前')]
era_imgs = [(a, b, text_img(s, FL, 40, (230, 200, 160), 3)) for a, b, s in ERAS]
T_SERIES = text_img('38 亿年家谱', FB, 110, (255, 220, 170), 6)
T_EP = text_img('第 0 季 · 第 1 集', FM, 46, (220, 220, 220), 3)
T_NAME = text_img('一颗岩浆球', FB, 80, (255, 255, 255), 5)
T_NEXT1 = text_img('下一集', FM, 48, (220, 220, 220), 3)
T_NEXT2 = text_img('第一场雨', FB, 96, (170, 210, 255), 6)

def put(img, t_im, cx, cy, a):
    if a <= 0: return
    m = t_im.getchannel('A')
    if a < 1: m = m.point(lambda p: int(p * a))
    img.paste(t_im.convert('RGB'), (int(cx - t_im.width / 2), int(cy - t_im.height / 2)), m)

def fade_win(t, a, b, f=0.45):
    return min(ss(a, a + f, t), 1 - ss(b - f, b, t))

# ---------- particles ----------
pr = np.random.default_rng(5)
NP = 2600
p_rho = 140 + pr.random(NP) ** 0.8 * 760
p_a0 = pr.random(NP) * 2 * np.pi
p_w = 0.55 * (300 / p_rho) ** 1.5
p_b = 90 + pr.random(NP) * 165
p_sz = 1 + pr.random(NP) * 2.2
PL_RHO, PL_A0 = 560.0, 0.6

ND = 1100
d_v = pr.normal(size=(ND, 2)) * 520 + np.array([380, -380])
d_k = 1.2 + pr.random(ND) * 1.5
d_rho = 400 + pr.random(ND) ** 0.7 * 260
d_a0 = pr.random(ND) * 2 * np.pi
d_w = 0.55 * (480 / d_rho) ** 1.5
d_sz = 1 + pr.random(ND) * 2.5
d_f = 0.85 + pr.random(ND) * 0.15
PC = np.array([CX + 520 * 0.7071, CY - 520 * 0.7071])
M_RHO, M_A0, M_W, M_R = 500.0, 0.25, 0.12, 92

def moon_pos(t):
    a = M_A0 + M_W * (t - 34)
    return CX + M_RHO * math.cos(a), CY + M_RHO * math.sin(a) * 0.28, math.sin(a) >= 0

CLEAN = False

def render_orig(t):
    f = bg.copy()
    rot = 0.3 + t * 0.018
    parts = []
    # ---- scene 1/2: disk ----
    if t < 15.2:
        g = np.exp(-D / 90) * 1.0 + np.exp(-D / 320) * 0.35
        f += g[..., None] * np.array([255, 190, 110]) * ss(0.5, 4, t)
        f[D < 42] = np.array([255, 245, 220])
        ang = p_a0 + p_w * t
        pull = ss(9, 14.5, t) * np.exp(-((p_rho - PL_RHO) / 90) ** 2)
        pa = PL_A0 + 0.55 * (300 / PL_RHO) ** 1.5 * t
        px = CX + p_rho * np.cos(ang); py = CY + p_rho * np.sin(ang) * 0.32
        plx = CX + PL_RHO * math.cos(pa); ply = CY + PL_RHO * math.sin(pa) * 0.32
        px = lerp(px, plx, pull); py = lerp(py, ply, pull)
        vis = ss(1.5, 5, t)
        for i in range(0, NP):
            if np.sin(ang[i]) < 0 and (px[i] - CX) ** 2 + (py[i] - CY) ** 2 < 42 ** 2: continue
            b = p_b[i] * vis
            parts.append((px[i], py[i], p_sz[i], (int(b), int(b * 0.8), int(b * 0.62))))
        pr_r = 3 + 30 * ss(8, 14.5, t)
        if t > 8:
            col, a = rocky(pr_r, rot, N1, ([120, 40, 10], [255, 140, 40]), 0.6)
            blend(f, col, a, plx, ply)
    else:
        # ---- earth ----
        R = 300 + 40 * ss(15, 25, t) if t < 25 else 340
        h = 1.0 - 0.78 * ss(44, 54, t)
        clouds = 0.65 * ss(47, 55, t)
        burn = 0.9 * math.exp(-max(t - TC, 0) / 3.5) if t >= TC else 0.0
        gs = (0.55 * h + 0.12) + burn * 0.8
        gcol = np.array([255, 110, 40]) * h + np.array([110, 150, 230]) * (1 - h)
        f += (np.exp(-np.maximum(D - R, 0) / 55) * gs * (D > R - 2))[..., None] * gcol * 0.9
        mx, my, mfront = moon_pos(t)
        ma = ss(39.5, 43.5, t)
        if t > 39 and not mfront:
            col, a = rocky(M_R, rot * 0.5, MN, ([60, 58, 56], [165, 160, 152]), 0.4 * (1 - ss(40, 52, t)))
            blend(f, col, a, mx, my, ma)
        col, a = earth(R, rot, h, clouds, burn)
        blend(f, col, a, CX, CY)
        # theia
        if 24 < t < TC:
            k = ss(25.0, TC, t) ** 1.25
            dist = lerp(980, 520, k)
            tx, ty = CX + dist * 0.7071, CY - dist * 0.7071
            col, a = rocky(180, rot * 1.3 + 1, MN, ([55, 45, 40], [150, 125, 105]), 0.15)
            blend(f, col, a, tx, ty)
        if t > 39 and mfront:
            col, a = rocky(M_R, rot * 0.5, MN, ([60, 58, 56], [165, 160, 152]), 0.4 * (1 - ss(40, 52, t)))
            blend(f, col, a, mx, my, ma)
        # debris
        if TC <= t < 44.5:
            dt = t - TC
            free = PC + d_v * ((1 - np.exp(-d_k * dt)) / d_k)[:, None]
            ang = d_a0 + d_w * dt
            ring = np.stack([CX + d_rho * np.cos(ang), CY + d_rho * np.sin(ang) * 0.28], 1)
            m = ss(33, 37.5, t)
            pos = free * (1 - m) + ring * m
            c = ss(39, 43.8, t) * d_f
            pos = pos * (1 - c[:, None]) + np.array([mx, my]) * c[:, None]
            heat = math.exp(-dt / 2.5)
            fa = 1 - ss(42.5, 44.4, t)
            for i in range(ND):
                x, y = pos[i]
                back = (m > 0.5) and np.sin(ang[i]) < 0
                if back and (x - CX) ** 2 + (y - CY) ** 2 < R * R: continue
                b = fa
                cl = (int((180 + 75 * heat) * b), int((150 + 40 * heat) * b), int((130 - 60 * heat) * b))
                parts.append((x, y, d_sz[i], cl))
    # ---- flash ----
    if TC - 0.25 < t < TC + 2.0:
        fl = ss(TC - 0.25, TC, t) if t < TC else math.exp(-(t - TC) / 0.45)
        f = f * (1 - fl) + np.array([255, 245, 225]) * fl
    # ---- global fades ----
    gf = 1.0 if CLEAN else ss(0, 1.2, t) * (1 - 0.35 * ss(61.5, 62.5, t)) * (1 - ss(64.6, 66, t))
    gf *= min(1 - ss(14.4, 15.1, t), 1) if t < 15.1 else ss(15.1, 15.9, t)
    f *= gf
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(img)
    for x, y, s, c in parts:
        if -5 < x < W + 5 and -5 < y < H + 5:
            c = tuple(int(v * gf) for v in c)
            dr.ellipse((x - s, y - s, x + s, y + s), fill=c)
    # ---- text ----
    if CLEAN: return img
    ta = fade_win(t, 1.0, 6.0, 0.7)
    put(img, T_SERIES, W / 2, 760, ta)
    put(img, T_EP, W / 2, 880, ta)
    put(img, T_NAME, W / 2, 1010, fade_win(t, 2.2, 6.0, 0.7))
    for a, b, im in cap_imgs:
        if a <= t <= b: put(img, im, W / 2, 1560, fade_win(t, a, b, 0.35))
    for a, b, im in era_imgs:
        if a <= t <= b: put(img, im, W / 2, 230, fade_win(t, a, b, 0.6))
    na = fade_win(t, 62.0, 66.0, 0.6)
    put(img, T_NEXT1, W / 2, 1500, na)
    put(img, T_NEXT2, W / 2, 1610, na)
    return img

def audio(path):
    sr = 44100; t = np.arange(int(sr * DUR)) / sr
    r = np.random.default_rng(3)
    s = 0.16 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    s += 0.11 * np.sin(2 * np.pi * 82.4 * t + 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t + 2))
    s += 0.05 * np.sin(2 * np.pi * 110.3 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t))
    n = r.normal(size=t.size); F = np.fft.rfft(n); fr = np.fft.rfftfreq(t.size, 1 / sr)
    rumble = np.fft.irfft(F / (1 + (fr / 120) ** 2), t.size); rumble /= np.abs(rumble).max()
    band = np.fft.irfft(F * np.exp(-((fr - 900) / 700) ** 2), t.size); band /= np.abs(band).max()
    s += 0.12 * rumble
    dt = t - TC
    pre = np.clip((dt + 6) / 6, 0, 1) ** 2 * (dt < 0)
    s += 0.3 * band * pre
    post = dt >= 0
    fq = 28 + 70 * np.exp(-np.clip(dt, 0, None) * 1.8)
    ph = 2 * np.pi * np.cumsum(fq) / sr
    s += post * (0.9 * np.sin(ph) * np.exp(-np.clip(dt, 0, None) / 2.2) + 0.6 * rumble * np.exp(-np.clip(dt, 0, None) / 1.0))
    env = np.clip(t / 2, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
    s *= env; s = s / np.abs(s).max() * 0.85
    d = (s * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(d.tobytes())


# ---------- inserted prologue: the solar nebula collapses ----------
INS = 12.6
NEB = fbm(5, 17, 3)
_neb = np.asarray(Image.fromarray((NEB[:, 200:488] * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
_nr = np.random.default_rng(23)
s_x = _nr.normal(size=NP) * 330; s_y = _nr.normal(size=NP) * 420
def nebula(t):
    f = bg.copy()
    c1 = ss(6.0, 14.5, t); c2 = ss(13.0, 18.4, t)
    neb_a = (1 - c1) * 0.9 + 0.1
    f += (np.clip(_neb - 0.3, 0, 1) ** 1.2 * 280 * neb_a)[..., None] * np.array([0.75, 0.45, 0.9])
    core = ss(8.0, 15.4, t)
    f += (np.exp(-D / (60 + 260 * (1 - core))) * core * 0.9 * (1 - ss(15.4, 17.5, t)))[..., None] * np.array([255, 170, 110])
    ign = ss(15.4, 15.9, t)
    if ign > 0:
        g = np.exp(-D / 90) * 1.0 + np.exp(-D / 320) * 0.35
        f += g[..., None] * np.array([255, 190, 110]) * ign
        f[D < 42 * ign] = np.array([255, 245, 220])
    fl = ss(15.3, 15.6, t) * (1 - ss(15.7, 16.6, t))
    if fl > 0: f = f * (1 - fl * 0.7) + np.array([255, 240, 220]) * fl * 0.7
    rot = t * 0.08
    cr, sr = math.cos(rot), math.sin(rot)
    k = 1 - 0.55 * c1
    sx = (s_x * cr - s_y * sr * 0.3) * k; sy = (s_x * sr * 0.3 + s_y * cr) * k
    ang = p_a0 + p_w * 6.0
    tx = p_rho * np.cos(ang); ty = p_rho * np.sin(ang) * 0.32
    px = CX + lerp(sx, tx, c2); py = CY + lerp(sy, ty, c2)
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    vis = 0.35 + 0.65 * ss(6.0, 9.0, t)
    for i in range(NP):
        b = p_b[i] * vis
        dr.ellipse((px[i] - p_sz[i], py[i] - p_sz[i], px[i] + p_sz[i], py[i] + p_sz[i]), fill=(int(b), int(b * 0.8), int(b * 0.62)))
    return img

def render(t):
    if t < 6.0 + INS: return nebula(t)
    return render_orig(t - INS)
if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        for ts in sys.argv[2:]:
            render(float(ts)).save(f'still_{ts}.png')
    else:
        out = sys.argv[2]
        audio('ep1.wav')
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', 'ep1.wav',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                              '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out],
                             stdin=subprocess.PIPE)
        nf = int(DUR * FPS)
        for i in range(nf):
            p.stdin.write(render(i / FPS).tobytes())
            if i % 150 == 0: print(i, nf, flush=True)
        p.stdin.close(); p.wait()
        print('done')
