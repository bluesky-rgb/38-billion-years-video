import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import sea, mul
from ep10 import chase

CLEAN = False
rng = np.random.default_rng(111)
yy = np.arange(H, dtype=np.float32)[:, None, None]
CAMB_BG = (np.array([30, 95, 115]) * (1 - yy / H) + np.array([8, 32, 42]) * (yy / H)) * np.ones((1, W, 1))
FLOOR = 1470

def camb_bg(t):
    img = Image.fromarray(np.clip(CAMB_BG, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, FLOOR, W, H), fill=(110, 95, 75))
    for k in range(36):
        x = (k * 101) % W; dr.ellipse((x - 34, FLOOR - 6 + (k % 4) * 8, x + 34, FLOOR + 10 + (k % 4) * 8), fill=(125, 108, 85))
    for k in range(50):
        x = (k * 211 + t * 6) % W; y = (k * 337 - t * 10) % FLOOR
        dr.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(70, 120, 130))
    return img, dr

def trilobite(dr, x, y, s, a=1.0):
    dr.ellipse((x - 46 * s, y - 30 * s, x + 46 * s, y + 30 * s), fill=mul((150, 120, 90), a), outline=mul((95, 75, 55), a), width=2)
    dr.chord((x + 10 * s, y - 30 * s, x + 66 * s, y + 30 * s), 270, 90, fill=mul((165, 135, 100), a), outline=mul((95, 75, 55), a))
    for j in range(-3, 3):
        dr.line((x + j * 13 * s, y - 28 * s, x + j * 13 * s, y + 28 * s), fill=mul((110, 88, 65), a), width=2)
    dr.line((x - 46 * s, y, x + 46 * s, y), fill=mul((110, 88, 65), a), width=2)
    for dy in (-14, 14):
        dr.ellipse((x + 40 * s - 6 * s, y + dy * s - 6 * s, x + 40 * s + 6 * s, y + dy * s + 6 * s), fill=mul((40, 40, 45), a))

def anomalo(dr, x, y, s, t, a=1.0, face=1):
    for j in range(10):
        lx = x - face * j * 26 * s; w = (40 - j * 2.5) * s
        flap = 10 * s * math.sin(t * 6 - j * 0.7)
        dr.ellipse((lx - 22 * s, y - w - flap, lx + 22 * s, y + w + flap), fill=mul((200, 110, 90), a), outline=mul((140, 70, 55), a), width=2)
    hx = x + face * 30 * s
    dr.ellipse((hx - 30 * s, y - 26 * s, hx + 30 * s, y + 26 * s), fill=mul((215, 125, 100), a))
    for dy in (-1, 1):
        dr.ellipse((hx - 8 * s, y + dy * 30 * s - 9 * s, hx + 10 * s, y + dy * 30 * s + 9 * s), fill=mul((30, 30, 35), a))
        pts = [(hx + face * (20 + k * 12) * s, y + dy * (6 + k * 9 - (k * k) * 1.3) * s) for k in range(8)]
        dr.line(pts, fill=mul((230, 150, 120), a), width=int(9 * s))

def sponge(dr, x, s):
    dr.polygon([(x - 30 * s, FLOOR), (x - 40 * s, FLOOR - 160 * s), (x - 20 * s, FLOOR - 220 * s), (x + 20 * s, FLOOR - 220 * s), (x + 40 * s, FLOOR - 160 * s), (x + 30 * s, FLOOR)], fill=(200, 170, 110), outline=(160, 130, 85))

