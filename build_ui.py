#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 reports/ 下的结构化 GitHub Trending 报告（*.json），
生成一个自包含的静态站点 dist/index.html（内嵌数据），
用于查看每日 / 每周 / 每月的上榜数据，并以卡片形式展示每个 repo 的完整字段。

运行：python build_ui.py
依赖：无（纯标准库；不再依赖 marked.js，直接结构化渲染）

数据来源说明（回应"HTML 写死"疑问）：
  dist/index.html 里的数据由本脚本在「每次运行时」自动扫描 reports/*.json 注入，
  不是手写的死值。自动化每天跑完 build_report.py 会紧接运行本脚本重新生成 dist/，
  所以新报告会自动进入页面。本脚本只负责"构建"。
"""
import os
import re
import json
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT, "reports")
DIST_DIR = os.path.join(ROOT, "dist")

# 文件名形如 github_trending_日报_2026-08-09.json
PATTERN = re.compile(r"github_trending_(日报|周报|月报)_(\d{4}-\d{2}-\d{2})\.json$")

TYPES = ["日报", "周报", "月报"]


def scan_reports():
    reports = []
    for f in glob.glob(os.path.join(REPORT_DIR, "*.json")):
        m = PATTERN.search(os.path.basename(f))
        if not m:
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue
        data.setdefault("type", m.group(1))
        data.setdefault("date", m.group(2))
        reports.append(data)
    return reports


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>GitHub Trending 报告</title>
<style>
  :root{
    --bg:#f7f8fa; --panel:#ffffff; --border:#e5e7eb; --text:#1f2328;
    --muted:#6b7280; --accent:#2563eb; --accent-soft:#eff6ff;
    --new:#16a34a; --shadow:0 1px 3px rgba(0,0,0,.08);
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6}
  header{padding:20px 24px;border-bottom:1px solid var(--border);background:var(--panel)}
  header h1{margin:0;font-size:20px}
  header p{margin:4px 0 0;color:var(--muted);font-size:13px}
  .tabs{display:flex;gap:8px;padding:16px 24px 0}
  .tab{padding:8px 18px;border:1px solid var(--border);border-radius:8px;background:var(--panel);
    cursor:pointer;font-size:14px;color:var(--muted);user-select:none}
  .tab.active{background:var(--accent);border-color:var(--accent);color:#fff}
  .layout{display:flex;gap:16px;padding:16px 24px 40px;align-items:flex-start}
  .sidebar{width:200px;flex:0 0 200px;background:var(--panel);border:1px solid var(--border);
    border-radius:10px;padding:8px;box-shadow:var(--shadow);max-height:78vh;overflow:auto}
  .sidebar .empty{color:var(--muted);font-size:13px;padding:12px}
  .date-item{padding:9px 12px;border-radius:7px;cursor:pointer;font-size:14px;margin-bottom:2px}
  .date-item:hover{background:var(--accent-soft)}
  .date-item.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
  .content{flex:1;min-width:0}
  .overview{background:var(--panel);border:1px solid var(--border);border-radius:10px;
    padding:14px 18px;box-shadow:var(--shadow);margin-bottom:16px;font-size:14px;
    display:flex;flex-wrap:wrap;gap:18px;align-items:center}
  .overview b{color:var(--accent)}
  .overview .new b{color:var(--new)}
  .overview .src{margin-left:auto;color:var(--muted);font-size:12px}
  .cards{display:flex;flex-direction:column;gap:14px}
  .repo{background:var(--panel);border:1px solid var(--border);border-radius:12px;
    padding:16px 20px;box-shadow:var(--shadow)}
  .repo-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .repo .rank{font-size:13px;font-weight:700;color:var(--muted);min-width:34px}
  .repo .name{font-size:17px;font-weight:600;color:var(--accent);text-decoration:none}
  .repo .name:hover{text-decoration:underline}
  .badge-new{background:var(--new);color:#fff;font-size:12px;font-weight:600;
    padding:2px 8px;border-radius:999px}
  .meta{display:flex;flex-wrap:wrap;gap:16px;margin:10px 0 6px;font-size:13px;color:var(--muted)}
  .meta .lang{display:inline-flex;align-items:center;gap:6px}
  .meta .lang .dot{width:10px;height:10px;border-radius:50%;background:#2563eb}
  .meta .period{color:var(--new)}
  .desc{font-size:13px;color:#374151;margin:6px 0 0}
  .intro{margin-top:10px;padding:10px 14px;background:var(--accent-soft);border-radius:9px;
    font-size:14px;color:#1f2937}
  .intro b{color:var(--accent)}
  .placeholder{color:var(--muted);background:var(--panel);border:1px dashed var(--border);
    border-radius:10px;padding:40px;text-align:center}
  @media (max-width:720px){.layout{flex-direction:column}.sidebar{width:100%;flex:none;max-height:none}}
</style>
</head>
<body>
<header>
  <h1>GitHub Trending 报告中心</h1>
  <p>每日 / 每周 / 每月 GitHub 热门项目榜单（结构化展示 + 项目探索简介 + 🆕 新增标记）</p>
</header>
<div class="tabs" id="tabs"></div>
<div class="layout">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="content" id="content"></main>
</div>

<script>
const DATA = /*__DATA__*/;
const TYPES = ["日报","周报","月报"];
const PERIOD_LABEL = {daily:"今日",weekly:"本周",monthly:"本月"};
const grouped = {日报:[],周报:[],月报:[]};
DATA.forEach(r => { (grouped[r.type] = grouped[r.type]||[]).push(r); });
Object.keys(grouped).forEach(t => grouped[t].sort((a,b)=> b.date.localeCompare(a.date)));

