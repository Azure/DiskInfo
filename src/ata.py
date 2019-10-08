"""
    Copyright (c) Microsoft Corporation
"""

import time
import logging

from binascii       import hexlify, unhexlify
from .constants     import *
from .ioctl         import GetATAIdentify, GetATASMARTLog, GetATAGPLLog
from .datahandle    import parseLog

# ATA Command Opcodes
ATA_READ_LOG_EXT                = 0x2F

# ATA Log Page Identifiers
ATA_LOG_DIRECTORY               = 0x00
ATA_LOG_SMART_ERROR_SUM         = 0x01
ATA_LOG_SMART_ERROR_COMP        = 0x02
ATA_LOG_SMART_ERROR_COMP_EXT    = 0x03
ATA_LOG_DEVICE_STATS            = 0x04
ATA_LOG_SMART_SELF_TEST         = 0x06
ATA_LOG_SMART_SELF_TEST_EXT     = 0x07
ATA_LOG_SMART_POWER_CONDITION   = 0x08
ATA_LOG_PENDING_DEFECTS         = 0x0C
ATA_LOG_NCQ_CMD_ERROR_LOG       = 0x10
ATA_LOG_SATA_PHY_EVENT_COUNTER  = 0x11
ATA_LOG_IDENTIFY                = 0x30

# Identify Support Bit Identifiers
WORD76_NCQ_FEATURE_BIT          = (0x01 << 8)
WORD76_SATA_PHY_EVENT_COUNT_BIT = (0x01 << 10)
WORD82_SMART_FEATURE_BIT        = (0x01 << 0)
WORD84_SMART_ERR_LOG_BIT        = (0x01 << 0)
WORD84_GPL_FEATURE_BIT          = (0x01 << 5)

# Optional log support bit identifiers
SMART_FEAT_SET_BIT              = (0x01 << 0)
GPL_BIT                         = (0x01 << 1)
SMART_ERR_LOG_BIT               = (0x01 << 2)
NCQ_BIT                         = (0x01 << 3)
SATA_PHY_EVENT_COUNT_BIT        = (0x01 << 4)

def GetATADeviceLog(diskNumber, logId, page, isSMART):
    if (isSMART):
        # SMART Logs are fetched using Property Standard Query IOCTL.
        return GetATASMARTLog(diskNumber, logId)
    else:
        # GPL Logs are fetched using pass through IOCTL and thus must pass the command opcode.
        return GetATAGPLLog(diskNumber, logId, page, ATA_READ_LOG_EXT)


def storeATADeviceVendorUniqueLogs(diskNumber, model, devicedict, drive, itsaresult, fwRev):
    GETVULOGS = itsaresult[2]
    logging.debug("GETVULOGS {0}".format(GETVULOGS))
    if GETVULOGS is not None:
        logging.debug("calling GETVULOGS({0}, {1}, {2})".format(drive,model,fwRev))
        vuLogs = GETVULOGS(drive, model, fwRev)
        logging.debug("vuLogs {0}".format(vuLogs))
        if vuLogs is not None:
            for logpage in vuLogs:
                logging.debug("logpage {0}".format(logpage))
                # logpage should be a tuple or list of length 3
                logpagelen = len(logpage)
                if ( (3 <= logpagelen) and (logpagelen < 4) ):
                    logpageid   = logpage[0]
                    logpagejson = logpage[1]
                    isSmart     = logpage[2]
                    
                    if ((logpageid >= 0xA0) and (logpageid <= 0xDF)):
                        logbuffer =  GetATADeviceLog(diskNumber, logpageid, 0, isSmart)
                    else:
                        # Log page is not in legal VU range.
                        logbuffer = 0
                    
                    time.sleep(LOG_FETCH_DELAY)
                    logging.debug("logbuffer {0}".format(logbuffer))
                    if logbuffer != 0:
                        logpagejson = logPageDirVu() + logpagejson
                        logging.debug("enter parseLog {0}".format(logpagejson))
                        devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logpagejson, True))
                        logging.debug("leave parseLog {0}".format(logpagejson))
                else:
                    logging.warning("Invalid VU log page information provided")


def storeATADeviceGPLLogs(diskNumber, devicedict, logSupport):
    isSmart = False
    
    logbuffer =  GetATADeviceLog(diskNumber, ATA_LOG_DIRECTORY, 0, isSmart)
    if logbuffer != 0:
        devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"ATA/Directory.json", True))
    time.sleep(LOG_FETCH_DELAY)
    
    if (logSupport & NCQ_BIT):
        logbuffer =  GetATADeviceLog(diskNumber, ATA_LOG_NCQ_CMD_ERROR_LOG, 0, isSmart)
        if logbuffer != 0:
            devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"ATA/NCQCmdErrLog.json", True))
        time.sleep(LOG_FETCH_DELAY)
    
    if (logSupport & SATA_PHY_EVENT_COUNT_BIT):
        logbuffer =  GetATADeviceLog(diskNumber, ATA_LOG_SATA_PHY_EVENT_COUNTER, 0, isSmart)
        if logbuffer != 0:
            devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"ATA/SATAPhyEventCounter.json", True))
        time.sleep(LOG_FETCH_DELAY)


