from judge_on_off import JudgeClass
import common_delays as c

class TxtClass:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, 'w')

    def write(self, text):
        self.file.write(text + '\n')

    def close(self, Operation):
        for key, value in vars(Operation.config).items():
            self.write(f"{key}: {value}")
        for i in range(Operation.config.valve_num):
            for j in range(2):
                self.write(f"Valve {i} {JudgeClass.OpenClose(j)} delay from pump{i} {JudgeClass.InfuseStop(j)}: {c.delays[i][j]}")
        self.file.close()

    
