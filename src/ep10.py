import numpy as np, math, sys
from PIL import Image, ImageDraw
from ep1 import W, H, CX, ss, lerp, text_img, put, FM, FB, fbm
from ep4 import sea, mul
from ep9 import scene_g

CLEAN = False
rng = np.random.default_rng(101)

# ---------- top-down seafloor with microbial mat ----------
_mt = fbm(5, 103, 32)
MAT = np.asarray(Image.fromarray((_mt[:, 100:676] * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
MAT_BG = (np.array([92, 104, 70]) * (0.85 + 0.3 * MAT[..., None])).astype(np.float32)

def floor_img(trails=(), stone=0.0):
    f = MAT_BG.copy()
    if stone > 0:
        g = np.array([120, 115, 108]) * (0.8 + 0.3 * MAT[..., None])
        f = f * (1 - stone) + g * stone
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img)
    for pts in trails:
        if len(pts) > 1:
            dr.line(pts, fill=(55, 50, 40) if stone < 0.5 else (80, 76, 70), width=26, joint='curve')
            dr.line(pts, fill=(75, 70, 55) if stone < 0.5 else (100, 96, 90), width=12, joint='curve')
    return img, dr

def worm(dr, pts, r0, col, head_col=None, a=1.0):
    n = len(pts)
    for i in range(n - 1, -1, -1):
        x, y = pts[i]
        r = r0 * (0.55 + 0.45 * math.sin(math.pi * (i + 1) / (n + 1)) ** 0.6)
        c = col if i else (head_col or col)
        dr.ellipse((x - r, y - r, x + r, y + r), fill=mul(c, a), outline=mul(tuple(int(v * 0.7) for v in c), a), width=2)

def path_pos(u, y0, amp, wl):
    x = lerp(-80, W + 80, u)
    return x, y0 + amp * math.sin(x / wl)

def crawl_scene(t):
    u = ss(15.6, 27.0, t) * 0.9
    y0 = 1000
    trail = [path_pos(v, y0, 90, 130) for v in np.linspace(0, u, 60)] if u > 0.01 else []
    stone = ss(24.0, 26.0, t)
    img, dr = floor_img([trail], stone)
    if stone < 0.9:
        hx, hy = path_pos(u, y0, 90, 130)
        body = [path_pos(max(0, u - k * 0.012), y0, 90, 130) for k in range(10)]
        worm(dr, body, 28, (230, 150, 140), (250, 190, 120), 1 - stone)
    return img

# ---------- big worm diagram ----------
BX0, BX1, BY = 200, 880, 980
L_HEAD = text_img('头', FB, 56, (255, 220, 130), 4); L_TAIL = text_img('尾', FB, 56, (200, 220, 240), 4)
L_MOUTH = text_img('嘴', FM, 38, (255, 220, 130), 3); L_ANUS = text_img('肛门', FM, 38, (200, 220, 240), 3)
L_SENSE = text_img('感觉细胞', FM, 38, (255, 220, 130), 3); L_GUT = text_img('消化道', FM, 38, (230, 200, 170), 3)
L_L = text_img('左', FB, 44, (150, 200, 255), 3); L_R = text_img('右', FB, 44, (255, 180, 140), 3)
L_NERVE = text_img('神经索', FM, 38, (255, 235, 140), 3); L_BRAIN = text_img('小"脑"', FM, 38, (255, 235, 140), 3)
L_ASYM = text_img('不对称：原地打转', FM, 34, (220, 220, 225), 2); L_SYM = text_img('对称：走直线', FM, 34, (220, 220, 225), 2)
FOOD = [rng.random() for _ in range(9)]
def body_outline(dr, sym=0.0, wob=0.0):
    pts = []
    for k in range(41):
        u = k / 40; x = lerp(BX0, BX1, u)
        w = 70 * math.sin(math.pi * min(1, u * 1.05 + 0.02)) ** 0.5 + 6
        pts.append((x, BY - w + 4 * math.sin(u * 20 + wob)))
    for k in range(40, -1, -1):
        u = k / 40; x = lerp(BX0, BX1, u)
        w = 70 * math.sin(math.pi * min(1, u * 1.05 + 0.02)) ** 0.5 + 6
        pts.append((x, BY + w + 4 * math.sin(u * 20 + wob + 1)))
    dr.polygon(pts, fill=(205, 130, 125), outline=(240, 175, 165))
    for k in range(1, 12):
        x = lerp(BX0, BX1, k / 12)
        dr.line((x, BY - 50, x, BY + 50), fill=(185, 115, 110), width=2)

def diagram(t):
    img, dr = sea(t + 400)
    body_outline(dr, wob=t * 2)
    hk = ss(32.6, 34.4, t)
    if hk > 0:
        for k in range(9):
            ang = -1.2 + k * 0.3
            x, y = BX1 - 30 + 34 * math.cos(ang), BY + 50 * math.sin(ang)
            dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=mul((255, 215, 110), hk))
        dr.ellipse((BX1 - 14, BY - 14, BX1 + 14, BY + 14), fill=mul((90, 40, 40), hk))
    gk = ss(41.0, 42.6, t)
    if gk > 0:
        x1 = lerp(BX1 - 10, BX0 + 14, gk)
        dr.line((BX1 - 10, BY, x1, BY), fill=(150, 80, 70), width=18)
        dr.line((BX1 - 10, BY, x1, BY), fill=(230, 190, 150), width=8)
        if gk >= 1:
            for ph in FOOD:
                q = (t * 0.25 + ph) % 1
                x = lerp(BX1 - 20, BX0 + 20, q)
                c = tuple(int(v) for v in lerp(np.array([120, 210, 120]), np.array([120, 100, 70]), q))
                dr.ellipse((x - 9, BY - 9, x + 9, BY + 9), fill=c)
            dr.ellipse((BX0 + 2, BY - 10, BX0 + 22, BY + 10), fill=(90, 40, 40))
    if 49.2 <= t:
        sk = ss(53.8, 55.0, t)
        if sk > 0:
            for x in range(BX0 - 40, BX1 + 60, 34):
                dr.line((x, BY, x + 18, BY), fill=mul((240, 240, 250), sk), width=3)
            put(img, L_L, BX0 + 120, BY - 140, sk); put(img, L_R, BX0 + 120, BY + 140, sk)
        nk = ss(58.0, 59.6, t)
        if nk > 0:
            xe = lerp(BX1 - 40, BX0 + 30, nk)
            dr.line((BX1 - 40, BY - 24, xe, BY - 24), fill=(255, 225, 120), width=6)
            for k in range(1, 12):
                x = lerp(BX0, BX1, k / 12)
                if x > xe: dr.ellipse((x - 7, BY - 31, x + 7, BY - 17), fill=(255, 225, 120))
            g = ss(59.0, 60.0, t)
            dr.ellipse((BX1 - 75, BY - 52, BX1 - 25, BY + 4), fill=mul((255, 235, 150), g), outline=mul((255, 250, 210), g), width=3)
    put(img, L_HEAD, BX1 + 70, BY, ss(36.8, 37.6, t)); put(img, L_TAIL, BX0 - 70, BY, ss(45.2, 46.0, t))
    put(img, L_SENSE, BX1 - 60, BY - 160, ss(32.8, 33.6, t) * (1 - ss(40.6, 41.2, t)))
    put(img, L_MOUTH, BX1 - 10, BY + 140, ss(33.6, 34.4, t) * (1 - ss(40.6, 41.2, t)))
    put(img, L_GUT, CX, BY + 140, ss(41.4, 42.2, t) * (1 - ss(48.8, 49.4, t)))
    put(img, L_ANUS, BX0 + 30, BY + 140, ss(43.0, 43.8, t) * (1 - ss(48.8, 49.4, t)))
    put(img, L_NERVE, CX, BY - 160, ss(58.4, 59.2, t)); put(img, L_BRAIN, BX1 - 50, BY - 200, ss(59.4, 60.2, t))
    if 49.4 <= t < 53.8:
        a = ss(49.4, 50.2, t) * (1 - ss(53.2, 53.8, t))
        q = (t - 49.4) * 1.4
        cx1, cy1 = 280, 1420
        bx, by = cx1 + 80 * math.cos(q), cy1 + 80 * math.sin(q)
        dr.ellipse((cx1 - 80, cy1 - 80, cx1 + 80, cy1 + 80), outline=mul((150, 160, 170), a), width=2)
        dr.ellipse((bx - 30, by - 18, bx + 22, by + 26), fill=mul((205, 130, 125), a))
        sx = lerp(620, 960, ((t - 49.4) / 4.4))
        dr.line((620, 1420, sx, 1420), fill=mul((150, 160, 170), a), width=2)
        dr.ellipse((sx - 34, 1400, sx + 34, 1440), fill=mul((205, 130, 125), a))
        put(img, L_ASYM, 280, 1540, a); put(img, L_SYM, 790, 1540, a)
    return img

# ---------- Kimberella ----------
L_KIM = text_img('金伯拉虫', FB, 46, (250, 230, 190), 3)
def kimberella(t):
    img, dr = floor_img()
    cx, cy = 420 + (t - 62) * 18, 1000
    k = ss(66.6, 68.0, t)
    for j in range(int(14 * ss(66.6, 70.4, t))):
        x0 = cx - 200 - j * 26
        for m in range(-3, 4):
            dr.line((x0, cy + m * 22, x0 + 30, cy + m * 34), fill=(60, 70, 40), width=4)
    pts = []
    for p in np.linspace(0, 2 * math.pi, 80):
        r = 1 + 0.06 * math.sin(p * 18 + t * 3)
        pts.append((cx + 170 * r * math.cos(p), cy + 105 * r * math.sin(p)))
    dr.polygon(pts, fill=(205, 175, 130), outline=(160, 130, 95))
    dr.ellipse((cx - 120, cy - 70, cx + 120, cy + 70), fill=(185, 150, 110))
    for j in range(-4, 5):
        dr.line((cx + j * 26, cy - 60, cx + j * 26, cy + 60), fill=(165, 130, 95), width=2)
    ext = 60 + 40 * (0.5 + 0.5 * math.sin(t * 3)) * k
    dr.line((cx + 165, cy, cx + 165 + ext, cy), fill=(220, 160, 130), width=14)
    dr.ellipse((cx + 155 + ext, cy - 14, cx + 183 + ext, cy + 14), fill=(240, 180, 150))
    put(img, L_KIM, cx, cy - 190, ss(62.4, 63.2, t))
    return img

# ---------- chase ----------
PREY = [(rng.random(), rng.random() * 6) for _ in range(5)]
L_PRED = text_img('捕食者', FB, 42, (255, 170, 150), 3); L_PREY = text_img('猎物', FB, 42, (180, 230, 200), 3)
def chase(t):
    img, dr = floor_img()
    lt = t - 70.8
    for i, (u, ph) in enumerate(PREY):
        a = ph + lt * 0.4
        x = CX + 330 * math.cos(a) + 30 * math.sin(lt * 2 + i); y = 1000 + 420 * math.sin(a * 1.3)
        body = [(x - 18 * k * math.cos(a + 1.57), y - 18 * k * math.sin(a * 1.3 + 1.57)) for k in range(7)]
        worm(dr, body, 16, (150, 210, 170), (200, 240, 210))
    if t > 75.2:
        k = ss(75.2, 76.4, t)
        a = PREY[0][1] + lt * 0.4 - 0.5
        x = CX + 330 * math.cos(a); y = 1000 + 420 * math.sin(a * 1.3)
        body = [(x - 22 * j * math.cos(a + 1.57), y - 22 * j * math.sin(a * 1.3 + 1.57)) for j in range(9)]
        worm(dr, body, 24 * k + 1, (200, 80, 70), (240, 120, 90))
        put(img, L_PRED, x, y - 90, ss(75.6, 76.4, t) * (1 - ss(82.8, 83.4, t)))
        a0 = PREY[0][1] + lt * 0.4
        put(img, L_PREY, CX + 330 * math.cos(a0), 1000 + 420 * math.sin(a0 * 1.3) - 60, ss(75.6, 76.4, t) * (1 - ss(82.8, 83.4, t)))
    return img

def dim(img, k):
    if k >= 0.999: return img
    return Image.fromarray((np.asarray(img, np.float32) * k).astype(np.uint8))

def render(t):
    if t < 15.2: return dim(scene_g(t + 90), 1 - ss(14.6, 15.2, t))
    if t < 28.0: return dim(crawl_scene(t), ss(15.2, 15.8, t) * (1 - ss(27.4, 28.0, t)))
    if t < 62.0: return dim(diagram(t), ss(28.0, 28.6, t) * (1 - ss(61.4, 62.0, t)))
    if t < 70.6: return dim(kimberella(t), ss(62.0, 62.6, t) * (1 - ss(70.0, 70.6, t)))
    return dim(chase(t), ss(70.6, 71.2, t))

CAPS = [(6.4, 10.6, '埃迪卡拉生物躺在海底，靠表面吸收养分'), (10.6, 14.8, '海底铺着一层细菌织成的"地毯"'),
        (15.4, 19.6, '约 5.6 亿年前，有的小动物开始爬行'), (19.6, 23.8, '去别处寻找食物，留下了爬痕'),
        (23.8, 27.8, '这些爬痕变成化石，今天还能找到'), (28.2, 32.4, '总朝一个方向爬，前端最先碰到食物和危险'),
        (32.4, 36.6, '感觉细胞集中到前端，嘴也长在前面'), (36.6, 40.8, '这就是"头"'),
        (40.8, 45.0, '食物从前往后走，残渣从后端排出'), (45.0, 49.2, '一条贯通的消化道出现了，也就有了"尾"'),
        (49.4, 53.6, '要沿直线爬，左右两边就得一样'), (53.6, 57.8, '于是，有了左右对称'),
        (57.8, 61.8, '神经排成一条线，前端聚成一个小"脑"'), (62.2, 66.4, '比如金伯拉虫，约 5.55 亿年前'),
        (66.4, 70.4, '它在海底爬行，刮食细菌地毯'), (71.0, 75.2, '动物会动了，能找食物，也能逃跑'),
        (75.2, 79.4, '于是，出现了捕食者和猎物'), (79.4, 83.6, '你追我逃，越来越激烈'),
        (83.8, 88.0, '一场生命大爆发，就要来了')]

if __name__ == '__main__':
    for ts in sys.argv[1:]: render(float(ts)).save(f'ep10_{ts}.png')
