import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, CY, ss, lerp, text_img, put, bg, D, blend, rocky, MN, FM, FB
from ep2 import earth2
from ep4 import sea, mini, mul, BACK
from ep5 import LIP

CLEAN = False
rng = np.random.default_rng(31)

BCOL = [(235, 150, 80), (160, 120, 230), (90, 190, 200), (230, 200, 90), (220, 110, 120)]
def capsule(dr, x, y, L, w, th, col, a=1.0):
    dx, dy = math.cos(th) * L / 2, math.sin(th) * L / 2
    dark = tuple(int(v * 0.55) for v in col)
    for ww, c in ((w + 8, dark), (w, col)):
        c = mul(c, a)
        dr.line((x - dx, y - dy, x + dx, y + dy), fill=c, width=int(ww))
        for ex, ey in ((x - dx, y - dy), (x + dx, y + dy)):
            dr.ellipse((ex - ww / 2, ey - ww / 2, ex + ww / 2, ey + ww / 2), fill=c)
    hl = tuple(min(255, int(v * 1.3)) for v in col)
    pts = [(x - dx * 0.6 + k * dx * 0.15 + math.sin(k * 1.7) * 3, y - dy * 0.6 + k * dy * 0.15 + math.cos(k * 1.7) * 5) for k in range(9)]
    dr.line(pts, fill=mul(hl, a), width=3)

# ---------- scene A: hungry protocells ----------
PC = [(rng.random() * W, 450 + rng.random() * 1100, 50 + rng.random() * 30, rng.random() * 6) for _ in range(9)]
FOOD = [(rng.random() * W, 400 + rng.random() * 1200, rng.integers(0, 9), 6.5 + rng.random() * 8) for _ in range(60)]
def pc_pos(i, t):
    x0, y0, r, ph = PC[i]
    return (x0 + 25 * math.sin(t * 0.4 + ph) + t * 4) % (W + 120) - 60, y0 + 25 * math.cos(t * 0.3 + ph)
def draw_pc(dr, x, y, r, t, a=1.0, i=0):
    m = max(10, int(2 * math.pi * r / 16))
    for j in range(m):
        p = 2 * math.pi * j / m
        dr.ellipse((x + r * math.cos(p) - 4, y + r * math.sin(p) - 4, x + r * math.cos(p) + 4, y + r * math.sin(p) + 4), fill=mul(LIP, a))
    mini(dr, x, y + 6, BACK, a, 0.45, t * 2 + i)
def scene_a(t):
    img, dr = sea(t + 140)
    for fx, fy, tgt, te in FOOD:
        x, y = pc_pos(tgt, t)
        k = ss(te, te + 1.2, t)
        if k >= 1: continue
        px, py = lerp(fx + 10 * math.sin(t + fy), x, k), lerp(fy, y, k)
        dr.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(230, 200, 110))
    for i, (x0, y0, r, ph) in enumerate(PC):
        x, y = pc_pos(i, t); capsule(dr, x, y, 60, 46, ph + 0.3 * math.sin(t * 0.5 + ph), BCOL[i % 5])
    return img

# ---------- scene B/C: shallow sea ----------
yy = np.arange(H, dtype=np.float32)[:, None]
SURF = 560
SKY0 = np.array([170, 140, 115]); SKY1 = np.array([110, 165, 230])
def sky_col(k): return SKY0 * (1 - k) + SKY1 * k
sea_grad = (np.array([30, 110, 120]) * (1 - (yy - SURF) / (H - SURF)) + np.array([5, 30, 40]) * ((yy - SURF) / (H - SURF)))
FLOOR = 1430
BACT = [(rng.random() * W, SURF + 60 + rng.random() * 380, rng.random() * 3.14, rng.random() * 6) for _ in range(46)]
OLD = [(rng.random() * W, 900 + rng.random() * 380, 40 + rng.random() * 18, rng.random() * 6) for _ in range(7)]
STROM = [(150, 1.0), (430, 1.25), (720, 0.9), (960, 1.1)]
RUST = [(rng.random() * W, SURF + 80 + rng.random() * 600, 33.4 + rng.random() * 8) for _ in range(140)]
L_O2 = text_img('氧气', FM, 30, (225, 245, 255), 2)
L_STROM = text_img('叠层石', FM, 38, (230, 220, 190), 3)
L_IRON = text_img('条带状铁矿', FM, 38, (240, 190, 170), 3)

