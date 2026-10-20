import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep17 import tree
from ep19 import FUR
from ep20 import hominin, savanna, SAV_SKY, render as render20

CLEAN = False
rng = np.random.default_rng(211)
STONE = (150, 145, 138)
DARK = grad((30, 30, 36), (16, 16, 20))

def lion(dr, x, y, s, t, a=1.0, face=1, walk=1.0):
    c = (200, 160, 90); ph = math.sin(t * 6) * walk
    for i, lx in enumerate((x + 70 * s, x - 70 * s)):
        p = ph * (1 if i else -1)
        dr.line((lx, y - 50 * s, lx + 14 * s * p, y), fill=mul(c, a * 0.9), width=int(18 * s))
    dr.ellipse((x - 110 * s, y - 110 * s, x + 100 * s, y - 40 * s), fill=mul(c, a))
    hx = x + face * 110 * s
    dr.ellipse((hx - 55 * s, y - 150 * s, hx + 55 * s, y - 50 * s), fill=mul((150, 100, 50), a))
    dr.ellipse((hx - 32 * s + face * 12 * s, y - 128 * s, hx + 32 * s + face * 12 * s, y - 72 * s), fill=mul(c, a))
    dr.line((x - face * 110 * s, y - 90 * s, x - face * 180 * s, y - 60 * s), fill=mul(c, a), width=int(8 * s))
def carcass(dr, x, y, s, meat=1.0):
    dr.ellipse((x - 160 * s, y - 60 * s, x + 160 * s, y + 10 * s), fill=(150, 70, 60) if meat > 0.5 else (120, 90, 70))
    for j in range(7):
        bx = x - 110 * s + j * 36 * s
        dr.arc((bx - 20 * s, y - 120 * s, bx + 20 * s, y - 10 * s), 180, 360, fill=(235, 225, 205), width=int(7 * s))
    dr.line((x + 150 * s, y - 20 * s, x + 260 * s, y - 10 * s), fill=(235, 225, 205), width=int(14 * s))
    dr.ellipse((x + 245 * s, y - 25 * s, x + 275 * s, y + 5 * s), fill=(235, 225, 205))

# ---------- A: savanna, the carcass ----------
L_FRUIT = text_img('果子不够吃', FB, 42, (255, 235, 200), 3)
L_LEFT = text_img('狮子吃剩的：肉和骨髓', FB, 42, (255, 225, 190), 3)
L_CANT = text_img('没有利爪尖牙：咬不开，撕不动', FB, 40, (255, 200, 180), 3)
def scav(t):
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((820, 540, 940, 660), fill=(255, 245, 210))
    savanna(dr); tree(dr, 980, GROUND, 470)
    carcass(dr, 520, GROUND + 60, 1.2)
    if t < 15.6:
        lion(dr, lerp(560, 1350, ss(11.0, 15.4, t)), GROUND + 40, 1.2, t, face=1)
    if t > 14.6:
        hx = lerp(-120, 300, ss(14.8, 18.6, t))
        if t <= 19.0: hominin(dr, hx, GROUND + 30, 1.3, t if t < 18.6 else 18.6)
        else:
            k = abs(math.sin(t * 4))
            hominin(dr, 360, GROUND + 30 + 30 * k, 1.3, 18.6, walk=0)
    put(img, L_FRUIT, 540, 640, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_LEFT, 540, 640, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_CANT, 540, 640, ss(19.2, 20.0, t))
    return img

# ---------- B: knapping and butchery ----------
L_FLAKE = text_img('石片：边缘像刀一样锋利', FB, 40, (255, 225, 160), 3)
L_LOM = text_img('洛迈奎 · 已知最早的石器', FB, 42, (255, 225, 160), 3)
L_OLD = text_img('奥杜威石器', FB, 46, (255, 225, 160), 3)
L_CUT = text_img('石片割肉 · 石锤砸骨', FB, 42, (255, 235, 200), 3)
L_RICH = text_img('骨髓：又肥又有营养', FB, 42, (255, 220, 140), 3)
def stone_poly(cx, cy, r, sd, flat=0.0):
    return [(cx + r * (1 + 0.15 * math.sin(3 * a + sd)) * math.cos(a), cy + r * (1 + 0.15 * math.sin(3 * a + sd)) * (0.7 - 0.3 * flat) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24)]
