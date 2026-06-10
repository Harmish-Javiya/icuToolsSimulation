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