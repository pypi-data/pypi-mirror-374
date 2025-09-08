from .base import ModbusBaseClientWrapper
from pymodbus.client import ModbusSerialClient, ModbusTcpClient, ModbusUdpClient
from .. import modbus_function_code


class ModbusTcpClientWrapper(ModbusTcpClient, ModbusBaseClientWrapper):

    def __init__(
        self,
        host="localhost",
        port=502,
        raise_on_error: bool = False,
        max_read_size: dict = None,
        read_mask: dict = None,
        max_write_size: dict = None,
        *args,
        **kwargs
    ):
        ModbusTcpClient.__init__(self, host=host, port=port, *args, **kwargs)
        ModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )


class ModbusUdpClientWrapper(ModbusUdpClient, ModbusBaseClientWrapper):
    def __init__(
        self,
        host="localhost",
        port=502,
        raise_on_error: bool = False,
        max_read_size: dict = None,
        read_mask: dict = None,
        max_write_size: dict = None,
        *args,
        **kwargs
    ):
        ModbusUdpClient.__init__(self, host=host, port=port, *args, **kwargs)
        ModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )


class ModbusSerialClientWrapper(ModbusSerialClient, ModbusBaseClientWrapper):

    def __init__(
        self,
        port,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        raise_on_error: bool = False,
        max_read_size: dict = None,
        read_mask: dict = None,
        max_write_size: dict = None,
        *args,
        **kwargs
    ):

        ModbusSerialClient.__init__(
            self,
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            *args,
            **kwargs
        )

        ModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )
