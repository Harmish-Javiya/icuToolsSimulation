from nicegui import ui
import plotly.graph_objects as go
from collections import deque
from datetime import datetime

# Import all backend modules
from src.ecgEngine import ECGEngine
from src.ecgHardware import HardwareInterface
from src.ecgAlarm import CardiacAlarmSystem
from src.ecgLogging import DataLogger

# ==========================================
# 1. STATE & INITIALIZATION
# ==========================================
ui.dark_mode().enable()

ecg = ECGEngine(heart_rate=75.0)
hardware = HardwareInterface(mode="RS232", serial_port="/tmp/ttyV0", baudrate=9600)
alarm_sys = CardiacAlarmSystem()
csv_logger = DataLogger()

ALL_LEADS = [
    "Lead I", "Lead II", "Lead III",
    "Lead aVR", "Lead aVL", "Lead aVF",
    "Lead V1", "Lead V2", "Lead V3", "Lead V4", "Lead V5", "Lead V6"
]

app_state = {
    "is_running": False,
    "current_time": 0.0,
    "dt": 0.05,
    "active_rhythm": "NORMAL SINUS RHYTHM",
    "channels": ["Lead II", "Lead V1", "Lead V6", "Lead aVR"]
}

history = {
    "time": deque(maxlen=250),
    "ch0": deque(maxlen=250),
    "ch1": deque(maxlen=250),
    "ch2": deque(maxlen=250),
    "ch3": deque(maxlen=250)
}

# List to hold the UI dropdown elements for dynamic updating
dropdown_elements = []


# ==========================================
# 2. UI UPDATE LOGIC & TELEMETRY
# ==========================================
def simulation_tick():
    if not app_state["is_running"]: return

    app_state["current_time"] += app_state["dt"]
    leads_to_track = app_state["channels"]

    # Step the physics engine
    vitals = ecg.step(app_state["dt"], leads_to_track)

    # Evaluate Alarms
    active_alarms = alarm_sys.evaluate(app_state["dt"], vitals["hr"], app_state["active_rhythm"])

    # Update arrays
    history["time"].append(app_state["current_time"])
    history["ch0"].append(vitals["voltages"][app_state["channels"][0]])
    history["ch1"].append(vitals["voltages"][app_state["channels"][1]])
    history["ch2"].append(vitals["voltages"][app_state["channels"][2]])
    history["ch3"].append(vitals["voltages"][app_state["channels"][3]])

    # Update UI KPIs
    lbl_hr.text = f"{vitals['hr']:.0f}"

    if active_alarms:
        lbl_alarm.text = " | ".join(active_alarms)
        lbl_alarm.classes(replace='text-red-500 font-bold tracking-widest text-sm animate-pulse')
    else:
        lbl_alarm.text = "SYSTEM STABLE"
        lbl_alarm.classes(replace='text-emerald-500 font-bold tracking-widest text-sm')

    # Log & Transmit Data
    csv_logger.log_step(app_state["current_time"], vitals["hr"], vitals["voltages"], app_state["active_rhythm"],
                        active_alarms)

    telemetry_payload = {
        "device_id": "ICU-BED-04",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "heart_rate": vitals["hr"],
        "voltages": vitals["voltages"],
        "rhythm_status": app_state["active_rhythm"],
        "alarms": active_alarms
    }
    hardware.send_data(telemetry_payload)

    # Update Plotly traces (Mathematical offsets for vertical stacking)
    fig.data[0].x = tuple(history["time"])
    fig.data[0].y = tuple([v + 6 for v in history["ch0"]])

    fig.data[1].x = tuple(history["time"])
    fig.data[1].y = tuple([v + 2 for v in history["ch1"]])

    fig.data[2].x = tuple(history["time"])
    fig.data[2].y = tuple([v - 2 for v in history["ch2"]])

    fig.data[3].x = tuple(history["time"])
    fig.data[3].y = tuple([v - 6 for v in history["ch3"]])

    graph.update()


ui.timer(app_state["dt"], simulation_tick)


# ==========================================
# 3. EVENT HANDLERS
# ==========================================
def toggle_simulation():
    app_state["is_running"] = not app_state["is_running"]
    btn_toggle.text = "⏸ PAUSE" if app_state["is_running"] else "▶ START"
    btn_toggle.classes(replace="bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/30" if app_state[
        "is_running"] else "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/30")


def inject_scenario(scenario: str, label: str):
    ecg.apply_intervention(scenario)
    app_state["active_rhythm"] = label
    lbl_rhythm.text = label


def refresh_dropdowns():
    """Updates all dropdowns to only show leads that are not currently in use."""
    for i, dropdown in enumerate(dropdown_elements):
        available = [lead for lead in ALL_LEADS if
                     lead not in app_state["channels"] or lead == app_state["channels"][i]]
        dropdown.options = available
        dropdown.update()


def change_channel(slot_index: int, e):
    """Hot-swaps a graph trace to a new lead and updates menus."""
    new_lead = e.value
    if new_lead == app_state["channels"][slot_index] or new_lead is None:
        return

    app_state["channels"][slot_index] = new_lead
    history[f"ch{slot_index}"].clear()
    fig.data[slot_index].name = new_lead
    graph.update()
    refresh_dropdowns()


