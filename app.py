from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
from engine import MinhajAI

ai = MinhajAI()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/health':
            return self.send_json({'ok': True, 'engine': 'MinhajAI-local'})
        if path == '/api/knowledge':
            return self.send_json(ai.knowledge_summary())
        if path == '/' or path == '/index.html':
            try:
                with open('web/index.html', encoding='utf-8') as f: raw=f.read().encode()
                self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
            except FileNotFoundError: self.send_json({'error':'UI missing'},404)
            return
        self.send_json({'error':'Not found'},404)

    def do_POST(self):
        if urlparse(self.path).path != '/api/chat': return self.send_json({'error':'Not found'},404)
        try:
            n=int(self.headers.get('Content-Length','0')); body=json.loads(self.rfile.read(n) or '{}')
            message=str(body.get('message','')).strip()
            if not message: return self.send_json({'error':'message is required'},400)
            self.send_json(ai.answer(message))
        except Exception as e:
            self.send_json({'error': str(e)},500)

if __name__ == '__main__':
    print('Minhaj AI running locally at http://127.0.0.1:8080')
    ThreadingHTTPServer(('127.0.0.1',8080), Handler).serve_forever()
