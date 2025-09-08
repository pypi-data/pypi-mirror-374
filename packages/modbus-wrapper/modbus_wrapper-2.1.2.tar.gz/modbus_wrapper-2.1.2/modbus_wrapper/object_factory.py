from .objects import ModbusObject
from typing import List


class ModbusObjectValidation(Exception):
    pass


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def get_modbus_object(
    modbus_number: int,
    value_to_write: int | bool = None,
    unit: int = 0,
    *args,
    **kwargs,
) -> ModbusObject:
    for object_class in all_subclasses(ModbusObject):
        try:
            modbus_number = int(modbus_number)
        except ValueError:
            modbus_number = modbus_number
        modbus_number_ok = modbus_number in object_class.NUMBER_RANGE_FAST

        if modbus_number_ok:
            return object_class(modbus_number, value_to_write, unit, *args, **kwargs)

    raise ModbusObjectValidation(
        f"provided number {modbus_number} is not valid Modbus object"
    )


def get_modbus_object_from_range(
    number_range: str, unit: int = 0
) -> List[ModbusObject]:
    """ """

    first_object_number = number_range.split("-")[0]
    last_object_number = number_range.split("-")[1]

    try:
        first_object_number = int(first_object_number)
        last_object_number = int(last_object_number)
    except ValueError:
        first_object_number = first_object_number
        last_object_number = last_object_number

    first_object = get_modbus_object(first_object_number)
    all_numbers = list(first_object.NUMBER_RANGE)
    index_of_first_obj = all_numbers.index(first_object_number)
    index_of_last_obj = all_numbers.index(last_object_number)

    objects_in_range = []

    for number in range(index_of_first_obj, index_of_last_obj + 1):
        objects_in_range.append(get_modbus_object(all_numbers[number], None, unit))

    return objects_in_range
