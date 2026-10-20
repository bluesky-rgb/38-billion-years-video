import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep17 import tree
from ep19 import FUR
from ep20 import hominin, savanna, SAV_SKY
from ep21 import render as render21, NIGHT, DARK

CLEAN = False
rng = np.random.default_rng(221)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
def glow_at(cx, cy, rx, ry, amp):
    return (np.exp(-(((_xx - cx) / rx) ** 2 + ((_yy - cy) / ry) ** 2)) * amp)[..., None] * np.array([1.0, 0.55, 0.18])
G_CAMP = glow_at(540, 1150, 420, 320, 160)
G_SMALL = glow_at(540, 1100, 260, 200, 150)
def add_glow(img, G, k):
    return Image.fromarray(np.clip(np.asarray(img, np.float32) + G * k, 0, 255).astype(np.uint8))
def flames(dr, x, y, s, t, k=1.0):
    for j in range(7):
        h = (70 + 45 * math.sin(t * 8 + j * 1.7)) * s * k
        fx = x + (j - 3) * 18 * s
        dr.polygon([(fx - 20 * s, y), (fx, y - h - 30 * s * k), (fx + 20 * s, y)], fill=(255, 140 + 15 * (j % 3), 40))
    for j in range(4):
        h = (40 + 25 * math.sin(t * 9 + j)) * s * k
        fx = x + (j - 1.5) * 18 * s
        dr.polygon([(fx - 12 * s, y), (fx, y - h), (fx + 12 * s, y)], fill=(255, 220, 120))
def logs(dr, x, y, s):
    dr.line((x - 70 * s, y + 10 * s, x + 70 * s, y - 10 * s), fill=(80, 55, 35), width=int(18 * s))
    dr.line((x - 70 * s, y - 10 * s, x + 70 * s, y + 10 * s), fill=(90, 62, 40), width=int(18 * s))

# ---------- A: after the wildfire ----------
L_ROAST = text_img('野火烧过：烤熟的动物和块茎', FB, 40, (255, 225, 180), 3)
L_SOFT = text_img('又软又香，好嚼得多', FB, 42, (255, 235, 200), 3)
BURNT_SKY = grad((120, 110, 110), (210, 170, 130), 480, 1100)
def burnt(t):
    img = Image.fromarray(BURNT_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(70, 60, 50))
    for i in range(40):
        x = (i * 29) % W; dr.line((x, GROUND, x + 3, GROUND - 10 - (i % 4) * 4), fill=(40, 34, 30), width=3)
    for i in range(6):
        q = (t * 0.12 + i / 6) % 1; x = 120 + i * 170; y = lerp(GROUND - 20, 520, q)
        sc = BURNT_SKY[int(min(max(y, 0), H - 1)), int(min(max(x, 0), W - 1))]; dr.ellipse((x - 40 - 60 * q, y - 30 - 30 * q, x + 40 + 60 * q, y + 30 + 30 * q), fill=tuple(int(v) for v in lerp(np.array((100, 95, 95)), sc, 0.3 + 0.7 * q)))
    dr.ellipse((560, GROUND + 10, 760, GROUND + 70), fill=(110, 60, 40))
    for j in range(5): dr.arc((580 + j * 30, GROUND - 30, 610 + j * 30, GROUND + 40), 180, 360, fill=(60, 45, 35), width=5)
    for j in range(3): dr.ellipse((240 + j * 70, GROUND + 40, 290 + j * 70, GROUND + 80), fill=(140, 90, 55))
    if t > 14.6:
        hominin(dr, lerp(-100, 420, ss(14.8, 17.6, t)), GROUND + 30, 1.4, t if t < 17.6 else 17.6, carry=t > 17.6)
    put(img, L_ROAST, 540, 640, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_SOFT, 540, 640, ss(15.0, 15.8, t))
    return img