TRI = [(rng.random() * W, FLOOR - 20 - rng.random() * 40, 0.7 + rng.random() * 0.6, rng.random() * 6) for _ in range(9)]
L_O2 = text_img('氧气', FB, 40, (200, 235, 255), 3); L_PR = text_img('捕食', FB, 40, (255, 170, 150), 3); L_GN = text_img('基因工具', FB, 40, (200, 210, 255), 3)
L_TRI = text_img('三叶虫', FB, 42, (240, 220, 180), 3); L_ANO = text_img('奇虾', FB, 46, (255, 190, 170), 3)
def explosion(t):
    img, dr = camb_bg(t)
    n = 1 + int(ss(15.6, 23.0, t) * 8.99)
    for k, x in enumerate([120, 330, 760, 960][:max(0, n - 4)]): sponge(dr, x, 0.8 + 0.1 * k)
    for i, (x0, y0, s, ph) in enumerate(TRI[:n]):
        x = (x0 + (t - 15) * 14 * (1 if i % 2 else -1)) % (W + 120) - 60
        trilobite(dr, x, y0, s)
    if 28.0 <= t < 32.4:
        a = ss(28.2, 29.0, t) * (1 - ss(31.8, 32.4, t))
        for j, (lab, col) in enumerate(((L_O2, (120, 190, 240)), (L_PR, (220, 110, 90)), (L_GN, (140, 150, 240)))):
            x = 220 + j * 320
            dr.ellipse((x - 90, 760 - 90, x + 90, 760 + 90), fill=mul((15, 30, 40), a), outline=mul(col, a), width=4)
            put(img, lab, x, 760, a)
    if t > 36.2:
        k = ss(36.4, 39.5, t)
        anomalo(dr, lerp(-260, 760, k), 900 + 40 * math.sin(t), 1.5, t)
    put(img, L_TRI, TRI[0][0] % W, FLOOR - 140, ss(32.6, 33.4, t) * (1 - ss(36.0, 36.6, t)))
    put(img, L_ANO, lerp(-260, 760, ss(36.4, 39.5, t)), 720, ss(37.4, 38.2, t))
    if 32.2 < t < 36.4:
        g = ss(32.6, 33.4, t) * (0.6 + 0.4 * math.sin(t * 5))
        x = TRI[1][0] % W
        dr.ellipse((x - 70, TRI[1][1] - 60, x + 90, TRI[1][1] + 60), outline=mul((255, 220, 140), g), width=3)
    return img

# ---------- chordate diagram ----------
X0, X1, Y0 = 170, 900, 960
def wave(x, t, amp):
    return amp * ((x - X0) / (X1 - X0)) ** 0.7 * math.sin((x - X1) / 160 - t * 6) if amp else 0.0
