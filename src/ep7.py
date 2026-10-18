import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import sea, mul
from ep6 import capsule, BCOL

CLEAN = False
rng = np.random.default_rng(71)
AER = (235, 110, 70)
BAC = [(rng.random() * W, 420 + rng.random() * 1200, rng.random() * 3.14, rng.integers(0, 5), rng.random() * 6) for _ in range(34)]
HC = (500, 960); HR = 270

def overlay_circle(img, cx, cy, r, fill, outline, w):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=w)
    base = img.convert('RGBA'); base.alpha_composite(lay); return base.convert('RGB')

def spark(dr, x, y, a, t, k):
    for j in range(5):
        ang = j * 1.256 + t * 2 + k
        r0, r1 = 34, 34 + 18 * (0.5 + 0.5 * math.sin(t * 6 + j))
        dr.line((x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang)), fill=mul((255, 230, 120), a), width=3)

def bacteria_field(img, dr, t, glow_from=None, scale=1.0, a=1.0, around=None):
    for i, (x0, y0, th, ci, ph) in enumerate(BAC):
        x, y = (x0 + 20 * math.sin(t * 0.5 + ph) + t * 3) % (W + 60) - 30, y0 + 20 * math.cos(t * 0.4 + ph)
        if around and (x - around[0]) ** 2 + (y - around[1]) ** 2 < (around[2] + 40) ** 2: continue
        aer = i % 4 == 0
        col = AER if aer else BCOL[ci]
        if aer and glow_from is not None:
            g = ss(glow_from, glow_from + 1.5, t)
            if g > 0: spark(dr, x, y, g * a, t, i)
        capsule(dr, x, y, 60 * scale, 46 * scale, th + 0.3 * math.sin(t + ph), col, a)

MPOS = [(620, 860), (360, 820), (650, 1080), (330, 1090), (520, 760), (470, 1170)]
L_MITO = text_img('线粒体', FB, 46, (255, 190, 140), 3)
L_NUC = text_img('细胞核', FB, 46, (170, 200, 255), 3)
L_EUK = text_img('真核细胞', FB, 56, (255, 225, 160), 4)
L_PL = text_img('植物', FM, 40, (150, 230, 140), 3); L_FU = text_img('真菌', FM, 40, (230, 200, 160), 3); L_AN = text_img('动物', FM, 40, (150, 200, 255), 3)

def mito(dr, x, y, s, th, a=1.0):
    w, h = 50 * s, 26 * s
    c, sn = math.cos(th), math.sin(th)
    pts = [(x + w * math.cos(p) * c - h * math.sin(p) * sn, y + w * math.cos(p) * sn + h * math.sin(p) * c) for p in np.linspace(0, 2 * math.pi, 28)]
    dr.polygon(pts, fill=mul((200, 85, 55), a), outline=mul((255, 170, 120), a))
    zz = []
    for k in range(9):
        u = -0.75 + k * 0.1875; v = 0.6 if k % 2 else -0.6
        zz.append((x + w * u * c - h * v * sn, y + w * u * sn + h * v * c))
    dr.line(zz, fill=mul((255, 200, 150), a), width=max(2, int(3 * s)))

def host(img, t, cx, cy, r, sc=1.0):
    img = overlay_circle(img, cx, cy, r, (175, 150, 235, 60), (205, 180, 255, 255), max(3, int(7 * sc)))
    dr = ImageDraw.Draw(img)
    return img, dr

def dna_loop(dr, cx, cy, s, a, t):
    pts = [(cx + (38 + 9 * math.sin(p * 7 + t)) * s * math.cos(p), cy + (30 + 9 * math.sin(p * 7 + t)) * s * math.sin(p)) for p in np.linspace(0, 2 * math.pi, 60)]
    dr.line(pts, fill=mul((130, 170, 255), a), width=max(2, int(4 * s)))

