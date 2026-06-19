import sys
from pathlib import Path

# ==========================================
# 0. CRITICAL PATH INJECTION
# ==========================================
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from nicegui import ui
import plotly.graph_objects as go
from collections import deque
from datetime import datetime
import logging

# Configure terminal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import the standalone backend modules
from src.icpEngine import ICPEngine
from src.icpAlarm import ICPAlarmSystem
from src.hardwareEngine import HardwareInterface
from src.icpLogging import DataLogger, logger

# ==========================================
# 1. STATE & INITIALIZATION
# ==========================================
ui.dark_mode().enable()

# Initialize the Microservice Backend
icp = ICPEngine(base_icp=10.0)
alarm_sys = ICPAlarmSystem()
csv_logger = DataLogger()

hardware = HardwareInterface(mode="Ethernet UDP", serial_port="/tmp/ttyV1", ip="127.0.0.1", net_port=8000)

app_state = {
    "is_running": False,
    "current_time": 0.0,
    "dt": 0.05,
    "active_status": "NORMAL COMPLIANCE"
}

# Dedicated queue for the single high-res brain wave
history = {
    "time": deque(maxlen=200),
    "waveform": deque(maxlen=200)
}


# ==========================================
# 2. UI UPDATE LOGIC & TELEMETRY
# ==========================================
def simulation_tick():
    if not app_state["is_running"]: return

    app_state["current_time"] += app_state["dt"]

    # Step the Neuro Engine
    neuro_data = icp.step(app_state["dt"])

    # Evaluate Alarms
    active_alarms = alarm_sys.evaluate(neuro_data["mean_icp"], neuro_data["simulated_hr"])

    # Update Arrays
    history["time"].append(app_state["current_time"])
    history["waveform"].append(neuro_data["waveform"])

    # Update UI KPIs
    lbl_icp.text = f"{neuro_data['mean_icp']:.0f}"
    lbl_hr.text = f"{neuro_data['simulated_hr']:.0f}"

    # Dynamic Color Logic for the UI
    if neuro_data["mean_icp"] >= 20.0:
        lbl_icp.classes(
            replace='text-[6rem] font-mono text-red-500 leading-none drop-shadow-[0_0_20px_rgba(239,68,68,0.6)] animate-pulse')
    elif neuro_data["mean_icp"] >= 15.0:
        lbl_icp.classes(
            replace='text-[6rem] font-mono text-yellow-500 leading-none drop-shadow-[0_0_20px_rgba(234,179,8,0.4)]')
    else:
        lbl_icp.classes(
            replace='text-[6rem] font-mono text-cyan-400 leading-none drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]')

    if active_alarms:
        lbl_alarm.text = " | ".join(active_alarms)
        lbl_alarm.classes(replace='text-red-500 font-bold tracking-widest text-sm animate-pulse')
    else:
        lbl_alarm.text = "NEUROLOGY STABLE"
        lbl_alarm.classes(replace='text-cyan-500 font-bold tracking-widest text-sm')

    # Transmit Standalone Telemetry Payload
    telemetry_payload = {
        "device_id": "ICP-NEURO-01",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mean_icp": neuro_data["mean_icp"],
        "simulated_hr": neuro_data["simulated_hr"],
        "waveform_val": neuro_data["waveform"],
        "status": app_state["active_status"],
        "alarms": active_alarms
    }
    hardware.send_data(telemetry_payload)

    # Log the data locally
    csv_logger.log_step(app_state["current_time"], neuro_data["simulated_hr"], neuro_data["mean_icp"],
                        neuro_data["waveform"], app_state["active_status"], active_alarms)

    # Update the High-Res Plotly Trace
    fig.data[0].x = tuple(history["time"])
    fig.data[0].y = tuple(history["waveform"])
    graph.update()


ui.timer(app_state["dt"], simulation_tick)


# ==========================================
# 3. EVENT HANDLERS
# ==========================================
def toggle_simulation():
    app_state["is_running"] = not app_state["is_running"]
    btn_toggle.text = "⏸ PAUSE" if app_state["is_running"] else "▶ START"
    btn_toggle.classes(replace="bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/30" if app_state[
        "is_running"] else "bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-500/30")


def update_manual_controls(e=None):
    """Pushes slider values directly into the physics engine."""
    icp.set_targets(slider_icp.value, slider_hr.value)
    app_state["active_status"] = "MANUAL OVERRIDE"
    lbl_status.text = "MANUAL OVERRIDE"


def inject_scenario(scenario: str, label: str):
    icp.apply_intervention(scenario)
    app_state["active_status"] = label
    lbl_status.text = label

    # Sync the UI sliders to match the newly injected scenario
    slider_icp.value = icp.target_icp
    slider_hr.value = icp.target_hr


def update_telemetry_mode(e):
    """Dynamically routes the outbound telemetry data."""
    hardware.configure(mode=e.value)
    logger.info(f"Telemetry output routed to: {e.value}")


# ==========================================
# 4. DASHBOARD LAYOUT (NEURO-ICU UI)
# ==========================================
ui.query('body').classes('bg-[#030303] text-gray-100 font-sans selection:bg-cyan-500/30')

with ui.header().classes('bg-[#0a0a0c] border-b border-gray-800/60 p-4 shadow-md justify-between items-center'):
    ui.label('DEDICATED INTRACRANIAL MONITOR').classes('text-xl font-bold tracking-[0.25em] text-cyan-400')
    lbl_alarm = ui.label('NEUROLOGY STABLE').classes('text-cyan-500 font-bold tracking-widest text-sm')

