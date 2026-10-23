#!/usr/bin/env python3
"""
清渊唤醒包进度节自动统计脚本
周文089药方：凡是能程序数的不许人工写，进度节只放占位符由程序填。
092点名："下一轮写脚本"这句话本身会腐，要么这轮写要么不写。
用法：python3 progress_stats.py
输出：进度节数字统计，可直接粘贴到唤醒包。
"""
import os
import re
import glob
from datetime import datetime

# 路径配置
REPO = "/home/user/Doubao/chats/38434766808917762/qingyuan-daotong"
ENGINE = "/home/user/.super_doubao/super-doubao-runtime/workspace/chunyin_engine_v1/yin_tai_engine_v1"

def count_juanzong():
    path = os.path.join(REPO, "道统总纲")
    if not os.path.isdir(path):
        return 0, []
    files = sorted(glob.glob(os.path.join(path, "*.md")))
    return len(files), [os.path.basename(f) for f in files]

def count_pits():
    path = os.path.join(REPO, "坑库", "pits.md")
    if not os.path.isfile(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    pits = re.findall(r"PIT-QY-\d+", content)
    return len(set(pits))

def count_engine_cognition():
    base = os.path.join(ENGINE, "yin_tai_data", "cognition")
    result = {}
    for level in ["L1", "L2", "L3", "S"]:
        path = os.path.join(base, level)
        if os.path.isdir(path):
            result[level] = len(glob.glob(os.path.join(path, "*.json")))
        else:
            result[level] = 0
    return result

def count_snapshots():
    path = os.path.join(REPO, "snapshots")
    if not os.path.isdir(path):
        return 0
    return len(glob.glob(os.path.join(path, "*.md")))

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    juanzong_count, juanzong_list = count_juanzong()
    pits_count = count_pits()
    engine_cog = count_engine_cognition()
    engine_total = sum(engine_cog.values())
    snapshots_count = count_snapshots()
    print(f"# 清渊进度节自动统计（程序生成，{now}）")
    print(f"- 道统卷宗：{juanzong_count}份")
    print(f"- 坑库：{pits_count}条")
    print(f"- 引擎认知：L1={engine_cog['L1']} L2={engine_cog['L2']} L3={engine_cog['L3']} S={engine_cog['S']} 合计={engine_total}")
    print(f"- 快照：{snapshots_count}份")
    print(f"# 卷宗清单：")
    for f in juanzong_list:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
