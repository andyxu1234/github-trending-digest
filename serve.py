#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
github-trending-digest 静态站点服务 + 收藏自动同步
========================================================
- 静态服务 dist/ （端口 8765）
- POST /api/write-favorites  : 写入 data/favorites.md
- 后台线程：轮询 mtime，变化时跑 python build_ui.py；完成后通过 SSE 通知所有连接
- GET  /api/rebuild-stream   : Server-Sent Events，前端订阅后自动 reload

不需要任何第三方依赖（标准库实现）。
启动：python serve.py [--port 8765]
"""
import os
import sys
import json
import time
import shutil
import threading
import subprocess
import http.server
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
DATA_DIR = ROOT / "data"
FAV_PATH = DATA_DIR / "favorites.md"
INDEX_HTML = DIST_DIR / "index.html"
PORT = 8765

# ---- rebuild 事件总线（用于 SSE 推送） ----
class RebuildBus:
    def __init__(self):
        self.clients = []  # list of queue.Queue
        self.lock = threading.Lock()

    def subscribe(self):
        import queue
        q = queue.Queue()
        with self.lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            if q in self.clients:
                self.clients.remove(q)

    def publish(self, event):
        with self.lock:
            for q in list(self.clients):
                try:
                    q.put_nowait(event)
                except Exception:
                    pass


BUS = RebuildBus()
LAST_REBUILD_AT = [0.0]  # 共享状态


def rebuild_index():
    """运行 build_ui.py 更新 dist/index.html"""
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_ui.py")],
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT),
        )
        ok = (result.returncode == 0)
        msg = (result.stdout or "").strip() or (result.stderr or "").strip()
        return ok, msg
    except Exception as e:
        return False, f"rebuild error: {e}"


def watcher_thread():
    """后台线程：polling data/favorites.md mtime；变化时 rebuild + 广播事件"""
    print(f"[watcher] polling {FAV_PATH} (every 300ms)")
    last_mtime = None
    while True:
        try:
            if FAV_PATH.exists():
                cur = FAV_PATH.stat().st_mtime
                if last_mtime is None:
                    last_mtime = cur
                elif cur != last_mtime:
                    last_mtime = cur
                    print(f"[watcher] detected favorites.md change -> rebuild")
                    ok, msg = rebuild_index()
                    print(f"[watcher] rebuild {'OK' if ok else 'FAIL'}: {msg[:200]}")
                    if ok:
                        LAST_REBUILD_AT[0] = time.time()
                        BUS.publish({"event": "rebuilt", "at": LAST_REBUILD_AT[0]})
        except Exception as e:
            print(f"[watcher] error: {e}")
        time.sleep(0.3)


# ---- HTTP handler ----
class Handler(http.server.SimpleHTTPRequestHandler):
    """扩展 SimpleHTTPRequestHandler：基于 DIST_DIR 的静态服务 + API 路由"""

    def end_headers(self):
        # 禁缓存（开发期方便）
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # SimpleHTTPRequestHandler.log_message 在 404/500 时传 (format_string, HTTPStatus)
        # 我们的 /api/ 路径都 self.send_error，不在这里走，所以直接 super
        super().log_message(fmt, *args)

    def do_POST(self):
        if self.path == "/api/write-favorites":
            self.handle_write_favorites()
        else:
            self.send_error(404)

    def do_GET(self):
        # SSE 路由
        if self.path.split("?")[0] == "/api/rebuild-stream":
            self.handle_sse()
            return
        # 静态服务 DIST_DIR（不调 super，避免 cwd 解析问题）
        import mimetypes
        rel = self.path.lstrip("/").split("?")[0] or "index.html"
        target = (DIST_DIR / rel).resolve()
        dist_root = DIST_DIR.resolve()
        # 防越界
        try:
            target.relative_to(dist_root)
        except ValueError:
            self.send_error(403)
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.exists() or not target.is_file():
            self.send_error(404)
            return
        try:
            with open(target, "rb") as f:
                data = f.read()
            ctype, _ = mimetypes.guess_type(str(target))
            if ctype is None:
                ctype = "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    # ----- API handlers -----
    def handle_write_favorites(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw)
            content = data.get("content", "")
            if not isinstance(content, str):
                raise ValueError("content must be string")
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return
        # atomic write：先 .tmp 再 rename，防止读到半截
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = FAV_PATH.with_suffix(".md.tmp")
        try:
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            shutil.move(str(tmp), str(FAV_PATH))
        except Exception as e:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def handle_sse(self):
        """SSE：浏览器订阅 rebuild 事件"""
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            # 发送初始 ready 事件，前端确认通道建立
            self.wfile.write(b"event: ready\ndata: {}\n\n")
            self.wfile.flush()
            queue = BUS.subscribe()
            # 30s 心跳（保活）
            last_heartbeat = time.time()
            while True:
                try:
                    msg = queue.get(timeout=15)
                    payload = json.dumps(msg, ensure_ascii=False)
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    # 心跳
                    if time.time() - last_heartbeat >= 15:
                        try:
                            self.wfile.write(b": heartbeat\n\n")
                            self.wfile.flush()
                        except Exception:
                            break
                        last_heartbeat = time.time()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            print(f"[sse] error: {e}")
        finally:
            try:
                BUS.unsubscribe(queue)
            except Exception:
                pass


def main():
    parser_args = sys.argv[1:]
    port = PORT
    for i, a in enumerate(parser_args):
        if a == "--port" and i + 1 < len(parser_args):
            port = int(parser_args[i + 1])
    # 启动 watcher 后台线程
    t = threading.Thread(target=watcher_thread, daemon=True)
    t.start()
    # 启动 HTTP server
    print(f"[serve] static: {DIST_DIR}")
    print(f"[serve] listening on http://localhost:{port}")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[serve] shutting down")


if __name__ == "__main__":
    main()
