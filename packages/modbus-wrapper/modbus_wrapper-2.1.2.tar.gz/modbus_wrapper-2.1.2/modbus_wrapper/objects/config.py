from dataclasses import dataclass


@dataclass
class MaxReadSize:
    COIL = 2000
    DISCRETE_INPUT = 2000
    INPUT_REGISTER = 125
    HOLDING_REGISTER = 125


@dataclass
class ReadMask:
    COIL = 0xFFFF
    DISCRETE_INPUT = 0xFFFF
    INPUT_REGISTER = 0xFFFF
    HOLDING_REGISTER = 0xFFFF


@dataclass
class MaxWriteSize:
    COIL = 1968
    HOLDING_REGISTER = 123