def knap(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 31.8:
        core = (560, 1080)
        dr.polygon(stone_poly(*core, 170, 0.4), fill=STONE, outline=(200, 195, 185))
        hit = 0
        for th in (24.4, 26.2, 28.0):
            if th - 1.0 < t < th: hit = ss(th - 1.0, th, t)
        ang = lerp(-0.9, 0.0, hit)
        hx, hy = 560 + 260 * math.cos(ang - 0.6), 1080 - 160 - 260 * math.sin(-ang + 0.6) * 0.6
        dr.polygon(stone_poly(hx, hy - 90, 90, 1.7), fill=(170, 160, 150), outline=(210, 200, 190))
        for th in (24.4, 26.2, 28.0):
            f = ss(th, th + 0.1, t) * (1 - ss(th + 0.3, th + 0.8, t))
            if f > 0:
                for j in range(8):
                    a = j * math.pi / 4; dr.line((680, 990, 680 + 70 * f * math.cos(a), 990 + 70 * f * math.sin(a)), fill=mul((255, 240, 200), f), width=4)
        fk = ss(28.0, 29.4, t)
        if fk > 0:
            fx, fy = lerp(700, 820, fk), lerp(990, 1280, fk)
            pts = [(fx - 70, fy - 20), (fx + 60, fy - 40), (fx + 80, fy + 10), (fx - 50, fy + 30)]
            dr.polygon(pts, fill=(185, 178, 168))
            if t > 29.0:
                g = 0.6 + 0.4 * math.sin(t * 5)
                dr.line((fx - 70, fy - 20, fx + 60, fy - 40), fill=mul((255, 230, 140), g), width=5)
        put(img, L_FLAKE, 540, 640, ss(28.4, 29.2, t))
        return img
    if t < 40.2:
        for i in range(5):
            cx = 160 + i * 190; cy = 1050 + (i % 2) * 70
            dr.polygon(stone_poly(cx, cy, 70 - (i % 3) * 10, i * 1.3, flat=0.4), fill=(160 - i * 6, 150 - i * 5, 140), outline=(210, 205, 195))
            for j in range(3): dr.line((cx - 40 + j * 25, cy - 20, cx - 30 + j * 25, cy + 10), fill=(120, 115, 108), width=3)
        put(img, L_LOM if t < 36.0 else L_OLD, 540, 640, ss(32.0, 32.8, t) * (1 - ss(35.6, 36.0, t)) if t < 36.0 else ss(36.2, 37.0, t))
        return img
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img); savanna(dr)
    dr.line((200, 1060, 880, 1060), fill=(235, 225, 205), width=48)
    for x in (200, 880): dr.ellipse((x - 46, 1020, x + 46, 1100), fill=(235, 225, 205))
    mk = ss(40.6, 43.0, t)
    dr.rounded_rectangle((300, 1000 + 20 * mk, 560, 1050), radius=14, fill=(160, 60, 55))
    fx = lerp(560, 300, mk); dr.polygon([(fx - 50, 990), (fx + 40, 975), (fx + 55, 1000), (fx - 40, 1010)], fill=(190, 182, 172))
    bk = ss(42.6, 43.4, t)
    hy = 900 - 60 * abs(math.sin(t * 5)) if t < 43.4 else 900
    dr.polygon(stone_poly(720, hy, 60, 2.0), fill=STONE)
    if bk > 0:
        dr.line((690, 1040, 710, 1075, 700, 1100), fill=(90, 70, 60), width=4)
        dr.ellipse((700, 1045, 760, 1080), fill=mul((245, 200, 90), bk))
    put(img, L_CUT, 540, 640, ss(40.6, 41.4, t) * (1 - ss(44.2, 44.6, t)))
    put(img, L_RICH, 540, 640, ss(44.6, 45.4, t))
    return img

