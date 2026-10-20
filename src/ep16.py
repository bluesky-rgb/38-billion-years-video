import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim, cynodont, render as render15

CLEAN = False
rng = np.random.default_rng(161)
GROUND = 1180
DAY_SKY = grad((205, 160, 110), (245, 215, 170), 480, 1100)
NIGHT_SKY = grad((10, 14, 34), (34, 40, 70), 480, 1100)
STARS = [(rng.random() * W, 480 + rng.random() * 620, rng.random()) for _ in range(90)]

def land(dr, night=0.0):
    c1 = tuple(int(v) for v in lerp(np.array([190, 145, 100]), np.array([45, 45, 60]), night))
    c2 = tuple(int(v) for v in lerp(np.array([110, 130, 80]), np.array([30, 45, 40]), night))
    dr.polygon([(0, GROUND - 40), (500, GROUND - 10), (W, GROUND - 50), (W, H), (0, H)], fill=c1)
    for x in (80, 990):
        for j in range(5):
            dr.line((x, GROUND - 30, x + (j - 2) * 30, GROUND - 120 + abs(j - 2) * 20), fill=c2, width=6)
    for x, h in ((170, 330), (930, 380)):
        dr.line((x, GROUND - 30, x, GROUND - 30 - h), fill=c2, width=12)
        for j in range(6):
            y = GROUND - 30 - h + 40 + j * 45; w = 30 + j * 18
            dr.polygon([(x, y - 30), (x - w, y + 20), (x + w, y + 20)], fill=c2)
def sky(t, night):
    img = Image.fromarray((DAY_SKY * (1 - night) + NIGHT_SKY * night).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if night > 0.05:
        for x, y, b in STARS:
            v = night * (0.5 + 0.5 * math.sin(t * 2 + b * 9))
            dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=mul((230, 230, 255), v))
        dr.ellipse((820, 560, 920, 660), fill=mul((240, 240, 220), night))
        dr.ellipse((845, 550, 945, 650), fill=tuple(int(v) for v in NIGHT_SKY[600, 900] * night + DAY_SKY[600, 900] * (1 - night)))
    else:
        dr.ellipse((800, 560, 920, 680), fill=(255, 245, 210))
    return img, dr

def dino(dr, x, y, s, t, a=1.0, face=1, col=(120, 140, 90), run=1.0):
    ph = math.sin(t * 7) * run
    hip = (x, y - 150 * s)
    for i, sg in enumerate((1, -1)):
        p = ph * sg
        knee = (x + face * (25 + 30 * p) * s, y - 80 * s)
        foot = (x + face * (5 + 45 * p) * s, y)
        c = mul(col, a * (0.85 if i else 1.0))
        dr.line((hip, knee), fill=c, width=int(26 * s)); dr.line((knee, foot), fill=c, width=int(18 * s))
        dr.line((foot[0], foot[1], foot[0] + face * 30 * s, foot[1]), fill=c, width=int(10 * s))
    dr.polygon([(x - face * 60 * s, y - 175 * s), (x - face * 300 * s, y - 150 * s), (x - face * 60 * s, y - 130 * s)], fill=mul(col, a))
    dr.ellipse((x - 90 * s, y - 200 * s, x + 90 * s, y - 115 * s), fill=mul(col, a))
    nx, ny = x + face * 120 * s, y - 260 * s
    dr.line((x + face * 60 * s, y - 175 * s, nx, ny), fill=mul(col, a), width=int(34 * s))
    dr.ellipse((nx - 45 * s, ny - 28 * s, nx + 45 * s, ny + 28 * s), fill=mul(col, a))
    dr.polygon([(nx + face * 20 * s, ny - 18 * s), (nx + face * 85 * s, ny + 4 * s), (nx + face * 20 * s, ny + 22 * s)], fill=mul(col, a))
    dr.ellipse((nx + face * 10 * s - 6 * s, ny - 14 * s, nx + face * 10 * s + 6 * s, ny - 2 * s), fill=mul((20, 20, 20), a))
    dr.line((x + face * 70 * s, y - 160 * s, x + face * 100 * s, y - 120 * s), fill=mul(col, a * 0.9), width=int(10 * s))
