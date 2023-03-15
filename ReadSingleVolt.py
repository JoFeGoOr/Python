from uldaq import (get_daq_device_inventory,DaqDevice,InterfaceType)

def main():
    interface_type = InterfaceType.ANY

    try:
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)

        if number_of_devices == 0:
            raise RuntimeError('Error: No dispositivo DAQ encontrado')
        
        print(number_of_devices, 'Dispositivo(s) DAQ encontrado(s):')

        for i in range(number_of_devices):
            print('  [', i, '] ', devices[i].product_name, ' (',
                  devices[i].unique_id, ')', sep='')
            
        if number_of_devices != 1:
            descriptor_index = input('\nSeleccione un dispositivo DAQ, ingrese un numero'
                                 + ' entre 0 y '
                                 + str(number_of_devices - 1) + ': ')
            descriptor_index = int(descriptor_index)
            if descriptor_index not in range(number_of_devices):
                raise RuntimeError('Error: Indice descriptor invalido')
        else:
            descriptor_index = 0

        # Crea el dispositivo DAQ desde el descriptor con el indice especificado.
        daq_device = DaqDevice(devices[descriptor_index])

        # Obtiene el objeto AIDevice y verifica si es valido.
        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise RuntimeError('Error: El dispositivo DAQ no soporta '
                               'entradas analogicas')
        
        # Establecemos la conexion con el dispositivo DAQ
        descriptor = daq_device.get_descriptor()
        print('\nConectando con', descriptor.dev_string, '- por favor espere')

    except RuntimeError as error:
        print('\n', error)



main()
