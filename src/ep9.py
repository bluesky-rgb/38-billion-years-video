import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import sea, mul

CLEAN = False
rng = np.random.default_rng(91)
PUR = (150, 125, 210); NUC = (120, 160, 250)

def ecell(dr, x, y, r, col=PUR, a=1.0, nuc=True, flag=None, t=0.0, edge=None):
    if flag is not None:
        ang = flag
        pts = []
        for k in range(10):
            d = r + k * r * 0.18
            w = r * 0.18 * math.sin(k * 0.9 - t * 9)
            pts.append((x + d * math.cos(ang) - w * math.sin(ang), y + d * math.sin(ang) + w * math.cos(ang)))
        dr.line(pts, fill=mul((210, 225, 235), a), width=max(2, int(r * 0.08)))
    dr.ellipse((x - r, y - r, x + r, y + r), fill=mul(col, a), outline=mul(edge or tuple(min(255, int(v * 1.35)) for v in col), a), width=max(2, int(r * 0.06)))
    if nuc:
        rn = r * 0.32
        dr.ellipse((x - rn, y - rn, x + rn, y + rn), fill=mul(NUC, a))

def glue(dr, p, q, a):
    for k in range(3):
        u = (k + 1) / 4
        x, y = lerp(p[0], q[0], u), lerp(p[1], q[1], u)
        dr.ellipse((x - 6, y - 6, x + 6, y + 6), fill=mul((250, 215, 110), a))

FREE = [(rng.random() * W, 420 + rng.random() * 1150, 22 + rng.random() * 12, rng.random() * 6) for _ in range(22)]
def scene_a(t):
    img, dr = sea(t + 300)
    for i, (x0, y0, r, ph) in enumerate(FREE):
        x = (x0 + 25 * math.sin(t * 0.4 + ph) + t * 5) % (W + 80) - 40; y = y0 + 20 * math.cos(t * 0.3 + ph)
        ecell(dr, x, y, r, flag=ph * 1.7, t=t + ph)
    for k in range(30):
        q = (t * 0.12 + k / 30) % 1
        x = (k * 173) % W; y = lerp(1600, 420, q)
        dr.ellipse((x - 4, y - 4, x + 4, y + 4), outline=(200, 230, 245), width=2)
    return img

HEX = [(0, 0)] + [(math.cos(k * math.pi / 3) * 92, math.sin(k * math.pi / 3) * 92) for k in range(6)]
L_PRED = text_img('捕食者', FM, 38, (220, 210, 200), 3)
def colony(dr, cx, cy, n, t, a=1.0, flag=False, s=1.0):
    pts = [(cx + dx * s, cy + dy * s) for dx, dy in HEX[:n]]
    for i in range(1, n):
        glue(dr, pts[0], pts[i], a)
    for i, (x, y) in enumerate(pts):
        fa = math.atan2(y - cy, x - cx) if i else None
        ecell(dr, x, y, 46 * s, a=a, flag=fa if flag else None, t=t + i)
    return pts

def scene_b(t):
    img, dr = sea(t + 300)
    cx, cy = 540, 1000
    if t < 23.8:
        k = ss(16.0, 18.6, t)
        p, q = (cx - 52 * k, cy), (cx + 52 * k, cy)
        if k < 0.98:
            ecell(dr, cx, cy, 60 + 10 * math.sin(k * math.pi), t=t)
        else:
            ga = ss(19.8, 20.6, t)
            glue(dr, p, q, ga)
            ecell(dr, *p, 46, t=t); ecell(dr, *q, 46, t=t)
        return img
    if t < 32.2:
        mv = ss(28.0, 31.8, t)
        ccx, ccy = cx, cy - 260 * mv
        colony(dr, ccx, ccy, 7, t, flag=t > 28.0)
        lx = 230 + 30 * math.sin(t)
        lone_dead = ss(25.6, 26.6, t)
        px = lerp(-160, 230, ss(24.0, 25.8, t)) if t < 27 else lerp(230, 330, ss(27, 27.8, t)) - lerp(0, 380, ss(27.8, 29.5, t))
        py = 1350
        if lone_dead < 1:
            ecell(dr, lx + 20 * lone_dead, py, 34 * (1 - lone_dead) + 1, t=t)
        r = 120 + 8 * math.sin(t * 3)
        pts = [(px + (r + 14 * math.sin(a_ * 5 + t * 2)) * math.cos(a_), py - 20 + (r + 14 * math.sin(a_ * 5 + t * 2)) * math.sin(a_)) for a_ in np.linspace(0, 2 * math.pi, 40)]
        dr.polygon(pts, fill=(95, 100, 105), outline=(150, 155, 160))
        put(img, L_PRED, px, py - 170, ss(24.2, 25, t) * (1 - ss(29.0, 29.6, t)))
        for k in range(8):
            if t > 28.0:
                q = (t * 1.2 + k / 8) % 1
                dr.line((ccx - 200 + k * 55, ccy + 200 + q * 80, ccx - 200 + k * 55, ccy + 230 + q * 80), fill=mul((180, 220, 235), 0.6 * (1 - q)), width=3)
        return img
    for j, (ox, oy) in enumerate([(540, 740), (250, 1080), (830, 1100), (420, 1380), (720, 1430)]):
        a = 1.0 if j == 0 else ss(32.6 + j * 0.6, 33.4 + j * 0.6, t)
        if a > 0.02: colony(dr, ox + 10 * math.sin(t + j), oy + 10 * math.cos(t * 0.8 + j), 7, t + j, 1.0, flag=True, s=(0.7 if j else 1.0) * a)
    return img

