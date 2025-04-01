#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

# Get port from command line argument or use default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Change to the directory containing this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
        
    def do_GET(self):
        # For the root path, redirect to the RSS feed
        if self.path == '/':
            self.path = '/npo_new_programs.xml'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving NPO RSS feed at port {PORT}")
    httpd.serve_forever()
