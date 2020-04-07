###
### Copyright (c) Microsoft Corporation. All rights reserved.
###

from ctypes import *

class IdCtrl(Structure):
    """Identify Controller"""
    _pack_ = 1
    _fields_ = [
        ('pci_vendor_id', c_uint16),
        ('pci_subsystem_vendor_id', c_uint16),
        ('serial_number', c_char * 20),
        ('model_number', c_char * 40),
        ('firmware_revision', c_char * 8),
        ('recommended_arbitration_burst', c_uint8),
        ('ieee_oui_id', c_uint8*3),
        ('reserved0', c_uint8),
        ('mdts', c_uint8),
        ('controller_id', c_uint16),
        ('version', c_uint32),
        ('rtd3_resume_latency', c_uint32),
        ('rtd3_entry_latency', c_uint32),
        ('oaes', c_uint32),
        ('controller_attributes', c_uint32),
        ('reserved1', c_uint8*156),
        ('oacs', c_uint16),
        ('abort_command_limit', c_uint8),
        ('async_event_req_limit', c_uint8),
        ('firmware_updates', c_uint8),
        ('log_page_attributes', c_uint8),
        ('error_log_page_entries', c_uint8),
        ('num_power_states', c_uint8),
        ('admin_vendor_specific_cmd_config', c_uint8),
        ('reserved2', c_uint8),
        ('wctemp', c_uint16),
        ('cctemp', c_uint16),
        ('reserved3', c_uint8*49),
        ('firmware_update_gran', c_uint8),
        ('keep_alive_support', c_uint16),
        ('reserved4', c_uint8*190),
        ('sq_entry_size', c_uint8),
        ('cq_entry_size', c_uint8),
        ('max_outstanding_cmd', c_uint16),
        ('num_numspaces', c_uint32),
        ('oncs', c_uint16),
        ('fused_op_support', c_uint16),
        ('format_nvm_attributes', c_uint8),
        ('volatile_write_cache', c_uint8),
        ('atomic_write_unit_normal', c_uint16),
        ('atomic_write_unit_pfail', c_uint16),
        ('nvm_vendor_specific_cmd_config', c_uint8),
        ('reserved5', c_uint8*237),
        ('nvm_sub_qualified_name', c_char * 256),
        ('reserved6', c_uint8*1024),
        ('power_state_0_descriptor', c_uint32*8)
    ]
    
class IdNs(Structure):
    """Identify Namespace"""
    _pack_ = 1
    _fields_ = [
        ('namespace_size', c_uint64),
        ('namespace_capacity', c_uint64),
        ('namespace_utilization', c_uint64),
        ('namespace_features', c_uint8),
        ('num_lba_formats', c_uint8),
        ('formatted_lba_size', c_uint8),
        ('metadata_capabilities', c_uint8),
        ('e2e_data_protection_capabilities', c_uint8),
        ('e2e_data_protection_type_settings', c_uint8),
        ('reserved0', c_uint8*98),
        ('lba_format_0_supported', c_uint32)
    ]

class ErrorEntry(Structure):
    """Get Log Page - Error Information (Log Identifier 01h)"""
    _pack_ = 1
    _fields_ = [
        ('error_count', c_uint64),
        ('sqid', c_uint16),
        ('cmd_id', c_uint16),
        ('status_field', c_uint16),
        ('param_error_location', c_uint16),
        ('lba', c_uint32),
        ('namespace', c_uint32),
        ('vendor_specific_info_available', c_uint8),
        ('reserved0', c_uint8*3),
        ('cmd_specific_info', c_uint64),
        ('reserved0', c_uint8*24)
    ]

class ErrorInformation(Structure):
    """Get Log Page - Error Information (Log Identifier 01h)"""
    _pack_ = 1
    _fields_ = [
        ('error_entry', ErrorEntry*64)
    ]

class CritWarningBits(Structure):
    _fields_ = [
        ('spare_below_threshold', c_uint8, 1),
        ('temperature_beyond_threshold', c_uint8, 1),
        ('nvm_subsystem_degraded', c_uint8, 1),
        ('read_only_mode', c_uint8, 1),
        ('capacitor_failed', c_uint8, 1),
        ('reserved', c_uint8, 3)
    ]

class SmartLog(Structure):
    """Get Log Page - SMART/Health Information (Log Identifier 02h)"""
    _pack_ = 1
    _fields_ = [
        ('critical_warning', CritWarningBits),
        ('temperature', c_uint16),
        ('avail_spare', c_uint8),
        ('spare_thresh', c_uint8),
        ('percent_used', c_uint8),
        ('reserved0', c_uint8 * 26),
        ('data_units_read', c_uint64 * 2),
        ('data_units_written', c_uint64 * 2),
        ('host_reads', c_uint64 * 2),
        ('host_writes', c_uint64 * 2),
        ('ctrl_busy_time', c_uint64 * 2),
        ('power_cycles', c_uint64 * 2),
        ('power_on_hours', c_uint64 * 2),
        ('unsafe_shutdowns', c_uint64 * 2),
        ('media_errors', c_uint64 * 2),
        ('num_err_log_entries', c_uint64 * 2),
        ('warning_temp_time', c_uint32),
        ('critical_comp_time', c_uint32),
        ('temp_sensor1', c_uint16),
        ('temp_sensor2', c_uint16),
        ('temp_sensor3', c_uint16),
        ('temp_sensor4', c_uint16),
        ('temp_sensor5', c_uint16),
        ('temp_sensor6', c_uint16),
        ('temp_sensor7', c_uint16),
        ('temp_sensor8', c_uint16),
        ('thm_temp1_trans_count', c_uint32),
        ('thm_temp2_trans_count', c_uint32),
        ('thm_temp1_total_time', c_uint32),
        ('thm_temp2_total_time', c_uint32),
        ('reserved1', c_uint8 * 280),
    ]

class AFI(Structure):
    _fields_ = [
        ('active', c_uint8, 3),
        ('rsrvd0', c_uint8, 1),
        ('next', c_uint8, 3),
        ('reserved0', c_uint8, 1)
    ]

class FwInfoLog(Structure):
    """Get Log Page - Firmware Slot Information (Log Identifier 03h)"""
    _pack_ = 1
    _fields_ = [
        ('afi', AFI),
        ('reserved0', c_uint8*7),
        ('frs1', c_char*8),
        ('frs2', c_char*8),
        ('frs3', c_char*8),
        ('frs4', c_char*8),
        ('frs5', c_char*8),
        ('frs6', c_char*8),
        ('frs7', c_char*8),
        ('reserved1', c_uint64*56)
    ]

class WCSLog(Structure):
    """Get Log Page - WCS (Log Identifier C0h)"""
    _pack_ = 1
    _fields_ = [
        ('media_written_unit', c_uint64*2),
        ('ecc_iterations', c_uint64*2),
        ('capacitor_health', c_uint8),
        ('supported_features', c_uint8),
        ('power_consumption', c_uint8),
        ('wear_range_delta', c_uint8),
        ('reserved0', c_uint8*4),
        ('temperature_throttling', c_uint8*8),
        ('unaligned_io', c_uint64),
        ('mapped_lba', c_uint32),
        ('program_fail_cnt', c_uint32),
        ('erase_fail_cnt', c_uint32),
        ('reserved1', c_uint8*12),
        ('security_version_number', c_uint32*2),
        ('reserved2', c_uint8*422),
        ('log_page_version', c_uint16)
    ]
