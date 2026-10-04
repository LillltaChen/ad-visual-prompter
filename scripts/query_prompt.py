#!/usr/bin/env python3
"""查询 AI 广告视觉提示词库。
用法:
  python3 query_prompt.py --number PA-012            # 按编号取单条
  python3 query_prompt.py --search "奶茶"             # 按关键词搜索标题/提示词
  python3 query_prompt.py --category 产品展示         # 按分类列出全部编号+标题
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "references" / "prompts.json"


def load() -> dict:
    with open(LIB, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    ap = argparse.ArgumentParser(description="查询 AI 广告视觉提示词库")
    ap.add_argument("--number", help="编号，如 PA-012 / ca-003（大小写不敏感）")
    ap.add_argument("--search", help="关键词搜索标题与提示词")
    ap.add_argument("--category", help="分类名，如 产品展示 / 内容创作")
    ap.add_argument("--json-out", action="store_true", help="以 JSON 输出完整记录")
    args = ap.parse_args()

    lib = load()
    items = lib["items"]
    if not (args.number or args.search or args.category):
        ap.error("必须提供 --number / --search / --category 之一")

    results = []
    if args.number:
        num = args.number.strip().upper()
        hits = [it for it in items if it["number"] == num]
        if not hits:
            sys.exit(f"无效编号 {num}；可用范围：PA-001~PA-076, CA-001~CA-070, BV-001~BV-008, MK-001~MK-006, EC-001~EC-004, NA-001")
        results = hits
    elif args.category:
        cat = args.category.strip()
        results = [it for it in items if it["category"] == cat or it["category_id"].upper() == cat.upper()]
        if not results:
            avail = "、".join(f"{p} {c['name']}({c['count']}条)" for p, c in lib["categories"].items())
            sys.exit(f"分类「{cat}」无记录；可选：{avail}")
    elif args.search:
        kw = args.search.strip().lower()
        results = [it for it in items if kw in it["title"].lower() or kw in (it["prompt"] or "").lower()]

    if args.json_out:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    for it in results:
        print(f"【{it['number']} · {it['title']}】({it['category']})")
        print(it["prompt"])
        if it.get("template"):
            print("\n--- 可变量模板 ---")
            print(it["template"])
        print("-" * 60)


if __name__ == "__main__":
    main()
