import logging
from dataclasses import dataclass
from typing import List, Type
from collections import namedtuple
from .objects import ModbusObject

LOG = logging.getLogger(__name__)


class CommonModbusObjectsUniqueException(Exception):
    pass


class ModbusWriteValueException(Exception):
    pass


@dataclass
class CommonModbusObjects:
    """Modbus objects of common type and unit address"""

    type: Type
    unit: int
    objects: List[ModbusObject]

    def __post_init__(self):
        for obj in self.objects:
            if type(obj) != self.type:
                raise CommonModbusObjectsUniqueException(
                    f"Modbus object {obj} is not type of {self.type}"
                )
            if obj.unit != self.unit:
                raise CommonModbusObjectsUniqueException(
                    f"Modbus object {obj} is different unit address {self.unit}"
                )

    @classmethod
    def get_common_modbus_objects(cls, modbus_objects: List[ModbusObject]) -> List:
        """returns list of CommonModbusObjects"""
        ModbusObjectTypesPerUnit = namedtuple(
            "ModbusObjectTypesPerUnit", ["type", "unit"]
        )
        unique_types_per_unit = list(
            {ModbusObjectTypesPerUnit(type(i), i.unit) for i in modbus_objects}
        )
        list_to_return = []
        for unique in unique_types_per_unit:
            match_unique = (
                lambda obj: type(obj) == unique.type and obj.unit == unique.unit
            )
            single_type_modbus_objects = list(filter(match_unique, modbus_objects))
            list_to_return.append(
                cls(unique.type, unique.unit, single_type_modbus_objects)
            )
        return list_to_return


class FunctionArgument:
    def _calculate_read_size(
        addresses, max_read_size: int = 1, read_mask: int = 1
    ) -> List[dict]:
        results = []
        done_list = set()
        addresses = sorted(addresses)

        for i in range(len(addresses)):
            if addresses[i] not in done_list:

                result_addresses = []
                read_size = 1
                starting_address = addresses[i]
                result_addresses.append(starting_address)
                remain_addresses = addresses[i + 1 :]
                _read_mask = read_mask
                for remain_address in remain_addresses:
                    prev_elemet_diff = remain_address - starting_address
                    if (
                        prev_elemet_diff <= _read_mask
                        and prev_elemet_diff + 1 <= max_read_size
                    ):
                        read_size = prev_elemet_diff + 1
                        done_list.add(remain_address)
                        result_addresses.append(remain_address)
                    _read_mask += 1

                results.append(
                    {
                        "starting_address": starting_address,
                        "size": read_size,
                        "addresses": result_addresses,
                    }
                )
        return results


@dataclass
class ReadFunctionArgument(FunctionArgument):
    starting_address: int
    size: int
    unit: int
    type: type
    objects: List[ModbusObject]

    @classmethod
    def get_arguments(
        cls,
        modbus_objects: List[ModbusObject],
        max_read_size_map: dict = None,
        read_mask_map: dict = None,
    ) -> list:
        """Function to get read arguments for modbus function from Modbus Objects"""

        common_modbus_objects = CommonModbusObjects.get_common_modbus_objects(
            modbus_objects
        )
        arguments = []
        for common in common_modbus_objects:
            addresses = [obj.address for obj in common.objects]

            max_read_size = max_read_size_map.get(common.type.FUNCTION_CODE.read)
            if not max_read_size:
                max_read_size = common.type.MAX_READ_SIZE

            read_mask = read_mask_map.get(common.type.FUNCTION_CODE.read)
            if not read_mask:
                read_mask = common.type.READ_MASK

            calculated_read_sizes = cls._calculate_read_size(
                addresses, max_read_size=max_read_size, read_mask=read_mask
            )

            for result in calculated_read_sizes:
                staring_address = result["starting_address"]
                size = result["size"]
                addresses = result["addresses"]
                object_list = CommonModbusObjects(
                    common.type,
                    common.unit,
                    [obj for obj in common.objects if obj.address in addresses],
                )
                arguments.append(
                    cls(
                        staring_address,
                        size,
                        common.unit,
                        common.type,
                        object_list.objects,
                    )
                )

        return arguments


@dataclass
class WriteFunctionArgument(FunctionArgument):
    starting_address: int
    values_to_write: List[int | bool] | int | bool
    write_function_code: int
    unit: int
    type: type
    objects: List[ModbusObject]

    @classmethod
    def get_arguments(
        cls, modbus_objects: List[ModbusObject], max_write_size_map: dict = None
    ):
        """Function to get read arguments for modbus function from Modbus Objects"""

        arguments = []
        modbus_objects = filter(cls._filter_write_values, modbus_objects)

        common_modbus_objects = CommonModbusObjects.get_common_modbus_objects(
            list(modbus_objects)
        )

        for common in common_modbus_objects:
            addresses = [obj.address for obj in common.objects]

            max_write_size = max_write_size_map.get(
                common.type.FUNCTION_CODE.multi_write
            )
            if not max_write_size:
                max_write_size = common.type.MAX_WRITE_SIZE

            read_mask = 1
            calculated_write_sizes = cls._calculate_read_size(
                addresses, max_read_size=max_write_size, read_mask=read_mask
            )

            for write in calculated_write_sizes:
                number_of_values_to_write = write["size"]
                starting_address = write["starting_address"]
                ending_address = starting_address + number_of_values_to_write
                get_write_value_for_address = lambda address: next(
                    obj.write.value for obj in common.objects if obj.address == address
                )
                get_objets_for_address = lambda address: next(
                    obj for obj in common.objects if obj.address == address
                )
                addresses_range = range(starting_address, ending_address)

                values_to_write = list(
                    map(get_write_value_for_address, addresses_range)
                )

                single_value_to_write = len(values_to_write) == 1
                if single_value_to_write:
                    values_to_write = values_to_write[0]
                    write_function_code = common.type.FUNCTION_CODE.write
                else:
                    write_function_code = common.type.FUNCTION_CODE.multi_write

                object_list = CommonModbusObjects(
                    common.type,
                    common.unit,
                    list(map(get_objets_for_address, addresses_range)),
                )

                arguments.append(
                    cls(
                        starting_address,
                        values_to_write,
                        write_function_code,
                        object_list.unit,
                        object_list.type,
                        object_list.objects,
                    )
                )

        return arguments

    @staticmethod
    def _filter_write_values(modbus_object: ModbusObject) -> bool:
        if modbus_object.write:
            return True
        LOG.warning(
            f"modbus object {modbus_object} does not contain write value and is excluded from write operation"
        )
        return
