import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim
from ep16 import GROUND
from ep21 import DARK
from ep22 import sapiens
from ep24 import person, SKINS, bubble
from ep25 import hut, SKY, GOLD
from ep26 import sack
from ep27 import DESERT
from ep28 import BRONZE, WARM, render as render28

CLEAN = False
STONE = (55, 52, 58)

def crown(dr, x, y, s, col=(240, 200, 90)):
    dr.polygon([(x - 30 * s, y), (x - 34 * s, y - 34 * s), (x - 14 * s, y - 16 * s), (x, y - 40 * s), (x + 14 * s, y - 16 * s), (x + 34 * s, y - 34 * s), (x + 30 * s, y)], fill=col)

# ---------- B: village elder ----------
L_ELDER = text_img('村里吵架：找德高望重的老人评理', FB, 38, (255, 235, 200), 3)
L_KNOW = text_img('大家都认识他，也都信他', FB, 40, (255, 225, 160), 3)
def village(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(185, 160, 95))
    for x in (120, 340, 760, 980): hut(dr, x, GROUND + 20, 0.8)
    sh = math.sin(t * 6)
    sapiens(dr, 280, GROUND + 260, 1.2, col=SKINS[0]); sapiens(dr, 800, GROUND + 260, 1.2, col=SKINS[3])
    dr.line((320, GROUND - 40, 400 + 15 * sh, GROUND - 10), fill=SKINS[0], width=12); dr.line((760, GROUND - 40, 680 - 15 * sh, GROUND - 10), fill=SKINS[3], width=12)
    sapiens(dr, 540, GROUND + 230, 1.1, col=(170, 160, 150)); dr.line((600, GROUND - 120, 610, GROUND + 230), fill=(120, 90, 60), width=8)
    if t > 14.8:
        for i in range(6):
            x = 140 + i * 160; person(dr, x, GROUND + 420, 1.2, SKINS[i % 5])
            dr.line((x, GROUND + 330, 540, GROUND - 40), fill=mul((255, 210, 120), ss(15.0, 16.0, t) * 0.6), width=2)
    put(img, L_ELDER, 540, 640, ss(10.8, 11.6, t) * (1 - ss(14.6, 15.0, t)))
    put(img, L_KNOW, 540, 640, ss(15.0, 15.8, t))
    return img

# ---------- C: city of strangers, third party ----------
L_STR = text_img('城里：成千上万互不认识的人', FB, 40, (255, 235, 200), 3)
L_THIRD = text_img('需要一个所有人都认的第三方', FB, 40, (255, 225, 160), 3)
L_Q = text_img('？', FB, 50, (255, 255, 255), 3)
def city(t):
    img = Image.fromarray(DESERT.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND - 40, W, H), fill=(200, 175, 125))
    for i in range(30):
        x = 30 + (i * 37) % 1020; y = GROUND - 60 - (i % 4) * 36
        dr.rectangle((x - 30, y - 50, x + 30, y), fill=(210, 185, 140), outline=(160, 135, 100), width=2)
    for i in range(16):
        x = 60 + (i * 67) % 960; y = GROUND + 140 + (i % 4) * 70
        person(dr, x, y, 1.0, SKINS[i % 5])
    sapiens(dr, 380, GROUND + 330, 1.2, col=SKINS[1]); sapiens(dr, 700, GROUND + 330, 1.2, col=SKINS[4])
    for x in (380, 700): put(img, L_Q, x, GROUND - 60, ss(19.4, 20.2, t))
    if t > 23.2:
        a = ss(23.4, 24.6, t)
        dr.rectangle((470, GROUND - 10, 610, GROUND + 60), fill=mul((140, 100, 70), a))
        sapiens(dr, 540, GROUND - 10, 1.1, a, col=(180, 140, 100)); dr.line((590, GROUND - 260, 600, GROUND - 10), fill=mul((120, 90, 60), a), width=8)
    put(img, L_STR, 540, 640, ss(19.2, 20.0, t) * (1 - ss(23.0, 23.4, t)))
    put(img, L_THIRD, 540, 640, ss(23.4, 24.2, t))
    return img

