class JudgeClass:
    def OpenClose(columns):
        '''開放か閉鎖か判断'''
        if(columns == 0):
            return "Open"
        elif(columns == 1):
            return "Close"
        else:
            return "Error"

    def InfuseStop(columns):
        '''バルブのON/OFFからポンプのInfuse/Stopの判断'''
        if(columns == 0):
            return "infuse"
        elif(columns == 1):
            return "stop"
        else:
            return "Error"