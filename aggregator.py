import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

UDP_IP = "127.0.0.1"
UDP_PORT = 8000

def run_master_aggregator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    logging.info(f"🎧 Local Aggregator listening on {UDP_IP}:{UDP_PORT}...\n")
    logging.info("-" * 60)

    try:
        while True:
            data_bytes, addr = sock.recvfrom(4096) 
            raw_string = data_bytes.decode('utf-8').strip()
            
            try:
                data = json.loads(raw_string)
                device = data.get("device_id", "UNKNOWN")
                
                if "ICP-NEURO" in device:
                    logging.info(f"[🧠 NEURO]   ICP: {data.get('mean_icp', '--')} mmHg")
                elif "SPO2-PULMO" in device:
                    logging.info(f"[🫁 PULMO]   SpO2: {data.get('spo2', '--')}% | HR: {data.get('heart_rate', '--')}")
                elif "VENT-PULMO" in device:
                    logging.info(f"[🫁 PULMO]   Vent Vol: {data.get('vol', '--')} | Paw: {data.get('paw', '--')}")
                elif "HEMO-CARDIO" in device:
                    logging.info(f"[🫀 CARDIO]  BP: {data.get('sbp', '--')}/{data.get('dbp', '--')} | MAP: {data.get('map', '--')}")
                elif "DEFIB-CARDIO" in device:
                    patient = data.get("patient", {})
                    logging.info(f"[⚡ DEFIB]   Status: {data.get('device', {}).get('state', '--')} | Rhythm: {patient.get('rhythm', '--')}")
                elif "CRRT-RENAL" in device:
                    logging.info(f"[🩸 RENAL]   Filter: {data.get('filter', {}).get('health', '--')}% | Fluid Bal: {data.get('fluid_balance', '--')}")
                else:
                    logging.info(f"[📦 OTHER]   {device}: {data}")

            except json.JSONDecodeError:
                logging.error("❌ Received malformed JSON packet")

    except KeyboardInterrupt:
        logging.info("\nAggregator safely shut down.")

if __name__ == "__main__":
    run_master_aggregator()