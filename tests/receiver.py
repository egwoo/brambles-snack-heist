"""A tiny local server for the audio test.

It serves the repo over http (so the page can POST) and saves each POSTed body into tests/out/audio under the
file name given in ?name=. tests/run.sh audio starts it, points headless Chrome at index.html?test&audio=...,
and stops both once the page posts "done".

Usage: python3 tests/receiver.py PORT
"""
import http.server
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tests', 'out', 'audio')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, *args):
        pass

    def do_POST(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = os.path.basename(query.get('name', ['unnamed'])[0])
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        with open(os.path.join(OUT, name), 'wb') as f:
            f.write(body)
        self.send_response(204)
        self.end_headers()


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), Handler).serve_forever()
