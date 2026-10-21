import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK, NIGHT
from ep22 import glow_at, add_glow, flames, logs, sitter, sapiens, you_outline
from ep23 import world, P, OCEAN, render as render23

CLEAN = False
rng = np.random.default_rng(241)
G_FIRE = glow_at(540, 1200, 460, 330, 170)
SKINS = [(115, 80, 58), (150, 110, 80), (95, 65, 48), (175, 135, 100), (130, 92, 66)]

def person(dr, x, y, s, col, a=1.0):
    dr.ellipse((x - 16 * s, y - 70 * s, x + 16 * s, y - 38 * s), fill=mul(col, a))
    dr.rounded_rectangle((x - 20 * s, y - 38 * s, x + 20 * s, y + 20 * s), radius=int(10 * s), fill=mul(col, a))

# ---------- A: the small band ----------
L_BAND = text_img('几十人的小群', FB, 44, (255, 225, 160), 3)
L_TRUST = text_img('合作靠：彼此认识、互相信任', FB, 40, (255, 235, 200), 3)
SEATS = [(540 + 300 * math.cos(a), 1210 + 120 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)]
def band(t):
    img = Image.fromarray(NIGHT.astype(np.uint8)); img = add_glow(img, G_FIRE, 0.95 + 0.05 * math.sin(t * 9)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND + 40, W, H), fill=(60, 46, 36))
    order = sorted(range(len(SEATS)), key=lambda i: SEATS[i][1])
    back = [i for i in order if SEATS[i][1] < 1210]; front = [i for i in order if SEATS[i][1] >= 1210]
    for i in back: sitter(dr, SEATS[i][0], SEATS[i][1], 0.8, 1 if SEATS[i][0] < 540 else -1, t, i)
    logs(dr, 540, 1240, 1.0); flames(dr, 540, 1230, 1.1, t)
    for i in front: sitter(dr, SEATS[i][0], SEATS[i][1] + 40, 0.95, 1 if SEATS[i][0] < 540 else -1, t, i)
    put(img, L_BAND, 540, 620, ss(6.6, 7.4, t) * (1 - ss(10.4, 10.8, t)))
    put(img, L_TRUST, 540, 620, ss(10.8, 11.6, t))
    return img

# ---------- B: network, gossip, 150 ----------
L_LANG = text_img('语言越来越复杂', FB, 44, (255, 225, 160), 3)
L_B1 = text_img('他很可靠', FB, 34, (40, 40, 40), 0); L_B2 = text_img('她在偷懒', FB, 34, (40, 40, 40), 0)
L_SPREAD = text_img('信任，靠聊天传开', FB, 42, (255, 235, 200), 3)
L_150 = text_img('直接认识的人：最多约 150 个', FB, 40, (255, 225, 160), 3)
L_SPLIT = text_img('人再多，群体就容易分裂', FB, 42, (255, 200, 170), 3)
NET = [(540 + 300 * math.cos(a) * r, 1020 + 300 * math.sin(a) * r) for a, r in zip(np.linspace(0, 2 * math.pi, 12, endpoint=False), [0.9, 0.6, 1.0, 0.75, 0.95, 0.55, 1.0, 0.7, 0.9, 0.6, 1.0, 0.8])]
EDGES = [(i, (i + 1) % 12) for i in range(12)] + [(i, (i + 5) % 12) for i in range(0, 12, 2)]
RING = [(540 + 380 * math.cos(a), 1020 + 380 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 150, endpoint=False)]
def bubble(img, dr, x, y, lab):
    w = lab.width + 30
    dr.rounded_rectangle((x - w / 2, y - 34, x + w / 2, y + 34), radius=20, fill=(245, 240, 230))
    dr.polygon([(x - 10, y + 32), (x + 10, y + 32), (x - 20, y + 56)], fill=(245, 240, 230))
    put(img, lab, x, y, 1.0)
