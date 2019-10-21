"""
    Copyright (c) Microsoft Corporation
"""

import sys
import time
import logging

from .constants      import *
from .discovery      import *
from .nvme           import storeNVMeDevice
from .ata            import storeATADevice
from .datahandle     import outputData

# Uncomment the appropriate logging level to control output verbosity.
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.CRITICAL)

def collectDiskInfo(classifier):

    # Capture start time for performance measurement debug.
    tStart = time.time()
    
    if (len(sys.argv) > 1):
        resultFolder = sys.argv[1]
    else:
        resultFolder = '.'

    disks = []
    nodeDict = []
    
    # Query the disks on the node.
    disks = get_disks()
    
    # Parse disk data one at a time.
    for disk in disks:
        model = disk[DISK_MODEL]
        bus = int(disk[DISK_BUS_TYPE])
        mnfgr = disk[DISK_MANUFACTURER]
        diskNumber = int(disk[DISK_OSDISK])
        drive = (model, bus, mnfgr)
        
        # Re-classify this drive to account for any bit flips in WMIC data.
        itsa = classifier(drive)
        logging.debug("itsa {0}".format(itsa))
            
        if itsa is not None:
            result = itsa()
            vendor = result[0]
            bus = result[1]
            deviceDict = {}
            logging.debug("Vendor = {0}, bus = {1} = {2}".format(vendor, bus, BUS_TYPE_NAMES[bus]))
                
            storeDiskData(disk, deviceDict)
            if bus == BUS_TYPE_NVME:
                storeNVMeDevice(diskNumber, model, deviceDict, drive, result)
            elif bus == BUS_TYPE_SATA:
                storeATADevice(diskNumber, model, deviceDict, drive, result)
            nodeDict.append(deviceDict)
    
    # Output the disk data.
    outputData(nodeDict, resultFolder)

    # Capture end time for performance measurement debug.
    tEnd = time.time()
    # Guideline is to stick within 1 second of processing time because this could block other services.
    logging.info("Execution time in seconds = {0}".format(float(tEnd - tStart)))
