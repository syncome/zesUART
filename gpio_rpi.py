import RPi.GPIO as GPIO

from ZesLogger import ZesLogger
from zesThread import FsmThread
from config import *

STATUS_PIN = GPIO_FLAG_PIN
N_RESET_PIN = GPIO_NRESET_PIN
# status pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(STATUS_PIN, GPIO.IN)
GPIO.setup(N_RESET_PIN, GPIO.OUT)

# GPIO.output(N_RESET_PIN, False)  # initialize GPIO NRESET


# OUT_PIN = 19
# IN_PIN = 26
# GPIO.setup(IN_PIN, GPIO.IN)
# GPIO.setup(OUT_PIN, GPIO.OUT)
#
#
# print(GPIO.input(IN_PIN))
# GPIO.output(OUT_PIN, True)
# print(GPIO.input(IN_PIN))
# GPIO.output(OUT_PIN, False)
# print(GPIO.input(IN_PIN))

DUMMY_POWER = False

def get_POWER_state(mythread: FsmThread):
    global DUMMY_POWER
    if DUMMY_POWER:
        return True
    else:
        DUMMY_POWER = True
        return False


def set_POWER_pin(mythread, on: bool):
    ZesLogger.log(cmdStr='SYS', dataStr=f'POWER is now set to {on}')
    pass


def set_NRESET_pin(value: bool):
    if value:
        GPIO.output(N_RESET_PIN, True)
    else:
        GPIO.output(N_RESET_PIN, False)
    ZesLogger.log(cmdStr='SYS', dataStr=f'NRESET is now set to {value}')


def read_STATUS_pin():
    value = GPIO.input(STATUS_PIN)
    if value:
        return True
    else:
        return False

def patch_STATUS_pin():
    pass