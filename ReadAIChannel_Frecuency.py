#En este codigo se leera 1 o varios canales a una frecuencia (muestras por segundo) dada por el usuario.

from uldaq import (get_daq_device_inventory,DaqDevice,InterfaceType,AiInputMode,AInFlag)
from os import system
from sys import stdout
from time import sleep

def main():

    rango_volt = 0
    canal_inicio = 0
    canal_fin = 0
    frecuancia = 0

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

    except RuntimeError as error:
        print('\n', error)

def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')

if __name__ == '__main__':
    main()