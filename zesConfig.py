from config import *
import os

TASK_PERIODIC_SECONDS = 10 * 60


CMD75_TEST_OP_A = 0b000 << 5
CMD75_TEST_OP_B = 0b001 << 5
CMD75_WRITE_A = 0b010 << 5
CMD75_WRITE_B = 0b011 << 5
CMD75_RD_CK_A = 0b100 << 5
CMD75_RD_CK_B = 0b101 << 5
CMD75_SVC_REG = 0b110 << 5
CMD75_OUT_GEN = 0b111 << 5
#
CMD43_DEFAULT = 0b00 << 3

SEQ = 'big'  # MSB FIRST
NUM_OF_DUPLICATE = 3
SERIAL_READ_BUFFER_SIZE = 128  # 128-bit per stream, multiplied 3 times

# SERIAL_DEVICE = 'COM5'
SERIAL_BAUDRATE = 9600


# def add_offset_to_tuple(tup, offset):
#     # Convert the tuple to a list
#     lst = list(tup)
#
#     # Add the offset value to each element in the list
#     lst = [x + offset for x in lst]
#
#     # Convert the list back to a tuple
#     new_tup = tuple(lst)
#     print(new_tup)
#     return new_tup
#
# offset = 8   # For version Prof Amel
# Out A B C register locations
POL_Counter_Loc     = (0, 7)
APG0_Loc            = (8, 13)
Wrt_Loc             = (14, 15)
FPGA2_Loc           = (16, 16)
TestSta_Loc         = (17, 18)
Reset_Loc           = (19, 20)
APG3_Loc            = (21, 36)
APG2_Loc            = (37, 52)
APG1_Loc            = (53, 68)
AZ_Loc              = (69, 69)
ErDaC_Loc           = (70, 93)
ErErc_Loc           = (94, 117)
Cycle_Loc           = (118, 127)
OpCode_Loc          = (128, 135)




LOG_FILE_PATH = HOME_FOLDER_PATH + "/zesUART/log/"
if not os.path.exists(LOG_FILE_PATH):
    os.makedirs(LOG_FILE_PATH)
    print("Log folder created.")

LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

MAX_WRITE_FAIL_RETRY = 3




reg_name = ["Others_Loc",
"Wrt_Loc",
"FPGA2_Loc",
"TestSta_Loc ",
"Reset_Loc",
"APG2_Loc",
"APG1_Loc",
"APG0_Loc",
"AZ_Loc",
"ErDaC_Loc",
"ErErc_Loc",
"Cycle_Loc",
"OpCode_Loc"]



reg_location = [
APG0_Loc,
Wrt_Loc,
FPGA2_Loc,
TestSta_Loc,
Reset_Loc,
APG3_Loc,
APG2_Loc,
APG1_Loc,
AZ_Loc,
ErDaC_Loc,
ErErc_Loc,
Cycle_Loc,
OpCode_Loc]




EXAMPLE_RESPONSE = {
    '0': '00000000000000000000000000000400',
    # '0': '',
    '2': '20000000000000000000000000000400',
    # '2': '',
    '4': '40000000000000000000000000000040', # GOOD
    # '4': '40000000000000000000000000000080',   # FAIL WRITE A
    '6': '60000000000000000000000000000040',
    '8': '80ffc000000000000000000000000000',
    'a': 'a0ffc000000000000000000000000000'
}

