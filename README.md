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
├── build_ui.py           # 生成自包含静态站点 dist/index.html
├── automate.py           # 无人值守流水线（抓取 → 生成简介 → 报告 → 站点）
├── serve.py              # 本地开发服务器（收藏同步 + SSE 自动刷新）
├── state.json            # 状态：简介缓存 + 三类快照
├── data/
│   ├── trending_raw.json # scraper 输出（仓库列表 + README 文本）
│   ├── favorites.md      # 收藏清单（会提交进仓库，用于线上展示）
│   └── intros_override.json  # LLM 写的新简介（临时，build 后清空）
├── reports/              # 生成的 Markdown + 结构化 JSON 报告
├── dist/                 # 静态站点产物（GitHub Pages 从这里发布）
└── .github/workflows/    # digest.yml（定时抓取）+ pages.yml（部署）
```

## 运行（手动）

```bash
# 一键跑完整流水线（抓取 → 生成简介 → 报告 → 站点）
python automate.py --type daily

# 或分步执行
python scraper.py                    # 1) 抓取（新仓库才拉 README，省 API 额度）
#    2) 为新仓库写简介 -> data/intros_override.json
#       形如 {"owner/repo": "一句话简介", ...}（云端由 automate.py 自动完成）
python build_report.py --type daily  # 3) 生成报告并更新快照
python build_ui.py                   # 4) 重建 dist/index.html
```

## 设计要点

- **简介缓存**：每个仓库的简介只生成一次，存于 `state.json` 的 `repo_intros`，后续直接复用，避免重复探索。
- **新增判定**：`last_daily / last_weekly / last_monthly` 存上一期仓库清单；当前清单与之求差得到 🆕 与退榜。首次运行无对比，不标 🆕。
- **抓取兜底**：GitHub API 拉 README 失败（限流/404）时降级为使用仓库描述，报告仍可用。
- **简介生成分层降级**：配了 `LLM_PROVIDER` + `LLM_API_KEY` 则调大模型生成中文简介；调用失败 / 未配置 / 单条漏返回，都自动回落到仓库原始 description，保证 CI 里永远能出报告。
- **空数据保护**：抓取结果为空时直接终止，不覆盖已有报告与快照。
- **依赖**：`requests` + `beautifulsoup4`（`build_ui.py` 只用标准库）。

## 自动化（GitHub Actions + GitHub Pages）

整套流程已搬到 GitHub Actions，无需本地机器常开：

| Workflow | 触发 | 作用 |
| --- | --- | --- |
| `.github/workflows/digest.yml` | 每天 01:00 UTC（09:00 GMT+8）<br>每周五 01:20 UTC<br>每月 1 号 01:40 UTC<br>手动 `workflow_dispatch` | 跑 `automate.py` 抓取 + 生成简介 + 出报告 + 重建站点，然后 commit & push |
| `.github/workflows/pages.yml` | `reports/`、`build_ui.py`、`dist/` 变更时 / 手动 | `python build_ui.py` → 上传 `dist/` → 部署到 GitHub Pages |

`digest.yml` 通过 `github.event.schedule`（cron 字符串）区分日报 / 周报 / 月报，避免用 matrix 在 schedule 触发时跑到空值。

### 首次启用

1. **开启 Pages**：仓库 `Settings → Pages → Build and deployment → Source` 选 **GitHub Actions**。
2. **配置简介生成（可选）**：`Settings → Secrets and variables → Actions`
   - Variables：`LLM_PROVIDER` = `deepseek` / `openai` / `gemini`（不配或填 `off` 则降级用仓库原始描述）
   - Variables：`LLM_MODEL`（可选，留空用默认：deepseek=`deepseek-chat`、openai=`gpt-4o-mini`、gemini=`gemini-2.0-flash`）
   - Secrets：`LLM_API_KEY` = 对应平台的 API Key
3. **允许 Action 写回**：`Settings → Actions → General → Workflow permissions` 选择 **Read and write permissions**。
4. 手动跑一次 `digest.yml` 验证。

站点地址：`https://<用户名>.github.io/github-trending-digest/`

### 本地等价运行

```bash
python automate.py --type daily          # 完整流水线
python automate.py --type weekly --no-scrape   # 复用已有 trending_raw.json，只重出报告
LLM_PROVIDER=mock python automate.py --type daily   # mock 简介，联调用
```

### 收藏功能的两种模式

`build_ui.py` 生成的页面会自动识别运行环境（`location.hostname`）：

- **本地 `serve.py`**：点 ⭐ 会 POST 到 `/api/write-favorites` 写入 `data/favorites.md`，并通过 SSE 自动 rebuild + 刷新页面。
- **线上 GitHub Pages**（纯静态，无后端）：收藏保存在浏览器 `localStorage`，页面提供「⬇ 导出 favorites.md」按钮；把导出的文件覆盖仓库 `data/favorites.md` 并 push，`pages.yml` 会重新构建，收藏即持久化到线上（同时作为 seed 回填到其他设备的 localStorage）。

`data/favorites.md` 位于仓库内，是线上收藏的唯一数据源。
