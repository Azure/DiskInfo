"""
    Copyright (c) Microsoft Corporation
"""

import time
import logging

from binascii                   import hexlify, unhexlify
from .constants                 import *
from .ioctl                     import GetATAIdentify, GetATASMARTLog, GetATAGPLLog
from .datahandle                import bin_to_dict, byte_swap_enable
from .structures.ata_standard   import *


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

ATA_LOG_VU_START                = 0xA0
ATA_LOG_VU_END                  = 0xDF

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

def get_fw_rev(device_dict):
    return device_dict["Identify"]["firmware_revision"]


def store_ata_log_page(disk_number, devicedict, log_name, log_id, log_struct, page, isSmart):
    if (isSmart):
        # SMART Logs are fetched using Property Standard Query IOCTL.
        log_buffer = GetATASMARTLog(disk_number, log_id)
    else:
        # GPL Logs are fetched using pass through IOCTL and thus must pass the command opcode.
        log_buffer = GetATAGPLLog(disk_number, log_id, page)

    if log_buffer != 0:
        devicedict.update({log_name:bin_to_dict(log_buffer, log_struct)})
    time.sleep(LOG_FETCH_DELAY)


def store_ata_vu_log_pages(disk_number, model, devicedict, drive, vu_log_function):
    logging.debug("vu_log_function {0}".format(vu_log_function))
    if vu_log_function is not None:
        logging.debug("calling vu_log_function({0}, {1}, {2})".format(drive,model,get_fw_rev(devicedict)))
        vuLogs = vu_log_function(drive, model, get_fw_rev(devicedict))
        logging.debug("vuLogs {0}".format(vuLogs))
        if vuLogs is not None:
            logsFetched = 0
            for vu_log_data in vuLogs:
                if (logsFetched <= LOG_VU_MAX):
                    logging.debug("logpage {0}".format(logpage))
                    # logpage should be a tuple or list of length 4
                    logpagelen = len(logpage)
                    if (logpagelen == 4):
                        log_name    = vu_log_data[0]
                        log_id      = vu_log_data[1]
                        log_struct  = vu_log_data[2]
                        is_smart     = vu_log_data[3]
                        
                        if ((log_id >= ATA_LOG_VU_START) and (log_id <= ATA_LOG_VU_END)):
                            store_ata_log_page(disk_number, devicedict,
                                                log_name, log_id, log_struct, 0, is_smart)
                        else:
                            logging.warning("Log page is not in legal VU range.")
                        logsFetched += 1
                    else:
                        logging.warning("Invalid VU log page information provided")


def store_ata_standard_log_pages(disk_number, devicedict):
    log_support = getLogSupportFromIdentify(devicedict)
    standard_logs = []
    
    if (log_support & GPL_BIT):
        log_entry = ("LogDirectory",    ATA_LOG_DIRECTORY,  LogDirectory,   0,  False)
        standard_logs.append(log_entry)
        if (log_support & NCQ_BIT):
            log_entry = ("NCQErrorLog", ATA_LOG_NCQ_CMD_ERROR_LOG,  NCQErrorLog,    0,  True)
            standard_logs.append(log_entry)
        if (log_support & SATA_PHY_EVENT_COUNT_BIT):
            log_entry = ("PHYEventCount",   ATA_LOG_SATA_PHY_EVENT_COUNTER, PHYEventCount,  0,  True)
            standard_logs.append(log_entry)
    else:
        logging.debug("GPL not supported on disk {0}".format(disk_number))

    if (log_support & SMART_FEAT_SET_BIT):
        if (log_support & SMART_ERR_LOG_BIT):
            log_entry = ("SmartError",  ATA_LOG_SMART_ERROR_SUM,    SMARTError, 0,  True)
            standard_logs.append(log_entry)
    else:
        logging.debug("SMART not supported on disk {0}".format(disk_number))
    
    for log_data in standard_logs:
        store_ata_log_page(disk_number, devicedict,
                            log_data[0], log_data[1], log_data[2], log_data[3], log_data[4])


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
    word76 = devicedict['Identify']['sata_features_supported']
    word82 = devicedict['Identify']['cmds_features_supported0'][0]
    word83 = devicedict['Identify']['cmds_features_supported0'][1]
    word84 = devicedict['Identify']['cmds_features_supported0'][2]
    word85 = devicedict['Identify']['cmds_features_supported_enabled0'][0]
    word86 = devicedict['Identify']['cmds_features_supported_enabled0'][1]
    word87 = devicedict['Identify']['cmds_features_supported_enabled0'][2]
    
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


def store_ata_identify_information(disk_number, devicedict):
    identify_buffer =  GetATAIdentify(disk_number)
    if identify_buffer != 0:
        devicedict.update({"Identify":bin_to_dict(identify_buffer, Id)})
    time.sleep(LOG_FETCH_DELAY)


def storeATADevice(disk_number, model, devicedict, drive, vu_log_function):
    byte_swap_enable(True)
    
    # Read Identify Information
    store_ata_identify_information(disk_number, devicedict)
    
    # Read Standard Logs
    store_ata_standard_log_pages(disk_number, devicedict)

    # Read Vendor Unique Logs
    store_ata_vu_log_pages(disk_number, model, devicedict, drive, vu_log_function)