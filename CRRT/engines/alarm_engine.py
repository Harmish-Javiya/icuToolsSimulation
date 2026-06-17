class AlarmEngine:

    def check(
        self,
        patient,
        pressure,
        filter_obj
    ):

        alarms = []

        # High Potassium
        if patient.potassium > 6:
            alarms.append(
                "HIGH POTASSIUM ALERT"
            )

        # Low Oxygen
        if patient.spo2 < 92:
            alarms.append(
                "LOW OXYGEN ALERT"
            )

        # High TMP
        if pressure.tmp > 250:
            alarms.append(
                "HIGH TMP ALERT"
            )

        # Filter Clotting
        if filter_obj.health < 20:
            alarms.append(
                "FILTER CLOTTING ALERT"
            )

        # Low Blood Pressure
        if patient.bp_sys < 90:
            alarms.append(
                "HYPOTENSION ALERT"
            )

        return alarms