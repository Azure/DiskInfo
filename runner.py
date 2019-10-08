"""
    Copyright (c) Microsoft Corporation
"""

from src.classify     import classify
from src.deviceinfo   import collectDiskInfo

if __name__ == "__main__":
    
    collectDiskInfo(classify)