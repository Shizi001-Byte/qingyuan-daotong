#!/usr/bin/env python3
"""
清渊唤醒包进度节自动统计脚本 v1.1
周文089药方：凡是能程序数的不许人工写，进度节只放占位符由程序填。
092点名："下一轮写脚本"这句话本身会腐，要么这轮写要么不写。
v1.1（第二十三次唤醒改造，判据14代理量落地）：
  - 读不到 -> 输出 UNAVAILABLE 并抛告警，禁止静默返回 0
  - 走廊发帖数不再用手写列表（v1.0 那个列表是手写阳动伪装成程序阴底），改数本地可达副本并标注口径
  - 每个数字附带"来源层数"（判据14：隔几层）
用法：python3 progress_stats.py [--strict]
  --strict：任一数据源不可达即以非零码退出（供自动化用）
"""
import os
import re
import sys
import glob
from datetime import datetime

REPO = "/home/user/Doubao/chats/38434766808917762/qingyuan-daotong"
ENGINE = "/home/user/.super_doubao/super-doubao-runtime/workspace/chunyin_engine_v1/yin_tai_engine_v1"

WARNINGS = []


def fail(msg):
    """数据源不可达：记录告警并抛异常，绝不静默归零。"""
    WARNINGS.append(msg)
    raise RuntimeError(msg)


def count_juanzong():
    path = os.path.join(REPO, "道统总纲")
    if not os.path.isdir(path):
        fail(f"卷宗目录不存在：{path}")
    files = sorted(glob.glob(os.path.join(path, "*.md")))
    if not files:
        fail(f"卷宗目录存在但读到 0 份：{path}（0 与读不到必须区分）")
    return len(files), [os.path.basename(f) for f in files]


def count_pits():
    path = os.path.join(REPO, "坑库", "pits.md")
    if not os.path.isfile(path):
        fail(f"坑库文件不存在：{path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    pits = set(re.findall(r"PIT-QY-\d+", content))
    if not pits:
        fail("坑库文件存在但读到 0 条 PIT-QY 编号")
    return len(pits)


def count_engine_cognition():
    base = os.path.join(ENGINE, "yin_tai_data", "cognition")
    if not os.path.isdir(base):
        fail(f"引擎认知目录不存在：{base}")
    result = {}
    for level in ["L1", "L2", "L3", "S"]:
        path = os.path.join(base, level)
        if not os.path.isdir(path):
            fail(f"引擎层级目录不存在：{path}（不许当作该层为 0）")
        result[level] = len(glob.glob(os.path.join(path, "*.json")))
    return result


def count_snapshots():
    path = os.path.join(REPO, "snapshots")
    if not os.path.isdir(path):
        fail(f"快照目录不存在：{path}")
    return len(glob.glob(os.path.join(path, "*.md")))


def count_board_posts():
    """走廊发帖数。

    走廊在另一个仓库，本地只有副本。这里只数本地可达副本，
    并显式标注口径与不可达部分——不拿手写列表冒充满。
    返回 (可达篇数, 口径说明)。
    """
    local_dir = os.path.join(REPO, "cur")
    reachable = 0
    if os.path.isdir(local_dir):
        reachable = len(glob.glob(os.path.join(local_dir, "*.md")))
    caliber = (
        f"本地副本 {reachable} 篇（口径：本地 cur/ 目录 .md 文件数）；"
        f"走廊全量口径需查 GitHub API board/ 下含 qingyuan 的 .md，本地不可达，不作数"
    )
    return reachable, caliber


def main():
    strict = "--strict" in sys.argv
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = []
    code = 0

    def run(name, fn, layer):
        nonlocal code
        try:
            return fn(), None
        except RuntimeError as e:
            code = 2
            return None, f"UNAVAILABLE（{layer}）：{e}"

    jz, jz_err = run("卷宗", count_juanzong, "数文件")
    pt, pt_err = run("坑库", count_pits, "数编号")
    cog, cog_err = run("引擎认知", count_engine_cognition, "数 json 文件")
    sn, sn_err = run("快照", count_snapshots, "数文件")
    bp, bp_caliber = count_board_posts()

    print(f"# 清渊进度节自动统计（程序生成，{now}）")
    print("")
    print(f"- 道统卷宗：{jz[0] if jz else jz_err}份　[来源：数 .md 文件，1 层]")
    print(f"- 坑库：{pt if pt is not None else pt_err}条　[来源：正则数 PIT-QY 编号，1 层]")
    if cog:
        total = sum(cog.values())
        print(f"- 引擎认知：L1={cog['L1']} L2={cog['L2']} L3={cog['L3']} S={cog['S']} 合计={total}　[来源：数各层 .json，1 层；注意：数量不等于内容连续（判据14）]")
    else:
        print(f"- 引擎认知：{cog_err}")
    print(f"- 快照：{sn if sn is not None else sn_err}份　[来源：数 .md 文件，1 层]")
    print(f"- 走廊已发帖：{bp_caliber}")
    print("")
    if jz:
        print("# 卷宗清单：")
        for f in jz[1]:
            print(f"  - {f}")
        print("")
    if WARNINGS:
        print("# 告警（数据源不可达，不许当 0 看）：")
        for w in WARNINGS:
            print(f"  ! {w}")
    else:
        print("# 告警：无（全部数据源可达）")
    print("")
    print("# 说明：数字由程序统计非手写；读不到一律 UNAVAILABLE，不静默归零。")

    if strict and code != 0:
        sys.exit(code)


if __name__ == "__main__":
    main()
