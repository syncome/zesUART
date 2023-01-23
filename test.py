import sys
from config import *
from ZesAntaris import ZesAntarisOperator
from zesThread import FsmThread
from AntarisCtrl import AntarisCtrl
import time, os, shutil, zipfile
from flightService import shutdown_app, process_health_check, \
    process_response_register, process_reponse_point_to_target, process_response_get_current_location, \
    process_response_download_file_to_gs, \
    process_response_payload_power_control, download_logfile_to_groundstation, run_payload_in_flight_mode

from flightService import fsms


def start_zes_ground_test(mythread: FsmThread):
    mythread.state = "STARTED"
    ZesAntarisOperator.ground_test_mode(mythread)
    mythread.state = "EXISTING"

    AntarisCtrl.sequence_done(mythread.channel, mythread.seq_id)

def start_zes_flight_test(mythread: FsmThread):
    mythread.state = "STARTED"

    # AntarisCtrl.get_sat_location(mythread.channel, mythread.correlation_id)
    # mythread.condition.acquire()
    # mythread.condition.wait()

    ZesAntarisOperator.power_on_and_prepare_payload_if_necessary(mythread)
    ZesAntarisOperator.one_time_flight_service_mode(mythread)
    mythread.state = "EXISTING"

    AntarisCtrl.sequence_done(mythread.channel, mythread.seq_id)

def start_test_sequence(start_seq_param):
    # start all sequences
    for key in fsms:
        fsms[key].start()
        print(f'Thread {key} started')


def zes_app_test(mode='ground'):
    ZesAntarisOperator.patch_STATUS_pin()

    callback_func_list = {
        'StartSequence': start_test_sequence,
        'Shutdown': shutdown_app,
        # 'PassthruCmd': process_passthru_tele_cmd,
        # 'NewFileUploaded': process_new_file_uploaded,
        'HealthCheck': process_health_check,
        'RespRegister': process_response_register,
        # 'RespPointToTarget': process_reponse_point_to_target,
        'RespGetCurrentLocation': process_response_get_current_location,
        # 'RespGetCurrentTime': process_response_get_current_time,
        # 'RespGetCurrentPowerState': process_response_get_current_power_state,
        'RespStageFileDownload': process_response_download_file_to_gs,
        'RespPayloadPowerControl': process_response_payload_power_control,
    }

    # Create Channel to talk to Payload Controller (PC)
    channel = AntarisCtrl.create_insecure_channel(callback_func_list)

    if channel == None:
        print("Error : Create Channel failed")
        exit()


    # Create FSM threads  (arg : channel, thread-id, correlation_id, count, seq_id, fsm-function)
    if mode == 'ground':
        fsms[1] = FsmThread(channel, 1, 10000, 'ZES_GROUND_TEST', start_zes_ground_test)
    else:
        fsms[1] = FsmThread(channel, 1, 10000, 'ZES_FLIGHT_TEST', start_zes_flight_test)

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

    fsms[4] = FsmThread(channel, 4, 40000, 'ZES_Download_Log', download_logfile_to_groundstation)
    fsms[4].start()
    fsms[4].join()

    AntarisCtrl.delete_channel_and_goodbye(channel)


if __name__ == "__main__":
    mode = 'ground'
    if sys.argv and len(sys.argv) >= 2:
        mode = sys.argv[1]
    zes_app_test(mode)
