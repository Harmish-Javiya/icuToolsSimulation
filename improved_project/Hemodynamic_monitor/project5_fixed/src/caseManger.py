import json


class CaseManager:

    def load_case(self, filename):

        with open(filename, "r") as f:

            return json.load(f)