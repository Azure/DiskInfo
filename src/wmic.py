"""
    Copyright (c) Microsoft Corporation
"""

import subprocess
import re
import logging

# We must use the MSFT_PhysicalDisk class to see the actual devices and not virtual disks.
WMIC_DISK_CMD = r"wmic /namespace:\\root\microsoft\windows\storage path MSFT_PhysicalDisk get DeviceId, Manufacturer, Model, BusType, SerialNumber"

# Example output from WMIC command:
# C:\> wmic /namespace:\\root\microsoft\windows\storage path MSFT_PhysicalDisk get DeviceId, Manufacturer, Model, BusType, SerialNumber
# BusType  DeviceId  Manufacturer  Model                    SerialNumber
# 17       1                       Z1001                    4200_0119_B315_0100_00F0_6E0B_0100_0000.
# 11       0                       WDC  WDS500G2B0A-00SM50  190893803568

# borrowed example from http://autosqa.com/2016/03/18/how-to-parse-wmic-output-with-python/

# Parsing format of WMIC
def parse_wmic_output(text):
    result = []
    # remove empty lines
    lines = [s for s in text.splitlines() if s.strip()]
    
    # No Instance(s) Available
    if len(lines) == 0:
        return result
        
    header_line = lines[0]
    # Find headers and their positions
    headers = re.findall('\\S+\\s+|\\S$', header_line)
    pos = [0]
    for header in headers:
        pos.append(pos[-1] + len(header))
    for i in range(len(headers)):
        headers[i] = headers[i].strip()
    # Parse each entries
    for r in range(1, len(lines)):
        row = {}
        for i in range(len(pos)-1):
            row[headers[i]] = lines[r][pos[i]:pos[i+1]].strip()
        result.append(row)
    return result

def get_disks_wmic():
    proc = subprocess.Popen(WMIC_DISK_CMD.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    errcode = proc.returncode
    if (not errcode):
        logging.debug("WMIC is supported")
        result = parse_wmic_output(stdout.decode('ascii').rstrip())
    else:
        logging.info("WMIC is not supported")
        result = 0
    
    return errcode, result