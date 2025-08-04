#!/usr/bin/env python3
"""
Startup script for AWS FinOps Application

This script helps start both the backend and frontend services.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import boto3
        print("✓ Python dependencies OK")
    except ImportError as e:
        print(f"✗ Missing Python dependency: {e}")
        print("Please run: pip install -r backend/requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js {result.stdout.strip()} OK")
        else:
            print("✗ Node.js not found")
            return False
    except FileNotFoundError:
        print("✗ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm {result.stdout.strip()} OK")
        else:
            print("✗ npm not found")
            return False
    except FileNotFoundError:
        print("✗ npm not found")
        return False
    
    return True


def install_frontend_dependencies():
    """Install frontend dependencies if needed."""
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✓ Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install frontend dependencies: {e}")
            return False
    
    return True


def start_backend():
    """Start the FastAPI backend."""
    print("Starting backend...")
    backend_dir = Path("backend")
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start uvicorn
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
        print("✓ Backend started on http://localhost:8000")
        return process
        
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return None


def start_frontend():
    """Start the Vue.js frontend."""
    print("Starting frontend...")
    frontend_dir = Path("frontend")
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Start development server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ])
        
        print("✓ Frontend started on http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"✗ Failed to start frontend: {e}")
        return None


def wait_for_backend():
    """Wait for backend to be ready."""
    import requests
    
    print("Waiting for backend to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✓ Backend is ready")
                return True
        except:
            pass
        
        attempt += 1
        time.sleep(1)
    
    print("✗ Backend failed to start")
    return False


def main():
    """Main startup function."""
    print("AWS FinOps Application Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Store original directory
    original_dir = os.getcwd()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait for backend to be ready
    if not wait_for_backend():
        backend_process.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("Application Started Successfully!")
    print("=" * 40)
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\nShutting down services...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main() 