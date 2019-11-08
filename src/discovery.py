"""
    Copyright (c) Microsoft Corporation
"""

import logging
from .wmic  import *
from .ps    import *

DISK_OSDISK           = "DeviceId"
DISK_MANUFACTURER     = "Manufacturer"
DISK_MODEL            = "Model"
DISK_BUS_TYPE         = "BusType"
DISK_SERIAL_NUMBER    = "SerialNumber"

def storeDiskData(diskdata, devicedict):
    devicedict.update({DISK_OSDISK:diskdata[DISK_OSDISK]})
    devicedict.update({DISK_MODEL:diskdata[DISK_MODEL]})
    devicedict.update({DISK_SERIAL_NUMBER:diskdata[DISK_SERIAL_NUMBER]})
    devicedict.update({DISK_BUS_TYPE:diskdata[DISK_BUS_TYPE]})

def get_disks():
    # Try WMIC first.
    status, result = get_disks_wmic()
    
    if (status):
        # WMIC not supported. Try Power Shell.
        status, result = get_disks_ps()
        
    if (status):
        logging.error("Unable to query disks")
    
    return result