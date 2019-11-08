"""
    Copyright (c) Microsoft Corporation
"""

import subprocess
import logging

PS_DISK_CMD = ["powershell",r"Get-WmiObject -Class MSFT_PhysicalDisk -Namespace root\Microsoft\Windows\Storage | Select-Object DeviceId, Manufacturer, Model, BusType, SerialNumber"]

# Parsing format of Get-WmiObject -Class MSFT_PhysicalDisk
def parse_MSFT_PhysicalDisk_output(text):
    lines = text.splitlines()
    result = []
    row = {}
    
    # Parse each entry
    for l in lines:
        ix = l.find(b": ")
        if (ix < 0):
            continue
        tag = l[0:ix]
        val = l[ix+2:]
        tag = tag.strip()
        tag = tag.decode('ascii')
        val = val.decode('ascii')
        if (row.get(tag) is not None):
            result.append(row)
            row = {}
        row[tag] = val
    if (len(row) > 0):
        result.append(row)
        row = {}
    return result

def get_disks_ps():
    proc = subprocess.Popen(PS_DISK_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    errcode = proc.returncode
    if (not errcode):
        logging.debug("Power Shell is supported")
        result = parse_MSFT_PhysicalDisk_output(stdout)
    else:
        logging.info("Power Shell is not supported")
        result = 0
    
    return errcode, result