L_NOTO = text_img('脊索', FB, 42, (170, 230, 255), 3); L_MYO = text_img('肌节', FB, 42, (255, 190, 140), 3)
L_NT = text_img('神经管', FB, 42, (255, 230, 130), 3); L_BR = text_img('脑', FB, 46, (255, 230, 130), 3)
L_RING = text_img('软骨环', FB, 42, (230, 230, 240), 3); L_SPINE = text_img('脊椎', FB, 48, (255, 225, 160), 3)
def chordate(t, rings=0.0):
    img, dr = sea(t + 500)
    amp = 60 * ss(53.8, 55.0, t) * (1 - ss(57.0, 57.8, t)) if t < 66 else 0
    xs = np.linspace(X0, X1, 50)
    top, bot = [], []
    for x in xs:
        u = (x - X0) / (X1 - X0)
        hw = 80 * math.sin(math.pi * min(1.0, u * 0.95 + 0.05)) ** 0.7 + 8
        w = wave(x, t, amp)
        top.append((x, Y0 - hw + w)); bot.append((x, Y0 + hw + w))
    dr.polygon(top + bot[::-1], fill=(200, 175, 160), outline=(235, 210, 195))
    mk = ss(49.6, 51.0, t)
    if mk > 0:
        for j in range(16):
            x = lerp(X0 + 60, X1 - 70, j / 15); w = wave(x, t, amp)
            u = (x - X0) / (X1 - X0); hw = 70 * math.sin(math.pi * min(1.0, u * 0.95 + 0.05)) ** 0.7
            dr.line((x + 14, Y0 - hw + w, x - 10, Y0 + w, ), fill=mul((225, 140, 95), mk), width=4)
            dr.line((x - 10, Y0 + w, x + 14, Y0 + hw + w), fill=mul((225, 140, 95), mk), width=4)
    nk = ss(41.4, 43.6, t)
    if nk > 0:
        xe = lerp(X0 + 30, X1 - 40, nk)
        pts = [(x, Y0 + wave(x, t, amp)) for x in np.linspace(X0 + 30, xe, 30)]
        dr.line(pts, fill=(140, 220, 250), width=16); dr.line(pts, fill=(200, 245, 255), width=6)
    tk = ss(58.0, 59.6, t)
    if tk > 0:
        xe = lerp(X0 + 50, X1 - 60, tk)
        pts = [(x, Y0 - 34 + wave(x, t, amp)) for x in np.linspace(X0 + 50, xe, 30)]
        dr.line(pts, fill=(250, 220, 110), width=14); dr.line(pts, fill=(200, 175, 160), width=5)
    bk = ss(62.2, 63.6, t)
    if bk > 0:
        bx = X1 - 70; by = Y0 - 34 + wave(bx, t, amp)
        r = 34 * bk
        dr.ellipse((bx - r, by - r * 0.8, bx + r, by + r * 0.8), fill=(255, 230, 130), outline=(255, 250, 200), width=2)
    if rings > 0:
        nr = int(rings * 14)
        for j in range(nr):
            x = lerp(X0 + 60, X1 - 110, j / 13)
            dr.rounded_rectangle((x - 18, Y0 - 26, x + 18, Y0 + 26), radius=8, fill=(225, 225, 235), outline=(150, 150, 165), width=2)
    put(img, L_NOTO, CX, Y0 + 150, ss(45.4, 46.2, t) * (1 - ss(49.0, 49.6, t)) if t < 66 else 0)
    put(img, L_MYO, CX, Y0 + 150, ss(49.8, 50.6, t) * (1 - ss(53.4, 54.0, t)) if t < 66 else 0)
    put(img, L_NT, CX, Y0 - 160, ss(58.2, 59.0, t) * (1 - ss(65.4, 66.0, t)) if t < 66 else 0)
    put(img, L_BR, X1 - 70, Y0 - 140, ss(62.6, 63.4, t) if t < 66 else 0)
    if rings > 0:
        put(img, L_RING, CX, Y0 + 150, ss(75.6, 76.4, t) * (1 - ss(79.0, 79.6, t)))
        put(img, L_SPINE, CX, Y0 + 150, ss(79.4, 80.2, t))
    return img

def haikou(dr, x, y, s, t, a=1.0, mouth=0.0):
    pts = []
    for p in np.linspace(0, 2 * math.pi, 50):
        r = 1.0
        pts.append((x + 90 * s * math.cos(p), y + 26 * s * math.sin(p) + 6 * s * math.sin(math.cos(p) * 3 - t * 8)))
    dr.polygon(pts, fill=mul((190, 170, 150), a), outline=mul((140, 120, 100), a))
    dr.polygon([(x - 40 * s, y - 24 * s), (x + 20 * s, y - 42 * s), (x + 40 * s, y - 22 * s)], fill=mul((175, 155, 135), a))
    dr.ellipse((x + 62 * s, y - 10 * s, x + 74 * s, y + 2 * s), fill=mul((30, 30, 35), a))
    for j in range(5):
        gx = x + (40 - j * 9) * s
        dr.line((gx, y - 6 * s, gx, y + 14 * s), fill=mul((130, 100, 85), a), width=2)
    for j in range(9):
        cx = x + (-60 + j * 12) * s
        dr.line((cx + 5 * s, y - 18 * s, cx - 3 * s, y, ), fill=mul((165, 135, 115), a), width=2)
    if mouth > 0:
        mr = 12 * s * mouth
        dr.ellipse((x + 88 * s - mr, y - mr, x + 88 * s + mr, y + mr), fill=mul((60, 30, 30), a), outline=mul((200, 150, 130), a), width=2)