let activeType = "日报";
let activeDate = null;

function fmtStars(n){
  if(typeof n !== "number") return "0";
  if(n >= 1000){ return (n/1000).toFixed(1).replace(/\\.0$/,"") + "k"; }
  return String(n);
}
function esc(s){
  return (s||"").replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
}

function renderTabs(){
  const el = document.getElementById("tabs");
  el.innerHTML = "";
  TYPES.forEach(t=>{
    const n = (grouped[t]||[]).length;
    const d = document.createElement("div");
    d.className = "tab" + (t===activeType? " active":"");
    d.textContent = t + (n? " ("+n+")":"");
    d.onclick = ()=>{
      activeType = t; activeDate = null;
      renderTabs(); renderSidebar();
      const list = grouped[activeType]||[];
      if(list.length){ activeDate = list[0].date; renderSidebar(); renderContent(list[0]); }
      else { renderContent(null); }
    };
    el.appendChild(d);
  });
}

function renderSidebar(){
  const el = document.getElementById("sidebar");
  el.innerHTML = "";
  const list = grouped[activeType] || [];
  if(!list.length){
    el.innerHTML = '<div class="empty">暂无'+activeType+'数据</div>';
    return;
  }
  list.forEach(r=>{
    const d = document.createElement("div");
    d.className = "date-item" + (r.date===activeDate? " active":"");
    d.textContent = r.date;
    d.onclick = ()=>{ activeDate = r.date; renderSidebar(); renderContent(r); };
    el.appendChild(d);
  });
}

function repoCard(r){
  const newBadge = r.is_new ? '<span class="badge-new">🆕</span>' : '';
  const periodTxt = (r.stars_period && r.stars_period>0)
    ? '<span class="period">📈 '+ (PERIOD_LABEL[r.type_en]||'本期') +' +'+ r.stars_period.toLocaleString() +'</span>' : '';
  const langTxt = r.language && r.language!=="—"
    ? '<span class="lang"><i class="dot"></i>'+ esc(r.language) +'</span>' : '';
  return '<div class="repo">'
    + '<div class="repo-head">'
    +   '<span class="rank">#'+ r.rank +'</span>'
    +   '<a class="name" href="'+ esc(r.url) +'" target="_blank" rel="noopener">'+ esc(r.key) +'</a>'
    +   newBadge
    + '</div>'
    + '<div class="meta">'
    +   langTxt
    +   '<span title="总 star">⭐ '+ fmtStars(r.stars_total) +'</span>'
    +   periodTxt
    +   '<span title="fork 数">🍴 '+ fmtStars(r.forks) +'</span>'
    + '</div>'
    + (r.description ? '<div class="desc">'+ esc(r.description) +'</div>' : '')
    + '<div class="intro"><b>简介</b>：'+ esc(r.intro || "（暂无简介）") +'</div>'
    + '</div>';
}

function renderContent(rep){
  const el = document.getElementById("content");
  if(!rep){
    el.innerHTML = '<div class="placeholder">从左侧选择一份'+activeType+'报告查看详情</div>';
    return;
  }
  let h = '<div class="overview">';
  h += '<span>本期上榜 <b>'+ rep.count +'</b> 个</span>';
  if(rep.is_first){
    h += '<span class="src">首次记录（无 🆕 对比）</span>';
  }else{
    h += '<span class="new">🆕 新增 <b>'+ rep.new_count +'</b> 个</span>';
    h += '<span>退榜 <b>'+ rep.removed_count +'</b> 个</span>';
  }
  h += '<span class="src">来源 '+ esc(rep.source||"") +' ｜ 抓取 '+ esc(rep.fetched_at||"") +'</span>';
  h += '</div>';
  h += '<div class="cards">';
  (rep.repos||[]).forEach(r => { h += repoCard(r); });
  h += '</div>';
  el.innerHTML = h;
  window.scrollTo({top:0,behavior:"smooth"});
}

function init(){
  renderTabs();
  const list = grouped[activeType]||[];
  if(list.length){
    activeDate = list[0].date;
    renderSidebar();
    renderContent(list[0]);
  }else{
    renderSidebar();
    renderContent(null);
  }
}
init();
</script>
</body>
</html>
"""


def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    reports = scan_reports()
    html = TEMPLATE.replace("/*__DATA__*/", json.dumps(reports, ensure_ascii=False))
    out = os.path.join(DIST_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    from collections import Counter
    c = Counter(r.get("type") for r in reports)
    print(f"已生成 {out}（共 {len(reports)} 份报告）")
    print("各类型数量：", dict(c))


if __name__ == "__main__":
    main()
