#!/usr/bin/env python3
"""
Test Runner with Server for Gista-CrewAI API

This script starts the Flask development server, runs the tests,
and then stops the server.
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import socket
import psutil  # type: ignore

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_process_by_port(port):
    """Find a process using a specific port"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def main():
    """Main function to run tests with server"""
    parser = argparse.ArgumentParser(description='Run tests with server for Gista-CrewAI API')
    parser.add_argument('--port', type=int, default=5001, help='Port for the Flask server (default: 5001)')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    # If no test arguments are provided, run all tests
    if not (args.unit or args.integration or args.e2e or args.all):
        args.all = True
    
    # Check if the server is already running
    server_was_running = is_port_in_use(args.port)
    server_process = None
    
    if server_was_running:
        print(f"Server is already running on port {args.port}")
    else:
        print(f"Starting server on port {args.port}...")
        server_process = subprocess.Popen(
            [sys.executable, "run_dev_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the server to start
        max_retries = 10
        retries = 0
        while not is_port_in_use(args.port) and retries < max_retries:
            time.sleep(1)
            retries += 1
        
        if not is_port_in_use(args.port):
            print("Failed to start server")
            if server_process:
                server_process.terminate()
            return
        
        print("Server started")
    
    # Build the command to run tests
    cmd = [sys.executable, "tests/run_all_tests.py", "--no-prompt"]
    
    if args.unit:
        cmd.append("--unit")
    if args.integration:
        cmd.append("--integration")
    if args.e2e:
        cmd.append("--e2e")
    if args.all:
        cmd.append("--all")
    
    # Run the tests
    try:
        subprocess.run(cmd)
    finally:
        # Stop the server if we started it
        if server_process and not server_was_running:
            print("Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("Server stopped")

if __name__ == "__main__":
    # Add the current directory to the path so that imports work
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main() 