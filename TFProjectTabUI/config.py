import common_delays as c

class Config:
    def __init__(self, config_data):
        self.tube_diameter = float(config_data.get("tube_diameter", 1.59))
        self.syringe_diameter = float(config_data.get("syringe_diameter", 35))
        self.max_vol = float(config_data.get("max_vol", 25))
        self.total_rate = float(config_data.get("total_rate", 10))
        self.total_time = float(config_data.get("total_time", 30))
        self.total_length = float(config_data.get("total_length", 1500))
        self.alarm_time = float(config_data.get("alarm_time", 3))
        self.slug_volume = list(map(float, config_data.get("slug_volume", [50, 50])))
        self.response_time = float(config_data.get("response_time", 0.1))
        self.gpio_pin = list(map(int, config_data.get("gpio_pin", [])))
        self.serial_port = list(config_data.get("serial_port", ['COM3', 'COM4']))
        self.baudrate = int(config_data.get("baudrate", 115200))
        self.delay = [
            list(map(float, delay))
            for delay in config_data.get("delay", [[0.0, 0.0] for _ in range(4)])
        ]
        self.pump_num = int(len(self.serial_port))
        self.valve_num = int(len(self.gpio_pin))
        c.delays = self.delay
