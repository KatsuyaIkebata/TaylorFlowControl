import csv
from datetime import datetime

class CSVClass:
    def __init__(self, file_name):
        current_time = datetime.now().strftime("%Y%m%d-%H%M")
        file_name = f'OperationLog-{current_time}.csv'
        csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Device','DeviceNum' 'Action']

        with open(file_name, mode='w', newline='') as file:
        # CSVファイルの設定
            csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Device','DeviceNum' 'Action']
            writer = csv.writer(file)
            writer.writerow(csv_header)
        