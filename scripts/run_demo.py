"""
Cross-Platform One-Command Local Demo Launcher
Knowledge-Driven IoT Fault Diagnosis System
Runs:
  1. Local Embedded MQTT Broker (Port 1884)
  2. Telemetry Ingestion Service (Validator, SQLite/CSV writer, Hybrid AI Engine)
  3. Synthetic Publisher (Simulating dynamic motor operating scenarios)
  4. FastAPI Backend API (Port 8000)
  5. Streamlit Industrial Dashboard (Port 8501)
"""

import sys
import os
import time
import subprocess
import signal
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

PYTHON_EXE = sys.executable

processes = []

def cleanup(sig=None, frame=None):
    print("\n[DEMO] Gracefully stopping all services...", flush=True)
    for p in reversed(processes):
        try:
            p.terminate()
        except Exception:
            pass
    for p in reversed(processes):
        try:
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("[DEMO] All services stopped. Goodbye.", flush=True)
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("=" * 80, flush=True)
print("[DEMO] Starting Knowledge-Driven IoT Fault Diagnosis System (Local Demo Mode)", flush=True)
print("=" * 80, flush=True)

# 1. Start Embedded MQTT Broker
print("[1/5] Starting Local MQTT Broker on port 1884...", flush=True)
p_broker = subprocess.Popen([PYTHON_EXE, "scripts/run_broker.py"])
processes.append(p_broker)
time.sleep(1.5)

# 2. Start Ingestion Service
print("[2/5] Starting Telemetry Ingestion & Diagnostic Consumer...", flush=True)
p_sub = subprocess.Popen([PYTHON_EXE, "ingestion/mqtt_subscriber.py"])
processes.append(p_sub)
time.sleep(1.5)

# 3. Start Synthetic Generator
print("[3/5] Starting Synthetic Telemetry Publisher (motor01)...", flush=True)
p_pub = subprocess.Popen([PYTHON_EXE, "simulation/mqtt_publisher.py", "--scenario", "normal", "--interval", "1.0"])
processes.append(p_pub)
time.sleep(1.5)

# 4. Start FastAPI Backend
print("[4/5] Starting FastAPI REST API on http://localhost:8000...", flush=True)
p_api = subprocess.Popen([PYTHON_EXE, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])
processes.append(p_api)
time.sleep(1.5)

# 5. Start Streamlit Industrial Dashboard
print("[5/5] Launching Streamlit Industrial Monitoring Portal at http://localhost:8501...", flush=True)
print("=" * 80, flush=True)
print("Credentials:", flush=True)
print("  - Admin:    admin / Admin@2026", flush=True)
print("  - Operator: operator / Operator@2026", flush=True)
print("=" * 80, flush=True)

p_dash = subprocess.Popen([
    PYTHON_EXE, "-m", "streamlit", "run", "dashboard/app.py",
    "--server.port=8501",
    "--server.address=0.0.0.0",
    "--browser.gatherUsageStats=false"
])
processes.append(p_dash)

try:
    p_dash.wait()
except KeyboardInterrupt:
    cleanup()
