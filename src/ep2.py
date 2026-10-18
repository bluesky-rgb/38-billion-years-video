import numpy as np, math, subprocess, sys
from PIL import Image, ImageDraw
import ep1
from ep1 import (W, H, FPS, CX, CY, ss, lerp, fbm, geom, earth, rocky, blend, bg, D,
                 text_img, put, fade_win, N1, N2, CL, MN, FB, FM, FL)

DUR = 66.0

# ---------- blue earth ----------
def earth2(R, rot, ocean, clouds):
    x, y, z, u, v, lam, a = geom(R, rot)
    n1 = N1[v, u]
    land = lerp(np.array([45, 40, 37]), np.array([110, 96, 84]), n1[..., None])
    sea_m = (np.clip((0.66 - n1) * 12, 0, 1) * ocean)[..., None]
    sea = lerp(np.array([8, 30, 70]), np.array([22, 72, 125]), (n1 / 0.66).clip(0, 1)[..., None])
    col = land * (1 - sea_m) + sea * sea_m
    col = col * (0.06 + 0.94 * lam[..., None])
    hv = np.array([-0.55, -0.45, 0.70]) + np.array([0, 0, 1.0]); hv /= np.linalg.norm(hv)
    spec = np.clip(x * hv[0] + y * hv[1] + z * hv[2], 0, 1) ** 60
    col = col + (spec * 200)[..., None] * sea_m
    c = CL[v, u]
    ca = (np.clip((c - 0.5) * 4, 0, 1) * clouds)[..., None]
    col = col * (1 - ca) + np.array([230, 232, 238]) * (0.12 + 0.88 * lam[..., None]) * ca
    limb = ((1 - z) ** 3)[..., None]
    col = col + limb * np.array([110, 160, 240]) * 0.7
    return col, a

# ---------- landscape precompute ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r1 = np.random.default_rng(21)
def noise1d(n, oct, seed):
    r = np.random.default_rng(seed); out = np.zeros(W); amp = 1; tot = 0
    for o in range(oct):
        k = 3 * 2 ** o; pts = r.random(k + 1)
        out += np.interp(np.linspace(0, k, W), np.arange(k + 1), pts) * amp; tot += amp; amp *= 0.5
    return out / tot
