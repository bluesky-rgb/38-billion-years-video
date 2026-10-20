import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep15 import grad, dim, therapsid
from ep16 import shrew, GROUND
from ep17 import globe, tree, climber, SPACE, STARS, render as render17

CLEAN = False
rng = np.random.default_rng(181)
FOREST_SKY = grad((120, 175, 215), (220, 230, 200), 480, 1100)

# ---------- A: warm earth, flowering forest ----------
L_POLE = text_img('两极附近也长满森林', FB, 42, (210, 245, 200), 3)
L_FLOW = text_img('开花植物：花、果实', FB, 42, (255, 225, 200), 3)
L_UP = text_img('爬上树：找吃的，也躲开捕食者', FB, 40, (255, 235, 200), 3)
L_PRED = text_img('地面的捕食者', FM, 36, (255, 210, 190), 3)
FRUITS = [(rng.random() * W, 560 + rng.random() * 380, rng.random()) for _ in range(40)]
def warm_globe(t):
    img = Image.fromarray(SPACE.astype(np.uint8)); dr = ImageDraw.Draw(img)
    for x, y, b in STARS: dr.point((x, y), fill=(int(160 + 80 * b),) * 3)
    globe(dr, 600, 1080, 360)
    for cy in (1080 - 360 + 40, 1080 + 360 - 40):
        dr.chord((600 - 200, cy - 60, 600 + 200, cy + 60), 0, 360, fill=(80, 140, 70))
    put(img, L_POLE, 540, 640, ss(10.8, 11.6, t))
    return img
def canopy(dr, t, flowers=1.0):
    for i, x in enumerate((80, 300, 540, 780, 1000)):
        dr.line((x, GROUND, x, 620), fill=(85, 65, 45), width=34 if i != 2 else 44)
        dr.line((x, 760, x + (-1) ** i * 180, 690), fill=(85, 65, 45), width=12)
        for k in range(6):
            cx = x + (k - 2.5) * 70; cy = 600 + (k % 2) * 50
            dr.ellipse((cx - 90, cy - 60, cx + 90, cy + 60), fill=(60 + 8 * k, 125, 65))
    for x, y, b in FRUITS:
        a = flowers * ss(15.0 + b * 2, 16.0 + b * 2, t)
        if a <= 0: continue
        col = (240, 120, 150) if b < 0.5 else (245, 170, 60)
        r = 9 + 6 * b
        dr.ellipse((x - r, y - r, x + r, y + r), fill=mul(col, a))
