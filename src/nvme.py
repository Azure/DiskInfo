"""
    Copyright (c) Microsoft Corporation
"""

import time
import logging

from ctypes                     import *
from .constants                 import *
from .ioctl                     import GetNVMeIdentify, GetNVMeLog
from .datahandle                import bin_to_dict, byte_swap_enable
from .structures.nvme_standard  import *


# NVMe Identify CNS Identifiers (must be kept in sync with ioctl.py SCOPE defines)
CNS_CONTROLLER                              = 0
CNS_NAMESPACE                               = 1

# NVMe Log Page Identifiers
NVME_LOG_PAGE_ERROR_INFO                    = 0x01
NVME_LOG_PAGE_HEALTH_INFO                   = 0x02
NVME_LOG_PAGE_FIRMWARE_SLOT_INFO            = 0x03
NVME_LOG_PAGE_CHANGED_NAMESPACE_LIST        = 0x04
NVME_LOG_PAGE_COMMAND_EFFECTS               = 0x05
NVME_LOG_PAGE_DEVICE_SELF_TEST              = 0x06
NVME_LOG_PAGE_TELEMETRY_HOST_INITIATED      = 0x07
NVME_LOG_PAGE_TELEMETRY_CTLR_INITIATED      = 0x08

NVME_LOG_PAGE_RESERVATION_NOTIFICATION      = 0x80
NVME_LOG_PAGE_SANITIZE_STATUS               = 0x81

NVME_LOG_PAGE_VU_START                      = 0xC0
NVME_LOG_PAGE_WCS_CLOUD_SSD                 = 0xC0
NVME_LOG_PAGE_VU_END                        = 0xFF

# NVMe Log Bit Parsers
ACTIVE_FIRMWARE_INFO_BITMASK                = 0x7

def get_fw_rev(device_dict):
    active_slot = device_dict['FirmwareSlotInformation']['afi']['active']
    return device_dict['FirmwareSlotInformation']["frs%d" % (active_slot)]


def store_nvme_identify(disk_number, devicedict, id_name, id_struct, cns):
    id_buffer =  GetNVMeIdentify(disk_number, cns)
    if id_buffer != 0:
        devicedict.update({id_name:bin_to_dict(id_buffer, id_struct)})
    time.sleep(LOG_FETCH_DELAY)


def store_nvme_log_page(disk_number, devicedict, log_name, log_id, log_struct, cns):
    log_buffer =  GetNVMeLog(disk_number, log_id, cns)
    if log_buffer != 0:
        devicedict.update({log_name:bin_to_dict(log_buffer, log_struct)})
    time.sleep(LOG_FETCH_DELAY)


def store_nvme_vu_log_pages(disk_number, model, devicedict, drive, vu_log_function):
    logging.debug("GETVULOGS {0}".format(vu_log_function))
    if vu_log_function is not None:
        logging.debug("calling vu_log_function({0},{1},{2})".format(drive,model,get_fw_rev(devicedict)))
        vuLogs = vu_log_function(drive, model, get_fw_rev(devicedict))
        logging.debug("vuLogs {0}".format(vuLogs))
        if vuLogs is not None:
            logsFetched = 0
            for vu_log_data in vuLogs:
                if (logsFetched <= LOG_VU_MAX):
                    logging.debug("vu_log_data {0}".format(vu_log_data))
                    logpagelen = len(vu_log_data)
                    if ((3 <= logpagelen) and (logpagelen <= 4)):
                        log_name    = vu_log_data[0]
                        log_id      = vu_log_data[1]
                        log_struct  = vu_log_data[2]
                        if (3 < logpagelen):
                            cns = vu_log_data[3]
                        else:
                            cns = CNS_CONTROLLER
                        
                        if ((NVME_LOG_PAGE_VU_START >= 0xC0) and (log_id <= NVME_LOG_PAGE_VU_END)):
                            store_nvme_log_page(disk_number, devicedict, log_name, log_id, log_struct, cns)
                        else:
                            logging.warning("LID is not in legal VU range.")
                        logsFetched += 1
                    else:
                        logging.warning("Invalid VU log page tuple provided.")


def store_nvme_standard_log_pages(disk_number, devicedict):
    standard_logs = [ 
        ("ErrorInformation",        NVME_LOG_PAGE_ERROR_INFO,           ErrorInformation,   CNS_CONTROLLER),
        ("SMART",                   NVME_LOG_PAGE_HEALTH_INFO,          SmartLog,           CNS_NAMESPACE),
        ("FirmwareSlotInformation", NVME_LOG_PAGE_FIRMWARE_SLOT_INFO,   FwInfoLog,          CNS_CONTROLLER),
        ("WCS",                     NVME_LOG_PAGE_WCS_CLOUD_SSD,        WCSLog,             CNS_NAMESPACE)
        ]
    
    for log_data in standard_logs:
        store_nvme_log_page(disk_number, devicedict, log_data[0], log_data[1], log_data[2], log_data[3])


def store_nvme_identify_information(disk_number, devicedict):
    standard_id = [ 
        ("IdentifyController",  IdCtrl, CNS_CONTROLLER),
        ("IdentifyNamespace",   IdNs,   CNS_NAMESPACE)
        ]
    
    for id_data in standard_id:
        store_nvme_identify(disk_number, devicedict, id_data[0], id_data[1], id_data[2])


def storeNVMeDevice(disk_number, model, devicedict, drive, vu_log_function):
    byte_swap_enable(False)
    
    # Read Identify Information
    store_nvme_identify_information(disk_number, devicedict)
    
    # Read Standard Logs
    store_nvme_standard_log_pages(disk_number, devicedict)

    # Read Vendor Unique Logs
    store_nvme_vu_log_pages(disk_number, model, devicedict, drive, vu_log_function)
