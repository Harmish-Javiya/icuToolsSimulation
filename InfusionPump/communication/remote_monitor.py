from tcp_client import TCPClient


client = TCPClient(
    "192.168.56.1"
)

while True:

    data = client.receive()

    print(data)