def sauro(dr, x, y, s, a=1.0, col=(95, 115, 80)):
    if a < 0.02: return
    for lx in (-80, -40, 50, 90):
        dr.line((x + lx * s, y - 110 * s, x + lx * s, y), fill=mul(col, a * 0.9), width=int(30 * s))
    dr.ellipse((x - 140 * s, y - 210 * s, x + 140 * s, y - 80 * s), fill=mul(col, a))
    dr.polygon([(x - 120 * s, y - 170 * s), (x - 330 * s, y - 100 * s), (x - 120 * s, y - 120 * s)], fill=mul(col, a))
    dr.line((x + 110 * s, y - 170 * s, x + 230 * s, y - 360 * s), fill=mul(col, a), width=int(40 * s))
    dr.ellipse((x + 205 * s, y - 385 * s, x + 275 * s, y - 345 * s), fill=mul(col, a))

# ---------- A: Triassic, upright legs, dinosaurs ----------
L_UP = text_img('腿长在身体正下方', FB, 42, (255, 235, 200), 3)
L_SPRAWL = text_img('趴着的腿', FB, 40, (240, 230, 210), 3); L_ERECT = text_img('直立的腿', FB, 40, (255, 225, 160), 3)
L_SPR2 = text_img('身体左右扭，喘不过气', FM, 32, (230, 220, 210), 3); L_ER2 = text_img('边跑边呼吸，省力', FM, 32, (255, 230, 190), 3)
L_BREATH = text_img('呼吸更高效：适合稀薄的空气', FB, 40, (220, 240, 255), 3)
L_DINO = text_img('恐龙', FB, 56, (255, 225, 160), 4); L_DAY = text_img('占满白天的陆地', FB, 42, (255, 235, 200), 3)
def front(dr, cx, cy, upright, a, t):
    dr.ellipse((cx - 90, cy - 70, cx + 90, cy + 70), fill=mul((140, 150, 100), a), outline=mul((80, 90, 60), a), width=3)
    dr.ellipse((cx - 35, cy - 150, cx + 35, cy - 80), fill=mul((140, 150, 100), a))
    for sg in (-1, 1):
        if upright:
            dr.line((cx + sg * 50, cy + 40, cx + sg * 55, cy + 230), fill=mul((120, 130, 85), a), width=26)
        else:
            dr.line((cx + sg * 80, cy + 10, cx + sg * 190, cy + 20), fill=mul((120, 130, 85), a), width=24)
            dr.line((cx + sg * 190, cy + 20, cx + sg * 200, cy + 150), fill=mul((120, 130, 85), a), width=22)
    dr.line((cx - 230, cy + 235, cx + 230, cy + 235), fill=mul((200, 180, 140), a), width=4)
