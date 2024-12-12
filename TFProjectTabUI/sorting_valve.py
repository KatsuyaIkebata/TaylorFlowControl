class Sort:
    def func(rows):
        '''バルブ番号からポンプ番号の判断'''
        if(rows % 2 == 0):
            return 0
        elif(rows % 2 == 1):
            return 1
        else:
            return "Error"