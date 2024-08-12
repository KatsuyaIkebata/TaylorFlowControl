class OperationManager:
    def __init__(self):
        self.pumps = [SyringePump(i) for i in range(2)]
        self.valves = [Valve(i) for i in range(4)]
        self.TubeDiameterInch = 1/8   # inch チューブの内径
        self.SyringeDiameter = 29.2   # mm シリンジポンプの内径
        self.TotalRate = 3            # mL/min 合計流量
        self.TotalTime = 1            # min 合計時間
        self.AlarmTime = 0.5          # min アラームが鳴る時間
        self.SlugLength1 = 30          # mm スラグ1の長さ(実際は少しずれる)
        self.SlugLength2 = 50         # mm スラグ2の長さ(実際は少しずれる)
        self.ResponseTime = 0.1       # s 応答を待つ時間
        '''
        ファイル間共通変数 delaysの初期設定
        バルブ命令の遅れ時間を設定
        [0][0]:バルブ0の開放(電源OFF)
        [3][1]: バルブ3の閉鎖(電源ON)
        '''
        self.delays = [[0.0 for _ in range(2)] for _ in range(4)]

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