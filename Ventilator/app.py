from nicegui import ui
import plotly.graph_objects as go
from collections import deque

# Import our backend engines
from src.hardware import HardwareInterface
from src.patientEngine import PatientEngine
from src.ventilator import VentilatorEngine
from src.alarm import AlarmSystem
from src.logging import DataLogger

# ==========================================
# 1. INITIALIZATION & STATE
# ==========================================
# Force dark mode for a medical monitor look
ui.dark_mode().enable()

patient = PatientEngine("Adult")
ventilator = VentilatorEngine()
alarms = AlarmSystem()
csv_logger = DataLogger()

# Deques for chart history (last 100 ticks)
history = {
    "time": deque(maxlen=100),
    "pressure": deque(maxlen=100),
    "flow": deque(maxlen=100)
}

# Global state variables
app_state = {
    "is_running": False,
    "current_time": 0.0,
    "dt": 0.1,
    "hardware": HardwareInterface(
        mode="Ethernet UDP",
        serial_port="/tmp/ttyV0",  # Unique cable for the Ventilator
        ip="127.0.0.1", 
        net_port=8000              # Standardized network port for the Master Aggregator
    )
}


# ==========================================
# 2. UI UPDATE LOGIC (THE HEARTBEAT)
# ==========================================
def simulation_tick():
    if not app_state["is_running"]:
        return

    dt = app_state["dt"]

    # --- A. Advance Backend Physics ---
    current_vitals = patient.get_state()
    applied_flow = ventilator.step(dt, current_vitals)
    patient.update_physics(applied_flow, dt, ventilator.peep)

    phase = ventilator.breath_phase
    active_alarms = alarms.evaluate(dt, current_vitals, phase)

    csv_logger.log_step(
        current_time=app_state["current_time"],
        vent_mode=sel_mode.value,
        breath_phase=phase,
        applied_flow=applied_flow,
        patient_state=current_vitals,
        active_alarms=list(active_alarms)
    )

    # --- B. Update History ---
    app_state["current_time"] += dt
    history["time"].append(app_state["current_time"])
    history["pressure"].append(current_vitals["pressure"])
    history["flow"].append(current_vitals["flow"])

    # --- C. Update UI Text/Metrics ---
    if active_alarms:
        alarm_banner.text = "🚨 ALARMS: " + " | ".join(active_alarms)
        alarm_banner.classes(replace="text-red-500 font-bold text-xl tracking-wider")
    else:
        alarm_banner.text = "✅ SYSTEM NORMAL"
        alarm_banner.classes(replace="text-emerald-400 font-bold text-lg tracking-wider")

    # Update dynamic labels
    lbl_pressure.text = f"{current_vitals['pressure']:.1f} cmH2O"
    lbl_flow.text = f"{current_vitals['flow']:.2f} L/s"
    lbl_volume.text = f"{current_vitals['volume'] * 1000:.0f} mL"
    lbl_spo2.text = f"{current_vitals['spo2']:.1f} %"
    lbl_phase.text = f"Phase: {phase.upper()}"

    # --- D. Update Plotly Graph ---
    # Instead of redrawing the whole graph, we just update the data arrays
    fig.data[0].x = tuple(history["time"])
    fig.data[0].y = tuple(history["pressure"])
    fig.data[1].x = tuple(history["time"])
    fig.data[1].y = tuple(history["flow"])

    telemetry_packet = {
        "device_id": "VENT-PULMO-01",
        "time": round(app_state["current_time"], 1),
        "paw": round(current_vitals["pressure"], 1),
        "flow": round(current_vitals["flow"], 2),
        "vol": round(current_vitals["volume"] * 1000, 0),
        "alarms": list(active_alarms)
    }
    app_state["hardware"].send_data(telemetry_packet)

    # Push the new pixels to the browser
    graph.update()


# Run this function every 0.1 seconds (100ms)
ui.timer(app_state["dt"], simulation_tick)


# ==========================================
# 3. EVENT HANDLERS
# ==========================================
def toggle_simulation():
    app_state["is_running"] = not app_state["is_running"]
    btn_toggle.text = "⏸ STOP SIMULATION" if app_state["is_running"] else "▶ START SIMULATION"
    btn_toggle.classes(
        replace="bg-red-600 hover:bg-red-500" if app_state["is_running"] else "bg-emerald-600 hover:bg-emerald-500")