L_SOLO = text_img('单独生活', FM, 38, (215, 225, 235), 3); L_ROS = text_img('连成一团', FM, 38, (215, 225, 235), 3)
def choano(dr, x, y, ang, s, t, a=1.0):
    c, sn = math.cos(ang), math.sin(ang)
    for k in range(9):
        off = (k - 4) * 0.13
        ex, ey = x + 70 * s * math.cos(ang + off), y + 70 * s * math.sin(ang + off)
        dr.line((x + 24 * s * c, y + 24 * s * sn, ex, ey), fill=mul((190, 210, 220), a), width=2)
    pts = []
    for k in range(10):
        d = 30 * s + k * 11 * s; w = 6 * s * math.sin(k * 0.9 - t * 9)
        pts.append((x + d * c - w * sn, y + d * sn + w * c))
    dr.line(pts, fill=mul((230, 235, 245), a), width=3)
    dr.ellipse((x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s), fill=mul((165, 140, 215), a), outline=mul((210, 190, 250), a), width=2)
    dr.ellipse((x - 8 * s, y - 8 * s, x + 8 * s, y + 8 * s), fill=mul(NUC, a))
def scene_c(t):
    img, dr = sea(t + 300)
    choano(dr, 270 + 10 * math.sin(t), 1000, -1.2 + 0.1 * math.sin(t * 2), 1.4, t)
    a = ss(41.0, 42.0, t)
    rx, ry = 780, 1000
    for k in range(8):
        ang = k * math.pi / 4 + t * 0.2
        if a > 0.02: choano(dr, rx + 60 * a * math.cos(ang), ry + 60 * a * math.sin(ang), ang, 0.9 * a, t + k, 1.0)
    put(img, L_SOLO, 270, 1250, ss(37.0, 37.8, t)); put(img, L_ROS, 780, 1250, a)
    return img

OUT = [(math.cos(k * math.pi / 6) * 210, math.sin(k * math.pi / 6) * 210) for k in range(12)]
INN = [(0, 0)] + [(math.cos(k * math.pi / 3 + 0.5) * 105, math.sin(k * math.pi / 3 + 0.5) * 105) for k in range(6)]
GREEN = (80, 180, 140); ORANGE = (220, 140, 80)
L_OUT = text_img('外层：摆动、抓食物', FM, 36, (160, 230, 200), 3)
L_IN = text_img('里层：消化、繁殖', FM, 36, (250, 200, 150), 3)
L_DO = text_img('外层细胞', FM, 34, (160, 230, 200), 2); L_DI = text_img('里层细胞', FM, 34, (250, 200, 150), 2)
L_DNA = text_img('同一套 DNA', FB, 40, (200, 215, 255), 3)
SW_O = [1, 1, 0, 0, 1, 0, 0, 1]; SW_I = [0, 0, 1, 1, 0, 1, 1, 0]
def big_colony(dr, cx, cy, t, k, a=1.0, drop=0.0):
    for i, (dx, dy) in enumerate(OUT):
        col = tuple(int(v) for v in lerp(np.array(PUR), np.array(GREEN), k))
        x, y = cx + dx, cy + dy
        if i == 2 and drop > 0:
            x += drop * 220; y -= drop * 160
            if drop < 0.97: ecell(dr, x, y, 44 * (1 - drop), (110, 110, 120), a, flag=math.atan2(dy, dx), t=t + i)
            continue
        ecell(dr, x, y, 44, col, a, flag=math.atan2(dy, dx) if k > 0.3 else None, t=t + i)
    for i, (dx, dy) in enumerate(INN):
        col = tuple(int(v) for v in lerp(np.array(PUR), np.array(ORANGE), k))
        ecell(dr, cx + dx, cy + dy, 44, col, a, t=t)
