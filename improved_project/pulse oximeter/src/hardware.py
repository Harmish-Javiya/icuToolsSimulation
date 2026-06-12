import json

class Hardware:

    def send(self, data):

        packet = json.dumps(data)

        print(packet)