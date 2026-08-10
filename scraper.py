# coding: utf-8
"""
scraper.py — 抓取 GitHub Trending（每日/每周/每月全量 repo）

输出 data/trending_raw.json:
{
  "fetched_at": "2026-08-09T19:30:00+08:00",
  "source": "https://github.com/trending",
  "repos": [
    {
      "rank": 1,
      "key": "owner/repo",
      "owner": "owner",
      "repo": "repo",
      "url": "https://github.com/owner/repo",
      "language": "TypeScript",
      "stars_total": 12456,
      "stars_today": 2483,
      "description": "原始 GitHub 描述",
      "readme_text": "README 前 N 字符（仅对新 repo 抓取）",
      "cached": true/false   # 是否已有 intro 缓存
    },
    ...
  ]
}

用法:
  python scraper.py                 # 默认抓取，新 repo 才拉 README
  python scraper.py --force-readme  # 全部重新拉 README（忽略缓存）
  python scraper.py --no-readme     # 不拉 README（仅列表，调试用）
  python scraper.py --out data/xxx.json
"""
import argparse
import base64
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
DEFAULT_OUT = os.path.join(DATA_DIR, "trending_raw.json")

TRENDING_URL = "https://github.com/trending"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}

README_MAX_CHARS = 4000


def log(msg):
    print(f"[scraper] {msg}", flush=True)


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"repo_intros": {}}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"state 读取失败，按空处理: {e}")
        return {"repo_intros": {}}


def fetch_trending(since="daily"):
    url = f"https://github.com/trending?since={since}"
    log(f"GET {url}")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_repo(article, rank):
    h2_a = article.select_one("h2.h3.lh-condensed a") or article.select_one("h2 a")
    if not h2_a:
        return None
    href = h2_a.get("href", "").strip()
    if not href.startswith("/"):
        href = "/" + href
    parts = [p for p in href.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    key = f"{owner}/{repo}"

    desc_el = article.find("p", class_=lambda c: c and "col-9" in c)
    description = desc_el.get_text(strip=True) if desc_el else ""

    lang_el = article.select_one('span[itemprop="programmingLanguage"]')
    language = lang_el.get_text(strip=True) if lang_el else ""

    stars_a = article.select_one('a[href$="/stargazers"]')
    stars_total = 0
    if stars_a:
        m = re.search(r"[\d,]+", stars_a.get_text())
        if m:
            stars_total = int(m.group(0).replace(",", ""))

    forks_a = article.select_one('a[href$="/forks"]')
    forks = 0
    if forks_a:
        m = re.search(r"[\d,]+", forks_a.get_text())
        if m:
            forks = int(m.group(0).replace(",", ""))

    period_m = re.search(r"([\d,]+)\s+stars (today|this week|this month)",
                          article.get_text())
    stars_period = int(period_m.group(1).replace(",", "")) if period_m else 0

    return {
        "rank": rank,
        "key": key,
        "owner": owner,
        "repo": repo,
        "url": "https://github.com" + href,
        "language": language,
        "stars_total": stars_total,
        "forks": forks,
        "stars_period": stars_period,
        "description": description,
    }


def fetch_readme(owner, repo):
    """通过 GitHub API 拉取 README 原文（base64）。失败返回空串。"""
    api = f"https://api.github.com/repos/{owner}/{repo}/readme"
    try:
        r = requests.get(api, headers={**HEADERS,
                                       "Accept": "application/vnd.github+json"},
                         timeout=20)
        if r.status_code != 200:
            return ""
        data = r.json()
        content = data.get("content", "")
        encoding = data.get("encoding", "base64")
        if encoding == "base64":
            try:
                text = base64.b64decode(content).decode("utf-8", errors="ignore")
            except Exception:
                text = ""
        else:
            text = content
        return text[:README_MAX_CHARS]
    except Exception as e:
        log(f"README 拉取失败 {owner}/{repo}: {e}")
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--since", default="daily",
                    choices=["daily", "weekly", "monthly"],
                    help="抓取时间维度：daily(当日)/weekly(本周)/monthly(本月)")
    ap.add_argument("--force-readme", action="store_true",
                    help="忽略缓存，全部重新拉 README")
    ap.add_argument("--no-readme", action="store_true",
                    help="完全不拉 README（调试用）")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    state = load_state()
    intros_cache = state.get("repo_intros", {}) or {}

    html = fetch_trending(args.since)
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select("article.Box-row")
    log(f"解析到 {len(articles)} 个 repo 行")

    repos = []
    for i, art in enumerate(articles, start=1):
        repo = parse_repo(art, i)
        if not repo:
            continue
        cached = repo["key"] in intros_cache
        repo["cached"] = cached
        repos.append(repo)

    if not args.no_readme:
        for repo in repos:
            if args.force_readme or not repo["cached"]:
                log(f"拉 README: {repo['key']}")
                repo["readme_text"] = fetch_readme(repo["owner"], repo["repo"])
            else:
                repo["readme_text"] = ""
    else:
        for repo in repos:
            repo["readme_text"] = ""

    out = {
        "fetched_at": datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=8))
        ).isoformat(),
        "source": f"https://github.com/trending?since={args.since}",
        "since": args.since,
        "repos": repos,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    log(f"写出 {len(repos)} 个 repo -> {args.out}")
    new_count = sum(1 for r in repos if not r["cached"])
    log(f"其中 {new_count} 个为新 repo（需生成简介）")


if __name__ == "__main__":
    main()
