#!/usr/bin/env python3
"""Test server starts and responds."""

import subprocess
import time
import requests
import sys
import os

# Start server in background
server_proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'red_dust.server.api:app', 
     '--host', '127.0.0.1', '--port', '8001'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ, 'PYTHONPATH': '.'}
)

print(f"Server started with PID {server_proc.pid}")

try:
    # Wait for server to start
    time.sleep(3)
    
    # Test endpoint
    response = requests.get('http://127.0.0.1:8001/api/state')
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Tick: {data.get('tick')}")
        print("Server is working!")
    else:
        print(f"Error: {response.text}")
finally:
    # Kill server
    server_proc.terminate()
    server_proc.wait()
    print("Server stopped.")