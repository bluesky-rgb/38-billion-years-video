import numpy as np, math, subprocess, sys
from PIL import Image, ImageDraw
from ep1 import W, H, FPS, ss, lerp, text_img, put, fade_win, FB, FM, FL
from ep4 import sea, base, strand, mini, mul, BC, PAIR, BACK

DUR = 70.0
CLEAN = False
LIP = (235, 120, 165); TAIL = (240, 180, 200)

def lipid(dr, x, y, th, a=1.0, s=1.0, wig=0.0):
    nx, ny = math.cos(th), math.sin(th); px, py = -ny, nx
    for o in (-5, 5):
        pts = []
        for k in range(5):
            d = 10 * s + k * 8 * s
            w = 2.5 * math.sin(k * 1.4 + wig) * s
            pts.append((x + nx * d + px * (o * s + w), y + ny * d + py * (o * s + w)))
        dr.line(pts, fill=mul(TAIL, a), width=max(2, int(4 * s)))
    r = 11 * s
    dr.ellipse((x - r, y - r, x + r, y + r), fill=mul(LIP, a))
    dr.ellipse((x - r * 0.5, y - r * 0.6, x - r * 0.05, y - r * 0.2), fill=mul((250, 175, 205), a))

# membrane as a bent sheet: b=0 straight line, b=1 closed circle
NL = 24; SP = 40.0; LC = NL * SP; GAP = 30.0
def sheet(b, cx, cy_mid):
    out = []
    for leaf, sgn in ((0, -1), (1, 1)):
        for i in range(NL):
            s = (i + 0.5) * SP - LC / 2
            if b < 1e-3:
                mx, my, nx, ny = cx + s, cy_mid, 0.0, 1.0
            else:
                rho = LC / (2 * math.pi * b); phi = s / rho
                ccx, ccy = cx, cy_mid + rho
                mx, my = ccx + rho * math.sin(phi), ccy - rho * math.cos(phi)
                nx, ny = -math.sin(phi), math.cos(phi)
            hx, hy = mx + sgn * nx * GAP, my + sgn * ny * GAP
            th = math.atan2(-sgn * ny, -sgn * nx)
            out.append((hx, hy, th))
    return out

def ring(cx, cy, r, n=None):
    n = n or max(12, int(2 * math.pi * r / 40))
    out = []
    for leaf, dr_ in ((0, GAP), (1, -GAP)):
        m = n if leaf == 0 else max(10, int(n * (r - GAP) / (r + GAP)))
        for i in range(m):
            ph = 2 * math.pi * (i + 0.5 * leaf) / m
            rr = r + dr_
            x, y = cx + rr * math.cos(ph), cy + rr * math.sin(ph)
            th = ph + math.pi if leaf == 0 else ph
            out.append((x, y, th))
    return out

fr = np.random.default_rng(5)
FREE_L = [(fr.random() * W, 420 + fr.random() * 1100, fr.random() * 6.28, fr.random() * 6) for _ in range(40)]

L_LOVE = text_img('爱水的头', FM, 40, (250, 175, 205), 3)
L_HATE = text_img('怕水的尾巴', FM, 40, (240, 200, 215), 3)

def scene_a(t):
    img, dr = sea(t + 70)
    tmp = 'AUGCCGAUAG'; n = len(tmp)
    tp = [(205 + i * 75, 1050) for i in range(n)]
    strand(img, dr, tp, tmp, [True] * n)
    for i in range(n):
        t0 = 6.6 + i * 0.75
        k = ss(t0, t0 + 0.5, t)
        if k <= 0: continue
        drift = max(0.0, t - (t0 + 0.9))
        ang = 1.2 + i * 2.39
        x = tp[i][0] + math.cos(ang) * drift * 120
        y = tp[i][1] - 150 - drift * 90 + math.sin(ang) * drift * 60
        a = 1 - ss(t0 + 2.5, t0 + 4.5, t)
        if a <= 0: continue
        sx, sy = lerp(tp[i][0] + 260 * math.cos(ang), x, k), lerp(500, y, k)
        base(img, dr, sx, sy, PAIR[tmp[i]], False, a)
    return img

def scene_b(t):
    img, dr = sea(t + 70)
    if t < 23.0:
        for x0, y0, th, ph in FREE_L:
            x = x0 + 30 * math.sin(t * 0.5 + ph); y = y0 + 25 * math.cos(t * 0.4 + ph)
            lipid(dr, x, y, th + 0.3 * math.sin(t + ph), ss(19.0, 20.0, t), 1.0, t * 2 + ph)
        return img
    if t < 27.4:
        a = ss(23.0, 23.6, t)
        for x0, y0, th, ph in FREE_L:
            x = x0 + 30 * math.sin(t * 0.5 + ph); y = y0 + 25 * math.cos(t * 0.4 + ph)
            if a < 0.98: lipid(dr, x, y, th + 0.3 * math.sin(t + ph), 1 - a, 1.0, t * 2 + ph)
        lipid(dr, 540, 820, math.pi / 2, a, 4.0, t * 2)
        put(img, L_LOVE, 540, 700, a); put(img, L_HATE, 540, 1150, a)
        return img
    k = ss(27.4, 30.2, t); b = ss(31.6, 35.0, t)
    tgt = sheet(b, 540, 900)
    for i, (x0, y0, th0, ph) in enumerate(FREE_L[:0]): pass
    for i, (hx, hy, th) in enumerate(tgt):
        x0, y0, th0, ph = FREE_L[i % len(FREE_L)]
        x0 = (x0 + i * 97) % W; y0 = 420 + ((y0 + i * 53) % 1100)
        x = lerp(x0, hx, k); y = lerp(y0, hy, k); a = lerp(th0, th, k)
        lipid(dr, x, y, a, ss(27.4, 28.0, t), 1.0, t * 2 + i)
    return img

