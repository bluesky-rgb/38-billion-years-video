import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB
from ep4 import mul
from ep12 import lobe

CLEAN = False
rng = np.random.default_rng(131)
yy = np.arange(H, dtype=np.float32)[:, None, None]
SKY = (np.array([120, 165, 205]) * (1 - yy / 1100) + np.array([215, 210, 190]) * (yy / 1100)) * np.ones((1, W, 1))
SKY = np.clip(SKY, 0, 255)

def ground_y(x, t=0.0, kind='shore'):
    if kind == 'shore':
        return 1290 - 380 * (1 - min(1, x / 760)) ** 1.4 + 18 * math.sin(x / 70)
    return 1180 + 14 * math.sin(x / 90)

# ---------- A: plants go ashore ----------
TREES = [(120, 1.1), (300, 1.4), (480, 1.0), (650, 1.3), (820, 1.15), (980, 1.25)]
BUGS = [(rng.random() * W, rng.random() * 6) for _ in range(10)]
L_ALGA = text_img('绿藻', FM, 38, (180, 240, 170), 3); L_MOSS = text_img('最早的陆地植物', FM, 38, (180, 240, 170), 3)
L_SOIL = text_img('土壤', FB, 42, (240, 210, 160), 3); L_ROCK = text_img('岩石', FM, 36, (220, 220, 220), 3)
L_FOREST = text_img('第一片森林', FB, 44, (220, 245, 200), 3); L_BUG = text_img('虫子、蜘蛛的祖先', FM, 38, (240, 230, 200), 3)
def land(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((800, 160, 920, 280), fill=(255, 245, 210))
    pts = [(x, ground_y(x)) for x in range(0, W + 20, 20)] + [(W, 1700), (0, 1700)]
    rock = (125, 110, 100)
    dr.polygon(pts, fill=rock)
    g = ss(10.6, 14.6, t)
    reach = lerp(0, W, g)
    for x in range(0, int(reach), 14):
        y = ground_y(x)
        h = 10 + 16 * ((x * 37) % 7) / 7
        dr.ellipse((x - 12, y - h, x + 12, y + 6), fill=(80, 150, 70))
    sk = ss(15.0, 18.6, t)
    if sk > 0:
        for x in range(0, W, 4):
            y = ground_y(x)
            d = 110 * sk
            dr.line((x, y, x, y + d), fill=(100, 72, 48))
        for k in range(40):
            x = (k * 97) % W; y = ground_y(x) + 24 + (k * 13) % int(80 * sk + 1)
            dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(70, 52, 38))
    water = [(x, 1320 + 6 * math.sin(x / 40 + t)) for x in range(0, W + 20, 20)] + [(W, H), (0, H)]
    dr.polygon(water, fill=(50, 110, 130))
    fk = ss(19.0, 22.6, t)
    if fk > 0:
        for x, s in TREES:
            y = ground_y(x); h = 420 * s * fk
            dr.line((x, y, x, y - h), fill=(95, 75, 55), width=int(14 * s))
            for j in range(6):
                yj = y - h * (0.45 + j * 0.1)
                w = 120 * s * (1 - j * 0.13) * fk
                dr.ellipse((x - w, yj - 30 * s, x + w, yj + 30 * s), fill=(60, 120 + j * 8, 60), outline=(40, 95, 45))
    bk = ss(23.4, 24.4, t)
    if bk > 0:
        for i, (x0, ph) in enumerate(BUGS):
            x = (x0 + (t - 23) * 30 * (1 if i % 2 else -1)) % W; y = ground_y(x) - 8
            dr.ellipse((x - 10, y - 6, x + 10, y + 6), fill=mul((60, 45, 35), bk))
            for j in (-1, 1):
                for l in range(3):
                    dr.line((x - 6 + l * 6, y, x - 8 + l * 6, y + j * 10), fill=mul((60, 45, 35), bk), width=2)
    put(img, L_ALGA, 900, 1220, ss(10.8, 11.6, t) * (1 - ss(12.8, 13.4, t)))
    put(img, L_MOSS, 540, 1080, ss(12.8, 13.6, t) * (1 - ss(14.6, 15.2, t)))
    put(img, L_ROCK, 150, ground_y(150) + 170, ss(15.2, 16.0, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_SOIL, 150, ground_y(150) + 60, ss(16.6, 17.4, t) * (1 - ss(18.8, 19.2, t)))
    put(img, L_FOREST, 540, 500, ss(20.6, 21.4, t) * (1 - ss(23.0, 23.4, t)))
    put(img, L_BUG, 540, 760, ss(24.0, 24.8, t))
    return img

# ---------- side-view fish ----------
def fish(dr, x, y, s, t, tilt=0.0, col=(130, 140, 115), head_up=0.0, fin=True):
    c, sn = math.cos(tilt), math.sin(tilt)
    def R(px, py): return (x + px * c - py * sn, y + px * sn + py * c)
    pts = [R(100 * s * math.cos(p), 30 * s * math.sin(p) + 4 * s * math.sin(math.cos(p) * 3 - t * 5)) for p in np.linspace(0, 2 * math.pi, 50)]
    dr.polygon(pts, fill=col, outline=tuple(int(v * 0.7) for v in col))
    dr.polygon([R(-95 * s, 0), R(-140 * s, -38 * s), R(-140 * s, 38 * s)], fill=col)
    ex, ey = R(64 * s, -14 * s + head_up * -6 * s)
    dr.ellipse((ex - 6 * s, ey - 6 * s, ex + 6 * s, ey + 6 * s), fill=(25, 25, 30))
    if fin:
        a, b = R(30 * s, 24 * s), R(10 * s, 70 * s)
        dr.line((a, b), fill=tuple(int(v * 0.85) for v in col), width=int(18 * s))

L_LUNG = text_img('肺：吸空气的气囊', FB, 42, (255, 200, 190), 3); L_LOWO2 = text_img('氧气少', FM, 38, (230, 230, 240), 3)
def swamp(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.ellipse((820, 150, 950, 280), fill=(255, 240, 200))
    for x, s in TREES[::2]:
        y = 820
        dr.line((x, y, x, y - 300 * s), fill=(90, 72, 52), width=int(12 * s))
        for j in range(5):
            yj = y - 300 * s * (0.5 + j * 0.1); w = 100 * s * (1 - j * 0.15)
            dr.ellipse((x - w, yj - 25 * s, x + w, yj + 25 * s), fill=(55, 115 + j * 8, 55))
    dr.polygon([(0, 820), (W, 820), (W, H), (0, H)], fill=(95, 80, 60))
    lvl = lerp(860, 1060, ss(29.4, 33.0, t))
    wpts = [(x, lvl + 5 * math.sin(x / 50 + t * 2)) for x in range(0, W + 20, 20)] + [(W, 1500), (0, 1500)]
    dr.polygon(wpts, fill=(80, 105, 70))
    dr.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=(70, 58, 45))
    hu = ss(32.2, 34.0, t)
    fx, fy = 520, lerp(1250, lvl - 10, hu * 0.85) if hu > 0 else 1250
    fish(dr, fx, fy + 30, 2.0, t, tilt=-0.45 * hu, col=(130, 140, 115))
    if hu > 0.8:
        for k in range(4):
            q = ((t * 0.8) + k / 4) % 1
            mx, my = fx + 190, fy - 70 - q * 60
            dr.ellipse((mx - 6, my - 6, mx + 6, my + 6), outline=(240, 240, 255), width=2)
    lk = ss(36.2, 37.4, t)
    if lk > 0:
        bx, by = fx - 30, fy + 10
        breath = 0.85 + 0.15 * math.sin(t * 3)
        dr.ellipse((bx - 70 * breath, by - 26 * breath, bx + 70 * breath, by + 26 * breath), fill=mul((230, 140, 135), lk), outline=mul((255, 210, 200), lk), width=3)
        dr.line((bx + 60, by - 10, fx + 120, fy - 40), fill=mul((255, 210, 200), lk), width=5)
    put(img, L_LOWO2, 820, 1300, ss(28.4, 29.2, t) * (1 - ss(31.6, 32.2, t)))
    put(img, L_LUNG, 520, 1460, lk)
    return img

# ---------- fin bones ----------
L_ONE = text_img('一根骨', FB, 40, (240, 240, 250), 3); L_TWO = text_img('两根骨', FB, 40, (240, 240, 250), 3); L_MANY = text_img('许多小骨', FB, 40, (240, 240, 250), 3)
def bones(dr, sx, sy, ang, L, s, col, k=1.0, digits=5):
    c, sn = math.cos(ang), math.sin(ang)
    def P(u, off=0.0): return (sx + u * L * c - off * sn, sy + u * L * sn + off * c)
    w = max(2, int(14 * s * k))
    dr.line((P(0.0), P(0.36)), fill=col, width=w)
    dr.line((P(0.40, -10 * s), P(0.68, -14 * s)), fill=col, width=max(2, int(10 * s * k)))
    dr.line((P(0.40, 10 * s), P(0.68, 14 * s)), fill=col, width=max(2, int(10 * s * k)))
    for j in range(digits):
        o = (j - (digits - 1) / 2) * 12 * s
        dr.line((P(0.72, o * 0.8), P(0.98, o * 1.4)), fill=col, width=max(2, int(6 * s * k)))
    return P
def finbones(t):
    img = Image.fromarray(np.clip(SKY * 0.0 + np.array([18, 40, 50]), 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    x, y, s = 480, 820, 3.2
    pts = [(x + 100 * s * math.cos(p), y + 30 * s * math.sin(p)) for p in np.linspace(0, 2 * math.pi, 60)]
    dr.polygon(pts, fill=(70, 80, 70), outline=(110, 125, 105))
    sx, sy = x + 30 * s, y + 24 * s
    push = ss(45.2, 47.0, t) * (0.5 + 0.5 * math.sin((t - 45) * 2.5))
    ang = lerp(1.2, 1.55, push)
    fin = [(sx - 22 * s, sy), (sx + 22 * s, sy), (sx + 260 * math.cos(ang) + 40, sy + 260 * math.sin(ang)), (sx + 260 * math.cos(ang) - 40, sy + 260 * math.sin(ang) + 10)]
    dr.polygon(fin, fill=(60, 80, 90), outline=(110, 130, 140))
    P = bones(dr, sx, sy, ang, 260, 2.2, (245, 245, 255))
    a1 = ss(41.2, 42.0, t); a2 = ss(42.4, 43.2, t); a3 = ss(43.6, 44.4, t)
    put(img, L_ONE, P(0.18)[0] + 150, P(0.18)[1], a1 * (1 - ss(49.0, 49.4, t)))
    put(img, L_TWO, P(0.55)[0] + 160, P(0.55)[1], a2 * (1 - ss(49.0, 49.4, t)))
    put(img, L_MANY, P(0.9)[0] + 170, P(0.9)[1], a3 * (1 - ss(49.0, 49.4, t)))
    if t > 45.0:
        dr.rectangle((0, sy + 250, W, H), fill=(80, 66, 50))
    return img

# ---------- Tiktaalik ----------
L_TIK = text_img('提塔利克鱼', FB, 46, (255, 225, 160), 3); L_NECK = text_img('脖子', FM, 38, (255, 225, 160), 3); L_EYE = text_img('眼睛在头顶', FM, 38, (255, 225, 160), 3)
def tiktaalik(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    dr.polygon([(0, 1060), (W, 1000), (W, H), (0, H)], fill=(110, 92, 70))
    dr.polygon([(0, 1150), (W, 1180), (W, H), (0, H)], fill=(80, 105, 85))
    x, y, s = 520, 1030, 2.4
    turn = 0.35 * math.sin((t - 58) * 1.6) * ss(58.2, 59.0, t)
    body = [(x - 120 * s + 240 * s * u, y + 6 * s * math.sin(u * 7 + t)) for u in np.linspace(0, 1, 30)]
    dr.polygon([(px, py - 28 * s * math.sin(math.pi * min(1, u * 1.1 + 0.05))) for (px, py), u in zip(body, np.linspace(0, 1, 30))] +
               [(px, py + 24 * s * math.sin(math.pi * min(1, u * 1.1 + 0.05))) for (px, py), u in list(zip(body, np.linspace(0, 1, 30)))[::-1]], fill=(120, 125, 95), outline=(80, 85, 60))
    hx, hy = x + 120 * s, y - 10 * s
    hc, hs = math.cos(turn - 0.15), math.sin(turn - 0.15)
    head = [(hx + 70 * s * math.cos(p) * hc - 22 * s * math.sin(p) * hs, hy + 70 * s * math.cos(p) * hs + 22 * s * math.sin(p) * hc) for p in np.linspace(-math.pi / 2, math.pi / 2, 20)]
    dr.polygon([(hx, hy - 24 * s), *head, (hx, hy + 22 * s)], fill=(130, 132, 100), outline=(80, 85, 60))
    ex, ey = hx + 30 * s * hc - (-20 * s) * hs, hy + 30 * s * hs + (-20 * s) * hc
    dr.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=(25, 25, 30))
    for fx in (x + 70 * s, x - 40 * s):
        dr.line((fx, y + 18 * s, fx + 20 * s, y + 40 * s), fill=(105, 110, 80), width=int(14 * s * 0.6))
        dr.line((fx + 20 * s, y + 40 * s, fx + 46 * s, y + 42 * s), fill=(105, 110, 80), width=int(10 * s * 0.6))
    put(img, L_TIK, x, y - 170, ss(54.0, 54.8, t))
    put(img, L_EYE, ex + 30, ey - 90, ss(58.4, 59.2, t) * (1 - ss(62.0, 62.6, t)))
    put(img, L_NECK, hx - 10, hy + 120, ss(59.4, 60.2, t) * (1 - ss(62.0, 62.6, t)))
    return img

# ---------- Acanthostega, arm, eggs ----------
L_ACA = text_img('棘螈 · 八根指头', FB, 44, (255, 225, 160), 3); L_TETRA = text_img('四足动物', FB, 44, (220, 245, 200), 3)
L_FISHFIN = text_img('肉鳍鱼的鳍', FM, 38, (230, 230, 240), 3); L_ARM = text_img('你的手臂', FM, 38, (255, 225, 160), 3)
L_EGG = text_img('卵还得产在水里', FM, 38, (230, 230, 240), 3)
def acanth(t):
    img = Image.fromarray(SKY.astype(np.uint8)); dr = ImageDraw.Draw(img)
    if t >= 79.6 and t < 84.2:
        img = Image.fromarray(np.full((H, W, 3), (18, 34, 44), np.uint8)); dr = ImageDraw.Draw(img)
        k = ss(79.8, 80.8, t)
        bones(dr, 260, 640, math.pi / 2, 600, 2.4, mul((220, 225, 235), k))
        P2 = bones(dr, 760, 600, math.pi / 2, 700, 2.6, mul((255, 225, 160), k))
        for j in range(5):
            o = (j - 2) * 30
            dr.ellipse((760 + o * 1.4 - 16, 600 + 700 - 6, 760 + o * 1.4 + 16, 600 + 700 + 26), outline=mul((255, 225, 160), k), width=3)
        put(img, L_FISHFIN, 260, 560, k); put(img, L_ARM, 760, 520, k)
        return img
    dr.polygon([(0, 1060), (W, 1020), (W, H), (0, H)], fill=(105, 88, 66))
    dr.polygon([(0, 1170), (W, 1190), (W, H), (0, H)], fill=(70, 105, 95))
    if t >= 84.2:
        for k in range(14):
            ex, ey = 380 + (k % 7) * 50, 1240 + (k // 7) * 44
            dry = ss(85.0, 88.0, t)
            col = tuple(int(v) for v in lerp(np.array([200, 225, 200]), np.array([150, 140, 110]), dry))
            dr.ellipse((ex - 20, ey - 20, ex + 20, ey + 20), fill=col, outline=(240, 245, 235), width=2)
            dr.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=(60, 70, 50))
        put(img, L_EGG, 540, 1450, ss(84.6, 85.4, t))
        return img
    x, y, s = 520, 1100, 2.2
    walk = math.sin((t - 66) * 2.0)
    body = [(x - 150 * s + 300 * s * u, y) for u in np.linspace(0, 1, 30)]
    up = [(px, py - 30 * s * math.sin(math.pi * min(1, u * 1.1 + 0.05))) for (px, py), u in zip(body, np.linspace(0, 1, 30))]
    dn = [(px, py + 22 * s * math.sin(math.pi * min(1, u * 1.1 + 0.05))) for (px, py), u in zip(body, np.linspace(0, 1, 30))]
    dr.polygon(up + dn[::-1], fill=(125, 120, 90), outline=(80, 78, 58))
    dr.polygon([(x - 150 * s, y), (x - 210 * s, y - 30 * s), (x - 210 * s, y + 24 * s)], fill=(120, 115, 85))
    dr.ellipse((x + 110 * s, y - 20 * s, x + 122 * s, y - 8 * s), fill=(25, 25, 30))
    for i, lx in enumerate((x + 80 * s, x - 70 * s)):
        ph = walk if i == 0 else -walk
        kx, ky = lx + 18 * s * ph, y + 40 * s
        dr.line((lx, y + 14 * s, kx, ky), fill=(110, 105, 78), width=int(12 * s))
        dr.line((kx, ky, kx + 10 * s, y + 62 * s), fill=(110, 105, 78), width=int(9 * s))
        for d in range(8):
            o = (d - 3.5) * 5 * s
            dr.line((kx + 10 * s, y + 62 * s, kx + 10 * s + o, y + 74 * s), fill=(110, 105, 78), width=3)
    put(img, L_TETRA if t < 71.0 else L_ACA, x, y - 170, ss(67.0, 67.8, t))
    if 75.2 <= t < 79.6:
        a = ss(75.4, 76.2, t)
        for k in range(10):
            ex, ey = 220 + k * 30, 1240 + (k % 2) * 30
            dr.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=mul((200, 225, 200), a), outline=mul((240, 245, 235), a), width=2)
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 6.0: return lobe(t + 68)
    if t < 27.6: return dim(land(t), ss(6.0, 6.6, t) * (1 - ss(27.0, 27.6, t)))
    if t < 40.6: return dim(swamp(t), ss(27.6, 28.2, t) * (1 - ss(40.0, 40.6, t)))
    if t < 53.6: return dim(finbones(t), ss(40.6, 41.2, t) * (1 - ss(53.0, 53.6, t)))
    if t < 66.6: return dim(tiktaalik(t), ss(53.6, 54.2, t) * (1 - ss(66.0, 66.6, t)))
    k = ss(66.6, 67.2, t)
    if 79.2 < t < 80.0: k *= 1 - 0.85 * math.sin(math.pi * (t - 79.2) / 0.8)
    if 83.8 < t < 84.6: k *= 1 - 0.85 * math.sin(math.pi * (t - 83.8) / 0.8)
    return dim(acanth(t), k)

CAPS = [(6.4, 10.6, '臭氧层挡住了紫外线，陆地不再是"死亡地带"'), (10.6, 14.8, '约 4.7 亿年前，水边的绿藻慢慢适应了干燥，爬上了岸'),
        (14.8, 19.0, '植物的根磨碎岩石、混进腐叶，第一次有了土壤'), (19.0, 23.2, '约 3.85 亿年前，地球上出现了第一片森林'),
        (23.2, 27.4, '虫子和蜘蛛的祖先也上了岸，陆地上有了吃的'), (27.8, 32.0, '泥盆纪的浅水沼泽，水温高、氧气少，还常常干涸'),
        (32.0, 36.2, '有的肉鳍鱼把头伸出水面，吞一口空气'), (36.2, 40.4, '用来吸空气的气囊，就是最早的肺'),
        (40.8, 45.0, '它们的鳍里，是一根骨、两根骨、许多小骨'), (45.0, 49.2, '有了骨头，鳍能撑起身体，在泥里挪动'),
        (49.2, 53.4, '这比只会划水的鳍，有力得多'), (53.8, 58.0, '约 3.75 亿年前，出现了提塔利克鱼'),
        (58.0, 62.2, '眼睛长到头顶，还有了脖子，能扭头张望'), (62.2, 66.4, '它还离不开水，但已经能在浅滩上撑起身体'),
        (66.8, 71.0, '后来，鳍变成了长着手指的四肢'), (71.0, 75.2, '比如有八根指头的棘螈，第一批四足动物'),
        (75.2, 79.4, '但它们的卵还得产在水里，一干就死')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep13_{ts}.png')
