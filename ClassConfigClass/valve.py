import RPi.GPIO as GPIO

class ValveClass:
    def __init__(self, id, gpio_pin):
        self.id = id       
        self.pin = gpio_pin       
        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.pin, GPIO.OUT)  # GPIOピンを出力モードに設定

    def open(self, Operation):
        print(f"Opening valve {self.id}")

    def close(self):
        print(f"Closing valve {self.id}")

    def end(self, Operation):
        self.open(Operation)
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup()