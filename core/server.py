from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import threading
import time
import socket
import json

app = FastAPI(title="ICU Central Patient Engine Server")

# The Master Physiological State
vitals_state = {
    "hr": 80.0, "spo2": 98.0, "rr": 16.0, "bp_sys": 120.0,
    "bp_dia": 80.0, "map": 93.0, "co": 5.0, "rhythm": "NSR",
    "temperature": 37.0, "fluid_balance": 0.0, "icp": 10.0,
    "scenario": "Healthy"
}

# The Master Ownership Rules
owners = {
    "hr": "ECG", "rhythm": "ECG",
    "spo2": "VENT", "rr": "VENT",
    "bp_sys": "HEMO", "bp_dia": "HEMO", "map": "HEMO", "co": "HEMO",
    "fluid_balance": "CRRT", "icp": "NEURO",
    "scenario": "ALL"
}


class UpdateRequest(BaseModel):
    source: str
    vital: str
    value: float | str


@app.get("/vitals/{vital}")
def get_vital(vital: str):
    if vital in vitals_state:
        return {"value": vitals_state[vital]}
    raise HTTPException(status_code=404, detail="Vital not found")


@app.post("/vitals")
def update_vital(req: UpdateRequest):
    owner = owners.get(req.vital)

    if owner and owner != "ALL" and owner != req.source:
        print(f"[BLOCKED] {req.source} attempted to modify {req.vital}. Owner={owner}")
        raise HTTPException(status_code=403, detail="Ownership violation")

    vitals_state[req.vital] = req.value
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {req.source} updated {req.vital} -> {req.value}")
    return {"status": "success"}


# ==========================================
# MASTER TELEMETRY BROADCASTER
# ==========================================
def udp_broadcaster():
    """Runs in the background and broadcasts the total ICU state via UDP."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target_address = ("127.0.0.1", 8000)

    while True:
        try:
            master_packet = {
                "device_id": "MASTER-ICU-SERVER",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "vitals": vitals_state.copy()  # Send the whole dictionary
            }
            packet_bytes = (json.dumps(master_packet) + "\n").encode("utf-8")
            udp_socket.sendto(packet_bytes, target_address)
        except Exception as e:
            print(f"Broadcast error: {e}")

        time.sleep(0.5)  # Transmit twice per second


if __name__ == "__main__":
    print("Starting Central Patient Server on Port 9000...")

    # Start the UDP broadcaster in the background before starting the web server
    threading.Thread(target=udp_broadcaster, daemon=True).start()

    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="warning")