with ui.row().classes('w-full max-w-[1800px] mx-auto p-6 gap-6'):
    # LEFT PANEL (KPIs & Telemetry)
    with ui.column().classes('w-80 gap-6'):
        btn_toggle = ui.button('▶ START', on_click=toggle_simulation).classes(
            'w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-4 rounded-xl tracking-[0.2em] transition-all shadow-lg shadow-cyan-500/30')

        # TELEMETRY ROUTING CARD
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-4 rounded-2xl shadow-xl'):
            ui.label("TELEMETRY ROUTING").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-2')
            ui.toggle(["RS232", "Ethernet UDP", "Ethernet TCP"], value="RS232", on_change=update_telemetry_mode).classes(
                'w-full shadow-none')

        # MAIN ICP CARD
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("INTRACRANIAL PRESSURE").classes(
                'text-cyan-500/70 text-[10px] font-bold uppercase tracking-[0.2em] mb-2')
            with ui.row().classes('items-baseline gap-2 mb-2'):
                lbl_icp = ui.label("10").classes(
                    'text-[6rem] font-mono text-cyan-400 leading-none drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]')
                ui.label("mmHg").classes('text-gray-500 text-sm font-bold tracking-wider')

            ui.separator().classes('my-4 border-gray-800/50')
            ui.label("CLINICAL STATUS").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em]')
            lbl_status = ui.label(app_state["active_status"]).classes(
                'text-sm text-cyan-400 font-mono tracking-widest mt-2')

        # SECONDARY PULSE CARD
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-4 rounded-2xl shadow-xl'):
            ui.label("SIMULATED PULSE").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-1')
            with ui.row().classes('items-baseline gap-2'):
                lbl_hr = ui.label("75").classes('text-3xl font-mono text-emerald-500 leading-none')
                ui.label("BPM").classes('text-gray-600 text-xs font-bold tracking-wider')

    # CENTER PANEL (High-Resolution Single Waveform)
    with ui.column().classes('flex-1'):
        fig = go.Figure()

        # Single, prominent trace for the brain wave
        fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='ICP Waveform', line=dict(color='#22d3ee', width=3),
                                 fill='tozeroy', fillcolor='rgba(34,211,238,0.05)'))

        fig.update_layout(
            height=800,
            margin=dict(l=40, r=20, t=40, b=40),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor='#17171a', zeroline=False, showticklabels=False, title="Time"),
            yaxis=dict(range=[0, 50], showgrid=True, gridcolor='#17171a', zeroline=False, title="Pressure (mmHg)",
                       title_font=dict(color="#555", size=12), tickfont=dict(color="#555")),
            showlegend=False,
            hovermode=False
        )

        with ui.card().classes('w-full h-full bg-[#0c0c0e] border border-gray-800/40 rounded-2xl p-1 shadow-2xl'):
            graph = ui.plotly(fig).classes('w-full h-full')

    # RIGHT PANEL (Controls & Scenarios)
    with ui.column().classes('w-80 gap-6'):
        # MANUAL OVERRIDE SLIDERS
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("MANUAL OVERRIDE").classes('text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-4')

            ui.label("TARGET ICP (mmHg)").classes('text-cyan-500/70 text-xs font-bold mb-1')
            slider_icp = ui.slider(min=5, max=50, value=10, on_change=update_manual_controls).classes(
                'w-full mb-4').props('color="cyan"')

            ui.label("TARGET HEART RATE (BPM)").classes('text-emerald-500/70 text-xs font-bold mb-1')
            slider_hr = ui.slider(min=30, max=160, value=75, on_change=update_manual_controls).classes('w-full').props(
                'color="green"')

        # SCENARIO INJECTION
        with ui.card().classes('w-full bg-[#0c0c0e] border border-gray-800/40 p-6 rounded-2xl shadow-xl'):
            ui.label("NEUROLOGIC EVENTS").classes(
                'text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em] mb-4')
            btn_classes = 'w-full mb-2 bg-[#131316] border border-gray-700/50 hover:bg-[#1a1a1e] text-gray-300 text-xs tracking-wider transition-all rounded-lg py-3'

            ui.button("NORMAL COMPLIANCE",
                      on_click=lambda: inject_scenario("normal_neuro", "NORMAL COMPLIANCE")).classes(btn_classes)
            ui.button("EARLY SWELLING",
                      on_click=lambda: inject_scenario("mild_swelling", "ELEVATED ICP DETECTED")).classes(
                btn_classes)

            ui.label("EMERGENCY TREATMENTS").classes(
                'text-emerald-500/70 text-[10px] font-bold uppercase tracking-[0.2em] mt-4 mb-2')
            treat_classes = 'w-full mb-2 bg-emerald-950/20 border border-emerald-900/50 hover:bg-emerald-900/40 text-emerald-400 text-xs tracking-wider transition-all rounded-lg py-3'

            ui.button("DRAIN CSF FLUID",
                      on_click=lambda: inject_scenario("treatment_drain_csf", "VENTRICULAR DRAIN OPEN")).classes(
                treat_classes)
            ui.button("PUSH IV MANNITOL",
                      on_click=lambda: inject_scenario("treatment_mannitol", "OSMOTIC DIURESIS ACTIVE")).classes(
                treat_classes)
            ui.button("HYPERVENTILATE", on_click=lambda: inject_scenario("treatment_hyperventilation",
                                                                         "THERAPEUTIC VASOCONSTRICTION")).classes(
                treat_classes)

            ui.separator().classes('my-2 border-gray-800/50')

            ui.button("MASSIVE BRAIN SWELLING", on_click=lambda: inject_scenario("brain_swelling",
                                                                                 "SEVERE INTRACRANIAL HYPERTENSION")).classes(
                'w-full mt-2 bg-red-950/20 border border-red-900/50 hover:bg-red-900/40 text-red-400 text-xs tracking-wider transition-all rounded-lg py-3')

ui.run(title="ICP Simulator", port=8081, dark=True)
