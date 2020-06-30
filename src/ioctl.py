"""
    Copyright (c) Microsoft Corporation
"""

import  logging
import  ctypes
import  ctypes.wintypes as wintypes

from    ctypes import *

# The MIT License (MIT)
#
# Copyright © 2014-2016 Santoso Wijaya <santoso.wijaya@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sub-license, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPOVERLAPPED = wintypes.LPVOID
LPSECURITY_ATTRIBUTES = wintypes.LPVOID

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
GENERIC_EXECUTE = 0x20000000
GENERIC_ALL = 0x10000000

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_ATTRIBUTE_NORMAL = 0x00000080

INVALID_HANDLE_VALUE = -1

NULL = 0
FALSE = wintypes.BOOL(0)
TRUE = wintypes.BOOL(1)

# NVMe Scope Identifiers (must be kept in sync with nvme.py CNS defines)
ADAPTER_SCOPE = 0
DEVICE_SCOPE = 1

#IOCTL Defines
# http://www.ioctls.net/
IOCTL_ATA_PASS_THROUGH_DIRECT = 0x4d030
IOCTL_STORAGE_QUERY_PROPERTY = 0x002d1400

# https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_query_type
PROPERTY_STANDARD_QUERY = 0

# https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_property_id
STORAGE_ADAPTER_PROTOCOL_SPECIFIC_PROPERTY = 49
STORAGE_DEVICE_PROTOCOL_SPECIFIC_PROPERTY = 50

# https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_protocol_type
PROTOCOL_TYPE_ATA  = 0x02
PROTOCOL_TYPE_NVME = 0x03

# https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_protocol_nvme_data_type
NVME_DATA_TYPE_IDENTIFY = 1
NVME_DATA_TYPE_LOG_PAGE = 2

# https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_protocol_ata_data_type
ATA_DATA_TYPE_IDENTIFY = 1
ATA_DATA_TYPE_LOG_PAGE = 2

# ATA Command Opcodes
ATA_READ_LOG_EXT                = 0x2F

ATA_FLAGS_DRDY_REQUIRED = (1 << 0)
ATA_FLAGS_DATA_IN       = (1 << 1)
ATA_FLAGS_DATA_OUT      = (1 << 2)
ATA_FLAGS_48BIT_COMMAND = (1 << 3)
ATA_FLAGS_USE_DMA       = (1 << 4)
ATA_FLAGS_NO_MULTIPLE   = (1 << 5)

NVME_MAX_LOG_SIZE = 4096
ATA_MAX_LOG_SIZE = 512
MAX_LOG_SIZE = 4096
LOG_BUF = wintypes.BYTE * MAX_LOG_SIZE

# Empirically chosen timeout value
ATA_CMD_TIMEOUT_SECONDS =   5

class ATA_PASS_THROUGH_DIRECT(ctypes.Structure):
    _fields_ = [
                ('Length', wintypes.USHORT),            # Length of this struct
                ('AtaFlags', wintypes.USHORT),          # Data xfer direction
                ('PathId', wintypes.CHAR),              # Set by port driver
                ('TargetId', wintypes.CHAR),            # Set by port driver
                ('Lun', wintypes.CHAR),                 # Set by port driver
                ('ReservedAsUchar', wintypes.CHAR),     # Reserved
                ('DataTransferLength', wintypes.ULONG), # Data buffer size in bytes
                ('TimeOutValue', wintypes.ULONG),       # Time for driver to wait in seconds
                ('ReservedAsUlong', wintypes.ULONG),    # Reserved
                ('DataBuffer', wintypes.LPVOID),        # Pointer to data buffer
                ('Features', wintypes.CHAR),
                ('LBACount', wintypes.CHAR),
                ('LBANumber', wintypes.CHAR),
                ('ICC', wintypes.CHAR),
                ('Auxiliary', wintypes.CHAR),
                ('Device', wintypes.CHAR),
                ('Command', wintypes.CHAR),
                ('Reserved', wintypes.CHAR),
                ('Features2', wintypes.CHAR),
                ('LBACount2', wintypes.CHAR),
                ('LBANumber2', wintypes.CHAR),
                ('ICC2', wintypes.CHAR),
                ('Auxiliary2', wintypes.CHAR),
                ('Device2', wintypes.CHAR),
                ('Command2', wintypes.CHAR),
                ('Reserved2', wintypes.CHAR),
                ('logbuffer', LOG_BUF),
                ]