def triassic(t):
    img, dr = sky(t, 0)
    land(dr)
    if t < 14.8:
        dino(dr, lerp(-250, 560, ss(10.6, 14.6, t)), GROUND + 20, 1.3, t, col=(140, 120, 90))
        put(img, L_UP, 540, 640, ss(11.4, 12.2, t) * (1 - ss(14.4, 14.8, t)))
        return img
    if t < 23.2:
        img = Image.fromarray(grad((40, 46, 56), (24, 28, 36)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        a = ss(14.8, 15.4, t)
        front(dr, 290, 960, False, a, t); front(dr, 790, 960, True, a, t)
        put(img, L_SPRAWL, 290, 700, a); put(img, L_ERECT, 790, 700, a)
        put(img, L_SPR2, 290, 1270, ss(15.8, 16.6, t)); put(img, L_ER2, 790, 1270, ss(16.6, 17.4, t))
        if t > 19.0:
            k = 0.5 + 0.5 * math.sin(t * 4)
            for r in (60, 100):
                rr = r + 20 * k
                dr.arc((790 - rr, 820 - rr, 790 + rr, 820 + rr), 200, 340, fill=mul((150, 210, 255), ss(19.2, 20.0, t)), width=4)
            put(img, L_BREATH, 540, 1380, ss(19.4, 20.2, t))
        return img
    k = ss(23.4, 31.0, t)
    sauro(dr, lerp(1350, 760, ss(26.8, 31.0, t)), GROUND + 10, 1.25, a=ss(26.8, 27.6, t))
    dino(dr, lerp(-200, 420, ss(23.4, 27.0, t)), GROUND + 20, 1.5, t, col=(120, 140, 90))
    put(img, L_DINO, 540, 620, ss(23.6, 24.4, t) * (1 - ss(27.2, 27.6, t)))
    put(img, L_DAY, 540, 620, ss(27.8, 28.6, t))
    return img

# ---------- B: shrink & night ----------
L_LOSE = text_img('犬齿兽：争不过', FB, 42, (255, 225, 190), 3); L_SMALLER = text_img('一代代变小', FB, 44, (255, 225, 160), 3)
L_NIGHT = text_img('夜里出来捉虫子', FB, 42, (220, 225, 255), 3)
def bug(dr, x, y, a):
    dr.ellipse((x - 10, y - 5, x + 10, y + 5), fill=mul((60, 50, 40), a))
    dr.ellipse((x - 4, y - 14, x + 10, y - 2), outline=mul((220, 230, 255), a), width=2)
def shrink(t):
    night = ss(39.6, 41.2, t)
    img, dr = sky(t, night)
    land(dr, night)
    for bx in (260, 820):
        dr.ellipse((bx - 70, GROUND + 40, bx + 70, GROUND + 100), fill=(50, 38, 30))
    if t < 36.0:
        dino(dr, 250, GROUND + 20, 1.6, t, run=0.15, face=1)
        cynodont(dr, lerp(720, 860, ss(33.5, 35.5, t)), GROUND + 30, 1.4, t, face=1)
        put(img, L_LOSE, 760, 860, ss(32.2, 33.0, t) * (1 - ss(35.6, 36.0, t)))
    elif t < 40.2:
        for i, s in enumerate((1.6, 1.15, 0.8, 0.55)):
            a = ss(36.2 + i * 0.7, 36.9 + i * 0.7, t)
            if a > 0: cynodont(dr, 170 + i * 250, GROUND + 30, s, 36, a, face=1)
        put(img, L_SMALLER, 540, 860, ss(36.6, 37.4, t) * (1 - ss(39.8, 40.2, t)))
    else:
        x = lerp(820, 560, ss(40.4, 43.4, t))
        cynodont(dr, x, GROUND + 30, 0.6, t, face=-1)
        for i in range(5):
            bx = 300 + i * 70 + 20 * math.sin(t * 3 + i); by = GROUND - 60 - 30 * math.cos(t * 2 + i)
            bug(dr, bx, by, night)
        put(img, L_NIGHT, 540, 860, ss(40.6, 41.4, t))
    return img

# ---------- C: warmth & fur ----------
L_COLD = text_img('夜里冷：身体一冷就动不起来', FB, 40, (190, 220, 255), 3)
L_HEAT = text_img('自己产热 · 体温恒定', FB, 42, (255, 200, 140), 3)
L_FUR = text_img('长出毛：把热量留住', FB, 42, (255, 230, 180), 3); L_RUN = text_img('夜里也能灵活跑动', FB, 42, (255, 235, 200), 3)
L_TH = text_img('体温', FM, 34, (240, 240, 240), 3)
def warm(t):
    img, dr = sky(t, 1.0)
    dr.rectangle((0, GROUND - 40, W, H), fill=(40, 42, 55))
    heat = ss(48.8, 50.6, t); fur = ss(53.0, 55.4, t)
    cx = 520 if t < 57.0 else lerp(520, 1300, ss(57.6, 60.8, t))
    cy = 1020
    if heat > 0:
        for r, c in ((220, 0.25), (160, 0.4), (110, 0.55)):
            dr.ellipse((cx - r * 1.4, cy - r * 0.7, cx + r * 1.4, cy + r * 0.7), fill=mul((255, 120, 60), heat * c * (0.8 + 0.2 * math.sin(t * 3))))
    if fur > 0:
        for i in range(70):
            ang = i / 70 * 2 * math.pi
            px, py = cx + 175 * math.cos(ang), cy + 75 * math.sin(ang)
            ln = 34 * fur
            dr.line((px, py, px + ln * math.cos(ang), py + ln * math.sin(ang)), fill=(150, 120, 90), width=5)
    cynodont(dr, cx, cy, 2.1, t if t > 57 else 44, face=1)
    if t < 57.0:
        for i in range(8):
            q = (t * 0.6 + i / 8) % 1; ang = -math.pi / 2 + (i - 3.5) * 0.35
            r0 = 170; r1 = r0 + 180 * q
            if fur > 0.5 and q > 0.45:
                r1 = r0 + 180 * (0.9 - q)
            px, py = cx + r1 * math.cos(ang) * 1.3, cy + r1 * math.sin(ang) * 0.9
            col = (255, 160, 90) if heat > 0.5 else (150, 190, 255)
            dr.ellipse((px - 8, py - 8, px + 8, py + 8), fill=mul(col, 0.4 + 0.6 * (1 - q)))
    tx, ty = 960, 760
    dr.rounded_rectangle((tx - 22, ty - 200, tx + 22, ty + 140), radius=22, fill=(30, 30, 40), outline=(220, 220, 230), width=3)
    lvl = 0.25 + 0.55 * heat
    wob = 0.08 * math.sin(t * 2) * (1 - heat) - 0.12 * (1 - heat) * ss(44.6, 46, t)
    lv = max(0.05, lvl + wob)
    dr.rounded_rectangle((tx - 12, ty + 130 - 320 * lv, tx + 12, ty + 130), radius=12, fill=(240, 80, 60) if heat > 0.4 else (100, 160, 240))
    put(img, L_TH, tx, ty + 190, 1.0 if t < 57 else 1 - ss(57, 57.6, t))
    put(img, L_COLD, 540, 620, ss(44.8, 45.6, t) * (1 - ss(48.4, 48.8, t)))
    put(img, L_HEAT, 540, 620, ss(49.0, 49.8, t) * (1 - ss(52.6, 53.0, t)))
    put(img, L_FUR, 540, 620, ss(53.2, 54.0, t) * (1 - ss(56.8, 57.2, t)))
    put(img, L_RUN, 540, 620, ss(57.4, 58.2, t))
    return img

# ---------- D: jaw bones to ear ----------
SKX, SKY_ = 470, 950
L_DARK = text_img('夜里看不清：靠耳朵和鼻子', FB, 40, (220, 225, 255), 3)
L_DENT = text_img('下颌主骨', FM, 34, (250, 235, 200), 3); L_ART = text_img('颌关节的两块小骨', FB, 36, (190, 225, 255), 3)
L_STA = text_img('原有的一块耳骨', FM, 34, (255, 230, 140), 3); L_OSS = text_img('三块听小骨：把声音放大', FB, 42, (255, 225, 160), 3)
L_CHAIN = text_img('鳃弓 → 下巴 → 听小骨', FB, 48, (255, 225, 160), 4); L_NEWJ = text_img('新的颌关节', FM, 34, (250, 235, 200), 3)
def skull(t):
    img = Image.fromarray(grad((24, 30, 44), (14, 18, 28)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 65.6:
        img2, dr2 = sky(t, 1.0); land(dr2, 1.0)
        cynodont(dr2, 540, GROUND + 30, 1.0, 61.5, face=-1)
        for r in (40, 80, 120):
            q = (t * 0.8 + r / 120) % 1
            dr2.arc((390 - r - 60 * q, GROUND - 40 - r, 390 + r + 60 * q, GROUND - 40 + r), 120, 240, fill=mul((220, 230, 255), 1 - q), width=3)
        put(img2, L_DARK, 540, 760, ss(61.6, 62.4, t))
        return img2
    k = ss(70.0, 74.0, t)
    # cranium
    dr.polygon([(SKX - 260, SKY_ + 40), (SKX - 230, SKY_ - 110), (SKX - 60, SKY_ - 200), (SKX + 180, SKY_ - 170), (SKX + 330, SKY_ - 60),
                (SKX + 360, SKY_ + 40), (SKX + 120, SKY_ + 30)], fill=(215, 205, 185), outline=(240, 235, 220))
    dr.ellipse((SKX - 120, SKY_ - 130, SKX - 20, SKY_ - 40), fill=(24, 30, 44))
    for i in range(7):
        x = SKX - 240 + i * 30; dr.polygon([(x, SKY_ + 40), (x + 12, SKY_ + 70), (x + 24, SKY_ + 40)], fill=(245, 245, 235))
    jx = lerp(SKX + 230, SKX + 210, k); jy = SKY_ + 70
    # dentary
    back = lerp(SKX + 120, SKX + 215, k)
    dr.polygon([(SKX - 250, SKY_ + 80), (back, SKY_ + 80), (back, SKY_ + 150), (SKX - 230, SKY_ + 150)], fill=(225, 190, 140), outline=(250, 225, 180))
    if k > 0.3:
        dr.ellipse((back - 20, SKY_ + 50, back + 20, SKY_ + 90), fill=mul((225, 190, 140), ss(0.3, 1, k)))
    # ear
    ex, ey = SKX + 300, SKY_ - 10
    dr.ellipse((ex - 34, ey - 34, ex + 34, ey + 34), outline=(255, 230, 140), width=4)
    dr.line((ex - 40, ey + 20, ex + 10, ey + 4), fill=(255, 220, 110), width=10)
    sc = lerp(1, 0.4, k)
    ax, ay = lerp(SKX + 160, ex - 10, k), lerp(SKY_ + 115, ey + 26, k)
    qx, qy = lerp(SKX + 240, ex - 26, k), lerp(SKY_ + 70, ey - 8, k)
    dr.polygon([(ax - 70 * sc, ay - 25 * sc), (ax + 70 * sc, ay - 30 * sc), (ax + 70 * sc, ay + 30 * sc), (ax - 70 * sc, ay + 25 * sc)], fill=(110, 170, 235), outline=(200, 230, 255))
    dr.ellipse((qx - 40 * sc, qy - 30 * sc, qx + 40 * sc, qy + 30 * sc), fill=(110, 170, 235), outline=(200, 230, 255))
    if t > 74.0:
        for i in range(3):
            q = (t * 0.7 + i / 3) % 1; r = lerp(260, 50, q)
            dr.arc((ex + 60 - r, ey - r, ex + 60 + r, ey + r), -40, 40, fill=mul((220, 235, 255), q), width=4)
    hl = 1 - ss(69.6, 70.0, t)
    put(img, L_DENT, SKX - 40, SKY_ + 210, ss(66.0, 66.8, t) * hl)
    put(img, L_ART, SKX + 200, SKY_ + 230, ss(66.6, 67.4, t) * (1 - ss(73.6, 74.0, t)))
    put(img, L_STA, ex + 30, ey - 120, ss(67.4, 68.2, t) * hl)
    put(img, L_NEWJ, SKX + 120, SKY_ + 210, ss(73.0, 73.8, t) * (1 - ss(77.8, 78.2, t)))
    put(img, L_OSS, 540, 680, ss(74.4, 75.2, t) * (1 - ss(77.8, 78.2, t)))
    put(img, L_CHAIN, 540, 680, ss(78.6, 79.4, t))
    return img

# ---------- E: milk ----------
L_TINY = text_img('幼崽很小，自己找不到吃的', FB, 40, (255, 235, 210), 3)
L_GLAND = text_img('皮肤腺体 → 营养液', FB, 42, (255, 240, 220), 3); L_MILK = text_img('乳汁', FB, 56, (255, 250, 240), 4)
L_MAMMAL = text_img('哺乳动物', FB, 60, (255, 225, 160), 4)
def burrow(t):
    img = Image.fromarray(grad((60, 42, 32), (36, 26, 20)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((140, 760, 940, 1260), fill=(26, 18, 14))
    cx, cy = 540, 1060
    cynodont(dr, cx, cy, 1.9, 82, face=-1)
    for i in range(70):
        ang = i / 70 * 2 * math.pi
        px, py = cx + 160 * math.cos(ang), cy + 55 * math.sin(ang)
        dr.line((px, py, px + 22 * math.cos(ang), py + 22 * math.sin(ang)), fill=(150, 120, 90), width=4)
    gk = ss(87.0, 88.4, t)
    for i in range(3):
        bx = 420 + i * 110; by = cy + 150
        dr.ellipse((bx - 34, by - 18, bx + 34, by + 18), fill=(230, 170, 160), outline=(250, 210, 200), width=2)
        dr.ellipse((bx + 18, by - 10, bx + 26, by - 2), fill=(40, 25, 25))
        if gk > 0:
            gx, gy = bx + 30, cy + 70
            dr.ellipse((gx - 14, gy - 14, gx + 14, gy + 14), fill=mul((255, 245, 225), gk * (0.7 + 0.3 * math.sin(t * 4 + i))))
            q = (t * 0.8 + i / 3) % 1
            dr.ellipse((gx - 6, gy + 16 + 50 * q - 6, gx + 6, gy + 16 + 50 * q + 6), fill=mul((255, 255, 245), gk * (1 - q)))
    put(img, L_TINY, 540, 680, ss(82.8, 83.6, t) * (1 - ss(86.6, 87.0, t)))
    put(img, L_GLAND, 540, 680, ss(87.2, 88.0, t) * (1 - ss(90.8, 91.2, t)))
    put(img, L_MILK, 540, 680, ss(91.2, 92.0, t) * (1 - ss(95.0, 95.4, t)))
    put(img, L_MAMMAL, 540, 680, ss(95.4, 96.2, t))
    return img

# ---------- F: Morganucodon, long night, Juramaia, the star ----------
L_MORG = text_img('摩尔根兽 · 约 10 厘米', FB, 42, (255, 225, 160), 3); L_SHREW = text_img('像今天的鼩鼱', FM, 36, (235, 235, 245), 3)
L_DAYD = text_img('白天：恐龙', FB, 42, (255, 225, 170), 3); L_NIGHTM = text_img('黑夜：哺乳动物', FB, 42, (200, 215, 255), 3)
L_SPAN = text_img('一亿多年', FB, 46, (255, 240, 220), 4)
L_JURA = text_img('侏罗兽 · 辽宁', FB, 42, (255, 225, 160), 3); L_YOU = text_img('通往你的那一支', FM, 36, (235, 235, 245), 3)
def shrew(dr, x, y, s, t, a=1.0, face=1, col=(120, 95, 75)):
    walk = math.sin(t * 12)
    dr.line((x - face * 60 * s, y, x - face * 150 * s, y + 10 * s), fill=mul(col, a), width=max(2, int(8 * s)))
    for i, lx in enumerate((x + 35 * s, x - 35 * s)):
        ph = walk if i == 0 else -walk
        dr.line((lx, y + 15 * s, lx + 8 * s * ph, y + 40 * s), fill=mul(col, a * 0.85), width=max(2, int(9 * s)))
    dr.ellipse((x - 70 * s, y - 30 * s, x + 70 * s, y + 28 * s), fill=mul(col, a))
    hx = x + face * 70 * s
    dr.polygon([(hx - face * 20 * s, y - 26 * s), (hx + face * 65 * s, y + 4 * s), (hx - face * 20 * s, y + 20 * s)], fill=mul(col, a))
    dr.ellipse((hx - 4 * s, y - 14 * s, hx + 6 * s, y - 4 * s), fill=mul((15, 12, 12), a))
    dr.ellipse((hx - face * 20 * s - 10 * s, y - 42 * s, hx - face * 20 * s + 10 * s, y - 22 * s), fill=mul((140, 110, 90), a))
    for j in (-1, 1): dr.line((hx + face * 60 * s, y + 2 * s, hx + face * 90 * s, y + 2 * s + j * 8 * s), fill=mul((230, 225, 210), a), width=1)
def foot(dr, x, y, s, a, col=(60, 75, 55)):
    dr.rectangle((x - 70 * s, 470, x + 70 * s, y - 50 * s), fill=mul(col, a))
    for j in (-1, 0, 1):
        dr.polygon([(x + j * 45 * s - 25 * s, y - 60 * s), (x + j * 85 * s, y + 10 * s), (x + j * 45 * s + 25 * s, y - 60 * s)], fill=mul(col, a))
def jurassic(t):
    if t < 107.8 or t >= 116.2:
        img, dr = sky(t, 1.0); land(dr, 1.0)
    if t < 107.8:
        foot(dr, 260, GROUND + 30, 1.6, 1.0)
        dr.ellipse((60, GROUND + 20, 460, GROUND + 70), fill=(25, 25, 32))
        x = lerp(1150, 640, ss(99.6, 103.0, t))
        shrew(dr, x, GROUND + 40, 1.4, t if t < 103 else 103, face=-1)
        if t > 100.4:
            dr.line((x - 130, GROUND + 110, x + 160, GROUND + 110), fill=(240, 235, 210), width=4)
            for j in range(6): dr.line((x - 130 + j * 58, GROUND + 100, x - 130 + j * 58, GROUND + 120), fill=(240, 235, 210), width=3)
        put(img, L_MORG, 640, 820, ss(100.2, 101.0, t)); put(img, L_SHREW, 640, 890, ss(104.0, 104.8, t))
        return img
    if t < 116.2:
        img = Image.new('RGB', (W, H)); top = Image.fromarray(DAY_SKY.astype(np.uint8)); bot = Image.fromarray(NIGHT_SKY.astype(np.uint8))
        img.paste(top.crop((0, 0, W, 900)), (0, 0)); img.paste(bot.crop((0, 900, W, H)), (0, 900))
        dr = ImageDraw.Draw(img)
        dr.rectangle((0, 840, W, 900), fill=(170, 130, 90)); dr.rectangle((0, 1240, W, 1300), fill=(40, 40, 52))
        for i, x in enumerate((180, 520, 860)):
            if i == 1: sauro(dr, x, 860, 0.8)
            else: dino(dr, x, 860, 0.9, t + i, col=(120, 140, 90))
        for i in range(5):
            q = ((t - 108) * 0.12 + i / 5) % 1
            shrew(dr, lerp(-60, 1140, q), 1250, 0.55, t + i, face=1)
        put(img, L_DAYD, 540, 600, ss(108.0, 108.8, t)); put(img, L_NIGHTM, 540, 1000, ss(108.8, 109.6, t))
        put(img, L_SPAN, 540, 1120, ss(110.0, 110.8, t))
        return img
    # Juramaia on a branch, then a star grows
    dr.line((700, GROUND - 30, 700, 560), fill=(55, 45, 40), width=40)
    dr.line((700, 900, 380, 820), fill=(55, 45, 40), width=18)
    for j in range(5): dr.ellipse((300 + j * 60, 780 - (j % 2) * 30, 360 + j * 60, 830 - (j % 2) * 30), fill=(30, 50, 40))
    x = lerp(700, 520, ss(116.4, 119.0, t)); y = lerp(900, 820, ss(116.4, 119.0, t)) - 32
    shrew(dr, x, y, 0.9, t if t < 119 else 119, face=-1, col=(130, 100, 80))
    sk = ss(120.8, 124.5, t)
    if sk > 0:
        sx, sy = 260, 600
        r = 6 + 10 * sk
        dr.line((sx + 6, sy - 4, sx + 6 + 120 * sk, sy - 4 - 70 * sk), fill=mul((255, 220, 170), 0.5 * sk), width=3)
        dr.ellipse((sx - r * 2.4, sy - r * 2.4, sx + r * 2.4, sy + r * 2.4), fill=mul((120, 90, 70), 0.35 * sk))
        dr.ellipse((sx - r, sy - r, sx + r, sy + r), fill=mul((255, 240, 210), sk))
    put(img, L_JURA, 560, 700, ss(116.6, 117.4, t) * (1 - ss(120.4, 120.8, t)))
    put(img, L_YOU, 560, 760, ss(117.2, 118.0, t) * (1 - ss(120.4, 120.8, t)))
    return img

def render(t):
    if t < 6.0: return render15(137.5 + t)
    if t < 31.8:
        k = ss(6.0, 6.6, t) * (1 - ss(31.2, 31.8, t))
        if 14.4 < t < 15.2: k *= 1 - 0.85 * math.sin(math.pi * (t - 14.4) / 0.8)
        if 22.8 < t < 23.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 22.8) / 0.8)
        return dim(triassic(t), k)
    if t < 44.4: return dim(shrink(t), ss(31.8, 32.4, t) * (1 - ss(43.8, 44.4, t)))
    if t < 61.4: return dim(warm(t), ss(44.4, 45.0, t) * (1 - ss(60.8, 61.4, t)))
    if t < 82.6:
        k = ss(61.4, 62.0, t) * (1 - ss(82.0, 82.6, t))
        if 65.2 < t < 66.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 65.2) / 0.8)
        return dim(skull(t), k)
    if t < 99.4: return dim(burrow(t), ss(82.6, 83.2, t) * (1 - ss(98.8, 99.4, t)))
    k = ss(99.4, 100.0, t)
    for a in (107.4, 115.8):
        if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
    return dim(jurassic(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep16_{ts}.png')
