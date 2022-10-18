from AntarisCtrl import AntarisCtrl
import serial
import time
from configparser import ConfigParser
from config import HOME_FOLDER_PATH

from config import SERIAL_DEVICE

from ZesLogger import ZesLogger
from zesConfig import *

from config import DEBUG, USE_VIRTUAL_PAYLOAD
from zesThread import FsmThread

if PLATFORM == 'ANTARIS':
    from gpio_antaris import read_STATUS_pin, set_NRESET_pin, set_POWER_pin, get_POWER_state
elif PLATFORM == 'RPI':
    from gpio_rpi import read_STATUS_pin, set_NRESET_pin, set_POWER_pin, get_POWER_state
else:
    from gpio_virtual import read_STATUS_pin, set_NRESET_pin, set_POWER_pin, get_POWER_state





class ZesAntarisOperator:
    #
    # CMD20 will be the selector
    @classmethod
    def save_mblk_to_file(cls, key, value):
        config = ConfigParser()
        configPath = HOME_FOLDER_PATH + '/zesUART/mblk.ini'
        config.read(configPath)
        if not config.has_section('MBLK'):
            config.add_section('MBLK')
        config.set('MBLK', key, value)
        with open(configPath, 'w') as f:
            config.write(f)

    @classmethod
    def get_saved_current_mblk(cls) -> int:
        config = ConfigParser()
        configPath = HOME_FOLDER_PATH + '/zesUART/mblk.ini'
        config.read(configPath)
        mblk = 0
        try:
            current_mblk = config.get('MBLK', 'current_mblk')
            mblk = int(current_mblk)
        except Exception as err:
            ZesLogger.log('ERR', f'Cannot convert current_mblk to int: {current_mblk}, use default 0 instead')
        return mblk

    @classmethod
    def assure_mblk(cls, mblk: int):
        if mblk < 0 or mblk > 7:
            # log
            return False
        return True

    @classmethod
    def get_bits_of_binary(cls, msgBits: bin, locations):
        lowIndex = locations[0]
        highIndex = locations[1]
        return bin(msgBits >> locations[0] & bin(2**(highIndex - lowIndex + 1) - 1) )

    @classmethod
    def convert_bytesarray_to_binary_str(cls, bytesArray):
        binStr = ''
        for each in bytesArray:
            binStr += '{:08b}'.format(each)
        return binStr

    @classmethod
    def get_bits_of_bytesarray(cls, bytesArray: bytearray, locations):   # MSB first
        if bytesArray is None:
            return ''
        lowIndex = locations[0]
        highIndex = locations[1]
        bytesLowIndex = int(lowIndex / 8)
        bytesHighIndex = int(highIndex / 8)

        bytesArrayLength = len(bytesArray)

        if bytesHighIndex >= bytesArrayLength or bytesLowIndex < 0 or bytesLowIndex > bytesHighIndex:
            if DEBUG: print('Incorrect bit index and bytesArray: ' + str(bytesArray))
            return
        bytesArraySlice = bytesArray[bytesArrayLength -bytesHighIndex - 1 : bytesArrayLength - bytesLowIndex]
        binaryStr = cls.convert_bytesarray_to_binary_str(bytesArraySlice)
        binaryStrLen = len(binaryStr)
        highEnd = binaryStrLen - (lowIndex - bytesLowIndex * 8)
        lowEnd = binaryStrLen - (highIndex - bytesLowIndex * 8 + 1)
        bitsStr = binaryStr[lowEnd:highEnd]
        return bitsStr


    def send_to_serial(cls, cmd):
        while True:
            numofFail = 0
            try:
                ser = serial.Serial(port=SERIAL_DEVICE, baudrate=SERIAL_BAUDRATE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.1)
                break
            except Exception as err:
                ZesLogger.log('ERR', f'Cannot open serial port {SERIAL_DEVICE}')
                if DEBUG:
                    print(f'[Debug] >>>  Could not open port, retrying. error as follows: {err}')

                numofFail += 1
                if numofFail > 20:
                    # Reset Board
                    if DEBUG:
                        print('[Debug] >>>  Could not open port, failed 20 times, aborted.')
                        raise ValueError(err)

                time.sleep(1 + numofFail)
        ser.write(cmd)
        ZesLogger.log("TX " + cmd.hex(), "")
        time.sleep(0.1)
        # msg = ser.read(size=SERIAL_READ_BUFFER_SIZE)
        line = ser.readline()

        if not line and USE_VIRTUAL_PAYLOAD:
            example = EXAMPLE_RESPONSE.get(cmd.hex()[0], '---')
            line = bytearray.fromhex(example)

            ZesLogger.log("RX VIRTUAL " + cmd.hex(), line.hex())
        else:
            ZesLogger.log("RX " + cmd.hex(), line.hex())
        return line


    @classmethod
    def build_cmd_and_send(cls, cmd, mblk):
        if not cls.assure_mblk(mblk):
            return
        zesCmd = (cmd | CMD43_DEFAULT | mblk).to_bytes(1, SEQ)
        obj = cls()
        response = obj.send_to_serial(zesCmd)
        return response

    @classmethod
    def test_operation_A(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Test A')
        msg = cls.build_cmd_and_send(cmd=CMD75_TEST_OP_A, mblk=mblk)
        return msg

    @classmethod
    def test_operation_B(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Test B')
        msg = cls.build_cmd_and_send(cmd=CMD75_TEST_OP_B, mblk=mblk)
        return msg

    @classmethod
    def write_operation_A(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Write A')
        msg = cls.build_cmd_and_send(cmd=CMD75_WRITE_A, mblk=mblk)
        return msg

    @classmethod
    def write_operation_B(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Write B')
        msg = cls.build_cmd_and_send(cmd=CMD75_WRITE_B, mblk=mblk)
        return msg

    @classmethod
    def read_check_A(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Read A')
        msg = cls.build_cmd_and_send(cmd=CMD75_RD_CK_A, mblk=mblk)
        return msg

    @classmethod
    def read_check_B(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Read B')
        msg = cls.build_cmd_and_send(cmd=CMD75_RD_CK_B, mblk=mblk)
        return msg

    @classmethod
    def service_update(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Service Update')
        msg = cls.build_cmd_and_send(cmd=CMD75_SVC_REG, mblk=mblk)
        return msg

    @classmethod
    def generate_output(cls, mblk):
        if DEBUG: print('[Debug] >>>  Performing Output Generation')
        msg = cls.build_cmd_and_send(cmd=CMD75_OUT_GEN, mblk=mblk)
        return msg

    @classmethod
    def test(cls):
        mblk = 0b000
        cls.test_operation_A(mblk=mblk)
        time.sleep(1)
        cls.test_operation_B(mblk=mblk)
        time.sleep(1)
        cls.write_operation_A(mblk=mblk)
        time.sleep(1)
        cls.read_check_A(mblk=mblk)
        time.sleep(1)
        cls.write_operation_B(mblk=mblk)
        time.sleep(1)
        cls.read_check_B(mblk=mblk)
        time.sleep(1)
        cls.service_update(mblk=mblk)
        time.sleep(1)
        cls.generate_output(mblk=mblk)
        time.sleep(1)


    @classmethod
    def check_FLAG(cls):
        flagStatus = read_STATUS_pin()
        if flagStatus:
            return 'OK'
        else:
            return 'FAIL'

    @classmethod
    def check_TestSta(self, msg):
        bitsStr = self.get_bits_of_bytesarray(msg, TestSta_Loc)
        if bitsStr == '01':
            return 'SRT'
        elif bitsStr == '10':
            return 'OK'
        elif bitsStr == '11':
            return 'HRT'
        else:
            return 'HRT'

    @classmethod
    def check_WriteSta(self, msg):
        bitsStr = self.get_bits_of_bytesarray(msg, Wrt_Loc)
        if bitsStr == '10':
            return 'FAIL'
        elif bitsStr == '01':
            return 'OK'
        elif bitsStr == '11':
            return 'HRT'
        else:
            return 'HRT'

    @classmethod
    def check_ReadReset(self, msg):  # TODO: Replace repair bit
        bitsStr = self.get_bits_of_bytesarray(msg, Reset_Loc)
        if bitsStr == '01':
            return 'SRT'
        else:
            return 'OK'

    @classmethod
    def check_RepairSta(self, msg):  # TODO: Replace repair bit
        bitsStr = self.get_bits_of_bytesarray(msg, Wrt_Loc)
        if bitsStr == '10':
            return 'REPAIR'
        elif bitsStr == '01':
            return 'HRT'
        else:
            return 'OK'

    @classmethod
    def hard_reset(cls, mythread: FsmThread):
        if DEBUG: print('[Debug] >>>  Performing hard reset')
        set_POWER_pin(mythread, False)
        time.sleep(1)
        set_NRESET_pin(False)
        time.sleep(1)
        set_POWER_pin(mythread, True)
        time.sleep(2)
        set_NRESET_pin(True)
        time.sleep(1)

    @classmethod
    def soft_reset(cls):
        if DEBUG: print('[Debug] >>>  Performing soft reset')
        set_NRESET_pin(False)
        time.sleep(1)
        set_NRESET_pin(True)
        time.sleep(1)


    @classmethod
    def power_on_and_prepare_payload_if_necessary(cls, mythread: FsmThread):
        if not get_POWER_state(mythread):
            ZesLogger.log(cmdStr='SYS', dataStr=f'Payload power off, re-init..')
            cls.hard_reset(mythread)
            cls.prepare_flight_mode(mythread)
            time.sleep(1)


    @classmethod
    def ground_test_mode(cls, mythread:FsmThread):
        avail_memblks = []
        mblk = 0  # starting from zero
        needHRT = True
        MAX_RETRY = 20
        while mblk < 8:
            for retry in range(MAX_RETRY):  # for each mblk
                print(f'[Debug] >>>  Trying for the {retry+1} time....')
                if needHRT:
                    cls.hard_reset(mythread)
                    needHRT = False

                flagStatus = cls.check_FLAG()
                if flagStatus == 'FAIL':
                    needHRT = True
                    continue

                status = ''
                msg = cls.test_operation_A(mblk=mblk)
                status = cls.check_TestSta(msg)
                if status == 'SRT':
                    mblk += 1
                    cls.soft_reset()
                    needHRT = False
                    continue  # start the new loop
                elif status == 'HRT':
                    needHRT = True
                    continue  # start the new loop
                elif status == 'OK':
                    print('[Debug] >>>  Test A passed.')

                status = ''
                msg = cls.test_operation_B(mblk=mblk)
                status = cls.check_TestSta(msg)
                if status == 'SRT':
                    mblk += 1
                    cls.soft_reset()
                    needHRT = False
                    continue  # start the new loop
                elif status == 'HRT':
                    needHRT = True
                    continue  # start the new loop
                elif status == 'OK':
                    print('[Debug] >>>  Test A passed.')

                status = ''
                softFailCount = 0
                hardFailCount = 0
                while status != 'OK':
                    msg = cls.write_operation_A(mblk=mblk)
                    status = cls.check_WriteSta(msg)

                    if status == 'FAIL':
                        softFailCount += 1
                        if softFailCount < MAX_WRITE_FAIL_RETRY:
                            time.sleep(1)
                            continue   # try again to write
                        else:  # still fail, change to another block
                            mblk += 1
                            status = 'HRT'
                            ZesLogger.log(cmdStr='SYS', dataStr=f'MBLK {mblk} tested bad for write_operation_A')
                            break
                    elif status == 'HRT':
                        hardFailCount += 1
                        if hardFailCount > 3:
                            break

                if status == 'HRT':
                    needHRT = True
                    continue   # start the new loop


                ###########
                status = ''
                msg = cls.read_check_A(mblk=mblk)
                status = cls.check_ReadReset(msg)
                if status == 'SRT':
                    mblk += 1
                    cls.soft_reset()
                else:
                    print('[Debug] >>>  Reset Check A passed.')
                ############

                status = ''
                softFailCount = 0
                hardFailCount = 0
                while status != 'OK':
                    msg = cls.write_operation_B(mblk=mblk)
                    status = cls.check_WriteSta(msg)

                    if status == 'FAIL':
                        softFailCount += 1
                        if softFailCount < MAX_WRITE_FAIL_RETRY:
                            time.sleep(1)
                            continue  # try again to write
                        else:  # still fail, change to another block
                            mblk += 1
                            status = 'HRT'
                            ZesLogger.log(cmdStr='SYS', dataStr=f'MBLK {mblk} tested bad for write_operation_B')
                            break
                    elif status == 'HRT':
                        hardFailCount += 1
                        if hardFailCount > 3:
                            break

                if status == 'HRT':
                    needHRT = True
                    continue

                ###########
                status = ''
                msg = cls.read_check_B(mblk=mblk)
                status = cls.check_ReadReset(msg)
                if status == 'SRT':
                    mblk += 1
                    cls.soft_reset()
                else:
                    print('[Debug] >>>  Reset Check B passed.')
                ############


                if retry < MAX_RETRY:
                    avail_memblks.append(str(mblk))
                    ZesLogger.log(cmdStr='SYS', dataStr=f'Ground Mode: MBLK {mblk} tested OK')
                    break
                else:
                    ZesLogger.log(cmdStr='SYS', dataStr=f'Ground Mode Test Failed: no working MBLK found after {MAX_RETRY} tries.')
                # return

            mblk += 1

        # save avail_memblks
        avail_memblks_str = ','.join(avail_memblks)
        ZesLogger.log(cmdStr='SYS', dataStr=f'Avail mblks: ' + avail_memblks_str)
        cls.save_mblk_to_file('current_mblk', avail_memblks[0])
        cls.save_mblk_to_file('available_mblks', avail_memblks_str)

        if DEBUG:
            if PLATFORM == "ANTARIS" and len(avail_memblks_str) > 0:
                print("\n\n[Debug] >>> Ground Test Passed. \n\n")
            elif PLATFORM == "WINDOWS" and len(avail_memblks_str) > 0:
                print("\n\n[Debug] >>> Ground Test Passed on Experimental Device. \n\n")
            else:
                print("\n\n[Debug] >>> Ground Test not passed. \n\n")


    @classmethod
    def prepare_flight_mode(cls, mythread: FsmThread):
        needHRT = False
        mblk = cls.get_saved_current_mblk()
        MAX_RETRY = 20
        for retry in range(MAX_RETRY):
            if needHRT:
                cls.hard_reset(mythread)

            flagStatus = cls.check_FLAG()
            if flagStatus == 'FAIL':
                ZesLogger.log(cmdStr='SYS', dataStr=f'Flag Status Fail, hard resetting...')
                needHRT = True
                continue

            msg = cls.test_operation_A(mblk=mblk)
            status = cls.check_TestSta(msg)
            if status == 'SRT':
                ZesLogger.log(cmdStr='SYS', dataStr=f'TestA Fail, soft resetting...')
                cls.soft_reset()              # test operation fail, try next memory block
                needHRT = False
                continue
            elif status == 'HRT':
                ZesLogger.log(cmdStr='SYS', dataStr=f'TestA Fail, hard resetting...')
                needHRT = True
                continue  # start the new loop

            status = ''
            softFailCount = 0
            hardFailCount = 0
            while status != 'OK':
                msg = cls.write_operation_A(mblk=mblk)
                status = cls.check_WriteSta(msg)
                if status == 'FAIL':
                    softFailCount += 1

                    if softFailCount > MAX_WRITE_FAIL_RETRY:
                        ZesLogger.log(cmdStr='SYS', dataStr=f'WriteA Fail, aborting...')
                        break # give up trying
                    else:
                        ZesLogger.log(cmdStr='SYS', dataStr=f'WriteA Fail, retrying {softFailCount}...')
                        time.sleep(1)  # wait for 1 sec and try again
                        continue
                elif status == 'HRT':
                    hardFailCount += 1
                    ZesLogger.log(cmdStr='SYS', dataStr=f'WriteA Hard Fail, retrying {hardFailCount}...')
                    if hardFailCount > 3:
                        break

            if status == 'FAIL':
                ZesLogger.log(cmdStr='SYS', dataStr=f'WriteA Fail, max retry reached, soft resetting...')
                mblk += 1
                cls.soft_reset()  # reset and try next memory block
                needHRT = False
                continue
            elif status == 'HRT':
                ZesLogger.log(cmdStr='SYS', dataStr=f'WriteA Hard Fail, max retry reached, hard resetting...')
                needHRT = True
                continue

            ZesLogger.log(cmdStr='SYS', dataStr=f'Flight Mode Ready')
            cls.save_mblk_to_file('current_mblk', str(mblk))
            return True

        ZesLogger.log(cmdStr='SYS', dataStr=f'Flight Mode Prepation Failed: no working MBLK found after {MAX_RETRY} tries.')
        return False

    @classmethod
    def one_time_flight_service_mode(cls, mythread: FsmThread):
        status = ""
        mblk = cls.get_saved_current_mblk()
        current_trail = 0
        MAX_RETRY = 20
        while status in ["", "HRT"] and current_trail < MAX_RETRY:
            current_trail += 1
            if status == "HRT":
                cls.hard_reset(mythread)
                cls.prepare_flight_mode(mythread)
            msg = cls.read_check_A(mblk=mblk)
            status = cls.check_RepairSta(msg)
            if status == 'REPAIR':
                cls.service_update(mblk=mblk)

        if status == "HRT" and current_trail >= MAX_RETRY:
            ZesLogger.log(cmdStr='SYS', dataStr=f'Read Checkk Operation A failed {MAX_RETRY} times, aborting')
        else:
            if DEBUG: print('[Debug] >>> Flight Operation Completed.')
