from ZesAntaris import ZesAntarisOperator
from AntarisCtrl import AntarisCtrl
from zesThread import FsmThread
import time

from antarisAPI.gen.antaris_api_types import *
from ZesLogger import ZesLogger
from config import *
import shutil
from config import *
import os
import zipfile



# global channel
#
# global fsms


# channel = None


fsms = dict()

power_status = 0




def get_thread_by(correlation_id: int):
    global fsms
    threadID = int(correlation_id / 10000)
    if threadID in fsms:
        return fsms[threadID]
    else:
        return None

def wakeup_seq_fsm(correlation_id: int):
    myThread = get_thread_by(correlation_id)
    if myThread:
        myThread.condition.acquire()
        myThread.condition.notify()
        myThread.condition.release()
    else:
        print(f"Thread not found for correlation_id={correlation_id}")

def shutdown_app(shutdown_param: ShutdownParams):
    pass

def start_sequence(start_seq_param: StartSequenceParams):
    # start all sequences
    global fsms
    for key in fsms:
        fsms[key].start()


def process_passthru_tele_cmd(param: PassthruCmdParams):
    cmd = param.passthru_cmd
    pass

# DELETED in ver 0.3
# def process_new_file_uploaded(param: NewFileUploadedParams):
#     newFileReceived = True
#     filepath = param.file_path
#     if DEBUG: print(f"New file uploaded at: {filepath}")


def process_response_register(param: RespRegisterParams):
    correlation_id = param.correlation_id


def process_reponse_point_to_target(resp_point_to_target_param):
    if DEBUG: print("process_response_point_to_target")
    pass


def process_response_get_current_location(param: RespGetCurrentLocationParams):
    ZesLogger.log(cmdStr='LOC', dataStr=f'Lon:{param.longitude}, Lat:{param.latitude}, Alt:{param.altitude}')
    correlation_id = param.correlation_id
    wakeup_seq_fsm(correlation_id)


# DELETED IN VER 0.3
# def process_response_get_current_time(param: RespGetCurrentTimeParams):
#     ZesLogger.log(cmdStr='TIM', dataStr=f'Ctl Tm:{param.epoch_time}, Sys Tm:{time.time()}')
#     correlation_id = param.correlation_id
#     wakeup_seq_fsm(correlation_id)


def process_response_get_current_power_state(param: RespGetCurrentPowerStateParams):
    if DEBUG: print("process_response_get_current_power_state : ", param)
    correlation_id = param.correlation_id
    relatedThread = get_thread_by(correlation_id)
    relatedThread.is_pl_power_on = param.power_state == "ON"   # TODO: Check and verify
    wakeup_seq_fsm(correlation_id)


def process_response_download_file_to_gs(param: RespStageFileDownloadParams):
    if DEBUG: print("process_response_download_file_to_gs : ", param.__str__())
    correlation_id = param.correlation_id
    isSuccess = param.req_status == 0
    relatedThread = get_thread_by(correlation_id)
    if relatedThread:
        if isSuccess:
            relatedThread.state = "FILE_DOWNLOADED"
        else:
            relatedThread.state = "FILE_DOWNLOAD_FAILED"
    wakeup_seq_fsm(correlation_id)


def process_health_check(health_check_param: RespHealthCheckParams):
    if DEBUG: print("process_health_check", health_check_param.__str__())
    pass


def process_response_payload_power_control(param: RespPayloadPowerControlParams):
    if DEBUG: print("process_response_payload_power_control", param.__str__())
    correlation_id = param.correlation_id
    relatedThread = get_thread_by(correlation_id)
    if relatedThread.will_power_on is not None:
        relatedThread.is_pl_power_on = relatedThread.will_power_on
        relatedThread.will_power_on = None
    wakeup_seq_fsm(correlation_id)




def start_zes_app(mythread: FsmThread):
    mythread.state = "STARTED"
    ZesAntarisOperator.power_on_and_prepare_payload_if_necessary(mythread)
    ZesAntarisOperator.one_time_flight_service_mode(mythread)
    mythread.state = "EXISTING"


def monitor_zes_FLAG(mythread: FsmThread):
    mythread.state = "STARTED"

    mythread.state = "EXISTING"
    pass