def storeATADeviceSMARTLogs(diskNumber, devicedict, logSupport):
    isSmart = True
    
    if (logSupport & SMART_ERR_LOG_BIT):
        logbuffer =  GetATADeviceLog(diskNumber, ATA_LOG_SMART_ERROR_SUM, 0, isSmart)
        if logbuffer != 0:
            devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"ATA/SMARTError.json", True))
        time.sleep(LOG_FETCH_DELAY)    
    else:
        logging.debug("SMART Err Log not supported on disk {0}".format(diskNumber))


def storeATADeviceStandardLogs(diskNumber, devicedict, logSupport):
    if (logSupport & GPL_BIT):
        storeATADeviceGPLLogs(diskNumber, devicedict, logSupport)
    else:
        logging.debug("GPL not supported on disk {0}".format(diskNumber))

    if (logSupport & SMART_FEAT_SET_BIT):
        storeATADeviceSMARTLogs(diskNumber, devicedict, logSupport)
    else:
        logging.debug("SMART not supported on disk {0}".format(diskNumber))


def IdentifyWord76Valid(word76):
    if ((word76 == 0xFFFF) or (word76 == 0)):
        return False
    else:
        logging.debug("ATA Identify word 76 is valid")
        return True
        
        
def IdentifyWord82And83Valid(word83):
    if ((word83 & (1<<14)) and not(word83 & (1<<15))):
        logging.debug("ATA Identify words 82 and 83 are valid")
        return True
    else:
        return False


def IdentifyWord84Valid(word84):
    if ((word84 & (1<<14)) and not(word84 & (1<<15))):
        logging.debug("ATA Identify word 84 is valid")
        return True
    else:
        return False


def IdentifyWord85And86And87Valid(word87):
    if ((word87 & (1<<14)) and not(word87 & (1<<15))):
        logging.debug("ATA Identify word 84 is valid")
        return True
    else:
        return False


def getLogSupportFromIdentify(devicedict):
    logSupport = 0
    word76 = devicedict['AtaIdentify']['SATASupport']
    word82 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported1']
    word83 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported2']
    word84 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported3']
    word85 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported4']
    word86 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported5']
    word87 = devicedict['AtaIdentify']['CmdsAndFeaturesSupported6']
    
    word76valid = IdentifyWord76Valid(word76)
    words82and83valid = IdentifyWord82And83Valid(word83)
    word84valid = IdentifyWord84Valid(word84)
    words85and86and87valid = IdentifyWord85And86And87Valid(word87)
    
    if (word76valid):
        if (word76 & WORD76_NCQ_FEATURE_BIT):
            logSupport |= NCQ_BIT
        
        if (word76 & WORD76_SATA_PHY_EVENT_COUNT_BIT):
            logSupport |= SATA_PHY_EVENT_COUNT_BIT
    
    if (words82and83valid):
        if (word82 & WORD82_SMART_FEATURE_BIT):
            logSupport |= SMART_FEAT_SET_BIT
    elif (words85and86and87valid):
        if (word85 & WORD82_SMART_FEATURE_BIT):
            logSupport |= SMART_FEAT_SET_BIT
    
    if (word84valid):
        if (word84 & WORD84_SMART_ERR_LOG_BIT):
            logSupport |= SMART_ERR_LOG_BIT
        
        if (word84 & WORD84_GPL_FEATURE_BIT):
            logSupport |= GPL_BIT
    elif (words85and86and87valid):
        if (word87 & WORD84_SMART_ERR_LOG_BIT):
            logSupport |= SMART_ERR_LOG_BIT
        
        if (word87 & WORD84_GPL_FEATURE_BIT):
            logSupport |= GPL_BIT

    return logSupport


def storeATAIdentifyInformation(diskNumber, devicedict):
    identifybuffer =  GetATAIdentify(diskNumber)
    if identifybuffer != 0:
        logdata = hexlify(identifybuffer).decode('ascii').rstrip()
        devicedict.update(parseLog(logdata, logPageDir()+"ATA/Id.json", True))
        
        # Extract firmware revision out for later use.
        fwRev = devicedict['AtaIdentify']['FirmwareRevision']
        
        logSupport = getLogSupportFromIdentify(devicedict)

    else:
        fwRev = 0
        logSupport = 0
    time.sleep(LOG_FETCH_DELAY)
    
    return fwRev, logSupport


def storeATADevice(diskNumber, model, devicedict, drive, itsaresult):

    # Read Identify Information
    fwRev, logSupport = storeATAIdentifyInformation(diskNumber, devicedict)
    
    # Read Standard Logs
    storeATADeviceStandardLogs(diskNumber, devicedict, logSupport)

    # Read Vendor Unique Logs
    storeATADeviceVendorUniqueLogs(diskNumber, model, devicedict, drive, itsaresult, fwRev)