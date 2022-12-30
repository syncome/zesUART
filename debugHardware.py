import sys
from config import *
from antarisAPI.gen.antaris_sdk_version import *
from ZesLogger import ZesLogger
from ZesAntaris import ZesAntarisOperator
from zesThread import FsmThread
from AntarisCtrl import AntarisCtrl
import time, os, shutil, zipfile
from flightService import shutdown_app, process_health_check, \
    process_response_register, process_reponse_point_to_target, process_response_get_current_location, \
    process_response_download_file_to_gs, \
    process_response_payload_power_control, download_logfile_to_groundstation, run_payload_in_flight_mode


YELLOW = "\x1b[1;33;40m"
RED = "\x1b[1;31;40m"

from flightService import fsms
from gpio_antaris import set_POWER_pin, set_NRESET_pin, read_STATUS_pin

def start_zes_hardware_debugging(mythread: FsmThread):
    mythread.state = "STARTED"

    print('=== 1 Debugging Power===')
    print(">Setting POWER to OFF...\n")
    set_POWER_pin(mythread, on=False)
    input(f'[Action 1.1] Please check and confirm the power to ZES payload is *OFF*, ZES payload Green LED is *OFF*.\n Press any key to continue.....\n\n')
    print(">Reading FLAG ...\n")
    value = read_STATUS_pin()
    input(f'[Action 1.2] The current FLAG value read from API is {value}, expected value is *LOW*\n Press any key to continue.....')

    print(">Setting POWER to ON...\n")
    set_POWER_pin(mythread, on=True)
    input('[Action 1.3] Please check and confirm the power to ZES payload is *ON*, ZES payload Green LED is *ON*.\n Press any key to continue.....')
    print(">Reading FLAG ...\n")
    value = read_STATUS_pin()
    input(f'[Action 1.4] The current FLAG value read from API is {value}, expected value is *HIGH*\n Press any key to continue.....')

    print(f'\n\n\n=== 2 Debugging GPIO-{GPIO_NRESET_PIN} NRESET ===')
    input('[Action 2.1] Please check the default NRST value, before any commands is send out \n Press any key to continue.....')

    print(">Setting NRST to LOW...\n")
    set_NRESET_pin(value=False)
    input('[Action 2.2] Please check and confirm Antaris GPIO-5 (NRST) is value *LOW* \n Press any key to continue.....')

    print(">Setting NRST to HIGH...\n")
    set_NRESET_pin(value=True)
    input('[Action 2.3] Please check and confirm Antaris GPIO-5 (NRST) is value *HIGH* \n Press any key to continue.....')

    value = read_STATUS_pin()
    input(f'Current status value is {value} \n Press any key to continue.......')

    print('\n\n\n=== 3 Debugging UART ===')
    from ZesAntaris import ZesAntarisOperator

    while True:
        print(">Sending command 0x00 to payload...\n")
        msg = ZesAntarisOperator.test_operation_A(mblk=0)
        if not msg:
            print('[Error] Cannot communicate with ZES payload via UART. \n')
            print('Key in "q" to quit, other keyss to continue...')
            action = input()
            if action == '':
                break
        else:
            print(f'Received msg: {msg}')

            print('=== Starting Ground Test ===')
            ZesAntarisOperator.ground_test_mode(mythread)
            break

    AntarisCtrl.sequence_done(mythread.channel, mythread.seq_id)
    mythread.state = "EXITING"


def start_test_sequence(start_seq_param):
    # start all sequences
    for key in fsms:
        fsms[key].start()
        print(f'Thread {key} started')


def zes_app_test(mode='ground'):
    SDK_VERSION = f'{ANTARIS_PA_PC_SDK_MAJOR_VERSION}.{ANTARIS_PA_PC_SDK_MINOR_VERSION}.{ANTARIS_PA_PC_SDK_PATCH_VERSION}'
    ZesLogger.log(cmdStr='SYS', dataStr=f'Zes Ver:{ZES_VERSION}, SDK Ver:{SDK_VERSION}')

    callback_func_list = {
        'StartSequence': start_test_sequence,
        'Shutdown': shutdown_app,
        'HealthCheck': process_health_check,
        'RespRegister': process_response_register,
        'RespGetCurrentLocation': process_response_get_current_location,
        'RespStageFileDownload': process_response_download_file_to_gs,
        'RespPayloadPowerControl': process_response_payload_power_control,
    }

    # Create Channel to talk to Payload Controller (PC)
    channel = AntarisCtrl.create_insecure_channel(callback_func_list)

    if channel == None:
        print("Error : Create Channel failed")
        exit()


    # Create FSM threads  (arg : channel, thread-id, correlation_id, count, seq_id, fsm-function)
    fsms[1] = FsmThread(channel, 1, 10000, 'ZES_HARDWARE_DEBUGGING', start_zes_hardware_debugging)


    print("===================================")
    print(fsms[1].seq_id)

    AntarisCtrl.register_app(channel, 10000)
    start_test_sequence(None)

    while fsms[1].state == "NOT_STARTED":
        if DEBUG: print(f'{fsms[1].seq_id} is not started yet, waiting PC to initialize and start')
        time.sleep(1)

        # Wait for all FSM threads to complete
    for key in fsms:
        if fsms[key].state != "NOT_STARTED":
            fsms[key].join()

    AntarisCtrl.delete_channel_and_goodbye(channel)


if __name__ == "__main__":
    mode = 'ground'
    if sys.argv and len(sys.argv) >= 2:
        mode = sys.argv[1]
    zes_app_test(mode)
