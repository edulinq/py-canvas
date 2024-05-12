import glob
import http
import http.server
import json
import multiprocessing
import os
import time
import urllib.parse

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
RESPONSES_DIR = os.path.join(THIS_DIR, "responses")

# Just a random port that is unlikely to be in use.
# Tests will sometimes need to point to a URL in their response,
# so this number will need to be static unless response infrastructure is updated.
PORT = 53179
ENCODING = 'utf8'

SLEEP_TIME_SEC = 0.2
REAP_TIME_SEC = 0.5

def start():
    process = multiprocessing.Process(target = _run)
    process.start()

    time.sleep(SLEEP_TIME_SEC)

    return process

def stop(process):
    if (process.is_alive()):
        process.terminate()
        process.join(REAP_TIME_SEC)

        if (process.is_alive()):
            process.kill()
            process.join(REAP_TIME_SEC)

    process.close()

def _run():
    _load_responses()

    server = http.server.HTTPServer(('', PORT), Handler)
    server.serve_forever()

def _load_responses():
    for path in sorted(glob.glob(os.path.join(RESPONSES_DIR, "**", "*.json"), recursive = True)):
        with open(path, 'r') as file:
            data = json.load(file)

        body = data['body']
        if (not data.get('text', False)):
            body = json.dumps(body)

        Handler._static_responses[data['url']] = body

class Handler(http.server.BaseHTTPRequestHandler):
    _static_responses = {}

    def log_message(self, format, *args):
        return

    def do_GET(self):
        raw_content = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(raw_content)

        code = http.HTTPStatus.OK
        headers = {}

        payload = self._get_response(self.path)

        self.send_response(code)

        for (key, value) in headers:
            self.send_header(key, value)
        self.end_headers()

        self.wfile.write(payload.encode(ENCODING))

    def do_POST(self):
        self.do_GET()

    def _get_response(self, path):
        path = urllib.parse.unquote(path)

        # First check for a full match.
        if (path in Handler._static_responses):
            return Handler._static_responses[path]

        # Check for a match without per_page.
        parts = urllib.parse.urlparse(path)

        params = urllib.parse.parse_qs(parts.query)
        params.pop('per_page', None)
        new_parts = parts._replace(query = urllib.parse.urlencode(params, doseq = True))
        new_path = urllib.parse.unquote(new_parts.geturl())

        if (new_path in Handler._static_responses):
            return Handler._static_responses[new_path]

        # Finally check for a match without params.
        raw_path = parts.path

        if (raw_path in Handler._static_responses):
            return Handler._static_responses[raw_path]

        raise ValueError("Could not find static response to path: '%s'." % (path))
