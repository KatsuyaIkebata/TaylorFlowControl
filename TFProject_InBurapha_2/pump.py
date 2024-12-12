import serial
import time
from write_csv import CSVClass 

class PumpClass:
    def __init__(self, id):
        self.id = id

    def setting(self, Operation):
        self.send_command(f'set diameter {Operation.Config.syringe_diameter}')
        time.sleep(0.1)
        self.receive_command(Operation)

        self.send_command(f'set rate {Operation.Config.total_rate}')
        time.sleep(0.1)
        self.receive_command(Operation)  

    def infuse(self, Operation):
        self.send_command('start')
        Operation.logCSV(f'pump {self.id}', 'infuse')
        print(f"Infusing from pump {self.id}")

    def stop(self, Operation):
        self.send_command('stop')
        Operation.logCSV(f'pump {self.id}', 'stop')
        print(f"pump {self.id} stop")


    def send_command(self, command):
        """シリンジポンプにコマンドを送信する"""
        command += '\r\n'
        self.ser.write(command.encode()) 
        # print(f'pump {self.id} {command}: {self.ser}')


    def receive_command(self, Operation):
        response = self.ser.read(self.ser.in_waiting or 1).decode().strip()
        Operation.NewCSV.log(f'Pump {self.id}', f'Response: {response}')
        # print(f'pump {self.id} response: {response}: {self.ser}')


    def end(self, Operation):
        self.stop(Operation)
        self.ser.close()