def apply_settings(e=None):
    ventilator.update_settings(
        mode=sel_mode.value,
        rr=sld_rr.value,
        peep=sld_peep.value,
        vt=sld_vt.value,
        target_pressure=sld_p.value,
        trigger_sensitivity=sld_trig.value
    )
    patient.fio2 = sld_fio2.value / 100.0
    patient.spont_rr = sld_spont_rr.value


def inject_scenario(scenario: str):
    patient.apply_intervention(scenario)


def change_hardware_port(e):
    selected_mode = e.value
    app_state["hardware"].configure(mode=selected_mode)
    ui.notify(f"Output switched to {selected_mode}", type="info")


# ==========================================
# 4. DASHBOARD LAYOUT
# ==========================================
# Global styling for a deep, modern dark mode
ui.query('body').classes('bg-[#0a0a0a]')

with ui.header().classes('bg-[#0f0f11] border-b border-gray-800 justify-between items-center p-4 shadow-md'):
    ui.label('🫁 Electronic Ventilator Simulator').classes('text-2xl font-bold text-gray-100')
    alarm_banner = ui.label('✅ SYSTEM NORMAL').classes('text-emerald-400 font-bold text-lg tracking-wider')

# SIDEBAR (Controls)
with ui.left_drawer(value=True).classes('bg-[#161618] border-r border-gray-800 p-5'):
    btn_toggle = ui.button('▶ START SIMULATION', on_click=toggle_simulation).classes(
        'w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold mb-6 transition-colors shadow-lg')

    ui.label("🎛️ Ventilator Settings").classes('text-sm font-bold text-blue-400 uppercase tracking-widest')
    sel_mode = ui.select(["VCV", "PCV"], value="VCV", on_change=apply_settings, label="Mode").classes('w-full mt-2')

    sld_rr = ui.slider(min=8, max=35, value=15, on_change=apply_settings).classes('w-full mt-4')
    ui.label().bind_text_from(sld_rr, 'value', backward=lambda v: f"Respiratory Rate: {v} bpm").classes(
        'text-gray-300 text-xs')

    sld_peep = ui.slider(min=0, max=20, value=5, on_change=apply_settings).classes('w-full mt-4')
    ui.label().bind_text_from(sld_peep, 'value', backward=lambda v: f"PEEP: {v} cmH2O").classes('text-gray-300 text-xs')

    sld_vt = ui.slider(min=0.2, max=0.8, step=0.01, value=0.5, on_change=apply_settings).classes('w-full mt-4')
    ui.label().bind_text_from(sld_vt, 'value', backward=lambda v: f"Tidal Volume: {v:.2f} L").classes(
        'text-gray-300 text-xs')

    sld_p = ui.slider(min=10, max=40, value=20, on_change=apply_settings).classes('w-full mt-4')
    ui.label().bind_text_from(sld_p, 'value', backward=lambda v: f"Target Pressure: {v} cmH2O").classes(
        'text-gray-300 text-xs')

    sld_fio2 = ui.slider(min=21, max=100, value=21, on_change=apply_settings).classes('w-full mt-4')
    ui.label().bind_text_from(sld_fio2, 'value', backward=lambda v: f"FiO2 (Oxygen): {v}%").classes(
        'text-gray-300 text-xs')

    ui.separator().classes('my-6 border-gray-800')

    ui.label("🧠 Patient Spontaneous Drive").classes('text-sm font-bold text-emerald-400 uppercase tracking-widest')
    sld_spont_rr = ui.slider(min=0, max=35, value=12, on_change=apply_settings).classes('w-full mt-2')
    ui.label().bind_text_from(sld_spont_rr, 'value', backward=lambda v: f"Patient Effort: {v} breaths/min").classes(
        'text-gray-300 text-xs')

    ui.label("⚙️ Ventilator Trigger Sensitivity").classes(
        'text-sm font-bold text-purple-400 uppercase tracking-widest mt-6')
    sld_trig = ui.slider(min=0.5, max=10.0, step=0.5, value=2.0, on_change=apply_settings).classes('w-full mt-2')
    ui.label().bind_text_from(sld_trig, 'value', backward=lambda v: f"Sensitivity: -{v} cmH2O").classes(
        'text-gray-300 text-xs')

    ui.separator().classes('my-6 border-gray-800')

    ui.label("💉 Patient Scenarios").classes('text-sm font-bold text-red-400 uppercase tracking-widest mb-3')
    ui.button("Normal (Reset)", on_click=lambda: inject_scenario("reset")).classes(
        'w-full mb-2 bg-gray-700 hover:bg-gray-600')
    ui.button("Trigger Bronchospasm", on_click=lambda: inject_scenario("bronchospasm")).classes(
        'w-full mb-2 bg-amber-700 hover:bg-amber-600 text-white')
    ui.button("Give Albuterol", on_click=lambda: inject_scenario("albuterol")).classes(
        'w-full mb-2 bg-cyan-700 hover:bg-cyan-600 text-white')
    ui.button("Trigger ARDS", on_click=lambda: inject_scenario("ards")).classes(
        'w-full mb-2 bg-purple-700 hover:bg-purple-600 text-white')

    ui.separator().classes('my-6 border-gray-800')

    ui.label("🔌 Hardware Output").classes('text-sm font-bold text-gray-500 uppercase tracking-widest mb-2')
    sel_hw = ui.select(
        ["RS232", "Ethernet UDP", "Ethernet TCP"],
        value="RS232",
        on_change=change_hardware_port
    ).classes('w-full mb-4')