def cell_interior(img, t, cx, cy, sc):
    dr = ImageDraw.Draw(img)
    def P(p): return cx + (p[0] - HC[0]) * sc, cy + (p[1] - HC[1]) * sc
    morph = ss(40.4, 42.4, t)
    n = 1 if t < 42.6 else (2 if t < 43.8 else (4 if t < 45.0 else 6))
    for i in range(n):
        par = [0, 0, 0, 1, 0, 2][i]
        tb = [0, 42.6, 43.8, 43.8, 45.0, 45.0][i]
        k = ss(tb, tb + 0.9, t) if i else 1.0
        x, y = lerp(*[MPOS[par][0], MPOS[i][0]], k), lerp(MPOS[par][1], MPOS[i][1], k)
        x, y = P((x + 6 * math.sin(t + i), y + 6 * math.cos(t * 0.8 + i)))
        th = 0.5 + i * 1.1 + 0.2 * math.sin(t * 0.6 + i)
        if i == 0 and morph < 1:
            capsule(dr, x, y, 60 * sc * (1 - morph), 46 * sc * (1 - morph) + 1, th, AER, 1.0)
        mito(dr, x, y, sc * (morph if i == 0 else 1.0), th)
        if t > 27.8 and t < 53:
            spark(dr, x, y, 0.6 * ss(27.8, 29, t) * (1 - ss(40.4, 41.5, t)), t, i)
    nk = ss(44.8, 47.0, t)
    nx, ny = P((500, 960))
    dna_loop(dr, nx, ny, sc * 1.2, 1.0, t)
    if nk > 0:
        rr = 92 * sc
        dr.ellipse((nx - rr, ny - rr, nx + rr, ny + rr), outline=mul((150, 180, 255), nk), width=max(2, int(6 * sc)))
        rr2 = rr - 10 * sc
        dr.ellipse((nx - rr2, ny - rr2, nx + rr2, ny + rr2), outline=mul((110, 140, 220), nk), width=max(2, int(3 * sc)))
    return img