far_y = 1020 + 120 * noise1d(W, 5, 31)
xs = (np.arange(W) - 540) / 540
near_y = 1520 - 380 * xs ** 2 + 70 * (noise1d(W, 5, 32) - 0.5)
far_m = (yy > far_y[None, :]).astype(np.float32)
near_m = (yy > near_y[None, :]).astype(np.float32)
gtex = np.asarray(Image.fromarray((N1 * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
ctex = np.asarray(Image.fromarray((N2 * 255).astype(np.uint8)).resize((W * 2, H * 2), Image.BICUBIC), np.float32)[H // 2:H // 2 + H, W // 2:W // 2 + W] / 255
hgt = np.clip((yy - 1000) / 900, 0, 1)
crack = np.clip(1 - np.abs(ctex - 0.5) * 45, 0, 1) * hgt
sky_top, sky_hor = np.array([18, 17, 20]), np.array([88, 70, 60])
k = np.clip(yy / 1150, 0, 1)[..., None]
sky = sky_top * (1 - k) + sky_hor * k
cloudtex = fbm(6, 41, 3)
far_col = (np.array([30, 27, 27]) + gtex[..., None] * np.array([40, 34, 30]))
near_col = (np.array([22, 20, 20]) + gtex[..., None] * np.array([55, 48, 42])) * (0.6 + 0.6 * hgt[..., None])

def sprite(rad):
    g = np.mgrid[-rad:rad, -rad:rad].astype(np.float32)
    return np.exp(-(g[0] ** 2 + g[1] ** 2) / (rad * 0.45) ** 2)
STEAM = sprite(90)
ns = 60
st_x = r1.integers(80, W - 80, ns); st_t0 = r1.random(ns) * 30 + 14
st_y = np.array([near_y[x] + r1.random() * 200 + 20 for x in st_x])
NR = 900
rn_x, rn_y = r1.random(NR) * (W + 300) - 150, r1.random(NR) * H
rn_v = 2200 + r1.random(NR) * 900; rn_l = 30 + r1.random(NR) * 50; rn_b = 120 + r1.random(NR) * 110
BOLTS = [17.6, 22.9, 27.4, 31.8, 35.2]
def bolt_pts(seed):
    r = np.random.default_rng(seed); x = 200 + r.random() * 680; y = 0; pts = [(x, y)]
    while y < far_y[int(min(max(x, 0), W - 1))]:
        y += 40 + r.random() * 60; x += (r.random() - 0.5) * 110; pts.append((x, y))
    return pts
BOLT_P = [bolt_pts(i + 5) for i in range(len(BOLTS))]

def add_sprite(f, spr, cx, cy, col, a):
    rad = spr.shape[0] // 2; x0, y0 = int(cx - rad), int(cy - rad)
    fx0, fy0, fx1, fy1 = max(x0, 0), max(y0, 0), min(x0 + 2 * rad, W), min(y0 + 2 * rad, H)
    if fx1 <= fx0 or fy1 <= fy0: return
    s = spr[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None] * a
    f[fy0:fy1, fx0:fx1] = f[fy0:fy1, fx0:fx1] * (1 - s) + np.array(col) * s

def landscape(t):
    lt = t - 15
    glow = 1 - ss(15, 31, t)
    cl = cloudtex[(np.arange(H) // 2) % 512][:, ((np.arange(W) + int(lt * 25)) // 2) % 1024]
    f = sky * (0.75 + 0.5 * cl[..., None] * (yy < 1150)[..., None])
    f = f + (glow * 70 * np.exp(-np.abs(yy - far_y[None, :]) / 140))[..., None] * np.array([1.0, 0.35, 0.1])
    fm = far_m[..., None]
    f = f * (1 - fm) + far_col * fm
    nm = near_m[..., None]
    gr = near_col + (crack * glow * 0.9)[..., None] * np.array([255, 120, 30])
    f = f * (1 - nm) + gr * nm
    wy = lerp(1960, 1330, ss(25.5, 37, t))
    if wy < H:
        wm = np.clip((yy - wy) / 3, 0, 1)[..., None]
        depth = np.clip((yy - wy) / 400, 0, 1)[..., None]
        wc = np.array([40, 52, 58]) * (1 - depth) + np.array([14, 26, 34]) * depth
        f = f * (1 - wm * 0.92) + wc * wm * 0.92
    lf = 0.0
    for b in BOLTS:
        if b <= t < b + 0.5: lf = max(lf, math.exp(-(t - b) / 0.12) * (1 if (t - b) % 0.16 < 0.1 else 0.4))
    f = f + lf * np.array([150, 150, 175]) * (1 - 0.5 * nm)
    for i in range(ns):
        age = t - st_t0[i]
        if 0 < age < 4 and st_y[i] < wy + 40:
            a = math.sin(age / 4 * math.pi) * 0.35 * (0.4 + 0.6 * glow)
            add_sprite(f, STEAM, st_x[i] + age * 15, st_y[i] - age * 70, (150, 145, 145), a)
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(img)
    for bi, b in enumerate(BOLTS):
        if b <= t < b + 0.35:
            dr.line(BOLT_P[bi], fill=(235, 235, 255), width=5); dr.line(BOLT_P[bi], fill=(255, 255, 255), width=2)
    ry = (rn_y + rn_v * lt) % H; rx = (rn_x + rn_v * 0.18 * lt) % (W + 300) - 150
    rain_a = ss(15, 16.5, t)
    for i in range(NR):
        b = int(rn_b[i] * rain_a)
        dr.line((rx[i], ry[i], rx[i] - rn_l[i] * 0.18, ry[i] - rn_l[i]), fill=(b, b, int(b * 1.08)), width=2)
    if wy < H:
        for i in range(0, 220):
            px = (i * 997 + int(lt * 31) * 13) % W; py = wy + ((i * 389 + int(lt * 17) * 7) % max(int(H - wy), 1))
            rr = 3 + (i % 5)
            dr.ellipse((px - rr * 2, py - rr * 0.5, px + rr * 2, py + rr * 0.5), outline=(95, 110, 118))
    return img

# ---------- text ----------
CAPS = [
    (6.4, 10.4, '地壳冷却后，空气里充满了水蒸气'),
    (10.4, 14.4, '温度一降，水汽开始凝结成雨'),
    (15.6, 20.0, '一场大雨，可能下了数百万年'),
    (20.0, 24.9, '雨点打在滚烫的岩石上，又化成蒸汽'),
    (25.4, 29.6, '岩石慢慢冷却，雨水终于留了下来'),
    (29.6, 33.8, '低洼处越积越满'),
    (33.8, 37.9, '原始海洋诞生了'),
    (39.0, 43.4, '那时的月亮，离地球近得多'),
    (43.4, 48.0, '在天上看起来大好几倍'),
    (48.6, 53.0, '巨大的潮汐，日夜搅动着海洋'),
    (53.6, 58.0, '空气中几乎没有氧气，紫外线直射海面'),
    (58.4, 62.0, '但正是在这片海里，生命的原料开始聚集'),
]
cap_imgs = [(a, b, text_img(s, FM, 54)) for a, b, s in CAPS]
ERA = text_img('约 44 亿年前', FL, 40, (230, 200, 160), 3)
T_SERIES = text_img('38 亿年家谱', FB, 110, (255, 220, 170), 6)
T_EP = text_img('第 0 季 · 第 2 集', FM, 46, (220, 220, 220), 3)
T_NAME = text_img('第一场雨', FB, 80, (255, 255, 255), 5)
T_NEXT1 = text_img('下一集', FM, 48, (220, 220, 220), 3)
T_NEXT2 = text_img('生命的原料', FB, 96, (170, 230, 190), 6)

CLEAN = False

def render(t):
    rot = 1.5 + t * 0.012
    if t < 15.0:
        f = bg.copy()
        R = 340 if t < 12 else lerp(340, 1100, ss(12, 15, t) ** 1.5)
        cl = lerp(0.65, 1.0, ss(2, 12, t))
        f += (np.exp(-np.maximum(D - R, 0) / 55) * 0.25 * (D > R - 2))[..., None] * np.array([110, 150, 230])
        mx, my = CX - 420 + t * 8, CY + 210
        col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0)
        blend(f, col, a, mx, my)
        col, a = earth(R, rot, 0.22, cl, 0.0)
        blend(f, col, a, CX, CY)
        f *= (1 if CLEAN else ss(0, 1.2, t)) * (1 - ss(14.2, 15.0, t))
        img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    elif t < 38.4:
        img = landscape(t)
        k = ss(15.0, 15.8, t) * (1 - ss(37.6, 38.4, t))
        img = Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))
    else:
        f = bg.copy()
        ocean = ss(38, 50, t) * 0.4 + 0.6
        f += (np.exp(-np.maximum(D - 340, 0) / 60) * 0.32 * (D > 338))[..., None] * np.array([110, 160, 240])
        mx, my = CX + 300 - (t - 38) * 4, CY - 520
        col, a = rocky(150, 0.8 + (t - 38) * 0.01, MN, ([60, 58, 56], [170, 165, 158]), 0.0)
        blend(f, col, a, mx, my)
        col, a = earth2(340, rot, ocean, 0.5)
        blend(f, col, a, CX, CY)
        f *= ss(38.4, 39.4, t) * (1 if CLEAN else (1 - 0.35 * ss(61.8, 62.6, t)) * (1 - ss(64.6, 66, t)))
        img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    if CLEAN: return img
    ta = fade_win(t, 1.0, 6.0, 0.7)
    put(img, T_SERIES, W / 2, 760, ta); put(img, T_EP, W / 2, 880, ta)
    put(img, T_NAME, W / 2, 1010, fade_win(t, 2.2, 6.0, 0.7))
    for a, b, im in cap_imgs:
        if a <= t <= b: put(img, im, W / 2, 1640 if 15 < t < 38.4 else 1560, fade_win(t, a, b, 0.35))
    put(img, ERA, W / 2, 230, fade_win(t, 6.0, 61.8, 0.6))
    na = fade_win(t, 62.2, 66.0, 0.6)
    put(img, T_NEXT1, W / 2, 1500, na); put(img, T_NEXT2, W / 2, 1610, na)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        for ts in sys.argv[2:]: render(float(ts)).save(f'ep2_still_{ts}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                              '-crf', '20', '-pix_fmt', 'yuv420p', sys.argv[2]], stdin=subprocess.PIPE)
        nf = int(DUR * FPS)
        for i in range(nf):
            p.stdin.write(render(i / FPS).tobytes())
            if i % 300 == 0: print(i, nf, flush=True)
        p.stdin.close(); p.wait(); print('done')

# ---------- inserted explainer: why the earth cooled ----------
INS = 21.0  # seconds inserted after module time 6
render_orig = render
_lava_a = np.asarray(Image.fromarray((N1[:, 100:676] * 255).astype(np.uint8)).resize((W * 2, H), Image.BICUBIC), np.float32) / 255
_lava_b = np.asarray(Image.fromarray((N2[:, 300:588] * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
_topdark = np.clip((np.arange(H, dtype=np.float32) - 120) / 260, 0.25, 1)[:, None, None]

def heat_earth(t):
    f = bg.copy()
    f += (np.exp(-np.maximum(D - 340, 0) / 55) * 0.35 * (D > 338))[..., None] * np.array([255, 120, 50])
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0)
    blend(f, col, a, CX - 420 + 6 * 8, CY + 210)
    col, a = earth(340, 1.5 + t * 0.012, 0.35, 0.3, 0.0)
    blend(f, col, a, CX, CY)
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for k in range(5):
        r = 360 + ((t * 90 + k * 110) % 550)
        al = (1 - (r - 360) / 550) * ss(6.2, 7.5, t)
        c = (int(255 * al), int(110 * al), int(50 * al))
        for j in range(18):
            a0 = j * 20 + (t * 6) % 20
            dr.arc((CX - r, CY - r, CX + r, CY + r), a0, a0 + 11, fill=c, width=5)
    if 14.6 < t < 18.8:
        for t0, ang, miss in ((15.0, -0.9, 0), (16.6, 0.5, 1)):
            k = (t - t0) / 1.4
            if 0 <= k <= 1:
                ex, ey = CX + 360 * math.sin(ang) + miss * 500, CY - 360 * math.cos(ang)
                sx, sy = ex + 900, ey - 900
                hx, hy = lerp(sx, ex, k), lerp(sy, ey, k)
                dr.line((hx, hy, lerp(hx, sx, 0.25), lerp(hy, sy, 0.25)), fill=(255, 220, 160), width=5)
                dr.ellipse((hx - 9, hy - 9, hx + 9, hy + 9), fill=(255, 245, 210))
    return img

def lava_crust(t):
    lt = t - 18.8
    sh = min(int(lt * 18), W - 1)
    a = _lava_a[:, sh:sh + W]
    thr = lerp(0.98, 0.42, ss(19.2, 26.5, t))
    crust = np.clip((_lava_b - thr) * 14 + 0.5, 0, 1) * (_lava_b > thr - 0.04)
    edge = np.clip(1 - np.abs(_lava_b - thr) * 30, 0, 1)
    molten = (np.array([150, 25, 0]) + (a[..., None] ** 1.2) * np.array([255, 170, 60]))
    rock = np.array([38, 34, 32]) + (_lava_a[:, W:][..., None]) * np.array([45, 40, 36])
    f = molten * (1 - crust[..., None]) + rock * crust[..., None]
    f = f + (edge * (1 - crust))[..., None] * np.array([255, 200, 90]) * 0.6
    f = f * _topdark
    return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

def render(t):
    if t < 6.0: return render_orig(t)
    if t < 18.8:
        k = ss(6.0, 6.8, t)
        img = heat_earth(t)
        if k < 1: img = Image.fromarray((np.asarray(render_orig(6.0), np.float32) * (1 - k) + np.asarray(img, np.float32) * k).astype(np.uint8))
        return img if t < 18.2 else Image.fromarray((np.asarray(img, np.float32) * (1 - ss(18.2, 18.8, t))).astype(np.uint8))
    if t < 27.6:
        img = lava_crust(t)
        return Image.fromarray((np.asarray(img, np.float32) * ss(18.8, 19.4, t) * (1 - ss(27.0, 27.6, t))).astype(np.uint8))
    img = render_orig(t - INS)
    return img if t > 28.2 else Image.fromarray((np.asarray(img, np.float32) * ss(27.6, 28.2, t)).astype(np.uint8))
