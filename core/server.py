from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime

app = FastAPI(title="ICU Central Patient Engine Server")

# The Master Physiological State
vitals_state = {
    "hr": 80.0, "spo2": 98.0, "rr": 16.0, "bp_sys": 120.0,
    "bp_dia": 80.0, "map": 93.0, "co": 5.0, "rhythm": "NSR",
    "temperature": 37.0, "fluid_balance": 0.0, "icp": 10.0,
    "scenario": "Healthy"  # <-- Added Global Scenario State
}

# The Master Ownership Rules
owners = {
    "hr": "ECG", "rhythm": "ECG",
    "spo2": "VENT", "rr": "VENT",
    "bp_sys": "HEMO", "bp_dia": "HEMO", "map": "HEMO", "co": "HEMO",
    "fluid_balance": "CRRT", "icp": "NEURO",
    "scenario": "ALL"      # <-- Added Universal Ownership for Scenarios
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

    # Allow if the source matches the owner, OR if the owner is "ALL"
    if owner and owner != "ALL" and owner != req.source:
        print(f"[BLOCKED] {req.source} attempted to modify {req.vital}. Owner={owner}")
        raise HTTPException(status_code=403, detail="Ownership violation")

    # Update the master state
    vitals_state[req.vital] = req.value

    # Print the matrix log so you can watch the simulation run
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {req.source} updated {req.vital} -> {req.value}")
    return {"status": "success"}


if __name__ == "__main__":
    print("Starting Central Patient Server on Port 9000...")
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="warning")