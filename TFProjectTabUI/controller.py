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
    def control(operation):
        config = operation.config
        for i in range(config.pump_num):
            if config.passed_time >= config.Timing.pC[i] and config.Iteration.pC[i] < config.Iteration.pA[i]:
                operation.Pump[i].stop(config)
                config.Iteration.pC[i] += 1

            if config.passed_time >= config.Timing.pD[i] and config.Iteration.pD[i] < config.Iteration.pA[i]:   
                config.Pump[i].receive_command(config)
                config.Iteration.pD[i] += 1

        if config.passed_time >= config.Timing.pA[0] and config.Iteration.pA[0] == config.Iteration.pC[0]:
            config.Timing.pB[0] = config.Timing.pA[0] + config.config.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
            config.Timing.pC[0] = config.Timing.pA[0] + config.config.infuse_time[0]    # ポンプ0の押出時間後に実行開始
            config.Timing.pD[0] = config.Timing.pC[0] + config.config.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
            for j in range(config.valve_num):
                if Sort.func == 0:
                    config.Timing.vA[j] = config.Timing.pA[0] + config.delays[j][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブjを開放（電源OFF）
                    config.Timing.vC[j] = config.Timing.pC[0] + config.delays[j][1] # ポンプ0の停止後、遅れ時間経過したらバルブjを閉鎖（電源ON）
            config.Pump[0].infuse(operation)
            config.Iteration.pA[0] += 1
            config.Timing.pA[0] = 0
            # print(f'Iteration of 1A: {config.Iteration.pA[0]}')
            for i in range(config.pump_num):
                config.Timing.pA[0] += config.config.infuse_time[i] * config.Iteration.pA[i]  # プロセス0Aの次の実行時間を設定
                # print(f'config.Timing.pA[0]: {config.Timing.pA[0]}')

        for i in range(1, config.pump_num):
            if config.passed_time >= config.Timing.pA[i] and config.Iteration.pA[i] == config.Iteration.pC[i]:
                config.Timing.pB[i] = config.Timing.pA[i] + config.config.response_time  # Bの押出開始後、応答時間が過ぎたら実行開始
                config.Timing.pC[i] = config.Timing.pA[i] + config.config.infuse_time1   # ポンプ1の押出時間後に実行開始
                config.Timing.pD[i] = config.Timing.pC[i] + config.config.response_time  # ポンプ1の停止後、応答時間が過ぎたら実行開始
                config.Timing.vA[i] = config.Timing.pA[i] + config.delays[1][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ1を開放（電源OFF）
                config.Timing.vC[i] = config.Timing.pC[i] + config.delays[1][1] # ポンプ1の停止後、遅れ時間経過したらバルブ1を閉鎖（電源ON）
                for j in range(config.valve_num):
                    if Sort.func(j) == i:
                        config.Timing.vA[j] = config.Timing.pA[i] + config.delays[i][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブjを開放（電源OFF）
                        config.Timing.vC[j] = config.Timing.pC[i] + config.delays[i][1] # ポンプ0の停止後、遅れ時間経過したらバルブjを閉鎖（電源ON）
                config.Pump[i].infuse(operation)
                config.Iteration.pA[i] += 1
                # print(f'Iteration of 2A: {config.Iteration.pA[i]}')
                config.Timing.pA[i] = config.config.infuse_time0 * (config.Iteration.pA[0] + 1) + config.config.infuse_time1 * config.Iteration.pA[i]  # プロセス1Aの次の実行時間を設定
                # print(f'config.Timing.pA[i]: {config.Timing.pA[i]}')

        for i in range(config.pump_num):
            if config.passed_time >= config.Timing.pB[i] and config.Iteration.pB[i] < config.Iteration.pA[i]:   
                config.Pump[i].receive_command(operation)
                config.Iteration.pB[i] += 1

            for j in range(config.valve_num):
                if Sort.func(j) == i:        
                    if config.passed_time >= config.Timing.vA[j] and config.Iteration.vA[j] == config.Iteration.vC[j]:
                        config.Valve[j].open(operation)
                        config.Timing.vA[j] = config.Timing.pA[j] + config.delays[j][0]
                        config.Iteration.vA[j] += 1

                    if config.passed_time >= config.Timing.vC[j] and config.Iteration.vC[j] < config.Iteration.vA[j]:
                        config.Valve[j].close(operation)
                        config.Timing.vC[j] = config.Timing.pC[j] + config.delays[j][1]
                        config.Iteration.vC[j] += 1