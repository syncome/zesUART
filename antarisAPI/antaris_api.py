# Copyright 2022 Antaris Inc
#
"""
Use of this software is governed by the terms of the
Antaris SDK License Agreement entered into between Antaris
and you or your employer. You may only use this software as
permitted in that agreement. If you or your employer has not
entered into the Antaris SDK License Agreement, you are not
permitted to use this software.
"""

import threading

import antarisAPI.antaris_api_server as SERVER_SIM
import antarisAPI.gen.antaris_api_types as API_TYPES

api_debug = 0

class AntarisChannel:
    def __init__(self, grpc_handle, encryption, callback_func_list):
        self.grpc_handle = grpc_handle
        self.encryption = encryption
        self.start_sequence = callback_func_list['StartSequence']
        self.shutdown_app = callback_func_list['Shutdown']
        self.process_passthru_cmd = callback_func_list['PassthruCmd']
        self.process_new_file_uploaded = callback_func_list['NewFileUploaded']
        self.process_health_check = callback_func_list['HealthCheck']
        self.process_resp_register = callback_func_list['RespRegister']
        self.process_resp_point_to_target = callback_func_list['RespPointToTarget']
        self.process_resp_get_curr_location = callback_func_list['RespGetCurrentLocation']
        self.process_resp_get_curr_time = callback_func_list['RespGetCurrentTime']
        self.process_resp_get_curr_power_state = callback_func_list['RespGetCurrentPowerState']
        self.process_resp_download_file_to_gs = callback_func_list['RespDownloadFileToGS']
        self.process_resp_payload_power_control = callback_func_list['RespPayloadPowerControl']

# API functions called by Payload Application and served by Payload Controller
def api_pa_pc_create_channel(encryption, callback_func_list):
    print("api_pa_pc_create_channel")
    # TODO :
    # Create GRPC channel and connect with PC. Currently passing
    # grpc handle as None while creating AntarisChannel
    channel = AntarisChannel(None, encryption, callback_func_list)

    # Create simulated PC thread
    channel.sim_pc_condition = threading.Condition()
    channel.sim_pc_thread = threading.Thread(target=SERVER_SIM.simulated_pc, args=(channel, channel.sim_pc_condition,))
    channel.sim_pc_thread.start()
    return channel

def api_pa_pc_delete_channel(channel):
    print("api_pa_pc_delete_channel")
    channel.cb_api = None
    SERVER_SIM.wakeup_pc(channel, None, 0)
    channel.sim_pc_thread.join()
    return 0

def api_pa_pc_register(channel, register_params):
    print("api_pa_pc_register")
    if (api_debug):
        register_params.display()
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_register, register_params.correlation_id)
    return 0

def api_pa_pc_point_to_target(channel, point_to_target_params):
    print("api_pa_pc_point_to_target")
    if (api_debug):
        point_to_target_params.display()
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_point_to_target, point_to_target_params.correlation_id)
    return 0

def api_pa_pc_get_current_location(channel, correlation_id):
    print("api_pa_pc_get_curent_location: correlation_id : ", correlation_id)
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_get_curr_location, correlation_id)
    return 0

def api_pa_pc_get_current_time(channel, correlation_id):
    print("api_pa_pc_get_current_time: correlation_id : ", correlation_id)
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_get_curr_time, correlation_id)
    return 0

def api_pa_pc_get_current_power_state(channel, correlation_id):
    print("api_pa_pc_get_current_power_state")
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_get_curr_power_state, correlation_id)
    return 0

def api_pa_pc_download_file_to_gs(channel, download_file_params):
    print("api_pa_pc_download_file_to_gs")
    if (api_debug):
        download_file_params.display()
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_download_file_to_gs, download_file_params.correlation_id)
    return 0

def api_pa_pc_sequence_done(channel, sequence_done_params):
    print("api_pa_pc_sequence_done")
    if (api_debug):
        sequence_done_params.display()
    return 0

def api_pa_pc_payload_power_control(channel, payload_power_control_params):
    print("api_pa_pc_payload_power_control")
    if (api_debug):
        payload_power_control_params.display()
    SERVER_SIM.wakeup_pc(channel, channel.process_resp_payload_power_control, payload_power_control_params.correlation_id)
    return 0

def api_pa_pc_response_health_check(channel, response_health_check_params):
    print("api_pa_pc_response_health_check")
    if (api_debug):
        response_health_check_params.display()
    # TODO : Send health-check response to PC
    return 0
