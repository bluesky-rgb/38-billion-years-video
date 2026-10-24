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
from ep26 import sack
from ep27 import tablet, wedge, DESERT, CLAY, CLAY_D, render as render27

CLEAN = False
SILVER = (205, 208, 215); BRONZE = (170, 120, 70); WARM = grad((58, 48, 40), (30, 24, 20))

def silver_bit(dr, x, y, s):
    dr.polygon([(x - 22 * s, y), (x - 8 * s, y - 14 * s), (x + 20 * s, y - 10 * s), (x + 24 * s, y + 6 * s), (x, y + 14 * s)], fill=SILVER, outline=(150, 152, 160))
def cowrie(dr, x, y, s):
    dr.ellipse((x - 26 * s, y - 36 * s, x + 26 * s, y + 36 * s), fill=(240, 228, 200), outline=(190, 170, 130), width=2)
    dr.line((x, y - 26 * s, x, y + 26 * s), fill=(120, 90, 60), width=max(2, int(4 * s)))
    for j in range(5): dr.line((x - 6 * s, y - 20 * s + j * 10 * s, x + 6 * s, y - 20 * s + j * 10 * s), fill=(150, 120, 80), width=2)
def scale_beam(dr, cx, cy, tilt, left, right):
    dr.line((cx, cy, cx, cy + 300), fill=(120, 100, 70), width=10)
    lx, ly = cx - 260, cy - 60 * tilt; rx, ry = cx + 260, cy + 60 * tilt
    dr.line((lx, ly, rx, ry), fill=(150, 125, 80), width=10)
    for (px, py) in ((lx, ly), (rx, ry)):
        dr.line((px, py, px - 70, py + 160), fill=(150, 125, 80), width=3); dr.line((px, py, px + 70, py + 160), fill=(150, 125, 80), width=3)
        dr.chord((px - 100, py + 120, px + 100, py + 200), 0, 180, fill=(170, 145, 95))
    return (lx, ly + 160), (rx, ry + 160)

