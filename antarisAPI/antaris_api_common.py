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

from . import antaris_sdk_environment as environment
import pdb
import socket

g_LISTEN_IP=None
g_PAYLOAD_CONTROLLER_IP=None
g_PAYLOAD_APP_IP=None
g_PC_GRPC_SERVER_PORT=None
g_PC_GRPC_SERVER_PORT_STR=None
g_PA_GRPC_SERVER_PORT=None
g_PA_GRPC_SERVER_PORT_STR =None

def init_vars():
    global g_LISTEN_IP
    global g_PAYLOAD_CONTROLLER_IP
    global g_PC_GRPC_SERVER_PORT
    global g_PC_GRPC_SERVER_PORT_STR
    global g_PA_GRPC_SERVER_PORT
    global g_PA_GRPC_SERVER_PORT_STR

    g_LISTEN_IP=environment.get_conf(environment.g_LISTEN_IP_CONF_KEY)
    g_PAYLOAD_CONTROLLER_IP=environment.get_conf(environment.g_PC_IP_CONF_KEY)
    g_PAYLOAD_APP_IP=environment.get_conf(environment.g_APP_IP_CONF_KEY)
    g_PC_GRPC_SERVER_PORT=environment.get_conf(environment.g_PC_API_PORT_CONF_KEY)
    g_PA_GRPC_SERVER_PORT=environment.get_conf(environment.g_APP_API_PORT_CONF_KEY)
    g_PC_GRPC_SERVER_PORT_STR="{}".format(g_PC_GRPC_SERVER_PORT)
    g_PA_GRPC_SERVER_PORT_STR ="{}".format(g_PA_GRPC_SERVER_PORT)

#pdb.set_trace()
init_vars()

def is_server_endpoint_available(ip, port):
    temp_socket = socket.socket()

    try:
        temp_socket.bind((ip, port))
    except socket.error as e:
        print(e)
        return False

    temp_socket.close()
    return True