def shallow(t):
    skyk = ss(41.6, 46.0, t)
    f = np.zeros((H, W, 3), np.float32)
    sk = sky_col(skyk)
    top = sk * 0.75 + np.array([20, 20, 30]) * 0.25
    kk = np.clip(yy / SURF, 0, 1)[..., None]
    f[:SURF] = (top * (1 - kk) + sk * kk)[:SURF]
    f[SURF:] = sea_grad[SURF:][:, None, :]
    f[SURF:] *= (0.85 + 0.15 * skyk)
    xs = np.arange(W, dtype=np.float32)[None, :]
    rays = (0.5 + 0.5 * np.sin(xs * 0.011 + yy[SURF:] * 0.004 + t * 0.35)) ** 3 * np.clip(1 - (yy[SURF:] - SURF) / 800, 0, 1)
    f[SURF:] += rays[..., None] * np.array([40, 60, 50])
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    sx, sy = 870, 230
    for r, c in ((95, (255, 245, 210)), (75, (255, 250, 230))):
        dr.ellipse((sx - r, sy - r, sx + r, sy + r), fill=c)
    dr.rectangle((0, SURF - 4, W, SURF + 4), fill=(200, 230, 235))
    # floor
    dr.rectangle((0, FLOOR, W, H), fill=(40, 34, 30))
    bands = int(ss(37.0, 42.0, t) * 7)
    for b in range(bands):
        y0 = FLOOR + 10 + b * 16
        dr.rectangle((0, y0, W, y0 + 8), fill=(140, 55, 35) if b % 2 == 0 else (85, 80, 78))
    # stromatolites
    layers = int(ss(27.8, 31.8, t) * 7)
    for x, s in STROM:
        for L in range(layers):
            w = (95 - L * 9) * s; h = (40 + L * 20) * s
            col = (110 - L * 4, 105 - L * 3, 80) if L % 2 else (150, 140, 105)
            dr.chord((x - w, FLOOR - h, x + w, FLOOR + h), 180, 360, fill=col)
        if layers:
            g = 0.6 + 0.4 * math.sin(t * 2 + x)
            dr.chord((x - 30 * s, FLOOR - (40 + layers * 20) * s - 6, x + 30 * s, FLOOR - (40 + layers * 20) * s + 22), 180, 360, fill=mul((80, 190, 110), g))
    # old residents
    for i, (x0, y0, r, ph) in enumerate(OLD):
        death = ss(48.0 + i * 0.5, 50.5 + i * 0.5, t)
        flee = i % 3 == 0
        x = x0 + 20 * math.sin(t * 0.4 + ph); y = y0 + 20 * math.cos(t * 0.3 + ph) + (death * 500 if flee else 0)
        a = (1 - death * (0.0 if flee else 1.0)) * ss(15.2, 16.0, t)
        if a > 0.02: capsule(dr, x, y, 56 * (1 - 0.4 * death * (not flee)), 42 * (1 - 0.4 * death * (not flee)), ph + 0.2 * math.sin(t * 0.4), BCOL[i % 2 + 1 if i % 2 else 0] if False else (BCOL[0] if i % 2 else BCOL[1]), a * (1 - 0.6 * death * flee))
    # bacteria
    ba = ss(15.6, 17.0, t)
    for i, (x0, y0, th, ph) in enumerate(BACT):
        x = (x0 + 18 * math.sin(t * 0.5 + ph) + t * 3) % (W + 40) - 20; y = y0 + 12 * math.cos(t * 0.6 + ph)
        th2 = th + 0.3 * math.sin(t * 0.7 + ph)
        dx, dy = math.cos(th2) * 22, math.sin(th2) * 22
        dr.line((x - dx, y - dy, x + dx, y + dy), fill=mul((40, 120, 70), ba), width=24)
        dr.line((x - dx, y - dy, x + dx, y + dy), fill=mul((80, 190, 110), ba), width=16)
        if t > 23.8 and i % 2 == 0:
            for k in range(3):
                ph2 = (t * 0.45 + k / 3 + i * 0.13) % 1
                by = y - ph2 * (y - SURF); bx = x + 8 * math.sin(ph2 * 9 + i)
                rr = 4 + 3 * ph2
                dr.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=mul((215, 240, 255), ss(23.8, 25, t)), width=2)
    if 23.8 < t < 28.6:
        put(img, L_O2, BACT[4][0] % W, BACT[4][1] - 90, ss(24.0, 24.6, t) * (1 - ss(28.0, 28.6, t)))
    for x0, y0, te in RUST:
        if t < te: continue
        k = min(1.0, (t - te) / 4.0)
        y = lerp(y0, FLOOR + 10, k ** 1.5)
        if k < 1: dr.ellipse((x0 - 4, y - 4, x0 + 4, y + 4), fill=(180, 75, 40))
    put(img, L_STROM, 430, FLOOR - 230, ss(28.4, 29.2, t) * (1 - ss(32.0, 32.6, t)))
    put(img, L_IRON, W / 2, FLOOR + 160, ss(38.0, 38.8, t) * (1 - ss(41.0, 41.6, t)))
    if 45.8 < t < 54.4:
        g = ss(45.8, 47, t) * (1 - ss(53.6, 54.4, t))
        a = np.asarray(img, np.float32).copy(); a[SURF:] = a[SURF:] * (1 - 0.18 * g) + np.array([40, 0, 10]) * 0.18 * g
        img = Image.fromarray(a.astype(np.uint8))
    return img

