import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import dino, sauro, shrew, land, sky, GROUND, render as render16

CLEAN = False
rng = np.random.default_rng(171)
SPACE = grad((4, 6, 16), (12, 16, 30))
STARS = [(rng.random() * W, 480 + rng.random() * 1400, rng.random()) for _ in range(160)]
CRET_SKY = grad((120, 170, 210), (225, 220, 195), 480, 1100)

def bird(dr, x, y, s, t, a=1.0, col=(70, 60, 55)):
    f = math.sin(t * 8)
    dr.ellipse((x - 26 * s, y - 10 * s, x + 26 * s, y + 10 * s), fill=mul(col, a))
    dr.ellipse((x + 18 * s, y - 16 * s, x + 36 * s, y + 2 * s), fill=mul(col, a))
    dr.polygon([(x + 34 * s, y - 9 * s), (x + 48 * s, y - 5 * s), (x + 34 * s, y - 3 * s)], fill=mul((220, 170, 60), a))
    for sg in (-1,):
        dr.polygon([(x - 10 * s, y - 4 * s), (x + 10 * s, y - 4 * s), (x - 20 * s, y - 4 * s - 60 * s * f)], fill=mul(col, a * 0.9))
def tree(dr, x, base, h, a=1.0, burn=0.0, dead=0.0):
    tc = tuple(int(v) for v in lerp(np.array([85, 65, 45]), np.array([40, 35, 32]), max(burn, dead)))
    dr.line((x, base, x, base - h), fill=mul(tc, a), width=16)
    lc = tuple(int(v) for v in lerp(np.array([70, 130, 70]), np.array([60, 50, 40]), max(burn, dead)))
    if dead < 0.95:
        for j in range(4):
            y = base - h + 30 + j * 50; w = 40 + j * 22
            dr.polygon([(x, y - 50), (x - w, y + 20), (x + w, y + 20)], fill=mul(lc, a * (1 - dead)))
    else:
        for j in range(3):
            y = base - h * (0.5 + j * 0.15); dr.line((x, y, x + (-1) ** j * 60, y - 40), fill=mul(tc, a), width=6)

