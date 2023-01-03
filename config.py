PLATFORM = 'ANTARIS'


ZES_VERSION = '1.0.1.8'

USE_VIRTUAL_PAYLOAD = False
USE_VIRTUAL_HARDWARE_CTRL = False
DEBUG = False

SERIAL_DEVICE = ""    # UART device endpoint

GPIO_NRESET_PIN = ""      # GPIO output pin (as ZES_NRST in schematic)
GPIO_FLAG_PIN = ""        # GPIO input pin (as ZES_FLAG in schematic)

HOME_FOLDER_PATH = ""     # the folder where this zesUART is placed at

'''
=========================================================
Antaris Related Settings
=========================================================
'''
if PLATFORM == 'ANTARIS':
    SERIAL_DEVICE = "/dev/ttyUSB1"                 # UART device endpoint

    GPIO_NRESET_PIN = 5  # GPIO output pin (as ZES_NRST in schematic)
    GPIO_FLAG_PIN = 6    # GPIO input pin (as ZES_FLAG in schematic)

    HOME_FOLDER_PATH = "/opt/antaris/app"            # the folder where this zesUART is placed in

    DEBUG = False

elif PLATFORM == 'ANTARIS-DOCKER':
    SERIAL_DEVICE = "/dev/ttyCH343USB0"                 # UART device endpoint

    GPIO_NRESET_PIN = 5  # GPIO output pin (as ZES_NRST in schematic)
    GPIO_FLAG_PIN = 6    # GPIO input pin (as ZES_FLAG in schematic)

    HOME_FOLDER_PATH = "/opt/antaris/app"            # the folder where this zesUART is placed in

    DEBUG = True
    USE_VIRTUAL_PAYLOAD = True
    USE_VIRTUAL_HARDWARE_CTRL = True

elif PLATFORM == 'WINDOWS':
    '''
    =========================================================
    Development Settings
    =========================================================
    '''
    SERIAL_DEVICE = "COM5"

    GPIO_NRESET_PIN = "/dev/antaris/gpio13/value"
    GPIO_FLAG_PIN = "/dev/antaris/gpio14/value"

    HOME_FOLDER_PATH = "E:/Git"

    USE_VIRTUAL_PAYLOAD = False
    USE_VIRTUAL_HARDWARE_CTRL = True
    DEBUG = True

elif PLATFORM == 'RPI':
    '''
    =========================================================
    Test Settings
    =========================================================
    '''
    SERIAL_DEVICE = "/dev/ttyAMA0"

    GPIO_NRESET_PIN = 24
    GPIO_FLAG_PIN = 23

    HOME_FOLDER_PATH = "/home/pi"
    DEBUG = True