L_HK = text_img('海口鱼', FB, 46, (240, 225, 200), 3)
def haikou_scene(t):
    img, dr = camb_bg(t)
    for i, (x0, y0, s, ph) in enumerate(TRI[:6]):
        trilobite(dr, (x0 + (t - 60) * 10) % (W + 120) - 60, y0, s)
    x = lerp(200, 700, ss(66.4, 74.4, t)); y = 980 + 40 * math.sin(t * 1.5)
    haikou(dr, x, y, 2.2, t)
    put(img, L_HK, x, y - 150, ss(66.8, 67.6, t))
    return img

L_SUCK = text_img('没有下巴：只能吸食', FM, 38, (230, 220, 210), 3)
def escape(t):
    img, dr = camb_bg(t)
    if t < 87.8:
        k = ss(83.6, 87.6, t)
        fx = lerp(560, 1250, k ** 1.4); ax = lerp(-150, 520, k)
        haikou(dr, fx, 950 + 30 * math.sin(t * 3), 1.8, t * 1.8)
        anomalo(dr, ax, 960, 1.4, t)
        return img
    m = 0.5 + 0.5 * math.sin(t * 4)
    haikou(dr, 520, 960, 3.2, t, mouth=0.4 + 0.6 * m)
    for j in range(10):
        q = (t * 0.5 + j / 10) % 1
        px = lerp(980, 520 + 88 * 3.2, q); py = 960 + (j - 5) * 18 * (1 - q)
        dr.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(200, 210, 150))
    put(img, L_SUCK, 540, 1180, ss(88.2, 89.0, t))
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 15.2: return dim(chase(t + 70), 1 - ss(14.6, 15.2, t))
    if t < 40.8: return dim(explosion(t), ss(15.2, 15.8, t) * (1 - ss(40.2, 40.8, t)))
    if t < 66.2: return dim(chordate(t), ss(40.8, 41.4, t) * (1 - ss(65.6, 66.2, t)))
    if t < 74.8: return dim(haikou_scene(t), ss(66.2, 66.8, t) * (1 - ss(74.2, 74.8, t)))
    if t < 83.4: return dim(chordate(t, rings=ss(75.2, 78.8, t)), ss(74.8, 75.4, t) * (1 - ss(82.8, 83.4, t)))
    return dim(escape(t), ss(83.4, 84.0, t))

CAPS = [(6.4, 10.6, '约 5.4 亿年前，捕食者和猎物你追我逃'), (10.6, 14.8, '氧气继续增多，海底被翻得乱七八糟'),
        (15.4, 19.6, '约 5.39 亿年前，寒武纪大爆发开始了'), (19.6, 23.8, '两千万年里，大多数动物类群纷纷登场'),
        (23.8, 28.0, '为什么这么快？几个原因叠在了一起'), (28.0, 32.2, '氧气够了，捕食逼人，基因工具也齐了'),
        (32.2, 36.4, '有的长出硬壳，有的长出眼睛'), (36.4, 40.6, '顶级捕食者，是一米长的奇虾'),
        (41.0, 45.2, '有一类小动物，背上长出一根有弹性的软棒'), (45.2, 49.4, '它叫脊索，像弹簧一样撑起身体'),
        (49.4, 53.6, '两侧肌肉一节一节排列，左右交替收缩'), (53.6, 57.8, '身体左右甩动，游得飞快'),
        (57.8, 62.0, '脊索上方，是一条空心的神经管'), (62.0, 66.0, '神经管的前端，膨大成了脑'),
        (66.4, 70.6, '比如云南澄江的海口鱼，约 5.18 亿年前'), (70.6, 74.6, '它是已知最早的脊椎动物之一'),
        (75.0, 79.2, '后来，脊索周围长出一节节软骨环'), (79.2, 83.2, '变成了脊椎：既能弯曲，又很结实'),
        (83.6, 87.8, '游得快，就能躲开奇虾'), (87.8, 92.0, '但它们还没有下巴，只能张嘴吸食')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep11_{ts}.png')
