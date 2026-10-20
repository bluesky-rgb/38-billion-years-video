import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK
from ep22 import sapiens, you_outline, flames, glow_at, add_glow, render as render22

CLEAN = False
OCEAN = grad((20, 50, 90), (12, 30, 60))
MX, MY, MW, MH = 20, 600, 1040, 680
CONT = {
 'af': [(0.10, 0.42), (0.17, 0.40), (0.22, 0.44), (0.27, 0.52), (0.25, 0.62), (0.21, 0.78), (0.17, 0.84), (0.14, 0.72), (0.12, 0.58), (0.06, 0.52), (0.05, 0.45)],
 'eu': [(0.03, 0.20), (0.10, 0.12), (0.20, 0.10), (0.22, 0.20), (0.20, 0.34), (0.13, 0.36), (0.06, 0.34)],
 'as': [(0.20, 0.10), (0.35, 0.06), (0.55, 0.06), (0.66, 0.10), (0.64, 0.20), (0.56, 0.30), (0.55, 0.40), (0.50, 0.48), (0.46, 0.50), (0.40, 0.58), (0.37, 0.48), (0.31, 0.46), (0.28, 0.40), (0.22, 0.36), (0.20, 0.26)],
 'ar': [(0.22, 0.38), (0.28, 0.40), (0.31, 0.48), (0.26, 0.52), (0.23, 0.46)],
 'se': [(0.46, 0.52), (0.52, 0.55), (0.55, 0.62), (0.50, 0.64), (0.45, 0.58)],
 'au': [(0.54, 0.70), (0.62, 0.66), (0.68, 0.70), (0.68, 0.82), (0.60, 0.86), (0.54, 0.80)],
 'na': [(0.70, 0.10), (0.80, 0.06), (0.92, 0.10), (0.96, 0.18), (0.92, 0.30), (0.86, 0.40), (0.82, 0.48), (0.78, 0.44), (0.74, 0.30), (0.70, 0.20)],
 'sa': [(0.83, 0.52), (0.90, 0.54), (0.94, 0.62), (0.90, 0.76), (0.86, 0.90), (0.83, 0.80), (0.81, 0.62)]}
def P(x, y): return (MX + x * MW, MY + y * MH)
def world(dr, bridge=0.0, land=(150, 140, 110)):
    for k, pts in CONT.items():
        dr.polygon([P(*p) for p in pts], fill=land)
    if bridge > 0:
        dr.polygon([P(0.63, 0.09), P(0.71, 0.09), P(0.71, 0.09 + 0.06 * bridge), P(0.63, 0.09 + 0.06 * bridge)], fill=(185, 165, 115))
# route segments: (start, end, t0, t1, label, label_pos)
ROUTE = [((0.20, 0.55), (0.26, 0.44), 23.6, 27.4), ((0.26, 0.44), (0.36, 0.50), 40.4, 44.0), ((0.36, 0.50), (0.48, 0.56), 44.6, 47.6),
         ((0.48, 0.56), (0.60, 0.74), 49.0, 52.0), ((0.24, 0.38), (0.12, 0.24), 53.4, 56.4), ((0.40, 0.42), (0.52, 0.30), 57.6, 60.6),
         ((0.52, 0.30), (0.66, 0.13), 80.0, 84.0), ((0.66, 0.13), (0.78, 0.24), 84.2, 87.6), ((0.78, 0.24), (0.86, 0.80), 88.4, 92.0)]
DATES = [((0.30, 0.40), '7–6 万年前', 25.4), ((0.62, 0.66), '5 万年前', 51.0), ((0.10, 0.20), '4.5 万年前', 55.4), ((0.52, 0.26), '4 万年前', 59.6),
         ((0.86, 0.64), '2–1.5 万年前', 90.0)]
L_DATES = [(p, text_img(s_, FB, 30, (255, 225, 160), 3), t0) for p, s_, t0 in DATES]
def routes(dr, t, alpha=1.0):
    for (a, b, t0, t1) in ROUTE:
        k = ss(t0, t1, t)
        if k <= 0: continue
        ax, ay = P(*a); bx, by = P(*b)
        ex, ey = lerp(ax, bx, k), lerp(ay, by, k)
        dr.line((ax, ay, ex, ey), fill=mul((255, 210, 120), alpha), width=6)
        dr.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=mul((255, 240, 200), alpha))
