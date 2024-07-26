import RPi.GPIO as GPIO
import time

# GPIOの設定
GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
GPIO.setwarnings(True)

# 使用するGPIOピンの設定
pin1 = 6  # 使用するGPIOピン番号を指定
pin2 = 13  # 使用するGPIOピン番号を指定
pin3 = 19  # 使用するGPIOピン番号を指定
pin4 = 26  # 使用するGPIOピン番号を指定
GPIO.setup(pin1, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin2, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin3, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin4, GPIO.OUT)  # GPIOピンを出力モードに設定

# 電流を流す
GPIO.output(pin1, GPIO.HIGH)  # ピン1をHIGHに設定して電流を流す
print("GPIO pin1 is set to HIGH. Current is flowing.")
time.sleep(5)  # 5秒間待機

GPIO.output(pin2, GPIO.HIGH)  # ピン2をHIGHに設定して電流を流す
print("GPIO pin2 is set to HIGH. Current is flowing.")
time.sleep(5)  # 5秒間待機

GPIO.output(pin3, GPIO.HIGH)  # ピン3をHIGHに設定して電流を流す
print("GPIO pin3 is set to HIGH. Current is flowing.")
time.sleep(5)  # 5秒間待機

GPIO.output(pin4, GPIO.HIGH)  # ピン4をHIGHに設定して電流を流す
print("GPIO pin4 is set to HIGH. Current is flowing.")
time.sleep(30)  # 30秒間待機

# 電流を止める
GPIO.output(pin1, GPIO.LOW)  # ピンをLOWに設定して電流を止める
print("GPIO pin1 is set to LOW. Current is stopped.")
GPIO.output(pin1, GPIO.LOW)  # ピンをLOWに設定して電流を止める

print("GPIO pin2 is set to LOW. Current is stopped.")
GPIO.output(pin2, GPIO.LOW)  # ピンをLOWに設定して電流を止める
print("GPIO pin3 is set to LOW. Current is stopped.")
GPIO.output(pin3, GPIO.LOW)  # ピンをLOWに設定して電流を止める

print("GPIO pin4 is set to LOW. Current is stopped.")
GPIO.output(pin4, GPIO.LOW)  # ピンをLOWに設定して電流を止める

# GPIOのクリーンアップ
GPIO.cleanup()  # GPIO設定をリセット
