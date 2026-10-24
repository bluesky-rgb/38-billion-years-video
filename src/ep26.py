import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK
from ep22 import sapiens
from ep24 import person, SKINS, bubble
from ep25 import hut, SKY, GOLD, render as render25

CLEAN = False
FAM = [(220, 120, 90), (110, 170, 220), (150, 200, 120)]

def granary(dr, gx, gy, s=1.0, fill=1.0):
    dr.rounded_rectangle((gx - 90 * s, gy - 220 * s, gx + 90 * s, gy), radius=int(50 * s), fill=(170, 130, 80))
    dr.polygon([(gx - 110 * s, gy - 200 * s), (gx, gy - 300 * s), (gx + 110 * s, gy - 200 * s)], fill=(200, 170, 100))
    if fill > 0: dr.rectangle((gx - 60 * s, gy - 20 * s - 160 * s * fill, gx + 60 * s, gy - 20 * s), fill=GOLD)
def sack(dr, x, y, s, col=GOLD):
    dr.rounded_rectangle((x - 22 * s, y - 40 * s, x + 22 * s, y), radius=int(12 * s), fill=col, outline=(150, 120, 60), width=2)
    dr.line((x - 10 * s, y - 40 * s, x + 10 * s, y - 40 * s), fill=(150, 120, 60), width=3)
def village(dr):
    dr.rectangle((0, GROUND, W, H), fill=(185, 160, 95))
    for x in (140, 360, 760, 960): hut(dr, x, GROUND + 20, 0.9)

