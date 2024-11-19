import serial

class TimingClass_0_2:
    def __init__(self, config, delays):
        self.p0A = 0  # 0秒後に実行開始
        self.p0B = self.p0A + config.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
        self.p0C = self.p0A + config.infuse_time0    # ポンプ0の押出時間後に実行開始
        self.p0D = self.p0C + config.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
        self.p1A = self.p0A + config.infuse_time0    # ポンプ0の停止と同時に実行
        self.p1B = self.p1A + config.response_time   # Bの押出開始後、応答時間が過ぎたら実行開始
        self.p1C = self.p1A + config.infuse_time1    # ポンプ1の押出時間後に実行開始
        self.p1D = self.p1C + config.response_time   # ポンプ1の停止後、応答時間が過ぎたら実行開始

class IterationClass_0_2:
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

class RunOpeClass_0_2:
    def operation_0_2(Operation):
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
            Operation.Pump[0].infuse(Operation)
            Operation.Iteration.p0A += 1
            # print(f'Iteration of 1A: {Operation.Iteration.p0A}')
            Operation.Timing.p0A = Operation.config.infuse_time0 * Operation.Iteration.p0A + Operation.config.infuse_time1 * Operation.Iteration.p0A  # プロセス1Aの次の実行時間を設定
            # print(f'Operation.Timing.p0A: {Operation.Timing.p0A}')

        if Operation.passed_time >= Operation.Timing.p1A and Operation.Iteration.p1A == Operation.Iteration.p1C:
            Operation.Timing.p1B = Operation.Timing.p1A + Operation.config.response_time  # Bの押出開始後、応答時間が過ぎたら実行開始
            Operation.Timing.p1C = Operation.Timing.p1A + Operation.config.infuse_time1   # ポンプ1の押出時間後に実行開始
            Operation.Timing.p1D = Operation.Timing.p1C + Operation.config.response_time  # ポンプ1の停止後、応答時間が過ぎたら実行開始
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


