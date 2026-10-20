# 38 亿年家谱

**项目网页：https://bluesky-rgb.github.io/38-billion-years-video/**

**研究笔记：https://bluesky-rgb.github.io/38-billion-years-research/**（按主题整理的全部理解，[仓库](https://github.com/bluesky-rgb/38-billion-years-research)）

在网页上可以播放全部已完成的剧集，查看每集的因果链和旁白，以及项目思路、方法论、理解笔记、概念词典、待审核稿件和制作日志。

| 页面 | 内容 |
| --- | --- |
| [总览](https://bluesky-rgb.github.io/38-billion-years-video/site/) | 全部剧集、时间轴、最新进展 |
| [项目思路](https://bluesky-rgb.github.io/38-billion-years-video/site/about.html) | 两条主线、社会的本质、方案、产品矩阵、英文版、发布指标 |
| [方法论](https://bluesky-rgb.github.io/38-billion-years-video/site/method.html) | 正向流程六步、修订中学到的规则、引导装置、检查清单 |
| [理解笔记](https://bluesky-rgb.github.io/38-billion-years-video/site/notes.html) | 制作中提出的每个问题和答案 |
| [概念词典](https://bluesky-rgb.github.io/38-billion-years-video/site/glossary.html) | 片中全部概念卡 |
| [待审核](https://bluesky-rgb.github.io/38-billion-years-video/site/review.html) | 下一集的完整稿子 |
| [制作日志](https://bluesky-rgb.github.io/38-billion-years-video/site/log.html) | 从想法到现在的每一步 |

一部按时间顺序讲清"你从哪里来"的竖屏科普短剧：从星云收缩成太阳、地球诞生、生命起源，一路讲到人类。每集 1–3 分钟，讲清一次跃迁的来龙去脉，集集相连。

- 画幅：9:16 竖屏，1080×1920，30 帧
- 语言：中文（英文版规划中）
- 进度：已完成 20 集（第 0、1、2 季全部，第 3 季前 2 集），共规划 24 集
- 在线观看：`site/videos/` 中有每集 720p 预览版，也可在项目网页中直接播放

## 工作方式

每一步都提交到这个仓库，网页随之更新：

1. 讨论中的每个问题和答案写进 `knowledge/notes.json`
2. 下一集的稿子写进 `knowledge/drafts.json`，在网页"待审核"页审阅
3. 定稿后写入 `src/series.py` 的剧集表，因果链写进 `knowledge/flow.json`
4. 渲染成片，预览版放进 `site/videos/`
5. 每一步记进 `knowledge/log.json`，运行 `python3 site/build.py` 重新生成网页

## 核心方法：正向流程

每一集、每一个新出现的事物，都按六步讲完，不允许凭空出现、不允许跳步：

1. **前提**：当时的世界是什么样
2. **形成**：新东西从哪来，一步步怎么形成
3. **变化**：为什么会变，原因 → 结果
4. **概念**：新词第一次出现就用一句大白话解释（概念卡）
5. **影响**：它改变了什么，和你有什么关系
6. **引出**：这个变化成为下一集的前提

详见 [docs/方法论.md](docs/方法论.md)。

## 剧集

| # | 季 · 集 | 标题 | 时长 |
| --- | --- | --- | --- |
| 1 | 0 · 1 | 一颗岩浆球 | 90 秒 |
| 2 | 0 · 2 | 第一场雨 | 98 秒 |
| 3 | 0 · 3 | 生命的原料 | 77 秒 |
| 4 | 0 · 4 | 会复制的分子 | 79 秒 |
| 5 | 0 · 5 | 第一个细胞 | 77 秒 |
| 6 | 0 · 6 | 改变天空的细菌 | 104 秒 |
| 7 | 1 · 1 | 吞下发电厂 | 77 秒 |
| 8 | 1 · 2 | 雪球地球 | 171 秒 |
| 9 | 1 · 3 | 细胞开始分工 | 116 秒 |
| 10 | 1 · 4 | 有了头和尾 | 104 秒 |
| 11 | 1 · 5 | 第一根脊梁 | 108 秒 |
| 12 | 1 · 6 | 长出下巴的鱼 | 90 秒 |
| 13 | 2 · 1 | 爬上岸的鱼 | 95 秒 |
| 14 | 2 · 2 | 带着海水的蛋 | 104 秒 |
| 15 | 2 · 3 | 大死亡 | 142 秒 |
| 16 | 2 · 4 | 恐龙脚下的小老鼠 | 140 秒 |
| 17 | 2 · 5 | 一颗小行星 | 140 秒 |
| 18 | 2 · 6 | 爬上树 | 137 秒 |
| 19 | 3 · 1 | 尾巴消失了 | 137 秒 |
| 20 | 3 · 2 | 站起来 | 136 秒 |
| 21 | 3 · 3 | 第一把石器 | 稿件审核中 |

完整的分季规划见 [docs/规划.md](docs/规划.md)；每集的旁白、字幕、概念卡、年代标签都在 [scripts/episodes.json](scripts/episodes.json)。

## 目录

```
docs/       方法论、规划、修订记录、下一步
knowledge/  我们的理解：每集因果链、理解笔记、决策、制作日志、待审核稿件
scripts/    每集稿件数据（episodes.json）
src/        渲染与混音代码
site/       项目总览网页与海报图
```

## 渲染

所有画面都由 Python 代码逐帧生成（numpy + Pillow），用 ffmpeg 编码。

```bash
pip install numpy pillow
# 需要 ffmpeg，以及离线语音合成 sherpa-onnx（见 src/README.md）
cd src
python3 series.py 9 stills 10 50 90         # 预览第 9 集的几帧
python3 series.py 9 audio                   # 生成旁白与混音
python3 series.py 9 video 第1季第3集.mp4    # 渲染整集
```

- `series.py`：系列框架。负责上集回顾、顶部时间轴、标题、字幕、概念卡、尺度提示、"和你有什么关系"、下集预告与混音；剧集表 `EPS` 是所有文字内容的唯一来源
- `ep1.py` … `ep20.py`：每集的画面（`CLEAN = True` 时只出画面，文字由框架叠加）
- `ep*_bed.py` / `ep*_audio.py`：每集的背景音乐与音效

## 已知限制

- 旁白目前使用离线合成（sherpa-onnx + MeloTTS），后期统一替换为 MiniMax 语音
- 第 1、2、6、8 集的音效轨在插入新段落时做过拼接，拼接步骤记录在 [src/README.md](src/README.md)

## 许可

文字与画面内容采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans)，代码采用 MIT。