def dots(dr, t):
    for i in range(24):
        px, py = P(0.12 + 0.12 * ((i * 0.37) % 1), 0.48 + 0.3 * ((i * 0.61) % 1))
        dr.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(230, 80, 60))

# ---------- A ----------
L_AF = text_img('智人：在非洲生活了二十多万年', FB, 40, (255, 225, 160), 3)
def start(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr); dots(dr, t)
    put(img, L_AF, 540, 520, ss(6.6, 7.4, t))
    return img

# ---------- B: ice age sea level ----------
L_ICE = text_img('冰期：海水冻成冰川', FB, 42, (220, 235, 255), 3)
L_120 = text_img('海平面低了一百多米', FB, 40, (200, 225, 255), 3)
L_LAND = text_img('海峡变窄，露出陆地', FB, 42, (255, 225, 160), 3)
def sea(t):
    img = Image.fromarray(grad((140, 175, 205), (210, 220, 225), 480, 1000).astype(np.uint8)); dr = ImageDraw.Draw(img)
    drop = ss(15.0, 19.0, t)
    lvl = 960 + 260 * drop
    dr.rectangle((0, lvl, W, 1500), fill=(40, 100, 150))
    dr.polygon([(0, 700), (180, 640), (330, 820), (420, 1300), (0, 1300)], fill=(140, 125, 95))
    dr.polygon([(W, 680), (880, 630), (740, 830), (660, 1300), (W, 1300)], fill=(140, 125, 95))
    dr.polygon([(330, 1300), (420, 1150), (540, 1180), (660, 1150), (740, 1300)], fill=(150, 132, 100))
    dr.rectangle((0, 1300, W, 1500), fill=(110, 95, 75))
    ik = ss(10.8, 14.6, t)
    dr.polygon([(80, 690), (180, 640), (280, 700), (260, 720 - 0 * ik), (100, 720)], fill=(240, 248, 255))
    dr.polygon([(80, 690 - 60 * ik), (180, 640 - 90 * ik), (280, 700 - 60 * ik), (280, 700), (180, 640), (80, 690)], fill=(235, 245, 255))
    dr.polygon([(800, 680 - 60 * ik), (880, 630 - 90 * ik), (980, 670 - 60 * ik), (980, 670), (880, 630), (800, 680)], fill=(235, 245, 255))
    dr.line((0, 960, W, 960), fill=(255, 255, 255), width=2)
    if drop > 0.1:
        dr.line((40, 960, 40, lvl), fill=(255, 225, 160), width=4); dr.polygon([(28, lvl - 20), (52, lvl - 20), (40, lvl)], fill=(255, 225, 160))
    if t > 19.0:
        for i in range(3):
            q = (t * 0.3 + i / 3) % 1
            x = lerp(300, 780, q)
            dr.ellipse((x - 8, 1140 - 8, x + 8, 1140 + 8), fill=(230, 80, 60))
    put(img, L_ICE, 540, 560, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_120, 540, 560, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_LAND, 540, 560, ss(19.2, 20.0, t))
    return img

# ---------- C: the spread ----------
L_NOT = text_img('不是远行：一代人只往前挪几十公里', FB, 38, (255, 235, 200), 3)
L_THOU = text_img('几千年，走过一整片大陆', FB, 42, (255, 225, 160), 3)
L_BOAT = text_img('划船渡海', FB, 38, (220, 235, 255), 3)
L_TY = text_img('田园洞人', FB, 34, (255, 235, 200), 3)
def boat(dr, x, y, s):
    dr.polygon([(x - 40 * s, y), (x + 40 * s, y), (x + 28 * s, y + 16 * s), (x - 28 * s, y + 16 * s)], fill=(150, 110, 70))
    dr.line((x, y, x, y - 46 * s), fill=(120, 90, 60), width=3); dr.polygon([(x, y - 46 * s), (x + 30 * s, y - 14 * s), (x, y - 10 * s)], fill=(235, 230, 215))
