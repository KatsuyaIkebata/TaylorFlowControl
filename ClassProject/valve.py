class Valve:
    def __init__(self, valve_id):
        self.valve_id = valve_id

    def open(self):
        print(f"Valve {self.valve_id} opened.")

    def close(self):
        print(f"Valve {self.valve_id} closed.")