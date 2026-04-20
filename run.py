#!/usr/bin/env python3
"""
Credit Risk Markov System - Single Command Runner
Starts backend API and frontend server automatically
"""

import subprocess
import sys
import time
import os
import webbrowser
import signal
from pathlib import Path


def install_requirements():
    """Install dependencies if needed"""
    print("Checking dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], 
            cwd=str(Path(__file__).parent),
            check=True
        )
        print("Dependencies ready\n")
    except Exception as e:
        print(f"Warning: {e}\n")


def start_backend():
    """Start FastAPI backend server"""
    print("Starting Backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(Path(__file__).parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Backend running on http://localhost:8000\n")
    return backend_process


def start_frontend():
    """Start HTTP server for frontend"""
    print("Starting Frontend (Web Server)...")
    frontend_dir = Path(__file__).parent / "frontend"
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Frontend running on http://localhost:8080\n")
    return frontend_process


def open_browser():
    """Open browser after servers start"""
    time.sleep(3)
    try:
        print("Opening browser...\n")
        webbrowser.open("http://localhost:8080")
    except:
        print("Open http://localhost:8080 manually in your browser\n")


def main():
    print("\n" + "="*60)
    print("  CREDIT RISK MARKOV CHAIN ANALYZER")
    print("  Stochastic Process Analysis for Credit Default Risk")
    print("="*60 + "\n")
    
    backend_proc = None
    frontend_proc = None

    try:
        install_requirements()
        
        backend_proc = start_backend()
        frontend_proc = start_frontend()
        
        # Open browser in separate thread
        try:
            open_browser()
        except:
            pass
        
        print("="*60)
        print("  SYSTEM RUNNING")
        print("="*60)
        print("\nAPI:      http://localhost:8000")
        print("Frontend: http://localhost:8080")
        print("\nFeatures:")
        print("   - Upload bank statement PDF")
        print("   - View Markov transition matrix")
        print("   - Analyze credit risk & default probability")
        print("   - State sequence visualization")
        print("   - Dynamic credit scoring\n")
        print("Press Ctrl+C to stop\n")
        
        # Keep backend running
        backend_proc.wait()
        
    except KeyboardInterrupt:
        print("\n\nShutting down servers...\n")
        
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        
        try:
            if backend_proc:
                backend_proc.wait(timeout=5)
            if frontend_proc:
                frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if backend_proc:
                backend_proc.kill()
            if frontend_proc:
                frontend_proc.kill()
        
        print("✅ Servers stopped\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()

