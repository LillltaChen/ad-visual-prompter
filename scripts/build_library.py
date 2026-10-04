#!/usr/bin/env python3
"""从 prompts.json 生成画廊 gallery/index.html（自包含静态页面）。
用法: python3 build_library.py
"""
from __future__ import annotations
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "references" / "prompts.json"
OUT = ROOT / "gallery" / "index.html"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def main() -> None:
    lib = json.loads(LIB.read_text(encoding="utf-8"))
    items = lib["items"]
    cats = lib["categories"]
    gallery_root = ROOT / "assets" / "gallery"

    cards = []
    for it in items:
        prompt_esc = esc(it["prompt"]).replace("\n", "<br>")
        tpl = esc(it.get("template") or "").replace("\n", "<br>")
        tpl_block = f'<div class="tpl"><div class="tpl-tag">可变量模板</div><div class="tpl-body">{tpl}</div></div>' if tpl else ""
        link = f'<a class="link" href="{esc(it["links"])}" target="_blank" rel="noopener">参考链接 ↗</a>' if it.get("links") else ""
        # 效果图缩略图：assets/gallery/{编号}/ 下第一张图
        img_html = ""
        img_dir = gallery_root / it["number"]
        if img_dir.is_dir():
            imgs = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
            if imgs:
                rel = f"../assets/gallery/{it['number']}/{imgs[0].name}"
                img_html = f'<img class="thumb" loading="lazy" src="{esc(rel)}" alt="{esc(it["number"])} 效果图">'
        cards.append(f"""<div class="card" data-prefix="{esc(it['number'].split('-')[0])}" data-cat="{esc(it['category'])}" data-text="{esc((it['title'] + ' ' + it['prompt']).lower())}">
  {img_html}<div class="card-head"><span class="num">{esc(it['number'])}</span><span class="cat">{esc(it['category'])}</span></div>
  <div class="title">{esc(it['title'])}</div>
  <details><summary>查看完整提示词</summary><div class="prompt">{prompt_esc}</div>{tpl_block}{link}</details>
</div>""")

    tabs = "".join(
        f'<button class="tab{" active" if p == "PA" else ""}" data-filter="{p}">{p} · {c["name"]}（{c["count"]}）</button>'
        for p, c in cats.items()
    ) + '<button class="tab" data-filter="all">全部（{}）</button>'.format(len(items))

    html_doc = f"""<html style="margin:0;padding:0;">
<title>AI 广告视觉提示词库 · 编号画廊</title>
<div style="width:100%;box-sizing:border-box;background:#f6f8fb;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;padding:24px 20px;color:#1a2333;">
  <div style="font-size:20px;font-weight:700;">AI 广告视觉提示词库 · 编号画廊</div>
  <div style="font-size:13px;color:#5a6b85;margin:4px 0 16px;">{len(items)} 条广告生图提示词 · 来源：飞书多维表格「使用 Image 2.5」@ AI 广告视觉 作品合集 · 点击「查看完整提示词」复制原文</div>
  <input id="search" type="text" placeholder="搜索标题或提示词关键词…" style="width:100%;box-sizing:border-box;padding:10px 12px;font-size:14px;border:1px solid #c9d4e4;border-radius:8px;margin-bottom:12px;">
  <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">{tabs}</div>
  <div id="grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;">{''.join(cards)}</div>
  <div style="font-size:12px;color:#8a97ad;margin-top:16px;">提示词为原文逐字收录，含具体品牌与版式细节；出图时建议直接使用原文。缩略图为该编号在飞书表格中的效果图（本地缓存）。</div>
</div>
<style>
  .card{{background:#fff;border:1px solid #d5deea;border-radius:10px;padding:12px;box-sizing:border-box;}}
  .thumb{{width:100%;height:160px;object-fit:cover;border-radius:8px;margin-bottom:8px;background:#eef2f6;}}
  .card-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}}
  .num{{font-weight:700;color:#2047f2;font-size:13px;}}
  .cat{{font-size:12px;color:#5a6b85;background:#eef2ff;border-radius:4px;padding:2px 6px;}}
  .title{{font-size:14px;font-weight:600;color:#1a2333;line-height:1.4;margin-bottom:6px;}}
  details summary{{font-size:13px;color:#2047f2;cursor:pointer;}}
  .prompt{{font-size:13px;line-height:1.6;color:#33415a;margin-top:8px;white-space:pre-line;word-break:break-word;}}
  .tpl{{background:#fff8f0;border-left:3px solid #c05621;border-radius:6px;padding:8px;margin-top:8px;}}
  .tpl-tag{{font-size:12px;font-weight:700;color:#c05621;margin-bottom:4px;}}
  .tpl-body{{font-size:13px;color:#33415a;white-space:pre-line;}}
  .link{{font-size:12px;color:#3d7a2e;}}
</style>
<script>
(function(){{
  var grid=document.getElementById('grid'),search=document.getElementById('search'),cards=[].slice.call(grid.querySelectorAll('.card'));
  var cur='PA';
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  function apply(){{
    var kw=search.value.trim().toLowerCase();
    cards.forEach(function(c){{
      var ok=(cur==='all'||c.getAttribute('data-prefix')===cur)&&(!kw||c.getAttribute('data-text').indexOf(kw)>=0);
      c.style.display=ok?'':'none';
    }});
  }}
  tabs.forEach(function(t){{
    t.addEventListener('click',function(){{
      tabs.forEach(function(x){{x.classList.remove('active');}});t.classList.add('active');
      cur=t.getAttribute('data-filter');apply();
    }});
  }});
  search.addEventListener('input',apply);
  apply();
}})();
</script>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"已生成画廊: {OUT}（{len(items)} 条）")


if __name__ == "__main__":
    main()