# MAIN AREA (Metrics & Graphs)
with ui.column().classes('w-full max-w-7xl mx-auto p-6'):
    # KPI Row
    with ui.row().classes('w-full justify-between gap-4 mb-6'):
        with ui.card().classes('flex-1 bg-[#1c1c1e] border border-gray-800 items-center p-5 shadow-lg rounded-xl'):
            ui.label("PEAK PRESSURE").classes('text-gray-400 text-xs font-bold uppercase tracking-widest')
            lbl_pressure = ui.label("0.0 cmH2O").classes('text-4xl font-mono font-bold text-amber-400 mt-2')
            lbl_phase = ui.label("Phase: EXPIRATION").classes('text-xs text-gray-500 mt-2 font-mono')

        with ui.card().classes('flex-1 bg-[#1c1c1e] border border-gray-800 items-center p-5 shadow-lg rounded-xl'):
            ui.label("CURRENT FLOW").classes('text-gray-400 text-xs font-bold uppercase tracking-widest')
            lbl_flow = ui.label("0.00 L/s").classes('text-4xl font-mono font-bold text-cyan-400 mt-2')

        with ui.card().classes('flex-1 bg-[#1c1c1e] border border-gray-800 items-center p-5 shadow-lg rounded-xl'):
            ui.label("CURRENT VOLUME").classes('text-gray-400 text-xs font-bold uppercase tracking-widest')
            lbl_volume = ui.label("0 mL").classes('text-4xl font-mono font-bold text-violet-400 mt-2')

        with ui.card().classes('flex-1 bg-[#1c1c1e] border border-gray-800 items-center p-5 shadow-lg rounded-xl'):
            ui.label("SpO2").classes('text-gray-400 text-xs font-bold uppercase tracking-widest')
            lbl_spo2 = ui.label("98.0 %").classes('text-4xl font-mono font-bold text-emerald-400 mt-2')

    # Plotly Graph Setup
    fig = go.Figure()
    # Using specific hex colors to match the KPI cards
    fig.add_trace(
        go.Scatter(x=[], y=[], mode='lines', name='Pressure (cmH2O)', line=dict(color='#fbbf24', width=2.5)))  # Amber
    fig.add_trace(
        go.Scatter(x=[], y=[], mode='lines', name='Flow (L/s)', line=dict(color='#22d3ee', width=2.5)))  # Cyan

    fig.update_layout(
        height=550, margin=dict(l=40, r=20, t=40, b=30),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Time (seconds)", showgrid=True, gridcolor='#333333', zerolinecolor='#444444'),
        yaxis=dict(title="Measurements", showgrid=True, gridcolor='#333333', zerolinecolor='#444444'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#cccccc"))
    )

    with ui.card().classes('w-full bg-[#1c1c1e] border border-gray-800 rounded-xl shadow-lg p-2'):
        graph = ui.plotly(fig).classes('w-full')

# ==========================================
# 5. EXECUTE APP
# ==========================================
# This starts the local server and opens your browser
ui.run(title="ICU Ventilator Sim", port=8080, dark=True)