# ---------- D: three sources of power ----------
L_SRC = text_img('统治者的权力，从哪里来？', FB, 42, (255, 225, 160), 3)
L_P = [text_img(s_, FB, 40, (255, 235, 200), 3) for s_ in ('武力', '信仰', '好处')]
L_P2 = [text_img(s_, FM, 30, (220, 220, 230), 3) for s_ in ('拿武器的人', '神 · 天命', '保护 · 水渠 · 秩序')]
L_TAX = text_img('换来：交税和服从', FB, 42, (255, 225, 160), 3)
def power(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    rx, ry = 540, 820
    dr.rectangle((rx - 70, ry - 20, rx + 70, ry + 120), fill=(95, 62, 40))
    sapiens(dr, rx, ry + 110, 0.8, col=(190, 145, 105)); crown(dr, rx, ry - 115, 0.8)
    put(img, L_SRC, 540, 620, ss(27.8, 28.6, t) * (1 - ss(31.6, 32.0, t)))
    for i, (x, t0) in enumerate(((200, 32.0), (540, 36.2), (880, 40.4))):
        a = ss(t0, t0 + 0.8, t)
        if a <= 0: continue
        y = 1180
        dr.rounded_rectangle((x - 140, y - 110, x + 140, y + 110), radius=24, fill=mul((40, 34, 30), a), outline=mul((255, 210, 130), a), width=3)
        if i == 0:
            dr.line((x - 40, y + 60, x + 40, y - 60), fill=mul((170, 150, 120), a), width=8); dr.polygon([(x + 40, y - 60), (x + 26, y - 30), (x + 56, y - 46)], fill=mul((200, 200, 210), a))
        elif i == 1:
            dr.ellipse((x - 34, y - 70, x + 34, y - 2), fill=mul((255, 210, 110), a))
            for j in range(8):
                ang = j * math.pi / 4; dr.line((x + 44 * math.cos(ang), y - 36 + 44 * math.sin(ang), x + 64 * math.cos(ang), y - 36 + 64 * math.sin(ang)), fill=mul((255, 210, 110), a), width=4)
        else:
            dr.polygon([(x - 40, y - 70), (x + 40, y - 70), (x + 34, y - 10), (x, y + 10), (x - 34, y - 10)], fill=mul((130, 160, 200), a))
        put(img, L_P[i], x, y + 50, a); put(img, L_P2[i], x, y + 150, a)
        dr.line((x, y - 110, rx, ry + 120), fill=mul((255, 210, 120), a * 0.6), width=3)
    if t > 44.4:
        k = ss(44.6, 47.0, t)
        for i in range(4):
            x = lerp(80 + i * 30, 380 + i * 30, k); sack(dr, x, 1500, 0.9)
        put(img, L_TAX, 540, 1440, ss(44.6, 45.4, t))
    return img

# ---------- E: the state ----------
L_STATE = text_img('国家', FB, 64, (255, 225, 160), 5)
L_ST2 = text_img('一片土地 · 统一管理 · 税收 · 军队', FB, 36, (255, 235, 200), 3)
BORDER = [(220, 760), (520, 690), (860, 780), (900, 1080), (760, 1360), (420, 1400), (180, 1180)]
def state(t):
    img = Image.fromarray(grad((60, 80, 100), (40, 54, 70)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    k = ss(49.0, 51.4, t)
    dr.polygon(BORDER, fill=mul((170, 155, 110), 0.4 + 0.6 * k))
    n = len(BORDER); m = int(n * k)
    for i in range(m): dr.line((BORDER[i], BORDER[(i + 1) % n]), fill=(255, 210, 120), width=6)
    cx, cy = 540, 1040
    dr.polygon([(cx, cy - 40), (cx + 12, cy - 12), (cx + 40, cy - 12), (cx + 18, cy + 6), (cx + 26, cy + 34), (cx, cy + 18), (cx - 26, cy + 34), (cx - 18, cy + 6), (cx - 40, cy - 12), (cx - 12, cy - 12)], fill=(240, 200, 90))
    if t > 50.0:
        for i, (x, y) in enumerate(((330, 900), (720, 920), (420, 1260), (700, 1240), (300, 1100), (780, 1090))):
            dr.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(230, 220, 200))
            q = ((t - 50) * 0.4 + i / 6) % 1
            dr.ellipse((lerp(x, cx, q) - 6, lerp(y, cy, q) - 6, lerp(x, cx, q) + 6, lerp(y, cy, q) + 6), fill=GOLD)
        for j in range(5):
            x, y = BORDER[j][0] * 0.85 + cx * 0.15, BORDER[j][1] * 0.85 + cy * 0.15
            dr.line((x, y - 30, x, y + 10), fill=(200, 200, 210), width=4); dr.ellipse((x - 10, y - 50, x + 10, y - 30), fill=(160, 120, 90))
    put(img, L_STATE, 540, 600, ss(53.2, 54.0, t)); put(img, L_ST2, 540, 1500, ss(49.2, 50.0, t))
    return img

# ---------- F: written laws ----------
L_HAM = text_img('汉谟拉比法典：282 条，刻在石碑上', FB, 38, (255, 225, 160), 3)
L_SEE = text_img('规则写下来，大家都能看见', FB, 40, (255, 235, 200), 3)
L_DING = text_img('郑国子产：把刑法铸在鼎上', FB, 40, (255, 225, 160), 3)
L_QIN = text_img('秦：统一法律、文字、度量衡、货币', FB, 38, (255, 225, 160), 3)
L_U = [text_img(s_, FB, 34, (255, 235, 200), 3) for s_ in ('法律', '文字', '度量衡', '货币')]
def laws(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 70.2:
        x = 540
        dr.rounded_rectangle((x - 150, 760, x + 150, 1380), radius=80, fill=STONE)
        dr.rectangle((x - 120, 800, x + 120, 960), fill=(70, 66, 74))
        sapiens(dr, x - 50, 950, 0.5, col=(90, 86, 94)); sapiens(dr, x + 50, 950, 0.55, col=(90, 86, 94))
        k = ss(61.8, 64.6, t)
        for j in range(int(18 * k)):
            y = 990 + j * 20; dr.line((x - 110, y, x + 110 - (j % 3) * 20, y), fill=(120, 116, 124), width=4)
        if t > 66.0:
            for i in range(6):
                person(dr, 140 + i * 160 if i < 3 else 640 + (i - 3) * 160, 1500, 1.3, SKINS[i % 5], ss(66.2 + i * 0.2, 66.8 + i * 0.2, t))
        put(img, L_HAM, 540, 640, ss(57.6, 58.4, t) * (1 - ss(65.8, 66.2, t)))
        put(img, L_SEE, 540, 640, ss(66.2, 67.0, t))
        return img
    if t < 74.4:
        x, y = 540, 1060
        dr.ellipse((x - 220, y - 160, x + 220, y + 40), fill=BRONZE, outline=(120, 80, 45), width=4)
        dr.rectangle((x - 220, y - 60, x + 220, y + 120), fill=BRONZE)
        dr.ellipse((x - 220, y + 40, x + 220, y + 200), fill=(150, 104, 60))
        for sg in (-1, 1): dr.rectangle((x + sg * 150 - 20, y + 160, x + sg * 150 + 20, y + 340), fill=BRONZE)
        dr.rectangle((x - 20, y + 180, x + 20, y + 360), fill=BRONZE)
        for sg in (-1, 1): dr.arc((x + sg * 180 - 50, y - 240, x + sg * 180 + 50, y - 120), 180, 360, fill=BRONZE, width=16)
        for j in range(5): dr.line((x - 150 + j * 70, y - 30, x - 150 + j * 70, y + 90), fill=(110, 75, 40), width=4)
        put(img, L_DING, 540, 640, ss(70.4, 71.2, t))
        return img
    for i, lab in enumerate(L_U):
        a = ss(74.8 + i * 0.6, 75.4 + i * 0.6, t)
        x = 180 + i * 240; y = 1050
        dr.rounded_rectangle((x - 100, y - 100, x + 100, y + 100), radius=24, fill=mul((40, 34, 30), a), outline=mul((255, 210, 130), a), width=3)
        put(img, lab, x, y, a)
    put(img, L_QIN, 540, 640, ss(74.6, 75.4, t))
    return img

# ---------- G: law constrains, but unequal ----------
L_STABLE = text_img('写下的法律：规则更稳定', FB, 42, (255, 225, 160), 3)
L_BIND = text_img('也在一定程度上，约束了统治者', FB, 40, (255, 235, 200), 3)
L_UNEQ = text_img('但早期法律也写明：身份不同，并不平等', FB, 36, (255, 200, 170), 3)
L_TIERS = [text_img(s_, FB, 34, (240, 235, 220), 3) for s_ in ('贵族', '平民', '奴隶')]
def fair(t):
    img = Image.fromarray(WARM.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 87.2:
        dr.rounded_rectangle((380, 900, 700, 1300), radius=30, fill=STONE)
        for j in range(10): dr.line((410, 940 + j * 32, 670, 940 + j * 32), fill=(120, 116, 124), width=4)
        if t > 83.0:
            k = ss(83.2, 84.6, t)
            crown(dr, 540, 840, 1.6)
            for j in range(6):
                ang = math.pi + j * math.pi / 5
                dr.ellipse((540 + 90 * math.cos(ang) * k - 10, 830 + 50 * math.sin(ang) * k - 10, 540 + 90 * math.cos(ang) * k + 10, 830 + 50 * math.sin(ang) * k + 10), outline=(180, 180, 190), width=4)
        put(img, L_STABLE, 540, 640, ss(79.0, 79.8, t) * (1 - ss(82.8, 83.2, t)))
        put(img, L_BIND, 540, 640, ss(83.2, 84.0, t))
        return img
    for i, (w, lab) in enumerate(zip((220, 420, 620), L_TIERS)):
        y = 860 + i * 180
        dr.rectangle((540 - w / 2, y, 540 + w / 2, y + 150), fill=[(180, 140, 70), (130, 110, 90), (90, 80, 76)][i], outline=(60, 50, 40), width=3)
        put(img, lab, 540, y + 75, ss(87.6 + i * 0.4, 88.2 + i * 0.4, t))
    put(img, L_UNEQ, 540, 640, ss(87.4, 88.2, t))
    return img

# ---------- H: theories ----------
L_ORI = text_img('国家是怎么起源的？不同解释：', FB, 40, (255, 225, 160), 3)
L_TH = [text_img(s_, FB, 38, (240, 240, 245), 3) for s_ in ('征服和强迫', '约定：用服从换保护', '管理水利这样的大事')]
L_MIX = text_img('现实中，往往几种都有', FB, 42, (255, 235, 200), 3)
def theories(t):
    img = Image.fromarray(DARK.astype(np.uint8)); dr = ImageDraw.Draw(img)
    put(img, L_ORI, 540, 640, ss(91.8, 92.6, t))
    mix = ss(108.6, 110.6, t)
    for i, (lab, t0) in enumerate(zip(L_TH, (96.0, 100.2, 104.4))):
        a = ss(t0, t0 + 0.8, t)
        if a <= 0: continue
        if mix > 0:
            ang = -math.pi / 2 + i * 2 * math.pi / 3
            x, y = 540 + 170 * math.cos(ang) * mix, 1060 + 170 * math.sin(ang) * mix
            r = 210
            dr.ellipse((x - r, y - r, x + r, y + r), outline=mul([(240, 120, 100), (120, 180, 240), (130, 210, 140)][i], a), width=5)
            put(img, lab, x + 120 * math.cos(ang), y + 120 * math.sin(ang) * 0.9, a)
        else:
            y = 860 + i * 220
            dr.rounded_rectangle((170, y - 80, 910, y + 80), radius=26, fill=mul((36, 40, 52), a), outline=mul([(240, 120, 100), (120, 180, 240), (130, 210, 140)][i], a), width=4)
            put(img, lab, 540, y, a)
    put(img, L_MIX, 540, 1460, ss(108.8, 109.6, t))
    return img

# ---------- I: states connected ----------
L_LINK = text_img('道路、航船、贸易：把国家连在一起', FB, 38, (255, 225, 160), 3)
STATES = [(220, 820, 140), (560, 760, 170), (880, 880, 120), (360, 1200, 160), (760, 1240, 150)]
def connect(t):
    img = Image.fromarray(grad((40, 80, 120), (24, 50, 80)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    g = ss(113.0, 115.0, t)
    for i, (x, y, r) in enumerate(STATES):
        rr = r * (0.7 + 0.3 * g)
        dr.polygon([(x + rr * (1 + 0.15 * math.sin(3 * a + i)) * math.cos(a), y + rr * 0.8 * (1 + 0.15 * math.sin(3 * a + i)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)], fill=(170, 155, 110), outline=(230, 200, 140))
        dr.polygon([(x, y - 20), (x + 8, y - 6), (x + 22, y - 6), (x + 10, y + 4), (x + 14, y + 20), (x, y + 10), (x - 14, y + 20), (x - 10, y + 4), (x - 22, y - 6), (x - 8, y - 6)], fill=(240, 200, 90))
    if t > 117.0:
        k = ss(117.2, 120.0, t)
        for i, (a, b) in enumerate(((0, 1), (1, 2), (0, 3), (3, 4), (1, 4), (2, 4))):
            (ax, ay, _), (bx, by, _) = STATES[a], STATES[b]
            ex, ey = lerp(ax, bx, k), lerp(ay, by, k)
            col = (255, 210, 120) if i % 2 == 0 else (200, 230, 255)
            dr.line((ax, ay, ex, ey), fill=col, width=5)
            if k > 0.2:
                q = (t * 0.5 + i / 6) % 1
                dr.ellipse((lerp(ax, bx, q) - 7, lerp(ay, by, q) - 7, lerp(ax, bx, q) + 7, lerp(ay, by, q) + 7), fill=col)
        put(img, L_LINK, 540, 1500, ss(117.2, 118.0, t))
    return img

def render(t):
    if t < 10.6: return dim(render28(133.1 + min(t, 6.0)), 1 - ss(10.0, 10.6, t) if t > 6 else 1.0)
    if t < 19.0: return dim(village(t), ss(10.6, 11.2, t) * (1 - ss(18.4, 19.0, t)))
    if t < 27.6: return dim(city(t), ss(19.0, 19.6, t) * (1 - ss(27.0, 27.6, t)))
    if t < 48.8: return dim(power(t), ss(27.6, 28.2, t) * (1 - ss(48.2, 48.8, t)))
    if t < 57.4: return dim(state(t), ss(48.8, 49.4, t) * (1 - ss(56.8, 57.4, t)))
    if t < 78.8:
        k = ss(57.4, 58.0, t) * (1 - ss(78.2, 78.8, t))
        for a in (69.8, 74.0):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(laws(t), k)
    if t < 91.6:
        k = ss(78.8, 79.4, t) * (1 - ss(91.0, 91.6, t))
        if 86.8 < t < 87.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 86.8) / 0.8)
        return dim(fair(t), k)
    if t < 112.8: return dim(theories(t), ss(91.6, 92.2, t) * (1 - ss(112.2, 112.8, t)))
    return dim(connect(t), ss(112.8, 113.4, t))

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep29_{ts}.png')
