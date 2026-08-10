# coding: utf-8
"""
build_report.py — 根据抓取结果与简介缓存生成 Markdown 报告，并更新状态快照。

流水线（由自动化编排）:
  1. scraper.py           -> data/trending_raw.json
  2. LLM 为新 repo 写简介 -> data/intros_override.json  {"owner/repo": "简介"}
  3. build_report.py      -> reports/<type>_<date>.md  + 更新 state.json

用法:
  python build_report.py --type daily
  python build_report.py --type weekly
  python build_report.py --type monthly
"""
import argparse
import datetime
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
RAW_PATH = os.path.join(DATA_DIR, "trending_raw.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
OVERRIDE_PATH = os.path.join(DATA_DIR, "intros_override.json")

TYPE_LABEL = {"daily": "日报", "weekly": "周报", "monthly": "月报"}
PERIOD_LABEL = {"daily": "今日", "weekly": "本周", "monthly": "本月"}


def log(msg):
    print(f"[build_report] {msg}", flush=True)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"读取失败 {path}: {e}")
        return default if default is not None else {}


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def fmt_stars(n):
    if n >= 1000:
        return f"{n/1000:.1f}k".rstrip("0").rstrip(".")
    return str(n)


def previous_date_label(snapshot_keys, today):
    """给新增对比一个人类可读的上一期日期提示（best-effort）。"""
    return "上一期"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=["daily", "weekly", "monthly"])
    ap.add_argument("--raw", default=RAW_PATH)
    ap.add_argument("--out-dir", default=REPORTS_DIR)
    ap.add_argument("--override", default=OVERRIDE_PATH)
    args = ap.parse_args()

    os.makedirs(REPORTS_DIR, exist_ok=True)

    raw = load_json(args.raw, {})
    repos = raw.get("repos", [])
    fetched_at = raw.get("fetched_at", "")
    state = load_json(STATE_PATH, {"repo_intros": {}})
    if "repo_intros" not in state:
        state["repo_intros"] = {}

    # 合并简介：override（LLM 新写）覆盖缓存
    override = load_json(args.override, {})
    if override:
        state["repo_intros"].update(override)
        log(f"合并 {len(override)} 条新简介到缓存")

    # 计算新增 / 退榜
    snap_key = f"last_{args.type}"
    prev_keys = state.get(snap_key, []) or []
    prev_set = set(prev_keys)
    cur_keys = [r["key"] for r in repos]
    cur_set = set(cur_keys)

    is_first = len(prev_keys) == 0
    new_keys = [k for k in cur_keys if k not in prev_set]
    removed = [k for k in prev_keys if k not in cur_set]

    # 渲染
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    date_str = today.strftime("%Y-%m-%d")
    label = TYPE_LABEL[args.type]
    fname = f"github_trending_{label}_{date_str}.md"
    out_path = os.path.join(args.out_dir, fname)

    lines = []
    lines.append(f"# GitHub Trending {label} · {date_str}")
    lines.append("")
    lines.append(f"> 数据来源 [github.com/trending](https://github.com/trending)"
                 f" ｜ 抓取时间 {fetched_at} ｜ 共 {len(repos)} 个上榜项目")
    lines.append("")
    lines.append("## 概览")
    if is_first:
        lines.append(f"- 本期上榜：**{len(repos)}** 个")
        lines.append(f"- 说明：首次记录，暂无可对比的上一期，故不标注 🆕")
    else:
        lines.append(f"- 本期上榜：**{len(repos)}** 个")
        new_flag = " 🆕" if new_keys else ""
        lines.append(f"- 本期新增：🆕 **{len(new_keys)}** 个"
                     + ("（对比上一期同类型报告）" if new_keys else ""))
        lines.append(f"- 本期退榜：**{len(removed)}** 个")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 项目列表")
    lines.append("")

    repo_rows = []
    for r in repos:
        key = r["key"]
        is_new = (not is_first) and (key in new_keys)
        new_badge = " 🆕" if is_new else ""
        lang = r.get("language") or "—"
        stars = fmt_stars(r.get("stars_total", 0))
        stars_period = r.get("stars_period", r.get("stars_today", 0))
        star_line = f"⭐ {stars}"
        if stars_period:
            star_line += f"（{PERIOD_LABEL.get(args.type, '本期')} +{stars_period:,}）"
        intro = state["repo_intros"].get(key) or r.get("description") or "（暂无简介）"
        lines.append(f"### {r['rank']}. "
                     f"[{r['repo']}]({r['url']}) · {lang}{new_badge}")
        lines.append(star_line)
        lines.append(f"**简介**：{intro}")
        lines.append("")
        repo_rows.append({
            "rank": r["rank"],
            "key": key,
            "owner": r.get("owner"),
            "repo": r.get("repo"),
            "url": r.get("url"),
            "language": lang,
            "stars_total": r.get("stars_total", 0),
            "forks": r.get("forks", 0),
            "stars_period": stars_period,
            "description": r.get("description") or "",
            "intro": intro,
            "is_new": is_new,
        })

    if removed:
        lines.append("---")
        lines.append("")
        lines.append("## 退榜项目")
        lines.append("")
        for k in removed:
            lines.append(f"- {k}")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"报告写出 -> {out_path}")

    # 结构化 JSON（字段齐全，供 UI 渲染）
    json_path = os.path.join(args.out_dir,
                             f"github_trending_{label}_{date_str}.json")
    report_json = {
        "type": label,
        "type_en": args.type,
        "date": date_str,
        "source": raw.get("source", ""),
        "fetched_at": fetched_at,
        "generated_at": today.isoformat(),
        "count": len(repos),
        "is_first": is_first,
        "new_count": len(new_keys),
        "removed_count": len(removed),
        "new_keys": new_keys,
        "removed": removed,
        "repos": repo_rows,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, ensure_ascii=False, indent=2)
    log(f"结构化报告写出 -> {json_path}")

    # 更新快照
    state[snap_key] = cur_keys
    save_state(state)
    log(f"更新快照 {snap_key}（{len(cur_keys)} 项）")

    # 清空 override，避免下次误用（沙箱下删除可能被拦截，故写空而非删）
    try:
        with open(args.override, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    except Exception:
        pass

    print(out_path)


if __name__ == "__main__":
    main()
