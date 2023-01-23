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
    numValue = 1 if value else 0
    AntarisCtrl.set_gpio_pin(GPIO_NRESET_PIN, numValue)
    ZesLogger.log(cmdStr='SYS', dataStr=f'NRESET is now set to {numValue}')


def read_STATUS_pin():
    patch_STATUS_pin()
    return True  # assume payload is always working --> require manual reboot or reset

def patch_STATUS_pin():
    AntarisCtrl.set_gpio_pin(GPIO_FLAG_PIN, 0)
