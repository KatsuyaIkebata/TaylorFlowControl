import serial

class TimingClass_4_2:
    def __init__(self, config, delays):
        self.p0A = 0  # 0秒後に実行開始
        self.p0B = self.p0A + config.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
        self.p0C = self.p0A + config.infuse_time0    # ポンプ0の押出時間後に実行開始
        self.p0D = self.p0C + config.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
        self.p1A = self.p0A + config.infuse_time0    # ポンプ0の停止と同時に実行
        self.p1B = self.p1A + config.response_time   # Bの押出開始後、応答時間が過ぎたら実行開始
        self.p1C = self.p1A + config.infuse_time1    # ポンプ1の押出時間後に実行開始
        self.p1D = self.p1C + config.response_time   # ポンプ1の停止後、応答時間が過ぎたら実行開始
        self.v0A = self.p0A + delays[0][0]    # ポンプ0の押出後、遅れ時間経過した後、バルブ0を開放（電源OFF）
        self.v0C = self.p0C + delays[0][1]    # ポンプ0の停止後、遅れ時間経過した後、バルブ0を開放（電源OFF）
        self.v1A = self.p1A + delays[1][0]    # ポンプ1の停止と同時にバルブ1を稼働（閉鎖）
        self.v1C = self.p1C + delays[1][1]    # ポンプ1の押出と同時にバルブ1を停止（開放）
        self.v2A = self.p0A + delays[2][0]    # ポンプ0の停止後、遅れ時間経過した後、バルブ2を稼働（閉鎖）
        self.v2C = self.p0C + delays[2][1]    # ポンプ0の押出後、遅れ時間経過した後、バルブ2を停止（開放）
        self.v3A = self.p1A + delays[3][0]    # ポンプ1の停止後、遅れ時間経過した後、バルブ3を稼働（閉鎖）
        self.v3C = self.p1C + delays[3][1]    # ポンプ1の押出後、遅れ時間経過した後、バルブ3を停止（開放）

class IterationClass_4_2:
    def __init__(self):
        # 各プロセスの実行回数の設定
        self.p0A = 0
        self.p0B = 0
        self.p0C = 0
        self.p0D = 0
        self.p1A = 0
        self.p1B = 0
        self.p1C = 0
        self.p1D = 0
        self.v0A = 0
        self.v0C = 0
        self.v1A = 0
        self.v1C = 0
        self.v2A = 0
        self.v2C = 0
        self.v3A = 0
        self.v3C = 0


