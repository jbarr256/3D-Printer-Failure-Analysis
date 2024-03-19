import serial, time
#initialization and open the port

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call
#ser = serial.Serial('COM4')  # open serial port

# with serial.Serial('COM4',9600, timeout=5) as ser:
#     x = ser.read()          # read one byte
#     s = ser.read(10)        # read up to ten bytes (timeout)
#     line = ser.readline()   # read a '\n' terminated line
#     print(line)
#     print(x)

# i = 0
# while i <= 3:
#     ser = serial.Serial('COM4', 9600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)
#     s = ser.readline()
#     print(s)


def write_read(x):
    arduino = serial.Serial(port='/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0', baudrate=9600, timeout=.1)
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data


# while True:
#     num = "1"
#     value = write_read(num)
#     value = str(value)
#     print(value)