def antaris_satellite_status(mythread: FsmThread):
    mythread.state = "STARTED"

    # AntarisCtrl.get_controller_time(mythread.channel, mythread.correlation_id)
    # mythread.correlation_id += 1
    # mythread.state = "WAITING_FOR_GET_TIME"
    # mythread.condition.acquire()
    # mythread.condition.wait()

    AntarisCtrl.get_sat_location(mythread.channel, mythread.correlation_id)
    mythread.correlation_id += 1
    mythread.state = "WAITING_FOR_GET_SAT_LOCATION"
    mythread.condition.acquire()
    mythread.condition.wait()

    # Tell PC that current sequence is done
    AntarisCtrl.sequence_done(mythread.channel)
    mythread.state = "EXITING"
    print("sequence_a_fsm : state : ", mythread.state)
    mythread.condition.release()


def download_logfile_to_groundstation(mythread: FsmThread):
    mythread.state = "STARTED"
    yesterdayZipLogFile = ZesLogger.zip_or_get_previous_day_log_file_name()
    if yesterdayZipLogFile:
        retry = 0
        while mythread.state != "FILE_DOWNLOADED" and retry < 5:
            retry += 1
            AntarisCtrl.download_file_to_groundstation(mythread.channel, mythread.correlation_id, yesterdayZipLogFile)
            mythread.condition.acquire()
            mythread.condition.wait()
            time.sleep(1)

        if mythread.state == "FILE_DOWNLOADED":
            ZesLogger.rename_file_downloaded(yesterdayZipLogFile)
            ZesLogger.clean_old_files()
        else:
            print('Can not download file')

    ZesLogger.clean_old_files()
    mythread.state = "EXISTING"
    pass


def run_payload_in_flight_mode():
    global fsms

    callback_func_list = {
        'StartSequence': start_sequence,
        'Shutdown': shutdown_app,
        'PassthruCmd': process_passthru_tele_cmd,
        # 'NewFileUploaded': process_new_file_uploaded,
        'HealthCheck': process_health_check,
        'RespRegister': process_response_register,
        # 'RespPointToTarget': process_reponse_point_to_target,
        'RespGetCurrentLocation': process_response_get_current_location,
        # 'RespGetCurrentTime': process_response_get_current_time,
        'RespGetCurrentPowerState': process_response_get_current_power_state,
        'RespStageFileDownload': process_response_download_file_to_gs,
        'RespPayloadPowerControl' : process_response_payload_power_control,
    }



    # Create Channel to talk to Payload Controller (PC)
    channel = AntarisCtrl.create_insecure_channel(callback_func_list)

    if DEBUG: time.sleep(2)  # wait emulated PC to start

    if channel == None:
        print("Error : Create Channel failed")
        exit()

    # Create FSM threads  (arg : channel, thread-id, correlation_id, count, seq_id, fsm-function)
    fsms[1] = FsmThread(channel, 1, 10000, 'ZES_Main', start_zes_app)
    fsms[2] = FsmThread(channel, 2, 20000, 'ZES_Monitoring', monitor_zes_FLAG)
    fsms[3] = FsmThread(channel, 3, 30000, 'Antaris_Status', antaris_satellite_status)

    AntarisCtrl.register_app(channel, 10000)

    while fsms[1].state == "NOT_STARTED":
        if DEBUG: print(f'{fsms[1].seq_id} is not started yet, waiting PC to initialize and start')
        time.sleep(1)

        # Wait for all FSM threads to complete
    for key in fsms:
        if fsms[key].state != "NOT_STARTED":
            fsms[key].join()

    # all threads completed, logging finished.  Download file to ground station if necessary
    fsms[4] = FsmThread(channel, 4, 40000, 'ZES_Download_Log', download_logfile_to_groundstation)
    fsms[4].start()
    fsms[4].join()

    # DELETED IN VER 0.3
    # # replace new file, at the end of task execution
    # if newFileReceived and newFilePath:
    #     path, filename = os.path.split(newFilePath)
    #     zesAppPath = HOME_FOLDER_PATH + '/zesUART/'
    #     payloadFilePath = zesAppPath + filename
    #     shutil.copyfile(newFilePath, payloadFilePath)
    #     with zipfile.ZipFile(payloadFilePath, 'r') as zip_ref:
    #         zip_ref.extractall(zesAppPath)

    AntarisCtrl.sequence_done(channel)
    AntarisCtrl.delete_channel_and_goodbye(channel)
