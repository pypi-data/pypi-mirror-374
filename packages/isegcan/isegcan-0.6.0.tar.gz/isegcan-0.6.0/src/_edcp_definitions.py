import can
from collections import namedtuple

# set the stuff that will not change
can.rc['bitrate'] = 125000
can.rc['channel'] = 'can0'
can.rc['interface'] = 'socketcan'

# the command names map to the hex command. The data is contained with the command for the DCP commands
# The tuple contains also the struct typecodes of the address (channel, for example) and the value (of result and set
# commands) and a bool to indicate if it is a writable parameter.
CommTuple = namedtuple('CommTuple', 'command bytes addr_t val_t is_writable')
command_list = [CommTuple('register', b'\xd8', 'B', None, True),
                # module commands
                CommTuple('module_status', b'\x10\x00', None, 'H', True),  # 2-byte status
                CommTuple('module_control', b'\x10\x01', None, 'H', True),  # 2-byte control bits: 14=killena, 12=fineadj, 06=doClear maybe most important
                CommTuple('module_event_status', b'\x10\x02', None, 'H', True),  # 2-byte event status
                CommTuple('module_event_mask', b'\x10\x03', None, 'H', True),  # 2-byte event mask
                CommTuple('module_event_channel_status', b'\x10\x04', 'B', 'H', True),  # 1-byte offset + 2-byte isEvent for offset:offset+16 channels
                CommTuple('module_event_channel_mask', b'\x10\x04', 'B', 'H', True),  # 1-byte offset + 2-byte which channels propagate to isEventActive of module_status
                CommTuple('module_event_group_status', b'\x10\x05', None, 'I', True),  # isEvent for any of 32 groups
                CommTuple('module_event_group_mask', b'\x10\x06', None, 'I', True),  # 4-byte which groups propagate to isEventActive of module_status
                CommTuple('module_serial_number', b'\x12\x00', None, 'I', False),
                CommTuple('module_firmware_release', b'\x12\x01', None, 'I', False),
                CommTuple('module_bit_rate', b'\x12\x02', None, 'H', False),  # Only read for now
                CommTuple('module_firmware_name', b'\x12\x03', None, 'I', False),
                CommTuple('module_channel_number', b'\x12\x08', None, 'B', False),
                CommTuple('module_voltage_ramp_speed', b'\x11\x00', None, 'f', True),
                CommTuple('module_module_option', b'\x12\x80', None, 'I', False),
                # all channel read and write commands contain chn as first data byte
                CommTuple('channel_status', b'\x40\x00', 'B', 'H', True),  # ch, 2-byte status
                CommTuple('channel_control', b'\x40\x01', 'B', 'H', True),  # ch
                CommTuple('channel_event_status', b'\x40\x02', 'B', 'H', True),  # ch
                CommTuple('channel_event_mask', b'\x40\x03', 'B', 'H', True),  # ch
                CommTuple('channel_delayed_trip_time', b'\x40\x05', 'B', 'H', True),  # ch, 2-byte uint, time in ms to trip
                CommTuple('channel_delayed_trip_type', b'\x40\x06', 'B', 'B', True),  # ch, 1-byte uint
                CommTuple('channel_external_inhibit', b'\x40\x06', 'B', 'B', True),  # ch, 1-byte uint
                CommTuple('channel_voltage_ramp_priority', b'\x40\x10', 'B', 'H', True),  # ch, 2-byte uint (0 to ch-num)
                CommTuple('channel_set_voltage', b'\x41\x00', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_set_current', b'\x41\x01', 'B', 'f', True),  # ch, 4-byte float. If KILEna, this is trip, otherwise set.
                CommTuple('channel_voltage_measurement', b'\x41\x02', 'B', 'f', False),  # ch
                CommTuple('channel_current_measurement', b'\x41\x03', 'B', 'f', False),  # ch
                CommTuple('channel_voltage_bounds', b'\x41\x04', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_current_bounds', b'\x41\x05', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_nominal_voltage', b'\x41\x06', 'B', 'f', False),  # ch
                CommTuple('channel_nominal_current', b'\x41\x07', 'B', 'f', False),  # ch
                CommTuple('channel_nominal_power', b'\x41\x08', 'B', 'f', False),  # ch
                CommTuple('channel_current_measurement_range', b'\x41\x09', 'B', 'fB', False),  # ch, 4-byte float + U1
                CommTuple('channel_voltage_bottom', b'\x41\x0a', 'B', 'f', True),  # ch, 4-byte float, E08F2, E08C2, N06C2 and N04C2
                CommTuple('channel_vct_coefficient', b'\x41\x20', 'B', 'f', True),  # ch, VCT only
                CommTuple('channel_temperature_external', b'\x41\x21', 'B', 'f', True),  # ch, VCT only
                CommTuple('channel_resistor_external', b'\x41\x22', 'B', 'f', True),  # ch, 4-byte float, EHS stack
                CommTuple('channel_voltage_ramp_speed_up', b'\x41\x23', 'B', 'f', True),  # ch, 4-byte float (V/s) or (A/s) depending on mode
                CommTuple('channel_voltage_ramp_speed_down', b'\x41\x24', 'B', 'f', True),  # ch, 4-byte float (V/s) or (A/s) depending on mode
                CommTuple('channel_voltage_ramp_speed_min', b'\x41\x27', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_voltage_ramp_speed_max', b'\x41\x28', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_current_ramp_speed_min', b'\x41\x29', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_current_ramp_speed_max', b'\x41\x30', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_power_set', b'\x41\x34', 'B', 'f', True),  # ch, 4-byte float
                CommTuple('channel_power_measure', b'\x41\x35', 'B', 'f', False),  # ch, 4-byte float
                CommTuple('channel_output_mode', b'\x41\x40', 'B', 'B', True),  # ch, 1-byte unsigned (1,2,3), HV-mode switchable only
                CommTuple('channel_output_polarity', b'\x41\x41', 'B', 'b', True),  # ch, 1-byte signed int, polarity switchable only
                CommTuple('channel_output_voltage_mode', b'\x41\x42', 'B', 'f', False),  # ch, 4-byte float, HV-mode switchable only
                CommTuple('channel_output_current_mode', b'\x41\x43', 'B', 'f', False),  # ch, 4-byte float, HV-mode switchable only
                CommTuple('channel_output_voltage_mode_list', b'\x41\x5f', 'B', 'f', False),  # ch, 4-byte float, HV-mode switchable only
                CommTuple('channel_output_current_mode_list', b'\x41\x43', 'B', 'f', False),  # ch, 4-byte float, HV-mode switchable only
                CommTuple('channel_group_number', b'\x42\x00', 'B', 'B', True)  # ch, 1-byte signed int
                ]
# map from command name to command tuple
c_cmd = {v.command: v for v in command_list}
# map from bytes to command tuple
c_bytes = {v.bytes: v for v in command_list}
