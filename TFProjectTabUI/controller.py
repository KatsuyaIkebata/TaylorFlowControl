import common_delays as c
from sorting_valve import Sort 

class TimingClass:
    def __init__(self, config):        

        self.pA = [0]  # 0秒後に実行開始
        self.pB = [self.pA[0] + config.response_time]   # Aの押出開始後、応答時間が過ぎたら実行開始
        self.pC = [self.pA[0] + config.infuse_time[0]]    # ポンプ0の押出時間後に実行開始
        self.pD = [self.pC[0] + config.response_time]   # ポンプ0の停止後、応答時間が過ぎたら実行開始
        for i in range(1, config.pump_num):                   
            self.pA.append(self.pA[i-1] + config.infuse_time[i-1])    # ポンプiの停止と同時に実行
            self.pB.append(self.pA[i] + config.response_time)   # ポンプiの押出開始後、応答時間が過ぎたら実行開始
            self.pC.append(self.pA[i] + config.infuse_time[i])  # ポンプiの押出時間後に実行開始
            self.pD.append(self.pC[i] + config.response_time)   # ポンプiの停止後、応答時間が過ぎたら実行開始
        
        self.vA = []
        self.vC = []
        for i in range(config.valve_num):
            self.vA.append(self.pA[Sort.func(i)] + c.delays[i][0])    # ポンプxの停止と同時にバルブiを稼働（閉鎖）
            self.vC.append(self.pC[Sort.func(i)] + c.delays[i][1])    # ポンプxの押出と同時にバルブiを停止（開放）

class IterationClass:
    def __init__(self, config):
        # 各プロセスの実行回数の設定
        self.pA = []
        self.pB = []
        self.pC = []
        self.pD = []
        for _ in range(config.pump_num):
            self.pA.append(0) 
            self.pB.append(0)
            self.pC.append(0)
            self.pD.append(0)

        self.vA = []
        self.vC = []
        for _ in range(config.valve_num):
            self.vA.append(0)
            self.vC.append(0)

class RunOpeClass:
    @staticmethod
    def control(operation):
        return RunOpeClass.run_operation

    @staticmethod
    def run_operation(operation):
        config = operation.config
        for i in range(config.pump_num):
            if operation.passed_time >= operation.Timing.pC[i] and operation.Iteration.pC[i] < operation.Iteration.pA[i]:
                operation.Pump[i].stop(operation)
                operation.Iteration.pC[i] += 1

            if operation.passed_time >= operation.Timing.pD[i] and operation.Iteration.pD[i] < operation.Iteration.pA[i]:   
                operation.Pump[i].receive_command(operation)
                operation.Iteration.pD[i] += 1

        for i in range(config.pump_num):
            if operation.passed_time >= operation.Timing.pA[i] and operation.Iteration.pA[i] == operation.Iteration.pC[i]:
                operation.Timing.pB[i] = operation.Timing.pA[i] + operation.config.response_time  # Bの押出開始後、応答時間が過ぎたら実行開始
                operation.Timing.pC[i] = operation.Timing.pA[i] + operation.config.infuse_time[i]   # ポンプ1の押出時間後に実行開始
                operation.Timing.pD[i] = operation.Timing.pC[i] + operation.config.response_time  # ポンプ1の停止後、応答時間が過ぎたら実行開始
                for j in range(config.valve_num):
                    if Sort.func(j) == i:
                        operation.Timing.vA[j] = operation.Timing.pA[i] + c.delays[i][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブjを開放（電源OFF）
                        operation.Timing.vC[j] = operation.Timing.pC[i] + c.delays[i][1] # ポンプ0の停止後、遅れ時間経過したらバルブjを閉鎖（電源ON）
                operation.Pump[i].infuse(operation)
                operation.Iteration.pA[i] += 1
                operation.Timing.pA[i] = 0
                for j in range(config.pump_num):
                    operation.Timing.pA[i] += operation.config.infuse_time[j] * (operation.Iteration.pC[j] + 1)  # プロセスiAの次の実行時間を設定

        for i in range(config.pump_num):
            if operation.passed_time >= operation.Timing.pB[i] and operation.Iteration.pB[i] < operation.Iteration.pA[i]:   
                operation.Pump[i].receive_command(operation)
                operation.Iteration.pB[i] += 1

            for j in range(config.valve_num):
                if Sort.func(j) == i:        
                    if operation.passed_time >= operation.Timing.vA[j] and operation.Iteration.vA[j] == operation.Iteration.vC[j]:
                        operation.Valve[j].open(operation)
                        operation.Timing.vA[j] = operation.Timing.pA[i] + c.delays[j][0]
                        operation.Iteration.vA[j] += 1

                    if operation.passed_time >= operation.Timing.vC[j] and operation.Iteration.vC[j] < operation.Iteration.vA[j]:
                        operation.Valve[j].close(operation)
                        operation.Timing.vC[j] = operation.Timing.pC[i] + c.delays[j][1]
                        operation.Iteration.vC[j] += 1