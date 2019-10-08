from ..constants import *

NVME_LOG_PAGE_VU1   = 0xD0
NVME_LOG_PAGE_VU2   = 0xD1
NVME_LOG_PAGE_VU3   = 0xD2

modelABC            = "ABC"
firmwareXYZ         = "XYZ12345"

def GETVULOGSNVME(drive, modelNumber, firmware):
    result = [ 
        ( NVME_LOG_PAGE_VU1, "LogPages/ExampleVendor/VU1.json" )
        ]
    
    # Logs that change byte layout based on model number.
    if (modelNumber == modelABC):
        json = "LogPages/ExampleVendor/VU2_ABC.json"
    else:
        json = "LogPages/ExampleVendor/VU2_notABC.json"
    logpage = (NVME_LOG_PAGE_VU2, json)
    result.append(logpage)
    
    # Logs that change byte layout based on firmware rev.
    if (firmware == firmwareXYZ):
        json = "LogPages/ExampleVendor/VU3_XYZ.json"
    else:
        json = "LogPages/ExampleVendor/VU3_notXYZ.json"
    logpage = (NVME_LOG_PAGE_VU3, json)
    result.append(logpage)
    
    return(result);

def NVME():
    vendor = "ExampleVendor"
    bus = BUS_TYPE_NVME
    result = (vendor, bus, GETVULOGSNVME)
    return(result);

def SATA():
    vendor = "ExampleVendor"
    bus = BUS_TYPE_SATA
    result = (vendor, bus, None)
    return(result);