def contents(dr, cx, cy, n, t, r):
    pos = [(-50, -40), (50, 40), (-45, 55), (55, -55)]
    for i in range(n):
        dx, dy = pos[i % 4]; s = min(1.0, r / 150)
        mini(dr, cx + dx * s, cy + dy * s, BACK, 1.0, 0.8, t * 2 + i)

def cell(dr, cx, cy, r, t, hide=None):
    for x, y, th in ring(cx, cy, r):
        if hide and (x - hide[0]) ** 2 + (y - hide[1]) ** 2 < (hide[2] - 5) ** 2: continue
        lipid(dr, x, y, th, 1.0, 1.0, t * 2 + x * 0.05)

def scene_c(t):
    img, dr = sea(t + 70)
    cx, cy = 540, 950
    rho0 = LC / (2 * math.pi)
    if t < 48.6:
        r = lerp(rho0, 205, ss(44.4, 48.0, t))
        enter = ss(36.2, 38.6, t)
        sx, sy = lerp(540, cx, enter), lerp(1450, cy, enter)
        n = 1 + int(ss(40.4, 44.0, t) * 3.99)
        if enter < 1: mini(dr, sx, sy, BACK, 1.0, 0.8, t * 2)
        else: contents(dr, cx, cy, n, t, r)
        for i in range(8):
            ang = i * 0.785 + t * 0.2; k = ss(44.4 + i * 0.3, 45.6 + i * 0.3, t)
            if 0 < k < 1:
                rr = lerp(r + 260, r + GAP, k)
                lipid(dr, cx + rr * math.cos(ang), cy + rr * math.sin(ang), ang + math.pi, 1 - k * 0.5, 1.0, t * 2)
        cell(dr, cx, cy, r, t)
        return img
    k = ss(48.6, 52.2, t)
    r = lerp(205, 150, k); d = lerp(0, 175, k)
    c1, c2 = (cx - d, cy), (cx + d, cy)
    contents(dr, *c1, 2, t, r); contents(dr, *c2, 2, t + 1, r)
    cell(dr, *c1, r, t, hide=(c2[0], c2[1], r - GAP))
    cell(dr, *c2, r, t, hide=(c1[0], c1[1], r - GAP))
    return img

pc = np.random.default_rng(8)
PROTO = [(pc.random() * W, 450 + pc.random() * 1150, 45 + pc.random() * 40, pc.random() * 6) for _ in range(11)]
def scene_d(t):
    img, dr = sea(t + 70)
    a = ss(53.0, 54.0, t)
    for i, (x0, y0, r, ph) in enumerate(PROTO):
        x = (x0 + 25 * math.sin(t * 0.4 + ph) + (t - 53) * 6) % (W + 120) - 60; y = y0 + 25 * math.cos(t * 0.3 + ph)
        m = max(10, int(2 * math.pi * r / 16))
        for j in range(m):
            p = 2 * math.pi * j / m
            dr.ellipse((x + r * math.cos(p) - 4, y + r * math.sin(p) - 4, x + r * math.cos(p) + 4, y + r * math.sin(p) + 4), fill=mul(LIP, a))
        mini(dr, x, y + 6, BACK, a, 0.45, t * 2 + i)
    k = ss(57.2, 58.4, t)
    cx, cy = 540, 960
    if k > 0:
        g = k * (0.75 + 0.25 * math.sin(t * 3))
        for rr in (230, 260, 290):
            dr.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=mul((255, 220, 150), g * (320 - rr) / 90), width=3)
    if a > 0:
        dr.ellipse((cx - 175, cy - 175, cx + 175, cy + 175), fill=mul((10, 40, 55), a))
        cell(dr, cx, cy, 150, t)
        contents(dr, cx, cy, 2, t, 150)
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 18.8: return dim(scene_a(t), 1 - ss(18.2, 18.8, t))
    if t < 35.8: return dim(scene_b(t), ss(18.8, 19.4, t) * (1 - ss(35.3, 35.8, t)))
    if t < 52.8: return dim(scene_c(t), ss(35.8, 36.3, t) * (1 - ss(52.4, 52.9, t)))
    return dim(scene_d(t), ss(52.8, 53.3, t))

CAPS = [(6.4, 10.6, '会复制的分子，有一个大麻烦'), (10.6, 14.8, '刚拼好的零件，一转眼就漂走了'),
        (14.8, 18.6, '大海太大，什么都留不住'), (19.0, 23.2, '海里还有一种分子：脂类'),
        (23.2, 27.4, '它一头爱水，一头怕水'), (27.4, 31.6, '为了躲开水，它们自动排成两层'),
        (31.6, 35.6, '再卷成一个空心的小泡'), (36.0, 40.2, '有的泡泡，恰好把 RNA 包了进去'),
        (40.2, 44.4, '零件不再漂走，复制越来越快'), (44.4, 48.6, '泡泡吸收新的脂类，越长越大'),
        (48.6, 52.8, '最后一分为二，各自带走一份'), (53.0, 57.2, '这就是最早的细胞雏形'),
        (57.2, 61.8, '所有生物的共同祖先，出现了')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep5_{ts}.png')
