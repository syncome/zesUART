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

from concurrent import futures
import logging
import time

import grpc   # TODO: what is this grpc?   pip install grpcio
from antarisAPI.gen import antaris_api_pb2
from antarisAPI.gen import antaris_api_pb2_grpc
from antarisAPI import antaris_api_common as api_common

from antarisAPI.gen import antaris_api_types as api_types

api_debug = 0
g_shutdown_grace_seconds=5
g_shutdown_grace_for_grace=2

class AntarisChannel:
    def __init__(self, grpc_client_handle, grpc_server_handle, pc_to_app_server, is_secure, callback_func_list):
        self.grpc_client_handle = grpc_client_handle
        self.grpc_server_handle = grpc_server_handle
        self.pc_to_app_server = pc_to_app_server
        self.is_secure = is_secure
        self.start_sequence = callback_func_list['StartSequence']
        self.shutdown_app = callback_func_list['Shutdown']
        self.process_passthru_cmd = callback_func_list['PassthruCmd']
        self.process_health_check = callback_func_list['HealthCheck']
        self.process_resp_register = callback_func_list['RespRegister']
        self.process_resp_get_curr_location = callback_func_list['RespGetCurrentLocation']
        self.process_resp_get_curr_power_state = callback_func_list['RespGetCurrentPowerState']
        self.process_resp_stage_file_download = callback_func_list['RespStageFileDownload']
        self.process_resp_payload_power_control = callback_func_list['RespPayloadPowerControl']

