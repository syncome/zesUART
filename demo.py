import serial
import time
import datetime

# start of program

LOG_FILE_PATH = ""  # ending with back-slash /

SERIAL_DEVICE = "/dev/ttyAMA0"    # serial device ending point
SERIAL_BAUDRATE = 9600

def power_on_zes_payload():
    # TODO: Insert the REAL control code to power on ZES payload
    print('Power on ZES payload....')
    pass


def power_off_zes_payload():
    # TODO: Insert the REAL control code to power OFF ZES payload
    print('Power off ZES payload....')
    pass


def pull_up_pin_nReset():
    # TODO: Insert the REAL control code to pull up pin nReset
    print('Pulling up nReset....')
    pass


def pull_down_pin_nReset():
    # TODO: Insert the REAL control code to pull down pin nReset
    print('Pulling down nReset....')
    pass


def get_satellite_status():
    # TODO: Insert the REAL control code to get satellite current status
    longitude = 0.0
    latitude = 0.0
    altitude = 0.0
    return f'LON={longitude} LAT={latitude} ALT={altitude}'


def save_to_log(logType, text):
    timeNow = datetime.datetime.utcnow()
    dateStr = timeNow.strftime('%Y%m%d')
    filename = 'ZES_' + dateStr + '.log'
    timeStr = timeNow.strftime('%H:%M:%S.%f')
    logLine = timeStr + "," + logType + ',' + text
    with open(LOG_FILE_PATH + filename, 'a+') as f:
        f.write(logLine + '\n')


def send_to_serial(cmd):
    try:
        ser = serial.Serial(port=SERIAL_DEVICE,
                            baudrate=SERIAL_BAUDRATE,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=0.1)
    except Exception as err:
        save_to_log('ERR', f'Cannot open serial port {SERIAL_DEVICE}')
        return ''

    ser.write(cmd)        # send to payload via serial/UART
    time.sleep(0.2)
    line = ser.readline() # read payload response via serial/UART
    return line


if __name__ == "__main__":
    # ============= Fresh Star ================
    power_on_zes_payload()
    save_to_log('POWER', 'Power On')

    time.sleep(1)

    pull_up_pin_nReset()

    while True:
        satStatus = get_satellite_status()
        save_to_log('STATUS', satStatus)

        time.sleep(1)
        response = send_to_serial(0x80)  # hex 0x80, integer 128

        if not response: # payload has no valid response
            power_off_zes_payload()
            save_to_log('POWER', 'Power Reset')

            pull_down_pin_nReset()
            time.sleep(3)

            power_on_zes_payload()
            time.sleep(1)

            pull_up_pin_nReset()
            time.sleep(1)

        else:  # payload has valid response
            save_to_log('CMD', response)
            time.sleep(10*60)    # sleep for 10 minutes