def network(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 27.6:
        sp = ss(23.4, 26.6, t)
        for k, (i, j) in enumerate(EDGES):
            on = sp * len(EDGES) > k
            dr.line((NET[i], NET[j]), fill=(255, 210, 120) if on else (90, 95, 110), width=4 if on else 2)
        for i, (x, y) in enumerate(NET): person(dr, x, y + 30, 1.0, SKINS[i % 5])
        if 19.0 < t < 23.4:
            bubble(img, dr, NET[0][0] - 40, NET[0][1] - 110, L_B1)
            if t > 20.6: bubble(img, dr, NET[6][0] + 40, NET[6][1] - 110, L_B2)
        put(img, L_LANG, 540, 620, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
        put(img, L_SPREAD, 540, 620, ss(23.4, 24.2, t))
        return img
    n = int(150 * ss(27.8, 30.8, t))
    split = ss(32.2, 35.0, t)
    for i in range(n):
        x, y = RING[i]
        if split > 0:
            sg = -1 if i < 75 else 1
            x = lerp(x, 540 + sg * 260 + (x - 540) * 0.5, split); y = lerp(y, 1020 + (y - 1020) * 0.55, split)
        dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=SKINS[i % 5])
    if split > 0.3:
        dr.line((540, 760, 540, 1280), fill=mul((230, 90, 70), split), width=4)
    put(img, L_150, 540, 620, ss(27.8, 28.6, t) * (1 - ss(31.6, 32.0, t)))
    put(img, L_SPLIT, 540, 620, ss(32.0, 32.8, t))
    return img

# ---------- C: shared stories ----------
L_UNSEEN = text_img('人能谈论看不见的东西', FB, 42, (255, 225, 160), 3)
L_ICONS = [text_img(s_, FB, 34, (240, 235, 220), 3) for s_ in ('祖先的灵魂', '部落的图腾', '神话里的英雄')]
L_STR = text_img('两个陌生人，相信同一个故事', FB, 40, (255, 235, 200), 3)
L_COOP = text_img('就能当自己人，一起合作', FB, 42, (255, 225, 160), 3)
def totem(dr, x, y, s, a=1.0, col=(255, 200, 110)):
    dr.rectangle((x - 22 * s, y - 120 * s, x + 22 * s, y + 80 * s), fill=mul(col, a * 0.8))
    for j in range(3):
        yy_ = y - 100 * s + j * 60 * s
        dr.ellipse((x - 36 * s, yy_ - 4 * s, x + 36 * s, yy_ + 44 * s), fill=mul(col, a))
        dr.ellipse((x - 18 * s, yy_ + 10 * s, x - 6 * s, yy_ + 22 * s), fill=mul((60, 40, 30), a)); dr.ellipse((x + 6 * s, yy_ + 10 * s, x + 18 * s, yy_ + 22 * s), fill=mul((60, 40, 30), a))
    dr.polygon([(x - 80 * s, y - 120 * s), (x, y - 160 * s), (x + 80 * s, y - 120 * s)], fill=mul(col, a))
def stories(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 44.6:
        put(img, L_UNSEEN, 540, 620, ss(36.4, 37.2, t))
        for i, x in enumerate((220, 540, 860)):
            a = ss(40.6 + i * 0.9, 41.4 + i * 0.9, t)
            if a <= 0: continue
            g = add_glow(img, glow_at(x, 1000, 120, 160, 90), a); img = g; dr = ImageDraw.Draw(img)
            if i == 0:
                dr.ellipse((x - 50, 880, x + 50, 980), fill=mul((200, 210, 240), a)); dr.polygon([(x - 60, 980), (x + 60, 980), (x + 40, 1120), (x, 1090), (x - 40, 1120)], fill=mul((200, 210, 240), a))
            elif i == 1: totem(dr, x, 1040, 1.0, a)
            else:
                person(dr, x, 1080, 2.4, (230, 190, 120), a); dr.polygon([(x - 40, 870), (x, 830), (x + 40, 870)], fill=mul((255, 220, 120), a))
            put(img, L_ICONS[i], x, 1220, a)
        return img
    if t < 53.0:
        k = ss(49.2, 51.6, t)
        lx, rx = lerp(180, 420, k), lerp(900, 660, k)
        sapiens(dr, lx, 1300, 1.1, col=SKINS[0]); sapiens(dr, rx, 1300, 1.1, col=SKINS[3])
        for x in (lx, rx):
            dr.ellipse((x - 90, 790, x + 90, 960), fill=(245, 240, 230)); dr.ellipse((x - 14, 975, x + 6, 995), fill=(245, 240, 230))
            totem(dr, x, 900, 0.45)
        if k > 0.95:
            dr.line((lx + 50, 1110, rx - 50, 1110), fill=(255, 210, 120), width=12)
        put(img, L_STR, 540, 620, ss(44.8, 45.6, t) * (1 - ss(48.8, 49.2, t)))
        put(img, L_COOP, 540, 620, ss(49.2, 50.0, t))
        return img
    return img

# ---------- D: art evidence ----------
L_ART = [text_img(s_, FB, 38, (255, 225, 160), 3) for s_ in ('南非 · 刻纹', '印尼 · 洞穴壁画', '狮子人雕像 · 骨笛')]
def art(t):
    img = Image.fromarray(grad((70, 55, 45), (36, 28, 24)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 57.4:
        dr.polygon([(300, 900), (780, 860), (820, 1120), (280, 1160)], fill=(170, 80, 50))
        k = ss(53.6, 56.0, t)
        for j in range(int(8 * k)):
            dr.line((330 + j * 55, 920, 400 + j * 55, 1120), fill=(240, 200, 160), width=4)
            dr.line((400 + j * 55, 920, 330 + j * 55, 1120), fill=(240, 200, 160), width=4)
        dr.line((320, 1020, 790, 990), fill=(240, 200, 160), width=4)
        put(img, L_ART[0], 540, 640, ss(53.6, 54.4, t))
    elif t < 61.6:
        dr.rectangle((0, 760, W, 1400), fill=(150, 120, 95))
        k = ss(57.8, 60.0, t)
        c = mul((170, 60, 40), k)
        dr.ellipse((340, 960, 700, 1120), fill=c); dr.ellipse((660, 950, 780, 1030), fill=c)
        for x in (380, 460, 600, 670): dr.line((x, 1100, x, 1200), fill=c, width=16)
        for j in range(5):
            hx = 200 + j * 160; dr.ellipse((hx - 30, 820 - (j % 2) * 20, hx + 30, 880 - (j % 2) * 20), outline=mul((170, 60, 40), k * 0.7), width=4)
        put(img, L_ART[1], 540, 640, ss(57.8, 58.6, t))
    else:
        k = ss(61.8, 62.8, t)
        x = 380; c = mul((235, 225, 200), k)
        dr.rounded_rectangle((x - 50, 900, x + 50, 1240), radius=40, fill=c)
        dr.ellipse((x - 70, 820, x + 70, 940), fill=c); dr.ellipse((x - 85, 815, x - 50, 850), fill=c); dr.ellipse((x + 50, 815, x + 85, 850), fill=c)
        dr.rounded_rectangle((640, 980, 900, 1020), radius=18, fill=c)
        for j in range(4): dr.ellipse((680 + j * 55, 990, 696 + j * 55, 1006), fill=(70, 55, 45))
        put(img, L_ART[2], 540, 640, ss(62.0, 62.8, t))
    return img

# ---------- E: passing on knowledge ----------
L_PASS = text_img('故事把知识传给下一代', FB, 42, (255, 225, 160), 3)
L_K = [text_img(s_, FB, 34, (40, 40, 40), 0) for s_ in ('哪里有水', '哪种果子有毒', '工具怎么做')]
def teach(t):
    img = Image.fromarray(NIGHT.astype(np.uint8)); img = add_glow(img, glow_at(540, 1250, 360, 260, 160), 1.0); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND + 40, W, H), fill=(60, 46, 36))
    logs(dr, 540, 1270, 0.9); flames(dr, 540, 1260, 0.9, t)
    sitter(dr, 260, 1250, 1.2, 1, t, 0)
    for i, x in enumerate((720, 840, 950)): sitter(dr, x, 1270, 0.65, -1, t, i + 1)
    for i in range(3):
        a = ss(70.4 + i * 1.2, 71.0 + i * 1.2, t)
        if a > 0.5: bubble(img, dr, 300 + i * 30, 760 + i * 120, L_K[i])
    put(img, L_PASS, 540, 620, ss(66.2, 67.0, t))
    return img

# ---------- F: scaling up ----------
L_FARM = text_img('种地、定居：村落变成城市', FB, 40, (255, 235, 200), 3)
L_INST = [text_img(s_, FB, 38, (255, 225, 160), 3) for s_ in ('文字', '货币', '法律', '国家', '公司', '互联网')]
L_BIG = text_img('更大的共同故事和规则', FB, 42, (255, 225, 160), 3)
L_BILL = text_img('合作扩大到几十亿人', FB, 44, (255, 235, 200), 3)
def scale_up(t):
    if t < 83.2:
        k = ss(78.9, 82.6, t)
        img = Image.fromarray(grad((150, 185, 215), (235, 225, 190), 480, 1100).astype(np.uint8)); dr = ImageDraw.Draw(img)
        dr.rectangle((0, GROUND, W, H), fill=(170, 150, 90))
        for j in range(8): dr.rectangle((0, GROUND + 30 + j * 50, W, GROUND + 50 + j * 50), fill=(190, 170, 80))
        for i in range(5):
            x = 140 + i * 200
            dr.rectangle((x - 50, GROUND - 70, x + 50, GROUND), fill=(150, 110, 70)); dr.polygon([(x - 70, GROUND - 70), (x, GROUND - 130), (x + 70, GROUND - 70)], fill=(190, 160, 90))
        for i in range(7):
            h = (220 + (i * 97) % 300) * k
            x = 60 + i * 160
            if h > 4: dr.rectangle((x, GROUND - 140 - h, x + 110, GROUND - 140), fill=(110, 120, 140))
        put(img, L_FARM, 540, 620, ss(75.0, 75.8, t))
        return img
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr, land=(120, 115, 95))
    if t > 87.4:
        k = ss(87.6, 91.0, t)
        pts = [(0.15, 0.5), (0.12, 0.25), (0.30, 0.44), (0.42, 0.18), (0.52, 0.30), (0.50, 0.58), (0.62, 0.76), (0.80, 0.22), (0.88, 0.40), (0.87, 0.72), (0.36, 0.30), (0.25, 0.66)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:]:
                if (i * 7 + len(b)) % 3 == 0 or k > 0.6:
                    dr.line((P(*a), P(*b)), fill=mul((255, 210, 120), 0.35 + 0.65 * k), width=2)
        for i in range(int(300 * k)):
            x = (i * 0.618) % 1; y = (i * 0.379) % 1
            px, py = P(0.05 + 0.9 * x, 0.1 + 0.75 * y)
            dr.point((px, py), fill=(255, 240, 200))
    for i, lab in enumerate(L_INST):
        put(img, lab, 140 + i * 160, 520, ss(83.4 + i * 0.5, 84.0 + i * 0.5, t))
    put(img, L_BIG, 540, 1380, ss(87.6, 88.4, t) * (1 - ss(91.4, 91.8, t)))
    put(img, L_BILL, 540, 1380, ss(91.8, 92.6, t))
    return img

# ---------- G: one explanation ----------
L_ONE = text_img('这是一种解释', FB, 46, (255, 225, 160), 3)
L_ALT = [text_img(s_, FB, 38, c, 3) for s_, c in (('共同的故事', (255, 225, 160)), ('利益交换', (220, 225, 235)), ('制度', (220, 225, 235)), ('亲缘', (220, 225, 235)))]
L_DEBATE = text_img('科学家们还在争论', FB, 42, (255, 235, 200), 3)
def debate(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_ONE, 540, 620, ss(96.2, 97.0, t))
    for i, lab in enumerate(L_ALT):
        a = 1.0 if i == 0 else ss(100.4 + i * 0.5, 101.0 + i * 0.5, t)
        x = 290 + (i % 2) * 500; y = 900 + (i // 2) * 220
        if a > 0:
            dr.rounded_rectangle((x - 200, y - 70, x + 200, y + 70), radius=24, fill=mul((36, 40, 52), a), outline=mul((255, 210, 130) if i == 0 else (180, 185, 200), a), width=3)
            put(img, lab, x, y, a)
    put(img, L_DEBATE, 540, 1400, ss(100.6, 101.4, t))
    return img

# ---------- H: 3.8 billion years ----------
L_38 = text_img('38 亿年', FB, 70, (255, 225, 160), 5)
L_CELLS = text_img('细胞合作 → 身体', FB, 42, (255, 235, 200), 3)
L_PEOPLE = text_img('人和人合作 → 社会', FB, 42, (255, 235, 200), 3)
L_KEEP = text_img('生命一直在寻找新的合作方式', FB, 40, (255, 225, 160), 3)
L_YOU = text_img('你：最新的一环', FB, 46, (255, 225, 160), 4)
STAGES = [(0.10, (120, 200, 220)), (0.22, (150, 220, 160)), (0.34, (200, 220, 140)), (0.46, (230, 200, 120)), (0.58, (240, 170, 110)), (0.70, (240, 140, 110)), (0.82, (230, 120, 130))]
def finale(t):
    img = Image.fromarray(grad((10, 12, 26), (24, 20, 36)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(80):
        x = (i * 151) % W; y = 480 + (i * 89) % 1400
        dr.point((x, y), fill=(180, 180, 210))
    if t < 108.8:
        k = ss(104.8, 108.2, t)
        y = 1100
        dr.line((60, y, 60 + 960 * k, y), fill=(255, 210, 120), width=4)
        for fx, c in STAGES:
            if fx <= k + 0.05:
                x = 60 + 960 * fx
                dr.ellipse((x - 18, y - 18, x + 18, y + 18), fill=c)
        put(img, L_38, 540, 760, ss(104.8, 105.6, t))
        return img
    if t < 113.0:
        k = ss(109.0, 111.6, t)
        for i in range(60):
            a = i * 2.39996; r = 14 * math.sqrt(i) * (1 - 0.35 * k)
            x, y = 540 + r * math.cos(a), 1050 + r * math.sin(a)
            x = lerp(x + 300 * math.cos(i), x, k); y = lerp(y + 300 * math.sin(i * 1.3), y, k)
            dr.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(150, 210, 190), outline=(210, 245, 230))
        put(img, L_CELLS, 540, 620, ss(109.0, 109.8, t))
        return img
    if t < 117.4:
        k = ss(113.2, 115.6, t)
        pts = [(540 + 380 * math.cos(a) * (0.5 + 0.5 * ((i * 0.37) % 1)), 1050 + 380 * math.sin(a) * (0.5 + 0.5 * ((i * 0.61) % 1))) for i, a in enumerate(np.linspace(0, 2 * math.pi, 40, endpoint=False))]
        for i, p in enumerate(pts):
            for j in (i + 1, i + 7):
                if j < len(pts) and (i % 3 != 0 or k > 0.5): dr.line((p, pts[j]), fill=mul((255, 210, 120), 0.3 + 0.7 * k), width=2)
        for i, (x, y) in enumerate(pts): person(dr, x, y + 30, 0.7, SKINS[i % 5])
        put(img, L_PEOPLE, 540, 620, ss(113.2, 114.0, t))
        return img
    y = 1100
    dr.line((60, y, 1020, y), fill=(255, 210, 120), width=4)
    for fx, c in STAGES:
        x = 60 + 960 * fx; dr.ellipse((x - 18, y - 18, x + 18, y + 18), fill=c)
    yk = ss(121.8, 122.8, t)
    if yk > 0:
        img = add_glow(img, glow_at(1000, y - 120, 120, 160, 120), yk); dr = ImageDraw.Draw(img)
        you_outline(dr, 1000, y + 10, 0.55, yk)
        dr.ellipse((1000 - 18, y - 18, 1000 + 18, y + 18), fill=(255, 235, 180))
    put(img, L_KEEP, 540, 620, ss(117.6, 118.4, t) * (1 - ss(121.4, 121.8, t)))
    put(img, L_YOU, 540, 620, ss(121.8, 122.6, t))
    return img

def render(t):
    if t < 6.0: return render23(134.1 + t)
    if t < 14.8: return dim(band(t), ss(6.0, 6.6, t) * (1 - ss(14.2, 14.8, t)))
    if t < 36.2:
        k = ss(14.8, 15.4, t) * (1 - ss(35.6, 36.2, t))
        if 27.2 < t < 28.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 27.2) / 0.8)
        return dim(network(t), k)
    if t < 53.2:
        k = ss(36.2, 36.8, t) * (1 - ss(52.6, 53.2, t))
        if 44.2 < t < 45.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 44.2) / 0.8)
        return dim(stories(t), k)
    if t < 66.0:
        k = ss(53.2, 53.8, t) * (1 - ss(65.4, 66.0, t))
        for a in (57.0, 61.2):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(art(t), k)
    if t < 74.6: return dim(teach(t), ss(66.0, 66.6, t) * (1 - ss(74.0, 74.6, t)))
    if t < 96.0:
        k = ss(74.6, 75.2, t) * (1 - ss(95.4, 96.0, t))
        if 82.8 < t < 83.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 82.8) / 0.8)
        return dim(scale_up(t), k)
    if t < 104.6: return dim(debate(t), ss(96.0, 96.6, t) * (1 - ss(104.0, 104.6, t)))
    k = ss(104.6, 105.2, t)
    for a in (108.4, 112.6, 117.0):
        if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
    return dim(finale(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep24_{ts}.png')