class STORAGE_PROTOCOL_SPECIFIC_DATA(ctypes.Structure):
    _fields_ = [
                ('PropertyId', wintypes.DWORD),
                ('QueryType', wintypes.DWORD),
                ('ProtocolType', wintypes.DWORD),
                ('DataType', wintypes.ULONG),
                ('ProtocolDataRequestValue', wintypes.ULONG),
                ('ProtocolDataRequestSubValue', wintypes.ULONG),
                ('ProtocolDataOffset', wintypes.ULONG),
                ('ProtocolDataLength', wintypes.ULONG),
                ('FixedProtocolReturnData', wintypes.ULONG),
                ('ProtocolDataRequestSubValue2', wintypes.ULONG),
                ('ProtocolDataRequestSubValue3', wintypes.ULONG),
                ('Reserved', wintypes.ULONG),
                ('logbuffer', LOG_BUF),
                ]

def _CreateFile(filename, access, mode, creation, flags):
    """See: CreateFile function
        
        http://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx
        
        """
    CreateFile_Fn = windll.kernel32.CreateFileW
    CreateFile_Fn.argtypes = [
                              wintypes.LPWSTR,                    # _In_          LPCTSTR lpFileName
                              wintypes.DWORD,                     # _In_          DWORD dwDesiredAccess
                              wintypes.DWORD,                     # _In_          DWORD dwShareMode
                              LPSECURITY_ATTRIBUTES,              # _In_opt_      LPSECURITY_ATTRIBUTES lpSecurityAttributes
                              wintypes.DWORD,                     # _In_          DWORD dwCreationDisposition
                              wintypes.DWORD,                     # _In_          DWORD dwFlagsAndAttributes
                              wintypes.HANDLE]                    # _In_opt_      HANDLE hTemplateFile
    CreateFile_Fn.restype = wintypes.HANDLE
                              
    return wintypes.HANDLE(CreateFile_Fn(filename,
                                        access,
                                        mode,
                                        NULL,
                                        creation,
                                        flags,
                                        NULL))


def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
    """See: DeviceIoControl function
        
        http://msdn.microsoft.com/en-us/library/aa363216(v=vs.85).aspx
        
    """
    DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
    DeviceIoControl_Fn.argtypes = [
                                   wintypes.HANDLE,                    # _In_          HANDLE hDevice
                                   wintypes.DWORD,                     # _In_          DWORD dwIoControlCode
                                   wintypes.LPVOID,                    # _In_opt_      LPVOID lpInBuffer
                                   wintypes.DWORD,                     # _In_          DWORD nInBufferSize
                                   wintypes.LPVOID,                    # _Out_opt_     LPVOID lpOutBuffer
                                   wintypes.DWORD,                     # _In_          DWORD nOutBufferSize
                                   LPDWORD,                            # _Out_opt_     LPDWORD lpBytesReturned
                                   LPOVERLAPPED]                       # _Inout_opt_   LPOVERLAPPED lpOverlapped
    DeviceIoControl_Fn.restype = wintypes.BOOL
                                   
    # allocate a DWORD, and take its reference
    dwBytesReturned = wintypes.DWORD(0)
    lpBytesReturned = ctypes.byref(dwBytesReturned)
     
    status = DeviceIoControl_Fn(devhandle,
                                ioctl,
                                inbuf,
                                inbufsiz,
                                outbuf,
                                outbufsiz,
                                lpBytesReturned,
                                None)
                                   
    return status, dwBytesReturned


class DeviceIoControl(object):
    
    def __init__(self, path):
        self.path = path
        self._fhandle = None
    
    def _validate_handle(self):
        if self._fhandle is None:
            raise Exception('No file handle')
        if self._fhandle.value == wintypes.HANDLE(INVALID_HANDLE_VALUE).value:
            error = windll.kernel32.GetLastError()
            raise Exception('Failed to open %s. GetLastError(): %d - %s' %
                            (self.path, error, FormatError(error)))

    def ioctl(self, ctl, inbuf, inbufsiz, outbuf, outbufsiz):
        self._validate_handle()
        return _DeviceIoControl(self._fhandle, ctl, inbuf, inbufsiz, outbuf, outbufsiz)
    
    def __enter__(self):
        self._fhandle = _CreateFile(
                                    self.path,
                                    GENERIC_READ | GENERIC_WRITE,
                                    0,
                                    OPEN_EXISTING,
                                    FILE_ATTRIBUTE_NORMAL)
        self._validate_handle()
        return self

    def __exit__(self, typ, val, tb):
        try:
            self._validate_handle()
        except Exception:
            pass
        else:
            windll.kernel32.CloseHandle(self._fhandle)


