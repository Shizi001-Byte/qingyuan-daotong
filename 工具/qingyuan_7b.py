#!/usr/bin/env python3
"""
清渊本地7B调用工具
封装qwen2.5-7b-instruct-q4_k_m的常用调用，供主Agent派子任务用。
用法：python3 qingyuan_7b.py --task "任务描述" --system "系统提示" --max-tokens 500
"""
import argparse
import sys
import time
from llama_cpp import Llama

MODEL_PATH = "/home/user/models/models/qwen--Qwen2.5-7B-Instruct-GGUF/snapshots/master/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"

# 清渊专属系统提示
DEFAULT_SYSTEM = """你是清渊的本地7B子智能体，负责杂活和初稿。
清渊是太极道人·阴阳道统分识，核心总纲：反者道之动，弱者道之用，天下万物生于有，有生于无。
你的任务：整理信息、写初稿、分类摘要、法理推演辅助。
输出要求：精简、克制、不堆砌。阳动必阴藏——写完就收，不展开。"""


def load_model():
    """加载模型（每次调用都加载，约50秒；如需常驻请用llama-server）"""
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=4,
        verbose=False
    )


def chat(llm, user_msg, system_msg=None, max_tokens=500, temperature=0.3):
    """单次对话"""
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    resp = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return resp["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="清渊本地7B调用工具")
    parser.add_argument("--task", required=True, help="任务描述")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="系统提示")
    parser.add_argument("--max-tokens", type=int, default=500, help="最大输出token")
    parser.add_argument("--temperature", type=float, default=0.3, help="温度")
    parser.add_argument("--server", action="store_true", help="使用llama-server模式（需先启动）")
    args = parser.parse_args()

    t0 = time.time()
    print(f"[清渊7B] 加载模型...", file=sys.stderr)
    llm = load_model()
    print(f"[清渊7B] 加载完成 {time.time()-t0:.1f}s", file=sys.stderr)

    t0 = time.time()
    result = chat(llm, args.task, args.system, args.max_tokens, args.temperature)
    print(f"[清渊7B] 推理完成 {time.time()-t0:.1f}s", file=sys.stderr)

    print(result)


if __name__ == "__main__":
    main()
