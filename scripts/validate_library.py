#!/usr/bin/env python3
"""校验 AI 广告视觉提示词库完整性。
检查：编号唯一且连续、分类计数与元数据一致、必填字段非空、record_id 存在。
用法: python3 validate_library.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "references" / "prompts.json"

PREFIX_ORDER = ["PA", "CA", "BV", "MK", "EC", "NA"]


def main() -> None:
    lib = json.loads(LIB.read_text(encoding="utf-8"))
    items = lib["items"]
    errors: list[str] = []

    if lib["total"] != len(items):
        errors.append(f"total({lib['total']}) 与实际条数({len(items)}) 不一致")

    seen: set[str] = set()
    warnings: list[str] = []
    for it in items:
        num = it["number"]
        if num in seen:
            errors.append(f"编号重复: {num}")
        seen.add(num)
        if not it.get("title"):
            errors.append(f"{num} 缺标题")
        if not it.get("prompt"):
            warnings.append(f"{num} 提示词为空（源表未收录，仅有效果图参考）")
        if not it.get("record_id"):
            errors.append(f"{num} 缺 record_id")
        prefix = num.split("-")[0]
        if prefix not in PREFIX_ORDER:
            errors.append(f"{num} 前缀非法: {prefix}")

    # 编号连续性：每个前缀内部 001 起连续
    by_prefix: dict[str, list[str]] = {}
    for it in items:
        p, seq = it["number"].split("-")
        by_prefix.setdefault(p, []).append(int(seq))
    for p in PREFIX_ORDER:
        seqs = sorted(by_prefix.get(p, []))
        expected = list(range(1, len(seqs) + 1))
        if seqs != expected:
            errors.append(f"{p} 编号不连续: {seqs}")

    # 分类计数与 categories 元数据核对
    from collections import Counter
    real = Counter(it["number"].split("-")[0] for it in items)
    for p, meta in lib["categories"].items():
        if meta["count"] != real.get(p, 0):
            errors.append(f"分类 {p} 元数据计数({meta['count']}) 与实际({real.get(p,0)}) 不一致")

    if errors:
        print(f"FAIL: {len(errors)} 个问题")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"PASS: {len(items)} 条记录，编号唯一且连续，必填字段完整，分类计数一致。")
    for w in warnings:
        print("WARN:", w)


if __name__ == "__main__":
    main()
