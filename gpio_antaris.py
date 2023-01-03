import datetime
import threading
import time

from ZesLogger import ZesLogger
from config import GPIO_NRESET_PIN, GPIO_FLAG_PIN
from AntarisCtrl import AntarisCtrl
from zesThread import FsmThread


def get_POWER_state(mythread: FsmThread):
    # AntarisCtrl.get_power_status(mythread.channel, mythread.correlation_id)
    # mythread.condition.acquire()
    # mythread.condition.wait()
    # return mythread.is_pl_power_on

    # sleep 1s and then assume power is on
    time.sleep(1)
    return True


def set_POWER_pin(mythread: FsmThread, on: bool):
    mythread.will_power_on = on
    AntarisCtrl.set_power_pin(mythread.channel, mythread.correlation_id, on)
    mythread.condition.acquire()
    mythread.condition.wait()
    ZesLogger.log(cmdStr='SYS', dataStr=f'POWER is now set to {on}')


def set_NRESET_pin(value: bool):
    lock = threading.Lock()
    lock.acquire()
    print('will set NREST PIN')
    numValue = 1 if value else 0
    AntarisCtrl.set_gpio_pin(GPIO_NRESET_PIN, numValue)
    # with open(GPIO_NRESET_PIN, 'w') as f:
    #     f.write('1' if value else '0')
    lock.release()
    ZesLogger.log(cmdStr='SYS', dataStr=f'NRESET is now set to {numValue}')


def read_STATUS_pin():
    lock = threading.Lock()
    lock.acquire()
    # with open(GPIO_FLAG_PIN, 'r') as f:
    #     value = f.read()
    isValueHigh = AntarisCtrl.read_gpio_pin(GPIO_FLAG_PIN)
    lock.release()
    return isValueHigh