# ---------- scene D: ozone shield ----------
def ozone(t):
    f = bg.copy()
    f += (np.exp(-np.maximum(D - 340, 0) / 70) * 0.45 * (D > 338))[..., None] * np.array([110, 170, 250])
    col, a = rocky(92, 0.8, MN, ([60, 58, 56], [165, 160, 152]), 0.0)
    blend(f, col, a, CX - 380, CY + 330)
    col, a = earth2(340, 0.9 + t * 0.004, 1.0, 0.55)
    blend(f, col, a, CX, CY)
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    oz = ss(58.8, 60.5, t)
    if oz > 0:
        for rr, w, c in ((395, 10, (60, 140, 180)), (395, 4, (170, 235, 255))):
            dr.ellipse((CX - rr, CY - rr, CX + rr, CY + rr), outline=mul(c, oz * (0.8 + 0.2 * math.sin(t * 2))), width=w)
    uv = ss(62.6, 63.4, t)
    if uv > 0:
        for k in range(7):
            ang = -2.3 + k * 0.17
            ex, ey = CX + 410 * math.cos(ang), CY + 410 * math.sin(ang)
            ph = ((t * 1.3 + k * 0.37) % 1)
            sx, sy = ex + 700 * math.cos(ang), ey + 700 * math.sin(ang)
            hx, hy = lerp(sx, ex, ph), lerp(sy, ey, ph)
            pts = []
            for j in range(9):
                kk = j / 8; px, py = lerp(hx, lerp(hx, sx, 0.35), kk), lerp(hy, lerp(hy, sy, 0.35), kk)
                nx, ny = -math.sin(ang), math.cos(ang); wv = 10 * math.sin(j * 1.6 + t * 10)
                pts.append((px + nx * wv, py + ny * wv))
            dr.line(pts, fill=mul((190, 120, 255), uv), width=4)
            if ph > 0.85:
                dr.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), outline=mul((220, 190, 255), uv), width=3)
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render_orig(t):
    if t < 15.2: return dim(scene_a(t), 1 - ss(14.6, 15.2, t))
    if t < 54.4: return dim(shallow(t), ss(15.2, 15.8, t) * (1 - ss(53.8, 54.4, t)))
    return dim(ozone(t), ss(54.4, 55.0, t))

CAPS0 = [(6.4, 10.6, '最早的细胞，靠吃海里的化学物质过活'), (10.6, 14.8, '食物有限，大家都在抢'),
        (15.4, 19.6, '后来，一种细菌找到了新办法'), (19.6, 23.8, '用阳光、水和二氧化碳，自己造食物'),
        (23.8, 28.0, '代价是排出一种废气：氧气'), (28.0, 32.8, '它们一层层堆成石头，今天还能看到'),
        (33.2, 37.4, '氧气先和海水里的铁结合'), (37.4, 41.6, '铁锈一层层沉到海底'),
        (41.6, 45.8, '约 24 亿年前，氧气涌进了大气'), (45.8, 50.0, '对许多老住户来说，氧气是毒药'),
        (50.0, 54.2, '它们大批死去，或者躲进深处'), (54.6, 58.8, '这场灾难，是生命自己造成的'),
        (58.8, 63.0, '但氧气也在高空形成了臭氧层'), (63.0, 67.2, '替地球挡住了致命的紫外线'),
        (67.2, 71.4, '也给更复杂的生命，留下了机会')]


