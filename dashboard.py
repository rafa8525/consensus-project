from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import parse_qs
from pathlib import Path
import os
import json

PORT = 8000

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/goal":
            goal_path = Path("scheduled_goal.txt")
            if goal_path.exists():
                goal = goal_path.read_text(encoding="utf-8")
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(goal.encode("utf-8"))
                print("📤 Serving goal:", goal.strip())
            else:
                self.send_error(404, "Goal not found.")

        elif self.path == "/memory-list":
            try:
                files = os.listdir("memory")
                memory_logs = [f for f in files if f.startswith("memory_log_")]
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(memory_logs).encode("utf-8"))
                print("📤 Sent memory log list")
            except Exception as e:
                self.send_error(500, "Error reading memory folder.")

        elif self.path == "/logs/daily_digest.txt":
            digest_path = Path("logs/daily_digest.txt")
            if digest_path.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(digest_path.read_text(encoding="utf-8").encode("utf-8"))
            else:
                self.send_error(404, "Digest not found.")
        else:
            if self.path == "/":
                self.path = "/web/index.html"
            return super().do_GET()

    def do_POST(self):
        if self.path == "/save-goal":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(post_data)
            goal = data.get("goal", [""])[0]
            Path("scheduled_goal.txt").write_text(goal, encoding="utf-8")
            print("📝 Received /save-goal with:", goal)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Goal saved successfully.")
        else:
            self.send_error(404, "Unknown POST route")

with TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"✅ Serving dashboard at http://localhost:{PORT}")
    httpd.serve_forever()
