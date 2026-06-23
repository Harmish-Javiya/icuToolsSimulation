class Calculator:

    @staticmethod
    def calculate_infused_volume(flow_rate, dt=1):
        """
        flow_rate: mL/hr
        dt: seconds
        """
        return flow_rate * dt / 3600

    @staticmethod
    def calculate_remaining_volume(vtbi, infused):
        return max(0, vtbi - infused)

    @staticmethod
    def calculate_completion(infused, vtbi):
        return infused >= vtbi