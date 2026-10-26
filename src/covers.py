"""抖音封面：1080×1920，关键文字放在中间 3:4 区域内（主页网格会裁成 3:4）。"""
import os, sys, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import series, douyin
from PIL import Image, ImageDraw, ImageFilter
from ep1 import W, H, text_img, put, FB, FM

SEASON_NAME = {0: '地球与生命的诞生', 1: '海洋篇', 2: '登陆篇', 3: '人类篇', 4: '人类社会是怎样形成的'}
def cover(n):
    e = series.EPS[n]; s = e.get('season', 0); idx = e.get('idx', n)
    q1, q2, bt = douyin.HOOKS[n]
    img = e['mod'].render(bt).convert('RGB').filter(ImageFilter.GaussianBlur(4))
    arr = np.asarray(img, np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    shade = 0.35 + 0.35 * np.exp(-((yy - 900) / 520) ** 2)
    img = Image.fromarray((arr * shade).astype(np.uint8)); dr = ImageDraw.Draw(img)
    top = '第二部 · 人类社会' if s >= 4 else f'第 {s} 季 · {SEASON_NAME[s]}'
    put(img, text_img('38 亿年家谱', FB, 64, (255, 220, 170), 5), W / 2, 380, 1.0)
    put(img, text_img(top, FM, 42, (235, 235, 235), 3), W / 2, 470, 1.0)
    num = f'{idx:02d}'
    put(img, text_img(num, FB, 220, (255, 205, 110), 8), W / 2, 700, 1.0)
    title = e['title']
    T = text_img(title, FB, 150 if len(title) <= 4 else 120 if len(title) <= 6 else 96, (255, 255, 255), 8)
    T = douyin.fitw(T, 980)
    put(img, T, W / 2, 960, 1.0)
    dr.rounded_rectangle((W / 2 - 60, 1080, W / 2 + 60, 1088), radius=4, fill=(255, 205, 110))
    Q = douyin.fitw(text_img(q1.strip('"') + ' ' + q2, FM, 52, (255, 235, 200), 4), 960)
    put(img, Q, W / 2, 1180, 1.0)
    put(img, text_img(f'全系列第 {n} 集', FM, 34, (200, 200, 205), 3), W / 2, 1580, 1.0)
    os.makedirs('douyin/封面', exist_ok=True)
    img.save(f'douyin/封面/封面_{n:02d}_{title}.jpg', quality=92)
    return img

if __name__ == '__main__':
    ids = [int(x) for x in sys.argv[1:]] or sorted(series.EPS)
    ims = [cover(n) for n in ids]
    sheet = Image.new('RGB', (270 * min(len(ims), 10), 480 * ((len(ims) + 9) // 10)))
    for i, im in enumerate(ims): sheet.paste(im.resize((270, 480)), (270 * (i % 10), 480 * (i // 10)))
    sheet.save('douyin/covers_sheet.png'); print('ok', len(ims))
