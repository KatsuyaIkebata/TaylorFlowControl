class SyringePump:
    def __init__(self, pump_id):
        self.pump_id = pump_id

    def start(self):
        print(f"Syringe Pump {self.pump_id} started.")

    def stop(self):
        print(f"Syringe Pump {self.pump_id} stopped.")