# ---------- B: silver by weight ----------
L_SIL = text_img('先用白银来算账', FB, 42, (255, 225, 160), 3)
L_WT = text_img('白银按重量计价', FB, 42, (255, 225, 160), 3)
L_EQ = text_img('一份白银 = 一定数量的大麦', FB, 40, (255, 235, 200), 3)
def weigh(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    sk = ss(15.2, 16.4, t); bk = ss(19.2, 21.0, t)
    tilt = -0.8 * sk + 0.8 * bk
    (lx, ly), (rx, ry) = scale_beam(dr, 540, 900, tilt, 0, 0)
    for i in range(int(4 * sk + 0.99) if sk > 0 else 0): silver_bit(dr, lx - 45 + (i % 2) * 50, ly - 10 - (i // 2) * 22, 1.2)
    for i in range(int(4 * bk + 0.99) if bk > 0 else 0): sack(dr, rx - 50 + (i % 2) * 60, ry - (i // 2) * 44, 1.0)
    put(img, L_SIL, 540, 640, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_WT, 540, 640, ss(15.0, 15.8, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_EQ, 540, 640, ss(19.2, 20.0, t))
    return img

# ---------- C: debt and credit ----------
L_LATER = text_img('先拿货，以后再还', FB, 42, (255, 235, 200), 3)
L_DEBT = text_img('欠 10 份大麦', FB, 40, (90, 60, 40), 0)
L_CREDIT = text_img('欠账和信用，可能比硬币还早', FB, 40, (255, 225, 160), 3)
def credit(t):
    img = Image.fromarray(DESERT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    sy = lerp(1050, 560, ss(28.0, 31.6, t))
    dr.ellipse((900 - 40, sy - 40, 900 + 40, sy + 40), fill=(255, 235, 170))
    dr.rectangle((0, GROUND - 40, W, H), fill=(200, 175, 125))
    sapiens(dr, 260, GROUND + 160, 1.2, col=SKINS[0]); sapiens(dr, 820, GROUND + 160, 1.2, col=SKINS[3])
    k = ss(23.8, 26.4, t)
    for i in range(3): sack(dr, lerp(720, 340, k) + i * 40, GROUND + 160, 1.0)
    if t > 27.6:
        a = ss(27.8, 28.6, t)
        tablet(dr, 540, 820, 300, 150, a)
        put(img, L_DEBT, 540, 820, a)
        if t > 31.8:
            ck = ss(32.2, 33.4, t)
            dr.line((400, 760, lerp(400, 680, ck), lerp(760, 880, ck)), fill=(200, 60, 50), width=8)
    put(img, L_LATER, 540, 640, ss(23.6, 24.4, t) * (1 - ss(27.4, 27.8, t)))
    put(img, L_CREDIT, 540, 640, ss(32.0, 32.8, t))
    return img

# ---------- D: cowries ----------
L_COW = text_img('商朝：用海贝当钱', FB, 42, (255, 225, 160), 3)
L_WHY = text_img('小巧 · 耐用 · 难伪造', FB, 42, (255, 235, 200), 3)
L_CHARS = text_img('财  货  贵  赚', FB, 110, (255, 230, 170), 6)
L_BEI = text_img('都带着“贝”', FB, 44, (255, 225, 160), 3)
def cowries(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 44.6:
        n = int(18 * ss(36.4, 38.4, t))
        for i in range(n):
            x = 300 + (i % 6) * 95 + (i // 6 % 2) * 40; y = 930 + (i // 6) * 110
            cowrie(dr, x, y, 1.2)
        put(img, L_COW, 540, 640, ss(36.4, 37.2, t) * (1 - ss(40.2, 40.6, t)))
        put(img, L_WHY, 540, 640, ss(40.6, 41.4, t))
        return img
    put(img, L_CHARS, 540, 1000, ss(44.8, 45.8, t))
    put(img, L_BEI, 540, 1200, ss(45.8, 46.6, t))
    return img

# ---------- E: coins ----------
L_LYD = text_img('吕底亚：最早的铸币', FB, 42, (255, 225, 160), 3)
L_KNIFE = text_img('刀币 · 布币', FB, 42, (255, 225, 160), 3)
L_QIN = text_img('秦：圆形方孔的半两钱', FB, 42, (255, 225, 160), 3)
L_BANLIANG = text_img('半两', FB, 60, (90, 60, 30), 0)
def coins(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 57.4:
        x, y = 540, 1000
        k = ss(53.4, 54.4, t)
        dr.polygon([(x + 170 * (1 + 0.08 * math.sin(5 * a)) * math.cos(a), y + 150 * (1 + 0.08 * math.sin(3 * a)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)], fill=(215, 180, 100), outline=(160, 125, 60))
        if k > 0:
            dr.ellipse((x - 70, y - 50, x + 70, y + 50), outline=mul((140, 100, 40), k), width=6)
            dr.ellipse((x + 20, y - 30, x + 50, y), fill=mul((140, 100, 40), k))
        put(img, L_LYD, 540, 640, ss(49.2, 50.0, t))
        return img
    if t < 61.6:
        dr.rectangle((240, 860, 300, 1140), fill=BRONZE); dr.polygon([(240, 860), (300, 860), (340, 760), (270, 740)], fill=BRONZE)
        dr.ellipse((246, 1130, 294, 1180), outline=BRONZE, width=10)
        dr.polygon([(620, 820), (720, 820), (720, 880), (800, 1100), (720, 1060), (670, 1100), (620, 1060), (540, 1100), (620, 880)], fill=BRONZE)
        put(img, L_KNIFE, 540, 640, ss(57.6, 58.4, t))
        return img
    x, y = 540, 1000
    dr.ellipse((x - 200, y - 200, x + 200, y + 200), fill=BRONZE, outline=(120, 80, 45), width=6)
    dr.rectangle((x - 50, y - 50, x + 50, y + 50), fill=(30, 24, 20))
    put(img, L_BANLIANG, x, y - 120, 1.0) if False else None
    for i, ch in enumerate(('半', '两')):
        im = text_img(ch, FB, 70, (90, 60, 30), 0)
        put(img, im, x - 120 + i * 240, y, ss(61.8, 62.6, t))
    put(img, L_QIN, 540, 640, ss(61.8, 62.6, t))
    return img

# ---------- F: guaranteed ----------
L_STAMP = text_img('印记：重量和成色，有人担保', FB, 40, (255, 225, 160), 3)
def stamp(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    hit = abs(math.sin(t * 3))
    dr.rectangle((380, 1120, 700, 1200), fill=(110, 100, 95))
    dr.ellipse((470, 1080, 610, 1130), fill=SILVER)
    hy = 800 + 260 * (1 - hit)
    dr.rectangle((500, hy - 120, 580, hy), fill=(150, 145, 140)); dr.line((540, hy - 120, 540, hy - 300), fill=(120, 90, 60), width=18)
    if hit > 0.97:
        for j in range(6):
            a = j * math.pi / 3; dr.line((540, 1100, 540 + 70 * math.cos(a), 1100 + 40 * math.sin(a)), fill=(255, 240, 200), width=3)
    put(img, L_STAMP, 540, 640, ss(66.2, 67.0, t))
    return img

# ---------- G: belief, markets ----------
L_EAT = text_img('钱本身：吃不了，穿不了', FB, 42, (255, 200, 170), 3)
L_ALL = text_img('每个人都相信，别人也会收它', FB, 40, (255, 235, 200), 3)
L_STORY = text_img('又一个共同的故事', FB, 46, (255, 225, 160), 4)
L_MARKET = text_img('陌生人之间也能做买卖', FB, 42, (255, 235, 200), 3)
L_GROW = text_img('市场和城市越来越大', FB, 42, (255, 225, 160), 3)
def belief(t):
    if t < 78.8:
        img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
        sapiens(dr, 460, 1300, 1.6, col=SKINS[2])
        dr.ellipse((520, 860, 580, 920), fill=BRONZE)
        k = ss(76.0, 77.0, t)
        if k > 0:
            dr.line((660, 820, 800, 960), fill=mul((230, 80, 70), k), width=10); dr.line((660, 960, 800, 820), fill=mul((230, 80, 70), k), width=10)
        put(img, L_EAT, 540, 640, ss(74.8, 75.6, t))
        return img
    if t < 87.6:
        img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
        pts = [(540 + 340 * math.cos(a), 1020 + 340 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
        for i, (x, y) in enumerate(pts): person(dr, x, y + 30, 1.8, SKINS[i % 5])
        q = (t - 79) * 0.8
        i0 = int(q) % 10; f = q - int(q)
        (ax, ay), (bx, by) = pts[i0], pts[(i0 + 1) % 10]
        cx, cy = lerp(ax, bx, f), lerp(ay, by, f) - 60
        dr.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=BRONZE, outline=(230, 190, 120), width=3)
        if t > 83.2:
            for i in range(10):
                (ax, ay), (bx, by) = pts[i], pts[(i + 1) % 10]
                dr.line((ax, ay - 40, bx, by - 40), fill=mul((255, 210, 120), ss(83.4, 84.4, t)), width=3)
        put(img, L_ALL, 540, 640, ss(79.0, 79.8, t) * (1 - ss(82.8, 83.2, t)))
        put(img, L_STORY, 540, 640, ss(83.4, 84.2, t))
        return img
    img = Image.fromarray(DESERT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 40, W, H), fill=(200, 175, 125))
    g = ss(92.0, 95.0, t)
    for i in range(int(4 + 8 * g)):
        x = 80 + (i * 97) % 920; y = GROUND - 60 - (i // 6) * 40
        dr.rectangle((x - 40, y - 60, x + 40, y), fill=(210, 185, 140), outline=(160, 135, 100), width=2)
    for i in range(5):
        x = 120 + i * 210
        dr.rectangle((x - 70, GROUND + 60, x + 70, GROUND + 140), fill=(170, 120, 80)); dr.polygon([(x - 90, GROUND + 60), (x, GROUND + 10), (x + 90, GROUND + 60)], fill=[(200, 80, 70), (80, 140, 190), (220, 180, 80), (110, 170, 110), (180, 110, 170)][i])
    for i in range(12):
        q = ((t - 87.6) * 0.1 + i / 12) % 1
        person(dr, lerp(-40, 1120, q) if i % 2 else lerp(1120, -40, q), GROUND + 280 + (i % 3) * 50, 1.3, SKINS[i % 5])
    put(img, L_MARKET, 540, 640, ss(87.8, 88.6, t) * (1 - ss(91.6, 92.0, t)))
    put(img, L_GROW, 540, 640, ss(92.0, 92.8, t))
    return img

# ---------- H: origin debate ----------
L_DEB = text_img('货币是怎么出现的？也有争论', FB, 40, (255, 225, 160), 3)
L_A = text_img('以物换物 → 钱', FB, 40, (240, 240, 245), 3); L_B = text_img('欠账 → 钱', FB, 40, (240, 240, 245), 3)
L_A2 = text_img('传统说法', FM, 32, (200, 200, 210), 3); L_B2 = text_img('一些人类学家', FM, 32, (200, 200, 210), 3)
def debate(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_DEB, 540, 640, ss(96.4, 97.2, t))
    for i, (lab, sub, t0) in enumerate(((L_A, L_A2, 100.6), (L_B, L_B2, 104.8))):
        a = ss(t0, t0 + 0.8, t)
        if a <= 0: continue
        y = 920 + i * 280
        dr.rounded_rectangle((180, y - 90, 900, y + 90), radius=26, fill=mul((36, 40, 52), a), outline=mul((255, 210, 130), a), width=3)
        put(img, lab, 540, y - 20, a); put(img, sub, 540, y + 40, a)
    return img

# ---------- I: who guarantees? ----------
L_WHO = text_img('谁来担保钱的价值？', FB, 44, (255, 225, 160), 3)
L_RULER = text_img('往往是统治者', FB, 44, (255, 235, 200), 3)
L_POWER = text_img('统治者的权力，又从哪里来？', FB, 40, (255, 225, 160), 3)
def ruler(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 113.2:
        x, y = 540, 1000
        dr.ellipse((x - 220, y - 220, x + 220, y + 220), fill=SILVER, outline=(150, 152, 160), width=6)
        dr.ellipse((x - 90, y - 120, x + 90, y + 60), outline=(120, 122, 130), width=6)
        dr.polygon([(x - 80, y - 120), (x - 50, y - 180), (x, y - 140), (x + 50, y - 180), (x + 80, y - 120)], fill=(120, 122, 130))
        put(img, L_WHO, 540, 640, ss(109.2, 110.0, t))
        return img
    dr.rectangle((380, 1000, 700, 1320), fill=(80, 52, 34)); dr.rectangle((420, 760, 660, 1010), fill=(95, 62, 40))
    sapiens(dr, 540, 1300, 1.3, col=(190, 145, 105))
    dr.polygon([(500, 870), (515, 830), (540, 860), (565, 830), (580, 870)], fill=(240, 200, 90))
    if t > 117.2:
        g = ss(117.4, 118.4, t) * (0.6 + 0.4 * math.sin(t * 4))
        dr.ellipse((540 - 300, 1000 - 380, 540 + 300, 1000 + 380), outline=mul((255, 210, 120), g), width=4)
    put(img, L_RULER, 540, 640, ss(113.4, 114.2, t) * (1 - ss(117.0, 117.4, t)))
    put(img, L_POWER, 540, 640, ss(117.4, 118.2, t))
    return img

def render(t):
    if t < 10.6: return dim(render27(132.9 + min(t, 6.0)), 1 - ss(10.0, 10.6, t) if t > 6 else 1.0)
    if t < 23.4: return dim(weigh(t), ss(10.6, 11.2, t) * (1 - ss(22.8, 23.4, t)))
    if t < 36.2: return dim(credit(t), ss(23.4, 24.0, t) * (1 - ss(35.6, 36.2, t)))
    if t < 49.0:
        k = ss(36.2, 36.8, t) * (1 - ss(48.4, 49.0, t))
        if 44.2 < t < 45.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 44.2) / 0.8)
        return dim(cowries(t), k)
    if t < 66.0:
        k = ss(49.0, 49.6, t) * (1 - ss(65.4, 66.0, t))
        for a in (57.0, 61.2):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(coins(t), k)
    if t < 74.6: return dim(stamp(t), ss(66.0, 66.6, t) * (1 - ss(74.0, 74.6, t)))
    if t < 96.2:
        k = ss(74.6, 75.2, t) * (1 - ss(95.6, 96.2, t))
        for a in (78.4, 87.2):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(belief(t), k)
    if t < 109.0: return dim(debate(t), ss(96.2, 96.8, t) * (1 - ss(108.4, 109.0, t)))
    k = ss(109.0, 109.6, t)
    if 112.8 < t < 113.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 112.8) / 0.8)
    return dim(ruler(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep28_{ts}.png')