# ==========================================
# 4. DASHBOARD LAYOUT (HIGH-END CLINICAL UI)
# ==========================================
ui.query('body').classes('bg-[#030303] text-gray-100 font-sans selection:bg-cyan-500/30')

with ui.header().classes('bg-[#0a0a0c] border-b border-gray-800/60 p-4 shadow-md justify-between items-center'):
    ui.label('CENTRAL TELEMETRY STATION').classes('text-xl font-bold tracking-[0.25em] text-cyan-400')
    lbl_alarm = ui.label('SYSTEM STABLE').classes('text-emerald-500 font-bold tracking-widest text-sm')

with ui.row().classes('w-full max-w-[1800px] mx-auto p-6 gap-6'):
    # LEFT PANEL (Controls & Scenarios)
    with ui.column().classes('w-80 gap-6'):
        btn_toggle = ui.button('▶ START', on_click=toggle_simulation).classes(
            'w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl tracking-[0.2em] transition-all shadow-lg shadow-emerald-500/30')

        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("HEART RATE").classes('text-emerald-500/70 text-[10px] font-bold uppercase tracking-[0.2em] mb-2')
            with ui.row().classes('items-baseline gap-2 mb-4'):
                lbl_hr = ui.label("75").classes(
                    'text-[5rem] font-mono text-emerald-400 leading-none drop-shadow-[0_0_15px_rgba(52,211,153,0.3)]')
                ui.label("BPM").classes('text-gray-500 text-sm font-bold tracking-wider')

            ui.separator().classes('my-4 border-gray-800/50')
            ui.label("CURRENT RHYTHM").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em]')
            lbl_rhythm = ui.label(app_state["active_rhythm"]).classes(
                'text-sm text-cyan-400 font-mono tracking-widest mt-2')

        # Dynamic Channel Configuration Card
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("GRAPH ROUTING").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-4')

            dropdown_elements.clear()
            dropdown_elements.append(ui.select(ALL_LEADS, value=app_state["channels"][0], label="Slot 1 (Top)",
                                               on_change=lambda e: change_channel(0, e)).classes('w-full mb-2'))
            dropdown_elements.append(ui.select(ALL_LEADS, value=app_state["channels"][1], label="Slot 2",
                                               on_change=lambda e: change_channel(1, e)).classes('w-full mb-2'))
            dropdown_elements.append(ui.select(ALL_LEADS, value=app_state["channels"][2], label="Slot 3",
                                               on_change=lambda e: change_channel(2, e)).classes('w-full mb-2'))
            dropdown_elements.append(ui.select(ALL_LEADS, value=app_state["channels"][3], label="Slot 4 (Bottom)",
                                               on_change=lambda e: change_channel(3, e)).classes('w-full'))

            refresh_dropdowns()

        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("CLINICAL SCENARIOS").classes(
                'text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-4')

            btn_classes = 'w-full mb-3 bg-[#131316] border border-gray-700/50 hover:bg-[#1a1a1e] text-gray-300 text-xs tracking-wider transition-all rounded-lg py-3'
            ui.button("NORMAL SINUS RHYTHM", on_click=lambda: inject_scenario("reset", "NORMAL SINUS RHYTHM")).classes(
                btn_classes)
            ui.button("V-TACH (Fast)",
                      on_click=lambda: inject_scenario("tachycardia", "VENTRICULAR TACHYCARDIA")).classes(btn_classes)
            ui.button("BRADYCARDIA (Slow)",
                      on_click=lambda: inject_scenario("bradycardia", "SEVERE BRADYCARDIA")).classes(btn_classes)
            ui.button("ASYSTOLE (Flatline)", on_click=lambda: inject_scenario("asystole", "ASYSTOLE")).classes(
                'w-full mt-2 bg-red-950/20 border border-red-900/50 hover:bg-red-900/40 text-red-400 text-xs tracking-wider transition-all rounded-lg py-3')

    # RIGHT PANEL (4-Channel Staked ECG Graphs)
    with ui.column().classes('flex-1'):
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=[], y=[], mode='lines', name=app_state["channels"][0], line=dict(color='#10b981', width=2)))
        fig.add_trace(
            go.Scatter(x=[], y=[], mode='lines', name=app_state["channels"][1], line=dict(color='#0ea5e9', width=2)))
        fig.add_trace(
            go.Scatter(x=[], y=[], mode='lines', name=app_state["channels"][2], line=dict(color='#a855f7', width=2)))
        fig.add_trace(
            go.Scatter(x=[], y=[], mode='lines', name=app_state["channels"][3], line=dict(color='#f59e0b', width=2)))

        fig.update_layout(
            height=850,
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor='#17171a', zeroline=False, showticklabels=False),
            yaxis=dict(range=[-10, 10], showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color="#888", size=13),
                bgcolor="rgba(0,0,0,0)"
            ),
            hovermode=False
        )

        with ui.card().classes('w-full h-full bg-[#0c0c0e] border border-gray-800/40 rounded-2xl p-1 shadow-2xl'):
            graph = ui.plotly(fig).classes('w-full h-full')

ui.run(title="4-Channel ECG Monitor", port=8001, dark=True)