class RunOpeClass_4_2:
    def operation_4_2(Operation):
        if Operation.passed_time >= Operation.Timing.p0C and Operation.Iteration.p0C < Operation.Iteration.p0A:
            Operation.Pump[0].stop(Operation)
            Operation.Iteration.p0C += 1

        if Operation.passed_time >= Operation.Timing.p0D and Operation.Iteration.p0D < Operation.Iteration.p0A:   
            Operation.Pump[0].receive_command(Operation)
            Operation.Iteration.p0D += 1

        if Operation.passed_time >= Operation.Timing.p1C and Operation.Iteration.p1C < Operation.Iteration.p1A:   
            Operation.Pump[1].stop(Operation)
            Operation.Iteration.p1C += 1

        if Operation.passed_time >= Operation.Timing.p1D and Operation.Iteration.p1D < Operation.Iteration.p1A:   
            Operation.Pump[1].receive_command(Operation)
            Operation.Iteration.p1D += 1

        if Operation.passed_time >= Operation.Timing.p0A and Operation.Iteration.p0A == Operation.Iteration.p0C:
            Operation.Timing.p0B = Operation.Timing.p0A + Operation.config.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
            Operation.Timing.p0C = Operation.Timing.p0A + Operation.config.infuse_time0    # ポンプ0の押出時間後に実行開始
            Operation.Timing.p0D = Operation.Timing.p0C + Operation.config.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
            Operation.Timing.v0A = Operation.Timing.p0A + Operation.delays[0][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ0を開放（電源OFF）
            Operation.Timing.v0C = Operation.Timing.p0C + Operation.delays[0][1] # ポンプ0の停止後、遅れ時間経過したらバルブ0を閉鎖（電源ON）
            Operation.Timing.v2A = Operation.Timing.p0A + Operation.delays[2][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ2を開放（電源OFF）
            Operation.Timing.v2C = Operation.Timing.p0C + Operation.delays[2][1] # ポンプ0の停止後、遅れ時間経過したらバルブ2を閉鎖（電源ON）
            Operation.Pump[0].infuse(Operation)
            Operation.Iteration.p0A += 1
            # print(f'Iteration of 1A: {Operation.Iteration.p0A}')
            Operation.Timing.p0A = Operation.config.infuse_time0 * Operation.Iteration.p0A + Operation.config.infuse_time1 * Operation.Iteration.p0A  # プロセス1Aの次の実行時間を設定
            # print(f'Operation.Timing.p0A: {Operation.Timing.p0A}')

        if Operation.passed_time >= Operation.Timing.p1A and Operation.Iteration.p1A == Operation.Iteration.p1C:
            Operation.Timing.p1B = Operation.Timing.p1A + Operation.config.response_time  # Bの押出開始後、応答時間が過ぎたら実行開始
            Operation.Timing.p1C = Operation.Timing.p1A + Operation.config.infuse_time1   # ポンプ1の押出時間後に実行開始
            Operation.Timing.p1D = Operation.Timing.p1C + Operation.config.response_time  # ポンプ1の停止後、応答時間が過ぎたら実行開始
            Operation.Timing.v1A = Operation.Timing.p1A + Operation.delays[1][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ1を開放（電源OFF）
            Operation.Timing.v1C = Operation.Timing.p1C + Operation.delays[1][1] # ポンプ1の停止後、遅れ時間経過したらバルブ1を閉鎖（電源ON）
            Operation.Timing.v3A = Operation.Timing.p1A + Operation.delays[3][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ3を開放（電源OFF）
            Operation.Timing.v3C = Operation.Timing.p1C + Operation.delays[3][1] # ポンプ1の停止後、遅れ時間経過したらバルブ3を閉鎖（電源ON)
            Operation.Pump[1].infuse(Operation)
            Operation.Iteration.p1A += 1
            # print(f'Iteration of 2A: {Operation.Iteration.p1A}')
            Operation.Timing.p1A = Operation.config.infuse_time0 * (Operation.Iteration.p0A + 1) + Operation.config.infuse_time1 * Operation.Iteration.p1A  # プロセス1Aの次の実行時間を設定
            # print(f'Operation.Timing.p1A: {Operation.Timing.p1A}')

        if Operation.passed_time >= Operation.Timing.p0B and Operation.Iteration.p0B < Operation.Iteration.p0A:   
            Operation.Pump[0].receive_command(Operation)
            Operation.Iteration.p0B += 1

        if Operation.passed_time >= Operation.Timing.p1B and Operation.Iteration.p1B < Operation.Iteration.p1A:   
            Operation.Pump[1].receive_command(Operation)
            Operation.Iteration.p1B += 1

        
        if Operation.passed_time >= Operation.Timing.v0A and Operation.Iteration.v0A == Operation.Iteration.v0C:
            Operation.Valve[0].open(Operation)
            Operation.Timing.v0A = Operation.Timing.p0A + Operation.delays[0][0]
            Operation.Iteration.v0A += 1

        if Operation.passed_time >= Operation.Timing.v0C and Operation.Iteration.v0C < Operation.Iteration.v0A:
            Operation.Valve[0].close(Operation)
            Operation.Timing.v0C = Operation.Timing.p0C + Operation.delays[0][1]
            Operation.Iteration.v0C += 1

        if Operation.passed_time >= Operation.Timing.v1A and Operation.Iteration.v1A == Operation.Iteration.v1C:
            Operation.Valve[1].open(Operation)
            Operation.Timing.v1A = Operation.Timing.p1A + Operation.delays[1][0]
            Operation.Iteration.v1A += 1

        if Operation.passed_time >= Operation.Timing.v1C and Operation.Iteration.v1C < Operation.Iteration.v1A:
            Operation.Valve[1].close(Operation)
            Operation.Timing.v1C = Operation.Timing.p1C + Operation.delays[1][1]
            Operation.Iteration.v1C += 1
        
        if Operation.passed_time >= Operation.Timing.v2A and Operation.Iteration.v2A == Operation.Iteration.v2C:
            Operation.Valve[2].open(Operation)
            Operation.Timing.v2A = Operation.Timing.p0A + Operation.delays[2][0]
            Operation.Iteration.v2A += 1

        if Operation.passed_time >= Operation.Timing.v2C and Operation.Iteration.v2C < Operation.Iteration.v2A:
            Operation.Valve[2].close(Operation)
            Operation.Timing.v2C = Operation.Timing.p0C + Operation.delays[2][1]
            Operation.Iteration.v2C += 1
                
        if Operation.passed_time >= Operation.Timing.v3A and Operation.Iteration.v3A == Operation.Iteration.v3C:
            Operation.Valve[3].open(Operation)
            Operation.Timing.v3A = Operation.Timing.p1A + Operation.delays[3][0]
            Operation.Iteration.v3A += 1

        if Operation.passed_time >= Operation.Timing.v3C and Operation.Iteration.v3C < Operation.Iteration.v3A:
            Operation.Valve[3].close(Operation)
            Operation.Timing.v3C = Operation.Timing.p1C + Operation.delays[3][1]
            Operation.Iteration.v3C += 1