# ---------- C: brain energy ----------
L_W = text_img('占体重：约 2%', FB, 40, (230, 230, 240), 3); L_E2 = text_img('用掉能量：约 20%', FB, 40, (255, 210, 140), 3)
L_FEED = text_img('吃得越好，才养得起越大的脑', FB, 40, (255, 225, 160), 3)
def energy(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    cx = 300
    dr.ellipse((cx - 60, 640, cx + 60, 770), fill=(200, 160, 135))
    dr.rounded_rectangle((cx - 110, 780, cx + 110, 1150), radius=40, fill=(200, 160, 135))
    for sg in (-1, 1): dr.line((cx + sg * 60, 1150, cx + sg * 70, 1500), fill=(200, 160, 135), width=60)
    g = 0.7 + 0.3 * math.sin(t * 4)
    dr.ellipse((cx - 44, 652, cx + 44, 716), fill=mul((255, 170, 170), g))
    for i, (v, lab, c, t0) in enumerate(((0.02, L_W, (200, 200, 210), 49.0), (0.2, L_E2, (250, 190, 90), 53.2))):
        k = ss(t0, t0 + 1.2, t)
        y = 800 + i * 220
        dr.rounded_rectangle((520, y, 1000, y + 60), radius=20, fill=(40, 44, 54))
        dr.rounded_rectangle((520, y, 520 + max(24, 480 * v * 4 * k), y + 60), radius=20, fill=c)
        put(img, lab, 760, y + 110, ss(t0, t0 + 0.8, t))
    put(img, L_FEED, 540, 1320, ss(57.4, 58.2, t))
    return img

# ---------- D: skill & learning ----------
L_SKILL = text_img('挑石头 · 找角度 · 精确用力', FB, 40, (255, 235, 200), 3)
L_WATCH = text_img('看别人做，一次次练习', FB, 42, (255, 235, 200), 3)
L_BOTH = text_img('脑和手，一起变好', FB, 44, (255, 225, 160), 3)
def skill(t):
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img); savanna(dr)
    if t < 70.0:
        img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.polygon(stone_poly(540, 1100, 160, 0.3), fill=STONE)
        ang = 0.5 + 0.15 * math.sin(t * 2)
        hx, hy = 540 + 220 * math.cos(ang), 1100 - 220 * math.sin(ang) - 120
        dr.polygon(stone_poly(hx, hy, 80, 1.1), fill=(170, 160, 150))
        dr.line((hx + 60, hy + 40, hx + 160, hy + 200), fill=(200, 160, 135), width=50)
        dr.arc((540 + 60, 1100 - 260, 540 + 340, 1100 + 20), 290, 340, fill=(255, 220, 120), width=4)
        put(img, L_SKILL, 540, 640, ss(66.0, 66.8, t))
        return img
    for i, (x, s) in enumerate(((360, 1.4), (720, 0.9))):
        dr.ellipse((x - 70 * s, GROUND - 180 * s, x + 70 * s, GROUND - 20 * s), fill=FUR)
        dr.ellipse((x - 40 * s, GROUND - 250 * s, x + 40 * s, GROUND - 170 * s), fill=FUR)
        dr.ellipse((x - 20 * s + (-12 if i else 12) * s, GROUND - 235 * s, x + 26 * s + (-12 if i else 12) * s, GROUND - 195 * s), fill=(175, 145, 120))
        hit = abs(math.sin(t * 3 + i * 0.8))
        hx = x + 80 * s; hy = GROUND - 60 * s - 70 * s * hit
        dr.line((x + 30 * s, GROUND - 140 * s, hx, hy), fill=FUR, width=int(16 * s))
        dr.polygon(stone_poly(hx, hy, 26 * s, i), fill=STONE)
        dr.polygon(stone_poly(x + 90 * s, GROUND, 40 * s, i + 2), fill=(135, 130, 124))
    put(img, L_WATCH, 540, 640, ss(70.2, 71.0, t) * (1 - ss(74.0, 74.4, t)))
    put(img, L_BOTH, 540, 640, ss(74.4, 75.2, t))
    return img

