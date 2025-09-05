# IsegCAN

## Description
Simple library for controlling ISEG HV modules in a single crate over CAN bus. 

The library is just a wrapper around the Iseg DHCP command set. Most single channel and Module commands in the Iseg CAN control protocol have been implemented (see definitions.py). Some often used operations have been exposed as methods, but the raw CAN commands can be accessed

## Installation
IsegCAN uses python-can, and specifically the SocketCAN interface. Documentation can be found from https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html

For a quick start, the next few lines should work for PEAK usb adapter:
```
# Create a can network interface with a specific name
sudo ip link set can0 up type can bitrate 125000
```
Note that the bitrate depends on the setup of your Iseg modules. All connections fail and interface is brought down if the bitrate is wrong.

## Usage
The library has only one class, the resource. The resource object is used to control a single module.

Most EDCP commands are automatically generated from a dictionary in _edcp_definitions.py, but only small subset of them 
have been tested. They can be run using the automatically generated set_command and query_command methods, which have 
the same signature (value, channel). Type of value depends on the command. It is only used for set commands. Address is 
unsigned one-byte integer for the channel number in the module or for an offset for some module commands.

The query commands return a value and update the state of the resource directly in the resource object once they are 
read from the buffer. This is done automatically but is not synchronized, so there is a possibility of retrieving stale
data.

For ease of use, some methods have been defined for the most common uses. These are:

| **command**                          | **direction** | **description**                                       |
|--------------------------------------|---------------|-------------------------------------------------------|
| status(_value, channel)              | r             | Returns the 16-bit channel status                     |
| state(value, channel)                | w             | Set channel on or off                                 |
| state_query(_value, channel)         | r             | Read channel state                                    |
| voltage_out_measure(_value, channel) | r             | Measurement of the voltage                            |
| voltage_set(value, channel)          | w             | Set voltage                                           |
| voltage_set_query(_value, channel)   | r             | Read set voltage value                                |
| current_out_measure(_value, channel) | r             | Measurement of the current.                           |
| current_set(value, channel)          | w             | Set current limit                                     |
| current_set_query(_value, channel)   | r             | Read current limit                                    |
| ramp_speed(value, _channel)          | w             | Set ramp speed (in V/s. Max 20% of max voltage) |
| ramp_speed_query(_value, _channel)   | r             | Read ramp speed                                       | 
| reset_trip(_value, _channel)         | w             | Reset all trips                                       |


The rw commands either read the value (value = None) or write the value (value = new value).

## Random remarks
For some reason, the channel commands for ramp speed don't work with either of our Iseg modules (EHS F460n-F, EHS 84 60n). All ramp speed 
commands are therefore made using module command relative to the nominal voltage of channel 0.

## Support
Hmmm?

## Roadmap
The objective is to be functional with Dirigent via ICICLE. Other features may be decided in the future

## License
MIT

