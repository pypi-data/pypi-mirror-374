import time
from struct import pack, unpack, calcsize
from _edcp_definitions import *
import sys

# 11-bit CAN ID:
# bit 10: Crate (module)
# bit 9: Alarm (Normal)
# bits 8-3: module id
# bit 2: NMT (Normal)
# bit 1: Reply (Query)
# bit 0: Read (Write)

short_wait = 0.01


class Resource:
    """
    Class representing an ISEG HV module. It holds reference to the module, controls registration/unregistration of
    and keep-alive signals to the module.

    This is a dumb setup. At the moment it is only listening to a single module. Maybe in the future there will be a
    smarter version of this class that can handle multiple modules.
    """
    def __init__(self, module_id:int, channel: str = can.rc['channel'], interface: str = can.rc['interface'],
                 bitrate: int = can.rc['bitrate'], logging=False):
        """
        :param module_id:   6-bit address of the module (0-63). In ECH224 crate with single board modules this is the
                            slot number.
        :param channel:     The can channel ('can0', if only one PCan interface connected)
        :param interface:   In any modern linux this is 'socketcan'
        :param bitrate:     Iseg seems to be using 125000 Bps by default. It seems to be changeable for some modules.
                            All modules should be set to the same bitrate.

        """
        self.module_id = module_id
        self.module_bit_rate = bitrate
        self.can_id = get_address(self.module_id, alarm=True, nmt=False, reply=False, write=True)
        print('Can id of module:', hex(self.can_id))
        # when addressing, the module id is inserted into the 11-bit can id into positions 8-3, hence the << 3
        filters = [{"can_id": self.module_id << 3, "can_mask": 0x1f8, "extended": False}]
        # print(bin(filters[0]["can_id"]), bin(210), bin(0x1f8))
        # filter is used to only listen to messages from modules (mask is 0b111111000, so ignoring the  .
        self._bus = can.Bus(channel=channel, interface=interface, bitrate=bitrate,
                            can_filters=filters, receive_own_messages=True)

        self._reader = can.BufferedReader()
        self._listeners = [self._reader,  # BufferedReader() listener
                           ]
        if logging:
            self._listeners.append(can.Logger("logfile.txt"))

        # Create Notifier to use for scheduling of callbacks
        self._notifier = can.Notifier(self._bus, self._listeners, loop=None, timeout=short_wait)
        # Build the set and query methods
        self._generate_methods()
        self._register_module()

    def _register_module(self):
        """
        Connect to the module to stop it from spamming the DCP message. After registration the number of channels in the
        module is read and the lists are built.
        :return:
        """
        self.set_register(value=None, address=1)  # register has address but no value.
        # time.sleep(1.0)
        # print('bit rate', self.module_bit_rate)
        # print('Query Ch')
        mod_num = self.query_module_channel_number(None, None)
        if mod_num == 0:
            print("OVERRIDE missing channel number for module")
            print('Firmware', self.query_module_firmware_name(None, None))
            print('Ver', self.query_module_firmware_release(None, None))
            print('ModuleOption', bin(self.query_module_module_option(None, None)))
            print('module_event_status', bin(self.query_module_event_status(None, None)))
            self.module_channel_number = 8
        print('module_ch_num', self.module_channel_number)

        # generate the state variables that are automatically filled, whenever a message is received.
        self._generate_variables(self.module_channel_number)

        # set ramp speed to reasonably low (0.1%/s of nominal voltage). Maximum is 1.0%/s to maintain
        # high accuracy current measurement.
        # Absolute max is 20%. 
        # self.ramp_speed(2.0, None)


    def _unregister_module(self):
        self.set_register(value=None, address=0)

    def _command(self, command: CommTuple, value, address, is_write: bool):
        """
        Send command to the module. The command is from command_list, the value and address are given by the user.
        Commands that do not
        Length of the msg is checked before sending, but the sanity of the commands is not.

        :param command: CommandTuple
        :param address: Address of the command (ch number, offset, group number etc.). Will be prepended to the value
                        in both incoming and outgoing messages. Will be cast to type given in command.
        :param value:   Value that is written or read. Will be cast to type given in command.
                        message is given by cc dictionary.
        :return:
        """
        # print(address, value)
        EDCP_cmd = command.bytes
        if not command.addr_t is None:
            # if there is address, it is written to the command
            EDCP_cmd = EDCP_cmd + pack('>' + command.addr_t, address)
        if not is_write or command.val_t is None:  # read command/registering, value not included
            pass
        elif is_write:  # Is a write with data
            EDCP_cmd = EDCP_cmd + pack('>' + command.val_t, value)
        # print('command', EDCP_cmd.hex(), address)
        self._bus.send(can.Message(arbitration_id=get_address(self.module_id, alarm=True, nmt=False,
                                                              reply=False, write=is_write),
                                   data=EDCP_cmd, is_extended_id=False))

    @classmethod
    def _build_function(cls, command: CommTuple, is_write: bool):
        """
        Build each set_() and query_() function for all settings.

        :return:
        """
        if command.command == 'register': 
            # register command has no value, it never answers
            def amethod(self, value, address):
                cls._command(self, command, value, address, is_write=is_write)
            return amethod
        elif is_write:
            def setmethod(self, value, address):
                cls._command(self, command, value, address, is_write=is_write)
                self._listen(expected_cmd=command.command, require_answer=True)
            return setmethod
        else:
            def querymethod(self, value, address):
                cls._command(self, command, value, address, is_write=is_write)
                self._listen(expected_cmd=command.command, require_answer=True)
                # Query method returns value, for convenience
                if command.addr_t is None:
                    return getattr(self, command.command)
                else:
                    return getattr(self, command.command)[address]
            return querymethod

    @classmethod
    def _generate_methods(cls):
        '''
        Generate individual set_X() and query_X() functions for all settings

        note:: CLASSMETHOD
        '''
        for cmd in command_list:
            if cmd.is_writable:
                setattr(cls,
                        f'set_{cmd.command}',
                        cls._build_function(cmd, is_write=True))
            setattr(cls,
                    f'query_{cmd.command}',
                    cls._build_function(cmd, is_write=False))

        # now instantiation variables for everything. Lists don't have anything in them yet.
        for cmd in command_list:
            if not (cmd.addr_t is None) and not (cmd.val_t is None):  
                # if there is an address, and a value, there is a list of possible values
                setattr(cls, cmd.command, list())
            elif not (cmd.addr_t is None) and cmd.val_t is None:  
                # the registration command has no value
                setattr(cls, cmd.command, False)
            else:  # If no address in command, value is a single number
                setattr(cls, cmd.command, 0)

    def _generate_variables(self, num_channels: int):
        """
        Go through all commands and create variables for them. Channel commands are instantiated as lists so that
        each channel value can be stored with the channel number as index. The lists need to be appended to correct
        once the number of channels is known.

        :return:
        """

        for cmd in command_list:
            if cmd.command.startswith('channel_'):
                # stored as a list
                for _ in range(num_channels):
                    getattr(self, cmd.command).append(0)
            # The offset variables are stored as a single number lists for now
            elif cmd.addr_t is not None and cmd.val_t is not None:  # if there is an address, there is a value in a list
                getattr(self, cmd.command).append(0)

    def _parse(self, msg: can.Message) -> None:
        """
        Parses DCP/EDCP messages into address, value pairs. No functionality if no address or data.
        After parsing, the data is updated to class variables.

        All bitstrings are interpreted as the integer type of their size.

        :param msg: The incoming can.Message
        :return:    None
        """
        # print('In parse:')

        if bytes(msg.data[:2]) in c_bytes:
            command = c_bytes[bytes(msg.data[:2])]
            cmd_len = 2
        elif bytes(msg.data[:1]) in c_bytes:
            # probably a registration command
            command = c_bytes[bytes(msg.data[:1])]
            cmd_len = 1
        else:
            raise KeyError(f'Unknown message from the module: "{msg.data.hex()}"!')
        is_addr = False
        is_val = False
        fmt = '>'
        if command.addr_t is not None:
            is_addr = True
            fmt += command.addr_t
        if command.val_t is not None:
            is_val = True
            fmt += command.val_t

        address = None
        data = None
        if all((is_addr, is_val)):
            # This is a channel command or one of the module commands accepting offset, to have an address and a value
            # They are instantiated as lists in _generate_variables. 
            try:
                address, data = unpack(fmt, msg.data[cmd_len:])
            except:
                print(f'Malformed reply for {command.command}')
                print('debug: ', fmt, bytes(msg.data[cmd_len:]))
                return command, None, None
            #print(f'*********  {command.command}, channel: {address}, Module: {self.module_id}, value: {getattr(self, command.command)[address]}')
            datavar = getattr(self, command.command)
            datavar[address] = data
            setattr(self, command.command, datavar)
        elif is_addr:
            # Address without a value in response - register. This should not be caught
            address = unpack(fmt, msg.data[cmd_len:])[0]
            setattr(self, command.command, address)
        elif is_val:
            # Most module commands fall into this. There are some commands that return a tuple. This is not handled.
            # print(msg.data.hex(), cmd_len, fmt)
            data = unpack(fmt, msg.data[cmd_len:])[0]
            setattr(self, command.command, data)
        return command, data, address

    def _listen(self, expected_cmd: str=None, require_answer=False, timeout=0.3)-> bool:
        """ 
        _listen sends the messages to _parse to be processed. It returns True if message was found in the 
        buffer.

        A message in a buffer is, however, not a proof of a successful execution of a command. It could be 
        a command sent by the module (trip alarm etc.) or a response to an earlier query that was not listened 
        before current call.

        True is only set if received message matches the expected.
        
        """
        # print('Listening for', expected_cmd)
        start = time.time()
        elapsed = 0.0
        retval = False
        got_data = False
        while True: 
            try:
                msg = self._reader.get_message(timeout=timeout) 
                if not msg is None and msg.arbitration_id == self.can_id:
                    cmd_t, data, address = self._parse(msg)
                    if cmd_t.command == expected_cmd:
                        retval = True
                    got_data = True
                elif msg is None and got_data:
                    break

                elapsed = time.time() - start
                #    
                if elapsed < timeout:  # wait a bit if no messages in queue
                #    time.sleep(short_wait)
                    continue
                else:
                    break
            except TimeoutError:
                    pass
                    
            except:
                print('An exeption in _listen!')
                raise

        return retval

    def _flush(self):
        # Flush buffers
        while True:
            msg = self._reader.get_message(timeout=0.01) 
            if msg is None:
                break

    def __del__(self):
        # let the name spamming continue
        self._unregister_module()
        
        print('Exiting module', self.module_id)
        self._notifier.stop()
        self._bus.shutdown()
        time.sleep(0.5)
        print('Exit!')
    
    # Utility commands. They all default to the (value, channel) format, but only some of them can be written to and
    # reset returns full status.
    def module_status_query(self, _val, ch:int):
        """
        15 isKillEnable
        14 isTemperatureGood
        13 isSupplyGood
        12 isModuleGood
        11 isEventActive
        10 isSafetyLoopGood"
         9 isNoRamp
         8 isNoSumError
         7 Reserved
         6 isInputError
         5 isHardwareVoltageLimitGood
         4 needService
         3 isHighVoltageOn
         2 isLiveInsertion
         1 Reserved 
         0 isFineAdjustment
        """
        status = self.query_module_status(None, None)
        return status

    
    def channel_status_query(self, _val, ch:int):
        """
        15    isVoltageLimitExceeded 
        14    IsCurrentLimitExceeded 
        13    isTripExceeded 
        12    isExternalInhibit 
        11    isVoltageBoundsExceeded isCurrent
        10    BoundsExceeded 
        09    isArcError 
        08    isLowCurrentRange
        07    isConstantVoltage 
        06    isConstantCurrent 
        05    isEmergency 
        04    isRamp 
        03    isOn 
        02    inputError 
        01    isArc 
        00    Reserved
        """
        status = self.query_channel_status(None, ch)
        return status

    def state(self, val:int, ch:int)-> bool:  #
        """ Set the channel on bit. """
        if val > 0:
            self.set_module_event_status(1024, ch)
        self.set_channel_control(val * 8, ch)  # fourth bit is set by user
        status = self.query_channel_control(None, ch)
        is_on = (status & 8) > 0
        return is_on

    def state_query(self, _val, ch:int)->bool:  # , astate:Optional[bool]=None)->bool:
        """ read the channel on bit. """
        status = self.query_channel_control(None, ch)
        is_on = (status & 8) > 0
        return is_on
 
    def ramp_speed(self, val:float, ch)-> float:
        """
        Makes sense to operate in V/s, so first need to get the nominal voltage and calculate correct percentage.
        """
        # operate on ch0, no matter which kind of a module it is
        nominal_voltage = self.query_channel_nominal_voltage(None, 0)
        speed_in_percentage = val/abs(nominal_voltage)*100
        self.set_module_voltage_ramp_speed(speed_in_percentage, None)
        return self.ramp_speed_query(None, None)

    def ramp_speed_query(self, _val, _ch)-> float:
        speed_in_percentage = self.query_module_voltage_ramp_speed(None, None)
        nominal_voltage = self.query_channel_nominal_voltage(None, 0)
        speed_in_V_per_s = abs(nominal_voltage) * speed_in_percentage/100
        return speed_in_V_per_s

    def reset_trip(self, _val, ch:int)-> int:
        """
        bit event                       blocking    
        15  EventVoltageLimitExceeded   Yes
        14  EventCurrentLimitExceeded   Yes 
        13  EventTrip Yes 
        12  EventExternalInhibit        Yes 
        11  EventVoltageBounds 
        10  EventCurrentBounds 
        09  EventArcError 
        08  Reserved
        07  EventConstantVoltage 
        06  EventConstantCurrent 
        05  EventEmergencyOff           Yes
        04  EventEndOfRamp 
        03  EventOnToOff 
        02  EventInputError 
        01  EventArc
        00  Reserved

        Full reset of the blocking statuses should then be 53280 ('0b1101000000100000')
        """
        self.set_channel_event_status(53280, ch)
        event_status = self.query_channel_event_status(None, ch)
        return event_status

    def voltage_out_measure(self, _val, ch:int)-> float:
        """
        Read voltage, no intelligence.
        """
        v_meas = self.query_channel_voltage_measurement(None, ch)
        return v_meas

    def voltage_set(self, val:float, ch:int)-> float:
        """
        Set voltage.
        """
        timeout = 5.0
        _out = self.set_channel_set_voltage(val, ch)
        v_set = self.query_channel_set_voltage(None, ch)
        return v_set

    def voltage_set_query(self, _val, ch:int)-> float:
        """
        Query set voltage.
        """
        v_set = self.query_channel_set_voltage(None, ch)
        return v_set

    def current_out_measure(self, _val, ch:int)-> float:
        """
        Read current, no intelligence.
        """
        c_meas = self.query_channel_current_measurement(None, ch)
        return c_meas

    def current_set(self, val:float, ch:int)-> float:
        """
        Set current limit
        """
        _out = self.set_channel_set_current(val, ch)
        c_meas = self.query_channel_set_current(None, ch)
        return c_meas

    def current_set_query(self, _val, ch:int)-> float:
        """
        Set current limit
        """
        c_meas = self.query_channel_set_current(None, ch)
        return c_meas


def get_address(module_num: int, alarm: bool, nmt: bool, reply: bool, write: bool) -> int:
    return alarm << 9 | module_num << 3 | (nmt << 2) | (reply << 1) | (not write)


def test_connection(module_id: int, logging: bool = False):
    resource = Resource(module_id, logging=logging)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        module_id = int(sys.argv[1])
    else:
        raise Exception('No module id given')
    test_connection(module_id=module_id, logging=True)


