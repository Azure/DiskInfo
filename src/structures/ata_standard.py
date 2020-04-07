###
### Copyright (c) Microsoft Corporation. All rights reserved.
###

from ctypes import *

class PHYEventCount(Structure):
    """PHY Event Counter Page"""
    _pack_ = 1
    _fields_ = [
        ('reserved0', c_uint32),
        ('payload', c_uint8*504),
        ('reserved', c_uint8*3),
        ('checksum', c_uint8)
    ]

class NCQErrorLog(Structure):
    """NCQ Error Log Page"""
    _pack_ = 1
    _fields_ = [
        ('header', c_uint8),
        ('reserved0', c_uint8),
        ('status', c_uint8),
        ('error', c_uint8),
        ('lba0', c_uint8*3),
        ('device', c_uint8),
        ('lba1', c_uint8*3),
        ('reserved1', c_uint8),
        ('count', c_uint8*2),
        ('sense_key', c_uint8*3),
        ('lba_final', c_uint8*6),
        ('reserved2', c_uint8*488),
        ('checksum', c_uint8)
    ]

class LogDirectory(Structure):
    """Log Directory Page"""
    _pack_ = 1
    _fields_ = [
        ('version', c_uint16),
        ('num_log_pages', c_uint16*255)
    ]

class ErrorDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('reserved0', c_uint8),
        ('error', c_uint8),
        ('count', c_uint8),
        ('lba', c_uint8*3),
        ('device', c_uint8),
        ('status', c_uint8),
        ('extended_info', c_uint8*19),
        ('state', c_uint8),
        ('life_timestamp', c_uint16),
    ]

class ErrorEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('transport_specific', c_uint8),
        ('feature', c_uint8),
        ('count', c_uint8),
        ('lba', c_uint8*3),
        ('device', c_uint8),
        ('status', c_uint8),
        ('timestamp', c_uint32)
    ]

class ErrorLog(Structure):
    _pack_ = 1
    _fields_ = [
        ('first_cmd', ErrorEntry),
        ('second_cmd', ErrorEntry),
        ('third_cmd', ErrorEntry),
        ('fourth_cmd', ErrorEntry),
        ('fifth_cmd', ErrorEntry),
        ('error_data_structure', ErrorDataStructure)
    ]

class SMARTError(Structure):
    """SMART Error Log Page"""
    _pack_ = 1
    _fields_ = [
        ('version', c_uint8),
        ('index', c_uint8),
        ('error_log', ErrorLog),
        ('reserved0', c_uint8*57),
        ('checksum', c_uint8),
    ]

class Id(Structure):
    """Identify"""
    _pack_ = 1
    _fields_ = [
        ('general_configuration', c_uint16),
        ('reserved0', c_uint16),
        ('specific_configuration', c_uint16),
        ('reserved1', c_uint16*7),
        ('serial_number', c_char*20),
        ('reserved2', c_uint16*3),
        ('firmware_revision', c_char*8),
        ('model_number', c_char*40),
        ('reserved3', c_uint16),
        ('tcg_feature_set_options', c_uint16),
        ('capabilities', c_uint16*2),
        ('reserved4', c_uint16*9),
        ('user_addressable_sectors', c_uint16*2),
        ('reserved5', c_uint16*3),
        ('min_multiword_dma_xfer_cycle_time_per_word', c_uint16),
        ('recommended_multiword_dma_xfer_cycle_time', c_uint16),
        ('min_pio_xfer_cycle_time_wo_flow_control', c_uint16),
        ('min_pio_xfer_cycle_time_with_iordy', c_uint16),
        ('additional_supported', c_uint16),
        ('reserved6', c_uint16*5),
        ('max_queue_depth', c_uint16),
        ('sata_capabilities', c_uint16*2),
        ('sata_features_supported', c_uint16),
        ('sata_features_enabled', c_uint16),
        ('major_version', c_uint16),
        ('minor_version', c_uint16),
        ('cmds_features_supported0', c_uint16*3),
        ('cmds_features_supported_enabled0', c_uint16*3),
        ('reserved7', c_uint16*20),
        ('world_wide_name', c_char*8),
        ('reserved8', c_uint16*7),
        ('cmds_features_supported1', c_uint16),
        ('cmds_features_supported_enabled1', c_uint16), #119
        ('reserved9', c_uint16*96),
        ('media_rotation_rate', c_uint16),
        ('reserved10', c_uint16*4),
        ('transport_major_version', c_uint16),
        ('transport_minor_version', c_uint16),
        ('reserved11', c_uint16*33),
        ('integrity_word', c_uint16)
    ]
