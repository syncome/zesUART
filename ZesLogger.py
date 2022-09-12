import datetime
import threading
import os
import zipfile
from zesConfig import LOG_TIME_FORMAT, LOG_FILE_PATH

class ZesLogger:
    @classmethod
    def zip_or_get_previous_day_log_file_name(cls):
        utcDateTime = datetime.datetime.utcnow()
        previousDay = utcDateTime - datetime.timedelta(days=1)
        utcDateStr = previousDay.strftime('%Y%m%d')
        yesterdayLogfileName = LOG_FILE_PATH + 'ZES_' + utcDateStr + '.log'
        yesterdayZipFile = LOG_FILE_PATH + 'ZES_' + utcDateStr + '.zip'
        if os.path.exists(yesterdayLogfileName):
            z = zipfile.ZipFile(yesterdayZipFile, 'w', zipfile.ZIP_DEFLATED)
            z.write(yesterdayLogfileName)
            z.close()
            os.remove(yesterdayLogfileName)
            return yesterdayZipFile
        elif os.path.exists(yesterdayZipFile):
            return yesterdayZipFile
        else:
            return None

    @classmethod
    def log(cls, cmdStr, dataStr):
        # utcNowStr,cmdStr,data
        utcDateTime = datetime.datetime.utcnow()
        utcDateStr = utcDateTime.strftime('%Y%m%d')
        # utcNowStr = utcDateTime.strftime(LOG_TIME_FORMAT)
        utcNowStr = str(utcDateTime.timestamp())
        logStr = ','.join([utcNowStr, cmdStr, dataStr])
        logfileName = 'ZES_' + utcDateStr + '.log'
        fileNameWithPath = LOG_FILE_PATH + logfileName
        lock = threading.Lock()
        lock.acquire()
        with open(fileNameWithPath, 'a+') as f:
            f.write(logStr + '\n')
        lock.release()
        from config import DEBUG
        if DEBUG:
            print(logStr)

    @classmethod
    def rename_file_downloaded(cls, fileName):
        if os.path.exists(fileName):
            os.rename(fileName, fileName + '.bak')

    @classmethod
    def clean_old_files(cls):
        utcDateTime = datetime.datetime.utcnow()
        threeDaysAgo = utcDateTime - datetime.timedelta(days=7)
        utcDateStr = threeDaysAgo.strftime('%Y%m%d')
        fileToRemove = LOG_FILE_PATH + 'ZES_' + utcDateStr + '.zip.bak'
        if os.path.exists(fileToRemove):
            os.remove(fileToRemove)
