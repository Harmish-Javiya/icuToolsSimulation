# ICU Patient Telemetry Simulation Suite

A high-fidelity, modular, and completely offline software-defined medical device simulation platform. This suite provides real-time, physics-driven respiratory and cardiovascular data visualization alongside standardized telemetry streaming capabilities for training, testing, or ingestion into secure network infrastructures.

---

## 🚀 Features

### 1. Respiratory Module (Ventilator)
* **Active Two-Way Physics:** Simulates mechanical lung compliance, airflow resistance, and patient gas exchange (SpO2).
* **Clinical Modes:** Implements Volume Control Ventilation (VCV) and Pressure Control Ventilation (PCV) settings.
* **Smart Alarms:** Active tracking for barotrauma (high pressure) and disconnecting loops.

### 2. Cardiovascular Module (ECG Simulator)
* **Full 12-Lead Mathematical Matrix:** Uses multi-dimensional overlapping Gaussian curves to synthesize mathematically accurate PQRST waveforms.
* **Dynamic Slot Routing:** A mutually exclusive 4-channel UI layout allowing users to select any 4 camera viewpoints (Leads I-III, aVR-aVF, V1-V6) concurrently without data collision.
* **Lethal Rhythm Injection:** One-click generation of Normal Sinus Rhythm, Ventricular Tachycardia, Severe Bradycardia, and Asystole flatlines containing realistic ambient electromagnetic interference.

### 3. Data Infrastructure
* **Standardized JSON Sockets:** Telemetry is structurally serialized into JSON objects and fired over isolated UDP connections at 20 Hz to prevent network lag on the UI.
* **Offline Closed-Loops:** Designed to run entirely decoupled from the WAN, broadcasting safely via local virtual interfaces (such as VirtualBox Host-Only adapters).

---

## 📦 Installation & Setup

Ensure you have Python 3.10+ installed on your host system.

1. **Clone the repository and enter the root directory:**
   ```bash
   git clone https://github.com/Harmish-Javiya/icuToolsSimulation
   cd icuToolsSimulation
   ```
   
## Use Case

Important Prerequisite: This project strictly requires Python 3.10.
If you have a newer or older version, you must use a version manager (like pyenv) or install Python 3.10 specifically alongside your current installation to ensure compatibility.

## 1. Install Python 3.10

🪟 Windows

Download the Python 3.10 installer from the official Python website.

Run the installer.

CRITICAL: Check the box that says "Add Python 3.10 to PATH" at the bottom of the installer window before clicking "Install Now".

🍎 macOS

The easiest way to install a specific Python version on macOS is using Homebrew:
```bash
brew install python@3.10
```

🐧 Linux (Ubuntu/Debian)

Use the deadsnakes PPA to get the exact version:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

## 2. Create a Virtual Environment

It is highly recommended to isolate the project dependencies using a virtual environment (venv).

Open your terminal, navigate to the root directory of this project, and run the following commands based on your OS:

🪟 Windows (Command Prompt / PowerShell)
```
# Create the virtual environment using Python 3.10
py -3.10 -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

🍎 macOS & 🐧 Linux

```
# Create the virtual environment using Python 3.10
python3.10 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

(You will know it is activated when you see (venv) appear at the beginning of your terminal prompt).

## 3. Install Dependencies

With your virtual environment activated, install all required packages using the provided requirements.txt file:
```
# Upgrade pip to the latest version first
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

## 4. IDE Configuration

To ensure your code editor recognizes the dependencies and the Python 3.10 environment, follow these steps for your preferred IDE:

### 💻 Visual Studio Code (VS Code)

* Open the project folder in VS Code.

* Open the Command Palette (Ctrl+Shift+P on Windows/Linux, Cmd+Shift+P on macOS).

* Search for and select: Python: Select Interpreter.

* Choose the interpreter that lives inside your newly created virtual environment (it should look something like ./venv/Scripts/python.exe or ./venv/bin/python).

* Open a new terminal inside VS Code; it should automatically activate the (venv).

### 💻 PyCharm

* Open the project folder in PyCharm.
* Go to Settings (Windows/Linux: File -> Settings | macOS: PyCharm -> Settings).
* Navigate to Project: [Your Project Name] -> Python Interpreter.
* Click the "Add Interpreter" link or the gear icon next to the current interpreter dropdown, and select Add Local Interpreter...
* Select Existing environment.
* Point the path to the Python executable inside your virtual environment:
* Windows: <project_root>\venv\Scripts\python.exe
* Mac/Linux: <project_root>/venv/bin/python
* Click Apply and OK. PyCharm will begin indexing the installed packages.

## To Test Files

* we have to run 3 files to make it run
* ``` python core/server.py ``` in 1st terminal
* ``` python aggregator.py ``` in 2nd terminal
* ``` python masterboot.py ``` in 3rd terminal (this will fire up all the tools included in this python code)

and this is it , we successfully run our tools