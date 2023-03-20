#En este codigo se leera 1 o varios canales a una frecuencia (muestras por segundo) dada por el usuario.

from uldaq import (get_daq_device_inventory,DaqDevice,InterfaceType,AiInputMode,AInFlag)
from os import system
from sys import stdout
from time import sleep

def main():

    rango_volt = 0
    canal_inicio = 0
    canal_fin = 0
    frecuencia = 0

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

        # Pedimos al usuario los valores de trabajo
        canal_inicio = input('Ingrese el primer canal en el que se hara una lectura: ')
        canal_inicio = int(canal_inicio)
        canal_fin = input('Ingrese el ultimo canal en el que se hara una lectura: ')
        canal_fin = int(canal_fin)
        rango_volt = input('Ingrese el rango de voltajes (0=+-10v;1=+-5v;2=+-2v;3=+-1v): ')
        rango_volt = int(rango_volt)
        frecuencia = input('Indique la frecuencia de muestreo con la que se desa trabajar en hertz: ')
        frecuencia = int(frecuencia)

        print('\n', descriptor.dev_string, ' listo', sep='')
        print('    Canal: ', canal_inicio, ' a ', canal_fin)
        print('    Modo Input: ', input_mode.name)
        print('    Rango: ', ranges[rango_volt].name)

    except RuntimeError as error:
        print('\n', error)

def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')

if __name__ == '__main__':
    main()