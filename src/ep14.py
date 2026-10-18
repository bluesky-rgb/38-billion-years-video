import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep13 import acanth

CLEAN = False
rng = np.random.default_rng(141)
yy = np.arange(H, dtype=np.float32)[:, None, None]
SWAMP_SKY = np.clip((np.array([150, 175, 150]) * (1 - yy / 1100) + np.array([205, 205, 170]) * (yy / 1100)) * np.ones((1, W, 1)), 0, 255)
WL = 1240

def tree(dr, x, base, h, s, fallen=0.0):
    if fallen > 0:
        a = fallen * 1.35
        tx, ty = x + h * math.sin(a), base - h * math.cos(a)
        dr.line((x, base, tx, ty), fill=(85, 70, 50), width=int(22 * s))
        for j in range(6):
            u = 0.75 + j * 0.05
            px, py = x + h * u * math.sin(a), base - h * u * math.cos(a)
            dr.ellipse((px - 40 * s, py - 18 * s, px + 40 * s, py + 18 * s), fill=(70, 110, 55))
        return
    dr.line((x, base, x, base - h), fill=(85, 70, 50), width=int(22 * s))
    for j in range(14):
        y = base - h * (0.15 + j * 0.06)
        dr.ellipse((x - 14 * s, y - 6 * s, x + 14 * s, y + 6 * s), outline=(60, 50, 35), width=2)
    for k in range(7):
        ang = -math.pi / 2 + (k - 3) * 0.42
        ex, ey = x + 120 * s * math.cos(ang), base - h + 120 * s * math.sin(ang) + 40 * s
        dr.line((x, base - h, ex, ey), fill=(60, 115, 55), width=int(10 * s))
        dr.ellipse((ex - 22 * s, ey - 10 * s, ex + 22 * s, ey + 10 * s), fill=(70, 130, 60))

TREES = [(90, 760, 1.0), (300, 900, 1.3), (520, 700, 0.9), (720, 860, 1.2), (950, 780, 1.05)]
def dragonfly(dr, x, y, s, t):
    dr.line((x - 60 * s, y, x + 60 * s, y), fill=(40, 70, 80), width=int(8 * s))
    dr.ellipse((x + 50 * s, y - 8 * s, x + 70 * s, y + 8 * s), fill=(30, 50, 60))
    fl = math.sin(t * 40) * 0.5 + 0.5
    for dx in (20, 40):
        for sg in (-1, 1):
            dr.ellipse((x + dx * s - 14 * s, y + sg * (8 + 70 * fl) * s - 10 * s, x + dx * s + 14 * s, y + sg * (8 + 70 * fl) * s + 10 * s + 0), outline=(200, 230, 240), width=2)
            dr.line((x + dx * s, y, x + dx * s, y + sg * (12 + 80 * fl) * s), fill=(210, 235, 245), width=int(4 * s))
L_JELLY = text_img('只有一层胶质的卵', FM, 38, (230, 240, 230), 3); L_O2 = text_img('氧气约 30%（今天 21%）', FM, 36, (240, 240, 230), 3)
L_DF = text_img('翼展约 70 厘米', FM, 38, (240, 240, 230), 3)
def forest(t):
    img = Image.fromarray(SWAMP_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for x, h, s in TREES: tree(dr, x, WL - 20, h, s)
    dr.polygon([(0, WL - 30), (W, WL - 50), (W, WL), (0, WL)], fill=(80, 70, 50))
    dr.rectangle((0, WL, W, H), fill=(60, 90, 70))
    for k in range(12):
        ex, ey = 360 + (k % 6) * 42, WL + 70 + (k // 6) * 38
        dr.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=(190, 220, 195), outline=(230, 245, 235), width=2)
        dr.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=(60, 70, 50))
    dk = ss(14.8, 16.0, t)
    if dk > 0:
        dragonfly(dr, lerp(-200, 640, ss(14.8, 19.0, t)), 560 + 40 * math.sin(t * 2), 3.2, t)
    put(img, L_JELLY, 480, WL + 190, ss(6.6, 7.4, t) * (1 - ss(10.2, 10.8, t)))
    put(img, L_O2, 540, 330, ss(10.8, 11.6, t) * (1 - ss(14.4, 14.8, t)))
    put(img, L_DF, lerp(-200, 640, ss(14.8, 19.0, t)), 300, ss(15.6, 16.4, t))
    return img

