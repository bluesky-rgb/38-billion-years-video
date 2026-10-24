import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK
from ep22 import sapiens, glow_at, add_glow, you_outline
from ep23 import world, P, OCEAN
from ep24 import person, SKINS, STAGES
from ep27 import DESERT
from ep28 import BRONZE, WARM
from ep29 import render as render29

CLEAN = False
NIGHT_OCEAN = grad((8, 16, 34), (4, 10, 22))

def route(dr, pts, k, col, w=6):
    segs = list(zip(pts, pts[1:])); n = len(segs)
    for i, (a, b) in enumerate(segs):
        f = min(1.0, max(0.0, k * n - i))
        if f <= 0: break
        (ax, ay), (bx, by) = P(*a), P(*b)
        dr.line((ax, ay, lerp(ax, bx, f), lerp(ay, by, f)), fill=col, width=w)
def mover(dr, pts, q, col, r=9):
    segs = list(zip(pts, pts[1:])); n = len(segs)
    i = min(int(q * n), n - 1); f = q * n - i
    (ax, ay), (bx, by) = P(*segs[i][0]), P(*segs[i][1])
    x, y = lerp(ax, bx, f), lerp(ay, by, f)
    dr.ellipse((x - r, y - r, x + r, y + r), fill=col)

# ---------- B: Silk Road ----------
SILK = [(0.52, 0.30), (0.44, 0.30), (0.36, 0.30), (0.28, 0.34), (0.18, 0.28), (0.10, 0.26)]
L_ZQ = text_img('张骞出使西域', FB, 42, (255, 225, 160), 3)
L_SILK = text_img('丝绸之路：中国 → 中亚 → 波斯 → 罗马', FB, 36, (255, 235, 200), 3)
L_GOODS = text_img('丝绸、香料、纸和佛教，沿路传播', FB, 38, (255, 225, 160), 3)
def silk(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr)
    k = ss(11.0, 16.0, t)
    route(dr, SILK, k, (240, 200, 110), 7)
    if t > 16.0:
        for j in range(5):
            mover(dr, SILK if j % 2 else SILK[::-1], ((t - 16) * 0.12 + j / 5) % 1, [(240, 230, 210), (220, 160, 90), (200, 220, 240)][j % 3])
    put(img, L_ZQ, 540, 520, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_SILK, 540, 520, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_GOODS, 540, 520, ss(19.2, 20.0, t))
    return img