# ---------- A: Cretaceous ----------
L_MAM = text_img('哺乳动物：仍然很小', FB, 40, (255, 235, 200), 3); L_BIRD = text_img('鸟：恐龙的一支', FB, 42, (255, 235, 200), 3)
def cretaceous(t):
    img = Image.fromarray(CRET_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((820, 560, 940, 680), fill=(255, 250, 225))
    land(dr)
    sauro(dr, 760, GROUND + 10, 1.3)
    dino(dr, lerp(-200, 330, ss(6.2, 10.4, t)), GROUND + 30, 1.6, t, col=(110, 95, 75))
    dr.ellipse((850, GROUND + 50, 990, GROUND + 110), fill=(60, 45, 35))
    mk = ss(10.8, 11.6, t)
    if mk > 0: shrew(dr, 920, GROUND + 60, 0.7, 11, mk, face=-1)
    put(img, L_MAM, 800, GROUND - 80, mk * (1 - ss(14.4, 14.8, t)))
    bk = ss(14.9, 15.6, t)
    if bk > 0:
        bird(dr, lerp(-60, 700, ss(14.9, 19.0, t)), 760 - 60 * ss(14.9, 19.0, t), 2.2, t, bk)
        put(img, L_BIRD, 540, 640, bk)
    return img

# ---------- B: space, impact ----------
GX, GY, GR = 600, 1080, 360
CONT = [(-120, -150, 90, 0.4), (40, -60, 120, 1.9), (-160, 80, 80, 3.1), (110, 150, 70, 4.4), (-20, 200, 60, 5.0)]
def blobp(cx, cy, r, sd):
    return [(cx + r * (1 + 0.18 * math.sin(3 * a + sd) + 0.1 * math.sin(5 * a + sd * 2)) * math.cos(a),
             cy + r * (1 + 0.18 * math.sin(3 * a + sd) + 0.1 * math.sin(5 * a + sd * 2)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
def globe(dr, gx, gy, gr, haze=0.0):
    dr.ellipse((gx - gr - 10, gy - gr - 10, gx + gr + 10, gy + gr + 10), outline=(70, 120, 180), width=8)
    oc = tuple(int(v) for v in lerp(np.array([35, 90, 150]), np.array([95, 85, 75]), haze))
    lc = tuple(int(v) for v in lerp(np.array([110, 140, 80]), np.array([110, 95, 80]), haze))
    dr.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=oc)
    for x, y, r, sd in CONT:
        dr.polygon(blobp(gx + x * gr / 360, gy + y * gr / 360, r * gr / 360, sd), fill=lc)
    YX, YY = gx - 60 * gr / 360, gy - 10 * gr / 360
    return YX, YY
L_AST = text_img('小行星 · 直径约 10 公里', FB, 42, (255, 225, 170), 3)
L_EVE = text_img('珠穆朗玛峰 约 8.8 公里', FM, 34, (235, 235, 245), 3); L_A10 = text_img('小行星 约 10 公里', FM, 34, (255, 210, 160), 3)
L_YUC = text_img('尤卡坦半岛 · 墨西哥', FB, 42, (255, 225, 170), 3)
L_CRATER = text_img('约 180 公里宽的大坑', FB, 42, (255, 225, 170), 3)
L_NUKE = text_img('能量：人类所有核武器的上万倍', FB, 40, (255, 240, 220), 3)
def rock(dr, x, y, r, a=1.0):
    dr.polygon([(x + r * (1 + 0.15 * math.sin(5 * q)) * math.cos(q), y + r * (1 + 0.15 * math.sin(5 * q)) * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 20)], fill=mul((120, 105, 95), a))
    dr.ellipse((x - r * 0.3, y - r * 0.4, x, y - r * 0.1), fill=mul((90, 80, 72), a))
def space(t):
    img = Image.fromarray(SPACE.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for x, y, b in STARS: dr.point((x, y), fill=(int(160 + 80 * b),) * 3)
    if t < 23.2:
        yx, yy = globe(dr, GX, GY, GR)
        k = ss(19.2, 23.2, t)
        ax, ay = lerp(170, 300, k), lerp(640, 780, k)
        dr.polygon([(ax - 170, ay - 120), (ax - 10, ay - 22), (ax + 10, ay + 22)], fill=(150, 90, 60))
        rock(dr, ax, ay, 26)
        put(img, L_AST, 540, 640, ss(19.6, 20.4, t))
        return img
    if t < 27.4:
        dr.polygon([(180, 1300), (420, 760), (660, 1300)], fill=(150, 160, 175)); dr.polygon([(360, 900), (420, 760), (480, 900)], fill=(240, 245, 250))
        dr.ellipse((690, 690, 1000, 1300 - 0), fill=(120, 105, 95))
        dr.line((140, 1300, 1040, 1300), fill=(200, 200, 210), width=3)
        put(img, L_EVE, 420, 1360, ss(23.6, 24.4, t)); put(img, L_A10, 845, 1360, ss(24.2, 25.0, t))
        return img
    if t < 35.8:
        yx, yy = globe(dr, GX, GY, GR)
        if t < 31.6:
            k = ss(27.6, 29.6, t)
            ax, ay = lerp(260, yx, k), lerp(760, yy, k)
            rock(dr, ax, ay, lerp(26, 10, k))
            if t > 29.6:
                f = ss(29.6, 30.0, t) * (1 - ss(30.4, 31.4, t))
                for r in (40, 90, 150):
                    dr.ellipse((yx - r * f * 1.5, yy - r * f * 1.5, yx + r * f * 1.5, yy + r * f * 1.5), outline=mul((255, 230, 180), f), width=6)
                dr.ellipse((yx - 30, yy - 30, yx + 30, yy + 30), fill=mul((255, 240, 200), max(f, 0.3)))
            put(img, L_YUC, yx, yy - 120, ss(27.8, 28.6, t))
            return img
        img = Image.fromarray(grad((110, 140, 120), (80, 110, 95)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.polygon([(0, 560), (W, 560), (W, 900), (0, 1200)], fill=(40, 100, 150))
        cx, cy = 560, 1000
        for r, c in ((330, (150, 125, 95)), (300, (125, 100, 80)), (180, (140, 115, 90)), (90, (115, 90, 72))):
            dr.ellipse((cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), fill=c)
        dr.line((230, 1400, 890, 1400), fill=(240, 240, 240), width=5)
        for x in (230, 890): dr.line((x, 1385, x, 1415), fill=(240, 240, 240), width=4)
        put(img, L_CRATER, 560, 1470, ss(31.8, 32.6, t))
        return img
    img = Image.fromarray(grad((40, 30, 30), (90, 50, 30)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(35.9, 39.6, t)
    for i in range(4):
        r = (k * 900 + i * 120) % 1100
        dr.ellipse((540 - r, 1000 - r * 0.5, 540 + r, 1000 + r * 0.5), outline=mul((255, 200, 120), max(0, 1 - r / 1100)), width=10)
    fl = 1 - ss(36.0, 37.5, t)
    if fl > 0.02: dr.ellipse((540 - 260, 1000 - 260, 540 + 260, 1000 + 260), fill=mul((255, 250, 230), fl))
    dr.ellipse((540 - 120, 1000 - 50, 540 + 120, 1000 + 50), fill=mul((255, 150, 60), 0.5 + 0.5 * fl))
    put(img, L_NUKE, 540, 640, ss(36.4, 37.2, t))
    return img

# ---------- C: fire and tsunami ----------
L_RAIN = text_img('碎石落回：像流星雨', FB, 42, (255, 225, 180), 3); L_FIRE = text_img('空气滚烫 · 森林大火', FB, 42, (255, 215, 160), 3)
L_TSU = text_img('巨大的海啸', FB, 46, (220, 240, 255), 3)
TREES = [(90, 330), (260, 380), (450, 300), (640, 360), (830, 320), (1000, 370)]
def fire(t):
    if t < 48.6:
        hot = ss(42.0, 46.0, t)
        img = Image.fromarray((grad((60, 50, 70), (150, 110, 100), 480, 1100) * (1 - hot) + grad((140, 40, 20), (255, 140, 60), 480, 1100) * hot).astype(np.uint8))
        dr = ImageDraw.Draw(img)
        for i in range(26):
            q = (t * 0.45 + i / 26) % 1
            x = (i * 157) % W + q * 260; y = lerp(420, 1150, q)
            dr.line((x - 120, y - 70, x, y), fill=(255, 200, 120), width=4); dr.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 245, 220))
        dr.polygon([(0, GROUND - 30), (W, GROUND - 50), (W, H), (0, H)], fill=tuple(int(v) for v in lerp(np.array([110, 95, 70]), np.array([60, 40, 30]), hot)))
        for i, (x, h) in enumerate(TREES):
            b = ss(44.6 + i * 0.3, 46.0 + i * 0.3, t)
            tree(dr, x, GROUND - 30, h, burn=b)
            if b > 0:
                for j in range(3):
                    fh = (60 + 40 * math.sin(t * 9 + i + j)) * b
                    fx = x - 40 + j * 40
                    dr.polygon([(fx - 26, GROUND - 40 - h * 0.4), (fx, GROUND - 40 - h * 0.4 - fh * 2), (fx + 26, GROUND - 40 - h * 0.4)], fill=(255, 150 + 50 * (j % 2), 40))
        put(img, L_RAIN, 540, 640, ss(40.4, 41.2, t) * (1 - ss(44.0, 44.4, t)))
        put(img, L_FIRE, 540, 640, ss(44.6, 45.4, t))
        return img
    img = Image.fromarray(grad((90, 70, 70), (170, 120, 100), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1150), (420, 1130), (420, H), (0, H)], fill=(120, 100, 75))
    k = ss(49.0, 52.6, t)
    wx = lerp(1300, 380, k); hh = 520
    dr.polygon([(wx, 1150 - hh), (wx + 160, 1150 - hh + 60), (W + 100, 1150), (W + 100, H), (wx - 60, H), (wx - 60, 1150)], fill=(40, 90, 130))
    dr.arc((wx - 140, 1150 - hh - 20, wx + 160, 1150 - hh + 260), 180, 300, fill=(230, 240, 250), width=16)
    dr.rectangle((0, 1150, W, H), fill=(40, 90, 130)) if k > 0.98 else None
    for i, x in enumerate((80, 220, 350)): tree(dr, x, 1140, 260, burn=0.6)
    put(img, L_TSU, 540, 640, ss(49.0, 49.8, t))
    return img

# ---------- D: haze ----------
L_HAZE = text_img('尘埃、烟灰、硫酸盐遮住阳光', FB, 40, (240, 230, 220), 3)
L_WINTER = text_img('撞击冬天：持续好几年', FB, 44, (210, 225, 245), 3)
def haze(t):
    img = Image.fromarray(SPACE.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for x, y, b in STARS: dr.point((x, y), fill=(int(160 + 80 * b),) * 3)
    hz = ss(53.0, 58.0, t)
    sun = 1 - 0.7 * hz
    dr.ellipse((-140, 520, 120, 780), fill=mul((255, 240, 200), sun))
    for i in range(10):
        a = 0.3 * sun
        dr.line((120, 650, 120 + 500, 650 + (i - 5) * 70), fill=mul((255, 240, 200), a), width=3)
    globe(dr, GX, GY, GR, hz)
    arr = np.asarray(img, np.float32).copy()
    yy_, xx_ = np.ogrid[:H, :W]
    m = (((xx_ - GX) ** 2 + (yy_ - GY) ** 2) <= (GR + 40) ** 2).astype(np.float32)[..., None]
    arr = arr * (1 - m * 0.55 * hz) + m * 0.55 * hz * np.array([120, 105, 90])
    img = Image.fromarray(arr.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(18):
        ang = i / 18 * 2 * math.pi + t * 0.1
        r = GR + 20 + 15 * math.sin(t + i)
        rr = 50 * hz
        dr.ellipse((GX + r * math.cos(ang) - rr, GY + r * math.sin(ang) - rr * 0.6, GX + r * math.cos(ang) + rr, GY + r * math.sin(ang) + rr * 0.6), fill=mul((130, 115, 100), hz))
    put(img, L_HAZE, 540, 640, ss(53.2, 54.0, t) * (1 - ss(56.8, 57.2, t)))
    put(img, L_WINTER, 540, 640, ss(57.4, 58.2, t))
    return img

# ---------- bars ----------
L_B = [text_img(s_, FB, 36, c, 3) for s_, c in (('阳光', (255, 225, 140)), ('温度', (255, 190, 140)))]
L_DN = text_img('下降', FM, 32, (190, 210, 255), 3)
def bars(img, t, a):
    if a <= 0: return
    arr = np.asarray(img, np.float32).copy()
    arr[1300:1480, 40:1040] = arr[1300:1480, 40:1040] * (1 - 0.65 * a) + np.array([10, 14, 20]) * 0.65 * a
    img.paste(Image.fromarray(arr.astype(np.uint8))); dr = ImageDraw.Draw(img)
    vals = [0.85 - 0.75 * ss(53.0, 58.0, t), 0.7 - 0.5 * ss(56.0, 62.0, t)]
    for i, (v, c) in enumerate(zip(vals, [(250, 210, 90), (240, 130, 80)])):
        y = 1350 + i * 80
        put(img, L_B[i], 140, y, a)
        dr.rounded_rectangle((250, y - 16, 900, y + 16), radius=16, fill=mul((40, 45, 55), a))
        dr.rounded_rectangle((250, y - 16, 250 + 650 * v, y + 16), radius=16, fill=mul(c, a))
        put(img, L_DN, 965, y, a * ss(55 + i * 2, 56 + i * 2, t))

# ---------- E: food chain ----------
L_FC = [text_img(s_, FB, 38, (240, 240, 235), 3) for s_ in ('植物 · 海里的藻类', '吃植物的动物', '吃肉的动物')]
L_NOPS = text_img('没有阳光：不能光合作用', FB, 40, (255, 225, 160), 3)
L_BIG = text_img('个子越大，需要的食物越多', FB, 40, (255, 225, 170), 3)
L_ALLD = text_img('不会飞的恐龙：全部灭绝', FB, 46, (255, 150, 130), 4)
def chain(t):
    img = Image.fromarray(grad((30, 30, 36), (18, 18, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 74.0:
        cx = 540
        rows = [(1120, 820, (90, 150, 80)), (940, 560, (160, 140, 90)), (760, 300, (170, 90, 80))]
        for i, (y, w, c) in enumerate(rows):
            g = ss(62.0 + i * 3.6, 64.0 + i * 3.6, t) if t > 61.6 else 0
            g = ss(61.8, 63.0, t) if i == 0 else ss(66.0 + (i - 1) * 3.2, 67.6 + (i - 1) * 3.2, t)
            col = tuple(int(v) for v in lerp(np.array(c), np.array((70, 70, 72)), g))
            dr.polygon([(cx - w / 2, y + 70), (cx + w / 2, y + 70), (cx + w / 2 - 90, y - 90), (cx - w / 2 + 90, y - 90)], fill=col)
            put(img, L_FC[i], cx, y, 1.0)
            if g > 0.5:
                for j in range(3):
                    x = cx - w / 2 + 110 + j * (w - 220) / 2
                    dr.line((x - 30, y + 20, x + 30, y + 60), fill=mul((220, 70, 60), g), width=5)
        for y0, y1 in ((1030, 870), (850, 690)):
            dr.line((cx + 380, y0, cx + 380, y1), fill=(220, 220, 220), width=4); dr.polygon([(cx + 380, y1 - 20), (cx + 368, y1), (cx + 392, y1)], fill=(220, 220, 220))
        put(img, L_NOPS, 540, 600, ss(61.8, 62.6, t))
        return img
    put(img, L_BIG, 540, 600, ss(74.2, 75.0, t) * (1 - ss(77.8, 78.2, t)))
    if t < 78.2:
        for i, (x, s) in enumerate(((240, 1.2), (560, 0.8), (840, 0.5))):
            k = ss(75.2 + i * 0.6, 76.4 + i * 0.6, t)
            if i < 2: dino(dr, x, 1160, s, 74, 1 - 0.7 * k, run=0)
            else: shrew(dr, x, 1150, 1.0, 74, 1.0, face=-1)
            if k > 0.5 and i < 2:
                dr.line((x - 90, 760, x + 90, 1000), fill=mul((220, 70, 60), k), width=7); dr.line((x - 90, 1000, x + 90, 760), fill=mul((220, 70, 60), k), width=7)
        return img
    k = ss(78.4, 81.0, t)
    sauro(dr, 360, 1180, 1.1, 1 - 0.75 * k); dino(dr, 760, 1180, 1.2, 78, 1 - 0.75 * k, run=0)
    put(img, L_ALLD, 540, 600, ss(78.4, 79.2, t))
    return img

# ---------- F: survivors in the cold ----------
L_SM = text_img('小个子 · 什么都吃', FB, 42, (255, 235, 200), 3); L_SEEDS = text_img('躲在洞里：吃种子、虫子', FB, 40, (255, 235, 200), 3)
L_WARMB = text_img('恒定的体温：扛住寒冷', FB, 42, (255, 200, 150), 3); L_BIRD2 = text_img('鸟：恐龙唯一活下来的一支', FB, 42, (255, 235, 200), 3)
def winter(t):
    img = Image.fromarray(grad((70, 70, 78), (120, 115, 110), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1060), (W, 1040), (W, H), (0, H)], fill=(90, 85, 80))
    dr.rectangle((0, 1150, W, H), fill=(70, 55, 45))
    for i, (x, h) in enumerate(TREES[::2]): tree(dr, x + 40, 1050, h * 0.8, dead=1.0)
    for i in range(40):
        q = (t * 0.15 + i / 40) % 1
        x = (i * 113) % W + 30 * math.sin(t + i); y = lerp(480, 1050, q)
        dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(190, 185, 180))
    dr.ellipse((300, 1220, 780, 1440), fill=(40, 30, 25))
    cx, cy = 540, 1330
    warm = ss(91.2, 92.6, t)
    if warm > 0:
        for r in (170, 120):
            dr.ellipse((cx - r, cy - r * 0.5, cx + r, cy + r * 0.5), fill=mul((255, 130, 60), warm * 0.35))
    shrew(dr, cx, cy, 1.4, t if t < 88 else 88, face=-1, col=(130, 100, 80))
    for i in range(6):
        sx, sy = 400 + i * 22, 1380 + (i % 2) * 10
        dr.ellipse((sx - 7, sy - 5, sx + 7, sy + 5), fill=(200, 170, 110))
    if t > 95.0:
        bk = ss(95.4, 96.2, t)
        bird(dr, lerp(1150, TREES[4][0] + 100, ss(95.4, 97.0, t)), 1050 - TREES[4][1] * 0.8 * 0.6 - 10, 1.6, t if t < 97 else 97, bk)
    put(img, L_SM, 540, 620, ss(82.8, 83.6, t) * (1 - ss(86.6, 87.0, t)))
    put(img, L_SEEDS, 540, 620, ss(87.0, 87.8, t) * (1 - ss(90.8, 91.2, t)))
    put(img, L_WARMB, 540, 620, ss(91.2, 92.0, t) * (1 - ss(95.0, 95.4, t)))
    put(img, L_BIRD2, 540, 620, ss(95.6, 96.4, t))
    return img

# ---------- G: iridium evidence ----------
L_Q = text_img('怎么知道的？', FB, 52, (255, 225, 160), 4)
L_IR = text_img('一层薄薄的黏土：铱层', FB, 40, (255, 225, 160), 3)
L_BELOW = text_img('下面：有恐龙化石', FM, 34, (235, 230, 220), 3); L_ABOVE = text_img('上面：没有', FM, 34, (235, 230, 220), 3)
L_CRUST = text_img('地壳', FB, 38, (235, 235, 240), 3); L_ASTR = text_img('小行星', FB, 38, (255, 210, 160), 3)
L_IRC = text_img('铱的含量', FM, 34, (240, 240, 240), 3)
def iridium(t):
    img = Image.fromarray(grad((40, 46, 56), (24, 28, 36)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 108.0:
        for y0, y1, c in ((720, 900, (190, 160, 120)), (900, 916, (60, 50, 45)), (916, 1260, (165, 140, 105))):
            dr.rectangle((80, y0, 1000, y1), fill=c)
        hl = ss(104.2, 105.2, t) * (0.6 + 0.4 * math.sin(t * 4))
        dr.rectangle((80, 896, 1000, 920), outline=mul((255, 225, 160), hl), width=4)
        for i in range(4):
            x = 200 + i * 220; dr.line((x - 40, 1100, x + 40, 1080), fill=(235, 230, 215), width=10)
            dr.ellipse((x - 52, 1088, x - 32, 1108), fill=(235, 230, 215)); dr.ellipse((x + 32, 1072, x + 52, 1092), fill=(235, 230, 215))
        put(img, L_Q, 540, 600, ss(99.8, 100.6, t) * (1 - ss(103.6, 104.0, t)))
        put(img, L_IR, 540, 600, ss(104.2, 105.0, t))
        put(img, L_BELOW, 540, 1300, ss(105.0, 105.8, t)); put(img, L_ABOVE, 540, 680, 0)
        return img
    put(img, L_IRC, 540, 600, ss(108.2, 109.0, t))
    k = ss(108.6, 110.6, t)
    dr.line((200, 1240, 880, 1240), fill=(200, 200, 210), width=3)
    dr.rectangle((300, 1240 - 20, 440, 1240), fill=(160, 170, 180))
    dr.rectangle((640, 1240 - 520 * k, 780, 1240), fill=(255, 190, 110))
    put(img, L_CRUST, 370, 1300, 1.0); put(img, L_ASTR, 710, 1300, 1.0)
    return img

# ---------- H: dawn ----------
L_DAWN = text_img('恐龙让出了白天', FB, 46, (255, 235, 200), 4)
L_GROW = text_img('几百万年：哺乳动物变大、变多', FB, 40, (255, 235, 200), 3)
L_CLIMB = text_img('其中一支，爬上了树', FB, 42, (255, 225, 160), 3)
def climber(dr, x, y, s, t, a=1.0):
    c = (140, 105, 80)
    dr.ellipse((x - 26 * s, y - 50 * s, x + 26 * s, y + 50 * s), fill=mul(c, a))
    dr.ellipse((x - 26 * s, y - 92 * s, x + 26 * s, y - 44 * s), fill=mul(c, a))
    dr.ellipse((x + 2 * s, y - 80 * s, x + 16 * s, y - 64 * s), fill=mul((250, 240, 200), a)); dr.ellipse((x + 6 * s, y - 76 * s, x + 12 * s, y - 68 * s), fill=mul((20, 20, 20), a))
    ph = math.sin(t * 5)
    for sg in (-1, 1):
        dr.line((x, y - 20 * s, x + 30 * s, y - 40 * s + 14 * s * ph * sg), fill=mul(c, a), width=int(10 * s))
        dr.line((x, y + 30 * s, x + 30 * s, y + 46 * s - 14 * s * ph * sg), fill=mul(c, a), width=int(10 * s))
    dr.line((x - 10 * s, y + 40 * s, x - 50 * s, y + 140 * s), fill=mul(c, a), width=int(8 * s))
def dawn(t):
    k = ss(112.4, 116.0, t)
    img = Image.fromarray((grad((120, 120, 130), (150, 140, 130), 480, 1100) * (1 - k) + grad((110, 170, 220), (250, 220, 170), 480, 1100) * k).astype(np.uint8)); dr = ImageDraw.Draw(img)
    sy = lerp(1150, 620, ss(112.6, 117.0, t))
    dr.ellipse((760 - 70, sy - 70, 760 + 70, sy + 70), fill=(255, 235, 180))
    dr.polygon([(0, 1120), (W, 1100), (W, H), (0, H)], fill=tuple(int(v) for v in lerp(np.array([90, 85, 80]), np.array([110, 150, 80]), k)))
    for i, (x, h) in enumerate(TREES[::2]): tree(dr, x + 40, 1110, h * 0.9, dead=1 - k)
    for i, s in enumerate((0.6, 0.9, 1.3)):
        a = ss(116.8 + i * 0.8, 117.6 + i * 0.8, t)
        if a > 0: shrew(dr, 260 + i * 230, 1180, s, t, a, face=1, col=(150, 120, 90))
    if t > 120.6:
        tx = TREES[4][0] + 40
        cy_ = lerp(1080, 820, ss(121.0, 124.5, t)) if t < 126 else 820 + 6 * math.sin(t * 2)
        climber(dr, tx - 22, cy_, 1.2, t if t < 124.5 else 124.5, ss(120.8, 121.6, t))
    put(img, L_DAWN, 540, 640, ss(112.6, 113.4, t) * (1 - ss(116.4, 116.8, t)))
    put(img, L_GROW, 540, 640, ss(116.8, 117.6, t) * (1 - ss(120.6, 121.0, t)))
    put(img, L_CLIMB, 540, 640, ss(121.0, 121.8, t) * (1 - ss(125.6, 126.0, t)))
    return img

def render(t):
    if t < 6.0: return render16(136.5 + t)
    if t < 19.0: return dim(cretaceous(t), ss(6.0, 6.6, t) * (1 - ss(18.4, 19.0, t)))
    if t < 40.2:
        k = ss(19.0, 19.6, t) * (1 - ss(39.6, 40.2, t))
        for a in (22.8, 27.0, 31.2, 35.4):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(space(t), k)
    if t < 52.8:
        k = ss(40.2, 40.8, t) * (1 - ss(52.2, 52.8, t))
        if 48.2 < t < 49.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 48.2) / 0.8)
        return dim(fire(t), k)
    if t < 61.4: img = dim(haze(t), ss(52.8, 53.4, t) * (1 - ss(60.8, 61.4, t)))
    elif t < 82.6:
        k = ss(61.4, 62.0, t) * (1 - ss(82.0, 82.6, t))
        for a in (73.6, 77.8):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        img = dim(chain(t), k)
    elif t < 99.6: return dim(winter(t), ss(82.6, 83.2, t) * (1 - ss(99.0, 99.6, t)))
    elif t < 112.4:
        k = ss(99.6, 100.2, t) * (1 - ss(111.8, 112.4, t))
        if 107.6 < t < 108.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 107.6) / 0.8)
        return dim(iridium(t), k)
    else: return dim(dawn(t), ss(112.4, 113.0, t))
    if 54.6 < t < 82.6:
        k = ss(54.6, 55.4, t) * (1 - ss(81.8, 82.4, t))
        if 60.8 < t < 62.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 60.8) / 1.2)
        bars(img, t, k)
    return img

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep17_{ts}.png')