def GetNVMeLog(disk_number, logid, scope):
    
    filehandle = (r"\\.\PhysicalDrive" + str(disk_number))
    specificdata = STORAGE_PROTOCOL_SPECIFIC_DATA()
    
    if (scope == ADAPTER_SCOPE):
        specificdata.PropertyId = STORAGE_ADAPTER_PROTOCOL_SPECIFIC_PROPERTY
    elif (scope == DEVICE_SCOPE):
        specificdata.PropertyId = STORAGE_DEVICE_PROTOCOL_SPECIFIC_PROPERTY
        
    specificdata.QueryType = PROPERTY_STANDARD_QUERY
    specificdata.ProtocolType = PROTOCOL_TYPE_NVME
    specificdata.DataType = NVME_DATA_TYPE_LOG_PAGE
    specificdata.ProtocolDataRequestValue = logid
    specificdata.ProtocolDataRequestSubValue = 0
    
    # Must subtract 8 from the offset to account for putting PropertyID and QueryType into
    # Protocol Specific Data (they are actually part of Storage Property Query Structure)
    protocolDataOffset = ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA) - 8 - NVME_MAX_LOG_SIZE
    specificdata.ProtocolDataOffset = protocolDataOffset
    specificdata.ProtocolDataLength =  NVME_MAX_LOG_SIZE
    
    logging.debug("filehandle is {0}".format(filehandle))
    with DeviceIoControl(filehandle) as dctl:
        logging.debug("dctl is {0}".format(dctl))
        status, junk = dctl.ioctl(IOCTL_STORAGE_QUERY_PROPERTY,
                                  ctypes.byref(specificdata),  ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA),
                                  ctypes.byref(specificdata), ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA))
    if status:
        return specificdata.logbuffer
    else:
        error = windll.kernel32.GetLastError()
        logging.error('GetNVMeLog({0}, 0x{1}, {2}) Failed to IOCTL_STORAGE_QUERY_PROPERTY {3} . GetLastError(): {4} - {5}'
            .format(disk_number, hex(logid), scope, dctl, error, FormatError(error)))
        return 0


def GetNVMeIdentify(disk_number, scope):
    filehandle = (r"\\.\PhysicalDrive" + str(disk_number))
    specificdata = STORAGE_PROTOCOL_SPECIFIC_DATA()
    
    if (scope == ADAPTER_SCOPE):
        specificdata.PropertyId = STORAGE_ADAPTER_PROTOCOL_SPECIFIC_PROPERTY
        
    elif (scope == DEVICE_SCOPE):
        specificdata.PropertyId = STORAGE_DEVICE_PROTOCOL_SPECIFIC_PROPERTY
        
    specificdata.QueryType = PROPERTY_STANDARD_QUERY
    specificdata.ProtocolType = PROTOCOL_TYPE_NVME
    specificdata.DataType = NVME_DATA_TYPE_IDENTIFY
    specificdata.ProtocolDataRequestValue = 1
    specificdata.ProtocolDataRequestSubValue = 0
    
    # Must subtract 8 from the offset to account for putting PropertyID and QueryType into
    # Protocol Specific Data (they are actually part of Storage Property Query Structure)
    protocolDataOffset = ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA) - 8 - NVME_MAX_LOG_SIZE
    specificdata.ProtocolDataOffset = protocolDataOffset
    specificdata.ProtocolDataLength =  NVME_MAX_LOG_SIZE
    
    with DeviceIoControl(filehandle) as dctl:
        status, junk = dctl.ioctl(IOCTL_STORAGE_QUERY_PROPERTY,
                                  ctypes.byref(specificdata),  ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA),
                                  ctypes.byref(specificdata), ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA))
    if status:
        return specificdata.logbuffer
    else:
        error = windll.kernel32.GetLastError()
        logging.error('GetNVMeIdentify({0}, {1}) Failed to IOCTL_STORAGE_QUERY_PROPERTY {2}. GetLastError(): {3} - {4}'
            .format(disk_number, scope, dctl, error, FormatError(error)))
        return 0


def ATAPassThroughDirect(disk_number, flags, feature, lbacount, lbanumber2, lbanumber, opcode):
    filehandle = (r"\\.\PhysicalDrive" + str(disk_number))
    
    specificdata = ATA_PASS_THROUGH_DIRECT()
    specificdata.Length = ctypes.sizeof(ATA_PASS_THROUGH_DIRECT) - MAX_LOG_SIZE
    specificdata.AtaFlags = flags
    specificdata.DataTransferLength = ATA_MAX_LOG_SIZE
    specificdata.TimeOutValue = ATA_CMD_TIMEOUT_SECONDS
    specificdata.DataBuffer = ctypes.addressof(specificdata.logbuffer)
    specificdata.LBANumber = lbanumber
    specificdata.Features2 = feature
    specificdata.LBACount2 = lbacount
    specificdata.LBANumber2 = lbanumber2
    specificdata.Command2 = opcode
    
    with DeviceIoControl(filehandle) as dctl:
        status, junk = dctl.ioctl(IOCTL_ATA_PASS_THROUGH_DIRECT,
                                  ctypes.byref(specificdata),  ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA),
                                  ctypes.byref(specificdata), ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA))
    if status:
        return specificdata.logbuffer
    else:
        error = windll.kernel32.GetLastError()
        logging.error('GetATAIdentify({0}) Failed to IOCTL_ATA_PASS_THROUGH_DIRECT {1}. GetLastError(): {2} - {3}'
            .format(disk_number, dctl, error, FormatError(error)))
        return 0


