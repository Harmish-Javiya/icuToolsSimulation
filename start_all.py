import subprocess
import time
import sys
import os

# 🏥 THE WARD CONFIGURATION
# Update the paths inside the quotes if your folder names are slightly different
PROCESSES = [
    # 1. The Secure Choke Point (Must start FIRST)
    {"name": "Master Aggregator", "path": "aggregator.py"},
    
    # 2. The 8 ICU Microservices
    {"name": "Ventilator", "path": "Ventilator/app.py"},
    # {"name": "Pulse Oximeter", "path": "pulse oximeter/ui/mainWindow_v2.py"},
    # {"name": "Hemodynamics", "path": "HemodynamicsMonitor/app.py"},
    {"name": "Defibrillator", "path": "Defibrillator/ui.py"},
    {"name": "CRRT Machine", "path": "CRRT/main.py"},
    
    # Add your final tools here:
    {"name": "ECG Simulator", "path": "ECG/app.py"},
    {"name": "ICP Monitor", "path": "ICP/app.py"},
    # {"name": "Eighth Tool", "path": "Tool8/app.py"} # Update with your 8th tool's exact folder
]

def launch_ward():
    running_processes = []
    
    print("\n" + "="*50)
    print("🏥 POWERING UP HELIOS ICU SIMULATION WARD")
    print("="*50 + "\n")

    try:
        for p in PROCESSES:
            # Check if the file actually exists before trying to run it
            if not os.path.exists(p["path"]):
                print(f"⚠️  WARNING: Could not find {p['path']}. Skipping {p['name']}.")
                continue

            print(f"🟢 Launching {p['name']}...")
            
            # Start the process in the background
            process = subprocess.Popen([sys.executable, p["path"]])
            running_processes.append({"name": p["name"], "process": process})
            
            # Give the Aggregator a full second to wake up before blasting it with data
            if p["name"] == "Master Aggregator":
                time.sleep(1.5)
            else:
                time.sleep(0.5)

        print("\n✅ All available devices are online and broadcasting!")
        print("🛑 Press Ctrl+C in this terminal to shut down the entire ward.\n")

        # Keep the master script alive while the tools run
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 SHUTDOWN SEQUENCE INITIATED...")
        
        # Cleanly terminate all tools so you don't have zombie UI windows
        for p in running_processes:
            print(f"🔴 Stopping {p['name']}...")
            p["process"].terminate()
            
        print("\n🏥 Ward safely powered down. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    launch_ward()