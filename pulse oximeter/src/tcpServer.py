import socket
import threading


class TCPServer:

    def __init__(self,
                 host="0.0.0.0",
                 port=5000):

        self.host = host
        self.port = port

        self.client = None

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind(
            (self.host, self.port)
        )

        self.server.listen(1)

        thread = threading.Thread(
            target=self.accept_client,
            daemon=True
        )

        thread.start()

    def accept_client(self):

        while True:

            client, address = self.server.accept()

            print(
                "TCP Client Connected:",
                address
            )

            self.client = client

    def send(self, data):

        if self.client is None:
            return

        try:

            msg = (
                f"SPO2={data['spo2']},"
                f"HR={data['heart_rate']},"
                f"TEMP={data['temperature']},"
                f"BAT={data['battery']},"
                f"SIGNAL={data['signal_quality']},"
                f"SENSOR={data['sensor_connected']}\n"
            )

            self.client.sendall(
                msg.encode()
            )

        except:

            self.client = None