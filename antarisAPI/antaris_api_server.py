import time
import antarisAPI.gen.antaris_api_types as API_TYPES

def simulated_pc(channel, condition):
    print("Simulated PC Started")
    condition.acquire()

    while True:
        condition.wait() # sleep until next api is called
        if channel.cb_api == None:
            print("Simulated PC Exiting")
            break
        print("Payload Controller Responded")
        if channel.cb_api == channel.process_resp_register:
            resp_register_params = API_TYPES.RespRegisterParams(channel.cb_correlation_id, 0, "auth_token")
            channel.process_resp_register(resp_register_params)
            #Start Sequence A for duration 60 seconds
            start_sequence_params = API_TYPES.StartSequenceParams(0, "Sequence_A", 60)
            channel.start_sequence(start_sequence_params)
        elif channel.cb_api == channel.process_resp_point_to_target:
            resp_point_to_target_params = API_TYPES.RespPointToTargetParams(channel.cb_correlation_id, 0)
            channel.cb_api(resp_point_to_target_params)
        elif channel.cb_api == channel.process_resp_get_curr_location:
            resp_get_curr_location_params = API_TYPES.RespGetCurrentLocationParams(channel.cb_correlation_id, 0, 100, 100, 100)
            channel.cb_api(resp_get_curr_location_params)
        elif channel.cb_api == channel.process_resp_get_curr_time:
            resp_get_curr_time_params = API_TYPES.RespGetCurrentTimeParams(channel.cb_correlation_id, 0, int(time.time()))
            channel.cb_api(resp_get_curr_time_params)
        elif channel.cb_api == channel.process_resp_get_curr_power_state:
            resp_get_power_state_params = API_TYPES.RespGetCurrentPowerStateParams(channel.cb_correlation_id, 0, 0)
            channel.cb_api(resp_get_power_state_params)
        elif channel.cb_api == channel.process_resp_download_file_to_gs:
            resp_download_file_to_gs_params = API_TYPES.RespDownloadFileToGSParams(channel.cb_correlation_id, 0)
            channel.cb_api(resp_download_file_to_gs_params)
        elif channel.cb_api == channel.process_resp_payload_power_control:
            resp_payload_power_control_params = API_TYPES.RespPayloadPowerControlParams(channel.cb_correlation_id, 0)
            channel.cb_api(resp_payload_power_control_params)

    condition.release()

def wakeup_pc(channel, cb_api, correlation_id):
    channel.sim_pc_condition.acquire()
    channel.cb_api = cb_api
    channel.cb_correlation_id = correlation_id
    channel.sim_pc_condition.notify() # signal that a new api has been called
    channel.sim_pc_condition.release()
