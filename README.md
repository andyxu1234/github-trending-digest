# GitHub Trending Digest

自动抓取 [GitHub Trending](https://github.com/trending) 全量上榜仓库，为**每个仓库**生成一句「它到底做了什么」的探索简介，并产出 Markdown 报告。

- **日报**：每天 09:00（GMT+8）
- **周报**：每周五 09:00
- **月报**：每月 1 号 09:00

报告中会标注 🆕（对比上一期同类型报告的新增仓库）与退榜仓库。

## 目录结构

```
github-trending-digest/
├── scraper.py            # 抓取 trending 列表 + 新仓库 README
├── build_report.py       # 合并简介、算新增/退榜、渲染 Markdown、更新快照
├── state.json            # 状态：简介缓存 + 三类快照
├── data/
│   ├── trending_raw.json # scraper 输出（仓库列表 + README 文本）
│   └── intros_override.json  # LLM 写的新简介（临时）
├── reports/              # 生成的 Markdown 报告
└── .venv/                # Python 虚拟环境
```

## 运行（手动）

```bash
# 1) 抓取（新仓库才拉 README，省 API 额度）
.venv/Scripts/python.exe scraper.py

# 2) 为新仓库写简介 -> data/intros_override.json
#    形如 {"owner/repo": "一句话简介", ...}（由 LLM 完成）

# 3) 生成报告并更新快照
.venv/Scripts/python.exe build_report.py --type daily
```

## 设计要点

- **简介缓存**：每个仓库的简介只生成一次，存于 `state.json` 的 `repo_intros`，后续直接复用，避免重复探索。
- **新增判定**：`last_daily / last_weekly / last_monthly` 存上一期仓库清单；当前清单与之求差得到 🆕 与退榜。首次运行无对比，不标 🆕。
- **抓取兜底**：GitHub API 拉 README 失败（限流/404）时降级为使用仓库描述，报告仍可用。
- **依赖**：`requests` + `beautifulsoup4`（已装入 `.venv`）。

## 自动化

三个定时任务由 WorkBuddy 自动化编排，prompt 会依次执行：跑 `scraper.py` → 读 `data/trending_raw.json` 与 `state.json` → 为未缓存仓库写探索简介并写入 `data/intros_override.json` → 跑 `build_report.py` → 失败兜底。
