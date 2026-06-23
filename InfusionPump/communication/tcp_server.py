import socket
import json


class TCPServer:

    def __init__(self):

        self.host = "0.0.0.0"
        self.port = 5000

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.bind(
            (self.host, self.port)
        )

        self.server.listen(1)

        self.client = None

    def wait_for_client(self):

        print(
            "Waiting for connection..."
        )

        self.client, address = (
            self.server.accept()
        )

        print(
            f"Connected: {address}"
        )

    def send_data(self, data):

        if self.client:

            message = json.dumps(
                data
            ).encode()

            self.client.send(
                message
            )