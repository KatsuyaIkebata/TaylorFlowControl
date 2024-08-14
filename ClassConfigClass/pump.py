import serial

class PumpClass:
    def __init__(self, id):
        self.id = id

    def infuse(self):
        self.send_command(self.ser, 'RUN')
        print(f"Infusing from pump {self.id}")

    def stop(self):
        self.send_command(self.ser, 'STOP')
        print(f"pump {self.id} stop")

    def send_command(self, command):
        """シリンジポンプにコマンドを送信する"""
        command += '\r\n'
        ser.write(command.encode()) 

    def receive_command(self, ser):
        response = ser(ser.in_waiting or 1).decode().strip()
        return response


    def stop(self, Operation):
        print(f"Stopping pump {self.id}")

    def end(self, Operation):
        self.stop(Operation)
        self.ser.close()
