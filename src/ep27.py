import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK
from ep22 import sapiens
from ep24 import person, SKINS
from ep25 import hut, SKY, GOLD
from ep26 import sack, granary, render as render26

CLEAN = False
CLAY = (190, 150, 110); CLAY_D = (120, 85, 60)
DESERT = grad((150, 190, 215), (240, 220, 175), 480, 1100)

def tablet(dr, x, y, w, h, a=1.0):
    dr.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), radius=int(min(w, h) * 0.12), fill=mul(CLAY, a), outline=mul(CLAY_D, a), width=3)
def wedge(dr, x, y, s, ang, a=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(x, y), (x + 26 * s * ca - 8 * s * sa, y + 26 * s * sa + 8 * s * ca), (x + 26 * s * ca + 8 * s * sa, y + 26 * s * sa - 8 * s * ca)]
    dr.polygon(pts, fill=mul(CLAY_D, a))
def cone(dr, x, y, s, a=1.0):
    dr.polygon([(x, y - 40 * s), (x - 24 * s, y + 20 * s), (x + 24 * s, y + 20 * s)], fill=mul(CLAY, a), outline=mul(CLAY_D, a))
def ball(dr, x, y, s, a=1.0):
    dr.ellipse((x - 24 * s, y - 24 * s, x + 24 * s, y + 24 * s), fill=mul(CLAY, a), outline=mul(CLAY_D, a), width=2)
def wheat_glyph(dr, x, y, s, a=1.0):
    dr.line((x, y + 40 * s, x, y - 40 * s), fill=mul(CLAY_D, a), width=int(4 * s))
    for j in range(4):
        for sg in (-1, 1): dr.line((x, y - 30 * s + j * 16 * s, x + sg * 16 * s, y - 40 * s + j * 16 * s), fill=mul(CLAY_D, a), width=int(3 * s))

