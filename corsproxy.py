#!/usr/bin/env python3
"""Tiny CORS proxy for the ExpressVPN control API.

The control server (files/control-server.sh) returns no CORS headers and does
not handle OPTIONS preflight, so a browser page cannot read its responses
cross-origin. This proxy forwards GET/POST/OPTIONS to the upstream and injects
the permissive CORS headers the browser needs.

Defaults match control-panel.html: upstream http://localhost:8000, port 8090.
Override with CORS_UPSTREAM, CORS_PORT, CORS_HOST env vars.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import urllib.error
import urllib.request

UPSTREAM = os.environ.get("CORS_UPSTREAM", "http://localhost:8000").rstrip("/")
HOST = os.environ.get("CORS_HOST", "127.0.0.1")
PORT = int(os.environ.get("CORS_PORT", "8090"))
# Must exceed CLOUDFLARE_SPEED_TIMEOUT (default 120s) so /v1/speedtest survives.
TIMEOUT = 130


class Proxy(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _proxy(self):
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            data = self.rfile.read(n) if n else None
            req = urllib.request.Request(UPSTREAM + self.path, data=data, method=self.command)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                body = r.read()
                self.send_response(r.status)
                self._cors()
                self.send_header("Content-Type", r.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self._cors()
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())

    do_GET = do_POST = _proxy

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"CORS proxy on http://{HOST}:{PORT} -> {UPSTREAM}")
    ThreadingHTTPServer((HOST, PORT), Proxy).serve_forever()
