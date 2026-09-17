# coding: utf-8
"""
automate.py — 无人值守流水线（供 GitHub Actions 定时调用）

职责边界：
  1. 跑 scraper.py 抓取 trending（daily/weekly/monthly）
  2. 为「无缓存简介」的新 repo 生成简介并写入 data/intros_override.json
  3. 跑 build_report.py 生成 Markdown + 结构化 JSON 并更新快照
  4. 跑 build_ui.py 重建 dist/index.html

简介生成策略（分层降级，保证 CI 里永远能出结果）：
  A) LLM_PROVIDER 已配置且 API key 存在 -> 调大模型逐批生成中文探索简介
  B) 调用失败 / 未配置        -> 用 GitHub 原始 description 兜底

用法:
  python automate.py --type daily
  python automate.py --type weekly --skip-ui
  python automate.py --type daily --no-scrape      # 复用已有 data/trending_raw.json

环境变量:
  LLM_PROVIDER   openai | deepseek | gemini | mock | off     (默认 off)
  LLM_API_KEY    对应平台的 API Key（mock 不需要）
  LLM_MODEL      覆盖默认模型名
  LLM_BASE_URL   覆盖默认 base_url
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PATH = os.path.join(DATA_DIR, "trending_raw.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
OVERRIDE_PATH = os.path.join(DATA_DIR, "intros_override.json")

INTRO_MAX_CHARS = 120  # 单条简介字符上限（超出截断）
BATCH_SIZE = 12        # 每次 LLM 请求包含的仓库数
DEFAULT_TIMEOUT = 120  # 单次 LLM 请求超时（秒）
RETRIES = 3

# 各 provider 默认配置：base_url / model / 是否 OpenAI 兼容
PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "compat": True,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "compat": True,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "model": "gemini-2.0-flash",
        "compat": False,
    },
}

SYSTEM_PROMPT = (
    "你是一名资深开源项目分析师。用户会给出若干 GitHub 仓库的信息"
    "（仓库名、语言、原始描述，可能附带 README 片段）。\n"
    "请为每个仓库写一句**中文**探索简介，要求：\n"
    "1) 说清「它到底是什么、解决什么问题、给谁用」，不要复述仓库名；\n"
    "2) 长度 {} 字以内，一到两句话，口语化、具体，避免营销套话；\n"
    "3) 只输出 JSON，格式为 {{\"owner/repo\": \"简介\"}}，不要输出任何其他文字、注释或代码块标记。\n"
    "必须覆盖用户给出的每一个仓库。".format(INTRO_MAX_CHARS)
)


def log(msg):
    print(f"[automate] {msg}", flush=True)


def run_step(name, cmd):
    """顺序执行子步骤，失败即抛出，避免产出半成品。"""
    log(f"--- {name} ---")
    started = time.time()
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True,
                            encoding="utf-8", errors="replace")
    cost = time.time() - started
    if result.returncode != 0:
        raise RuntimeError(f"{name} 失败（exit {result.returncode}）")
    log(f"{name} 完成，耗时 {cost:.1f}s")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"读取失败 {path}: {e}")
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def clamp_intro(text, fallback):
    """清洗 LLM 输出：去掉换行/列表符号，超长截断。"""
    text = (text or "").strip()
    text = re.sub(r"^[\-\*\d\.\s]+", "", text)
    text = re.sub(r"\s*\n+\s*", " ", text)
    text = re.sub(r"^#+\s*", "", text)
    if not text:
        return fallback
    if len(text) > INTRO_MAX_CHARS:
        text = text[:INTRO_MAX_CHARS].rstrip() + "…"
    return text


# --------------------------------------------------------------------------
# LLM 调用
# --------------------------------------------------------------------------
def build_payload(provider, model, repos):
    """把一批 repo 描述成一个用户 prompt。"""
    parts = []
    for r in repos:
        seg = [
            f"仓库: {r['key']}",
            f"语言: {r.get('language') or '未知'}",
            f"原始描述: {(r.get('description') or '（无描述）').strip()}",
        ]
        readme = (r.get("readme_text") or "").strip()
        if readme:
            seg.append("README 片段:\n" + readme[:1200])
        parts.append("\n".join(seg))
    user_prompt = "\n\n===\n\n".join(parts)

    if provider == "gemini":
        return {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.4,
                                 "responseMimeType": "application/json"},
        }
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
    }


def extract_content(provider, body):
    if provider == "gemini":
        cands = body.get("candidates") or []
        if not cands:
            raise ValueError(f"Gemini 无 candidates: {str(body)[:300]}")
        parts = (cands[0].get("content") or {}).get("parts") or []
        return "".join(p.get("text", "") for p in parts)
    choices = body.get("choices") or []
    if not choices:
        raise ValueError(f"无 choices: {str(body)[:300]}")
    return (choices[0].get("message") or {}).get("content", "")


def parse_json_object(text):
    """容错解析：LLM 偶尔会包一层 ```json 代码块或加前后缀。"""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass
    raise ValueError("无法解析为 JSON: " + text[:200])


def call_llm(provider, repo_batch):
    """调用 LLM 生成一批简介；失败返回空 dict（由上层降级兜底）。"""
    import requests

    cfg = PROVIDERS[provider]
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    model = os.environ.get("LLM_MODEL", "").strip() or cfg["model"]
    base_url = os.environ.get("LLM_BASE_URL", "").strip() or cfg["base_url"]
    payload = build_payload(provider, model, repo_batch)

    if provider == "gemini":
        url = f"{base_url}/models/{model}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    else:
        url = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {api_key}"}

    for attempt in range(1, RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload,
                                 timeout=DEFAULT_TIMEOUT)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            content = extract_content(provider, resp.json())
            data = parse_json_object(content)
            if not isinstance(data, dict):
                raise ValueError("返回不是 JSON 对象")
            return {str(k).strip(): v for k, v in data.items()}
        except Exception as e:
            log(f"LLM 第 {attempt}/{RETRIES} 次失败: {e}")
            if attempt < RETRIES:
                time.sleep(2 * attempt)
    return {}


def mock_intro(repo):
    desc = (repo.get("description") or "").strip()
    return f"（占位简介）{desc}" if desc else "（占位简介）暂无描述"


def gen_intros_with_llm(provider, pending):
    """分批生成，返回 {key: intro}。未覆盖到的 key 不在结果里。"""
    out = {}
    total = len(pending)
    for i in range(0, total, BATCH_SIZE):
        batch = pending[i:i + BATCH_SIZE]
        log(f"LLM 生成简介 {i + 1}-{i + len(batch)}/{total} "
            f"（provider={provider}）")
        got = call_llm(provider, batch)
        hit = 0
        for r in batch:
            intro = got.get(r["key"])
            if isinstance(intro, str) and intro.strip():
                out[r["key"]] = clamp_intro(intro, "")
                hit += 1
        log(f"本批命中 {hit}/{len(batch)}")
    return out


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="CI 无人值守流水线")
    ap.add_argument("--type", required=True,
                    choices=["daily", "weekly", "monthly"])
    ap.add_argument("--no-scrape", action="store_true",
                    help="跳过抓取，直接复用已有 data/trending_raw.json")
    ap.add_argument("--skip-ui", action="store_true",
                    help="跳过 build_ui.py（只更新报告）")
    ap.add_argument("--force-intro", action="store_true",
                    help="忽略缓存，重新为所有 repo 生成简介")
    args = ap.parse_args()

    py = sys.executable
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1) 抓取
    if args.no_scrape:
        log("跳过抓取（--no-scrape）")
        if not os.path.exists(RAW_PATH):
            raise SystemExit(f"--no-scrape 但找不到 {RAW_PATH}")
    else:
        run_step("抓取 trending", [py, "scraper.py", "--since", args.type,
                                   "--out", RAW_PATH])

    raw = load_json(RAW_PATH, {})
    repos = raw.get("repos", [])
    if not repos:
        raise SystemExit("抓取结果为空，终止（不覆盖已有报告与快照）")
    log(f"本期 {len(repos)} 个 repo（since={raw.get('since')}）")

    state = load_json(STATE_PATH, {"repo_intros": {}})
    intros_cache = state.get("repo_intros", {}) or {}

    # 2) 找出缺简介的 repo（含 override 里已写好的）
    override = load_json(OVERRIDE_PATH, {})
    if not isinstance(override, dict):
        override = {}
    pending = [r for r in repos
               if args.force_intro or not intros_cache.get(r["key"])]
    log(f"待生成简介：{len(pending)} 个（缓存已有 {len(intros_cache)} 条）")

    provider = (os.environ.get("LLM_PROVIDER", "off") or "off").strip().lower()
    generated = {}

    if pending:
        if provider == "mock":
            log("provider=mock，生成占位简介（仅用于本地联调）")
            generated = {r["key"]: mock_intro(r) for r in pending}
        elif provider in PROVIDERS:
            if not os.environ.get("LLM_API_KEY", "").strip():
                log(f"provider={provider} 但未配置 LLM_API_KEY，降级为描述兜底")
                provider = "off"
            else:
                generated = gen_intros_with_llm(provider, pending)
                miss = [r for r in pending if r["key"] not in generated]
                if miss:
                    log(f"仍有 {len(miss)} 个 repo 未拿到 LLM 简介，逐条重试")
                    for r in miss:
                        one = call_llm_retry_single(provider, r)
                        if one:
                            generated.update(one)
        elif provider != "off":
            log(f"未知 provider={provider}，按未配置处理")

        # 兜底：剩余未生成的用原始 description
        fallback_n = 0
        for r in pending:
            if r["key"] not in generated:
                desc = (r.get("description") or "").strip()
                generated[r["key"]] = clamp_intro(
                    desc, "（暂无简介，可参考仓库 README）")
                fallback_n += 1
        if fallback_n:
            log(f"{fallback_n} 个 repo 使用原始描述兜底")

    # 写入 override（build_report.py 会把它合并进缓存）
    override.update(generated)
    save_json(OVERRIDE_PATH, override)
    log(f"写入 {len(override)} 条简介 -> {OVERRIDE_PATH}")

    # 3) 报告
    run_step("生成报告", [py, "build_report.py", "--type", args.type])

    # 4) 静态站点
    if args.skip_ui:
        log("跳过 build_ui（--skip-ui）")
    else:
        run_step("重建静态站点", [py, "build_ui.py"])

    log(f"全部完成（provider={provider}，新生成 {len(generated)} 条简介）")


def call_llm_retry_single(provider, repo):
    """单条重试：某些 repo 在批量返回里被漏掉时逐个补。"""
    got = call_llm(provider, [repo])
    intro = got.get(repo["key"])
    if isinstance(intro, str) and intro.strip():
        return {repo["key"]: clamp_intro(intro, "")}
    return {}


if __name__ == "__main__":
    main()
