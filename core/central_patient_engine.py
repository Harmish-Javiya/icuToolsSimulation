import requests


class CentralPatientEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.server_url = "http://127.0.0.1:9000"

            # A local safety cache in case the server connection hiccups
            cls._instance._fallback = {
                "hr": 80.0, "spo2": 98.0, "rr": 16.0, "bp_sys": 120.0,
                "bp_dia": 80.0, "map": 93.0, "co": 5.0, "rhythm": "NSR",
                "temperature": 37.0, "fluid_balance": 0.0, "icp": 10.0,
            }
        return cls._instance

    def get(self, vital):
        try:
            # Ask the server for the current vital
            response = requests.get(f"{self.server_url}/vitals/{vital}", timeout=0.1)
            if response.status_code == 200:
                val = response.json()["value"]
                self._fallback[vital] = val  # update local backup
                return val
        except requests.exceptions.RequestException:
            pass  # Silent fail: just use the local backup to keep the UI smooth

        return self._fallback.get(vital)

    def update(self, source, vital, value):
        try:
            # Tell the server to update the vital
            payload = {"source": source, "vital": vital, "value": value}
            requests.post(f"{self.server_url}/vitals", json=payload, timeout=0.1)
            self._fallback[vital] = value
            return True
        except requests.exceptions.RequestException:
            return False