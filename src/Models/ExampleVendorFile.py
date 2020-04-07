from ctypes import *
from ..constants import *

NVME_LOG_PAGE_VU1   = 0xD0
NVME_LOG_PAGE_VU2   = 0xD1
NVME_LOG_PAGE_VU3   = 0xD2

modelABC            = "ABC"
firmwareXYZ         = "XYZ12345"

class ExampleLog(Structure):
    """Example Log Page"""
    _pack_ = 1
    _fields_ = [
        ('field1', c_uint32),
        ('field2', c_uint32)
    ]

class ExampleLogModelSpecific1(Structure):
    """Example Log Page"""
    _pack_ = 1
    _fields_ = [
        ('field1', c_uint32),
        ('field2', c_uint32*4)
    ]

class ExampleLogModelSpecific2(Structure):
    """Example Log Page"""
    _pack_ = 1
    _fields_ = [
        ('field1', c_uint32),
        ('field2', c_uint32*8)
    ]

class ExampleLogFirmwareSpecific1(Structure):
    """Example Log Page"""
    _pack_ = 1
    _fields_ = [
        ('field1', c_uint32),
        ('field2', c_uint32*8)
    ]

class ExampleLogFirmwareSpecific2(Structure):
    """Example Log Page"""
    _pack_ = 1
    _fields_ = [
        ('field1', c_uint32),
        ('field2', c_uint32),
        ('field3', c_uint32*8)
    ]

def GETVULOGSNVME(drive, modelNumber, firmware):
    result = [ 
        ("Example1",    NVME_LOG_PAGE_VU1,  ExampleLog)
        ]
    
    # Logs that change byte layout based on model number.
    if (modelNumber == modelABC):
        struct = ExampleLogModelSpecific1
    else:
        struct = ExampleLogModelSpecific2
    log_entry = ("Example2", NVME_LOG_PAGE_VU2, struct)
    result.append(log_entry)
    
    # Logs that change byte layout based on firmware rev.
    if (firmware == firmwareXYZ):
        struct = ExampleLogFirmwareSpecific1
    else:
        struct = ExampleLogFirmwareSpecific2
    log_entry = ("Example3", NVME_LOG_PAGE_VU3, struct)
    result.append(log_entry)
    
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
    
def isExampleVendor(model):
    if (model.startswith("ExampleProdId")):
        return True
    else:
        return False
