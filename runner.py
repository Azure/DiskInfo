"""
    Copyright (c) Microsoft Corporation
"""

from src.classify     import classify
from src.sequencer    import collectDiskInfo

if __name__ == "__main__":
    
    collectDiskInfo(classify)