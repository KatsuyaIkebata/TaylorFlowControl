class OperationManager:
    def __init__(self):
        self.pumps = [SyringePump(i) for i in range(2)]
        self.valves = [Valve(i) for i in range(4)]

    def start_operation(self):
        thread = Thread(target=self.run_operation)
        thread.start()

    def run_operation(self):
        for pump in self.pumps:
            pump.start()
        for valve in self.valves:
            valve.open()
        for valve in self.valves:
            valve.close()
        for pump in self.pumps:
            pump.stop()