# ---------- B: keeping the fire ----------
L_KEEP = text_img('捡起燃烧的树枝，不断添柴', FB, 40, (255, 225, 160), 3)
def keep(t):
    k = ss(23.4, 26.4, t)
    img = Image.fromarray(NIGHT.astype(np.uint8))
    img = add_glow(img, G_SMALL, 0.35 + 0.65 * k)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(50, 42, 34))
    logs(dr, 540, GROUND + 10, 1.0)
    for j in range(int(k * 4)): dr.line((480 + j * 30, GROUND - 5, 520 + j * 30, GROUND - 40), fill=(90, 60, 40), width=10)
    flames(dr, 540, GROUND, 0.5 + 0.7 * k, t, 1.0 if t > 23.2 else 0.0)
    x = lerp(150, 400, ss(19.2, 22.6, t))
    hominin(dr, x, GROUND + 30, 1.4, t if t < 22.6 else 22.6, col=(120, 85, 60))
    if t < 23.4:
        bx, by = x + 40, GROUND - 260
        dr.line((x + 10, GROUND - 200, bx + 40, by), fill=(90, 60, 40), width=10)
        flames(dr, bx + 40, by, 0.35, t)
    put(img, L_KEEP, 540, 640, ss(19.4, 20.2, t))
    return img

