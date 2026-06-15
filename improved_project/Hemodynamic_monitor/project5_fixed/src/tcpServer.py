import socket
import threading


class TCPServer:
    """
    Sends hemodynamic data over UDP broadcast on port 5000.
    UDP requires no client handshake — the sender is always "online"
    the moment the socket is bound, so the UI shows Online immediately.
    Any listener on the same network (or localhost) can receive packets.
    """

    def __init__(self):

        self.host = "127.0.0.1"
        self.port = 5000

        self.running = False
        self.connected = False
        self._sock = None

    def start(self):
        """Open the UDP socket once — no blocking accept() needed."""
        try:
            self._sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM  # UDP — no connection required
            )
            # Allow sending to broadcast address if needed later
            self._sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_BROADCAST,
                1
            )
            self.running = True
            self.connected = True   # UDP is always ready to send
        except Exception as e:
            print(f"[TCPServer] Failed to open UDP socket: {e}")
            self.connected = False

    def send(self, data):
        """Send a UDP datagram. Non-blocking — drops packet silently on error."""
        if self._sock and self.running:
            try:
                self._sock.sendto(
                    (data + "\n").encode(),
                    (self.host, self.port)
                )
                self.connected = True
            except Exception as e:
                print(f"[TCPServer] Send error: {e}")
                self.connected = False

    def is_connected(self):
        return self.connected

    def stop(self):
        self.running = False
        self.connected = False
        if self._sock:
            self._sock.close()
            self._sock = None
