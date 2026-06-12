class CRRTMachine:

    def __init__(self):

        # Therapy Settings
        self.mode = "CVVHDF"

        self.blood_flow_rate = 150      # mL/min
        self.dialysate_flow_rate = 2000 # mL/hr
        self.ultrafiltration_rate = 100 # mL/hr

        self.running = False

    def start(self):
        self.running = True
        print("CRRT Machine Started")

    def stop(self):
        self.running = False
        print("CRRT Machine Stopped")

    def get_status(self):

        return {
            "Mode": self.mode,
            "Blood Flow Rate": self.blood_flow_rate,
            "Dialysate Flow Rate": self.dialysate_flow_rate,
            "Ultrafiltration Rate": self.ultrafiltration_rate,
            "Running": self.running
        }