def forest(t):
    img = Image.fromarray(FOREST_SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.rectangle((0, GROUND, W, H), fill=(95, 120, 70))
    canopy(dr, t)
    for i in range(6):
        bx = 200 + i * 140 + 30 * math.sin(t * 2 + i); by = 820 + 40 * math.cos(t * 3 + i)
        dr.ellipse((bx - 6, by - 4, bx + 6, by + 4), fill=(40, 40, 40))
    put(img, L_FLOW, 540, 1030, ss(15.2, 16.0, t) * (1 - ss(22.8, 23.2, t)))
    if t > 23.0:
        k = ss(23.4, 27.0, t)
        y = lerp(GROUND - 20, 780, k)
        if k < 0.98:
            climber(dr, 540 - 26, y, 1.5, t)
        else:
            climber(dr, 640, 735, 1.5, 27)
        put(img, L_UP, 540, 1060, ss(23.6, 24.4, t) * (1 - ss(27.2, 27.6, t)))
    if t > 27.4:
        pk = ss(27.6, 28.4, t)
        therapsid(dr, lerp(1250, 820, ss(27.6, 30.0, t)), GROUND + 40, 0.9, t, pk, face=-1)
        put(img, L_PRED, 820, GROUND + 190, pk)
    return img

# ---------- B: hands ----------
L_SLIP = text_img('细树枝上，爪子钩不住', FB, 40, (255, 225, 200), 3)
L_GRIP = text_img('能握住的，不容易摔下去', FB, 40, (255, 235, 200), 3)
L_OPP = text_img('拇指和其他手指相对：对握', FB, 40, (255, 225, 160), 3)
L_NAIL = text_img('尖爪 → 扁平的指甲', FB, 42, (255, 235, 210), 3); L_PAD = text_img('敏感的指尖肉垫', FB, 42, (255, 210, 190), 3)
SKIN = (205, 160, 130)
def finger(dr, x0, y0, ang, L, w, curl, nail, claw, pad=0.0, t=0.0):
    pts = [(x0, y0)]; a = ang
    for j in range(3):
        a += curl
        x1, y1 = pts[-1][0] + L / 3 * math.cos(a), pts[-1][1] + L / 3 * math.sin(a); pts.append((x1, y1))
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        dr.line((xa, ya, xb, yb), fill=SKIN, width=int(w))
        dr.ellipse((xb - w / 2, yb - w / 2, xb + w / 2, yb + w / 2), fill=SKIN)
    tx, ty = pts[-1]
    if claw > 0.02:
        dr.polygon([(tx - w * 0.35 * math.sin(a), ty + w * 0.35 * math.cos(a)), (tx + w * 1.4 * claw * math.cos(a), ty + w * 1.4 * claw * math.sin(a)),
                    (tx + w * 0.35 * math.sin(a), ty - w * 0.35 * math.cos(a))], fill=(60, 50, 45))
    if nail > 0.02:
        dr.ellipse((tx - w * 0.3, ty - w * 0.3, tx + w * 0.3, ty + w * 0.3), fill=mul((245, 225, 215), nail), outline=(170, 130, 110))
    if pad > 0.02:
        g = pad * (0.6 + 0.4 * math.sin(t * 4))
        dr.ellipse((tx - w * 0.45, ty - w * 0.45, tx + w * 0.45, ty + w * 0.45), outline=mul((255, 220, 120), g), width=4)
    return pts[-1]
def hands(t):
    img = Image.fromarray(grad((36, 52, 46), (20, 30, 28)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    by = 1000
    dr.rectangle((0, by - 18, W, by + 18), fill=(110, 85, 60))
    for i in range(6):
        dr.ellipse((150 + i * 160, by - 26, 190 + i * 160, by - 10), fill=(70, 120, 60))
    if t < 36.0:
        k = ss(32.4, 35.6, t)
        x, y = 540 + 120 * k, by - 40 + 260 * k ** 2
        rot = 0.6 * k
        for i in range(4):
            finger(dr, x - 60 + i * 40, y, math.pi / 2 + rot, 110, 30, 0.05, 0, 1.0)
        dr.ellipse((x - 90, y - 70, x + 90, y + 30), fill=SKIN)
        put(img, L_SLIP, 540, 640, ss(32.0, 32.8, t))
        return img
    curl = lerp(0.05, 0.75, ss(36.4, 38.6, t))
    opp = ss(44.6, 46.8, t); nail = ss(49.0, 51.4, t); pad = ss(53.2, 54.4, t)
    x, y = 520, by - 90
    for i in range(4):
        finger(dr, x - 70 + i * 48, y + 40, math.pi / 2 - 0.2, 170, 36, curl, nail, 1 - nail, pad, t)
    dr.ellipse((x - 110, y - 70, x + 110, y + 70), fill=SKIN)
    dr.rectangle((x - 70, y - 300, x + 70, y - 40), fill=SKIN)
    ta = lerp(math.pi * 0.95, math.pi * 0.25, opp)
    finger(dr, x + 100, y + 10, ta, 140, 40, lerp(0.1, -0.35, opp) * -1, nail, 1 - nail, pad, t)
    put(img, L_GRIP, 540, 640, ss(36.4, 37.2, t) * (1 - ss(44.2, 44.6, t)))
    put(img, L_OPP, 540, 640, ss(44.8, 45.6, t) * (1 - ss(48.4, 48.8, t)))
    put(img, L_NAIL, 540, 640, ss(49.0, 49.8, t) * (1 - ss(52.6, 53.0, t)))
    put(img, L_PAD, 540, 640, ss(53.2, 54.0, t))
    return img

# ---------- C: eyes and brain ----------
L_JUMP = text_img('跳过去：要判断有多远', FB, 40, (255, 235, 200), 3)
L_SIDE = text_img('眼在两侧：看得宽，量不准', FB, 36, (220, 225, 235), 3)
L_FRONT = text_img('眼在正前方：画面重叠', FB, 36, (255, 225, 160), 3)
L_DEPTH = text_img('重叠的部分：看出远近', FB, 42, (255, 225, 160), 3)
L_BRAIN = text_img('看、抓、跳：大脑来协调', FB, 40, (255, 235, 200), 3); L_BIGGER = text_img('大脑相对变大', FB, 44, (255, 215, 190), 3)
def head_top(dr, cx, cy, front, a, t):
    dr.ellipse((cx - 90, cy - 120, cx + 90, cy + 110), fill=mul((150, 115, 90), a))
    if front:
        eyes = [(cx - 40, cy - 90, -math.pi / 2 - 0.05), (cx + 40, cy - 90, -math.pi / 2 + 0.05)]
    else:
        eyes = [(cx - 85, cy - 40, -math.pi / 2 - 1.1), (cx + 85, cy - 40, -math.pi / 2 + 1.1)]
    L = 330; half = 0.62
    for ex, ey, ang in eyes:
        p1 = (ex + L * math.cos(ang - half), ey + L * math.sin(ang - half)); p2 = (ex + L * math.cos(ang + half), ey + L * math.sin(ang + half))
        dr.polygon([(ex, ey), p1, p2], outline=mul((180, 210, 240), a), width=3)
        dr.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=mul((30, 30, 30), a), outline=mul((240, 240, 220), a), width=3)
    if front:
        ov = ss(70.0, 71.4, t)
        if ov > 0:
            (ax, ay, aa), (bx, by_, ba) = eyes
            dr.polygon([(cx, ay - 70), (bx + L * math.cos(ba - half) - 20, by_ + L * math.sin(ba - half)), (ax + L * math.cos(aa + half) + 20, ay + L * math.sin(aa + half))],
                       fill=mul((255, 210, 120), 0.45 * ov * a))
def eyes(t):
    img = Image.fromarray(grad((30, 40, 52), (16, 22, 30)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 61.4:
        dr.line((0, 1020, 380, 980), fill=(110, 85, 60), width=22); dr.line((700, 960, W, 930), fill=(110, 85, 60), width=22)
        k = ss(58.4, 60.6, t)
        x = lerp(330, 760, k); y = 960 - 260 * math.sin(math.pi * k)
        climber(dr, x - 22, y - 40, 0.9, 58.4)
        dr.line((390, 1080, 690, 1060), fill=(255, 225, 160), width=4)
        for xx, yy in ((390, 1080), (690, 1060)): dr.line((xx, yy - 16, xx, yy + 16), fill=(255, 225, 160), width=4)
        put(img, L_JUMP, 540, 640, ss(57.6, 58.4, t))
        return img
    if t < 74.2:
        sk = 1.0 if t > 61.6 else 0.0; fk = 1.0 if t > 65.9 else 0.0
        head_top(dr, 280, 1200, False, sk, t); head_top(dr, 800, 1200, True, fk, t)
        put(img, L_SIDE, 280, 1400, sk); put(img, L_FRONT, 800, 1400, fk)
        put(img, L_DEPTH, 540, 640, ss(70.2, 71.0, t))
        return img
    cx, cy = 540, 1000
    dr.ellipse((cx - 220, cy - 180, cx + 220, cy + 180), fill=(150, 115, 90))
    dr.ellipse((cx + 140, cy - 40, cx + 300, cy + 90), fill=(150, 115, 90))
    dr.ellipse((cx + 150, cy - 60, cx + 190, cy - 20), fill=(30, 30, 30))
    bk = ss(78.6, 81.0, t)
    r = lerp(90, 150, bk)
    dr.ellipse((cx - 60 - r, cy - 40 - r * 0.75, cx - 60 + r, cy - 40 + r * 0.75), fill=(235, 170, 170), outline=(255, 210, 210), width=4)
    for j in range(4):
        dr.arc((cx - 60 - r * 0.8, cy - 40 - r * 0.6 + j * r * 0.25, cx - 60 + r * 0.8, cy - 40 + j * r * 0.25), 200, 340, fill=(200, 130, 130), width=3)
    put(img, L_BRAIN, 540, 640, ss(74.4, 75.2, t) * (1 - ss(78.2, 78.6, t)))
    put(img, L_BIGGER, 540, 640, ss(78.6, 79.4, t))
    return img

# ---------- D: Archicebus and primates ----------
L_PRI = text_img('灵长类', FB, 60, (255, 225, 160), 4)
L_ARCH = text_img('阿喀琉斯基猴 · 湖北', FB, 42, (255, 225, 160), 3); L_7 = text_img('约 7 厘米', FM, 36, (240, 240, 230), 3)
L_TREE = [text_img(s_, FB, 40, c, 3) for s_, c in (('早期灵长类', (255, 225, 160)), ('猴', (230, 230, 240)), ('猿', (230, 230, 240)), ('人', (255, 215, 150)))]
def archi(t):
    img = Image.fromarray(grad((25, 45, 40), (14, 26, 22)).astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t < 95.6:
        dr.line((0, 1060, W, 1000), fill=(100, 78, 55), width=40)
        for i in range(7): dr.ellipse((60 + i * 150, 960 - (i % 2) * 40, 160 + i * 150, 1010 - (i % 2) * 40), fill=(50, 95, 55))
        x = lerp(1200, 560, ss(83.0, 86.6, t))
        climber(dr, x - 22, 940, 1.6, t if t < 86.6 else 86.6)
        put(img, L_PRI, 540, 640, ss(83.2, 84.0, t) * (1 - ss(86.8, 87.2, t)))
        if t > 87.0:
            put(img, L_ARCH, 540, 640, ss(87.2, 88.0, t))
            k = ss(91.4, 92.2, t)
            dr.line((440, 1110, 660, 1110), fill=mul((240, 240, 230), k), width=4)
            for xx in (440, 660): dr.line((xx, 1095, xx, 1125), fill=mul((240, 240, 230), k), width=4)
            put(img, L_7, 550, 1170, k)
        return img
    k = ss(95.8, 97.6, t)
    rx, ry = 540, 1300
    put(img, L_TREE[0], rx, ry + 60, ss(95.8, 96.4, t))
    for i, (tx, ty) in enumerate(((240, 800), (540, 760), (840, 800))):
        kk = ss(96.2 + i * 0.6, 97.4 + i * 0.6, t)
        dr.line((rx, ry, lerp(rx, tx, kk), lerp(ry, ty + 40, kk)), fill=(230, 200, 150) if i < 2 else (255, 215, 150), width=7)
        put(img, L_TREE[i + 1], tx, ty, ss(97.2 + i * 0.6, 97.8 + i * 0.6, t))
    return img

# ---------- E: cooling, forests shrink, a tailless shadow ----------
L_ICE = text_img('约 3400 万年前起：南极结冰', FB, 42, (215, 235, 255), 3)
L_DRY = text_img('变冷、变干，森林收缩', FB, 42, (240, 225, 190), 3)
L_HARD = text_img('树上的家变小了', FB, 42, (240, 225, 190), 3)
L_TAIL = text_img('个子越来越大，尾巴越来越短', FB, 40, (255, 225, 160), 3)
def tailbeast(dr, x, y, s, tail, a, col=(70, 55, 45)):
    dr.ellipse((x - 40 * s, y - 70 * s, x + 40 * s, y + 60 * s), fill=mul(col, a))
    dr.ellipse((x - 34 * s, y - 130 * s, x + 34 * s, y - 64 * s), fill=mul(col, a))
    for sg in (-1, 1):
        dr.line((x + sg * 30 * s, y - 40 * s, x + sg * 60 * s, y + 50 * s), fill=mul(col, a), width=int(14 * s))
        dr.line((x + sg * 20 * s, y + 50 * s, x + sg * 30 * s, y + 140 * s), fill=mul(col, a), width=int(16 * s))
    if tail > 0.02:
        dr.arc((x - 10 * s, y + 20 * s, x + 10 * s + 160 * s * tail, y + 60 * s + 160 * s * tail), 180, 330, fill=mul(col, a), width=int(10 * s))
def cooling(t):
    if t < 108.4:
        img = Image.fromarray(SPACE.astype(np.uint8)); dr = ImageDraw.Draw(img)
        for x, y, b in STARS: dr.point((x, y), fill=(int(160 + 80 * b),) * 3)
        globe(dr, 600, 1080, 360, 0.15 * ss(104, 108, t))
        ik = ss(100.4, 104.0, t)
        cy = 1080 + 360 - 40
        dr.chord((600 - 220 * ik, cy - 70 * ik, 600 + 220 * ik, cy + 70 * ik), 0, 360, fill=(240, 248, 255))
        put(img, L_ICE, 540, 640, ss(100.4, 101.2, t) * (1 - ss(104.0, 104.4, t)))
        put(img, L_DRY, 540, 640, ss(104.4, 105.2, t))
        return img
    dk = ss(108.6, 112.0, t)
    img = Image.fromarray((FOREST_SKY * (1 - dk) + grad((170, 175, 170), (225, 210, 170), 480, 1100) * dk).astype(np.uint8)); dr = ImageDraw.Draw(img)
    gc = tuple(int(v) for v in lerp(np.array([95, 120, 70]), np.array([185, 165, 105]), dk))
    dr.rectangle((0, GROUND, W, H), fill=gc)
    for i, x in enumerate((80, 260, 440, 620, 800, 980)):
        gone = ss(109.0 + i * 0.4, 110.6 + i * 0.4, t) if i not in (2, 3) else 0
        if gone < 0.98:
            tree(dr, x, GROUND, 520, 1 - gone)
    for i in range(30):
        x = (i * 37) % W; h = 20 + (i % 4) * 8
        dr.line((x, GROUND, x + 4, GROUND - h * dk), fill=(150, 140, 80), width=3)
    put(img, L_HARD, 540, 640, ss(108.8, 109.6, t) * (1 - ss(112.4, 112.8, t)))
    if t > 112.6:
        for i, (s, tl) in enumerate(((0.7, 1.0), (1.0, 0.5), (1.4, 0.0))):
            a = ss(117.0 + i * 0.7, 117.8 + i * 0.7, t)
            if a > 0: tailbeast(dr, 260 + i * 260, GROUND - 140 * s + 10, s, tl, a)
        put(img, L_TAIL, 540, 640, ss(117.2, 118.0, t))
    return img

def render(t):
    if t < 6.0: return render17(136.5 + t)
    if t < 14.8: return dim(warm_globe(t), ss(6.0, 6.6, t) * (1 - ss(14.2, 14.8, t)))
    if t < 31.8: return dim(forest(t), ss(14.8, 15.4, t) * (1 - ss(31.2, 31.8, t)))
    if t < 57.2: return dim(hands(t), ss(31.8, 32.4, t) * (1 - ss(56.6, 57.2, t)))
    if t < 82.8:
        k = ss(57.2, 57.8, t) * (1 - ss(82.2, 82.8, t))
        for a in (61.0, 73.8):
            if a < t < a + 0.8: k *= 1 - 0.85 * math.sin(math.pi * (t - a) / 0.8)
        return dim(eyes(t), k)
    if t < 99.9:
        k = ss(82.8, 83.4, t) * (1 - ss(99.3, 99.9, t))
        if 95.2 < t < 96.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 95.2) / 0.8)
        return dim(archi(t), k)
    k = ss(99.9, 100.5, t)
    if 108.0 < t < 108.8: k *= 1 - 0.85 * math.sin(math.pi * (t - 108.0) / 0.8)
    return dim(cooling(t), k)

CAPS = []

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep18_{ts}.png')
