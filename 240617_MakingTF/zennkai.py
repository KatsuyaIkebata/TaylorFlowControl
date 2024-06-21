import serial
import time

# Set up the serial connection
ser = serial.Serial(
    port='COM6',         # Replace with your actual COM port
    baudrate=115200,     # Baud rate
    timeout=1            # Timeout for read
)

# Ensure the connection is open
if ser.is_open:
    print("Serial connection established.")
else:
    print("Failed to establish serial connection.")

def send_command(command, sec):
    """ Send command to the syringe pump and read the response """
    command += '\r\n'
    ser.write(command.encode())
    time.sleep(0.1)  # Wait for the pump to process the command
    response = ser.read(ser.in_waiting or 1).decode().strip()
    time.sleep(sec - 0.1)
    return response

def end():
    ser.write('STP\r\n' .encode())
    time.sleep(0.1)
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

# Set the syringe diameter to 29 mm
# response = send_command('DIAMETER 29.0')
# print('Set Diameter Response:', response)

# Start the pump for 10 seconds (Infusion)
response = send_command('RUN', 10) # Infuse for 10 seconds
print('Run (Infusion) Response:', response)


# Stop the pump
response = send_command('STOP', 5) # Wait for 5 seconds
print('Stop Response:', response) 

# Start the pump for 5 seconds (Infusion)
response = send_command('IRUN', 5) # Infuse for 5 seconds
print('Run (Infusion) Response:', response)

# Start the pump for 7 seconds (Withdrawal)
''' Syringe pump I used was infuse only
response = send_command('DIR W')  # Set direction to withdrawal
print('Set Direction to Withdrawal Response:', response)
response = send_command('RUN')
print('Run (Withdrawal) Response:', response)
time.sleep(7)  # Withdraw for 7 seconds
'''

# Stop the pump
response = end()
print('Stop Response:', response)


# Close the serial connection
ser.close()
print("Serial connection closed.")