# ---------- E: genus Homo ----------
L_HOMO = text_img('人属', FB, 60, (255, 225, 160), 4)
L_HAB = text_img('能人 · 脑约 600 毫升', FB, 38, (255, 235, 200), 3)
L_ERE = text_img('直立人 · 和你差不多高', FB, 38, (255, 235, 200), 3)
L_YOUH = text_img('你', FB, 40, (200, 200, 210), 3)
L_AXE = text_img('手斧：两面打制，左右对称', FB, 40, (255, 225, 160), 3)
def homo(t):
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img); savanna(dr)
    if t < 91.2:
        put(img, L_HOMO, 540, 640, ss(78.8, 79.6, t) * (1 - ss(82.6, 83.0, t)))
        a1 = ss(83.0, 83.8, t); a2 = ss(87.2, 88.0, t)
        if a1 > 0: hominin(dr, 260, GROUND + 30, 1.25, 83, walk=0, a=a1, col=(110, 82, 62)); put(img, L_HAB, 250, GROUND + 110, a1)
        if a2 > 0: hominin(dr, 560, GROUND + 30, 1.9, t, walk=0.3, a=a2, col=(120, 88, 66)); put(img, L_ERE, 580, GROUND + 180, a2)
        if a2 > 0:
            x, y, s = 860, GROUND + 30, 1.95
            dr.ellipse((x - 28 * s, y - 290 * s, x + 30 * s, y - 228 * s), outline=(200, 200, 210), width=3)
            dr.rounded_rectangle((x - 34 * s, y - 230 * s, x + 34 * s, y - 105 * s), radius=20, outline=(200, 200, 210), width=3)
            for sg in (-1, 1): dr.line((x + sg * 15 * s, y - 110 * s, x + sg * 18 * s, y), fill=(200, 200, 210), width=3)
            put(img, L_YOUH, x, GROUND + 110, a2)
        return img
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(91.4, 93.4, t)
    pts = [(540 + 160 * math.sin(a) * (0.55 + 0.45 * math.cos(a / 2) ** 2), 1060 - 260 * math.cos(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    dr.polygon(pts, fill=(165, 150, 130), outline=(220, 210, 190))
    for j in range(10):
        if j / 10 < k:
            yy_ = 860 + j * 40; ww = 120 - abs(j - 4) * 18
            for sg in (-1, 1): dr.arc((540 + sg * ww - 40, yy_ - 30, 540 + sg * ww + 40, yy_ + 30), 0, 360, fill=(140, 125, 108), width=3)
    dr.line((540, 780, 540, 1340), fill=mul((255, 225, 160), k * 0.6), width=2)
    put(img, L_AXE, 540, 640, ss(91.6, 92.4, t))
    return img

# ---------- F: the loop ----------
L_N = [text_img(s_, FB, 46, c, 4) for s_, c in (('工具', (220, 220, 230)), ('食物', (255, 190, 150)), ('大脑', (255, 180, 190)))]
L_FAST = text_img('越转越快', FB, 50, (255, 225, 160), 4)
def loop(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    cx, cy, R = 540, 1020, 300
    nodes = [(cx + R * math.cos(a), cy + R * math.sin(a)) for a in (-math.pi / 2, math.pi / 6, math.pi * 5 / 6)]
    sp = 0.6 + 3.0 * ss(108.4, 111.0, t)
    ph = (t - 95.6) * sp
    for i in range(3):
        k = ss(95.8 + i * 4.2, 96.8 + i * 4.2, t)
        a0 = -math.pi / 2 + i * 2 * math.pi / 3 + 0.35; a1 = a0 + 2 * math.pi / 3 - 0.7
        if k > 0:
            dr.arc((cx - R, cy - R, cx + R, cy + R), math.degrees(a0), math.degrees(a0 + (a1 - a0) * k), fill=(255, 210, 130), width=8)
            if k > 0.95:
                ex, ey = cx + R * math.cos(a1), cy + R * math.sin(a1)
                dr.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=(255, 210, 130))
    if t > 104.0:
        for j in range(3):
            a = ph + j * 2 * math.pi / 3
            dr.ellipse((cx + R * math.cos(a) - 12, cy + R * math.sin(a) - 12, cx + R * math.cos(a) + 12, cy + R * math.sin(a) + 12), fill=(255, 245, 220))
    for i, (x, y) in enumerate(nodes):
        dr.ellipse((x - 90, y - 60, x + 90, y + 60), fill=(36, 40, 52), outline=(200, 200, 210), width=3)
        put(img, L_N[i], x, y, 1.0)
    put(img, L_FAST, 540, 640, ss(108.6, 109.4, t))
    return img

# ---------- G: night, wildfire ----------
L_HARD = text_img('生肉、硬根茎：嚼起来很费劲', FB, 40, (255, 235, 200), 3)
L_FIRE = text_img('一团野火', FB, 46, (255, 200, 120), 3)
NIGHT = grad((14, 18, 36), (50, 46, 60), 480, 1100)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
GLOW = (np.exp(-(((_xx - 820) / 380) ** 2 + ((_yy - (GROUND - 60)) / 260) ** 2)) * 140)[..., None] * np.array([1.0, 0.5, 0.15])
def wildfire(t):
    fk = ss(117.0, 119.0, t)
    img = Image.fromarray(NIGHT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(60):
        x = (i * 173) % W; y = 500 + (i * 97) % 500
        dr.point((x, y), fill=(200, 200, 220))
    dr.rectangle((0, GROUND, W, H), fill=(60, 52, 40))
    if fk > 0:
        arr = np.asarray(img, np.float32) + GLOW * fk * (0.85 + 0.15 * math.sin(t * 9))
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
        for j in range(9):
            h = (80 + 50 * math.sin(t * 7 + j * 1.3)) * fk
            x = 700 + j * 30
            dr.polygon([(x - 22, GROUND), (x, GROUND - h - 40), (x + 22, GROUND)], fill=(255, 150 + 10 * (j % 3), 50))
    if t < 116.8:
        dr.ellipse((380, GROUND - 10, 560, GROUND + 40), fill=(150, 60, 55))
        for j in range(4): dr.line((600 + j * 30, GROUND + 10, 620 + j * 30, GROUND + 60), fill=(150, 120, 80), width=10)
        hominin(dr, 300, GROUND + 30, 1.4, t, walk=0, col=(90, 70, 55))
        put(img, L_HARD, 540, 640, ss(112.8, 113.6, t))
    else:
        x = lerp(200, 520, ss(117.4, 121.0, t))
        hominin(dr, x, GROUND + 30, 1.5, t if t < 121 else 121, col=tuple(int(v) for v in lerp(np.array([70, 55, 45]), np.array([150, 105, 75]), fk)))
        put(img, L_FIRE, 820, GROUND - 260, ss(117.4, 118.2, t))
    return img

def render(t):
    if t < 6.0: return render20(132.5 + t)
    if t < 23.2: return dim(scav(t), ss(6.0, 6.6, t) * (1 - ss(22.6, 23.2, t)))
    if t < 48.8:
        k = ss(23.2, 23.8, t) * (1 - ss(48.2, 48.8, t))
        for a in (31.4, 39.8):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(knap(t), k)
    if t < 61.6: return dim(energy(t), ss(48.8, 49.4, t) * (1 - ss(61.0, 61.6, t)))
    if t < 78.6:
        k = ss(61.6, 62.2, t) * (1 - ss(78.0, 78.6, t))
        if 69.6 < t < 70.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 69.6) / 0.8)
        return dim(skill(t), k)
    if t < 95.6:
        k = ss(78.6, 79.2, t) * (1 - ss(95.0, 95.6, t))
        if 90.8 < t < 91.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 90.8) / 0.8)
        return dim(homo(t), k)
    if t < 112.6: return dim(loop(t), ss(95.6, 96.2, t) * (1 - ss(112.0, 112.6, t)))
    return dim(wildfire(t), ss(112.6, 113.2, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep21_{ts}.png')