# ---------- C: printing ----------
L_MOV = text_img('中国：活字印刷', FB, 42, (255, 225, 160), 3)
L_GUT = text_img('欧洲：古登堡的金属活字', FB, 42, (255, 225, 160), 3)
L_COPY = text_img('知识第一次能便宜地大量复制', FB, 40, (255, 235, 200), 3)
CHARS = '天地人和山水日月风云'
L_CH = [text_img(c, FB, 46, (60, 40, 25), 0) for c in CHARS]
def printing(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 32.0:
        n = int(10 * ss(23.6, 27.0, t)) if t < 27.8 else 10
        for i in range(n):
            x = 300 + (i % 5) * 120; y = 900 + (i // 5) * 130
            dr.rectangle((x - 50, y - 50, x + 50, y + 50), fill=(205, 175, 130), outline=(140, 110, 70), width=3)
            put(img, L_CH[i], x, y, 1.0)
        if t > 27.8:
            dr.rectangle((230, 820, 850, 1130), outline=(200, 200, 210), width=6)
            for i in range(10):
                x = 300 + (i % 5) * 120; y = 900 + (i // 5) * 130
                dr.rectangle((x - 50, y - 50, x + 50, y + 50), fill=(150, 152, 160))
        put(img, L_MOV, 540, 640, ss(23.6, 24.4, t) * (1 - ss(27.4, 27.8, t)))
        put(img, L_GUT, 540, 640, ss(27.8, 28.6, t))
        return img
    k = ss(32.2, 35.6, t)
    n = int(1 + 40 * k)
    for i in range(n):
        x = 160 + (i % 8) * 110 + (i // 8 % 2) * 20; y = 820 + (i // 8) * 140
        dr.rectangle((x - 40, y - 55, x + 40, y + 55), fill=(240, 235, 220), outline=(170, 160, 140), width=2)
        for j in range(4): dr.line((x - 28, y - 38 + j * 22, x + 28, y - 38 + j * 22), fill=(120, 110, 100), width=3)
    put(img, L_COPY, 540, 640, ss(32.2, 33.0, t))
    return img

# ---------- D: oceans ----------
ZHENG = [(0.52, 0.42), (0.48, 0.58), (0.40, 0.56), (0.32, 0.52), (0.26, 0.56), (0.22, 0.66)]
COLUMB = [(0.06, 0.32), (0.20, 0.40), (0.50, 0.40), (0.80, 0.40)]
COL2 = [(0.04, 0.36), (0.40, 0.42), (0.80, 0.42)]
L_ZH = text_img('郑和七下西洋', FB, 42, (255, 225, 160), 3)
L_COL = text_img('哥伦布到达美洲', FB, 42, (255, 225, 160), 3)
L_EX = text_img('作物、动物、疾病和人，跟着交换', FB, 38, (255, 235, 200), 3)
L_DARK = text_img('也带来了殖民和奴隶贸易', FB, 40, (255, 180, 160), 3)
def oceans(t):
    img = Image.fromarray(OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr)
    route(dr, ZHENG, ss(36.6, 40.0, t), (240, 200, 110), 6)
    if t > 40.4:
        pts = [(0.12, 0.30), (0.40, 0.36), (0.78, 0.42)]
        (ax, ay), (bx, by), (cx, cy) = P(*pts[0]), P(*pts[1]), P(*pts[2])
        k = ss(40.6, 43.6, t)
        mid = lambda q: ((1 - q) ** 2 * ax + 2 * (1 - q) * q * bx + q * q * cx, (1 - q) ** 2 * ay + 2 * (1 - q) * q * by + q * q * cy)
        prev = mid(0)
        for i in range(1, int(40 * k) + 1):
            cur = mid(i / 40); dr.line((prev, cur), fill=(200, 230, 255), width=6); prev = cur
    if t > 44.6:
        for j in range(6):
            q = ((t - 44.6) * 0.18 + j / 6) % 1
            if j % 2: q = 1 - q
            x, y = lerp(P(0.14, 0.34)[0], P(0.78, 0.42)[0], q), lerp(P(0.14, 0.34)[1], P(0.78, 0.42)[1], q) - 60 * math.sin(math.pi * q)
            dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=[(130, 200, 120), (240, 200, 80), (200, 120, 90)][j % 3])
    if t > 48.8:
        a = ss(49.0, 50.0, t)
        for j in range(4):
            q = ((t - 48.8) * 0.15 + j / 4) % 1
            x, y = lerp(P(0.20, 0.56)[0], P(0.84, 0.60)[0], q), lerp(P(0.20, 0.56)[1], P(0.84, 0.60)[1], q)
            dr.rectangle((x - 10, y - 6, x + 10, y + 6), fill=mul((200, 70, 60), a))
    put(img, L_ZH, 540, 520, ss(36.6, 37.4, t) * (1 - ss(40.2, 40.6, t)))
    put(img, L_COL, 540, 520, ss(40.6, 41.4, t) * (1 - ss(44.4, 44.8, t)))
    put(img, L_EX, 540, 520, ss(44.8, 45.6, t) * (1 - ss(48.6, 49.0, t)))
    put(img, L_DARK, 540, 520, ss(49.0, 49.8, t))
    return img

# ---------- E: industry ----------
L_STEAM = text_img('蒸汽机：工业革命', FB, 42, (255, 225, 160), 3)
L_FAST = text_img('工厂、铁路、轮船：更快、更远', FB, 40, (255, 235, 200), 3)
SMOG = grad((150, 150, 150), (200, 190, 170), 480, 1100)
def industry(t):
    img = Image.fromarray(SMOG.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(110, 100, 90))
    for i, x in enumerate((140, 330, 520)):
        dr.rectangle((x - 70, GROUND - 200, x + 70, GROUND), fill=(140, 80, 60))
        dr.polygon([(x - 70, GROUND - 200), (x - 35, GROUND - 240), (x, GROUND - 200), (x + 35, GROUND - 240), (x + 70, GROUND - 200)], fill=(120, 70, 50))
        dr.rectangle((x + 30, GROUND - 400, x + 60, GROUND - 200), fill=(110, 60, 45))
        for j in range(5):
            q = (t * 0.3 + j / 5 + i * 0.13) % 1
            r = 20 + 40 * q
            dr.ellipse((x + 45 - r + 60 * q, GROUND - 420 - 260 * q - r, x + 45 + r + 60 * q, GROUND - 420 - 260 * q + r), fill=mul((90, 88, 86), 1 - 0.5 * q))
    dr.line((0, GROUND + 140, W, GROUND + 140), fill=(80, 70, 60), width=6); dr.line((0, GROUND + 170, W, GROUND + 170), fill=(80, 70, 60), width=6)
    for k in range(30): dr.rectangle((k * 40, GROUND + 136, k * 40 + 12, GROUND + 176), fill=(100, 80, 60))
    if t > 57.4:
        tx = lerp(-400, 1400, ss(57.6, 65.0, t))
        dr.rectangle((tx, GROUND + 40, tx + 180, GROUND + 140), fill=(40, 40, 45)); dr.rectangle((tx + 130, GROUND - 20, tx + 170, GROUND + 40), fill=(40, 40, 45))
        for j in range(3): dr.rectangle((tx - 200 * (j + 1), GROUND + 60, tx - 200 * (j + 1) + 180, GROUND + 140), fill=(120, 60, 50))
        for j in range(4):
            r = 20 + 15 * j; dr.ellipse((tx + 150 - 50 * j - r, GROUND - 60 - 40 * j - r, tx + 150 - 50 * j + r, GROUND - 60 - 40 * j + r), fill=(200, 200, 200))
    put(img, L_STEAM, 540, 640, ss(53.6, 54.4, t) * (1 - ss(57.2, 57.6, t)))
    put(img, L_FAST, 540, 640, ss(57.6, 58.4, t))
    return img

# ---------- F: telegraph -> internet ----------
L_TEL = text_img('电报、电话', FB, 42, (255, 225, 160), 3)
L_NET = text_img('互联网：消息从几个月，变成一瞬间', FB, 38, (255, 235, 200), 3)
CITIES = [(0.08, 0.24), (0.16, 0.30), (0.12, 0.60), (0.26, 0.40), (0.42, 0.22), (0.52, 0.32), (0.50, 0.54), (0.62, 0.76), (0.78, 0.22), (0.86, 0.36), (0.88, 0.70), (0.34, 0.30)]
def network(t):
    img = Image.fromarray(NIGHT_OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr, land=(50, 56, 66))
    k1 = ss(66.4, 69.6, t); k2 = ss(70.6, 74.4, t)
    pairs = [(i, j) for i in range(len(CITIES)) for j in range(i + 1, len(CITIES))]
    for n, (i, j) in enumerate(pairs):
        if n % 6 == 0 and n / len(pairs) < k1 + 0.01:
            dr.line((P(*CITIES[i]), P(*CITIES[j])), fill=(200, 170, 110), width=2)
        elif n / len(pairs) < k2:
            dr.line((P(*CITIES[i]), P(*CITIES[j])), fill=(110, 190, 255), width=1)
    for c in CITIES:
        x, y = P(*c); dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 230, 160))
    if t > 70.6:
        for j in range(16):
            i, jj = pairs[(j * 7) % len(pairs)]
            q = ((t - 70.6) * 1.2 + j / 16) % 1
            (ax, ay), (bx, by) = P(*CITIES[i]), P(*CITIES[jj])
            dr.ellipse((lerp(ax, bx, q) - 5, lerp(ay, by, q) - 5, lerp(ax, bx, q) + 5, lerp(ay, by, q) + 5), fill=(220, 245, 255))
    put(img, L_TEL, 540, 520, ss(66.4, 67.2, t) * (1 - ss(70.2, 70.6, t)))
    put(img, L_NET, 540, 520, ss(70.6, 71.4, t))
    return img

# ---------- G: billions cooperating ----------
L_BIL = text_img('几十亿陌生人，一起合作', FB, 44, (255, 225, 160), 3)
L_INST = [text_img(s_, FB, 34, (255, 235, 200), 3) for s_ in ('货币', '法律', '国家', '公司', '网络')]
L_STORY = text_img('靠的，还是共同的故事和规则', FB, 40, (255, 235, 200), 3)
_r = np.random.default_rng(301)
LIGHTS = [P(_r.random(), _r.random()) for _ in range(1800)]
def billions(t):
    img = Image.fromarray(NIGHT_OCEAN.astype(np.uint8)); dr = ImageDraw.Draw(img)
    world(dr, land=(40, 46, 56))
    arr = np.asarray(img)
    for px, py in LIGHTS:
        if arr[int(py), int(px)][0] > 30:
            dr.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(255, 225, 150))
    for i, lab in enumerate(L_INST):
        put(img, lab, 140 + i * 200, 1420, ss(79.2 + i * 0.5, 79.8 + i * 0.5, t))
    put(img, L_BIL, 540, 520, ss(79.0, 79.8, t) * (1 - ss(82.8, 83.2, t)))
    put(img, L_STORY, 540, 520, ss(83.2, 84.0, t))
    return img