FOOD = [(rng.random() * 6.28, rng.random()) for _ in range(14)]
def scene_main(t):
    img, dr = sea(t + 210)
    zoom = lerp(1.0, 0.5, ss(53.0, 56.0, t))
    cx, cy = lerp(HC[0], CX, ss(53, 56, t)), lerp(HC[1], 1080, ss(53, 56, t))
    bacteria_field(img, dr, t, glow_from=None, scale=lerp(1.0, 0.5, ss(53, 56, t)), a=1.0, around=(cx, cy, HR * zoom))
    img, dr = host(img, t, cx, cy, HR * zoom, zoom)
    if t < 36.2:
        # engulf the aerobic bacterium
        k = ss(19.8, 23.4, t)
        bx, by = lerp(1000, MPOS[0][0], k), lerp(560, MPOS[0][1], k)
        bx += 8 * math.sin(t * 1.3); by += 8 * math.cos(t * 1.1)
        pk = ss(21.6, 23.2, t)
        if pk > 0:
            dr.ellipse((bx - 52, by - 52, bx + 52, by + 52), outline=mul((205, 180, 255), pk), width=4)
        if 23.6 < t < 27.8:
            dg = (0.5 + 0.5 * math.sin((t - 23.6) * 6)) * (1 - ss(26.4, 27.6, t))
            for j in range(10):
                ang = j * 0.628 + t
                dr.ellipse((bx + 70 * math.cos(ang) - 6, by + 70 * math.sin(ang) - 6, bx + 70 * math.cos(ang) + 6, by + 70 * math.sin(ang) + 6), fill=mul((180, 230, 120), dg))
        if t > 32.0:
            for ang, ph in FOOD:
                q = (t * 0.5 + ph) % 1
                r = lerp(HR - 20, 60, q)
                dr.ellipse((bx + r * math.cos(ang) - 6, by + r * math.sin(ang) - 6, bx + r * math.cos(ang) + 6, by + r * math.sin(ang) + 6), fill=mul((230, 200, 110), ss(32.0, 33, t)))
        capsule(dr, bx, by, 60, 46, 0.5 + 0.2 * math.sin(t * 0.6), AER)
        if t > 27.8: spark(dr, bx, by, ss(27.8, 29, t), t, 0)
        dna_loop(dr, HC[0] - 20, HC[1] + 60, 1.2, 1.0, t)
        return img
    if 36.2 <= t < 40.4:
        g = 0.5 + 0.5 * math.sin(t * 3)
        bx, by = MPOS[0]
        dr.ellipse((bx - 60, by - 60, bx + 60, by + 60), outline=mul((255, 220, 150), g), width=3)
    img = cell_interior(img, t, cx, cy, zoom)
    dr = ImageDraw.Draw(img)
    put(img, L_MITO, MPOS[0][0] + 150, MPOS[0][1] - 110, ss(41.0, 41.8, t) * (1 - ss(52.6, 53.2, t)))
    put(img, L_NUC, 500, 960 + 150, ss(46.6, 47.4, t) * (1 - ss(52.6, 53.2, t)))
    put(img, L_EUK, cx, cy - HR * zoom - 60, ss(49.0, 49.8, t))
    tr = ss(57.2, 59.0, t)
    if tr > 0:
        top = cy - HR * zoom - 60
        ends = [(220, 470), (540, 400), (860, 470)]
        for (ex, ey) in ends:
            mx, my = lerp(cx, ex, tr), lerp(top - 45, ey + 60, tr)
            dr.line((cx, top - 45, mx, my), fill=(200, 210, 220), width=4)
        if tr > 0.95:
            a = ss(58.6, 59.4, t)
            x, y = ends[0]; dr.ellipse((x - 26, y - 46, x + 26, y + 46), fill=mul((90, 180, 90), a)); dr.line((x, y - 40, x, y + 60), fill=mul((60, 120, 60), a), width=4)
            x, y = ends[1]; dr.chord((x - 50, y - 40, x + 50, y + 40), 180, 360, fill=mul((200, 150, 100), a)); dr.rectangle((x - 12, y, x + 12, y + 44), fill=mul((230, 210, 180), a))
            x, y = ends[2]; dr.ellipse((x - 46, y - 22, x + 34, y + 22), fill=mul((90, 150, 230), a)); dr.polygon([(x + 30, y), (x + 62, y - 24), (x + 62, y + 24)], fill=mul((90, 150, 230), a))
            put(img, L_PL, ends[0][0], ends[0][1] - 90, a); put(img, L_FU, ends[1][0], ends[1][1] - 90, a); put(img, L_AN, ends[2][0], ends[2][1] - 90, a)
    return img

def scene_a(t):
    img, dr = sea(t + 210)
    bacteria_field(img, dr, t, glow_from=10.6)
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 15.0: return dim(scene_a(t), 1 - ss(14.4, 15.0, t))
    return dim(scene_main(t), ss(15.0, 15.6, t))

CAPS = [(6.4, 10.6, '氧气多了，有的细菌学会了用它'), (10.6, 14.8, '用氧气分解食物，能量多出十几倍'),
        (15.2, 19.4, '约 20 亿年前，一个大细胞'), (19.4, 23.6, '吞下了一个会用氧气的细菌'),
        (23.6, 27.8, '奇怪的是，它没有被消化'), (27.8, 32.0, '细菌住在里面，替主人用氧气发电'),
        (32.0, 36.2, '主人给它庇护和食物'), (36.2, 40.4, '它们再也离不开对方'),
        (40.4, 44.6, '被吞的细菌，变成了线粒体'), (44.6, 48.8, '细胞把自己的 DNA，包进了细胞核'),
        (48.8, 53.0, '更复杂的细胞诞生了：真核细胞'), (53.0, 57.2, '有了发电厂，细胞能长得更大'),
        (57.2, 61.6, '后来所有的动物、植物和真菌，都来自它')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep7_{ts}.png')
