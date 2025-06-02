import os
import http.server
import socketserver
import json
from urllib.parse import unquote

PORT = 8000
BASE_DIR = os.path.dirname(__file__)
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/web/index.html'

        elif self.path == '/memory':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            files = sorted(f for f in os.listdir(MEMORY_DIR) if f.endswith(".txt"))
            self.wfile.write(json.dumps(files).encode())

        elif self.path.startswith('/memory/'):
            filename = self.path.replace('/memory/', '')
            filepath = os.path.join(MEMORY_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")

        elif self.path == '/goal':
            goal_path = os.path.join(BASE_DIR, "scheduled_goal.txt")
            if os.path.exists(goal_path):
                with open(goal_path, "r", encoding="utf-8") as f:
                    goal_text = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(goal_text.encode())
            else:
                self.send_error(404, "Scheduled goal not found")

        elif self.path.startswith('/search?keyword='):
            keyword = unquote(self.path.split('=')[1]).lower()
            matches = []

            for fname in os.listdir(MEMORY_DIR):
                if fname.endswith(".txt"):
                    fpath = os.path.join(MEMORY_DIR, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if keyword in content.lower():
                            matches.append(f"\n--- {fname} ---\n{content.strip()}\n")

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write("\n".join(matches).encode())

        elif self.path == '/agent-counts':
            counts = {}
            for fname in os.listdir(LOGS_DIR):
                if fname.endswith(".txt"):
                    with open(os.path.join(LOGS_DIR, fname), "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        for agent in ["planner", "executor", "researcher", "memory_manager", "scheduler"]:
                            if agent in content:
                                counts[agent] = counts.get(agent, 0) + content.count(agent)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(counts).encode())

        else:
            super().do_GET()

os.chdir(BASE_DIR)
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"✅ Serving dashboard at http://localhost:{PORT}")
    httpd.serve_forever()