def spread(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr); dots(dr, t); routes(dr, t)
    for p, im, t0 in L_DATES:
        if t0 < 62: put(img, im, *P(*p), ss(t0, t0 + 0.6, t))
    if 48.6 < t:
        bx, by = P(0.56, 0.66); boat(dr, bx, by + 6 * math.sin(t * 3), 1.0)
        put(img, L_BOAT, bx - 110, by + 40, ss(49.2, 50.0, t) * (1 - ss(53.0, 53.4, t)))
    put(img, L_TY, *P(0.56, 0.36), ss(58.0, 58.8, t))
    put(img, L_NOT, 540, 520, ss(32.0, 32.8, t) * (1 - ss(39.8, 40.2, t)))
    put(img, L_THOU, 540, 520, ss(40.4, 41.2, t) * (1 - ss(44.2, 44.6, t)))
    if 31.8 < t < 40.4:
        for i in range(5):
            x = 160 + i * 190; y = 1400
            sapiens(dr, x, y, 0.45, ss(32.0 + i * 0.6, 32.6 + i * 0.6, t))
            if i < 4: dr.line((x + 30, y - 60, x + 160, y - 60), fill=(255, 225, 160), width=3)
    return img

# ---------- D: meeting the others ----------
L_NEA = text_img('尼安德特人', FB, 40, (220, 210, 190), 3); L_DEN = text_img('丹尼索瓦人', FB, 40, (220, 210, 190), 3)
L_SAP = text_img('智人', FB, 40, (255, 225, 160), 3)
L_KIDS = text_img('他们还生了孩子', FB, 42, (255, 235, 200), 3)
L_DNA = text_img('非洲以外的人：约 2% 来自尼安德特人', FB, 38, (255, 225, 160), 3)
def neander(dr, x, y, s, a=1.0, col=(150, 115, 90)):
    dr.ellipse((x - 32 * s, y - 300 * s, x + 32 * s, y - 232 * s), fill=mul(col, a))
    dr.rectangle((x - 30 * s, y - 286 * s, x + 34 * s, y - 274 * s), fill=mul((120, 92, 72), a))
    dr.rounded_rectangle((x - 50 * s, y - 235 * s, x + 50 * s, y - 115 * s), radius=int(20 * s), fill=mul(col, a))
    for sg in (-1, 1):
        dr.line((x + sg * 54 * s, y - 220 * s, x + sg * 64 * s, y - 125 * s), fill=mul(col, a), width=int(18 * s))
        dr.line((x + sg * 20 * s, y - 118 * s, x + sg * 24 * s, y), fill=mul(col, a), width=int(22 * s))
