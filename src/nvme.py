"""
    Copyright (c) Microsoft Corporation
"""

import time
import logging

from binascii       import hexlify, unhexlify
from .constants     import *
from .ioctl         import GetNVMeIdentify, GetNVMeLog
from .datahandle    import parseLog

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
NVME_LOG_PAGE_WCS_CLOUD_SSD                 = 0xC0

# NVMe Log Bit Parsers
ACTIVE_FIRMWARE_INFO_BITMASK                = 0x7

def storeNVMeDeviceVendorUniqueLogs(diskNumber, model, devicedict, drive, itsaresult, fwRev):
    GETVULOGS = itsaresult[2]
    logging.debug("GETVULOGS {0}".format(GETVULOGS))
    if GETVULOGS is not None:
        logging.debug("calling GETVULOGS({0},{1},{2})".format(drive,model,fwRev))
        vuLogs = GETVULOGS(drive, model, fwRev)
        logging.debug("vuLogs {0}".format(vuLogs))
        if vuLogs is not None:
            for logpage in vuLogs:
                logging.debug("logpage {0}".format(logpage))
                ## logpage should be a tuple or list of length 2 (or 3 when CNS provided)
                logpagelen = len(logpage)
                if ( (2 <= logpagelen) and (logpagelen < 4) ):
                    logpageid   = logpage[0]
                    logpagejson = logpage[1]
                    if (2 < logpagelen):
                        cns = logpage[2]
                    else:
                        cns = CNS_CONTROLLER

                    if ((logpageid >= 0xC0) and (logpageid <= 0xFF)):
                        logbuffer =  GetNVMeLog(diskNumber, logpageid, cns)
                    else:
                        # Log page is not in legal VU range.
                        logbuffer = 0
                    time.sleep(LOG_FETCH_DELAY)
                    logging.debug("logbuffer {0}".format(logbuffer))
                    if logbuffer != 0:
                        logpagejson = logPageDirVu() + logpagejson
                        logging.debug("enter parseLog {0}".format(logpagejson))
                        devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logpagejson, False))
                        logging.debug("leave parseLog {0}".format(logpagejson))
                else:
                    logging.warning("Invalid VU log page information provided")

def storeNVMeDeviceStandardLogs(diskNumber, devicedict):
    logbuffer =  GetNVMeLog(diskNumber, NVME_LOG_PAGE_HEALTH_INFO, CNS_NAMESPACE)
    if logbuffer != 0:
        devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"NVMe/SMART.json", False))
    time.sleep(LOG_FETCH_DELAY)
    
    logbuffer =  GetNVMeLog(diskNumber, NVME_LOG_PAGE_FIRMWARE_SLOT_INFO, CNS_CONTROLLER)
    if logbuffer != 0:
        logdata = hexlify(logbuffer).decode('ascii').rstrip()
        devicedict.update(parseLog(logdata, logPageDir()+"NVMe/FirmwareSlot.json", False))
        
        # Extract firmware revision out for later use.
        AFI = devicedict['FirmwareSlotInformation']['ActiveFirmwareInfo']
        fwSlot = AFI & ACTIVE_FIRMWARE_INFO_BITMASK
        fwRevSlots = {
            1: "FirmwareRevisionSlot1",
            2: "FirmwareRevisionSlot2",
            3: "FirmwareRevisionSlot3",
            4: "FirmwareRevisionSlot4",
            5: "FirmwareRevisionSlot5",
            6: "FirmwareRevisionSlot6",
            7: "FirmwareRevisionSlot7"
        }
        fwRev = devicedict['FirmwareSlotInformation'][fwRevSlots.get(fwSlot, "")]
    else:
        fwRev = 0
    time.sleep(LOG_FETCH_DELAY)
    
    logbuffer =  GetNVMeLog(diskNumber, NVME_LOG_PAGE_WCS_CLOUD_SSD, CNS_NAMESPACE)
    if logbuffer != 0:
        devicedict.update(parseLog(hexlify(logbuffer).decode('ascii').rstrip(), logPageDir()+"NVMe/WCS.json", False))
    time.sleep(LOG_FETCH_DELAY)
    return fwRev


def storeNVMeIdentifyInformation(diskNumber, devicedict):
    identifybuffer =  GetNVMeIdentify(diskNumber, CNS_CONTROLLER)
    if identifybuffer != 0:
        devicedict.update(parseLog(hexlify(identifybuffer).decode('ascii').rstrip(), logPageDir()+"NVMe/IdCtrl.json", False))
    time.sleep(LOG_FETCH_DELAY)
    
    identifybuffer =  GetNVMeIdentify(diskNumber, CNS_NAMESPACE)
    if identifybuffer != 0:
        devicedict.update(parseLog(hexlify(identifybuffer).decode('ascii').rstrip(), logPageDir()+"NVMe/IdNs.json", False))
    time.sleep(LOG_FETCH_DELAY)


def storeNVMeDevice(diskNumber, model, devicedict, drive, itsaresult):
    
    # Read Identify Information
    storeNVMeIdentifyInformation(diskNumber, devicedict)
    
    # Read Standard Logs
    fwRev = storeNVMeDeviceStandardLogs(diskNumber, devicedict)

    # Read Vendor Unique Logs
    storeNVMeDeviceVendorUniqueLogs(diskNumber, model, devicedict, drive, itsaresult, fwRev)