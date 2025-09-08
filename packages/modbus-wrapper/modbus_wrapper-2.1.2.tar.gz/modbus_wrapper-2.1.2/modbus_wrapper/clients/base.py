import logging
from typing import List
from .. import modbus_function_code
from ..object_factory import (
    ModbusObject,
    get_modbus_object,
    get_modbus_object_from_range,
)
from ..function_argument import ReadFunctionArgument, WriteFunctionArgument
from pymodbus.pdu.bit_message import ModbusPDU
from pymodbus.pdu.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config

pymodbus_apply_logging_config(level=logging.ERROR)

LOG = logging.getLogger(__name__)


class FunctionUnknow(Exception):
    pass


class ObjectNonWriteable(Exception):
    pass


class ModbusConnectionError(Exception):
    pass


class ModbusException(Exception):
    def __init__(self, response: ExceptionResponse):
        self.response = response

    def __str__(self):
        return f"{self.response.function_code} Code: {self.response.exception_code}"


class ModbusBaseClientWrapper:

    def __init__(
        self,
        raise_on_error,
        max_read_size: dict = None,
        read_mask: dict = None,
        max_write_size: dict = None,
    ):

        self.raise_on_error = raise_on_error

        self.function_map = {
            modbus_function_code.READ_COILS: self.read_coils,
            modbus_function_code.READ_HOLDING_REGISTERS: self.read_holding_registers,
            modbus_function_code.READ_DISCRETE_INPUTS: self.read_discrete_inputs,
            modbus_function_code.READ_INPUT_REGISTERS: self.read_input_registers,
            modbus_function_code.WRITE_SINGLE_COIL: self.write_coil,
            modbus_function_code.WRITE_SINGLE_HOLDING_REGISTER: self.write_register,
            modbus_function_code.WRITE_MULTIPLE_COILS: self.write_coils,
            modbus_function_code.WRITE_MULTIPLE_HOLDING_REGISTERS: self.write_registers,
        }

        max_read_size = max_read_size or {}
        read_mask = read_mask or {}
        max_write_size = max_write_size or {}

        self.max_read_size_map = {
            modbus_function_code.READ_COILS: max_read_size.get("coil", None),
            modbus_function_code.READ_HOLDING_REGISTERS: max_read_size.get(
                "holding_register", None
            ),
            modbus_function_code.READ_DISCRETE_INPUTS: max_read_size.get(
                "discrete_input", None
            ),
            modbus_function_code.READ_INPUT_REGISTERS: max_read_size.get(
                "input_register", None
            ),
        }

        self.read_mask_map = {
            modbus_function_code.READ_COILS: read_mask.get("coil", None),
            modbus_function_code.READ_HOLDING_REGISTERS: read_mask.get(
                "holding_register", None
            ),
            modbus_function_code.READ_DISCRETE_INPUTS: read_mask.get(
                "discrete_input", None
            ),
            modbus_function_code.READ_INPUT_REGISTERS: read_mask.get(
                "input_register", None
            ),
        }

        self.max_write_size_map = {
            modbus_function_code.WRITE_MULTIPLE_COILS: max_write_size.get("coil", None),
            modbus_function_code.WRITE_MULTIPLE_HOLDING_REGISTERS: max_write_size.get(
                "holding_register", None
            ),
        }

    def read(
        self, modbus_numbers: List[int | str], unit: int = 0, *args, **kwargs
    ) -> dict:

        modbus_objects = self._get_modbus_objects(modbus_numbers, unit)

        self.read_modbus_objects(modbus_objects, *args, **kwargs)

        return self._get_dict_results_from_objects(modbus_objects)

    def read_modbus_objects(self, modbus_objects: List[ModbusObject]) -> None:
        arguments = ReadFunctionArgument.get_arguments(
            modbus_objects,
            max_read_size_map=self.max_read_size_map,
            read_mask_map=self.read_mask_map,
        )

        with self:
            if not self.connected:
                raise ModbusConnectionError("Modbus connection not established")
            for arg in arguments:
                self._read(arg)

    def write(self, modbus_numbers_with_values: dict, unit: int = 0) -> dict:
        modbus_objects = [
            get_modbus_object(n, v, unit) for n, v in modbus_numbers_with_values.items()
        ]

        self.write_modbus_objects(modbus_objects)

        return self._get_dict_results_from_objects(modbus_objects)

    def write_modbus_objects(self, modbus_objects: List[ModbusObject]):
        arguments = WriteFunctionArgument.get_arguments(
            modbus_objects,
            max_write_size_map=self.max_write_size_map,
        )

        with self:
            if not self.connected:
                raise ModbusConnectionError("Modbus connection not established")
            for arg in arguments:
                self._write(arg)

    def _pre_logging(
        self,
        argument: WriteFunctionArgument | ReadFunctionArgument,
        function_string: str,
    ) -> tuple:
        LOG.debug(f'executing function: "{function_string}" for argument: "{argument}"')

    def _update_objects_with_write_values(
        self,
        write_response: ModbusPDU,
        write_argument: WriteFunctionArgument,
        function_string: str,
    ) -> None:

        write_error = write_response.isError()

        if not write_error:
            [obj.current.update(obj.write.value) for obj in write_argument.objects]
        else:
            LOG.error(
                f'failed to write "{function_string}" for argument: "{write_argument}"'
            )
            return

        return not write_error

    def _write(self, write_argument: WriteFunctionArgument):
        write_function = self._get_function(write_argument.write_function_code)
        function_string = write_function.__doc__.splitlines()[0]
        self._pre_logging(write_argument, function_string)

        write_response: ModbusPDU = write_function(
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

    def _update_objects_with_collected_values(
        self,
        argument: ReadFunctionArgument,
        read_result: ModbusPDU,
        function_string: str,
    ) -> bool:

        collected_values = {
            argument.starting_address: read_result.bits or read_result.registers
        }

        LOG.debug(f'results: "{collected_values[argument.starting_address]}"')

        if (
            not collected_values[argument.starting_address] or read_result.isError()
        ):  # None means no reply from modbus target
            LOG.error(f"{function_string} failed to read {argument}")
            collected_values[argument.starting_address] = [
                None for i in range(0, argument.size)
            ]  # Fill all results with None, when no reply from Modbus target
            return

        increment = 0
        for value in collected_values[argument.starting_address]:
            collected_values[argument.starting_address + increment] = value
            increment += 1

        for object in argument.objects:
            object.current.update(collected_values[object.address])
        return True

    def _read(self, argument: ReadFunctionArgument) -> None:

        read_function = self._get_function(argument.type.FUNCTION_CODE.read)
        function_string = read_function.__doc__.splitlines()[0]
        self._pre_logging(argument, function_string)
        read_result: ModbusPDU = read_function(
            address=argument.starting_address, count=argument.size, slave=argument.unit
        )
        if read_result.isError() and self.raise_on_error:
            raise ModbusException(read_result)

        self._update_objects_with_collected_values(
            argument,
            read_result,
            function_string,
        )

    def _get_function(self, code: [hex, int]):
        """Get modbus function by code"""
        try:
            function = self.function_map[code]
        except KeyError:
            raise FunctionUnknow(f"code {code} not valid")

        return function

    def _get_modbus_objects(
        self,
        modbus_numbers: List[int | str],
        unit: int = 0,
    ) -> List[ModbusObject]:

        modbus_objects = []

        for n in modbus_numbers:
            try:
                range_entry = "-" in n
            except TypeError:
                range_entry = False

            if range_entry:
                modbus_objects = modbus_objects + get_modbus_object_from_range(n, unit)
            else:
                modbus_objects.append(get_modbus_object(n, None, unit))

        return modbus_objects

    def _get_dict_results_from_objects(
        self, modbus_objects: List[ModbusObject]
    ) -> dict:
        return {obj.__repr__(): obj.current.__repr__() for obj in modbus_objects}
