"""
    Copyright (c) Microsoft Corporation
"""

import binascii
import os
import json
import logging

from binascii import hexlify, unhexlify
from ctypes import *

BYTE_SWAP_ENABLED = False

def byte_swap_enable(enable):
    global BYTE_SWAP_ENABLED
    BYTE_SWAP_ENABLED = enable


def struct_to_dict(struct_data, log_dict):
    for field in struct_data._fields_:
        if (not (field[0].startswith("reserved") or field[0].startswith("rsv") or field[0].startswith("not_populated_yet") or field[0].startswith("padding"))):
            value = getattr(struct_data, field[0])
            if (isinstance(value, int) or isinstance(value, str)):
                log_dict.update({field[0]:value})
            elif (isinstance(value, bytes)):
                try:
                    raw_string = (value).decode('UTF-8')
                    if (BYTE_SWAP_ENABLED):
                        string = (''.join([raw_string[x:x+2][::-1] for x in range(0, len(raw_string), 2)]))
                    else:
                        string = raw_string
                except:
                    logging.debug("Couldn't convert {0} to string".format(value))
                    string = None
                if (string is not None and len(string) != 0):
                    log_dict.update({field[0]:string})
            elif (isinstance(value, Array)):
                array_values = []
                for x in range (0, len(value)):
                    field_name = "%s%d" % (field[0], x)
                    if (isinstance(value[x], int) or isinstance(value[x], str)):
                        array_values.append(value[x])
                    else:
                        array_dict = {}
                        struct_to_dict(value[x], array_dict)
                        array_values.append(array_dict)
                log_dict.update({field[0]:array_values})
            else:
                log_dict_second_level = {}
                struct_to_dict(value, log_dict_second_level)
                log_dict.update({field[0]:log_dict_second_level})
    return log_dict


def bin_to_dict(log_buffer, log_struct):
    log_dict = {}
    struct_data = cast(log_buffer, POINTER(log_struct)).contents
    return struct_to_dict(struct_data, log_dict)


def outputData(dict, result_folder, outputToScreen):
    if (outputToScreen):
        print(json.dumps(dict, indent=2))
    else:
        result_file = "diskData{0}.json".format(int(dict['DeviceId']))
        logging.info(json.dumps(dict, indent=2))
        with open(os.path.join(result_folder, result_file), 'w') as f:
            json.dump(dict, f, indent=2)

