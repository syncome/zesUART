import serial
import time

SERIAL_DEVICE = "/dev/ttyAMA0"    # serial device ending point
SERIAL_BAUDRATE = 9600


CMD75_TEST_OP_A = 0b000 << 5  # 00
CMD75_TEST_OP_B = 0b001 << 5  # 20
CMD75_WRITE_A = 0b010 << 5    # 40
CMD75_WRITE_B = 0b011 << 5    # 60
CMD75_RD_CK_A = 0b100 << 5    # 80
CMD75_RD_CK_B = 0b101 << 5    # A0
CMD75_SVC_REG = 0b110 << 5    # C0
CMD75_OUT_GEN = 0b111 << 5    # E0

def send_to_serial(cmd):
    try:
        ser = serial.Serial(port=SERIAL_DEVICE,
                            baudrate=SERIAL_BAUDRATE,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=0.1)
    except Exception as err:
        print(f'[Error]: Cannot open serial port {SERIAL_DEVICE}')
        return ''

    ser.write(cmd)         # send to payload via serial/UART
    time.sleep(0.2)
    line = ser.readline()  # read payload response via serial/UART
    time.sleep(0.2)
    return line

retry = 1
hasError = False
while True:
        print(f'>>>  Trying for the {retry} time....')

        res = send_to_serial(0x00)
        if res:
            print('>>> Test 00 passed.')

        res = send_to_serial(0x20)
        if res:
            print('>>> Test 20 passed.')

        res = send_to_serial(0x40)
        if res:
            print('>>> Test 40 passed.')

        res = send_to_serial(0x60)
        if res:
            print('>>> Test 60 passed.')

        res = send_to_serial(0x80)
        if res:
            print('>>> Test 80 passed.')

        res = send_to_serial(0x40)
        if res:
            print('>>> Test 20 passed.')

        retry += 1


