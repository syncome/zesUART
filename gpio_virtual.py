from ZesLogger import ZesLogger
from zesThread import FsmThread

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
    ZesLogger.log(cmdStr='SYS', dataStr=f'NRESET is now set to {value}')
    return True


def read_STATUS_pin():
    print(f'STATUS is True')
    return True
