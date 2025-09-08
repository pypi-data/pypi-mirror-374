# modbus_wrapper

wrapper for pyModbusTCP accepting all Modbus numbers with Fatek support

## read

List of different Modbus types can be provided in the input:

Reading Coils, Holding registers and Discrete input:
```python
>> client = ModbusClient("10.0.57.30")
>> modbus_object_list = [20,20,30,31,32,33,33, 400800, 400801, 100300]
>> client read(modbus_list)
{'20': 'False', '30': 'False', '31': 'True', '32': 'True', '33': 'False', '400800': '0', '400801': '0', '100300': 'None'}
```

For above example only 3 modbus function calls will be executed:
```python
read_coils(19, 14)
read_holding_registers(799, 2)
read_discrete_inputs(299, 1)
```

* All coils are read in one function call thanks to **MaxReadSize** and **ReadMask** parameters which can be configured in [modbus object config file](modbus_wrapper/objects/config.py)

```python
client.read(modbus_list, max_read_size=1)
```

For above example, 8 modbus functions will be executed:
```python
read_coils(19, 1)
read_coils(29, 1)
read_coils(30, 1)
read_coils(31, 1)
read_coils(32, 1)
read_holding_registers(799, 1)
read_holding_registers(800, 1)
read_discrete_inputs(299, 1)
```

### read with range

## read_modbus_objects

## write

## write_modbus_objects

## Fatek Support 

### Fatek table

| Modbus | FATEK | Description |
| ------ | ----- | -----------
| 000001～000256 | Y0～Y255 | Discrete Output
| 001001～001256 | X0～X255 | Discrete Input
| 002001～004002 | M0～M2001 | Discrete M Relay
| 006001～007000 | S0～S999 | Discrete S Relay
| 009001～009256 | T0～T255 | Status of T0～T255
| 009501～009756 | C0～C255 | Status of C0～C255
| 400001～404168 | R0～R4167 | Holding Register
| 405001～405999 | R5000～R5998 | Holding Register or ROR
| 406001～408999 | D0～D2998 Data | Register
| 409001～409256 | T0～T255 | Current Value of T0～T255
| 409501～409700 | C0～C199 | Current Value of C0～C199( 16-bit)
| 409701～409812 | C200～C255 | Current Value of C200～C255( 32-bit)