'''
ファイル間共通変数 delaysの設定
バルブ命令の遅れ時間を設定
[0][0]:バルブ0の開放(電源OFF)
[3][1]: バルブ3の閉鎖(電源ON)
'''
delays = [[0.0 for _ in range(2)] for _ in range(4)]