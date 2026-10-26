#!/bin/bash
# 逐集单独进程生成抖音版（避免内存不足）；已有完好成片的跳过
cd /home/claude
while pgrep -f "douyin.py [0-9]" >/dev/null; do sleep 20; done
for n in "$@"; do
  f=$(ls douyin/抖音版_$(printf %02d $n)_*.mp4 2>/dev/null | head -1)
  if [ -n "$f" ] && ffprobe -v error "$f" >/dev/null 2>&1; then echo "skip $n"; continue; fi
  rm -f "$f"; s=$(date +%s)
  python3 douyin.py $n >> douyin/run.log 2>&1 && echo "ok $n $(( $(date +%s)-s ))s" || echo "FAIL $n"
done
