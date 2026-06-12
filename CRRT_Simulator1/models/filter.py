import random


class Filter:

    def __init__(self):

        self.health = 100.0

        self.clotting_rate = 0.1

        self.status = "Healthy"

    def update(self):

        # Simulate gradual filter wear

        self.health -= random.uniform(
            self.clotting_rate,
            self.clotting_rate + 0.2
        )

        self.health = max(0, self.health)

        self.update_status()

    def update_status(self):

        if self.health >= 70:
            self.status = "Healthy"

        elif self.health >= 40:
            self.status = "Warning"

        elif self.health >= 10:
            self.status = "Critical"

        else:
            self.status = "Replace Filter"

    def replace_filter(self):

        self.health = 100.0

        self.status = "Healthy"

        print("Filter Replaced Successfully")

    def get_filter_data(self):

        return {
            "Health (%)":
                round(self.health, 2),

            "Status":
                self.status
        }