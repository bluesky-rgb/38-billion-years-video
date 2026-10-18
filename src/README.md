# src

## 依赖

- Python 3.10+，`numpy`、`pillow`
- `ffmpeg`
- 中文字体 Noto Sans CJK（路径写在 `ep1.py` 顶部）
- 离线语音合成：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx/releases) 的 `linux-x64-shared` 版本与 `vits-melo-tts-zh_en` 模型，解压到 `src/dl/bin/` 和 `src/dl/model/`

## 文件

| 文件 | 内容 |
| --- | --- |
| `series.py` | 系列框架与剧集表 `EPS`（所有字幕、旁白、概念卡、年代、尺度提示） |
| `ep1.py` … `ep11.py` | 每集画面；`render(t)` 返回第 t 秒的画面 |
| `ep1_bed.py`、`ep2_audio.py`、`ep3_audio.py`、`ep4_audio.py` | 第 1–4 集背景音乐与音效（ep2–4 用 `BEDONLY=1` 只导出音效轨） |
| `ep5_bed.py` … `ep11_bed.py` | 第 5–11 集背景音乐与音效 |

每集音效轨导出为 `bed{n}.npy`，`series.py` 渲染时读取它并叠加旁白。

## 一集的生成顺序

```bash
python3 ep9_bed.py                         # 生成 bed9.npy
python3 series.py 9 audio                  # 合成旁白，混音为 s9.wav，并打印每句时长是否放得下
python3 series.py 9 stills 10 50 90        # 检查关键帧
python3 series.py 9 video out.mp4          # 渲染整集（约 20–35 分钟）
```

## 音效轨拼接说明

以下几集在后期插入了新段落，音效轨是在原轨基础上拼接的：

- 第 1 集：开头 6 秒后插入 12.6 秒星云序章（原轨开头 6 秒循环 + 呼啸与点燃音效）
- 第 2 集：6 秒后插入 21.6 秒"地球为什么冷却"（取第 1 集冷却段音乐）
- 第 6 集：6 秒后插入 16.8 秒"细胞变成细菌"（新生成的和弦与分裂提示音）
- 第 8 集：32.2 秒处插入 25.2 秒"大陆是怎么来的"（低沉和弦 + 隆隆声）

画面侧对应的插入逻辑写在各集文件末尾的 `render()` 包装函数里。
