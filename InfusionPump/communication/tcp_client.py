import socket
import json


class TCPClient:

    def __init__(
            self,
            host):

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.client.connect(
            (host, 5000)
        )

    def receive(self):

        data = self.client.recv(
            4096
        )

        return json.loads(
            data.decode()
        )