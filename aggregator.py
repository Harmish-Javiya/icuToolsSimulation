import socket
import json
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')

UDP_IP = "127.0.0.1"
UDP_PORT = 8000

# === THE MEMORY CACHE ===
cached_vitals = {
    "hr": "--", "spo2": "--", "bp_sys": "--", "bp_dia": "--", "scenario": "Unknown", "icp": "--"
}

# === SETUP JSON LOGGING DIRECTORY ===
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ---> CHANGED: USE A SINGLE STATIC FILE INSTEAD OF TIMESTAMPED ONES <---
JSON_LOG_FILE = os.path.join(LOG_DIR, "icu_master_telemetry_log.json")


def log_to_json_file(data_dict):
    """Appends a JSON dictionary to the single master log file."""
    # Add a timestamp to the data if it doesn't already have one,
    # so you can distinguish between different simulation runs in the single file.
    if "timestamp" not in data_dict and "aggregator_timestamp" not in data_dict:
        data_dict["aggregator_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(JSON_LOG_FILE, 'a') as f:
        # Write the JSON object on a new line (JSON Lines format)
        json.dump(data_dict, f)
        f.write('\n')


def run_master_aggregator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    logging.info(f"⚙️ MASTER ICU Aggregator listening on {UDP_IP}:{UDP_PORT}...")
    logging.info(f"💾 Saving all JSON packets continuously to: {JSON_LOG_FILE}\n")
    logging.info("=" * 70)

    try:
        while True:
            data_bytes, addr = sock.recvfrom(4096)
            raw_string = data_bytes.decode('utf-8').strip()

            try:
                data = json.loads(raw_string)

                # ---> SAVE TO THE SINGLE FILE <---
                log_to_json_file(data)

                device_id = data.get("device_id", "UNKNOWN")

                # 1. CATCH THE MASTER SERVER (Update the Cache)
                if "MASTER-ICU" in device_id:
                    vitals = data.get("vitals", {})
                    cached_vitals.update(vitals)

                # 2. CATCH THE THIN PAYLOAD DEVICES (Merge with Cache)
                elif "VENT-PULMO" in device_id:
                    logging.info(
                        f"[🫁 VENT] Paw: {data.get('paw', '--')} | Vol: {data.get('vol', '--')} || Patient SpO2: {cached_vitals['spo2']}%")

                elif "DEFIB-CARDIO" in device_id:
                    dev_state = data.get("device", {}).get("state", "--")
                    rhythm = data.get("local_rhythm", "--")
                    event = data.get("latest_event", "")
                    logging.info(
                        f"[⚡ DEFIB] State: {dev_state} | Rhythm: {rhythm} | Event: {event} || Patient HR: {cached_vitals['hr']} bpm")

                elif "HEMO-CARDIO" in device_id:
                    logging.info(
                        f"[🩸 HEMO] SV: {data.get('sv', '--')} | CVP: {data.get('cvp', '--')} || Patient BP: {cached_vitals['bp_sys']}/{cached_vitals['bp_dia']}")

                elif "ICP-NEURO" in device_id:
                    logging.info(
                        f"[🧠 NEURO] Local ICP: {data.get('mean_icp', '--')} || Global ICP: {cached_vitals['icp']}")

                elif "PUMP-MED" in device_id:
                    status = data.get("state", "--")
                    flow = data.get("flow_rate", "--")
                    infused = data.get("infused", "--")
                    logging.info(f"[💧 PUMP] State: {status} | Rate: {flow} mL/hr | Infused: {infused} mL")

            except json.JSONDecodeError:
                pass

    except KeyboardInterrupt:
        logging.info("\nAggregator safely shut down.")


if __name__ == "__main__":
    run_master_aggregator()