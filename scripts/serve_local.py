#!/usr/bin/env python3
"""Local preview server: serves local.html (with valuations) at /.

Run from the repo root: python3 scripts/serve_local.py [port]
The deployed site uses index.html, which never contains valuations.
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class LocalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        import os
        clean = self.path.split('?')[0]
        if clean.endswith('/index.html'):
            clean = clean[: -len('index.html')]
        if clean.endswith('/'):
            candidate = self.translate_path(clean + 'local.html')
            if os.path.exists(candidate):
                self.path = clean + 'local.html'
        return super().do_GET()

    def log_message(self, *args):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
print(f'serving local.html at http://localhost:{port}/')
ThreadingHTTPServer(('127.0.0.1', port), LocalHandler).serve_forever()
