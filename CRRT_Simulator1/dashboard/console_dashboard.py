class ConsoleDashboard:

    def display(
        self,
        patient,
        pressure,
        filter_obj,
        fluid,
        alarms
    ):

        print("\n" * 3)

        print("=" * 60)
        print("          CRRT SIMULATOR DASHBOARD")
        print("=" * 60)

        print("\nPATIENT STATUS")
        print("-" * 60)

        print(f"Heart Rate      : {patient.hr} bpm")
        print(
            f"Blood Pressure  : "
            f"{patient.bp_sys}/{patient.bp_dia} mmHg"
        )
        print(f"SpO2            : {patient.spo2}%")
        print(
            f"Temperature     : "
            f"{patient.temperature} °C"
        )

        print("\nRENAL PARAMETERS")
        print("-" * 60)

        print(f"BUN             : {patient.bun}")
        print(
            f"Creatinine      : "
            f"{patient.creatinine}"
        )
        print(
            f"Potassium       : "
            f"{patient.potassium}"
        )

        print("\nPRESSURE DATA")
        print("-" * 60)

        print(
            f"Access Pressure : "
            f"{pressure.access_pressure}"
        )

        print(
            f"Return Pressure : "
            f"{pressure.return_pressure}"
        )

        print(
            f"TMP             : "
            f"{pressure.tmp}"
        )

        print("\nFILTER STATUS")
        print("-" * 60)

        print(
            f"Health          : "
            f"{round(filter_obj.health,2)}%"
        )

        print(
            f"Status          : "
            f"{filter_obj.status}"
        )

        print("\nFLUID BALANCE")
        print("-" * 60)

        print(
            f"Net Balance     : "
            f"{fluid.get_net_balance()} mL"
        )

        print("\nALARMS")
        print("-" * 60)

        if alarms:

            for alarm in alarms:
                print(f"⚠ {alarm}")

        else:
            print("No Active Alarms")

        print("=" * 60)


        