# ---------- A: village & the old way of sharing ----------
L_SHARE = text_img('采集打猎时：肉放不了几天，分给大家最划算', FB, 34, (255, 235, 200), 3)
def opening(t):
    if t < 10.6:
        img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
        village(dr); granary(dr, 560, GROUND + 60)
        return img
    img = Image.fromarray(grad((40, 46, 40), (22, 26, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    cx, cy = 540, 1060
    dr.ellipse((cx - 70, cy - 30, cx + 70, cy + 30), fill=(170, 70, 60))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, y = cx + 330 * math.cos(a), cy + 200 * math.sin(a)
        person(dr, x, y + 30, 1.6, SKINS[i % 5])
        q = ((t - 11) * 0.5 + i / 8) % 1 if t > 11 else 0
        if t > 11:
            px, py = lerp(cx, x, q), lerp(cy, y, q)
            dr.ellipse((px - 14, py - 9, px + 14, py + 9), fill=(190, 80, 70))
    put(img, L_SHARE, 540, 640, ss(10.8, 11.6, t))
    return img

# ---------- B: storage & "mine" ----------
L_YEAR = text_img('粮食：能存一整年', FB, 42, (255, 225, 160), 3)
L_MEAT = text_img('肉', FB, 36, (230, 200, 190), 3); L_GRAIN = text_img('粮', FB, 36, (255, 225, 160), 3)
L_MINE = text_img('这是我的！', FB, 40, (40, 40, 40), 0)
L_FIELD = text_img('自己开垦、播种、照看的地，收成归自己', FB, 36, (255, 235, 200), 3)
L_PROP = text_img('财产', FB, 56, (255, 225, 160), 4)
def mine(t):
    if t < 23.2:
        img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
        k = ss(19.4, 22.6, t)
        for row, (lab, decay, col) in enumerate(((L_MEAT, 1.0, (190, 80, 70)), (L_GRAIN, 0.05, GOLD))):
            y = 900 + row * 260
            put(img, lab, 120, y + 30, 1.0)
            for m in range(12):
                x = 200 + m * 66
                if m / 12 > k: break
                v = max(0.0, 1 - decay * m / 2.5)
                dr.rectangle((x, y + 60 - 120 * v, x + 48, y + 60), fill=col if v > 0.05 else (70, 70, 74))
        put(img, L_YEAR, 540, 640, ss(19.4, 20.2, t))
        return img
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 31.8:
        village(dr); granary(dr, 540, GROUND + 60)
        sapiens(dr, lerp(1150, 700, ss(23.4, 26.4, t)), GROUND + 160, 1.0, col=(60, 50, 50))
        if t > 27.4:
            sapiens(dr, lerp(-80, 360, ss(27.4, 28.8, t)), GROUND + 160, 1.0, col=SKINS[1])
            if t > 28.6: bubble(img, dr, 380, GROUND - 200, L_MINE)
        return img
    dr.rectangle((0, GROUND - 60, W, H), fill=(150, 125, 80))
    for i in range(3):
        x0 = 40 + i * 340
        for j in range(5): dr.line((x0 + 20, GROUND + j * 80, x0 + 300, GROUND + j * 80), fill=mul(FAM[i], 0.8), width=6)
        for (px, py) in ((x0, GROUND - 40), (x0 + 320, GROUND - 40), (x0, GROUND + 420), (x0 + 320, GROUND + 420)):
            dr.ellipse((px - 18, py - 14, px + 18, py + 14), fill=(130, 125, 118))
        sapiens(dr, x0 + 160, GROUND - 40, 0.8, col=SKINS[i])
        dr.rectangle((x0 + 150, GROUND - 330, x0 + 170, GROUND - 300), fill=FAM[i])
    put(img, L_FIELD, 540, 640, ss(32.0, 32.8, t) * (1 - ss(35.8, 36.2, t)))
    put(img, L_PROP, 540, 640, ss(36.2, 37.0, t))
    return img

# ---------- C: generations of surplus ----------
L_LUCK = text_img('地更肥 · 运气更好 · 孩子更多', FB, 38, (255, 235, 200), 3)
L_SUR = text_img('余粮越积越多', FB, 42, (255, 225, 160), 3)
L_INH = text_img('传给下一代', FB, 42, (255, 225, 160), 3)
L_GAP = text_img('一代代：差距越拉越大', FB, 42, (255, 190, 160), 3)
L_GEN = [text_img(f'第 {i + 1} 代', FM, 30, (220, 220, 230), 3) for i in range(4)]
STACK = [[2, 2, 2], [3, 2, 1], [6, 3, 1], [11, 4, 1]]
def gens(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for g in range(4):
        k = ss(40.8 + g * 3.0, 42.0 + g * 3.0, t) if g < 2 else ss(49.0 + (g - 2) * 2.4, 50.2 + (g - 2) * 2.4, t)
        if g == 0: k = ss(40.6, 41.4, t)
        if k <= 0: continue
        y = 1460 - g * 0
        x0 = 120 + g * 230
        put(img, L_GEN[g], x0 + 90, 1510, k)
        for f in range(3):
            n = STACK[g][f]
            for j in range(int(n * k + 0.999)):
                sack(dr, x0 + 30 + f * 60, y - j * 44, 1.0, col=mul(FAM[f], 0.5) if False else GOLD)
                dr.rectangle((x0 + 22 + f * 60, y - j * 44 - 34, x0 + 38 + f * 60, y - j * 44 - 30), fill=FAM[f])
        if g > 0 and t > 48.8:
            dr.line((x0 - 60, 1000, x0 - 20, 1000), fill=(255, 210, 120), width=4); dr.polygon([(x0 - 20, 990), (x0, 1000), (x0 - 20, 1010)], fill=(255, 210, 120))
    put(img, L_LUCK, 540, 640, ss(40.6, 41.4, t) * (1 - ss(44.4, 44.8, t)))
    put(img, L_SUR, 540, 640, ss(44.8, 45.6, t) * (1 - ss(48.6, 49.0, t)))
    put(img, L_INH, 540, 640, ss(49.0, 49.8, t) * (1 - ss(52.8, 53.2, t)))
    put(img, L_GAP, 540, 640, ss(53.2, 54.0, t))
    return img

# ---------- D: specialists, walls ----------
L_SPEC = [text_img(s_, FB, 36, (255, 235, 200), 3) for s_ in ('工匠', '祭司', '首领')]
L_NOFARM = text_img('余粮养活不种地的人', FB, 42, (255, 225, 160), 3)
L_WALL = text_img('争抢：围墙和武器', FB, 42, (255, 200, 170), 3)
def specialists(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    village(dr)
    if t < 66.0:
        granary(dr, 540, GROUND - 20, 0.9)
        for i, x in enumerate((200, 540, 880)):
            a = ss(61.8 + i * 0.8, 62.6 + i * 0.8, t)
            if a <= 0: continue
            y = GROUND + 360
            sapiens(dr, x, y, 1.0, a, col=SKINS[i + 1])
            if i == 0:
                for j in range(3): dr.polygon([(x + 50 + j * 36, y), (x + 40 + j * 36, y - 50), (x + 76 + j * 36, y - 50), (x + 66 + j * 36, y)], fill=mul((180, 110, 70), a))
            elif i == 1:
                dr.rectangle((x + 60, y - 70, x + 120, y), fill=mul((200, 190, 170), a)); dr.ellipse((x + 75, y - 100, x + 105, y - 70), fill=mul((255, 200, 100), a))
            else:
                dr.line((x + 50, y - 230, x + 50, y), fill=mul((120, 90, 60), a), width=8); dr.ellipse((x + 38, y - 250, x + 62, y - 226), fill=mul((255, 210, 120), a))
            put(img, L_SPEC[i], x, y + 50, a)
            if a > 0.5: dr.line((540, GROUND + 40, x, y - 300), fill=mul(GOLD, a), width=3)
        put(img, L_NOFARM, 540, 640, ss(57.6, 58.4, t))
        return img
    granary(dr, 540, GROUND + 60)
    wk = ss(70.4, 73.0, t)
    for i in range(14):
        x = 20 + i * 76; h = 160 * wk
        if h > 2: dr.rectangle((x, GROUND + 260 - h, x + 60, GROUND + 260), fill=(150, 115, 75))
    sapiens(dr, 700, GROUND + 160, 1.0, col=SKINS[2]); dr.line((740, GROUND - 160, 760, GROUND + 140), fill=(110, 85, 60), width=6)
    dr.polygon([(735, GROUND - 180), (745, GROUND - 160), (725, GROUND - 160)], fill=(150, 145, 140))
    if t > 70.2:
        for i in range(3):
            sapiens(dr, lerp(1250, 980, wk) + i * 60, GROUND + 380, 0.9, col=(70, 60, 60))
    put(img, L_WALL, 540, 640, ss(70.4, 71.2, t))
    return img

# ---------- E: archaeology ----------
L_CAT = text_img('加泰土丘：家家房子差不多大', FB, 40, (255, 225, 160), 3)
L_LIANG = text_img('良渚：少数大墓堆满玉器', FB, 40, (255, 225, 160), 3)
L_EMPTY = text_img('多数墓：几乎空空', FM, 34, (230, 230, 235), 3)
def archaeo(t):
    if t < 83.2:
        img = Image.fromarray(grad((190, 170, 140), (160, 140, 110)).astype(np.uint8)); dr = ImageDraw.Draw(img)
        k = ss(74.8, 77.4, t)
        for r in range(6):
            for c in range(6):
                if (r * 6 + c) / 36 > k: continue
                x = 150 + c * 140 + (r % 2) * 20; y = 780 + r * 120
                dr.rectangle((x, y, x + 120, y + 100), fill=(210, 190, 155), outline=(150, 130, 100), width=4)
                dr.rectangle((x + 50, y + 40, x + 70, y + 60), fill=(90, 70, 50))
        if t > 79.0:
            for i in range(10):
                x = 180 + (i * 97) % 760; y = 800 + (i * 131) % 600
                person(dr, x, y, 0.8, SKINS[i % 5])
        put(img, L_CAT, 540, 640, ss(74.8, 75.6, t))
        return img
    img = Image.fromarray(grad((120, 100, 80), (80, 64, 50)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, 820, W, 860), fill=(150, 130, 100))
    dr.rectangle((80, 900, 520, 1160), fill=(60, 48, 38), outline=(170, 150, 110), width=4)
    k = ss(83.6, 85.6, t)
    for i in range(int(14 * k)):
        x = 120 + (i * 61) % 360; y = 940 + (i // 6) * 70
        if i % 2: dr.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(120, 170, 130), outline=(170, 210, 170), width=3); dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(60, 48, 38))
        else: dr.rectangle((x - 20, y - 26, x + 20, y + 26), fill=(110, 160, 120), outline=(170, 210, 170), width=3)
    for i in range(6):
        x = 600 + (i % 3) * 140; y = 920 + (i // 3) * 140
        dr.rectangle((x, y, x + 110, y + 100), fill=(60, 48, 38), outline=(140, 125, 100), width=3)
    put(img, L_LIANG, 540, 640, ss(83.4, 84.2, t)); put(img, L_EMPTY, 810, 1240, ss(87.6, 88.4, t))
    return img

# ---------- F: is inequality inevitable? ----------
L_Q = text_img('不平等，是种地之后必然出现的吗？', FB, 40, (255, 225, 160), 3)
L_NO = text_img('不少早期村落，长期保持平等', FB, 40, (255, 235, 200), 3)
L_CHOOSE = text_img('怎样组织社会，人们一直在选择', FB, 40, (255, 225, 160), 3)
def debate(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_Q, 540, 640, ss(92.0, 92.8, t) * (1 - ss(99.8, 100.2, t)))
    if t < 100.2:
        for i in range(2):
            x0 = 120 + i * 480
            dr.rounded_rectangle((x0, 800, x0 + 360, 1200), radius=24, outline=(180, 185, 200), width=3)
            sizes = [1.0] * 5 if i == 0 else [1.8, 1.0, 0.7, 0.6, 0.5]
            for j, s in enumerate(sizes):
                hut(dr, x0 + 60 + (j % 3) * 120, 960 + (j // 3) * 180, 0.45 * s)
        return img
    if t < 104.4:
        for i in range(3):
            x0 = 80 + i * 320
            dr.rounded_rectangle((x0, 800, x0 + 280, 1150), radius=24, outline=(255, 210, 130), width=3)
            for j in range(4): hut(dr, x0 + 60 + (j % 2) * 140, 940 + (j // 2) * 160, 0.45)
        put(img, L_NO, 540, 640, ss(100.4, 101.2, t))
        return img
    dr.line((540, 1400, 540, 1050), fill=(200, 200, 210), width=10)
    k = ss(104.8, 106.6, t)
    for sg in (-1, 1):
        dr.line((540, 1050, 540 + sg * 300 * k, 1050 - 300 * k), fill=(255, 210, 130), width=10)
    put(img, L_CHOOSE, 540, 640, ss(104.6, 105.4, t))
    return img

# ---------- G: disputes, memory overload ----------
L_DIS = text_img('财产越多，纠纷越多', FB, 42, (255, 200, 170), 3)
L_OWE = text_img('谁欠谁几袋粮？谁家的地在哪？', FB, 38, (255, 235, 200), 3)
L_MEM = text_img('光靠脑子，记不住了', FB, 44, (255, 225, 160), 3)
def disputes(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    village(dr)
    for i in range(6): sack(dr, 470 + i * 34, GROUND + 160, 1.4)
    sapiens(dr, 300, GROUND + 200, 1.3, col=SKINS[0]); sapiens(dr, 820, GROUND + 200, 1.3, col=SKINS[3])
    if 109.0 < t:
        sh = 0.5 + 0.5 * math.sin(t * 6)
        dr.line((340, GROUND - 120, 440 + 20 * sh, GROUND - 60), fill=SKINS[0], width=12)
        dr.line((780, GROUND - 120, 680 - 20 * sh, GROUND - 60), fill=SKINS[3], width=12)
    if t > 113.0:
        n = int(18 * ss(113.2, 116.8, t))
        for i in range(n):
            x = 120 + (i * 151) % 840; y = 760 + (i * 97) % 300
            for j in range(1 + i % 4): dr.line((x + j * 10, y, x + j * 10, y + 30), fill=(60, 50, 40), width=3)
    if t > 117.2:
        k = ss(117.4, 119.4, t)
        dr.rounded_rectangle((380, 1400, 700, 1490), radius=14, fill=mul((190, 150, 110), k))
        for j in range(6): dr.line((410 + j * 46, 1415, 430 + j * 46, 1475), fill=mul((110, 80, 60), k), width=4)
    put(img, L_DIS, 540, 640, ss(109.0, 109.8, t) * (1 - ss(112.8, 113.2, t)))
    put(img, L_OWE, 540, 640, ss(113.2, 114.0, t) * (1 - ss(117.0, 117.4, t)))
    put(img, L_MEM, 540, 640, ss(117.4, 118.2, t))
    return img

def render(t):
    if t < 6.0: return render25(137.1 + t)
    if t < 19.0:
        k = ss(6.0, 6.6, t) * (1 - ss(18.4, 19.0, t))
        if 10.2 < t < 11.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 10.2) / 0.8)
        return dim(opening(t), k)
    if t < 40.4:
        k = ss(19.0, 19.6, t) * (1 - ss(39.8, 40.4, t))
        for a in (22.8, 31.4):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(mine(t), k)
    if t < 57.4: return dim(gens(t), ss(40.4, 41.0, t) * (1 - ss(56.8, 57.4, t)))
    if t < 74.6:
        k = ss(57.4, 58.0, t) * (1 - ss(74.0, 74.6, t))
        if 65.6 < t < 66.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 65.6) / 0.8)
        return dim(specialists(t), k)
    if t < 91.8:
        k = ss(74.6, 75.2, t) * (1 - ss(91.2, 91.8, t))
        if 82.8 < t < 83.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 82.8) / 0.8)
        return dim(archaeo(t), k)
    if t < 108.8: return dim(debate(t), ss(91.8, 92.4, t) * (1 - ss(108.2, 108.8, t)))
    return dim(disputes(t), ss(108.8, 109.4, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep26_{ts}.png')