# ---------- C: evidence ----------
L_CAVE = text_img('南非的山洞：灰烬和烧过的骨头', FB, 40, (255, 225, 180), 3)
L_HEARTH = text_img('火塘：固定生火的地方', FB, 42, (255, 225, 160), 3)
def evidence(t):
    if t < 36.0:
        img = Image.fromarray(grad((60, 50, 44), (30, 26, 24)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.ellipse((-200, 560, 1280, 1500), fill=(20, 16, 14))
        for y0, y1, c in ((1220, 1280, (140, 120, 95)), (1280, 1305, (70, 70, 72)), (1305, 1400, (150, 128, 100)), (1400, 1500, (130, 110, 88))):
            dr.rectangle((0, y0, W, y1), fill=c)
        g = ss(28.4, 29.4, t) * (0.6 + 0.4 * math.sin(t * 4))
        dr.rectangle((0, 1278, W, 1307), outline=mul((255, 210, 120), g), width=3)
        for i in range(8):
            x = 120 + i * 120; dr.line((x - 20, 1292, x + 20, 1288), fill=(25, 22, 20), width=7)
        put(img, L_CAVE, 540, 640, ss(28.0, 28.8, t))
        return img
    img = Image.fromarray(NIGHT.astype(np.uint8)); img = add_glow(img, G_SMALL, 1.0); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(50, 42, 34))
    for j in range(10):
        a = j / 10 * 2 * math.pi
        x, y = 540 + 140 * math.cos(a), GROUND + 20 + 40 * math.sin(a)
        dr.ellipse((x - 26, y - 18, x + 26, y + 18), fill=(130, 125, 118))
    logs(dr, 540, GROUND + 10, 1.0); flames(dr, 540, GROUND, 1.1, t)
    put(img, L_HEARTH, 540, 640, ss(36.2, 37.0, t))
    return img

# ---------- D: what heat does ----------
L_WHY = text_img('火为什么这么重要？', FB, 46, (255, 225, 160), 4)
L_RAW = text_img('生的：坚韧的长纤维', FM, 36, (230, 230, 235), 3); L_COOK = text_img('熟的：软化、分解', FM, 36, (255, 215, 160), 3)
L_EN = text_img('身体吸收的能量', FB, 38, (240, 240, 240), 3)
L_RAWB = text_img('生', FB, 36, (230, 230, 235), 3); L_COOKB = text_img('熟', FB, 36, (255, 215, 160), 3)
L_GERM = text_img('高温杀死病菌', FB, 42, (200, 245, 200), 3)
def fibers(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 48.8:
        put(img, L_WHY, 540, 640, ss(40.6, 41.4, t) * (1 - ss(44.4, 44.8, t)))
        ck = ss(45.0, 47.6, t)
        for side, (x0, lab) in enumerate(((120, L_RAW), (600, L_COOK))):
            for i in range(9):
                y = 820 + i * 50
                if side == 0 or ck < 0.05:
                    pts = [(x0 + j * 30, y + 14 * math.sin(j * 0.9 + i)) for j in range(13)]
                    dr.line(pts, fill=(200, 170, 120), width=6)
                else:
                    for j in range(4):
                        sx = x0 + j * 95 + 20 * ck * math.sin(i + j)
                        L = lerp(90, 40, ck)
                        dr.line((sx, y, sx + L, y + 8 * math.sin(i * j)), fill=(230, 190, 120), width=6)
            put(img, lab, x0 + 180, 1320, 1.0 if side == 0 else ss(45.2, 46.0, t))
        if t > 44.6:
            img2 = add_glow(img, glow_at(780, 1360, 200, 80, 120), ss(44.6, 45.4, t)); img = img2; dr = ImageDraw.Draw(img)
            flames(dr, 780, 1420, 0.8, t)
        return img
    if t < 53.0:
        put(img, L_EN, 540, 700, 1.0)
        for i, (v, lab, c, t0) in enumerate(((0.45, L_RAWB, (200, 200, 210), 49.0), (0.8, L_COOKB, (250, 180, 80), 49.8))):
            y = 860 + i * 200
            k = ss(t0, t0 + 1.4, t)
            put(img, lab, 140, y + 30, 1.0)
            dr.rounded_rectangle((220, y, 980, y + 60), radius=20, fill=(40, 44, 54))
            dr.rounded_rectangle((220, y, 220 + 760 * v * k, y + 60), radius=20, fill=c)
        return img
    img = add_glow(img, glow_at(540, 1250, 300, 120, 140), 1.0); dr = ImageDraw.Draw(img)
    flames(dr, 540, 1300, 1.2, t)
    for i in range(10):
        x = 200 + (i * 73) % 680; y = 800 + (i * 131) % 300
        k = ss(53.6 + i * 0.12, 54.4 + i * 0.12, t)
        dr.ellipse((x - 26, y - 20, x + 26, y + 20), fill=mul((110, 200, 110), 1 - 0.8 * k))
        for j in range(5): dr.line((x - 26, y - 10 + j * 5, x - 40, y - 14 + j * 7), fill=mul((110, 200, 110), 1 - 0.8 * k), width=2)
        if k > 0.5: dr.line((x - 30, y - 24, x + 30, y + 24), fill=mul((230, 80, 70), k), width=4)
    put(img, L_GERM, 540, 640, ss(53.2, 54.0, t))
    return img

# ---------- E: chewing time, smaller jaws ----------
L_CHIMP = text_img('黑猩猩：每天咀嚼五六个小时', FM, 36, (230, 230, 235), 3)
L_HUMC = text_img('吃熟食的人：约一个小时', FM, 36, (255, 215, 160), 3)
L_SMALL = text_img('牙齿、下巴、肠子都变小了', FB, 40, (255, 235, 200), 3)
L_TOBRAIN = text_img('省下的能量 → 大脑', FB, 44, (255, 200, 200), 3)
def clockface(dr, cx, cy, r, frac, col):
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 44, 54), outline=(200, 200, 210), width=3)
    if frac > 0: dr.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frac, fill=col)
    for j in range(12):
        a = j / 12 * 2 * math.pi
        dr.line((cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill=(200, 200, 210), width=3)
def chew(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 65.8:
        clockface(dr, 300, 960, 180, (5.5 / 24) * ss(57.6, 59.4, t), (220, 120, 90))
        put(img, L_CHIMP, 300, 1200, ss(57.6, 58.4, t))
        clockface(dr, 780, 960, 180, (1 / 24) * ss(61.8, 63.0, t), (250, 190, 90))
        put(img, L_HUMC, 780, 1200, ss(61.8, 62.6, t))
        return img
    k = ss(66.2, 69.0, t)
    cx, cy = 520, 1000
    dr.ellipse((cx - 220, cy - 260, cx + 180, cy + 60), fill=(200, 160, 135))
    jaw = lerp(1.0, 0.65, k)
    dr.polygon([(cx + 120, cy - 40), (cx + 120 + 170 * jaw, cy + 10), (cx + 120 + 150 * jaw, cy + 120 * jaw), (cx - 40, cy + 140 * jaw)], fill=(195, 155, 130))
    for j in range(6):
        tx = cx + 130 + j * 26 * jaw
        dr.rectangle((tx, cy + 10, tx + 18 * jaw, cy + 10 + 26 * jaw), fill=(245, 240, 225))
    bk = ss(70.2, 72.0, t)
    r = lerp(110, 150, bk)
    dr.ellipse((cx - 60 - r, cy - 150 - r * 0.7, cx - 60 + r, cy - 150 + r * 0.7), fill=(235, 170, 170), outline=(255, 210, 210), width=3)
    put(img, L_SMALL, 540, 640, ss(66.0, 66.8, t) * (1 - ss(69.8, 70.2, t)))
    put(img, L_TOBRAIN, 540, 640, ss(70.2, 71.0, t))
    return img

# ---------- F: around the fire ----------
L_WARM = text_img('温暖 · 光亮', FB, 44, (255, 220, 150), 3)
L_BEAST = text_img('猛兽不敢靠近', FB, 42, (255, 225, 190), 3)
L_SHARE = text_img('围坐：分食物、说话', FB, 42, (255, 235, 200), 3)
L_NIGHTL = text_img('天黑以后，一天还没有结束', FB, 40, (220, 225, 255), 3)
def sitter(dr, x, y, s, face, t, i):
    c = (110 + 10 * (i % 2), 80, 58)
    dr.ellipse((x - 50 * s, y - 150 * s, x + 50 * s, y - 20 * s), fill=c)
    dr.ellipse((x - 32 * s, y - 210 * s, x + 32 * s, y - 145 * s), fill=c)
    dr.ellipse((x + face * 8 * s - 18 * s, y - 198 * s, x + face * 8 * s + 18 * s, y - 165 * s), fill=(185, 140, 105))
    dr.ellipse((x - 60 * s, y - 40 * s, x + 60 * s, y + 10 * s), fill=c)
    ph = math.sin(t * 2 + i)
    dr.line((x, y - 110 * s, x + face * (60 + 15 * ph) * s, y - 80 * s), fill=c, width=int(14 * s))
def camp(t):
    img = Image.fromarray(NIGHT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(80):
        x = (i * 151) % W; y = 480 + (i * 89) % 560
        dr.point((x, y), fill=(220, 220, 240))
    img = add_glow(img, G_CAMP, 0.95 + 0.05 * math.sin(t * 9)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND + 40, W, H), fill=(60, 46, 36))
    for i, (x, y, s, f) in enumerate(((300, 1180, 1.1, 1), (780, 1180, 1.1, -1), (420, 1330, 1.3, 1), (680, 1330, 1.3, -1))):
        if y < 1300: sitter(dr, x, y, s, f, t, i)
    logs(dr, 540, 1240, 1.1); flames(dr, 540, 1230, 1.3, t)
    for i, (x, y, s, f) in enumerate(((300, 1180, 1.1, 1), (780, 1180, 1.1, -1), (420, 1330, 1.3, 1), (680, 1330, 1.3, -1))):
        if y >= 1300: sitter(dr, x, y, s, f, t, i)
    if 78.4 < t < 83.0:
        k = ss(78.8, 82.0, t)
        for sg in (-1, 1):
            ex = 540 + sg * lerp(430, 560, k)
            dr.ellipse((ex - 14, 1050 - 6, ex - 2, 1050 + 6), fill=(255, 230, 120)); dr.ellipse((ex + 6, 1050 - 6, ex + 18, 1050 + 6), fill=(255, 230, 120))
    if t > 83.0:
        for i in range(2):
            q = (t * 0.6 + i * 0.5) % 1
            x = lerp(330, 750, q) if i == 0 else lerp(750, 330, q)
            dr.ellipse((x - 14, 1100 - 10, x + 14, 1100 + 10), fill=(200, 110, 70))
    put(img, L_WARM, 540, 640, ss(74.6, 75.4, t) * (1 - ss(78.4, 78.8, t)))
    put(img, L_BEAST, 540, 640, ss(78.8, 79.6, t) * (1 - ss(82.6, 83.0, t)))
    put(img, L_SHARE, 540, 640, ss(83.0, 83.8, t) * (1 - ss(86.8, 87.2, t)))
    put(img, L_NIGHTL, 540, 640, ss(87.2, 88.0, t))
    return img

# ---------- G: colder places, bigger brains ----------
L_COLD = text_img('有了火：走进更冷的地方', FB, 40, (220, 235, 255), 3)
L_BR = text_img('大脑：超过 1000 毫升', FB, 40, (255, 200, 200), 3)
def cold(t):
    img = Image.fromarray(grad((120, 140, 170), (215, 225, 235), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(235, 240, 248))
    for x in (120, 900):
        dr.polygon([(x, GROUND - 420), (x - 110, GROUND), (x + 110, GROUND)], fill=(70, 100, 90))
        dr.polygon([(x, GROUND - 420), (x - 50, GROUND - 230), (x + 50, GROUND - 230)], fill=(240, 245, 250))
    for i in range(50):
        q = (t * 0.2 + i / 50) % 1; x = (i * 61) % W + 20 * math.sin(t + i); y = lerp(480, GROUND, q)
        dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(250, 250, 255))
    x = lerp(200, 520, ss(91.6, 95.4, t))
    hominin(dr, x, GROUND + 30, 1.4, t if t < 95.4 else 95.4, col=(110, 82, 62))
    dr.line((x + 20, GROUND - 220, x + 60, GROUND - 300), fill=(90, 60, 40), width=10)
    flames(dr, x + 60, GROUND - 300, 0.35, t)
    if t > 95.6:
        k = ss(95.8, 97.4, t)
        dr.rounded_rectangle((120, 1340, 960, 1400), radius=20, fill=(40, 44, 54))
        dr.rounded_rectangle((120, 1340, 120 + 840 * lerp(0.45, 0.82, k), 1400), radius=20, fill=(235, 150, 150))
        put(img, L_BR, 540, 1450, ss(95.8, 96.6, t))
    put(img, L_COLD, 540, 640, ss(91.6, 92.4, t))
    return img

# ---------- H: Homo sapiens ----------
L_SAP = text_img('智人 · 摩洛哥', FB, 50, (255, 225, 160), 4)
L_YOURS = text_img('你的物种', FB, 44, (255, 235, 200), 3)
L_SAME = text_img('身体：和你几乎一样', FB, 42, (255, 235, 200), 3)
L_ONLY = text_img('只生活在非洲', FB, 44, (255, 225, 160), 3)
L_NEXT = text_img('下一步：走向整个世界', FB, 42, (255, 235, 200), 3)
AFR = [(0.30, 0.0), (0.55, 0.0), (0.72, 0.1), (0.95, 0.26), (1.0, 0.33), (0.86, 0.46), (0.80, 0.62), (0.66, 0.85), (0.55, 1.0), (0.46, 0.96), (0.40, 0.72), (0.36, 0.52), (0.16, 0.46), (0.0, 0.31), (0.05, 0.12)]
def sapiens(dr, x, y, s, a=1.0, col=(115, 80, 58)):
    dr.ellipse((x - 26 * s, y - 300 * s, x + 26 * s, y - 238 * s), fill=mul(col, a))
    dr.rounded_rectangle((x - 36 * s, y - 238 * s, x + 36 * s, y - 110 * s), radius=int(16 * s), fill=mul(col, a))
    for sg in (-1, 1):
        dr.line((x + sg * 40 * s, y - 225 * s, x + sg * 52 * s, y - 120 * s), fill=mul(col, a), width=int(14 * s))
        dr.line((x + sg * 16 * s, y - 115 * s, x + sg * 20 * s, y), fill=mul(col, a), width=int(18 * s))
def you_outline(dr, x, y, s, a=1.0):
    c = mul((200, 200, 210), a)
    dr.ellipse((x - 26 * s, y - 300 * s, x + 26 * s, y - 238 * s), outline=c, width=3)
    dr.rounded_rectangle((x - 36 * s, y - 238 * s, x + 36 * s, y - 110 * s), radius=int(16 * s), outline=c, width=3)
    for sg in (-1, 1): dr.line((x + sg * 16 * s, y - 115 * s, x + sg * 20 * s, y), fill=c, width=3)
def africa(t):
    if t < 112.8:
        img = Image.fromarray(grad((180, 175, 175), (240, 205, 160), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.rectangle((0, GROUND, W, H), fill=(200, 160, 110))
        dr.polygon([(0, GROUND), (250, GROUND - 220), (520, GROUND)], fill=(170, 130, 95))
        if t < 108.6:
            sapiens(dr, lerp(300, 560, ss(100.2, 103.6, t)), GROUND + 30, 1.6)
            put(img, L_SAP, 540, 640, ss(100.2, 101.0, t) * (1 - ss(104.0, 104.4, t)))
            put(img, L_YOURS, 540, 640, ss(104.4, 105.2, t))
        else:
            sapiens(dr, 420, GROUND + 30, 1.6)
            you_outline(dr, 680, GROUND + 30, 1.6, ss(108.8, 109.6, t))
            put(img, L_SAME, 540, 640, ss(108.8, 109.6, t))
        return img
    img = Image.fromarray(grad((20, 50, 90), (12, 30, 60)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    ox, oy, sw, sh = 300, 860, 520, 640
    dr.polygon([(0, 560), (W, 560), (W, 840), (820, 900), (760, 820), (560, 880), (330, 860), (0, 900)], fill=(120, 130, 100))
    dr.polygon([(ox + x * sw, oy + y * sh) for x, y in AFR], fill=(200, 170, 110))
    for i in range(30):
        px = ox + sw * (0.35 + 0.4 * ((i * 0.37) % 1)); py = oy + sh * (0.15 + 0.6 * ((i * 0.61) % 1))
        dr.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(230, 80, 60))
    put(img, L_ONLY, 540, 640, ss(113.0, 113.8, t) * (1 - ss(116.8, 117.2, t)))
    if t > 117.0:
        k = ss(117.2, 119.6, t)
        sx, sy = ox + sw * 0.85, oy + sh * 0.15
        for ex, ey in ((sx + 160, sy - 160), (sx - 60, sy - 240), (sx + 260, sy - 40)):
            mx, my = lerp(sx, ex, k), lerp(sy, ey, k)
            dr.line((sx, sy, mx, my), fill=(255, 225, 160), width=6)
            dr.ellipse((mx - 10, my - 10, mx + 10, my + 10), fill=(255, 225, 160))
        put(img, L_NEXT, 540, 640, ss(117.2, 118.0, t))
    return img

def render(t):
    if t < 6.0: return render21(132.9 + t)
    if t < 19.0: return dim(burnt(t), ss(6.0, 6.6, t) * (1 - ss(18.4, 19.0, t)))
    if t < 27.6: return dim(keep(t), ss(19.0, 19.6, t) * (1 - ss(27.0, 27.6, t)))
    if t < 40.4:
        k = ss(27.6, 28.2, t) * (1 - ss(39.8, 40.4, t))
        if 35.6 < t < 36.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 35.6) / 0.8)
        return dim(evidence(t), k)
    if t < 57.2:
        k = ss(40.4, 41.0, t) * (1 - ss(56.6, 57.2, t))
        for a in (48.4, 52.6):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(fibers(t), k)
    if t < 74.4:
        k = ss(57.2, 57.8, t) * (1 - ss(73.8, 74.4, t))
        if 65.4 < t < 66.2: k *= 1 - 0.85 * math.sin(math.pi * (t - 65.4) / 0.8)
        return dim(chew(t), k)
    if t < 91.4: return dim(camp(t), ss(74.4, 75.0, t) * (1 - ss(90.8, 91.4, t)))
    if t < 100.0: return dim(cold(t), ss(91.4, 92.0, t) * (1 - ss(99.4, 100.0, t)))
    k = ss(100.0, 100.6, t)
    if 112.4 < t < 113.2: k *= 1 - 0.85 * math.sin(math.pi * (t - 112.4) / 0.8)
    return dim(africa(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep22_{ts}.png')