# ---------- B: Mesopotamia ----------
L_MESO = text_img('两河流域：土地肥沃，却很少下雨', FB, 38, (255, 235, 200), 3)
L_CANAL = text_img('挖渠引水：许多村子必须一起干', FB, 38, (255, 225, 160), 3)
L_RIV = [text_img(s_, FM, 32, (200, 230, 255), 3) for s_ in ('幼发拉底河', '底格里斯河')]
def meso(t):
    img = Image.fromarray(grad((205, 185, 140), (180, 160, 120)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i, x0 in enumerate((260, 760)):
        pts = [(x0 + 90 * math.sin(y / 160 + i) + (y - 600) * 0.25 * (1 if i == 0 else -0.6), y) for y in range(560, 1560, 20)]
        dr.line(pts, fill=(70, 130, 180), width=22)
        put(img, L_RIV[i], pts[3][0] + (90 if i == 0 else -90), 640, 1.0)
    ck = ss(15.0, 18.6, t)
    for j in range(8):
        y = 820 + j * 85
        xl = 260 + 90 * math.sin(y / 160) + (y - 600) * 0.25; xr = 760 + 90 * math.sin(y / 160 + 1) - (y - 600) * 0.15
        L = (xr - xl) * min(1, ck * 1.5 - j * 0.1)
        if L > 0:
            dr.line((xl, y, xl + L, y), fill=(90, 150, 200), width=6)
            for k in range(3):
                fx = xl + 60 + k * (xr - xl - 120) / 2
                if fx < xl + L: dr.rectangle((fx - 30, y + 10, fx + 30, y + 40), fill=(130, 165, 80))
    if t > 15.0:
        for j in range(5):
            x = 380 + j * 70; y = 740 + (j % 2) * 30
            person(dr, x, y, 0.9, SKINS[j % 5])
    put(img, L_MESO, 540, 560, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_CANAL, 540, 560, ss(15.0, 15.8, t))
    return img

# ---------- C: tokens -> envelope -> tablet ----------
L_TOK = text_img('陶筹：用小泥块代表货物', FB, 40, (255, 225, 160), 3)
L_C = text_img('一份粮', FM, 34, (240, 235, 220), 3); L_B = text_img('一只羊', FM, 34, (240, 235, 220), 3)
L_ENV = text_img('封进泥球，外面按出记号', FB, 40, (255, 235, 200), 3)
L_ENOUGH = text_img('只看记号，就够了', FB, 42, (255, 225, 160), 3)
L_TAB = text_img('泥板：数字 + 图形', FB, 42, (255, 225, 160), 3)
def tokens(t):
    img = Image.fromarray(grad((60, 48, 40), (34, 26, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 27.6:
        for i in range(3): cone(dr, 260 + i * 70, 1050, 1.4)
        for i in range(2): ball(dr, 700 + i * 80, 1060, 1.4)
        put(img, L_C, 330, 1160, ss(23.4, 24.2, t)); put(img, L_B, 740, 1160, ss(24.2, 25.0, t))
        put(img, L_TOK, 540, 640, ss(19.2, 20.0, t))
        return img
    if t < 40.4:
        cx, cy = 540, 1040
        ek = ss(27.8, 29.6, t); cr = ss(36.2, 37.4, t)
        if ek < 1:
            for i in range(3): cone(dr, lerp(380 + i * 70, cx - 60 + i * 50, ek), 1050, 1.2)
            for i in range(2): ball(dr, lerp(700 + i * 80, cx - 20 + i * 50, ek), 1060, 1.2)
        R = 190
        if ek > 0.3:
            dr.ellipse((cx - R, cy - R, cx + R, cy + R), fill=mul(CLAY, ss(0.3, 1.0, ek)), outline=mul(CLAY_D, ss(0.3, 1.0, ek)), width=4)
        mk = ss(32.0, 34.0, t)
        for i in range(3):
            if mk > i / 5: dr.polygon([(cx - 120 + i * 50, cy - 70), (cx - 140 + i * 50, cy - 20), (cx - 100 + i * 50, cy - 20)], fill=CLAY_D)
        for i in range(2):
            if mk > (3 + i) / 5: dr.ellipse((cx + 40 + i * 60 - 20, cy - 65, cx + 40 + i * 60 + 20, cy - 25), fill=CLAY_D)
        if cr > 0:
            dr.line((cx - 30, cy + 20, cx + 10, cy + 80, cx - 20, cy + 150), fill=(40, 30, 25), width=int(3 + 6 * cr))
        put(img, L_ENV, 540, 640, ss(28.0, 28.8, t) * (1 - ss(35.8, 36.2, t)))
        put(img, L_ENOUGH, 540, 640, ss(36.2, 37.0, t))
        return img
    tablet(dr, 540, 1040, 560, 400)
    k = ss(40.8, 43.6, t)
    for i in range(int(5 * k)):
        wedge(dr, 330 + i * 46, 930, 1.4, math.pi / 2)
    if t > 44.6:
        a = ss(44.8, 45.8, t)
        wheat_glyph(dr, 640, 1060, 2.0, a)
        for i in range(3): dr.ellipse((380 + i * 50 - 16, 1100 - 16, 380 + i * 50 + 16, 1100 + 16), outline=mul(CLAY_D, a), width=5)
    put(img, L_TAB, 540, 640, ss(40.8, 41.6, t))
    return img

# ---------- D: cuneiform, hieroglyphs, oracle bones ----------
L_SCRIBE = text_img('乌鲁克的书吏：芦苇笔压出楔形笔画', FB, 38, (255, 235, 200), 3)
L_CUNE = text_img('楔形文字：最早的文字，大多是账本', FB, 38, (255, 225, 160), 3)
L_EGY = text_img('埃及 · 象形文字', FB, 42, (255, 225, 160), 3)
L_ORA = text_img('商朝 · 甲骨文', FB, 42, (255, 225, 160), 3)
L_GLY = text_img('羊  牛  田  人', FM, 46, (90, 60, 40), 0)
def scripts(t):
    img = Image.fromarray(grad((60, 48, 40), (34, 26, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 61.8:
        tablet(dr, 540, 1060, 640, 520)
        n = int(48 * ss(53.4, 60.0, t))
        for i in range(n):
            r, c = divmod(i, 8)
            x = 280 + c * 70; y = 870 + r * 70
            wedge(dr, x, y, 1.1, (i * 1.3) % 3.0)
        if 53.2 < t < 61.0:
            px = 280 + (n % 8) * 70; py = 870 + (n // 8) * 70
            dr.line((px + 10, py - 10, px + 160, py - 220), fill=(170, 150, 90), width=12)
        put(img, L_SCRIBE, 540, 640, ss(49.2, 50.0, t) * (1 - ss(57.2, 57.6, t)))
        put(img, L_CUNE, 540, 640, ss(57.6, 58.4, t))
        return img
    if t < 66.0:
        img = Image.fromarray(grad((220, 200, 150), (190, 165, 120)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.rectangle((240, 780, 840, 1340), fill=(225, 205, 160), outline=(150, 120, 80), width=4)
        x, y = 380, 900
        dr.ellipse((x - 50, y - 24, x + 50, y + 24), outline=(60, 50, 40), width=6); dr.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(60, 50, 40))
        dr.polygon([(620, 860), (700, 900), (650, 960), (600, 950)], fill=(60, 50, 40)); dr.line((650, 960, 640, 1000), fill=(60, 50, 40), width=6)
        for j in range(4): dr.arc((300 + j * 60, 1080, 360 + j * 60, 1130), 180, 360, fill=(40, 90, 150), width=6)
        dr.rectangle((620, 1060, 720, 1240), outline=(60, 50, 40), width=6)
        put(img, L_EGY, 540, 640, ss(62.0, 62.8, t))
        return img
    dr.polygon([(300, 820), (800, 800), (860, 1080), (760, 1340), (340, 1360), (240, 1100)], fill=(225, 205, 165), outline=(170, 150, 110))
    for j in range(5): dr.line((360 + j * 90, 860, 380 + j * 90, 900, 360 + j * 90, 930), fill=(150, 110, 70), width=3)
    put(img, L_GLY, 550, 1120, ss(66.4, 67.4, t))
    put(img, L_ORA, 540, 640, ss(66.2, 67.0, t))
    return img

# ---------- E: Uruk ----------
L_CITY = text_img('乌鲁克：住着几万人', FB, 42, (255, 225, 160), 3)
L_TEMPLE = text_img('神庙：存粮、分配劳力、管理水渠', FB, 38, (255, 235, 200), 3)
L_REC = text_img('城市需要记录', FB, 42, (255, 225, 160), 3)
L_BIGGER = text_img('记录，让城市管得更大', FB, 42, (255, 225, 160), 3)
def uruk(t):
    img = Image.fromarray(DESERT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 40, W, H), fill=(200, 175, 125))
    grow = ss(83.2, 86.4, t)
    n = int(14 + 18 * grow)
    for i in range(n):
        x = 60 + (i * 83) % 960; y = GROUND + 30 + ((i * 47) % 4) * 60
        dr.rectangle((x - 40, y - 50, x + 40, y), fill=(210, 185, 140), outline=(160, 135, 100), width=2)
    for j in range(3):
        w = 400 - j * 110; y0 = GROUND - 40 - j * 90
        dr.rectangle((540 - w / 2, y0 - 90, 540 + w / 2, y0), fill=(205, 175, 125), outline=(150, 120, 85), width=3)
    dr.rectangle((500, GROUND - 400, 580, GROUND - 310), fill=(230, 220, 200))
    dr.line((0, GROUND + 300, W, GROUND + 300), fill=(90, 150, 200), width=14)
    if t > 74.6:
        for i in range(5):
            q = ((t - 74.6) * 0.35 + i / 5) % 1
            x = lerp(100, 400, q) if i % 2 else lerp(980, 680, q)
            sack(dr, x, GROUND - 20, 1.0)
    if t > 78.8:
        for i in range(4):
            q = ((t - 78.8) * 0.4 + i / 4) % 1
            tablet(dr, 540 + 300 * math.cos(i * 1.6), lerp(GROUND - 300, 760, q), 50, 36)
    put(img, L_CITY, 540, 640, ss(70.6, 71.4, t) * (1 - ss(74.4, 74.8, t)))
    put(img, L_TEMPLE, 540, 640, ss(74.8, 75.6, t) * (1 - ss(78.6, 79.0, t)))
    put(img, L_REC, 540, 640, ss(79.0, 79.8, t) * (1 - ss(82.8, 83.2, t)))
    put(img, L_BIGGER, 540, 640, ss(83.2, 84.0, t))
    return img

# ---------- F: memory outside the brain ----------
L_OUT = text_img('知识存在了脑子外面', FB, 42, (255, 225, 160), 3)
L_FAR = text_img('传给陌生人 · 传给几百年后的人', FB, 38, (255, 235, 200), 3)
L_HIST = text_img('历史，从这里开始', FB, 50, (255, 225, 160), 4)
def history(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(91.8, 95.0, t)
    for i in range(5):
        x = 140 + i * 200
        a = 1.0 if i == 0 else ss(91.8 + i * 0.6, 92.4 + i * 0.6, t)
        if a > 0: person(dr, x, 1150, 2.2, SKINS[i % 5], a)
    tx = lerp(140, 940, k) if t > 91.6 else 140
    tablet(dr, tx + 60, 1000, 90, 64)
    put(img, L_OUT, 540, 640, ss(87.6, 88.4, t) * (1 - ss(91.4, 91.8, t)))
    put(img, L_FAR, 540, 640, ss(91.8, 92.6, t) * (1 - ss(95.6, 96.0, t)))
    put(img, L_HIST, 540, 640, ss(96.0, 96.8, t))
    return img

# ---------- G: taxes and the trouble with barter ----------
L_TAX = text_img('谁该交多少粮：最早的税', FB, 40, (255, 225, 160), 3)
L_BARTER = text_img('以物换物，太麻烦', FB, 42, (255, 200, 170), 3)
L_PROB = text_img('粮会坏 · 羊会跑 · 大小不好分', FB, 38, (255, 235, 200), 3)
L_NEED = text_img('需要一种大家都认的东西', FB, 42, (255, 225, 160), 3)
def sheep(dr, x, y, s, t):
    dr.ellipse((x - 50 * s, y - 34 * s, x + 50 * s, y + 30 * s), fill=(240, 238, 230))
    dr.ellipse((x + 40 * s, y - 40 * s, x + 74 * s, y - 6 * s), fill=(60, 55, 55))
    ph = math.sin(t * 9)
    for lx in (-30, 30): dr.line((x + lx * s, y + 20 * s, x + lx * s + 8 * s * ph, y + 60 * s), fill=(60, 55, 55), width=int(6 * s))
def tax(t):
    img = Image.fromarray(DESERT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 40, W, H), fill=(200, 175, 125))
    if t < 108.8:
        granary(dr, 760, GROUND + 40, 1.1)
        sapiens(dr, 560, GROUND + 160, 1.1, col=SKINS[3]); tablet(dr, 620, GROUND - 60, 70, 50)
        for i in range(3):
            x = lerp(-100 + i * 120, 300 + i * 70, ss(100.4, 103.4, t))
            sapiens(dr, x, GROUND + 220, 1.0, col=SKINS[i]); sack(dr, x + 40, GROUND + 60, 1.0)
        put(img, L_TAX, 540, 640, ss(100.4, 101.2, t))
        return img
    sx = 300 + 400 * ((t - 109) * 0.25 % 1)
    sheep(dr, sx, GROUND + 140, 1.4, t)
    sapiens(dr, 200, GROUND + 260, 1.1, col=SKINS[1]); sapiens(dr, 880, GROUND + 260, 1.1, col=SKINS[4])
    for i in range(4):
        sack(dr, 780 + i * 40, GROUND + 260, 1.0, col=(150, 140, 90) if t > 113 else GOLD)
    if t > 117.2:
        k = ss(117.4, 119.4, t)
        for i in range(5):
            x = 400 + i * 60; y = 1440
            dr.ellipse((x - 24, y - 12, x + 24, y + 12), fill=mul((210, 210, 220), k), outline=mul((240, 240, 250), k), width=2)
    put(img, L_BARTER, 540, 640, ss(109.0, 109.8, t) * (1 - ss(112.8, 113.2, t)))
    put(img, L_PROB, 540, 640, ss(113.2, 114.0, t) * (1 - ss(117.0, 117.4, t)))
    put(img, L_NEED, 540, 640, ss(117.4, 118.2, t))
    return img

def render(t):
    if t < 10.6: return dim(render26(133.1 + min(t, 6.0) + max(0, t - 6.0) * 0.0), 1 - ss(10.0, 10.6, t) if t > 6 else 1.0)
    if t < 19.0: return dim(meso(t), ss(10.6, 11.2, t) * (1 - ss(18.4, 19.0, t)))
    if t < 49.0:
        k = ss(19.0, 19.6, t) * (1 - ss(48.4, 49.0, t))
        for a in (27.2, 40.0):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(tokens(t), k)
    if t < 70.4:
        k = ss(49.0, 49.6, t) * (1 - ss(69.8, 70.4, t))
        for a in (61.4, 65.6):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(scripts(t), k)
    if t < 87.4: return dim(uruk(t), ss(70.4, 71.0, t) * (1 - ss(86.8, 87.4, t)))
    if t < 100.2: return dim(history(t), ss(87.4, 88.0, t) * (1 - ss(99.6, 100.2, t)))
    k = ss(100.2, 100.8, t)
    if 108.4 < t < 109.2: k *= 1 - 0.85 * math.sin(math.pi * (t - 108.4) / 0.8)
    return dim(tax(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep27_{ts}.png')
