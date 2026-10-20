import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep17 import tree
from ep19 import ape_walk, FUR, render as render19

CLEAN = False
rng = np.random.default_rng(201)
SAV_SKY = grad((150, 190, 215), (245, 225, 175), 480, 1100)
GRASS = (195, 170, 105)

def hominin(dr, x, y, s, t, a=1.0, walk=1.0, col=FUR, carry=False, face=1):
    ph = math.sin(t * 5) * walk
    hip = (x, y - 120 * s)
    for i, sg in enumerate((1, -1)):
        p = ph * sg
        knee = (x + face * 18 * s * p, y - 60 * s)
        foot = (x + face * 34 * s * p, y)
        c = mul(col, a * (0.85 if i else 1.0))
        dr.line((hip, knee), fill=c, width=int(18 * s)); dr.line((knee, foot), fill=c, width=int(15 * s))
        dr.line((foot[0], foot[1], foot[0] + face * 20 * s, foot[1]), fill=c, width=int(9 * s))
    dr.ellipse((x - 34 * s, y - 230 * s, x + 34 * s, y - 105 * s), fill=mul(col, a))
    dr.ellipse((x - 28 * s, y - 290 * s, x + 30 * s, y - 228 * s), fill=mul(col, a))
    dr.ellipse((x + face * 2 * s - 18 * s, y - 278 * s, x + face * 2 * s + 22 * s, y - 245 * s), fill=mul((175, 145, 120), a))
    for sg in (1, -1):
        p = -ph * sg
        if carry and sg == 1:
            dr.line((x, y - 200 * s, x + face * 40 * s, y - 150 * s), fill=mul(col, a), width=int(12 * s))
            dr.ellipse((x + face * 20 * s - 26 * s, y - 185 * s, x + face * 20 * s + 26 * s, y - 135 * s), fill=mul((120, 92, 70), a))
        else:
            dr.line((x, y - 200 * s, x + face * 22 * s * p, y - 110 * s), fill=mul(col, a), width=int(12 * s))
def savanna(dr, k=1.0):
    gc = tuple(int(v) for v in lerp(np.array([110, 125, 75]), np.array(GRASS), k))
    dr.rectangle((0, GROUND, W, H), fill=gc)
    for i in range(60):
        x = (i * 23) % W; h = 18 + (i % 5) * 6
        dr.line((x, GROUND, x + 5, GROUND - h * k), fill=(165, 145, 85), width=3)

