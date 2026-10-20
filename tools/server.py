#!/usr/bin/env python3
"""
Dev server for the flatpack authoring tool and viewer.

Serves the project root and accepts writes to products/*/build.json so the
authoring tool can save without a build step.

    python3 tools/server.py            # http://0.0.0.0:8000
"""
from __future__ import annotations

import json
import os
import posixpath
import re
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PORT = int(os.environ.get("PORT", "8000"))
SAFE_SAVE = re.compile(r"^products/[A-Za-z0-9._-]+/build\.json$")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "/api/" in (self.path or ""):
            sys.stderr.write("  %s - %s\n" % (self.address_string(), fmt % args))

    # ------------------------------------------------------------------ API
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/catalogue":
            items = []
            pdir = os.path.join(ROOT, "products")
            for slug in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
                f = os.path.join(pdir, slug, "build.json")
                if not os.path.exists(f):
                    continue
                try:
                    d = json.load(open(f, encoding="utf-8"))
                except Exception:
                    continue
                p = d.get("product", {})
                items.append({
                    "id": slug,
                    "name": p.get("name") or slug,
                    "typeName": p.get("typeName"),
                    "dims": (p.get("dims") or {}).get("text"),
                    "status": d.get("status"),
                    "steps": len(d.get("steps") or []),
                    "buildPages": len(d.get("manual", {}).get("buildPages") or []),
                    "parts": len(d.get("parts") or []),
                    "hardware": len(d.get("hardware") or []),
                })
            return self._json({"products": items, "root": ROOT})

        if path == "/api/pages":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            slug = (q.get("id") or [""])[0]
            pj = os.path.join(ROOT, "products", slug, "pages.json")
            if not os.path.exists(pj):
                return self._json({"error": "no pages.json"}, 404)
            return self._json(json.load(open(pj, encoding="utf-8")))

        return super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/save":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception as e:
                return self._json({"error": f"bad json: {e}"}, 400)
            rel = (body.get("path") or "").lstrip("/")
            if not SAFE_SAVE.match(rel):
                return self._json({"error": f"refusing to write {rel!r}"}, 403)
            dest = os.path.join(ROOT, rel)
            if not os.path.exists(os.path.dirname(dest)):
                return self._json({"error": "no such product"}, 404)
            data = body.get("data")
            if not isinstance(data, dict):
                return self._json({"error": "data must be an object"}, 400)
            tmp = dest + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, dest)
            return self._json({"ok": True, "path": rel, "bytes": os.path.getsize(dest)})

        return self._json({"error": "not found"}, 404)


def find_server(host: str, default_port: int) -> tuple[ThreadingHTTPServer, int]:
    env_port = os.environ.get("PORT")
    if env_port:
        port = int(env_port)
        return ThreadingHTTPServer((host, port), Handler), port
    # Try default port, then scan for an open port if busy
    for port in [default_port, 8001, 8002, 8003, 8080, 8088, 8888]:
        try:
            return ThreadingHTTPServer((host, port), Handler), port
        except OSError as e:
            if e.errno == 48:  # Address already in use
                continue
            raise
    # Fallback to ephemeral port
    srv = ThreadingHTTPServer((host, 0), Handler)
    return srv, srv.server_address[1]


def main() -> int:
    srv, port = find_server("0.0.0.0", PORT)
    print(f"flatpack tools  ->  http://0.0.0.0:{port}")
    print(f"  authoring tool  /tools/")
    print(f"  viewer          /viewer/")
    print(f"  serving         {ROOT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
