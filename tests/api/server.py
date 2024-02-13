import http
import http.server
import json
import multiprocessing
import time
import urllib.parse

PORT = 12345
ENCODING = 'utf8'

SLEEP_TIME_SEC = 0.2
REAP_TIME_SEC = 0.5

def start():
    next_response_queue = multiprocessing.Queue()

    process = multiprocessing.Process(target = _run, args = (next_response_queue,))
    process.start()

    time.sleep(SLEEP_TIME_SEC)

    return process, next_response_queue

def stop(process):
    if (process.is_alive()):
        process.terminate()
        process.join(REAP_TIME_SEC)

        if (process.is_alive()):
            process.kill()
            process.join(REAP_TIME_SEC)

    process.close()

def _run(next_response_queue):
    Handler._next_response_queue = next_response_queue
    server = http.server.HTTPServer(('', PORT), Handler)
    server.serve_forever()

class Handler(http.server.BaseHTTPRequestHandler):
    _next_response_queue = None

    def do_GET(self):
        raw_content = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(raw_content)

        code = http.HTTPStatus.OK
        headers = {}

        content = Handler._next_response_queue.get()
        payload = json.dumps(content)

        self.send_response(code)

        for (key, value) in headers:
            self.send_header(key, value)
        self.end_headers()

        self.wfile.write(payload.encode(ENCODING))
