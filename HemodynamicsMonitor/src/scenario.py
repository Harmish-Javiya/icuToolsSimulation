class Scenario:

    @staticmethod
    def healthy(patient):
        patient.hr = 75
        patient.sbp = 120
        patient.dbp = 80
        patient.sv = 70
        patient.cvp = 8
        patient.rr = 16
        patient.spo2 = 98

    @staticmethod
    def hemorrhage(patient):
        patient.hr = 120
        patient.sbp = 85
        patient.dbp = 50
        patient.sv = 45
        patient.cvp = 3
        patient.rr = 24
        patient.spo2 = 94

    @staticmethod
    def sepsis(patient):
        patient.hr = 110
        patient.sbp = 90
        patient.dbp = 55
        patient.sv = 80
        patient.cvp = 5
        patient.rr = 26
        patient.spo2 = 95

    @staticmethod
    def heart_failure(patient):
        patient.hr = 105
        patient.sbp = 100
        patient.dbp = 65
        patient.sv = 40
        patient.cvp = 16
        patient.rr = 22
        patient.spo2 = 93

    @staticmethod
    def arrest(patient):
        patient.hr = 0
        patient.sbp = 0
        patient.dbp = 0
        patient.sv = 0
        patient.cvp = 0
        patient.rr = 0
        patient.spo2 = 0

