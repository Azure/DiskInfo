"""
    Copyright (c) Microsoft Corporation
"""

import src.Models.ExampleVendorFile

from .constants import *
from .Models.ExampleVendorFile  import *


def UNKNOWN_SATA():
    vendor = "UNKNOWN"
    bus = BUS_TYPE_SATA
    result = (vendor, bus, None)
    return(result);

def UNKNOWN_NVME():
    vendor = "UNKNOWN"
    bus = BUS_TYPE_NVME
    result = (vendor, bus, None)
    return(result);

def classify(drive):
    model = drive[0].upper()
    bus = drive[1]
    mnfgr = drive[2].upper()
    
    if (bus == BUS_TYPE_NVME):
        if (isExampleVendor(model)):
            return (src.Models.ExampleVendorFile.NVME)
        # More vendor ID checks for NVMe drives to be added here.
        else:
            return (UNKNOWN_NVME)
    elif (bus == BUS_TYPE_SATA or (bus == BUS_TYPE_SAS and mnfgr.startswith(SATA_ON_SAS_ID))):
        if (isExampleVendor(model)):
            return (src.Models.ExampleVendorFile.SATA)
        # More vendor ID checks for SATA drives to be added here.
        else:
            return (UNKNOWN_SATA)
    else:
        return (None)