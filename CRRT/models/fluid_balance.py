class FluidBalance:

    def __init__(self):

        self.intake = 0.0
        self.output = 0.0

    def add_intake(self, amount):

        self.intake += amount

    def add_output(self, amount):

        self.output += amount

    def get_net_balance(self):

        return self.intake - self.output

    def get_data(self):

        return {
            "Intake (mL)": self.intake,
            "Output (mL)": self.output,
            "Net Balance (mL)": self.get_net_balance()
        }