def dna_strip(img, dr, x0, y, sw, col, a):
    for i, on in enumerate(sw):
        x = x0 + i * 52
        dr.rounded_rectangle((x, y - 18, x + 44, y + 18), radius=8, fill=mul(col if on else (45, 55, 70), a), outline=mul((140, 160, 200), a), width=2)
def scene_d(t):
    img, dr = sea(t + 300)
    cx, cy = 540, 860
    k = ss(45.6, 48.6, t)
    big_colony(dr, cx, cy, t, k)
    la = ss(49.6, 50.4, t) * (1 - ss(53.2, 53.8, t))
    put(img, L_OUT, cx, cy - 300, la); put(img, L_IN, cx, cy + 300, la)
    da = ss(53.8, 54.6, t)
    if da > 0:
        put(img, L_DNA, W / 2, 1210, da)
        sk = ss(58.0, 59.0, t)
        swo = [1] * 8 if sk == 0 else SW_O; swi = [1] * 8 if sk == 0 else SW_I
        put(img, L_DO, 170, 1300, da); dna_strip(img, dr, 300, 1300, swo, GREEN, da)
        put(img, L_DI, 170, 1380, da); dna_strip(img, dr, 300, 1380, swi, ORANGE, da)
    return img

L_SPONGE = text_img('海绵', FB, 46, (240, 220, 180), 3)
def scene_e(t):
    img, dr = sea(t + 300)
    if t < 70.6:
        drop = ss(66.6, 69.0, t)
        big_colony(dr, 540, 900, t, 1.0, drop=drop)
        if t < 66.4:
            g = 0.5 + 0.5 * math.sin(t * 4)
            dr.ellipse((540 - 290, 900 - 290, 540 + 290, 900 + 290), outline=mul((250, 215, 110), g * ss(62.4, 63.4, t)), width=3)
        return img
    a = ss(70.8, 71.8, t)
    base_y = 1450
    pts = [(380, base_y), (340, 1100), (380, 820), (450, 700), (630, 700), (700, 820), (740, 1100), (700, base_y)]
    dr.polygon(pts, fill=mul((205, 170, 110), a), outline=mul((240, 210, 150), a))
    dr.ellipse((470, 680, 610, 730), fill=mul((60, 45, 30), a))
    pr = np.random.default_rng(5)
    for k in range(26):
        u, v = pr.random(), pr.random()
        y = lerp(800, 1400, v); half = lerp(110, 170, v)
        x = 540 + (u - 0.5) * 2 * half * 0.85
        dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=mul((80, 60, 40), a))
    for k in range(6):
        q = (t * 0.6 + k / 6) % 1
        side = -1 if k % 2 else 1
        x = lerp(540 + side * 330, 540 + side * 160, q); y = 1100 + (k - 3) * 60
        dr.line((x, y, x + side * -26, y), fill=mul((170, 220, 240), a * (1 - q)), width=4)
        y2 = lerp(690, 520, q)
        dr.line((540 + (k - 3) * 14, y2, 540 + (k - 3) * 14, y2 - 24), fill=mul((170, 220, 240), a * (1 - q)), width=4)
    put(img, L_SPONGE, 540, 1560, a)
    return img

L_NEED = text_img('身体需要的能量', FM, 32, (215, 215, 220), 2); L_GIVE = text_img('线粒体 + 氧气能提供的', FM, 32, (215, 215, 220), 2)
def scene_f(t):
    img, dr = sea(t + 300)
    s = lerp(0.6, 1.0, ss(75.4, 78.0, t))
    for i, (dx, dy) in enumerate(OUT + INN):
        ecell(dr, 540 + dx * s, 820 + dy * s, 44 * s, GREEN if i < 12 else ORANGE, flag=math.atan2(dy, dx) if i < 12 else None, t=t + i)
    for k in range(24):
        q = (t * 0.25 + k / 24) % 1
        x = (k * 211) % W; y = lerp(1600, 380, q)
        dr.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(215, 240, 255), width=2)
    need = lerp(0.25, 0.8, ss(75.4, 78.4, t)); give = lerp(0.3, 0.85, ss(79.4, 82.4, t))
    for i, (lab, v, c) in enumerate(((L_NEED, need, (255, 150, 90)), (L_GIVE, give, (120, 220, 160)))):
        y = 1290 + i * 80
        put(img, lab, 220, y - 34, 1.0)
        dr.rounded_rectangle((100, y - 12, 980, y + 14), radius=13, fill=(25, 30, 40), outline=(90, 100, 115), width=2)
        dr.rounded_rectangle((103, y - 9, 103 + 874 * v, y + 11), radius=10, fill=c)
    return img

