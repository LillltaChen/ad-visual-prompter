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
    data = []
    for it in items:
        prompt_raw = it["prompt"]
        prompt_esc = esc(prompt_raw).replace("\n", "<br>")
        tpl = esc(it.get("template") or "").replace("\n", "<br>")
        tpl_block = f'<div class="tpl"><div class="tpl-tag">可变量模板</div><div class="tpl-body">{tpl}</div></div>' if tpl else ""
        link = f'<a class="link" href="{esc(it["links"])}" target="_blank" rel="noopener">参考链接 ↗</a>' if it.get("links") else ""
        # 效果图：assets/gallery/{编号}/ 下第一张图
        img_rel = ""
        img_dir = gallery_root / it["number"]
        if img_dir.is_dir():
            imgs = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
            if imgs:
                img_rel = f"../assets/gallery/{it['number']}/{imgs[0].name}"
                img_html = f'<div class="thumb-wrap"><img class="thumb" loading="lazy" src="{esc(img_rel)}" alt="{esc(it["number"])} 效果图"></div>'
            else:
                img_html = ""
        else:
            img_html = ""
        cards.append(f"""<div class="card" data-prefix="{esc(it['number'].split('-')[0])}" data-cat="{esc(it['category'])}" data-text="{esc((it['title'] + ' ' + it['prompt']).lower())}" data-num="{esc(it['number'])}">
  {img_html}<div class="card-head"><span class="num">{esc(it['number'])}</span><span class="cat">{esc(it['category'])}</span></div>
  <div class="title">{esc(it['title'])}</div>
  <button class="view-btn" type="button">查看详情 · 复制提示词</button>
</div>""")
        data.append({
            "number": it["number"], "title": it["title"], "category": it["category"],
            "prompt": prompt_raw, "template": it.get("template") or "",
            "links": it.get("links") or "", "img": img_rel,
        })
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    tabs = '<button class="tab" data-filter="all">全部（{}）</button>'.format(len(items)) + "".join(
        f'<button class="tab{" active" if p == "PA" else ""}" data-filter="{p}">{p} · {c["name"]}（{c["count"]}）</button>'
        for p, c in cats.items()
    )

    total = len(items)
    stats = "".join(
        f'<span class="stat"><b>{c["count"]}</b>{p} · {c["name"]}</span>' for p, c in cats.items()
    ) + f'<span class="stat"><b>{total}</b>全部</span>'

    html_doc = f"""<html style="margin:0;padding:0;">
<title>AI 广告视觉提示词库 · 编号画廊</title>
<div style="width:100%;box-sizing:border-box;min-height:100vh;background:#f6f8fb;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#0f172a;">
  <div class="hero" style="box-sizing:border-box;background:linear-gradient(135deg,#0b1220 0%,#16224d 55%,#1f3a8a 100%);color:#fff;padding:44px 28px 34px;">
    <div style="max-width:1180px;margin:0 auto;">
      <div class="badge" style="display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#93c5fd;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:6px 14px;">Ad Visual Prompter</div>
      <h1 style="margin:14px 0 6px;font-size:30px;font-weight:700;letter-spacing:-.01em;">AI 广告视觉提示词库</h1>
      <p style="margin:0;font-size:14px;color:#c7d4f0;">{total} 条经实测的竖版广告生图提示词 · 点击「查看完整提示词」复制原文 · 来源：飞书多维表格「使用 Image 2.5」@ AI 广告视觉 作品合集</p>
      <div class="stats" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;">{stats}</div>
    </div>
  </div>
  <div class="toolbar" style="position:sticky;top:0;z-index:10;background:rgba(248,250,252,.86);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid #e2e8f0;padding:12px 28px;">
    <div style="max-width:1180px;margin:0 auto;">
      <div style="display:flex;gap:10px;align-items:stretch;margin-bottom:10px;">
        <div style="position:relative;flex:1;">
          <svg style="position:absolute;left:12px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:#94a3b8;pointer-events:none;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
          <input id="search" type="text" placeholder="搜索标题或提示词关键词…" style="width:100%;box-sizing:border-box;padding:10px 12px 10px 36px;font-size:14px;border:1px solid #cbd5e1;border-radius:10px;background:#fff;outline:none;box-shadow:0 1px 2px rgba(15,23,42,.04);">
        </div>
        <div class="seg" style="display:flex;align-items:center;gap:2px;background:#eef2f7;border:1px solid #e2e8f0;border-radius:10px;padding:3px;flex-shrink:0;">
          <span style="font-size:12px;color:#64748b;padding:0 8px;">尺寸</span>
          <button class="size-btn" data-size="s">小</button>
          <button class="size-btn" data-size="m">中</button>
          <button class="size-btn" data-size="l">大</button>
        </div>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">{tabs}</div>
    </div>
  </div>
  <main style="max-width:1180px;margin:0 auto;padding:20px 28px 8px;">
    <div id="grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">{''.join(cards)}</div>
    <div style="display:flex;flex-wrap:wrap;gap:10px;font-size:12px;color:#94a3b8;margin:18px 0 26px;">
      <span>提示词为原文逐字收录，含具体品牌与版式细节，出图时建议直接使用原文。</span>
      <span>缩略图为该编号在飞书表格中的效果图（本地缓存，3:4 竖版）。</span>
      <span>技能：ad-visual-prompter</span>
    </div>
  </main>
  <div class="overlay" id="overlay" aria-hidden="true">
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-head">
        <div class="modal-meta">
          <span class="num" id="mNum"></span>
          <span class="cat" id="mCat"></span>
        </div>
        <span class="modal-title" id="mTitle"></span>
        <button class="close-btn" id="mClose" type="button" aria-label="关闭">✕</button>
      </div>
      <div class="modal-body">
        <div class="modal-fig"><img id="mImg" alt="效果图"></div>
        <div class="modal-info">
          <div class="prompt-wrap">
            <button class="copy-btn" id="mCopy" type="button">复制提示词</button>
            <div class="prompt-scroll" id="mPrompt"></div>
          </div>
          <div id="mTpl" class="tpl" style="display:none;"></div>
          <div id="mLink" style="font-size:13px;margin-top:2px;"></div>
        </div>
      </div>
    </div>
  </div>
</div>
<script id="gal-data" type="application/json">{data_json}</script>
<style>
  .tab{{font-size:13px;font-weight:600;padding:7px 13px;border:1px solid transparent;border-radius:999px;background:#fff;color:#475569;cursor:pointer;transition:all .18s ease;box-shadow:0 1px 2px rgba(15,23,42,.05);}}
  .tab:hover{{color:#1e40af;background:#eff6ff;}}
  .tab.active{{background:linear-gradient(135deg,#1d4ed8,#2563eb);color:#fff;box-shadow:0 2px 8px rgba(37,99,235,.35);}}
  .stat{{font-size:12px;color:#c7d4f0;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:6px 12px;}}
  .stat b{{font-weight:700;color:#fff;margin-right:6px;}}
  .seg .size-btn{{font-size:13px;font-weight:600;padding:6px 12px;border:1px solid transparent;background:transparent;border-radius:8px;color:#64748b;cursor:pointer;transition:all .15s ease;}}
  .seg .size-btn:hover{{color:#1e40af;}}
  .seg .size-btn.active{{background:#fff;color:#1d4ed8;box-shadow:0 1px 3px rgba(15,23,42,.14);border-color:#e2e8f0;}}
  #search:focus{{border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.15);}}
  .card{{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:12px;box-sizing:border-box;box-shadow:0 1px 2px rgba(15,23,42,.05);transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;display:flex;flex-direction:column;cursor:pointer;}}
  .card:hover{{transform:translateY(-2px);box-shadow:0 10px 24px rgba(15,23,42,.10);border-color:#c7d2fe;}}
  .thumb-wrap{{position:relative;border-radius:10px;overflow:hidden;margin-bottom:10px;background:#eef2f7;}}
  .thumb{{display:block;width:100%;aspect-ratio:3/4;object-fit:cover;transition:transform .3s ease;}}
  .card:hover .thumb{{transform:scale(1.03);}}
  .card-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;gap:8px;}}
  .num{{font-weight:700;color:#1d4ed8;font-size:13px;font-variant-numeric:tabular-nums;letter-spacing:.02em;}}
  .cat{{font-size:11px;font-weight:600;color:#4338ca;background:#eef2ff;border:1px solid #e0e7ff;border-radius:6px;padding:2px 8px;white-space:nowrap;}}
  .title{{font-size:14px;font-weight:600;color:#0f172a;line-height:1.45;margin-bottom:10px;}}
  .view-btn{{margin-top:auto;font-size:13px;font-weight:600;color:#1d4ed8;background:#eff6ff;border:1px solid #dbeafe;border-radius:9px;padding:8px 10px;cursor:pointer;transition:all .15s ease;}}
  .view-btn:hover{{background:#1d4ed8;color:#fff;border-color:#1d4ed8;}}
  .overlay{{position:fixed;inset:0;background:rgba(15,23,42,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;padding:20px;z-index:100;opacity:0;pointer-events:none;transition:opacity .2s ease;}}
  .overlay.show{{opacity:1;pointer-events:auto;}}
  .modal{{background:#fff;border-radius:18px;max-width:920px;width:100%;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 24px 60px rgba(15,23,42,.30);transform:translateY(14px) scale(.98);transition:transform .22s ease;}}
  .overlay.show .modal{{transform:none;}}
  .modal-head{{display:flex;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid #eef2f7;flex-shrink:0;}}
  .modal-meta{{display:flex;gap:8px;align-items:center;flex-shrink:0;}}
  .modal-title{{font-size:16px;font-weight:700;color:#0f172a;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
  .close-btn{{flex-shrink:0;width:32px;height:32px;border:none;border-radius:9px;background:#f1f5f9;color:#475569;font-size:15px;cursor:pointer;transition:all .15s ease;}}
  .close-btn:hover{{background:#fee2e2;color:#b91c1c;}}
  .modal-body{{display:flex;flex:1;min-height:0;}}
  .modal-fig{{flex:0 0 42%;background:#eef2f7;display:flex;align-items:stretch;overflow:hidden;}}
  .modal-fig img{{width:100%;height:100%;object-fit:cover;display:block;}}
  .modal-info{{flex:1;min-width:0;display:flex;flex-direction:column;padding:16px 18px 18px;gap:10px;overflow:hidden;}}
  .prompt-wrap{{position:relative;flex:1;min-height:0;background:#f8fafc;border:1px solid #eef2f7;border-radius:12px;}}
  .copy-btn{{position:absolute;top:10px;right:10px;z-index:2;font-size:12px;font-weight:700;color:#fff;background:#1d4ed8;border:none;border-radius:8px;padding:7px 12px;cursor:pointer;box-shadow:0 2px 6px rgba(29,78,216,.35);transition:all .15s ease;}}
  .copy-btn:hover{{background:#1e40af;}}
  .copy-btn.copied{{background:#15803d;}}
  .prompt-scroll{{height:100%;overflow-y:auto;padding:14px 14px 14px;box-sizing:border-box;font-size:13px;line-height:1.75;color:#334155;white-space:pre-line;word-break:break-word;}}
  .tpl{{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:10px 12px;}}
  .tpl-tag{{font-size:11px;font-weight:700;color:#b45309;margin-bottom:4px;}}
  .tpl-body{{font-size:13px;color:#475569;white-space:pre-line;}}
  .link{{font-size:12px;font-weight:600;color:#15803d;}}
  @media (max-width:640px){{
    .hero{{padding:32px 18px 26px;}}
    .toolbar{{padding:12px 18px;}}
    main{{padding:16px 18px 8px;}}
    .toolbar > div > div:first-child{{flex-wrap:wrap;}}
    #search{{flex:1 1 100%;}}
    .modal{{max-height:92vh;}}
    .modal-body{{flex-direction:column;}}
    .modal-fig{{flex:none;max-height:34vh;}}
  }}
</style>
<script>
(function(){{
  var grid=document.getElementById('grid'),search=document.getElementById('search'),cards=[].slice.call(grid.querySelectorAll('.card'));
  var cur='PA';
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  var sizes={{'s':'repeat(auto-fill,minmax(180px,1fr))','m':'repeat(auto-fill,minmax(280px,1fr))','l':'repeat(auto-fill,minmax(400px,1fr))'}};
  var sizeBtns=[].slice.call(document.querySelectorAll('.size-btn'));
  var sz=localStorage.getItem('gal_size')||'m';
  function setSize(s){{
    sz=s;grid.style.gridTemplateColumns=sizes[s];
    sizeBtns.forEach(function(b){{b.classList.toggle('active',b.getAttribute('data-size')===s);}});
    try{{localStorage.setItem('gal_size',s);}}catch(e){{}}
  }}
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
  sizeBtns.forEach(function(b){{
    b.addEventListener('click',function(){{setSize(b.getAttribute('data-size'));}});
  }});
  search.addEventListener('input',apply);

  // 详情弹层
  var DATA;
  try{{DATA=JSON.parse(document.getElementById('gal-data').textContent);}}catch(e){{DATA=[];}}
  var byNum={{}};DATA.forEach(function(d){{byNum[d.number]=d;}});
  var overlay=document.getElementById('overlay'),mImg=document.getElementById('mImg'),
      mNum=document.getElementById('mNum'),mCat=document.getElementById('mCat'),
      mTitle=document.getElementById('mTitle'),mPrompt=document.getElementById('mPrompt'),
      mTpl=document.getElementById('mTpl'),mLink=document.getElementById('mLink'),
      mCopy=document.getElementById('mCopy'),mClose=document.getElementById('mClose');
  function fillText(el,html){{
    if(!el)return;
    var wrap=document.createElement('div');wrap.innerHTML=html||'';el.textContent=wrap.textContent||'';
  }}
  function openModal(num){{
    var d=byNum[num];if(!d)return;
    mNum.textContent=d.number;mCat.textContent=d.category;mTitle.textContent=d.title;
    if(d.img){{mImg.src=d.img;mImg.style.display='block';}}else{{mImg.removeAttribute('src');mImg.style.display='none';}}
    fillText(mPrompt,d.prompt);
    if(d.template){{
      mTpl.style.display='';mTpl.innerHTML='<div class="tpl-tag">可变量模板</div><div class="tpl-body"></div>';
      fillText(mTpl.querySelector('.tpl-body'),d.template);
    }}else{{mTpl.style.display='none';mTpl.innerHTML='';}}
    mLink.innerHTML=d.links?'<a class="link" href="'+d.links+'" target="_blank" rel="noopener">参考链接 ↗</a>':'';
    mCopy.textContent='复制提示词';mCopy.classList.remove('copied');
    overlay.classList.add('show');overlay.setAttribute('aria-hidden','false');
    document.body.style.overflow='hidden';
    try{{history.replaceState(null,'','#'+num);}}catch(e){{}}
  }}
  function closeModal(){{
    overlay.classList.remove('show');overlay.setAttribute('aria-hidden','true');
    document.body.style.overflow='';
    try{{history.replaceState(null,'',location.pathname+location.search);}}catch(e){{}}
  }}
  cards.forEach(function(c){{
    c.addEventListener('click',function(){{openModal(c.getAttribute('data-num'));}});
  }});
  mClose.addEventListener('click',closeModal);
  overlay.addEventListener('click',function(e){{if(e.target===overlay)closeModal();}});
  document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeModal();}});
  mCopy.addEventListener('click',function(){{
    var d=byNum[mNum.textContent];if(!d)return;
    var done=function(){{
      mCopy.textContent='已复制 ✓';mCopy.classList.add('copied');
      setTimeout(function(){{mCopy.textContent='复制提示词';mCopy.classList.remove('copied');}},2000);
    }};
    if(navigator.clipboard&&window.isSecureContext){{
      navigator.clipboard.writeText(d.prompt).then(done,function(){{
        var ta=document.createElement('textarea');ta.value=d.prompt;
        ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);
        ta.select();try{{document.execCommand('copy');done();}}catch(err){{}}ta.remove();
      }});
    }}else{{
      var ta=document.createElement('textarea');ta.value=d.prompt;
      ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);
      ta.select();try{{document.execCommand('copy');done();}}catch(err){{}}ta.remove();
    }}
  }});
  if(location.hash&&byNum[location.hash.slice(1)])openModal(location.hash.slice(1));
  setSize(sz);apply();
}})();
</script>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"已生成画廊: {OUT}（{len(items)} 条）")


if __name__ == "__main__":
    main()
