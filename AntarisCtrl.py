from config import PLATFORM, USE_VIRTUAL_HARDWARE_CTRL
import antarisAPI.antaris_api_client as api
from antarisAPI.gen.antaris_api_types import *


class AntarisCtrl:
    @classmethod
    def get_power_status(cls, channel, correlation_id):
        api.api_pa_pc_get_current_power_state(channel, correlation_id)

    @classmethod
    def set_power_pin(cls, channel, correlation_id, on=True):
        payload_power_control_params = ReqPayloadPowerControlParams(correlation_id, 1 if on else 0)
        api.api_pa_pc_payload_power_control(channel, payload_power_control_params)

    @classmethod
    def get_sat_location(cls, channel, correlation_id):
        api.api_pa_pc_get_current_location(channel, correlation_id)

    @classmethod
    def create_secure_channel(cls, callback_func_list):
        return api.api_pa_pc_create_channel(callback_func_list)

    @classmethod
    def create_insecure_channel(cls, callback_func_list):
        return api.api_pa_pc_create_insecure_channel(callback_func_list)

    @classmethod
    def register_app(cls, channel, correlation_id):
        register_params = ReqRegisterParams(correlation_id, 0)
        api.api_pa_pc_register(channel, register_params)

    @classmethod
    def download_file_to_groundstation(cls, channel, correlation_id, filePath):
        download_file_params = ReqStageFileDownloadParams(correlation_id, filePath)
        api.api_pa_pc_stage_file_download(channel, download_file_params)

    @classmethod
    def sequence_done(cls, channel):
        sequence_done_params = CmdSequenceDoneParams(0)
        api.api_pa_pc_sequence_done(channel, sequence_done_params)

    @classmethod
    def delete_channel_and_goodbye(cls, channel):
        api.api_pa_pc_delete_channel(channel)

    @classmethod
    def respond_to_heartbeat(cls):
        # TODO:  Page 21
        # responseParam = {}
        # api.api_pa_pc_response_heart_beat(responseParam)
        pass

    @classmethod
    def respond_to_healthcheck(cls):
        # TODO: Page 21
        # responseParam: ResponseHealthCheckParams = {}
        # api.api_pa_pc_healthcheck(responseParam)
        pass


