class Pump:
    def __init__(self, id):
        self.id = id

    def infuse(self):
        print(f"Infusing from pump {self.id}")

    def stop(self):
        print(f"Stopping pump {self.id}")
