"""
start_server.py
Zero-dependency HTTP server runner for SamaadSetu Citizen Portal & Officer Desk.
Run:
    python start_server.py
Then open:
    Citizen Portal:  http://localhost:8080/index.html
    Officer Desk:    http://localhost:8080/officer.html
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).resolve().parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Enable CORS and disable cache for seamless hackathon development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def run():
    os.chdir(DIRECTORY)
    print("=" * 65)
    print("  SAMAADSETU - UNIVERSAL CITIZEN GRIEVANCE & VERIFICATION SYSTEM")
    print("=" * 65)
    print(f" Serving directory : {DIRECTORY}")
    print(f" Citizen Portal    : http://localhost:{PORT}/index.html")
    print(f" Officer Desk      : http://localhost:{PORT}/officer.html")
    print("=" * 65)
    print(" Press Ctrl+C to stop the server.")

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run()