class PCToAppService(antaris_api_pb2_grpc.AntarisapiApplicationCallbackServicer):
    def set_channel(self, channel):
        self.channel = channel

    def PA_StartSequence(self, request, context):
        if self.channel.start_sequence:
            app_request = api_types.peer_to_app_StartSequenceParams(request)
            app_ret = self.channel.start_sequence(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ShutdownApp(self, request, context):
        if self.channel.shutdown_app:
            app_request = api_types.peer_to_app_ShutdownParams(request)
            app_ret = self.channel.shutdown_app(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessPassThruTeleCmd(self, request, context):
        if self.channel.process_passthru_cmd:
            app_request = api_types.peer_to_app_PassthruCmdParams(request)
            app_ret = self.channel.process_passthru_cmd(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessHealthCheck(self, request, context):
        if self.channel.process_health_check:
            app_request = api_types.peer_to_app_HealthCheckParams(request)
            app_ret = self.channel.process_health_check(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessResponseRegister(self, request, context):
        if self.channel.process_resp_register:
            app_request = api_types.peer_to_app_RespRegisterParams(request)
            app_ret = self.channel.process_resp_register(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessResponseGetCurrentLocation(self, request, context):
        if self.channel.process_resp_get_curr_location:
            app_request = api_types.peer_to_app_RespGetCurrentLocationParams(request)
            app_ret =  self.channel.process_resp_get_curr_location(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessResponseGetPowerstate(self, request, context):
        if self.channel.process_resp_get_curr_power_state:
            app_request = api_types.peer_to_app_RespGetCurrentPowerStateParams(request)
            app_ret = self.channel.process_resp_get_curr_power_state(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessResponseStageFileDownload(self, request, context):
        if self.channel.process_resp_stage_file_download:
            app_request = api_types.peer_to_app_RespStageFileDownloadParams(request)
            app_ret = self.channel.process_resp_stage_file_download(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

    def PA_ProcessResponsePayloadPowerControl(self, request, context):
        if self.channel.process_resp_payload_power_control:
            app_request = api_types.peer_to_app_RespPayloadPowerControlParams(request)
            app_ret = self.channel.process_resp_payload_power_control(app_request)
            return antaris_api_pb2.AntarisReturnType(return_code = app_ret)
        else:
            return antaris_api_pb2.AntarisReturnType(return_code = api_types.AntarisReturnCode.An_NOT_IMPLEMENTED)

def api_pa_pc_create_channel_common(secure, callback_func_list):
    print("api_pa_pc_create_channel_common")

    client_handle = antaris_api_pb2_grpc.AntarisapiPayloadControllerStub(grpc.insecure_channel("{}:{}".format(api_common.LISTEN_IP, api_common.SERVER_GRPC_PORT)))
    server_handle =  grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_handle.add_insecure_port("{}:{}".format(api_common.LISTEN_IP, api_common.APP_GRPC_CALLBACK_PORT))
    pc_to_app_server = PCToAppService()
    antaris_api_pb2_grpc.add_AntarisapiApplicationCallbackServicer_to_server(pc_to_app_server, server_handle)
    channel = AntarisChannel(client_handle, server_handle, pc_to_app_server, secure, callback_func_list)
    pc_to_app_server.set_channel(channel)
    server_handle.start()

    print("started callback server and created channel")

    return channel

# API functions called by Payload Application and served by Payload Controller
def api_pa_pc_create_channel(callback_func_list):
   channel = api_pa_pc_create_channel_common(True, callback_func_list)
   return channel

def api_pa_pc_create_insecure_channel(callback_func_list):
   channel = api_pa_pc_create_channel_common(False, callback_func_list)
   return channel

def api_pa_pc_delete_channel(channel):
    global g_shutdown_grace_seconds
    global g_shutdown_grace_for_grace
    quiesce_time = g_shutdown_grace_seconds + g_shutdown_grace_for_grace

    print("api_pa_pc_delete_channel, stopping callback server")
    channel.grpc_server_handle.stop(g_shutdown_grace_seconds).wait()
    print("callback server successfully stopped, sleeping for quiesce time (s) = {}".format(quiesce_time))
    time.sleep(quiesce_time)
    return 0

def api_pa_pc_register(channel, register_params):
    print("api_pa_pc_register")
    if (api_debug):
        register_params.display()
    peer_params = api_types.app_to_peer_ReqRegisterParams(register_params)

    peer_ret = channel.grpc_client_handle.PC_register(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_get_current_location(channel, correlation_id):
    print("api_pa_pc_get_curent_location: correlation_id : ", correlation_id)

    peer_ret = channel.grpc_client_handle.PC_get_current_location(antaris_api_pb2.AntarisCorrelationId(correlation_id = correlation_id))

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_get_current_power_state(channel, correlation_id):
    print("api_pa_pc_get_current_power_state")

    peer_ret = channel.grpc_client_handle.PC_get_current_power_state(antaris_api_pb2.AntarisCorrelationId(correlation_id = correlation_id))

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_stage_file_download(channel, download_file_params):
    print("api_pa_pc_stage_file_download")
    if (api_debug):
        download_file_params.display()
    peer_params = api_types.app_to_peer_ReqStageFileDownloadParams(download_file_params)

    peer_ret = channel.grpc_client_handle.PC_stage_file_download(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_sequence_done(channel, sequence_done_params):
    print("api_pa_pc_sequence_done")
    if (api_debug):
        sequence_done_params.display()
    peer_params = api_types.app_to_peer_CmdSequenceDoneParams(sequence_done_params)

    peer_ret = channel.grpc_client_handle.PC_sequence_done(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_payload_power_control(channel, payload_power_control_params):
    print("api_pa_pc_payload_power_control")
    if (api_debug):
        payload_power_control_params.display()
    peer_params = api_types.app_to_peer_ReqPayloadPowerControlParams(payload_power_control_params)

    peer_ret = channel.grpc_client_handle.PC_payload_power_control(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_response_health_check(channel, response_health_check_params):
    print("api_pa_pc_response_health_check")
    if (api_debug):
        response_health_check_params.display()
    peer_params = api_types.app_to_peer_RespHealthCheckParams(response_health_check_params)

    peer_ret = channel.grpc_client_handle.PC_response_health_check(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code

def api_pa_pc_response_shutdown(channel, response_shutdown_params):
    print("api_pa_pc_response_shutdown")
    if (api_debug):
        response_shutdown_params.display()
    peer_params = api_types.app_to_peer_RespShutdownParams(response_shutdown_params)

    peer_ret = channel.grpc_client_handle.PC_response_shutdown(peer_params)

    if (api_debug):
        print("Got return code {} => {}".format(peer_ret.return_code, api_types.AntarisReturnCode.reverse_dict[peer_ret.return_code]))

    return peer_ret.return_code