FR = [(160, 1.0, 0.2), (360, 1.3, 1.4), (900, 1.15, 2.2), (760, 0.8, 3.1)]
DISC = [(560, 1500, 1.0), (260, 1560, 0.7), (850, 1580, 0.85)]
L_FROND = text_img('像叶子的', FM, 36, (220, 230, 210), 3); L_DISC = text_img('像圆盘的', FM, 36, (220, 230, 210), 3)
def scene_g(t):
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    f = (np.array([25, 85, 105]) * (1 - yy / H) + np.array([8, 30, 40]) * (yy / H)) * np.ones((1, W, 1))
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 1460, W, H), fill=(120, 105, 80))
    for k in range(40):
        x = (k * 97) % W; dr.ellipse((x - 30, 1455 + (k % 5) * 8, x + 30, 1470 + (k % 5) * 8), fill=(135, 118, 90))
    for x, s, ph in FR:
        sway = 0.08 * math.sin(t * 0.8 + ph)
        h = 420 * s
        top = (x + h * sway, 1470 - h)
        dr.line((x, 1470, top[0], top[1]), fill=(150, 160, 110), width=int(8 * s))
        for j in range(12):
            u = (j + 1) / 13
            px, py = lerp(x, top[0], u), lerp(1470, top[1], u)
            w = 70 * s * math.sin(u * math.pi) + 10
            dr.ellipse((px - w, py - 14 * s, px, py + 6 * s), fill=(175, 180, 120), outline=(130, 140, 95))
            dr.ellipse((px, py - 14 * s, px + w, py + 6 * s), fill=(175, 180, 120), outline=(130, 140, 95))
    for x, y, s in DISC:
        rx, ry = 110 * s, 70 * s
        dr.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(200, 160, 120), outline=(150, 115, 85), width=3)
        for j in range(-6, 7):
            xx = x + j * rx / 7
            hh = ry * math.sqrt(max(0.0, 1 - (j / 7) ** 2))
            dr.line((xx, y - hh, xx, y + hh), fill=(160, 120, 90), width=2)
        dr.line((x - rx, y, x + rx, y), fill=(150, 115, 85), width=2)
    put(img, L_FROND, 360, 860, ss(92.2, 93.0, t)); put(img, L_DISC, 560, 1640 - 210, ss(93.0, 93.8, t))
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 15.2: return dim(scene_a(t), 1 - ss(14.6, 15.2, t))
    if t < 36.4: return dim(scene_b(t), ss(15.2, 15.8, t) * (1 - ss(35.8, 36.4, t)))
    if t < 45.0: return dim(scene_c(t), ss(36.4, 37.0, t) * (1 - ss(44.4, 45.0, t)))
    if t < 62.0: return dim(scene_d(t), ss(45.0, 45.6, t) * (1 - ss(61.6, 62.0, t)))
    if t < 74.8: return dim(scene_e(t), ss(62.0, 62.4, t) * (1 - ss(74.2, 74.8, t)))
    if t < 83.4: return dim(scene_f(t), ss(74.8, 75.4, t) * (1 - ss(82.8, 83.4, t)))
    return dim(scene_g(t), ss(83.4, 84.2, t))

CAPS = [(6.4, 10.6, '雪球融化后，海里养分丰富，氧气增多'), (10.6, 14.8, '海里到处是单个的真核细胞'),
        (15.4, 19.6, '细胞分裂时，有时没有完全分开'), (19.6, 23.8, '它们靠表面的"胶"，粘在了一起'),
        (23.8, 28.0, '粘成一团，个头大了，不容易被吃掉'), (28.0, 32.2, '一起摆动，还能游得更快'),
        (32.2, 36.2, '于是，粘在一起的群体留下了更多后代'), (36.6, 40.8, '今天海里还有这样的生物：领鞭毛虫'),
        (40.8, 44.8, '它们有时单独生活，有时连成一团'), (45.2, 49.4, '群体里的细胞，开始分工'),
        (49.4, 53.6, '外层摆动抓食物，里层消化和繁殖'), (53.6, 57.8, 'DNA 一模一样，为什么能做不同的事？'),
        (57.8, 61.8, '因为每个细胞，打开了不同的基因开关'), (62.2, 66.4, '分工越细，细胞越离不开彼此'),
        (66.4, 70.6, '离开群体就活不了：多细胞生物诞生了'), (70.6, 74.6, '最早的代表之一，就是海绵'),
        (75.0, 79.2, '为什么偏偏是这个时候？'), (79.2, 83.2, '身体越大越耗能，线粒体和氧气刚好够用'),
        (83.6, 87.8, '约 5.7 亿年前，海底长出了大型生物'), (87.8, 92.0, '这就是埃迪卡拉生物群'),
        (92.0, 96.2, '有的像叶子，有的像圆盘，大多躺着不动'), (96.2, 100.4, '它们还没有头，也分不清前后')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep9_{ts}.png')
