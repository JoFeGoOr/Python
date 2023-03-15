from uldaq import (get_daq_device_inventory,InterfaceType)

def main():
    interface_type = InterfaceType.ANY

    try:
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)
        print(number_of_devices)
        if number_of_devices == 0:
            raise RuntimeError('Error: No DAQ devices found')

    except RuntimeError as error:
        print('\n', error)
