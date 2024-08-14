class Valve:
    def __init__(self, id):
        self.id = id

    def open(self):
        print(f"Opening valve {self.id}")

    def close(self):
        print(f"Closing valve {self.id}")