# ---------- inserted bridge: protocells become bacteria ----------
INS = 16.8
ir = np.random.default_rng(44)
P4 = [(140 + ir.random() * 800, 520 + ir.random() * 820) for _ in range(16)]
FCOL = [BCOL[ir.integers(0, 5)] for _ in range(16)]
FTH = [ir.random() * 3.14 for _ in range(16)]
def node_pos(g, j):
    span = 2 ** (4 - g); pts = P4[j * span:(j + 1) * span]
    return sum(p[0] for p in pts) / span, sum(p[1] for p in pts) / span
def title_bg(t):
    img, dr = sea(t + 140)
    x, y = node_pos(0, 0)
    m = 44
    for k in range(m):
        ph = 2 * math.pi * k / m
        dr.ellipse((x + 150 * math.cos(ph) - 5, y + 150 * math.sin(ph) - 5, x + 150 * math.cos(ph) + 5, y + 150 * math.sin(ph) + 5), fill=LIP)
    mini(dr, x, y + 6, BACK, 1.0, 0.5, t * 2)
    return img
EXTRA = [(ir.random() * W, 420 + ir.random() * 1200, ir.random() * 3.14, ir.integers(0, 5), ir.random() * 6) for _ in range(50)]
L_BAC = text_img('细菌', FB, 52, (255, 225, 160), 4)
def bridge(t):
    img, dr = sea(t + 140)
    gt = (t - 6.4) / 1.25
    g = int(min(4, max(0, math.floor(gt))))
    fk = ss(0, 0.6, gt - g) if g < 4 else 1.0
    morph = ss(12.4, 15.0, t)
    zoom = lerp(1.0, 0.62, ss(19.0, 22.4, t))
    def Z(x, y): return CX + (x - CX) * zoom, 950 + (y - 950) * zoom
    for e in EXTRA:
        x0, y0, th, ci, ph = e; ea = ss(19.2, 21.0, t)
        if ea > 0:
            x, y = x0 + 20 * math.sin(t * 0.5 + ph), y0 + 20 * math.cos(t * 0.4 + ph)
            capsule(dr, x, y, 60 * 0.62, 46 * 0.62, th + 0.3 * math.sin(t + ph), BCOL[ci], ea)
    for i in range(16):
        j0 = i >> (4 - g); j1 = i >> max(0, 4 - g - 1)
        p0 = node_pos(g, j0); p1 = node_pos(min(4, g + 1), j1) if g < 4 else p0
        x, y = lerp(p0[0], p1[0], fk), lerp(p0[1], p1[1], fk)
        x += 10 * math.sin(t * 0.6 + i); y += 10 * math.cos(t * 0.5 + i)
        if i != (i >> (4 - g)) << (4 - g) and fk < 0.02 and g < 4: continue
        x, y = Z(x, y)
        r = 60 * zoom * lerp(2.5, 1.0, ss(6.4, 9.2, t))
        if morph < 1:
            pa = 1 - ss(12.4, 13.6, t)
            m = max(22, int(2 * math.pi * r / 22))
            for k in range(m):
                ph = 2 * math.pi * k / m
                dr.ellipse((x + r * math.cos(ph) - 5, y + r * math.sin(ph) - 5, x + r * math.cos(ph) + 5, y + r * math.sin(ph) + 5), fill=mul(LIP, pa))
            mini(dr, x, y + 6, BACK, pa, 0.5 * zoom, t * 2 + i)
        if morph > 0:
            capsule(dr, x, y, 64 * zoom * morph, 48 * zoom * morph, FTH[i], FCOL[i], 1.0)
    put(img, L_BAC, CX, 380, ss(15.0, 15.8, t) * (1 - ss(21.8, 22.6, t)))
    return img

def render(t):
    if t < 6.4: return title_bg(t)
    if t < 22.8:
        img = bridge(t)
        return img if t < 22.2 else dim(img, 1 - ss(22.2, 22.8, t))
    if t < 23.4: return dim(render_orig(t - INS), ss(22.8, 23.4, t))
    return render_orig(t - INS)

CAPS = [(6.4, 10.6, '原始细胞一次次分裂，一次次出错'), (10.6, 14.8, '几亿年里，后代变得越来越结实'),
        (14.8, 19.0, '它们成了真正的细胞：细菌'), (19.0, 22.8, '小到看不见，却遍布整个海洋'),
        (23.2, 27.4, '它们靠吃海里的化学物质过活'), (27.4, 31.6, '食物有限，大家都在抢'),
        (32.2, 36.4, '后来，其中一种细菌找到了新办法')] + [(a + INS, b + INS, x) for a, b, x in CAPS0[3:]]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep6_{ts}.png')