# ---------- B: rift valley ----------
L_WHY = text_img('森林为什么会变少？', FB, 46, (255, 225, 160), 4)
L_PUSH = text_img('地下的热量把地壳往上顶', FB, 40, (255, 210, 170), 3)
L_RIFT = text_img('东非大裂谷', FB, 50, (255, 225, 160), 4)
L_WEST = text_img('湿气被高地挡住', FM, 36, (210, 230, 255), 3); L_EAST = text_img('这边越来越干', FB, 40, (255, 215, 160), 3)
L_PATCH = text_img('森林碎成一块一块', FB, 42, (210, 240, 200), 3)
def rift(t):
    img = Image.fromarray(grad((120, 165, 200), (215, 220, 210), 480, 1000).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 27.4:
        up = ss(15.0, 19.0, t); sp = ss(19.2, 22.4, t)
        base = 1060
        def surf(x):
            b = -150 * up * math.exp(-((x - 540) / 300) ** 2)
            if abs(x - 540) < 90 * sp: b += 140 * sp * (1 - (abs(x - 540) / (90 * sp + 1e-6)) ** 2)
            return base + b
        pts = [(x, surf(x)) for x in range(0, W + 20, 20)]
        dr.polygon(pts + [(W, 1250), (0, 1250)], fill=(150, 120, 85))
        dr.rectangle((0, 1250, W, 1560), fill=(200, 90, 50))
        for y in range(1250, 1560, 8):
            q = (y - 1250) / 310; dr.line((0, y, W, y), fill=(int(200 + 40 * q), int(90 + 20 * q), 50), width=8)
        if t > 14.8:
            for i in range(5):
                q = (t * 0.5 + i / 5) % 1
                x = 420 + i * 60; y = lerp(1540, 1270, q)
                dr.line((x, y, x, y - 40), fill=(255, 220, 140), width=6); dr.polygon([(x - 12, y - 40), (x + 12, y - 40), (x, y - 62)], fill=(255, 220, 140))
        greenL = 1 - 0.0 * ss(23.4, 27, t); dryR = ss(23.6, 27.0, t)
        for x in range(30, W, 70):
            y = surf(x)
            if x < 380: dr.ellipse((x - 26, y - 50, x + 26, y), fill=(60, 120, 60))
            elif x > 700:
                c = tuple(int(v) for v in lerp(np.array([60, 120, 60]), np.array([180, 160, 95]), dryR))
                dr.ellipse((x - 26, y - 50 + 30 * dryR, x + 26, y), fill=c)
        if t > 23.2:
            for i in range(3):
                q = (t * 0.25 + i / 3) % 1
                cx = lerp(-80, 330, q); cy = 760 + i * 40
                for dx, r in ((-40, 34), (0, 44), (40, 34)): dr.ellipse((cx + dx - r, cy - r, cx + dx + r, cy + r), fill=(240, 245, 250))
                for j in range(4): dr.line((cx - 30 + j * 20, cy + 40, cx - 36 + j * 20, cy + 90), fill=(170, 210, 250), width=3)
            put(img, L_WEST, 230, 660, ss(23.6, 24.4, t)); put(img, L_EAST, 850, 860, ss(24.4, 25.2, t))
        put(img, L_WHY, 540, 640, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
        put(img, L_PUSH, 540, 640, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
        put(img, L_RIFT, 540, 640, ss(19.2, 20.0, t) * (1 - ss(23.0, 23.4, t)))
        return img
    img = Image.fromarray(np.full((H, W, 3), GRASS, np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(27.6, 31.0, t)
    for i in range(14):
        cx = (i * 211) % 980 + 50; cy = 600 + (i * 157) % 800
        r = lerp(160, 70 + 20 * (i % 3), k)
        dr.ellipse((cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), fill=(70, 120, 65))
    put(img, L_PATCH, 540, 560, ss(27.8, 28.6, t))
    return img

# ---------- C: walking ----------
L_OPEN = text_img('走过开阔地，去另一片树林', FB, 40, (255, 235, 200), 3)
L_E = text_img('走长路消耗的能量', FM, 34, (240, 240, 240), 3)
L_Q = text_img('四肢着地', FB, 36, (240, 230, 210), 3); L_B2 = text_img('两腿直立', FB, 36, (255, 225, 160), 3)
L_HANDS = text_img('手空出来：抱孩子、拿食物', FB, 40, (255, 235, 200), 3)
L_SEE = text_img('看得远 · 正午晒得少', FB, 42, (255, 235, 200), 3)
def walking(t):
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((800, 540, 920, 660), fill=(255, 245, 210))
    savanna(dr)
    for x, s in ((60, 1.0), (1010, 1.0)): tree(dr, x, GROUND, 480)
    if t < 36.0:
        ape_walk(dr, lerp(150, 700, ss(32.0, 35.8, t)), GROUND + 20, 0.9, t)
        put(img, L_OPEN, 540, 1320, ss(32.0, 32.8, t))
        return img
    if t < 44.4:
        if t < 40.2: ape_walk(dr, lerp(200, 760, ss(36.2, 40.0, t)), GROUND + 20, 0.9, t)
        else: hominin(dr, lerp(200, 760, ss(40.4, 44.0, t)), GROUND + 20, 1.2, t)
        dr.rounded_rectangle((90, 1270, 990, 1500), radius=20, fill=(20, 24, 30))
        put(img, L_E, 540, 1305, 1.0)
        put(img, L_Q, 200, 1380, 1.0); put(img, L_B2, 200, 1450, ss(40.4, 41.0, t))
        dr.rounded_rectangle((300, 1365, 300 + 600 * ss(36.4, 38.0, t), 1395), radius=14, fill=(230, 120, 90))
        dr.rounded_rectangle((300, 1435, 300 + 150 * ss(40.6, 42.0, t), 1465), radius=14, fill=(250, 200, 100))
        return img
    if t < 48.6:
        hominin(dr, 540, GROUND + 20, 1.5, t, carry=True)
        for i in range(3): dr.ellipse((600 + i * 26, GROUND - 230, 624 + i * 26, GROUND - 206), fill=(220, 120, 60))
        put(img, L_HANDS, 540, 1320, ss(44.6, 45.4, t))
        return img
    hominin(dr, 400, GROUND + 20, 1.5, t, walk=0.2)
    ey = GROUND + 20 - 260 * 1.5
    dr.line((430, ey, 1000, ey + 40), fill=(255, 235, 160), width=3)
    for i in range(5):
        x = 330 + i * 35
        dr.line((x, 480, x + 5, ey - 30), fill=(255, 230, 150), width=2)
    put(img, L_SEE, 540, 1320, ss(48.8, 49.6, t))
    return img

# ---------- D: skeleton changes ----------
L_SK = [text_img(s_, FB, 38, (255, 225, 160), 3) for s_ in ('头骨下的大孔：移到正下方', '脊柱弯成 S 形：像弹簧', '骨盆：又短又宽，像一只碗', '足弓 · 大脚趾并拢')]
L_APE = text_img('黑猩猩', FM, 34, (230, 230, 235), 3); L_HUM = text_img('人', FM, 34, (255, 225, 160), 3)
BONE = (230, 222, 205)
def skel(t):
    img = Image.fromarray(grad((26, 30, 40), (14, 16, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    stage = 0 if t < 61.4 else 1 if t < 65.6 else 2 if t < 69.8 else 3
    hl = lambda i: ss([57.4, 61.6, 65.8, 70.0][i], [58.2, 62.4, 66.6, 70.8][i], t) * (0.6 + 0.4 * math.sin(t * 4)) if i == stage else 0
    def hc(i):
        k = min(1.0, hl(i)); return tuple(int(a + (b - a) * k) for a, b in zip(BONE, (255, 200, 90)))
    # ape: hunched, skull hole at back
    ax, ay = 280, 1300
    dr.ellipse((ax + 60, ay - 520, ax + 190, ay - 420), outline=BONE, width=6)
    dr.ellipse((ax + 70, ay - 440, ax + 92, ay - 418), outline=mul((255, 210, 120), max(hl(0), 0.3)), width=5)
    pts = [(ax + 80, ay - 430), (ax + 20, ay - 380), (ax - 20, ay - 300), (ax - 30, ay - 220)]
    dr.line(pts, fill=hc(1), width=10)
    dr.polygon([(ax - 80, ay - 250), (ax + 20, ay - 250), (ax + 10, ay - 160), (ax - 70, ay - 140)], outline=hc(2), width=5)
    dr.line((ax - 30, ay - 160, ax - 10, ay - 80, ax - 40, ay), fill=BONE, width=9)
    dr.line((ax - 70, ay, ax + 10, ay), fill=hc(3), width=8)
    dr.line((ax - 70, ay, ax - 95, ay - 20), fill=BONE, width=6)
    dr.line((ax + 30, ay - 370, ax + 90, ay - 120, ax + 100, ay), fill=BONE, width=8)
    put(img, L_APE, ax, ay + 60, 1.0)
    # human: upright
    hx, hy = 780, 1300
    dr.ellipse((hx - 65, hy - 640, hx + 65, hy - 510), outline=BONE, width=6)
    dr.ellipse((hx - 11, hy - 525, hx + 11, hy - 503), outline=mul((255, 210, 120), max(hl(0), 0.3)), width=5)
    sp = [(hx + 0, hy - 505), (hx - 14, hy - 450), (hx + 6, hy - 380), (hx - 10, hy - 310), (hx + 2, hy - 260)]
    dr.line(sp, fill=hc(1), width=10)
    dr.chord((hx - 80, hy - 300, hx + 80, hy - 190), 0, 180, outline=hc(2), width=6)
    for sg in (-1, 1):
        dr.line((hx + sg * 40, hy - 240, hx + sg * 22, hy - 120, hx + sg * 28, hy), fill=BONE, width=9)
        dr.line((hx + sg * 50, hy - 460, hx + sg * 70, hy - 230), fill=BONE, width=8)
    dr.arc((hx - 10, hy - 22, hx + 70, hy + 22), 180, 360, fill=hc(3), width=7)
    dr.line((hx - 10, hy, hx + 70, hy), fill=BONE, width=4)
    put(img, L_HUM, hx, hy + 60, 1.0)
    for i in range(4):
        put(img, L_SK[i], 540, 600, ss([57.4, 61.6, 65.8, 70.0][i], [58.2, 62.4, 66.6, 70.8][i], t) * (1 - ss([61.0, 65.2, 69.4, 73.6][i], [61.4, 65.6, 69.8, 74.2][i], t)))
    return img

# ---------- E: fossils & footprints ----------
L_SAH = text_img('乍得沙赫人 · 可能已开始直立', FB, 40, (255, 225, 160), 3)
L_ARDI = text_img('地猿 · 还能爬树', FB, 42, (255, 225, 160), 3)
L_LUCY = text_img('露西 · 南方古猿', FB, 44, (255, 225, 160), 3)
L_PRINT = text_img('莱托里脚印 · 坦桑尼亚', FB, 42, (255, 225, 160), 3)
def footprint(dr, x, y, s, a, left):
    sg = -1 if left else 1
    dr.ellipse((x - 18 * s, y - 50 * s, x + 18 * s, y + 30 * s), fill=mul((95, 90, 88), a))
    for j in range(5):
        r = (9 - j) * s * 0.9
        dr.ellipse((x - 16 * s + j * 8 * s - r, y - 62 * s - (j == 0) * 4 * s - r, x - 16 * s + j * 8 * s + r, y - 62 * s + r), fill=mul((95, 90, 88), a))
def fossil(t):
    if t < 82.6:
        img = Image.fromarray(grad((40, 40, 46), (22, 22, 26)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        if t < 78.4:
            dr.ellipse((360, 820, 720, 1100), fill=(150, 130, 100), outline=(200, 180, 150), width=4)
            dr.ellipse((560, 880, 640, 950), fill=(40, 35, 30)); dr.ellipse((440, 880, 520, 950), fill=(40, 35, 30))
            dr.rectangle((470, 1000, 610, 1080), fill=(130, 110, 85))
            put(img, L_SAH, 540, 640, ss(74.4, 75.2, t))
        else:
            img = Image.fromarray(grad((120, 170, 140), (60, 100, 70), 480, 1300).astype(np.uint8)); dr = ImageDraw.Draw(img)
            dr.line((700, 1500, 700, 600), fill=(90, 70, 50), width=40); dr.line((700, 860, 420, 800), fill=(90, 70, 50), width=18)
            hominin(dr, 560, 1100, 1.2, t, walk=0.0)
            dr.line((560, 1100 - 200 * 1.2, 520, 830), fill=FUR, width=14)
            put(img, L_ARDI, 540, 640, ss(78.6, 79.4, t))
        return img
    if t < 86.8:
        img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
        savanna(dr)
        hominin(dr, lerp(300, 620, ss(82.8, 86.4, t)), GROUND + 20, 1.6, t, col=(120, 90, 65))
        put(img, L_LUCY, 540, 640, ss(83.0, 83.8, t))
        return img
    img = Image.fromarray(grad((150, 145, 140), (110, 105, 100), 480, 1500).astype(np.uint8)); dr = ImageDraw.Draw(img)
    n = int(ss(87.2, 92.0, t) * 10)
    for i in range(n):
        x = 360 + (i % 2) * 80 + 14 * i; y = 1500 - i * 90
        footprint(dr, x, y, 1.1, 1.0, i % 2 == 0)
    put(img, L_PRINT, 540, 640, ss(87.2, 88.0, t))
    return img

# ---------- F: brain sizes ----------
L_BS = text_img('大脑容量', FB, 40, (240, 240, 240), 3)
L_BN = [text_img(s_, FB, 36, c, 3) for s_, c in (('黑猩猩 约 400 毫升', (230, 230, 235)), ('露西 约 450 毫升', (255, 225, 160)), ('你 约 1350 毫升', (150, 150, 160)))]
L_LEGS = text_img('先是腿，后是脑', FB, 50, (255, 225, 160), 4)
def brains(t):
    img = Image.fromarray(grad((30, 30, 40), (16, 16, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_BS, 540, 600, 1.0)
    for i, (v, c) in enumerate(((400, (200, 200, 210)), (450, (250, 200, 110)), (1350, (90, 90, 100)))):
        y = 820 + i * 170
        dr.rounded_rectangle((120, y, 120 + 0.6 * v * ss(95.6 + i * 0.5, 96.6 + i * 0.5, t), y + 60), radius=20, fill=c)
        put(img, L_BN[i], 540, y + 110, ss(96.0 + i * 0.5, 96.8 + i * 0.5, t))
    put(img, L_LEGS, 540, 1420, ss(99.8, 100.6, t))
    return img

# ---------- G: the cost ----------
L_BACK = text_img('腰酸背痛', FB, 40, (255, 170, 150), 3); L_KNEE = text_img('膝盖磨损', FB, 40, (255, 170, 150), 3)
L_BIRTH = text_img('骨盆变窄：生孩子更难', FB, 42, (255, 200, 170), 3)
def cost(t):
    img = Image.fromarray(grad((30, 30, 40), (16, 16, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 108.0:
        cx = 540
        dr.ellipse((cx - 55, 560, cx + 55, 680), fill=(200, 160, 135))
        dr.rounded_rectangle((cx - 110, 690, cx + 110, 1060), radius=40, fill=(200, 160, 135))
        for sg in (-1, 1):
            dr.line((cx + sg * 60, 1060, cx + sg * 70, 1440), fill=(200, 160, 135), width=60)
            dr.line((cx + sg * 110, 720, cx + sg * 150, 1020), fill=(200, 160, 135), width=40)
        p = 0.6 + 0.4 * math.sin(t * 5)
        bk = ss(104.2, 105.0, t)
        dr.ellipse((cx - 50, 940, cx + 50, 1020), outline=mul((255, 80, 60), bk * p), width=8)
        kk = ss(105.4, 106.2, t)
        for sg in (-1, 1): dr.ellipse((cx + sg * 65 - 40, 1230, cx + sg * 65 + 40, 1290), outline=mul((255, 80, 60), kk * p), width=8)
        put(img, L_BACK, 830, 980, bk); put(img, L_KNEE, 830, 1260, kk)
        return img
    k = ss(108.4, 110.4, t)
    dr.chord((340, 820, 740, 1180), 0, 180, outline=BONE, width=10)
    w = lerp(170, 125, k)
    dr.ellipse((540 - w, 900, 540 + w, 1060), outline=(255, 210, 120), width=4)
    dr.ellipse((540 - 105, 880, 540 + 105, 1080), outline=(255, 160, 150), width=4)
    put(img, L_BIRTH, 540, 640, ss(108.4, 109.2, t))
    return img

# ---------- H: stones ----------
L_STONE = text_img('空出的双手：摆弄身边的石头', FB, 40, (255, 225, 160), 3)
def stones(t):
    img = Image.fromarray(SAV_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    savanna(dr); tree(dr, 980, GROUND, 460)
    x, y = 520, GROUND + 30
    dr.ellipse((x - 70, y - 200, x + 70, y - 40), fill=FUR)
    dr.ellipse((x - 40, y - 270, x + 40, y - 190), fill=FUR); dr.ellipse((x - 20, y - 255, x + 26, y - 215), fill=(175, 145, 120))
    for sg in (-1, 1): dr.ellipse((x + sg * 50 - 40, y - 60, x + sg * 50 + 40, y + 10), fill=FUR)
    hit = abs(math.sin(t * 3)) if t > 116.8 else 0.5
    hx, hy = x + 120, y - 60 - 80 * hit
    dr.line((x + 40, y - 150, hx, hy), fill=FUR, width=18)
    dr.polygon([(hx - 30, hy - 10), (hx + 20, hy - 30), (hx + 36, hy + 10), (hx - 10, hy + 26)], fill=(150, 145, 140))
    dr.line((x - 40, y - 150, x + 100, y - 20), fill=FUR, width=18)
    dr.polygon([(x + 70, y - 30), (x + 150, y - 40), (x + 160, y + 10), (x + 80, y + 14)], fill=(130, 125, 120))
    for i in range(6): dr.ellipse((200 + i * 40, y + 20 + (i % 2) * 12, 230 + i * 40, y + 44 + (i % 2) * 12), fill=(140, 135, 128))
    if t > 117.0 and hit < 0.15:
        for j in range(5):
            ang = -math.pi / 2 + (j - 2) * 0.5; dr.line((x + 120, y - 40, x + 120 + 50 * math.cos(ang), y - 40 + 50 * math.sin(ang)), fill=(255, 240, 200), width=3)
    put(img, L_STONE, 540, 640, ss(112.6, 113.4, t))
    return img

def render(t):
    if t < 6.0: return render19(133.1 + t)
    if t < 10.6: return dim(render19(133.1 + t), 1 - ss(10.0, 10.6, t))
    if t < 31.8:
        k = ss(10.6, 11.2, t) * (1 - ss(31.2, 31.8, t))
        if 27.0 < t < 27.8: k *= 1 - 0.85 * math.sin(math.pi * (t - 27.0) / 0.8)
        return dim(rift(t), k)
    if t < 53.0: return dim(walking(t), ss(31.8, 32.4, t) * (1 - ss(52.4, 53.0, t)))
    if t < 74.2: return dim(skel(t), ss(53.0, 53.6, t) * (1 - ss(73.6, 74.2, t)))
    if t < 95.4:
        k = ss(74.2, 74.8, t) * (1 - ss(94.8, 95.4, t))
        for a in (78.0, 82.2, 86.4):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(fossil(t), k)
    if t < 103.8: return dim(brains(t), ss(95.4, 96.0, t) * (1 - ss(103.2, 103.8, t)))
    if t < 112.4:
        k = ss(103.8, 104.4, t) * (1 - ss(111.8, 112.4, t))
        if 107.6 < t < 108.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 107.6) / 0.8)
        return dim(cost(t), k)
    return dim(stones(t), ss(112.4, 113.0, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep20_{ts}.png')
