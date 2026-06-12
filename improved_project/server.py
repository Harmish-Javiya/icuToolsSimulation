import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


class SimulatorHTTPServer:
    def __init__(self, simulator, host="0.0.0.0", port=8000):
        self.simulator = simulator
        self.host = host
        self.port = port
        self.httpd = None
        self.thread = None

    def start(self):
        if self.httpd is not None:
            return True

        try:
            self.httpd = ThreadingHTTPServer((self.host, self.port), self._build_handler())
        except OSError as exc:
            raise RuntimeError(f"Unable to start API server on port {self.port}: {exc}") from exc

        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        self.thread = None

    def _build_handler(self):
        simulator = self.simulator
        port = self.port

        class Handler(BaseHTTPRequestHandler):
            def _send_json(self, payload, status=200):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _read_json(self):
                content_length = int(self.headers.get("Content-Length", "0"))
                if content_length <= 0:
                    return {}
                body = self.rfile.read(content_length).decode("utf-8")
                try:
                    return json.loads(body) or {}
                except json.JSONDecodeError:
                    return {}

            def do_GET(self):
                parsed = urlparse(self.path)
                path = parsed.path

                if path == "/health":
                    self._send_json({"status": "ok", "port": port})
                    return

                if path == "/status":
                    self._send_json(simulator.status())
                    return

                if path == "/events":
                    self._send_json({"events": simulator.events})
                    return

                self._send_json({"error": "Not found"}, 404)

            def do_POST(self):
                parsed = urlparse(self.path)
                path = parsed.path
                data = self._read_json()

                if path == "/charge":
                    simulator.charge()
                    simulator.add_event("Charge command issued over API")
                    self._send_json({"ok": True, "status": simulator.status()})
                    return

                if path == "/shock":
                    success = simulator.shock()
                    simulator.add_event("Shock command issued over API")
                    self._send_json({"ok": success, "status": simulator.status()})
                    return

                if path == "/disarm":
                    simulator.disarm()
                    simulator.add_event("Disarm command issued over API")
                    self._send_json({"ok": True, "status": simulator.status()})
                    return

                if path == "/recharge":
                    simulator.recharge()
                    simulator.add_event("Recharge command issued over API")
                    self._send_json({"ok": True, "status": simulator.status()})
                    return

                if path == "/ecg":
                    sample = simulator.ecg_sample()
                    self._send_json({"ok": True, "sample": round(sample, 3)})
                    return

                if path == "/rhythm":
                    rhythm_name = data.get("rhythm")
                    if rhythm_name:
                        from src.patient import Rhythm

                        for rhythm in Rhythm:
                            if rhythm.value == rhythm_name:
                                simulator.patient.set_rhythm(rhythm)
                                simulator.update()
                                simulator.add_event(f"Rhythm changed to {rhythm_name} over API")
                                self._send_json({"ok": True, "status": simulator.status()})
                                return
                    self._send_json({"ok": False, "error": "Invalid rhythm"}, 400)
                    return

                if path == "/mode":
                    mode_name = data.get("mode")
                    if mode_name:
                        from src.device import Mode

                        for mode in Mode:
                            if mode.value == mode_name:
                                simulator.device.set_mode(mode)
                                simulator.update()
                                simulator.add_event(f"Mode changed to {mode_name} over API")
                                self._send_json({"ok": True, "status": simulator.status()})
                                return
                    self._send_json({"ok": False, "error": "Invalid mode"}, 400)
                    return

                self._send_json({"error": "Not found"}, 404)

            def log_message(self, format, *args):
                return

        return Handler
