#En este codigo se hace la lectura más basica de un canal analogico, sirve para familiarizarse con la conexion al dispositivo y posibles manejos para
#varios dispositivos conectados al mismo tiempo

from uldaq import (get_daq_device_inventory,DaqDevice,InterfaceType,AiInputMode,AInFlag)
from os import system
from sys import stdout
from time import sleep

def main():

    range_index = 0     #controla que rango de voltajes se usara
    canal = 0           #indica el canal que se ocupara para realizar la lectura.

    try:
        # Obtenemos una lista de objetos(dispositivos) que pueden ser usados como DaqDevice
        devices = get_daq_device_inventory(InterfaceType.ANY)
        number_of_devices = len(devices)

        # Verificamos si existe algun dispositivo conectado
        if number_of_devices == 0:
            raise RuntimeError('Error: No dispositivo DAQ encontrado')
        
        # Describimos la cantidad de objetos(dispositivos) encontrados y el detallle correspondiente
        print(number_of_devices, 'Dispositivo(s) DAQ encontrado(s):')
        for i in range(number_of_devices):
            print('  [', i, '] ', devices[i].product_name, ' (',
                  devices[i].unique_id, ')', sep='')
        
        # Si existe solo 1, su indice es automaticamente 0, si existe mas de 1, se debe verificar con que dispositivo queremos interactuar
        if number_of_devices > 1:
            descriptor_index = input('\nSeleccione un dispositivo DAQ, ingrese un numero entre 0 y ' + str(number_of_devices - 1) + ': ')
            descriptor_index = int(descriptor_index)
            if descriptor_index not in range(number_of_devices):
                raise RuntimeError('Error: Indice descriptor invalido')
        else:
            descriptor_index = 0

        # Crea el dispositivo DAQ desde el descriptor con el indice especificado.
        daq_device = DaqDevice(devices[descriptor_index])

        # Obtiene el objeto AIDevice(Subsistema de entradas analogicas) y verifica si es valido.
        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise RuntimeError('Error: El dispositivo DAQ no soporta entradas analogicas')
        
        # Establecemos la conexion con el dispositivo DAQ, 3 flash de led indica que la conexion fue exitosa
        descriptor = daq_device.get_descriptor()
        print('\nConectando con', descriptor.dev_string, '- por favor espere')
        daq_device.connect(connection_code=0)
        if daq_device.is_connected() == True:
            daq_device.flash_led(3)
        else:
            raise RuntimeError('Error: No se pudo hacer conexion con el dispositivo')

        ai_info = ai_device.get_info()

        # La entrada por defecto es SINGLE_ENDED.
        input_mode = AiInputMode.SINGLE_ENDED

        # Obtenemos un lista de rango de voltajes validos
        ranges = ai_info.get_ranges(input_mode)
        #for i in range(len(ranges)):
        #    print(ranges[i])
        #print(ranges[range_index])

        print('\n', descriptor.dev_string, ' listo', sep='')
        print('    Canal: ', canal)
        print('    Modo Input: ', input_mode.name)
        print('    Rango: ', ranges[range_index].name)

        try:
            input('\nPresionar ENTER para continuar\n')
        except (NameError, SyntaxError):
            pass

        system('clear')

        try:
            # bucle para la toma de datos
            while True:
                try:
                    reset_cursor()
                    # Mensaje de inicializacion
                    print('Porfavor Presione CTRL + C para terminar con el proceso\n')
                    print('Dispositivo DAQ activo: ', descriptor.dev_string, ' (',descriptor.unique_id, ')\n', sep='')
                    data = ai_device.a_in(canal,input_mode,ranges[range_index],AInFlag.DEFAULT)
                    print('canal ',canal,' data: ','{:.6f}'.format(data), sep='')
                    #sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            #system('clear')
            pass


    except RuntimeError as error:
        print('\n', error)

def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')

if __name__ == '__main__':
    main()