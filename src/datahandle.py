"""
    Copyright (c) Microsoft Corporation
"""

import binascii
import os
import json
import logging

from binascii import hexlify, unhexlify


def loadJson(fileName):
    exitCode = 0
    jsonObj  = {}
    
    if os.path.isfile(fileName):
        with open(fileName) as jsonFile:
            try:
                jsonObj = json.load(jsonFile)
            except ValueError as e:
                logging.error("ERROR: Invalid JSON syntax in {0}: {1}\n".format(fileName, str(e)))
                exitCode = 1
    else:
        logging.error("ERROR: File {0} not found".format(fileName))
        exitCode = 1
    
    return exitCode, jsonObj

def checkJsonProp(jsonObj, attrStr, attrType, fileName):
    if attrStr not in jsonObj:
        logging.error("ERROR: {0} is missing {1} property".format(fileName, attrStr))
        return 1
    
    if not isinstance(jsonObj[attrStr], attrType):
        logging.error("ERROR: {0}, '{1}' should contain a(n) {2}".format(fileName, attrStr, str(attrType)))
        return 1
    return 0

def parseLog(logdata, conffile, byteswap):
    exitcode, logjson = loadJson(conffile)
    logging.debug("type(exitcode) is {0}, exit code is {1}".format(type(exitcode), exitcode))
    if 1 == exitcode:
        logging.error("Failed to load JSON parser")
        return {}
    logging.debug("type(logjson) is {0}, logjson is {1}".format(type(logjson), logjson))
    value = 0
    attrs = {}
    for attr in logjson["Attributes"]:
        logging.debug("type(attr) is {0}, attr is {1}".format(type(attr), attr))
        fromNibble = attr["Offset"]*2
        toNibble = (attr["Offset"]*2)+(attr["Size"]*2)
        binary = logdata[fromNibble:toNibble]
        logging.debug("fromNibble is {0}, toNibble is {1}, attr['Datatype'] is {2}, attr['Name'] is {3}, binary is {4}"
            .format(fromNibble, toNibble, attr['Datatype'], attr['Name'], binary))
        if attr["Datatype"] == "int":
            try:
                value = int.from_bytes(unhexlify(binary), byteorder='little')
                attrs.update({attr["Name"]:value})
            except:
                logging.error("Error parsing int. Binary data is {0}".format(binary))
        elif attr["Datatype"] == "string":
            try:
                value = unhexlify(binary).decode('utf-8')
                
                if byteswap:
                    # ATA devices need this char swapping for String fields in Identify...
                    s = (''.join([ value[x:x+2][::-1] for x in range(0, len(value), 2) ]))
                else:
                    s = value
                
                attrs.update({attr["Name"]:s})
            except:
                logging.error("Error parsing string. Binary data is {0}".format(binary))
        else:
            logging.error("Error - Unknown datatype. Datatype is {0}.".format(attr['Datatype']))
    retdict = {}
    retdict.update({logjson["type"]:attrs})
    return retdict


def outputData(nodeDict, resultFolder, outputToScreen):
    resultFile = 'diskData.json'

    if (outputToScreen):
        print(json.dumps(nodeDict, indent=2))
    else:
        logging.info(json.dumps(nodeDict, indent=2))
        with open(os.path.join(resultFolder, resultFile), 'w') as f:
            json.dump(nodeDict, f)

