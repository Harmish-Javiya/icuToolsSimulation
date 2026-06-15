# MED-CRT Defibrillator Simulator

This project is a simple defibrillator simulator with a graphical user interface, a small HTTP API, and a basic patient/ECG/alarm model. It is designed to show how a defibrillator system might behave in a simulated environment.

## What this project does

The simulator lets you:
- change the patient rhythm
- select device mode
- choose shock energy
- charge and deliver shocks
- monitor alarms and vitals
- view an ECG waveform
- send telemetry data
- run a small API server for remote control

## Main files

- main.py: starts the application
- ui.py: builds the graphical interface
- simulator.py: connects the device, patient, ECG, alarms, and hardware together
- server.py: provides a simple HTTP API
- src/device.py: defines the defibrillator behavior
- src/patient.py: simulates the patient and vital signs
- src/ecg.py: generates ECG samples
- src/alarms.py: checks and raises alarm conditions
- src/hardware.py: simulates telemetry packet sending
- src/logger.py: saves events to a CSV log file

## Simple explanation of the main functions

### Main entry point
- main.py
  - Starts the simulator app and opens the UI.

### Simulator logic
- simulator.py
  - __init__: creates the device, patient, ECG, alarms, hardware, and logger.
  - add_event(text): stores a new event in the event list.
  - update(): updates the patient state and checks alarms.
  - charge(): starts charging the defibrillator and prepares it for shock.
  - shock(): delivers a shock if the device is ready.
  - disarm(): puts the device in a disarmed state.
  - recharge(): restores the battery.
  - telemetry(): sends the device data to the hardware interface.
  - ecg_sample(): gets the current ECG sample.
  - status(): returns the current device, patient, alarm, and event information.

### HTTP API server
- server.py
  - __init__: creates the server object with host and port details.
  - start(): starts the web server.
  - stop(): stops the web server.
  - _build_handler(): creates the request handler for API requests.
  - _send_json(): sends a JSON reply to the client.
  - _read_json(): reads JSON data from a request.
  - do_GET(): handles read requests like status and health checks.
  - do_POST(): handles actions such as charge, shock, disarm, recharge, and rhythm changes.

### Device behavior
- src/device.py
  - __init__: sets the starting values of the defibrillator.
  - set_mode(mode): changes the operating mode.
  - set_energy(energy): selects the shock energy level.
  - charge(): starts charging the device.
  - ready(): makes the device ready to shock.
  - shock(): delivers the shock if the device is ready.
  - disarm(): puts the device in a disarmed state.
  - recharge(): refills the battery.
  - toggle_sync(): turns synchronization on or off.
  - toggle_pacing(): turns pacing on or off.
  - status(): returns the device status.

### Patient simulation
- src/patient.py
  - __init__: sets the patient’s initial vital signs.
  - set_rhythm(rhythm): changes the patient’s heart rhythm.
  - update_vitals(): updates heart rate, oxygen level, and blood pressure.
  - simulate(): makes the patient state change over time.
  - apply_shock(energy): tries to restore a normal rhythm after a shock.
  - status(): returns the patient’s current vitals.

### ECG generation
- src/ecg.py
  - __init__: starts the ECG generator.
  - next_sample(rhythm): creates one ECG signal value.
  - get_samples(rhythm, count=20): creates multiple ECG samples.

### Alarm system
- src/alarms.py
  - __init__: starts the alarm system as normal.
  - evaluate(device, patient): checks the state and raises the correct alarm.
  - get_alarm(): returns the current alarm message.
  - get_level(): returns the severity level.
  - status(): returns the alarm state.

### Hardware interface
- src/hardware.py
  - __init__: starts the hardware interface as disconnected.
  - connect(): marks the hardware as connected.
  - disconnect(): marks the hardware as disconnected.
  - create_packet(device, patient, alarm): builds a telemetry packet.
  - send(device, patient, alarm): sends the telemetry packet.
  - status(): returns the hardware connection status.

### Logging
- src/logger.py
  - __init__: creates the log file if needed.
  - ensure_file(): makes sure the CSV file exists.
  - log_event(...): writes events to the log file.
  - count(): returns the number of logged events.

### User interface
- ui.py
  - __init__: creates the app window and starts the simulator.
  - _build_ui(): creates the screen layout.
  - _build_right_column(right): creates the side controls panel.
  - apply_energy(): applies the chosen shock energy.
  - set_rhythm(rhythm): changes the rhythm from the UI.
  - trigger_alarm_test(): shows a test alarm.
  - charge_device(): starts charging the device.
  - deliver_shock(): applies a shock.
  - disarm_device(): disarms the device.
  - recharge_device(): recharges the battery.
  - show_ecg(): shows an ECG sample.
  - send_telemetry(): sends telemetry data.
  - _refresh_display(): updates the visible screen data.
  - _tick(): updates the screen continuously like a live display.
  - _start_api_server(): starts the API server.
  - toggle_server(): enables or disables the API server.

## How to run

Run the simulator from the project folder with:

```bash
python main.py
```

You can also pass a port:

```bash
python main.py --port 8000
```

## Notes

This project is a simulation and is intended for learning and demonstration purposes.