def meet(t):
    img = Image.fromarray(grad((140, 160, 175), (215, 210, 190), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(150, 135, 100))
    if t < 74.4:
        sapiens(dr, 330, GROUND + 30, 1.5)
        put(img, L_SAP, 330, GROUND + 100, 1.0)
        nk = ss(62.2, 63.4, t)
        neander(dr, 740, GROUND + 30, 1.5, nk)
        put(img, L_NEA, 740, GROUND + 100, ss(66.2, 67.0, t)); put(img, L_DEN, 740, GROUND + 160, ss(67.4, 68.2, t))
        ck = ss(70.4, 71.6, t)
        if ck > 0:
            sapiens(dr, 540, GROUND + 30, 0.7, ck, col=(135, 98, 72))
            put(img, L_KIDS, 540, 560, ck)
        return img
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(74.8, 76.4, t)
    for i in range(3):
        x0, y0 = 120, 900 + i * 140
        for j in range(50):
            col = (230, 150, 90) if (j in (17, 41) and k > 0.3) else (110, 160, 220)
            dr.rectangle((x0 + j * 17, y0, x0 + j * 17 + 12, y0 + 60), fill=col)
    put(img, L_DNA, 540, 640, ss(74.8, 75.6, t))
    return img

# ---------- E: Beringia ----------
L_BR = text_img('白令陆桥', FB, 40, (255, 225, 160), 3)
L_AM = text_img('一路走到美洲最南端', FB, 40, (255, 235, 200), 3)
def bering(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr, bridge=ss(80.4, 83.6, t)); dots(dr, t); routes(dr, t)
    for p, im, t0 in L_DATES: put(img, im, *P(*p), ss(t0, t0 + 0.6, t))
    put(img, L_BR, *P(0.67, 0.02), ss(84.2, 85.0, t))
    put(img, L_AM, 540, 520, ss(88.4, 89.2, t))
    return img

# ---------- F: skin and sunlight ----------
L_STRONG = text_img('阳光强：深色皮肤保护身体', FB, 38, (255, 225, 160), 3)
L_WEAK = text_img('阳光弱：浅色皮肤更易合成维生素 D', FB, 36, (220, 235, 255), 3)
L_LAT = text_img('肤色随纬度变化', FB, 44, (255, 235, 200), 3)
def skin(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i, (y, inten, col) in enumerate(((760, 0.35, (230, 195, 165)), (1000, 0.65, (190, 140, 100)), (1240, 1.0, (110, 72, 50)))):
        dr.rectangle((60, y - 100, 1020, y + 100), fill=(int(30 + 30 * inten), int(30 + 22 * inten), 34))
        for j in range(int(3 + 9 * inten)):
            x = 120 + j * 40; dr.line((x, y - 100, x + 40, y - 20), fill=(255, 220, 120), width=int(2 + 3 * inten))
        a = ss(93.0 + (2 - i) * 1.0, 94.0 + (2 - i) * 1.0, t)
        if a > 0:
            sapiens(dr, 780, y + 95, 0.62, a, col=col)
    put(img, L_STRONG, 540, 560, ss(92.8, 93.6, t) * (1 - ss(96.6, 97.0, t)))
    put(img, L_WEAK, 540, 560, ss(97.0, 97.8, t) * (1 - ss(100.8, 101.2, t)))
    put(img, L_LAT, 540, 560, ss(101.2, 102.0, t))
    return img

# ---------- G: one family ----------
L_ONLY = text_img('只剩下智人', FB, 44, (255, 225, 160), 3)
L_ONE = text_img('所有人：同一群非洲祖先', FB, 42, (255, 225, 160), 3)
L_SMALLD = text_img('基因差别，其实很小', FB, 42, (255, 235, 200), 3)
L_HOW = text_img('散落全球的人，靠什么联合在一起？', FB, 38, (255, 235, 200), 3)
END_PTS = [(0.16, 0.6), (0.12, 0.26), (0.30, 0.44), (0.42, 0.18), (0.52, 0.30), (0.50, 0.58), (0.62, 0.76), (0.80, 0.22), (0.88, 0.40), (0.87, 0.72)]
def family(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr, bridge=1.0)
    if t < 118.0:
        routes(dr, 200, alpha=1.0 if t < 109.6 else 0.4)
        for p in END_PTS:
            x, y = P(*p); dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(230, 80, 60))
        if t > 109.6:
            k = ss(109.8, 111.6, t); ox, oy = P(0.20, 0.55)
            for p in END_PTS:
                x, y = P(*p); dr.line((x, y, lerp(x, ox, k), lerp(y, oy, k)), fill=(255, 225, 160), width=3)
            dr.ellipse((ox - 16, oy - 16, ox + 16, oy + 16), fill=(255, 225, 160))
        put(img, L_ONLY, 540, 520, ss(105.6, 106.4, t) * (1 - ss(109.4, 109.8, t)))
        put(img, L_ONE, 540, 520, ss(109.8, 110.6, t) * (1 - ss(113.6, 114.0, t)))
        put(img, L_SMALLD, 540, 520, ss(114.0, 114.8, t))
        return img
    arr = np.asarray(img, np.float32).copy()
    arr *= 0.55
    img = Image.fromarray(arr.astype(np.uint8))
    for p in END_PTS:
        x, y = P(*p)
        img = add_glow(img, glow_at(x, y, 60, 60, 120), ss(118.4, 120.0, t))
    dr = ImageDraw.Draw(img)
    for i, p in enumerate(END_PTS):
        x, y = P(*p)
        if t > 118.4: flames(dr, x, y + 10, 0.22, t + i, ss(118.4, 119.6, t))
    put(img, L_HOW, 540, 520, ss(118.2, 119.0, t))
    return img

def render(t):
    if t < 6.0: return render22(132.9 + t)
    if t < 10.6: return dim(start(t), ss(6.0, 6.6, t) * (1 - ss(10.0, 10.6, t)))
    if t < 23.2: return dim(sea(t), ss(10.6, 11.2, t) * (1 - ss(22.6, 23.2, t)))
    if t < 61.8: return dim(spread(t), ss(23.2, 23.8, t) * (1 - ss(61.2, 61.8, t)))
    if t < 79.8:
        k = ss(61.8, 62.4, t) * (1 - ss(79.2, 79.8, t))
        if 74.0 < t < 74.8: k *= 1 - 0.85 * math.sin(math.pi * (t - 74.0) / 0.8)
        return dim(meet(t), k)
    if t < 92.6: return dim(bering(t), ss(79.8, 80.4, t) * (1 - ss(92.0, 92.6, t)))
    if t < 105.4: return dim(skin(t), ss(92.6, 93.2, t) * (1 - ss(104.8, 105.4, t)))
    return dim(family(t), ss(105.4, 106.0, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep23_{ts}.png')
