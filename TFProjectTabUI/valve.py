try: 
    import RPi.GPIO as GPIO
    # print("import gpio successed")
except:
    import fakeRPiGPIO as GPIO
from write_csv import CSVClass

class ValveClass:
    def __init__(self, id, gpio_pin):
        self.id = id       
        self.pin = gpio_pin  
        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.pin, GPIO.OUT)  # GPIOピンを出力モードに設定

    def open(self, Operation):
        GPIO.output(self.pin, GPIO.LOW)
        Operation.logCSV(f'valve {self.id}', 'open')
        print(f"Opening valve {self.id}")

    def close(self, Operation):
        GPIO.output(self.pin, GPIO.HIGH)
        Operation.logCSV(f'valve {self.id}', 'close')
        print(f"Closing valve {self.id}")

    def end(self):
        print(f"instance valve {self.id} was deconstructed.")
        GPIO.output(self.pin, GPIO.LOW)

    def __del__(self):
        GPIO.cleanup()
        print(f"gpio was cleaned up.")