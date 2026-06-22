import subprocess
import sys
import time

def main():
    print("========================================")
    print("  HELIOS ICU SIMULATOR - MASTER BOOT    ")
    print("========================================")

    # sys.executable guarantees that the script uses the exact same
    # Python virtual environment (.venv) that you are currently running.
    python_bin = sys.executable
    processes = []

    try:
        # 1. BOOT THE BRAIN (Central Server)
        print("[1/7] Starting Central Patient Server...")
        server_process = subprocess.Popen([python_bin, "core/server.py"])
        processes.append(server_process)

        # Give the server 2 seconds to fully start and open port 9000
        time.sleep(2)

        # 2. DEFINE THE ORGANS (Your Modules)
        # Make sure these paths match your exact folder names!
        modules = [
            ("Ventilator", "Ventilator/app.py"),
            ("ECG", "ECG/app.py"),
            ("ICP Monitor", "ICP/app.py"),
            ("Pulse Oximeter", "pulse oximeter/app.py"),
            ("Hemodynamics", "HemodynamicsMonitor/app.py"),
            ("Defibrillator", "Defibrillator/main.py"),
            # ("CRRT", "CRRT/main.py")
        ]

        # 3. BOOT THE ORGANS
        step = 2
        for name, path in modules:
            print(f"[{step}/7] Starting {name}...")
            proc = subprocess.Popen([python_bin, path])
            processes.append(proc)
            step += 1
            # A tiny delay prevents UI windows from crashing into each other on startup
            time.sleep(0.5)

        print("========================================")
        print(" All systems online! Press Ctrl+C to shut down.")
        print("========================================")

        # Keep the master script alive while the child processes run
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        # 4. GRACEFUL SHUTDOWN
        # If you press Ctrl+C in the terminal, it will safely kill all windows at once.
        print("\n[SYSTEM] Shutting down all simulator modules...")
        for p in processes:
            p.terminate()
        print("[SYSTEM] Shutdown complete.")

if __name__ == "__main__":
    main()