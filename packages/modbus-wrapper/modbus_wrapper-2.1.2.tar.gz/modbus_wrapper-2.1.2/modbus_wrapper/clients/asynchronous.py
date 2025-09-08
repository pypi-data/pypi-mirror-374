import logging
import asyncio
from typing import List
from pymodbus.client import (
    AsyncModbusTcpClient,
    AsyncModbusUdpClient,
    AsyncModbusSerialClient,
)
from .base import (
    ModbusBaseClientWrapper,
    ModbusConnectionError,
    ModbusException,
    ModbusPDU,
)
from ..object_factory import get_modbus_object
from ..function_argument import WriteFunctionArgument, ReadFunctionArgument
from ..objects import ModbusObject


LOG = logging.getLogger(__name__)


class AsyncModbusBaseClientWrapper(ModbusBaseClientWrapper):

    async def read(
        self, modbus_numbers: List[int | str], unit: int = 0, *args, **kwargs
    ) -> dict:

        modbus_objects = self._get_modbus_objects(modbus_numbers, unit)

        await self.read_modbus_objects(modbus_objects, *args, **kwargs)

        return self._get_dict_results_from_objects(modbus_objects)

    async def read_modbus_objects(
        self,
        modbus_objects: List[ModbusObject],
    ) -> None:

        arguments = ReadFunctionArgument.get_arguments(
            modbus_objects,
            max_read_size_map=self.max_read_size_map,
            read_mask_map=self.read_mask_map,
        )

        async with self:
            if not self.connected:
                raise ModbusConnectionError("Modbus connection not established")
            tasks = []
            for arg in arguments:
                tasks.append(asyncio.create_task(self._read(arg)))

            results = asyncio.gather(*tasks)
            await results

    async def write(self, modbus_numbers_with_values: dict, unit: int = 0) -> dict:
        modbus_objects = [
            get_modbus_object(n, v, unit) for n, v in modbus_numbers_with_values.items()
        ]

        await self.write_modbus_objects(modbus_objects)

        return self._get_dict_results_from_objects(modbus_objects)

    async def write_modbus_objects(self, modbus_objects: List[ModbusObject]):
        arguments = WriteFunctionArgument.get_arguments(
            modbus_objects,
            max_write_size_map=self.max_write_size_map,
        )

        async with self:
            if not self.connected:
                raise ModbusConnectionError("Modbus connection not established")
            tasks = []
            for arg in arguments:
                tasks.append(asyncio.create_task(self._write(arg)))

            results = asyncio.gather(*tasks)
            await results

    async def _write(self, write_argument: WriteFunctionArgument):

        write_function = self._get_function(write_argument.write_function_code)
        function_string = write_function.__doc__.splitlines()[0]
        self._pre_logging(write_argument, function_string)

        write_response: ModbusPDU = await write_function(
            write_argument.starting_address,
            write_argument.values_to_write,
            slave=write_argument.unit,
        )
        if write_response.isError() and self.raise_on_error:
            raise ModbusException(write_response)

        self._update_objects_with_write_values(
            write_response,
            write_argument,
            function_string,
        )

    async def _read(self, argument: ReadFunctionArgument) -> None:

        read_function = self._get_function(argument.type.FUNCTION_CODE.read)
        function_string = read_function.__doc__.splitlines()[0]

        self._pre_logging(argument, function_string)

        read_result: ModbusPDU = await read_function(
            address=argument.starting_address, count=argument.size, slave=argument.unit
        )
        if read_result.isError() and self.raise_on_error:
            raise ModbusException(read_result)

        self._update_objects_with_collected_values(
            argument, read_result, function_string
        )


class AsyncModbusTcpClientWrapper(AsyncModbusTcpClient, AsyncModbusBaseClientWrapper):
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
        AsyncModbusTcpClient.__init__(self, host=host, port=port, *args, **kwargs)
        AsyncModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )


class AsyncModbusUdpClientWrapper(AsyncModbusUdpClient, AsyncModbusBaseClientWrapper):
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
        AsyncModbusUdpClient.__init__(self, host=host, port=port, *args, **kwargs)
        AsyncModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )


class AsyncModbusSerialClientWrapper(
    AsyncModbusSerialClient, AsyncModbusBaseClientWrapper
):
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
        AsyncModbusSerialClient.__init__(
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
        AsyncModbusBaseClientWrapper.__init__(
            self, raise_on_error, max_read_size, read_mask, max_write_size
        )