# ---------- H: new problems ----------
L_NEW = text_img('合作越大，问题也越大', FB, 42, (255, 200, 170), 3)
L_PB = [text_img(s_, FB, 38, (240, 240, 245), 3) for s_ in ('贫富差距', '战争', '环境压力')]
def problems(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_NEW, 540, 640, ss(87.6, 88.4, t))
    for i, lab in enumerate(L_PB):
        a = ss(88.4 + i * 1.0, 89.2 + i * 1.0, t)
        if a <= 0: continue
        y = 900 + i * 200
        dr.rounded_rectangle((220, y - 70, 860, y + 70), radius=24, fill=mul((40, 30, 30), a), outline=mul((230, 120, 100), a), width=3)
        put(img, lab, 540, y, a)
    return img

# ---------- I: 38 billion years ----------
L_38 = text_img('38 亿年', FB, 70, (255, 225, 160), 5)
L_COOP = text_img('生命一直在寻找新的合作方式', FB, 40, (255, 225, 160), 3)
L_TOP = text_img('人类社会：最新、也最复杂的一层', FB, 38, (255, 235, 200), 3)
L_NEXT = text_img('接下来会怎样？', FB, 46, (255, 225, 160), 4)
L_US = text_img('取决于我们一起讲什么样的故事', FB, 40, (255, 235, 200), 3)
L_STAGE = [text_img(s_, FM, 28, (220, 220, 230), 3) for s_ in ('地球', '细胞', '多细胞', '脊椎', '登陆', '哺乳', '人类')]
def recap(t):
    img = Image.fromarray(grad((10, 12, 26), (24, 20, 36)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for i in range(80):
        dr.point(((i * 151) % W, 480 + (i * 89) % 1400), fill=(180, 180, 210))
    y = 1060
    k = ss(91.8, 95.0, t)
    dr.line((60, y, 60 + 960 * k, y), fill=(255, 210, 120), width=4)
    for i, (fx, c) in enumerate(STAGES):
        if fx <= k + 0.03:
            x = 60 + 960 * fx; dr.ellipse((x - 18, y - 18, x + 18, y + 18), fill=c)
            put(img, L_STAGE[i], x, y + 52, 1.0)
    if t > 95.6:
        nk = ss(95.8, 98.6, t)
        x0 = 60 + 960 * 0.82
        for j in range(30):
            ang = -math.pi / 2 + (j - 15) * 0.06; r = 60 + (j * 37) % 200
            ex, ey = x0 + 120 * nk + r * math.cos(ang) * 0.5 * nk, y - r * nk
            dr.line((x0, y, ex, ey), fill=mul((255, 210, 120), 0.5 * nk), width=2)
            dr.ellipse((ex - 5, ey - 5, ex + 5, ey + 5), fill=mul((255, 235, 180), nk))
    if t > 100.0:
        yk = ss(100.2, 101.2, t)
        img = add_glow(img, glow_at(1000, y - 120, 120, 160, 120), yk); dr = ImageDraw.Draw(img)
        you_outline(dr, 1000, y + 10, 0.55, yk)
    put(img, L_38, 540, 760, ss(91.8, 92.6, t) * (1 - ss(95.4, 95.8, t)))
    put(img, L_COOP, 540, 640, ss(95.8, 96.6, t) * (1 - ss(99.8, 100.2, t)))
    put(img, L_TOP, 540, 640, ss(100.2, 101.0, t) * (1 - ss(104.2, 104.6, t)))
    put(img, L_NEXT, 540, 640, ss(104.6, 105.4, t) * (1 - ss(108.4, 108.8, t)))
    put(img, L_US, 540, 640, ss(108.8, 109.6, t))
    return img

def render(t):
    if t < 10.6: return dim(render29(132.7 + min(t, 6.0)), 1 - ss(10.0, 10.6, t) if t > 6 else 1.0)
    if t < 23.4: return dim(silk(t), ss(10.6, 11.2, t) * (1 - ss(22.8, 23.4, t)))
    if t < 36.2:
        k = ss(23.4, 24.0, t) * (1 - ss(35.6, 36.2, t))
        if 31.6 < t < 32.4: k *= 1 - 0.85 * math.sin(math.pi * (t - 31.6) / 0.8)
        return dim(printing(t), k)
    if t < 53.2: return dim(oceans(t), ss(36.2, 36.8, t) * (1 - ss(52.6, 53.2, t)))
    if t < 66.0: return dim(industry(t), ss(53.2, 53.8, t) * (1 - ss(65.4, 66.0, t)))
    if t < 78.8: return dim(network(t), ss(66.0, 66.6, t) * (1 - ss(78.2, 78.8, t)))
    if t < 87.4: return dim(billions(t), ss(78.8, 79.4, t) * (1 - ss(86.8, 87.4, t)))
    if t < 91.6: return dim(problems(t), ss(87.4, 88.0, t) * (1 - ss(91.0, 91.6, t)))
    return dim(recap(t), ss(91.6, 92.2, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep30_{ts}.png')
