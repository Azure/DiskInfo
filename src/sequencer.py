"""
    Copyright (c) Microsoft Corporation
"""

import sys
import time
import logging

from argparse       import ArgumentParser
from .constants     import *
from .discovery     import *
from .nvme          import storeNVMeDevice
from .ata           import storeATADevice
from .datahandle    import outputData

REV_MAJOR = 2
REV_MINOR = 0

# Uncomment the appropriate logging level to control output verbosity.
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.CRITICAL)


def dumpDataForDisk(diskNum, diskNumList):
    if (diskNumList is None):
        # No list was passed. Print data for all disks.
        return True
    else:
        for passedDiskNum in diskNumList:
            if (diskNum == int(passedDiskNum)):
                # This disk was in the passed in list.
                return True
        return False

def collectDiskInfo(classifier):

    # Capture start time for performance measurement debug.
    tStart = time.time()
    
    # Setup options and arguments.
    usage = "python runner.py outputDirectory [options]"
    parser = ArgumentParser(description=usage)
    parser.add_argument("file", default=".", nargs="?")
    parser.add_argument("-d", "--device", action="store", dest="dev", nargs="*", help="Only output data for specified disk number(s).")
    parser.add_argument("-l", "--list", action="store_true", dest="list", help="Output list of storage devices on the node.")
    parser.add_argument("-o", "--output", action="store_true", dest="output", help="Output disk data to screen only.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Enable verbose output.")
    options = parser.parse_args()
    
    if (options.output):
        # Output mode pushes only final result to stdout
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.CRITICAL)
    elif (options.verbose):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.DEBUG)
    
    # Query the disks on the node.
    disks = get_disks()
    
    if (options.list):
        print ("%12s %30s %5s %30s" % ("Disk Number", "Model", "Bus", "Serial Number"))
    
    # Parse disk data one at a time.
    for disk in disks:
        model = disk[DISK_MODEL]
        bus = int(disk[DISK_BUS_TYPE])
        mnfgr = disk[DISK_MANUFACTURER]
        disk_number = int(disk[DISK_OSDISK])
        serialNumber = disk[DISK_SERIAL_NUMBER]
        drive = (model, bus, mnfgr)
        
        if (options.list):
            print ("%12d %30s %5s %30s" % (disk_number, model, BUS_TYPE_NAMES[bus], serialNumber))
            continue

        if (not dumpDataForDisk(disk_number, options.dev)):
            continue
        
        # Classify this drive to understand vendor and available log pages.
        itsa = classifier(drive)
        logging.debug("itsa {0}".format(itsa))

        if itsa is not None:
            result = itsa()
            vendor = result[0]
            bus = result[1]
            vu_log_function = result[2]
            logging.debug("Vendor = {0}, bus = {1} = {2}".format(vendor, bus, BUS_TYPE_NAMES[bus]))
            
            device_dict = {}
            device_dict.update({"REV_MAJOR":REV_MAJOR})
            device_dict.update({"REV_MINOR":REV_MINOR})
            storeDiskData(disk, device_dict)
            if bus == BUS_TYPE_NVME:
                storeNVMeDevice(disk_number, model, device_dict, drive, vu_log_function)
            elif bus == BUS_TYPE_SATA:
                storeATADevice(disk_number, model, device_dict, drive, vu_log_function)
    
            # Output the disk data.
            outputData(device_dict, options.file, options.output)

    # Capture end time for performance measurement debug.
    tEnd = time.time()
    # Guideline is to stick within 5 seconds of processing time because this could block other services.
    logging.info("Execution time in seconds = {0}".format(float(tEnd - tStart)))
