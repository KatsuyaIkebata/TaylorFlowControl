def decideit():
    if stop:
        print(f"Stop is {stop}")
    else:
        print(f"stop is {stop}, over")
    print(f"var_a is {var_a}")
    # var_a += 2 これをかくと、上のやつがエラー吐く
    print(f"var_a in func is {var_a}")
    print("End of function")

stop = False
var_a = 1
decideit()
print(f"var_a is {var_a}")
