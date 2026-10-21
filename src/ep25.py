import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep17 import globe, SPACE, STARS
from ep21 import DARK
from ep22 import sapiens
from ep23 import world, P, OCEAN
from ep24 import person, SKINS, render as render24

CLEAN = False
rng = np.random.default_rng(251)
SKY = grad((140, 185, 220), (240, 230, 195), 480, 1100)
GOLD = (215, 180, 90)

def wheat(dr, x, y, h, s, sway, shatter=0.0, mutant=False, a=1.0):
    tx = x + sway * 20 * s
    dr.line((x, y, tx, y - h), fill=mul((170, 150, 70), a), width=max(2, int(3 * s)))
    for j in range(7):
        gy = y - h + j * 12 * s
        for sg in (-1, 1):
            gx = tx + sg * 7 * s
            fall = 0 if mutant else shatter * (1 + j * 0.3) * 120 * s
            dr.ellipse((gx - 5 * s, gy - 8 * s + fall, gx + 5 * s, gy + 8 * s + fall), fill=mul((225, 190, 100) if not mutant else (240, 205, 110), a))
def field(dr, t, n=60, y0=1160, h=150, s=1.0, shatter=0.0):
    for i in range(n):
        x = (i * 37 + (i % 3) * 11) % W
        wheat(dr, x, y0 + (i % 4) * 20, h + (i % 5) * 12, s, math.sin(t * 1.5 + i * 0.7) * 0.4, shatter)
def hut(dr, x, y, s):
    dr.rectangle((x - 60 * s, y - 70 * s, x + 60 * s, y), fill=(160, 120, 80))
    dr.polygon([(x - 80 * s, y - 70 * s), (x, y - 140 * s), (x + 80 * s, y - 70 * s)], fill=(190, 160, 90))
    dr.rectangle((x - 14 * s, y - 40 * s, x + 14 * s, y), fill=(80, 55, 35))

# ---------- A: foragers ----------
L_BAND = text_img('几十人一群，四处采集打猎', FB, 40, (255, 235, 200), 3)
def foragers(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(165, 150, 100))
    for i in range(7):
        x = lerp(-200, 1200, ((t - 6) * 0.08 + i * 0.07) % 1.4 / 1.4) if False else lerp(-150 + i * 60, 700 + i * 60, ss(6.2, 14.6, t))
        sapiens(dr, x, GROUND + 30 + (i % 2) * 30, 0.9 if i % 3 else 0.6, col=SKINS[i % 5])
    put(img, L_BAND, 540, 640, ss(10.8, 11.6, t))
    return img

# ---------- B: ice ends, climate steadies ----------
L_END = text_img('最后一次冰期结束', FB, 44, (220, 235, 255), 3)
L_STEADY = text_img('气候第一次稳定了上千年', FB, 42, (255, 225, 160), 3)
L_AXIS = text_img('气温', FM, 32, (220, 220, 230), 3); L_NOW = text_img('1.17 万年前', FM, 30, (255, 225, 160), 3)
def climate(t):
    img = Image.fromarray(SPACE.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 19.2:
        for x, y, b in STARS: dr.point((x, y), fill=(int(160 + 80 * b),) * 3)
        globe(dr, 600, 1080, 360)
        ik = 1 - ss(15.4, 18.6, t)
        cy = 1080 - 360 + 30
        dr.chord((600 - 300 * (0.3 + 0.7 * ik), cy - 40 - 120 * ik, 600 + 300 * (0.3 + 0.7 * ik), cy + 40 + 120 * ik), 0, 360, fill=(240, 248, 255))
        put(img, L_END, 540, 600, ss(15.4, 16.2, t))
        return img
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    x0, x1, yc = 100, 980, 1050
    dr.line((x0, 1300, x1, 1300), fill=(160, 160, 170), width=3); dr.line((x0, 760, x0, 1300), fill=(160, 160, 170), width=3)
    put(img, L_AXIS, x0 + 40, 740, 1.0)
    k = ss(19.4, 22.4, t); xs = 640
    pts = []
    for i in range(200):
        x = x0 + (x1 - x0) * i / 199
        if x > x0 + (x1 - x0) * k: break
        if x < xs: y = yc + 120 * math.sin(i * 0.9) * math.cos(i * 0.31) + 60 * math.sin(i * 2.3)
        else: y = yc - 120 + 8 * math.sin(i * 0.7)
        pts.append((x, y))
    if len(pts) > 1: dr.line(pts, fill=(255, 190, 110), width=4)
    dr.line((xs, 760, xs, 1300), fill=(255, 225, 160), width=2)
    put(img, L_NOW, xs, 1340, ss(20.4, 21.0, t))
    put(img, L_STEADY, 540, 600, ss(20.8, 21.6, t))
    return img

# ---------- C: where the wild grains grew ----------
L_FC = text_img('新月沃地：野生小麦、大麦', FB, 34, (255, 225, 160), 3)
L_CN = text_img('长江：野生稻 · 黄河：野生小米', FB, 34, (255, 225, 160), 3)
def wildmap(t, labels2=False):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr)
    for (p, t0, lab, ly) in (((0.25, 0.36), 23.6, L_FC, 0.27), ((0.52, 0.34), 27.8, L_CN, 0.44)):
        a = ss(t0, t0 + 0.8, t)
        if a <= 0: continue
        x, y = P(*p)
        r = 26 + 6 * math.sin(t * 3)
        dr.ellipse((x - r, y - r, x + r, y + r), outline=mul((255, 210, 120), a), width=4)
        dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=mul((255, 225, 160), a))
        put(img, lab, *P(p[0], ly), a)
    return img

