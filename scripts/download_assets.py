#!/usr/bin/env python3
"""从飞书多维表格下载效果图到本地，作为出图参考图。
依赖宿主环境的 lark-cli（需已登录，--as user）。

用法:
  python3 download_assets.py --number PA-012 --base-token <token> --table-id <table> [--out dir]
  python3 download_assets.py --all --base-token <token> --table-id <table> [--out dir]
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "references" / "prompts.json"
DEFAULT_OUT = ROOT / "assets" / "gallery"


def load() -> dict:
    with open(LIB, encoding="utf-8") as f:
        return json.load(f)


def download_one(lib: dict, number: str, base_token: str, table_id: str, out_dir: Path, overwrite: bool) -> None:
    hits = [it for it in lib["items"] if it["number"].upper() == number.upper()]
    if not hits:
        sys.exit(f"无效编号 {number}")
    it = hits[0]
    atts = it.get("attachments") or []
    if not atts:
        print(f"{number} 无附件，跳过")
        return
    record_id = it["record_id"]
    # 只下载首张作为参考图；如需全部，文件可用 --all 或直接下载该记录全部
    tok = atts[0]["file_token"]
    out = out_dir / number
    out.mkdir(parents=True, exist_ok=True)
    cmd = [
        "lark-cli", "base", "+record-download-attachment",
        "--base-token", base_token, "--table-id", table_id,
        "--record-id", record_id, "--file-token", tok,
        "--output", str(out), "--format", "json",
    ]
    if overwrite:
        cmd.append("--overwrite")
    print(f"下载 {number} → {out}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [失败] {res.stderr.strip() or res.stdout.strip()}")
    else:
        print(f"  [成功] {res.stdout.strip()[:200]}")


def main() -> None:
    ap = argparse.ArgumentParser(description="下载提示词库效果图")
    ap.add_argument("--number", help="编号，如 PA-012")
    ap.add_argument("--all", action="store_true", help="下载全部 165 条的首张参考图")
    ap.add_argument("--base-token", required=True, help="飞书多维表格 base_token")
    ap.add_argument("--table-id", required=True, help="飞书数据表 table_id")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="输出目录")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在文件")
    args = ap.parse_args()

    if not (args.number or args.all):
        ap.error("必须提供 --number 或 --all")
    lib = load()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if args.number:
        download_one(lib, args.number, args.base_token, args.table_id, out, args.overwrite)
    else:
        for it in lib["items"]:
            download_one(lib, it["number"], args.base_token, args.table_id, out, args.overwrite)


if __name__ == "__main__":
    main()
