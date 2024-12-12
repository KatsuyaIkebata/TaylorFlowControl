import csv
from datetime import datetime

class CSVClass:
    def __init__(self, file_name):
        csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Device','DeviceNum' 'Action']
        self.file_name = file_name
        with open(file_name, mode='w', newline='') as file:
        # CSVファイルの設定
            csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Device','DeviceNum' 'Action']
            writer = csv.writer(file)
            writer.writerow(csv_header)

    def log(self, device, action):
        """CSVファイルにログを記録する"""
        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            now = datetime.now()
            writer.writerow([now.hour, now.minute, now.second, now.microsecond // 1000, device, action])

        