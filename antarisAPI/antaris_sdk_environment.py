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

import os
import re
import pdb

g_ENV_FILENAME_VARIABLE="ANTARIS_ENV_CONF_FILE"
g_CONF_FILE="/opt/antaris/sdk/lib/conf/sdk_env.conf"

g_PC_IP_CONF_KEY="PAYLOAD_CONTROLLER_IP"
g_APP_IP_CONF_KEY="PAYLOAD_APP_IP"
g_LISTEN_IP_CONF_KEY="LISTEN_IP"
g_PC_API_PORT_CONF_KEY="PC_API_PORT"
g_APP_API_PORT_CONF_KEY="APP_API_PORT"

g_default_values = {    g_PC_IP_CONF_KEY: "127.0.0.1",
                        g_APP_IP_CONF_KEY: "127.0.0.1",
                        g_LISTEN_IP_CONF_KEY: "0.0.0.0",
                        g_PC_API_PORT_CONF_KEY: "50051",
                        g_APP_API_PORT_CONF_KEY: "50053"}

g_values_from_conf_file = {}

def sdk_environment_read_config():
    global g_CONF_FILE
    determine_conf_file()
    conf_file=None

    try:
        conf_file = open(g_CONF_FILE, 'r')
    except:
        return

    while True:
        line = conf_file.readline()

        if (not line):
            break

        update_a_conf(line)

    conf_file.close()

def determine_conf_file():
    global g_ENV_FILENAME_VARIABLE
    global g_CONF_FILE
    if g_ENV_FILENAME_VARIABLE in os.environ:
        g_CONF_FILE = os.environ.get(g_ENV_FILENAME_VARIABLE)

def parse_a_conf(conf_line):
    conf = {"prop": "", "value": ""}
    conf_no_comment = conf_line.split("#")
    conf_content=conf_no_comment[0]
    conf_content=re.sub(r"[\n\t\s]*", "", conf_content)
    var_and_value=conf_content.split("=")

    if (len(var_and_value) == 2):
        conf["prop"] = var_and_value[0]
        conf["value"] = var_and_value[1]

    return conf

def update_a_conf(conf_line):
    global g_values_from_conf_file
    global g_default_values

    conf = parse_a_conf(conf_line)

    # if we know this property, then save it
    if conf["prop"] in g_default_values:
        g_values_from_conf_file[conf["prop"]] = conf["value"]

def get_conf(prop_name):
    global g_values_from_conf_file
    global g_default_values

    if prop_name in g_values_from_conf_file:
        return g_values_from_conf_file[prop_name]
    elif prop_name in g_default_values:
        return g_default_values[prop_name]
    else:
        return None

#pdb.set_trace()

sdk_environment_read_config()
