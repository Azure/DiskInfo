"""
    Copyright (c) Microsoft Corporation
"""

import os

# BusType Enums
BUS_TYPE_SCSI   =  1
BUS_TYPE_ATA    =  3
BUS_TYPE_RAID   =  8
BUS_TYPE_SAS    = 10
BUS_TYPE_SATA   = 11
BUS_TYPE_NVME   = 17

BUS_TYPE_NAMES = {
    BUS_TYPE_SCSI : "SCSI",
    BUS_TYPE_ATA  : "ATA",
    BUS_TYPE_RAID : "RAID",
    BUS_TYPE_SAS  : "SAS",
    BUS_TYPE_SATA : "SATA",
    BUS_TYPE_NVME : "NVME"
}

SATA_ON_SAS_ID  = "ATA"

# This delay prevents overwhelming disk with inquiries and impacting QoS.
# Delay value is in second granularity.
LOG_FETCH_DELAY = 0.01

# Limiting the number of log pages that can be fetched from a single device
# to avoid overwhelming the telemetry pipe.
LOG_VU_MAX      = 5

LOG_PAGE_DIR    = os.path.join(os.path.dirname(__file__), "LogPages/")
LOG_PAGE_DIR_VU = os.path.join(os.path.dirname(__file__), "LogPages/")

def setLogPageDir(dirSrc):
    global LOG_PAGE_DIR
    LOG_PAGE_DIR = dirSrc
    
def logPageDir():
    global LOG_PAGE_DIR
    return LOG_PAGE_DIR

def setLogPageDirVu(dirSrc):
    global LOG_PAGE_DIR_VU
    LOG_PAGE_DIR_VU = dirSrc
    
def logPageDirVu():
    global LOG_PAGE_DIR_VU
    return LOG_PAGE_DIR_VU