L_COAL = text_img('煤', FB, 52, (240, 230, 210), 4)
def coal(t):
    img = Image.fromarray(SWAMP_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    surf = 760
    fall = ss(19.6, 22.4, t)
    for i, (x, h, s) in enumerate(TREES[:4]):
        tree(dr, x, surf, h * 0.6, s * 0.7, fallen=fall * (0.9 + 0.1 * i))
    dr.rectangle((0, surf, W, H), fill=(110, 92, 70))
    bury = ss(23.6, 27.6, t)
    nl = int(1 + bury * 5)
    for j in range(nl):
        y0 = surf + 40 + j * 150 * bury
        dr.rectangle((0, y0, W, y0 + 60), fill=(60, 45, 30) if j else (50, 40, 28))
    if bury > 0.4:
        y0 = surf + 40 + 4 * 150 * bury
        dr.rectangle((0, y0, W, y0 + 90), fill=(25, 22, 22))
        put(img, L_COAL, 540, y0 + 45, ss(25.6, 26.4, t))
    return img

def puddle(t):
    img = Image.fromarray(SWAMP_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 900, W, H), fill=(130, 110, 80))
    dry = ss(28.6, 32.0, t)
    rw = lerp(380, 120, dry)
    dr.ellipse((300 - rw, 1180 - rw * 0.35, 300 + rw, 1180 + rw * 0.35), fill=(70, 100, 85))
    for k in range(8):
        ex, ey = 220 + (k % 4) * 52, 1160 + (k // 4) * 40
        shrink = 1 - 0.5 * dry
        col = tuple(int(v) for v in lerp(np.array([190, 220, 195]), np.array([150, 135, 100]), dry))
        r = 18 * shrink
        dr.ellipse((ex - r, ey - r, ex + r, ey + r), fill=col, outline=(220, 220, 200), width=2)
    far = ss(32.6, 34.6, t)
    if far > 0:
        for k in range(6):
            ex, ey = 760 + (k % 3) * 50, 1020 + (k // 3) * 44
            dr.ellipse((ex - 20, ey - 20, ex + 20, ey + 20), fill=mul((240, 235, 220), far), outline=mul((200, 190, 170), far), width=3)
        dr.line((420, 1180, 740, 1040), fill=mul((255, 225, 160), far), width=4)
        dr.polygon([(740, 1040), (712, 1042), (724, 1064)], fill=mul((255, 225, 160), far))
    return img

# ---------- egg cross-section ----------
EX, EY = 540, 900
L_EMB = text_img('胚胎', FB, 40, (255, 225, 190), 3); L_AMN = text_img('羊膜 · 羊水', FB, 40, (170, 220, 255), 3)
L_ALL = text_img('收集废物的膜', FM, 36, (230, 220, 190), 3); L_YOLK = text_img('卵黄：养分', FM, 36, (255, 220, 120), 3)
L_SHELL = text_img('硬壳', FB, 40, (240, 240, 240), 3); L_PORE = text_img('小孔：氧气进来', FM, 36, (220, 240, 255), 3)
L_AMNIOTE = text_img('羊膜卵', FB, 56, (255, 225, 160), 4)
def egg(t):
    img = Image.fromarray(np.full((H, W, 3), (22, 36, 44), np.uint8)); dr = ImageDraw.Draw(img)
    rx, ry = 300, 380
    sk = ss(49.6, 51.4, t)
    if sk > 0:
        dr.ellipse((EX - rx - 22, EY - ry - 22, EX + rx + 22, EY + ry + 22), fill=mul((235, 230, 215), sk))
        if t > 53.8:
            pk = ss(53.8, 54.6, t)
            for k in range(28):
                a = k * 2 * math.pi / 28
                px, py = EX + (rx + 11) * math.cos(a), EY + (ry + 11) * math.sin(a)
                dr.ellipse((px - 4, py - 4, px + 4, py + 4), fill=mul((120, 110, 95), pk))
            for k in range(10):
                q = (t * 0.6 + k / 10) % 1; a = k * 0.63 + 0.2
                rr = lerp(rx + 140, rx - 30, q)
                px, py = EX + rr * math.cos(a), EY + rr * ry / rx * math.sin(a)
                dr.ellipse((px - 9, py - 9, px + 9, py + 9), fill=mul((150, 210, 255), pk * (1 - 0.6 * q)), outline=mul((230, 245, 255), pk), width=2)
    base = (60, 110, 90) if t < 37.4 else (205, 215, 195)
    dr.ellipse((EX - rx, EY - ry, EX + rx, EY + ry), fill=base, outline=(240, 245, 235), width=4)
    jelly = 1 - ss(37.2, 39.4, t)
    if jelly > 0:
        dr.ellipse((EX - rx + 30, EY - ry + 30, EX + rx - 30, EY + ry - 30), outline=mul((180, 220, 190), jelly), width=6)
    yk = ss(45.6, 47.0, t)
    if yk > 0:
        dr.ellipse((EX - 160, EY + 60, EX + 160, EY + 330), fill=mul((245, 200, 70), yk), outline=mul((255, 230, 140), yk), width=3)
        dr.ellipse((EX + 60, EY - 300, EX + 250, EY - 120), fill=mul((200, 185, 140), yk), outline=mul((235, 220, 180), yk), width=3)
    ak = ss(41.4, 42.8, t)
    if ak > 0:
        dr.ellipse((EX - 200, EY - 260, EX + 120, EY + 60), fill=mul((110, 170, 220), ak), outline=mul((200, 235, 255), ak), width=4)
    ek = ss(38.6, 40.4, t)
    if ek > 0:
        cx, cy = EX - 40, EY - 100
        pts = [(cx + 70 * math.cos(p) * (1 - 0.35 * math.sin(p / 2)), cy + 70 * math.sin(p)) for p in np.linspace(0.3, 2 * math.pi - 0.3, 30)]
        dr.polygon(pts, fill=mul((240, 175, 160), ek), outline=mul((255, 210, 195), ek))
        dr.ellipse((cx + 10, cy - 50, cx + 34, cy - 26), fill=mul((60, 30, 30), ek))
        dr.line((cx - 40, cy + 50, EX - 30, EY + 80), fill=mul((240, 175, 160), ek), width=8)
    put(img, L_EMB, EX - 40, EY - 220, ss(39.0, 39.8, t) * (1 - ss(41.0, 41.4, t)))
    put(img, L_AMN, EX - 320, EY - 330, ss(42.0, 42.8, t))
    put(img, L_ALL, EX + 250, EY - 360, ss(45.8, 46.6, t))
    put(img, L_YOLK, EX, EY + 420, ss(46.4, 47.2, t))
    put(img, L_SHELL, EX + 300, EY + 330, ss(50.4, 51.2, t))
    put(img, L_PORE, EX - 200, EY + 470, ss(54.4, 55.2, t))
    put(img, L_AMNIOTE, EX, 340, ss(58.2, 59.0, t))
    return img

# ---------- Hylonomus ----------
L_HYL = text_img('林蜥 · 约 20 厘米', FB, 44, (255, 225, 160), 3); L_SCALE = text_img('干燥的鳞片皮肤', FM, 38, (240, 230, 210), 3)
L_STUMP = text_img('空心树桩', FM, 38, (240, 230, 210), 3)
def lizard(dr, x, y, s, t, a=1.0):
    walk = math.sin(t * 4)
    body = [(x - 120 * s + 240 * s * u, y) for u in np.linspace(0, 1, 30)]
    up = [(px, py - 18 * s * math.sin(math.pi * min(1, u * 1.3))) for (px, py), u in zip(body, np.linspace(0, 1, 30))]
    dn = [(px, py + 14 * s * math.sin(math.pi * min(1, u * 1.3))) for (px, py), u in zip(body, np.linspace(0, 1, 30))]
    dr.polygon(up + dn[::-1], fill=mul((120, 110, 70), a), outline=mul((80, 70, 45), a))
    dr.polygon([(x - 120 * s, y), (x - 260 * s, y + 6 * s), (x - 120 * s, y + 8 * s)], fill=mul((115, 105, 65), a))
    dr.ellipse((x + 100 * s, y - 10 * s, x + 110 * s, y), fill=mul((25, 25, 30), a))
    for j in range(12):
        sx = x - 90 * s + j * 15 * s
        dr.arc((sx - 6 * s, y - 14 * s, sx + 6 * s, y - 2 * s), 200, 340, fill=mul((90, 80, 50), a), width=2)
    for i, lx in enumerate((x + 60 * s, x - 60 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 8 * s, lx + 16 * s * ph, y + 30 * s), fill=mul((110, 100, 62), a), width=int(8 * s))
def hylonomus(t):
    img = Image.fromarray(SWAMP_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for x, h, s in TREES[::2]: tree(dr, x, 1000, h * 0.7, s * 0.8)
    dr.rectangle((0, 1000, W, H), fill=(120, 100, 72))
    dr.rectangle((640, 640, 900, 1010), fill=(95, 75, 52)); dr.rectangle((680, 660, 860, 1010), fill=(40, 30, 22))
    for k in range(5):
        ex, ey = 180 + k * 46, 1060
        dr.ellipse((ex - 18, ey - 22, ex + 18, ey + 22), fill=(240, 235, 220), outline=(200, 190, 170), width=3)
    lizard(dr, lerp(250, 520, ss(62.8, 70.0, t)), 960, 1.6, t)
    put(img, L_SCALE, 420, 800, ss(63.0, 63.8, t) * (1 - ss(66.4, 66.8, t)))
    put(img, L_HYL, 420, 800, ss(67.0, 67.8, t) * (1 - ss(70.6, 71.0, t)))
    put(img, L_STUMP, 770, 590, ss(71.2, 72.0, t))
    return img

# ---------- two branches ----------
L_AMN2 = text_img('羊膜动物', FB, 44, (255, 225, 160), 3)
L_SAUR = text_img('爬行类 · 恐龙 · 鸟', FB, 40, (170, 220, 170), 3); L_SYN = text_img('合弓类 → 哺乳动物', FB, 40, (240, 190, 160), 3)
L_YOU = text_img('你', FB, 64, (255, 225, 160), 4); L_INLAND = text_img('远离水的内陆', FM, 38, (240, 230, 210), 3)
def branches(t):
    img = Image.fromarray(np.full((H, W, 3), (22, 36, 44), np.uint8)); dr = ImageDraw.Draw(img)
    if t < 79.8:
        img = Image.fromarray(SWAMP_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.polygon([(0, 1100), (300, 900), (600, 1000), (W, 800), (W, H), (0, H)], fill=(150, 125, 90))
        dr.ellipse((60, 1180, 400, 1300), fill=(70, 100, 85))
        for i in range(4):
            lizard(dr, lerp(200, 600 + i * 100, ss(75.8, 79.6, t)), 1050 - i * 60 - lerp(0, 120, ss(75.8, 79.6, t)) * (i / 3), 0.9, t + i)
        put(img, L_INLAND, 700, 760, ss(76.2, 77.0, t))
        return img
    rx, ry = 540, 1400
    dr.ellipse((rx - 16, ry - 16, rx + 16, ry + 16), fill=(255, 225, 160))
    put(img, L_AMN2, rx, ry + 60, 1.0)
    k1 = ss(80.0, 82.0, t); k2 = ss(84.2, 86.2, t)
    lx, ly = lerp(rx, 260, k1), lerp(ry, 760, k1)
    dr.line((rx, ry, lx, ly), fill=(150, 210, 150), width=8)
    if k1 > 0.95: put(img, L_SAUR, 260, 700, ss(81.6, 82.4, t))
    mx, my = lerp(rx, 820, k2), lerp(ry, 760, k2)
    if k2 > 0:
        dr.line((rx, ry, mx, my), fill=(240, 180, 150), width=8)
    if k2 > 0.95:
        put(img, L_SYN, 820, 700, ss(85.8, 86.6, t))
        yk = ss(88.6, 89.6, t)
        if yk > 0:
            dr.line((820, 660, 820, 460), fill=mul((255, 225, 160), yk), width=6)
            g = yk * (0.7 + 0.3 * math.sin(t * 3))
            dr.ellipse((820 - 80, 380 - 80, 820 + 80, 380 + 80), outline=mul((255, 225, 160), g), width=4)
            put(img, L_YOU, 820, 380, yk)
    return img

def permian(t):
    yy2 = np.arange(H, dtype=np.float32)[:, None, None]
    sky = np.clip((np.array([90, 70, 80]) * (1 - yy2 / 1100) + np.array([230, 150, 100]) * (yy2 / 1100)) * np.ones((1, W, 1)), 0, 255)
    img = Image.fromarray(sky.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1100), (W, 1050), (W, H), (0, H)], fill=(150, 110, 75))
    dr.polygon([(620, 1060), (820, 820), (1000, 1050)], fill=(80, 60, 50))
    g = 0.6 + 0.4 * math.sin(t * 2)
    dr.ellipse((780, 780, 860, 840), fill=mul((255, 140, 60), g))
    for k in range(6):
        q = (t * 0.2 + k / 6) % 1
        dr.ellipse((820 - 60 - q * 120, 760 - q * 400, 820 + 60 + q * 120, 840 - q * 400), fill=mul((90, 80, 85), 1 - q))
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 6.0: return acanth(t + 86)
    if t < 19.2: return dim(forest(t), ss(6.0, 6.6, t) * (1 - ss(18.6, 19.2, t)))
    if t < 28.0: return dim(coal(t), ss(19.2, 19.8, t) * (1 - ss(27.4, 28.0, t)))
    if t < 36.8: return dim(puddle(t), ss(28.0, 28.6, t) * (1 - ss(36.2, 36.8, t)))
    if t < 62.4: return dim(egg(t), ss(36.8, 37.4, t) * (1 - ss(61.8, 62.4, t)))
    if t < 75.4: return dim(hylonomus(t), ss(62.4, 63.0, t) * (1 - ss(74.8, 75.4, t)))
    if t < 92.8:
        k = ss(75.4, 76.0, t)
        if 79.4 < t < 80.2: k *= 1 - 0.85 * math.sin(math.pi * (t - 79.4) / 0.8)
        return dim(branches(t), k)
    return dim(permian(t), ss(92.8, 93.6, t))

CAPS = [(6.4, 10.6, '两栖动物的卵只有一层胶质，必须产在水里'), (10.6, 14.8, '石炭纪到处是沼泽森林，空气里的氧气比今天多'),
        (14.8, 19.0, '昆虫长得很大，有的蜻蜓翼展约 70 厘米'), (19.4, 23.6, '大量树木倒在沼泽里，没有完全腐烂'),
        (23.6, 27.8, '被埋进地下，后来变成了煤'), (28.2, 32.4, '离水越远，卵越容易干死'),
        (32.4, 36.6, '能在稍干的地方产卵，就能去别人去不了的地方'), (37.0, 41.2, '有的四足动物，在一代代变异中，卵里长出了几层膜'),
        (41.2, 45.4, '羊膜把胚胎包在一小包液体里，这就是羊水'), (45.4, 49.6, '另一层膜收集废物，卵黄提供养分'),
        (49.6, 53.8, '最外面长出一层硬壳，挡住水分流失'), (53.8, 58.0, '壳上布满小孔，能让氧气透进来'),
        (58.0, 62.2, '这就是羊膜卵：把一小片"海水"装进蛋里'), (62.6, 66.8, '同时，皮肤变得干燥、长出鳞片，不怕失水'),
        (66.8, 71.0, '比如约 3.12 亿年前的林蜥，最早的爬行类之一'), (71.0, 75.2, '它的化石，在加拿大的空心树桩里被发现'),
        (75.6, 79.8, '动物第一次能在远离水的内陆生活'), (79.8, 84.0, '羊膜动物很快分成两支：一支通往爬行类、恐龙和鸟'),
        (84.0, 88.2, '另一支叫合弓类，通往哺乳动物，也就是你的祖先')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep14_{ts}.png')
