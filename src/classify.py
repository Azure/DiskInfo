"""
    Copyright (c) Microsoft Corporation
"""

from .constants import *
from .Models.ExampleVendorFile  import *


def UNKNOWN_SATA():
    vendor = "UNKNOWN"
    bus = BUS_TYPE_SATA
    result = ( vendor, bus, None )
    return(result);

def UNKNOWN_NVME():
    vendor = "UNKNOWN"
    bus = BUS_TYPE_NVME
    result = ( vendor, bus, None )
    return(result);

def classify(drive):
    driveProductId = drive[0]
    driveBusType = drive[1]
    driveManufacturer = drive[2]
    
    if (driveBusType == BUS_TYPE_NVME):
        if (driveProductId.upper().startswith("ExampleProdId")):
            return(Models.ExampleVendorFile.NVME)
        # More vendor ID checks for NVMe drives to be added here.
        else:
            return(UNKNOWN_NVME)
    elif (driveBusType == BUS_TYPE_SATA or (driveBusType == BUS_TYPE_SAS and driveManufacturer.upper().startswith(SATA_ON_SAS_ID))):
        if (driveProductId.upper().startswith("ExampleProdId")):
            return(Models.ExampleVendorFile.SATA)
        # More vendor ID checks for ATA drives to be added here.
        else:
            return(UNKNOWN_SATA)
    else:
        return(None)