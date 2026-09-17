#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 reports/ 下的结构化 GitHub Trending 报告（*.json），
生成一个自包含的静态站点 dist/index.html（内嵌数据），
用于查看每日 / 每周 / 每月的上榜数据，并以卡片形式展示每个 repo 的完整字段。
同时支持「⭐ 收藏」功能：
  - localStorage 存实时收藏（前端最简），收藏项可打多个标签
  - data/favorites.md 可手动维护，每行格式：
      - [owner/repo](https://github.com/owner/repo) — Lang — `2026-08-25T13:57:34+08:00` — #tag1 #tag2
  - build 时会读取 data/favorites.md 合并到收藏 tab 中持久展示（含标签）
  - 卡片 #排名 旁边有 ⭐/☆ 切换按钮
  - 收藏 tab 支持按标签过滤（OR 语义），每个卡片可加 / 删标签

运行：python build_ui.py
依赖：无（纯标准库；不再依赖 marked.js，直接结构化渲染）
"""
import os
import re
import json
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT, "reports")
DIST_DIR = os.path.join(ROOT, "dist")
FAV_PATH = os.path.join(ROOT, "data", "favorites.md")

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


def load_favorites():
    """解析 data/favorites.md，返回收藏列表 [{key, url, language, added_at, source_type, source_date}]。
    兼容两种行格式（手写或导出都 OK）：
      A) [owner/repo](https://github.com/owner/repo) — Lang — `2026-08-25T13:57:34+08:00`
      B) owner/repo | https://github.com/owner/repo | Lang | 2026-08-25T13:57:34+08:00
    解析不到的行静默跳过。
    """
    if not os.path.exists(FAV_PATH):
        return []
    try:
        with open(FAV_PATH, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []

    out = []
    # 匹配模式 A
    # 语言段用非贪婪 (.*?)，允许语言为空或恰好是分隔符字符「—」
    # （某 repo 无语言时 syncToServer 写入 "—"，会出现「— — —」三段，旧正则会误判为分隔符而整行丢弃）
    # 时间戳强制用反引号包裹，避免把语言占位符「—」误当作时间戳前缀
    pat_a = re.compile(
        r"\[([^\]]+)\]\(([^)]+)\)\s*"
        r"[—\-\u2013\u2014]\s*"
        r"(.*?)\s*"
        r"[—\-\u2013\u2014]\s*"
        r"`([^`\n\r]+)`"
        r"\s*(.*)$"
    )
    for line in lines:
        # 去掉前导列表符号（-/*/数字+.）和空白
        s = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line.strip())
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("<!--"):
            continue
        m = pat_a.match(s)
        if m:
            tags = re.findall(r"#(\S+)", m.group(5))
            out.append({
                "key": m.group(1).strip(),
                "url": m.group(2).strip(),
                "language": m.group(3).strip(),
                "added_at": m.group(4).strip(),
                "tags": tags,
            })
            continue
        # 形式 B: 管道分隔
        parts = [p.strip() for p in s.split("|")]
        if len(parts) >= 4 and "/" in parts[0]:
            out.append({
                "key": parts[0],
                "url": parts[1],
                "language": parts[2],
                "added_at": parts[3],
                "tags": [],
            })
    return out


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
    --fav:#f59e0b; --fav-soft:#fffbeb; --fav-border:#fde68a;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6}
  header{padding:20px 24px;border-bottom:1px solid var(--border);background:var(--panel)}
  header h1{margin:0;font-size:20px}
  header p{margin:4px 0 0;color:var(--muted);font-size:13px}
  .tabs{display:flex;gap:8px;padding:16px 24px 0;align-items:center}
  .tab{padding:8px 18px;border:1px solid var(--border);border-radius:8px;background:var(--panel);
    cursor:pointer;font-size:14px;color:var(--muted);user-select:none}
  .tab.active{background:var(--accent);border-color:var(--accent);color:#fff}
  .tab.tab-fav.active{background:var(--fav);border-color:var(--fav);color:#fff}
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
    padding:16px 20px;box-shadow:var(--shadow);position:relative}
  .repo-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .repo .rank{font-size:13px;font-weight:700;color:var(--muted);min-width:34px}
  .repo .name{font-size:17px;font-weight:600;color:var(--accent);text-decoration:none}
  .repo .name:hover{text-decoration:underline}
  .badge-new{background:var(--new);color:#fff;font-size:12px;font-weight:600;
    padding:2px 8px;border-radius:999px}
  .fav-btn{background:transparent;border:none;cursor:pointer;font-size:18px;
    color:#d1d5db;padding:4px 6px;border-radius:6px;line-height:1;
    transition:all .15s;flex:0 0 auto}
  .fav-btn:hover{background:var(--fav-soft);color:var(--fav);transform:scale(1.2)}
  .fav-btn:active{transform:scale(.95)}
  .fav-btn.active{color:var(--fav)}
  .fav-btn.active:hover{color:#dc2626}
  .meta{display:flex;flex-wrap:wrap;gap:16px;margin:10px 0 6px;font-size:13px;color:var(--muted)}
  .meta .lang{display:inline-flex;align-items:center;gap:6px}
  .meta .lang .dot{width:10px;height:10px;border-radius:50%;background:#2563eb}
  .meta .period{color:var(--new)}
  .desc{font-size:13px;color:#374151;margin:6px 0 0}
  .intro{margin-top:10px;padding:10px 14px;background:var(--accent-soft);border-radius:9px;
    font-size:14px;color:#1f2937}
  .intro b{color:var(--accent)}
  .fav-bar{background:var(--fav-soft);border:1px solid var(--fav-border);border-radius:10px;
    padding:14px 18px;box-shadow:var(--shadow);margin-bottom:16px;font-size:14px;
    display:flex;flex-wrap:wrap;gap:18px;align-items:center}
  .fav-bar b{color:#b45309}
  .fav-bar .stats{margin-left:auto;color:var(--muted);font-size:12px}
  .export-btn{padding:7px 14px;background:var(--accent);color:#fff;border:none;
    border-radius:7px;cursor:pointer;font-size:13px;font-weight:500;
    transition:all .15s;display:inline-flex;align-items:center;gap:6px}
  .export-btn:hover{background:#1d4ed8;transform:translateY(-1px);box-shadow:0 2px 6px rgba(37,99,235,.25)}
  .export-btn:active{transform:translateY(0)}
  .placeholder{color:var(--muted);background:var(--panel);border:1px dashed var(--border);
    border-radius:10px;padding:40px;text-align:center}
  .empty-fav{background:var(--panel);border:1px dashed var(--border);border-radius:10px;
    padding:50px 30px;text-align:center;color:var(--muted)}
  .empty-fav .icon{font-size:48px;margin-bottom:12px;opacity:.6}
  .empty-fav .tip{font-size:14px;margin-top:6px;color:#9ca3af}
  /* 标签 */
  .tags-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:12px}
  .tag{display:inline-flex;align-items:center;gap:4px;background:#eef2ff;color:#4338ca;
    border:1px solid #c7d2fe;border-radius:999px;padding:2px 6px 2px 10px;font-size:12px}
  .tag .tag-x{background:none;border:none;color:#6366f1;cursor:pointer;font-size:14px;
    line-height:1;padding:0 2px}
  .tag .tag-x:hover{color:#dc2626}
  .tag-input{border:1px dashed #c7d2fe;border-radius:999px;padding:3px 10px;font-size:12px;
    width:120px;outline:none;color:var(--text)}
  .tag-input:focus{border-color:#6366f1;background:#f5f3ff}
  .tag-input-wrap{position:relative;display:inline-flex}
  .tag-suggestions{position:absolute;top:calc(100% + 4px);left:0;z-index:20;
    background:#fff;border:1px solid #c7d2fe;border-radius:8px;box-shadow:0 6px 18px rgba(67,56,202,.18);
    min-width:172px;max-height:240px;overflow:auto;padding:4px}
  .tag-suggestion{padding:6px 10px;border-radius:6px;font-size:13px;cursor:pointer;
    color:#4338ca;white-space:nowrap;display:flex;align-items:center;gap:6px}
  .tag-suggestion:hover,.tag-suggestion.active{background:#eef2ff}
  .tag-suggestion-new{color:#16a34a;font-weight:600}
  .tag-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
  .tag-filter-chip{cursor:pointer;font-size:13px;padding:5px 12px;border:1px solid var(--border);
    border-radius:999px;background:var(--panel);color:var(--muted);user-select:none;transition:all .12s}
  .tag-filter-chip:hover{border-color:#6366f1;color:#4338ca}
  .tag-filter-chip.active{background:#4338ca;border-color:#4338ca;color:#fff}
  /* 顶部同步状态条 */
  #sync-status{padding:8px 24px;font-size:13px;text-align:center;
    background:var(--fav-soft);color:#92400e;border-bottom:1px solid var(--fav-border);
    transition:background .2s,color .2s}
  #sync-status.sync-offline{background:#f3f4f6;color:#6b7280;border-bottom-color:#e5e7eb}
  #sync-status.sync-error{background:#fee2e2;color:#991b1b;border-bottom-color:#fca5a5}
  #sync-status.sync-synced{background:#dbeafe;color:#1e40af;border-bottom-color:#93c5fd}
  #sync-status.sync-rebuilt{background:#d1fae5;color:#065f46;border-bottom-color:#6ee7b7}
  #sync-status.sync-syncing{background:#fef3c7;color:#92400e;border-bottom-color:#fcd34d}
  @media (max-width:720px){.layout{flex-direction:column}.sidebar{width:100%;flex:none;max-height:none}}
</style>
</head>
<body>
<header>
  <h1>GitHub Trending 报告中心</h1>
  <p>每日 / 每周 / 每月 GitHub 热门项目榜单（结构化展示 + 项目探索简介 + 🆕 新增标记）</p>
</header>
<div id="sync-status" class="sync-offline">⏳ 正在初始化 …</div>
<div class="tabs" id="tabs"></div>
<div class="layout">
  <aside class="sidebar" id="sidebar"></aside>
  <main class="content" id="content"></main>
</div>

<script>
const DATA = /*__DATA__*/;
const FAV_SEED = /*__FAVORITES__*/;
const TYPES = ["日报","周报","月报"];
const FAV_TYPE = "⭐ 收藏";
const ALL_TYPES = [...TYPES, FAV_TYPE];
const PERIOD_LABEL = {daily:"今日",weekly:"本周",monthly:"本月"};
const STORAGE_KEY = "gtd_favorites_v1";

// 是否运行在本地 serve.py 环境（提供 /api/write-favorites 与 SSE）。
// GitHub Pages 等纯静态托管下没有后端，收藏退化为纯 localStorage + 导出 Markdown。
const SYNC_AVAILABLE = location.protocol === "http:" &&
  ["localhost","127.0.0.1","[::1]"].includes(location.hostname);

const grouped = {日报:[],周报:[],月报:[]};
DATA.forEach(r => { (grouped[r.type] = grouped[r.type]||[]).push(r); });
Object.keys(grouped).forEach(t => grouped[t].sort((a,b)=> b.date.localeCompare(a.date)));

// 用 FAV_SEED（来自 build 时的 data/favorites.md）作为初始收藏的种子
// key -> {key, url, language, added_at, snapshot}
const FAV_MAP = new Map();
(FAV_SEED || []).forEach(f => {
  if (!f || !f.key) return;
  FAV_MAP.set(f.key, {
    key: f.key,
    url: f.url,
    language: f.language || "—",
    added_at: f.added_at || "",
    snapshot: null,
    tags: f.tags || [],
  });
});

let activeType = "日报";
let activeDate = null;
let activeTagFilters = new Set();

/* ---------- 工具函数 ---------- */
function fmtStars(n){
  if(typeof n !== "number") return "0";
  if(n >= 1000){ return (n/1000).toFixed(1).replace(/\\.0$/,"") + "k"; }
  return String(n);
}
function esc(s){
  return (s||"").replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
}
function nowIso(){
  const d = new Date();
  const pad = n => String(n).padStart(2,"0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}+08:00`;
}

/* ---------- 收藏存储（localStorage） ---------- */
function loadFavStore(){
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Map();
    const arr = JSON.parse(raw);
    const m = new Map();
    arr.forEach(it => { if (it && it.key) m.set(it.key, it); });
    return m;
  } catch(e) {
    return new Map();
  }
}
function saveFavStore(m){
  try {
    const arr = Array.from(m.values());
    localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
  } catch(e) { /* quota / private mode 静默 */ }
}
function isFav(key){
  return loadFavStore().has(key);
}
// 首次进入（或清过缓存）时，用 build 时注入的 FAV_SEED（来自 data/favorites.md）
// 回填收藏，使「清缓存兜底」真正生效：本地没有的收藏项从 seed 补回（含标签）。
function seedFavStoreFromFavSeed(){
  const seed = FAV_SEED || [];
  if (!seed.length) return;
  const m = loadFavStore();
  let changed = false;
  seed.forEach(f => {
    if (!f || !f.key) return;
    if (!m.has(f.key)){
      m.set(f.key, {
        key: f.key,
        url: f.url,
        language: f.language || "—",
        added_at: f.added_at || "",
        tags: f.tags || [],
        snapshot: null,
      });
      changed = true;
    } else {
      const it = m.get(f.key);
      if ((!it.tags || !it.tags.length) && (f.tags || []).length){
        it.tags = f.tags;
        m.set(f.key, it);
        changed = true;
      }
    }
  });
  if (changed) saveFavStore(m);
}
function toggleFav(btnEl){
  const key = btnEl.getAttribute("data-fav-key");
  if (!key) return;
  const m = loadFavStore();
  if (m.has(key)) {
    m.delete(key);
  } else {
    // 从 DATA 找最新 repo 信息，找不到就用收藏 seed 的快照
    let repo = null;
    for (const rep of DATA) {
      if (!rep.repos) continue;
      for (const r of rep.repos) {
        if (r.key === key) { repo = r; break; }
      }
      if (repo) break;
    }
    if (!repo) {
      const seed = FAV_MAP.get(key);
      if (seed) {
        repo = { key, url: seed.url, language: seed.language,
          rank: 0, owner: key.split("/")[0], repo: key.split("/")[1],
          stars_total: 0, forks: 0, stars_period: 0,
          description: "", intro: "" };
      }
    }
    if (!repo) return;
    m.set(key, {
      key: key,
      url: repo.url,
      language: repo.language || "—",
      added_at: nowIso(),
      tags: [],
      snapshot: {
        rank: repo.rank, owner: repo.owner, repo: repo.repo,
        stars_total: repo.stars_total, forks: repo.forks,
        stars_period: repo.stars_period,
        description: repo.description, intro: repo.intro,
      },
    });
  }
  saveFavStore(m);
  // 更新 tab 计数
  renderTabs();
  // 如果当前就在收藏 tab，需要重渲染
  if (activeType === FAV_TYPE) {
    renderSidebar();
    renderContent(null);
  }
  // 更新所有可见星标按钮状态
  document.querySelectorAll('.fav-btn[data-fav-key="'+ cssEscape(key) +'"]').forEach(b => {
    b.classList.toggle("active", m.has(key));
    b.textContent = m.has(key) ? "★" : "☆";
    b.title = m.has(key) ? "取消收藏" : "加入收藏";
  });
  // 同步到 server → data/favorites.md（serve.py 监听到变更会自动 rebuild + SSE 通知 reload）
  syncToServer();
}
function showSyncStatus(state, msg){
  const el = document.getElementById("sync-status");
  if (!el) return;
  el.className = "sync-" + state;
  el.innerHTML = msg;
}
function buildFavMarkdown(){
  const store = loadFavStore();
  const list = mergeWithLiveData(Array.from(store.values()))
    .sort((a,b) => (b.added_at||"").localeCompare(a.added_at||""));
  const today = new Date();
  const pad = n => String(n).padStart(2,"0");
  const dateStr = today.getFullYear() + "-" + pad(today.getMonth()+1) + "-" + pad(today.getDate())
    + " " + pad(today.getHours()) + ":" + pad(today.getMinutes());
  let md = "# 收藏的 GitHub 项目\\n\\n";
  md += "> 最后更新：" + dateStr + " ｜ 共 " + list.length + " 项\\n\\n";
  if (list.length === 0) {
    md += "（暂无收藏，先在页面里点 ☆ 收藏几个项目来吧）\\n";
  } else {
    list.forEach(f => {
      const lang = f.language || "—";
      const ts = f.added_at || "";
      const tagStr = (f.tags && f.tags.length) ? " — " + f.tags.map(t => "#" + t).join(" ") : "";
      md += "- [" + f.key + "](" + f.url + ") — " + lang + " — `" + ts + "`" + tagStr + "\\n";
    });
  }
  md += "\\n<!-- 自动同步于 " + new Date().toISOString() + " -->\\n";
  return md;
}
function downloadFavMd(){
  const md = buildFavMarkdown();
  const blob = new Blob([md], {type: "text/markdown;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "favorites.md";
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 0);
}
function syncToServer(){
  // 静态托管（GitHub Pages）没有后端写入能力，直接跳过同步
  if (!SYNC_AVAILABLE) return;
  const md = buildFavMarkdown();
  showSyncStatus("syncing", "🔄 同步中…（写入 data/favorites.md）");
  fetch("/api/write-favorites", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({content: md}),
  })
  .then(r => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  })
  .then(_ => {
    showSyncStatus("synced", "✅ 已写入 data/favorites.md，serve.py 检测到后将自动 rebuild…");
  })
  .catch(err => {
    showSyncStatus("error", "❌ 同步失败：" + err.message + "（请确认 serve.py 在运行）");
  });
}
function cssEscape(s){
  return (s||"").replace(/"/g, '\\"');
}
function mergeWithLiveData(favList){
  // 用最新 DATA 合并 star/描述/intro
  const liveMap = new Map();
  DATA.forEach(rep => (rep.repos||[]).forEach(r => liveMap.set(r.key, r)));
  return favList.map(f => {
    const live = liveMap.get(f.key);
    if (live) {
      return {
        key: f.key, url: f.url, language: f.language || live.language,
        added_at: f.added_at, is_live: true,
        rank: live.rank, owner: live.owner, repo: live.repo,
        stars_total: live.stars_total, forks: live.forks,
        stars_period: live.stars_period,
        description: live.description, intro: live.intro,
        tags: f.tags || [],
      };
    }
    return Object.assign({is_live: false, tags: f.tags || []}, f, f.snapshot || {});
  });
}

/* ---------- 标签管理 ---------- */
function parseTags(raw){
  if (!raw) return [];
  return raw.split(/[\\s,，、]+/).map(t => t.replace(/^#/, "").trim()).filter(Boolean);
}
function addTag(key, raw){
  const tags = parseTags(raw);
  if (!tags.length) return;
  const m = loadFavStore();
  const it = m.get(key);
  if (!it) return;
  const set = new Set(it.tags || []);
  tags.forEach(t => set.add(t));
  it.tags = Array.from(set);
  m.set(key, it);
  saveFavStore(m);
  renderFavorites();
  syncToServer();
}
function removeTag(key, tag){
  const m = loadFavStore();
  const it = m.get(key);
  if (!it) return;
  it.tags = (it.tags || []).filter(t => t !== tag);
  m.set(key, it);
  saveFavStore(m);
  renderFavorites();
  syncToServer();
}
function toggleTagFilter(tag){
  if (tag === "__all__") {
    activeTagFilters.clear();
  } else if (activeTagFilters.has(tag)) {
    activeTagFilters.delete(tag);
  } else {
    activeTagFilters.add(tag);
  }
  renderFavorites();
}
function addTagFromInput(input){
  addTag(input.getAttribute("data-key"), input.value);
}
function getAllTagsSet(){
  const s = new Set();
  loadFavStore().forEach(f => (f.tags||[]).forEach(t => s.add(t)));
  return s;
}
function renderTagSuggestions(input, key){
  const wrap = input.parentElement;
  let dd = wrap.querySelector(".tag-suggestions");
  if (!dd){
    dd = document.createElement("div");
    dd.className = "tag-suggestions";
    dd.hidden = true;
    wrap.appendChild(dd);
  }
  const store = loadFavStore();
  const card = store.get(key);
  const cardTags = card ? (card.tags||[]) : [];
  const val = (input.value || "").trim().toLowerCase();
  const allTags = Array.from(getAllTagsSet()).filter(t => !cardTags.includes(t));
  const matches = allTags.filter(t => val === "" || t.toLowerCase().indexOf(val) >= 0).sort();
  let html = "";
  const typedExact = allTags.some(t => t.toLowerCase() === val);
  if (input.value.trim() !== "" && val !== "" && !typedExact){
    html += '<div class="tag-suggestion tag-suggestion-new" data-key="'+ esc(key) +'" data-tag="'+ esc(input.value.trim()) +'">➕ 添加新标签「'+ esc(input.value.trim()) +'」</div>';
  }
  if (matches.length === 0 && html === ""){
    dd.hidden = true;
    return;
  }
  matches.forEach(t => {
    html += '<div class="tag-suggestion" data-key="'+ esc(key) +'" data-tag="'+ esc(t) +'">🏷 '+ esc(t) +'</div>';
  });
  dd.innerHTML = html;
  dd.hidden = false;
  dd._activeIdx = -1;
}
function tagSuggestionList(dd){
  return dd ? Array.from(dd.querySelectorAll(".tag-suggestion")) : [];
}
function setActiveSuggestion(dd, idx){
  const list = tagSuggestionList(dd);
  if (!list.length) return;
  idx = Math.max(0, Math.min(idx, list.length-1));
  list.forEach((el,i)=> el.classList.toggle("active", i===idx));
  dd._activeIdx = idx;
}

/* ---------- 渲染 ---------- */
function getFavCount(){
  return loadFavStore().size;
}
// 记住当前视图位置（标签 + 日期），SSE 刷新 / 手动刷新后自动恢复，避免"收藏后回到首页"
function saveViewState(){
  try {
    localStorage.setItem("gtd_view_v1", JSON.stringify({type: activeType, date: activeDate}));
  } catch(e){}
}
function loadViewState(){
  try {
    const raw = localStorage.getItem("gtd_view_v1");
    if (!raw) return null;
    const o = JSON.parse(raw);
    if (o && o.type) return o;
  } catch(e){}
  return null;
}

function renderTabs(){
  const el = document.getElementById("tabs");
  el.innerHTML = "";
  ALL_TYPES.forEach(t=>{
    let n = 0;
    if (t === FAV_TYPE) n = getFavCount();
    else n = (grouped[t]||[]).length;
    const d = document.createElement("div");
    let cls = "tab";
    if (t === FAV_TYPE) cls += " tab-fav";
    if (t === activeType) cls += " active";
    d.className = cls;
    d.textContent = t + (n? " ("+n+")":"");
    d.onclick = ()=>{
      activeType = t; activeDate = null;
      saveViewState();
      renderTabs(); renderSidebar();
      if (t === FAV_TYPE) {
        renderContent(null);
      } else {
        const list = grouped[t]||[];
        if (list.length){ activeDate = list[0].date; renderSidebar(); renderContent(list[0]); }
        else { renderContent(null); }
      }
    };
    el.appendChild(d);
  });
}

function renderSidebar(){
  const el = document.getElementById("sidebar");
  el.innerHTML = "";
  if (activeType === FAV_TYPE) {
    el.innerHTML = '<div class="empty">收藏 tab 不需要日期索引</div>';
    return;
  }
  const list = grouped[activeType] || [];
  if(!list.length){
    el.innerHTML = '<div class="empty">暂无'+activeType+'数据</div>';
    return;
  }
  list.forEach(r=>{
    const d = document.createElement("div");
    d.className = "date-item" + (r.date===activeDate? " active":"");
    d.textContent = r.date;
    d.onclick = ()=>{ activeDate = r.date; saveViewState(); renderSidebar(); renderContent(r); };
    el.appendChild(d);
  });
}

function repoCard(r, opts){
  opts = opts || {};
  const showFav = opts.showFav !== false;
  const tagsHtml = opts.tagsHtml || "";
  const newBadge = r.is_new ? '<span class="badge-new">🆕</span>' : '';
  const periodTxt = (r.stars_period && r.stars_period>0)
    ? '<span class="period">📈 '+ (PERIOD_LABEL[r.type_en]||'本期') +' +'+ r.stars_period.toLocaleString() +'</span>' : '';
  const langTxt = r.language && r.language!=="—"
    ? '<span class="lang"><i class="dot"></i>'+ esc(r.language) +'</span>' : '';
  const favActive = isFav(r.key);
  const favBtn = showFav
    ? '<button class="fav-btn '+ (favActive? "active":"") +'" data-fav-key="'+ esc(r.key) +'" ' +
        'title="'+ (favActive? "取消收藏":"加入收藏") +'">'+ (favActive? "★":"☆") +'</button>'
    : '';
  return '<div class="repo">'
    + '<div class="repo-head">'
    +   '<span class="rank">#'+ (r.rank || "—") +'</span>'
    +   favBtn
    +   '<a class="name" href="'+ esc(r.url) +'" target="_blank" rel="noopener">'+ esc(r.key) +'</a>'
    +   newBadge
    + '</div>'
    + '<div class="meta">'
    +   langTxt
    +   '<span title="总 star">⭐ '+ fmtStars(r.stars_total) +'</span>'
    +   periodTxt
    +   '<span title="fork 数">🍴 '+ fmtStars(r.forks) +'</span>'
    +   (r.is_live === false ? '<span style="color:#9ca3af">📦 快照</span>' : '')
    + '</div>'
    + (r.description ? '<div class="desc">'+ esc(r.description) +'</div>' : '')
    + '<div class="intro"><b>简介</b>：'+ esc(r.intro || "（暂无简介）") +'</div>'
    + tagsHtml
    + '</div>';
}

function renderContent(rep){
  const el = document.getElementById("content");
  if (activeType === FAV_TYPE) {
    renderFavorites();
    return;
  }
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
  (rep.repos||[]).forEach(r => { h += repoCard(r, {showFav: true}); });
  h += '</div>';
  el.innerHTML = h;
  window.scrollTo({top:0,behavior:"smooth"});
}

function renderFavorites(){
  const el = document.getElementById("content");
  const store = loadFavStore();
  let list = mergeWithLiveData(Array.from(store.values()));
  list.sort((a,b) => (b.added_at||"").localeCompare(a.added_at||""));
  const totalCount = list.length;
  // 标签过滤（OR 语义：命中任一选中标签即显示）
  if (activeTagFilters.size > 0) {
    list = list.filter(r => (r.tags||[]).some(t => activeTagFilters.has(t)));
  }
  let h = '<div class="fav-bar">';
  h += '<span>共 <b>'+ list.length +'</b> 个收藏项目' + (activeTagFilters.size ? '（已按标签筛选）' : '') + '</span>';
  if (SYNC_AVAILABLE) {
    h += '<span class="stats">💾 点击 ⭐ 自动写入 <code>data/favorites.md</code>，serve.py 检测到后自动 rebuild 并刷新页面</span>';
  } else {
    h += '<button class="export-btn" id="export-fav-btn" type="button">⬇ 导出 favorites.md</button>';
    h += '<span class="stats">💾 收藏保存在本机浏览器（localStorage）。导出后覆盖仓库的 <code>data/favorites.md</code> 并 push，即可同步到线上</span>';
  }
  h += '</div>';
  // 标签过滤条（聚合所有收藏的标签 + 计数）
  const tagCount = {};
  Array.from(store.values()).forEach(f => (f.tags||[]).forEach(t => { tagCount[t] = (tagCount[t]||0) + 1; }));
  const tagNames = Object.keys(tagCount).sort();
  if (tagNames.length > 0) {
    h += '<div class="tag-filters">';
    h += '<span class="tag-filter-chip ' + (activeTagFilters.size === 0 ? "active" : "") + '" data-tag="__all__">全部 (' + totalCount + ')</span>';
    tagNames.forEach(t => {
      h += '<span class="tag-filter-chip ' + (activeTagFilters.has(t) ? "active" : "") + '" data-tag="' + esc(t) + '">#' + esc(t) + ' (' + tagCount[t] + ')</span>';
    });
    h += '</div>';
  }
  if (list.length === 0) {
    h += '<div class="empty-fav">'
       +   '<div class="icon">⭐</div>'
       +   '<div>' + (activeTagFilters.size ? '没有符合所选标签的收藏项目' : '还没有收藏项目') + '</div>'
       +   '<div class="tip">在「日报 / 周报 / 月报」tab 中，点击 <code>#排名</code> 旁边的 ☆ 即可收藏' +
           (SYNC_AVAILABLE ? '（自动同步到 <code>data/favorites.md</code>）' : '（保存在本机浏览器）') + '</div>'
       + '</div>';
  } else {
    h += '<div class="cards">';
    list.forEach(r => {
      let tagsHtml = '<div class="tags-row">';
      (r.tags||[]).forEach(t => {
        tagsHtml += '<span class="tag">🏷 ' + esc(t)
          + '<button class="tag-x" data-key="' + esc(r.key) + '" data-tag="' + esc(t) + '" title="删除标签">×</button></span>';
      });
      tagsHtml += '<div class="tag-input-wrap">'
        + '<input class="tag-input" data-key="' + esc(r.key) + '" placeholder="+ 标签 / 搜索" />'
        + '</div>';
      tagsHtml += '</div>';
      h += repoCard(r, {showFav: true, tagsHtml: tagsHtml});
    });
    h += '</div>';
  }
  el.innerHTML = h;
  window.scrollTo({top:0,behavior:"smooth"});
}

function exportFavMd(){
  // 已废弃：点击 ⭐ 现在自动 sync 到 data/favorites.md（通过 /api/write-favorites）
  // 保留此函数仅为兼容旧版本浏览器，无实际操作
  console.warn("[fav] exportFavMd 已废弃，请刷新页面（serve.py 会推送 SSE 通知 reload）");
}

function init(){
  seedFavStoreFromFavSeed();
  const vs = loadViewState();
  if (vs) {
    activeType = vs.type;
    if (activeType === FAV_TYPE) {
      activeDate = null;
    } else {
      const list = grouped[activeType] || [];
      const has = list.some(r => r.date === vs.date);
      activeDate = (vs.date && has) ? vs.date : (list.length ? list[0].date : null);
    }
  }
  renderTabs();
  if (activeType === FAV_TYPE) {
    renderSidebar();
    renderContent(null);
  } else {
    const list = grouped[activeType]||[];
    const cur = list.find(r => r.date === activeDate);
    if (cur){
      renderSidebar();
      renderContent(cur);
    } else if (list.length){
      activeDate = list[0].date;
      renderSidebar();
      renderContent(list[0]);
    }else{
      renderSidebar();
      renderContent(null);
    }
  }
  // 事件代理：拦截所有 .fav-btn / .tag-x / .tag-filter-chip / 导出按钮 点击
  document.addEventListener("click", (e) => {
    if (e.target.closest && e.target.closest("#export-fav-btn")) {
      e.preventDefault();
      downloadFavMd();
      return;
    }
    const btn = e.target.closest && e.target.closest(".fav-btn");
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      toggleFav(btn);
      return;
    }
    const tx = e.target.closest && e.target.closest(".tag-x");
    if (tx) {
      e.preventDefault();
      e.stopPropagation();
      removeTag(tx.getAttribute("data-key"), tx.getAttribute("data-tag"));
      return;
    }
    const fc = e.target.closest && e.target.closest(".tag-filter-chip");
    if (fc) {
      e.preventDefault();
      e.stopPropagation();
      toggleTagFilter(fc.getAttribute("data-tag"));
      return;
    }
    const sug = e.target.closest && e.target.closest(".tag-suggestion");
    if (sug) {
      e.preventDefault();
      e.stopPropagation();
      addTag(sug.getAttribute("data-key"), sug.getAttribute("data-tag"));
      return;
    }
    // 点击其它地方时收起所有标签下拉
    document.querySelectorAll(".tag-suggestions").forEach(dd => {
      if (!dd.hidden && !dd.contains(e.target) && !(e.target.closest && e.target.closest(".tag-input-wrap"))){
        dd.hidden = true;
      }
    });
  });
  // 标签输入框：回车 / 方向键 / Esc 处理（支持选择已有标签或新建）
  document.addEventListener("keydown", (e) => {
    if (e.target.classList && e.target.classList.contains("tag-input")) {
      const input = e.target;
      const wrap = input.parentElement;
      const dd = wrap.querySelector(".tag-suggestions");
      if (e.key === "ArrowDown" && dd && !dd.hidden){
        e.preventDefault();
        setActiveSuggestion(dd, (dd._activeIdx||0) + 1);
        return;
      }
      if (e.key === "ArrowUp" && dd && !dd.hidden){
        e.preventDefault();
        setActiveSuggestion(dd, (dd._activeIdx||0) - 1);
        return;
      }
      if (e.key === "Escape" && dd){
        dd.hidden = true;
        return;
      }
      if (e.key === "Enter"){
        e.preventDefault();
        let tagToAdd = null;
        if (dd && !dd.hidden){
          const list = tagSuggestionList(dd);
          const act = list[dd._activeIdx >= 0 ? dd._activeIdx : 0];
          if (act) tagToAdd = act.getAttribute("data-tag");
        }
        if (!tagToAdd) tagToAdd = input.value.trim();
        if (tagToAdd) addTag(input.getAttribute("data-key"), tagToAdd);
        return;
      }
    }
  });
  // 标签输入框：聚焦 / 输入时弹出已有标签下拉
  document.addEventListener("focusin", (e) => {
    if (e.target.classList && e.target.classList.contains("tag-input")) {
      renderTagSuggestions(e.target, e.target.getAttribute("data-key"));
    }
  });
  document.addEventListener("input", (e) => {
    if (e.target.classList && e.target.classList.contains("tag-input")) {
      renderTagSuggestions(e.target, e.target.getAttribute("data-key"));
    }
  });
  // 静态托管（GitHub Pages）：没有后端，直接进入本地模式
  if (!SYNC_AVAILABLE) {
    showSyncStatus("offline",
      "📄 静态模式（GitHub Pages）· 收藏保存在本机浏览器，可在 ⭐ 收藏 tab 导出 <code>favorites.md</code> 后手动同步到仓库");
    return;
  }
  // SSE：订阅 serve.py 的 rebuild 事件，server 完成 build_ui.py 后自动 reload
  try {
    const es = new EventSource("/api/rebuild-stream");
    es.addEventListener("ready", () => {
      showSyncStatus("online",
        "✅ 已连接 serve.py · 点击 ⭐ 自动写入 <code>data/favorites.md</code>，变更后自动 rebuild 并刷新");
    });
    es.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg && msg.event === "rebuilt") {
          showSyncStatus("rebuilt", "🔄 dist/index.html 已重建 · 即将刷新页面…");
          setTimeout(() => window.location.reload(), 250);
        }
      } catch(err) { /* ignore */ }
    };
    es.onerror = () => {
      showSyncStatus("offline",
        "⚠️ 未连接 serve.py — 数据仅写到 localStorage（清浏览器缓存会丢失）。请运行 <code>python serve.py</code> 启用自动同步");
    };
  } catch(e) {
    showSyncStatus("offline", "⚠️ 浏览器不支持 SSE，请用 Chrome / Edge / Firefox");
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
    favorites = load_favorites()
    html = TEMPLATE.replace("/*__DATA__*/", json.dumps(reports, ensure_ascii=False))
    html = html.replace("/*__FAVORITES__*/", json.dumps(favorites, ensure_ascii=False))
    out = os.path.join(DIST_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    from collections import Counter
    c = Counter(r.get("type") for r in reports)
    print(f"已生成 {out}（共 {len(reports)} 份报告，{len(favorites)} 条收藏）")
    print("各类型数量：", dict(c))


if __name__ == "__main__":
    main()