# ---------- D: staying put ----------
L_STAY = text_img('在丰收的地方，一待就是几个月', FB, 40, (255, 235, 200), 3)
L_HOME = text_img('营地，变成了固定的家', FB, 42, (255, 225, 160), 3)
def wildfield(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 20, W, H), fill=(190, 165, 95))
    hk = ss(40.6, 42.6, t)
    for i, x in enumerate((180, 420, 880)):
        if hk > i / 3: hut(dr, x, GROUND - 10, 0.9)
    field(dr, t, n=46, y0=GROUND + 120, h=170)
    for i in range(4):
        x = 250 + i * 190; y = GROUND + 260
        sapiens(dr, x, y, 0.8, col=SKINS[i % 5])
        dr.ellipse((x + 20, y - 80, x + 70, y - 40), fill=(170, 130, 80))
    put(img, L_STAY, 540, 600, ss(36.4, 37.2, t) * (1 - ss(40.2, 40.6, t)))
    put(img, L_HOME, 540, 600, ss(40.6, 41.4, t))
    return img

# ---------- E: domestication ----------
L_WILD = text_img('野生：穗裂开，种子掉一地', FM, 34, (230, 230, 235), 3)
L_MUT = text_img('变异：种子牢牢长在穗上', FM, 34, (255, 225, 160), 3)
L_HARV = text_img('收割时，带走的正好是不掉粒的', FB, 38, (255, 235, 200), 3)
L_NEXT = text_img('第二年：不掉粒的越来越多', FB, 40, (255, 235, 200), 3)
L_DOM = text_img('驯化：人和植物一代代互相挑选', FB, 40, (255, 225, 160), 3)
def domest(t):
    img = Image.fromarray(grad((60, 70, 60), (30, 36, 30)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 53.2:
        sh = ss(45.4, 47.8, t)
        wheat(dr, 330, 1320, 520, 3.0, 0.0, sh)
        if t > 49.0: wheat(dr, 750, 1320, 520, 3.0, 0.0, 0.0, mutant=True, a=ss(49.2, 50.0, t))
        put(img, L_WILD, 330, 1380, ss(45.0, 45.8, t)); put(img, L_MUT, 750, 1380, ss(49.2, 50.0, t))
        return img
    if t < 61.6:
        img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.rectangle((0, GROUND - 20, W, H), fill=(170, 140, 85))
        frac = 0.08 if t < 57.4 else lerp(0.08, 0.6, ss(57.6, 60.4, t))
        for i in range(48):
            x = 20 + (i * 47) % 1040; y = GROUND + 120 + (i % 4) * 40
            m = ((i * 0.618) % 1) < frac
            wheat(dr, x, y, 160, 1.0, math.sin(t + i) * 0.3, 0.0 if m else 0.5, mutant=m)
        if t < 57.4:
            sapiens(dr, lerp(100, 900, ss(53.4, 57.0, t)), GROUND + 330, 1.0, col=SKINS[1])
            put(img, L_HARV, 540, 600, ss(53.4, 54.2, t))
        else:
            put(img, L_NEXT, 540, 600, ss(57.6, 58.4, t))
        return img
    put(img, L_DOM, 540, 600, ss(61.8, 62.6, t))
    for g in range(6):
        k = ss(62.2 + g * 0.5, 62.8 + g * 0.5, t)
        v = [0.05, 0.15, 0.35, 0.6, 0.8, 0.95][g]
        x = 140 + g * 160
        dr.rectangle((x - 40, 1300 - 500 * v * k, x + 40, 1300), fill=(240, 205, 110))
        dr.rectangle((x - 40, 1300 - 500, x + 40, 1300), outline=(150, 150, 160), width=2)
    return img

# ---------- F: independent origins ----------
L_T = [text_img(s_, FB, 32, (255, 225, 160), 3) for s_ in ('1.1 万年前 · 麦子', '1 万年前 · 稻、小米', '山羊 · 绵羊 · 猪')]
def origins(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr)
    for p, t0, lab, lp in (((0.25, 0.36), 66.2, L_T[0], (0.20, 0.28)), ((0.52, 0.34), 70.4, L_T[1], (0.52, 0.44)), ((0.27, 0.32), 74.6, L_T[2], (0.30, 0.20))):
        a = ss(t0, t0 + 0.8, t)
        if a <= 0: continue
        x, y = P(*p)
        for r in (30, 60, 90):
            rr = r + 10 * math.sin(t * 2 + r)
            dr.ellipse((x - rr, y - rr, x + rr, y + rr), outline=mul((240, 205, 110), a * (1 - r / 120)), width=3)
        dr.ellipse((x - 12, y - 12, x + 12, y + 12), fill=mul((255, 225, 160), a))
        put(img, lab, *P(*lp), a)
    return img

# ---------- G: Göbekli Tepe ----------
L_GT = text_img('哥贝克力石阵 · 比农业还早', FB, 40, (255, 225, 160), 3)
L_GATHER = text_img('为了共同的信仰，聚在一起', FB, 40, (255, 235, 200), 3)
L_FEED = text_img('养活这么多人：可能推动了种粮食', FB, 38, (255, 235, 200), 3)
def pillar(dr, x, y, s, a=1.0):
    c = mul((150, 128, 100), a)
    dr.rectangle((x - 22 * s, y - 220 * s, x + 22 * s, y), fill=c)
    dr.rectangle((x - 60 * s, y - 260 * s, x + 60 * s, y - 210 * s), fill=c)
    dr.ellipse((x - 14 * s, y - 160 * s, x + 14 * s, y - 120 * s), outline=mul((90, 75, 58), a), width=3)
    dr.line((x - 12 * s, y - 90 * s, x + 12 * s, y - 70 * s), fill=mul((90, 75, 58), a), width=3)
def gobekli(t):
    img = Image.fromarray(grad((170, 160, 150), (235, 210, 170), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 30, W, H), fill=(185, 160, 120))
    for i in range(8):
        a_ = i / 8 * 2 * math.pi
        x = 540 + 340 * math.cos(a_); y = 1200 + 110 * math.sin(a_)
        if y < 1200: pillar(dr, x, y, 0.9 + 0.2 * (y - 1090) / 220)
    pillar(dr, 470, 1230, 1.4); pillar(dr, 610, 1230, 1.4)
    for i in range(8):
        a_ = i / 8 * 2 * math.pi
        x = 540 + 340 * math.cos(a_); y = 1200 + 110 * math.sin(a_)
        if y >= 1200: pillar(dr, x, y, 0.9 + 0.2 * (y - 1090) / 220)
    if t > 83.0:
        n = int(16 * ss(83.2, 85.6, t))
        for i in range(n):
            x = 100 + (i * 137) % 880; y = 1400 + (i % 3) * 60
            person(dr, x, y, 1.1, SKINS[i % 5])
    if t > 87.2:
        for i in range(5):
            x = 180 + i * 180; dr.ellipse((x - 40, 1520, x + 40, 1570), fill=(170, 130, 80)); dr.ellipse((x - 34, 1510, x + 34, 1530), fill=GOLD)
    put(img, L_GT, 540, 600, ss(79.0, 79.8, t) * (1 - ss(82.8, 83.2, t)))
    put(img, L_GATHER, 540, 600, ss(83.2, 84.0, t) * (1 - ss(87.0, 87.4, t)))
    put(img, L_FEED, 540, 600, ss(87.4, 88.2, t))
    return img

# ---------- H: the farming trap ----------
L_HARD = text_img('更累，吃得更单一', FB, 42, (255, 225, 190), 3)
L_BONES = text_img('骨骼：个子变矮，蛀牙变多', FB, 40, (255, 225, 190), 3)
L_MORE = text_img('同一块地：多养活几十倍的人', FB, 40, (255, 225, 160), 3)
L_TRAP = text_img('人口一多，就回不去了', FB, 44, (255, 200, 170), 3)
L_FOR = text_img('采集', FB, 36, (230, 230, 235), 3); L_FARM = text_img('种田', FB, 36, (255, 225, 160), 3)
def trap(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 100.0:
        if t < 95.8:
            img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
            dr.rectangle((0, GROUND, W, H), fill=(150, 120, 75))
            for j in range(6): dr.line((0, GROUND + 40 + j * 60, W, GROUND + 40 + j * 60), fill=(130, 100, 60), width=6)
            for i, x in enumerate((300, 640)):
                bend = 0.5 + 0.5 * math.sin(t * 2 + i)
                hx, hy = x, GROUND + 60
                dr.line((hx, hy, hx + 10, hy - 110), fill=SKINS[i], width=22)
                dr.line((hx + 10, hy - 110, hx + 90, hy - 110 + 40 * bend), fill=SKINS[i], width=28)
                dr.ellipse((hx + 80, hy - 120 + 40 * bend, hx + 130, hy - 70 + 40 * bend), fill=SKINS[i])
                dr.line((hx + 100, hy - 80 + 40 * bend, hx + 100, hy + 10), fill=SKINS[i], width=10)
            put(img, L_HARD, 540, 600, ss(91.8, 92.6, t))
            return img
        for i, (h, c, lab) in enumerate(((600, (200, 200, 210), L_FOR), (520, (240, 190, 100), L_FARM))):
            x = 320 + i * 440
            dr.line((x, 1350, x, 1350 - h), fill=c, width=40)
            dr.ellipse((x - 40, 1350 - h - 80, x + 40, 1350 - h), outline=c, width=6)
            put(img, lab, x, 1400, 1.0)
        for j in range(5):
            x = 690 + j * 40; dr.rectangle((x, 1460, x + 28, 1500), fill=(240, 235, 220))
            if j in (1, 3): dr.ellipse((x + 6, 1468, x + 20, 1482), fill=(90, 70, 50))
        put(img, L_BONES, 540, 600, ss(96.0, 96.8, t))
        return img
    if t < 104.4:
        for i, (n, x0, lab) in enumerate(((6, 120, L_FOR), (120, 580, L_FARM))):
            dr.rectangle((x0, 800, x0 + 380, 1180), outline=(200, 200, 210), width=3)
            for j in range(int(n * ss(100.2 + i * 0.6, 101.6 + i * 0.6, t))):
                x = x0 + 20 + (j * 37) % 340; y = 820 + (j * 53) % 340
                dr.ellipse((x - 6, y - 6, x + 6, y + 6), fill=SKINS[j % 5])
            put(img, lab, x0 + 190, 1230, 1.0)
        put(img, L_MORE, 540, 600, ss(100.2, 101.0, t))
        return img
    k = ss(104.6, 106.4, t)
    dr.line((200, 1050, 880, 1050), fill=(255, 210, 120), width=8); dr.polygon([(880, 1030), (920, 1050), (880, 1070)], fill=(255, 210, 120))
    put(img, L_FOR, 200, 990, 1.0); put(img, L_FARM, 880, 990, 1.0)
    if k > 0:
        dr.line((880, 1130, lerp(880, 400, k), 1130), fill=(150, 150, 160), width=6)
        if k > 0.9:
            dr.line((370, 1100, 430, 1160), fill=(230, 80, 70), width=8); dr.line((370, 1160, 430, 1100), fill=(230, 80, 70), width=8)
    put(img, L_TRAP, 540, 600, ss(104.6, 105.4, t))
    return img

# ---------- I: why, and storage ----------
L_WHY = text_img('为什么偏偏这时开始种地？', FB, 42, (255, 225, 160), 3)
L_REASONS = [text_img(s_, FB, 40, (240, 240, 245), 3) for s_ in ('气候稳定', '人口压力', '聚会与信仰')]
L_DEB = text_img('都有证据，仍在讨论', FB, 40, (255, 235, 200), 3)
L_STORE = text_img('吃不完的粮食，要存起来', FB, 42, (255, 225, 160), 3)
L_PROB = text_img('存粮，带来了新的问题', FB, 42, (255, 200, 170), 3)
def why(t):
    if t < 117.2:
        img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
        put(img, L_WHY, 540, 600, ss(108.8, 109.6, t))
        for i, lab in enumerate(L_REASONS):
            a = ss(109.6 + i * 1.2, 110.4 + i * 1.2, t)
            x = 540; y = 840 + i * 190
            if a > 0:
                dr.rounded_rectangle((x - 260, y - 64, x + 260, y + 64), radius=24, fill=mul((36, 40, 52), a), outline=mul((255, 210, 130), a), width=3)
                put(img, lab, x, y, a)
        put(img, L_DEB, 540, 1450, ss(113.0, 113.8, t))
        return img
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(185, 160, 95))
    for i, x in enumerate((140, 360, 760, 960)): hut(dr, x, GROUND + 20, 0.9)
    gx, gy = 560, GROUND + 60
    dr.rounded_rectangle((gx - 90, gy - 220, gx + 90, gy), radius=50, fill=(170, 130, 80))
    dr.polygon([(gx - 110, gy - 200), (gx, gy - 300), (gx + 110, gy - 200)], fill=(200, 170, 100))
    fill_ = ss(117.6, 120.4, t)
    dr.rectangle((gx - 60, gy - 20 - 160 * fill_, gx + 60, gy - 20), fill=GOLD)
    if t > 121.4:
        k = ss(121.6, 123.0, t)
        sapiens(dr, gx + 170, GROUND + 140, 1.1, col=SKINS[2])
        sapiens(dr, lerp(1200, 900, k), GROUND + 140, 1.1, col=(60, 50, 50))
    put(img, L_STORE, 540, 600, ss(117.4, 118.2, t) * (1 - ss(121.2, 121.6, t)))
    put(img, L_PROB, 540, 600, ss(121.6, 122.4, t))
    return img

def render(t):
    if t < 6.0: return render24(137.7 + t)
    if t < 15.0: return dim(foragers(t), ss(6.0, 6.6, t) * (1 - ss(14.4, 15.0, t)))
    if t < 23.4:
        k = ss(15.0, 15.6, t) * (1 - ss(22.8, 23.4, t))
        if 18.8 < t < 19.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 18.8) / 0.8)
        return dim(climate(t), k)
    if t < 32.0: return dim(wildmap(t), ss(23.4, 24.0, t) * (1 - ss(31.4, 32.0, t)))
    if t < 44.8: return dim(wildfield(t), ss(32.0, 32.6, t) * (1 - ss(44.2, 44.8, t)))
    if t < 66.0:
        k = ss(44.8, 45.4, t) * (1 - ss(65.4, 66.0, t))
        for a in (52.8, 61.2):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(domest(t), k)
    if t < 78.8: return dim(origins(t), ss(66.0, 66.6, t) * (1 - ss(78.2, 78.8, t)))
    if t < 91.6: return dim(gobekli(t), ss(78.8, 79.4, t) * (1 - ss(91.0, 91.6, t)))
    if t < 108.6:
        k = ss(91.6, 92.2, t) * (1 - ss(108.0, 108.6, t))
        for a in (95.4, 99.6, 104.0):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(trap(t), k)
    k = ss(108.6, 109.2, t)
    if 116.8 < t < 117.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 116.8) / 0.8)
    return dim(why(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep25_{ts}.png')
