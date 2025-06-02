import os
import http.server
import socketserver
import json
from urllib.parse import unquote, parse_qs

print("🔧 Starting dashboard.py...")

PORT = 8000
BASE_DIR = os.path.dirname(__file__)
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
WEB_DIR = os.path.join(BASE_DIR, "web")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"📥 Received GET request: {self.path}")

        if self.path == '/' or self.path == '/index.html':
            index_path = os.path.join(WEB_DIR, "index.html")
            if os.path.exists(index_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Dashboard file missing")
                return

        elif self.path.startswith('/memory'):
            agent_filter = ""
            if '?' in self.path and 'agent=' in self.path:
                query = parse_qs(self.path.split('?')[1])
                agent_filter = query.get('agent', [''])[0].lower()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            files = []
            for f in sorted(os.listdir(MEMORY_DIR)):
                if f.endswith(".txt"):
                    if agent_filter:
                        with open(os.path.join(MEMORY_DIR, f), "r", encoding="utf-8") as content:
                            if agent_filter in content.read().lower():
                                files.append(f)
                    else:
                        files.append(f)

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

        elif self.path == '/digest':
            digest_path = os.path.join(LOGS_DIR, "daily_digest.txt")
            if os.path.exists(digest_path):
                with open(digest_path, "r", encoding="utf-8") as f:
                    digest = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(digest.encode())
            else:
                self.send_error(404, "Digest not found")

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

        elif self.path == '/insights':
            from agents import log_insights
            result = log_insights.analyze_logs()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode())

        elif self.path == '/download/logs.zip':
            self._send_zip("logs")

        elif self.path == '/download/memory.zip':
            self._send_zip("memory")

        else:
            print(f"❓ Unknown GET path: {self.path}")
            super().do_GET()

    def do_POST(self):
        print(f"📨 Received POST request: {self.path}")

        if self.path == '/save-goal':
            length = int(self.headers['Content-Length'])
            new_goal = self.rfile.read(length).decode()
            with open(os.path.join(BASE_DIR, "scheduled_goal.txt"), "w", encoding="utf-8") as f:
                f.write(new_goal)
            self.send_response(200)
            self.end_headers()

        elif self.path == '/run-now':
            from consensus import main
            print("⚡ Manual run triggered via dashboard")
            main.run()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write("✅ Main agent executed successfully.".encode("utf-8"))

    def _send_zip(self, folder_name):
        import io
        import zipfile

        folder_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(folder_path):
            self.send_error(404, "Folder not found")
            return

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=BASE_DIR)
                    zipf.write(file_path, arcname)

        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="{folder_name}.zip"')
        self.end_headers()
        self.wfile.write(buffer.getvalue())

os.chdir(BASE_DIR)

try:
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"✅ Serving dashboard at http://localhost:{PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Server error: {e}")
