from config import *
from ZesAntaris import ZesAntarisOperator
from zesThread import FsmThread
from AntarisCtrl import AntarisCtrl
import time, os, shutil, zipfile
from flightService import shutdown_app, process_passthru_tele_cmd, process_new_file_uploaded, process_health_check, \
    process_response_register, process_reponse_point_to_target, process_response_get_current_location, \
    process_response_get_current_time, process_response_get_current_power_state, process_response_download_file_to_gs, \
    process_response_payload_power_control, download_logfile_to_groundstation, run_payload_in_flight_mode

from flightService import fsms, newFileReceived, newFilePath


def start_zes_ground_test(mythread: FsmThread):
    mythread.state = "STARTED"
    ZesAntarisOperator.ground_test_mode(mythread)
    mythread.state = "EXISTING"

def start_zes_flight_test(mythread: FsmThread):
    mythread.state = "STARTED"
    ZesAntarisOperator.power_on_and_prepare_payload_if_necessary(mythread)
    ZesAntarisOperator.one_time_flight_service_mode(mythread)
    mythread.state = "EXISTING"

def start_test_sequence(start_seq_param):
    # start all sequences
    for key in fsms:
        fsms[key].start()
        print(f'Thread {key} started')


def zes_app_test(mode='ground'):
    callback_func_list = {
        'StartSequence': start_test_sequence,
        'Shutdown': shutdown_app,
        'PassthruCmd': process_passthru_tele_cmd,
        'NewFileUploaded': process_new_file_uploaded,
        'HealthCheck': process_health_check,
        'RespRegister': process_response_register,
        'RespPointToTarget': process_reponse_point_to_target,
        'RespGetCurrentLocation': process_response_get_current_location,
        'RespGetCurrentTime': process_response_get_current_time,
        'RespGetCurrentPowerState': process_response_get_current_power_state,
        'RespDownloadFileToGS': process_response_download_file_to_gs,
        'RespPayloadPowerControl': process_response_payload_power_control,
    }

    # Create Channel to talk to Payload Controller (PC)
    channel = AntarisCtrl.create_channel(True, callback_func_list)

    if channel == None:
        print("Error : Create Channel failed")
        exit()

    # Create FSM threads  (arg : channel, thread-id, correlation_id, count, seq_id, fsm-function)
    if mode == 'ground':
        fsms[1] = FsmThread(channel, 1, 10000, 'ZES_GROUND_TEST', start_zes_ground_test)
    else:
        fsms[1] = FsmThread(channel, 1, 10000, 'ZES_FLIGHT_TEST', start_zes_flight_test)


    AntarisCtrl.register_app(channel, 10000)

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

    # replace new file, at the end of task execution
    if newFileReceived and newFilePath:
        path, filename = os.path.split(newFilePath)
        zesAppPath = HOME_FOLDER_PATH + '/zesUART/'
        payloadFilePath = zesAppPath + filename
        shutil.copyfile(newFilePath, payloadFilePath)
        with zipfile.ZipFile(payloadFilePath, 'r') as zip_ref:
            zip_ref.extractall(zesAppPath)

    AntarisCtrl.sequence_done(channel)
    AntarisCtrl.delete_channel_and_goodbye(channel)


def test2():
    run_payload_in_flight_mode()