def GetATAGPLLog(disk_number, logid, page):
    
    flags = (ATA_FLAGS_DRDY_REQUIRED | ATA_FLAGS_DATA_IN | ATA_FLAGS_48BIT_COMMAND)
    return ATAPassThroughDirect(disk_number, flags, 0, 1, logid, page, ATA_READ_LOG_EXT)


def GetATASMARTLog(disk_number, page):
    
    filehandle = (r"\\.\PhysicalDrive" + str(disk_number))
    specificdata = STORAGE_PROTOCOL_SPECIFIC_DATA()
    
    specificdata.PropertyId = STORAGE_DEVICE_PROTOCOL_SPECIFIC_PROPERTY
    specificdata.QueryType = PROPERTY_STANDARD_QUERY
    specificdata.ProtocolType = PROTOCOL_TYPE_ATA
    specificdata.DataType = ATA_DATA_TYPE_LOG_PAGE
    specificdata.ProtocolDataRequestValue = page
    specificdata.ProtocolDataRequestSubValue = 0
    
    # Must subtract 8 from the offset to account for putting PropertyID and QueryType into
    # Protocol Specific Data (they are actually part of Storage Property Query Structure)
    protocolDataOffset = ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA) - 8 - MAX_LOG_SIZE
    specificdata.ProtocolDataOffset = protocolDataOffset
    specificdata.ProtocolDataLength =  ATA_MAX_LOG_SIZE
    
    logging.debug("filehandle is {0}".format(filehandle))
    with DeviceIoControl(filehandle) as dctl:
        logging.debug("dctl is {0}".format(dctl))
        status, junk = dctl.ioctl(IOCTL_STORAGE_QUERY_PROPERTY,
                                  ctypes.byref(specificdata),  ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA),
                                  ctypes.byref(specificdata), ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA))
    if status:
        return specificdata.logbuffer
    else:
        error = windll.kernel32.GetLastError()
        logging.error('GetATALog({0}, 0x{1}) Failed to IOCTL_STORAGE_QUERY_PROPERTY {2}. GetLastError(): {3} - {4}'
            .format(disk_number, page, dctl, error, FormatError(error)))
        return 0


def GetATAIdentify(disk_number):
    filehandle = (r"\\.\PhysicalDrive" + str(disk_number))
    specificdata = STORAGE_PROTOCOL_SPECIFIC_DATA()
    
    specificdata.PropertyId = STORAGE_DEVICE_PROTOCOL_SPECIFIC_PROPERTY
    specificdata.QueryType = PROPERTY_STANDARD_QUERY
    specificdata.ProtocolType = PROTOCOL_TYPE_ATA
    specificdata.DataType = ATA_DATA_TYPE_IDENTIFY
    specificdata.ProtocolDataRequestValue = 0
    specificdata.ProtocolDataRequestSubValue = 0
    
    # Must subtract 8 from the offset to account for putting PropertyID and QueryType into
    # Protocol Specific Data (they are actually part of Storage Property Query Structure)
    protocolDataOffset = ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA) - 8 - MAX_LOG_SIZE
    specificdata.ProtocolDataOffset = protocolDataOffset
    specificdata.ProtocolDataLength =  ATA_MAX_LOG_SIZE
    
    with DeviceIoControl(filehandle) as dctl:
        status, junk = dctl.ioctl(IOCTL_STORAGE_QUERY_PROPERTY,
                                  ctypes.byref(specificdata),  ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA),
                                  ctypes.byref(specificdata), ctypes.sizeof(STORAGE_PROTOCOL_SPECIFIC_DATA))
    if status:
        return specificdata.logbuffer
    else:
        error = windll.kernel32.GetLastError()
        logging.error('GetATAIdentify({0}) Failed to IOCTL_STORAGE_QUERY_PROPERTY {1}. GetLastError(): {2} - {3}'
            .format(disk_number, dctl, error, FormatError(error)))
        return 0