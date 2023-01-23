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

# This file assumes that, env.json file is present at /opt/antaris/app
# location. The sample file is checked-in in conf directory

from pylibftdi import BitBangDevice
import time, sys, json

# Define error code
g_GPIO_ERROR = -1 
g_GPIO_AVAILABLE = 1
g_SLEEP_TIME_IN_SEC = 1
g_MASK_BIT_0 = 1
g_MASK_BYTE = 0xFF 

# Read config info
jsonfile = open('/opt/antaris/app/config.json', 'r')

# returns JSON object as a dictionary
jsfile_data = json.load(jsonfile)

total_gpio_pins = jsfile_data['IO_Access']['GPIO_PIN_COUNT']
print("Pin count =", total_gpio_pins)

def verify_gpio_pin(input_pin):
    status = g_GPIO_ERROR
    for i in range(int(total_gpio_pins)):
        key = 'GPIO_PIN_'+str(i)
        value = jsfile_data['IO_Access'][key]
        if int(input_pin) == int(value):
            status = g_GPIO_AVAILABLE
    return status

#device specific functions
Device = BitBangDevice('FT769754')

def api_pa_pc_read_gpio(pin):
    status = verify_gpio_pin(pin)
    if status == g_GPIO_ERROR:
        return g_GPIO_ERROR
    time.sleep(g_SLEEP_TIME_IN_SEC)
    wr_port = g_MASK_BIT_0 << int(pin)
    wr_port = g_MASK_BYTE ^ wr_port
    out = Device.direction & wr_port
    Device.direction = out
    op = (Device.port >> pin) & g_MASK_BIT_0
    return op

def api_pa_pc_write_gpio(pin, value, shouldPatch=True):
    if pin == 5 and value == 1:
        # ZES Hard patch for NRST (GPIO-5):
        # set GPIO in read mode so that the onboard pull up resistor can pull NRST up to 1
        return api_pa_pc_read_gpio(pin)

    status = verify_gpio_pin(pin)
    if status == g_GPIO_ERROR:
        return g_GPIO_ERROR
    time.sleep(g_SLEEP_TIME_IN_SEC)
    wr_port = g_MASK_BIT_0 << int(pin)
    Device.direction = Device.direction | wr_port
    if value == 0:
        wr_val = g_MASK_BYTE ^ wr_port
        Device.port = Device.port & wr_val
    else:
        Device.port = (Device.port | wr_port)
    time.sleep(g_SLEEP_TIME_IN_SEC)
    op = (Device.port >> pin) & g_MASK_BIT_0
    return op
