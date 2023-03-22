#En este codigo se leera 1 o varios canales a una frecuencia (muestras por segundo) dada por el usuario.

from __future__ import print_function
from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,ScanOption, create_float_buffer, InterfaceType, AiInputMode)
from time import sleep
from os import system
from sys import stdout

def main():

    """Analog input scan example."""
    daq_device = None
    ai_device = None
    status = ScanStatus.IDLE

    range_index = 2
    interface_type = InterfaceType.ANY
    low_channel = 0
    high_channel = 0
    samples_per_channel = 1
    frec = 10
    frec2 = 100
    scan_options = ScanOption.CONTINUOUS
    flags = AInScanFlag.DEFAULT
    n = 1

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
        
        # Verificamos si dispositivo DAQ especificado es compatible con una entrada analógica controlada por hardware
        ai_info = ai_device.get_info()
        if not ai_info.has_pacer():
            raise RuntimeError('\nError: El dispositivo DAQ especificado no es compatible con la entrada analógica controlada por hardware')

        # Establecemos la conexion con el dispositivo DAQ, 3 flash de led indica que la conexion fue exitosa
        descriptor = daq_device.get_descriptor()
        print('\nConectando con', descriptor.dev_string, '- por favor espere')
        daq_device.connect(connection_code=0)
        if daq_device.is_connected() == True:
            daq_device.flash_led(3)
        else:
            raise RuntimeError('Error: No se pudo hacer conexion con el dispositivo')

        # La entrada por defecto es SINGLE_ENDED.
        input_mode = AiInputMode.SINGLE_ENDED

        # conseguimos el numero de canales y validamos el numero del canal superior.
        number_of_channels = ai_info.get_num_chans_by_mode(input_mode)
        if high_channel >= number_of_channels:
            high_channel = number_of_channels - 1
        channel_count = high_channel - low_channel + 1

        # Obtenemos un lista de rango de voltajes validos
        ranges = ai_info.get_ranges(input_mode)

        # separamos un espacion de memoria para la informacion a recibir.
        data1 = create_float_buffer(channel_count, samples_per_channel)

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Canales: ', low_channel, '-', high_channel)
        print('    Input mode: ', input_mode.name)
        print('    Rango: ', ranges[range_index].name)
        print('    Muestras por canal: ', samples_per_channel)
        print('    Frecuencia: ', frec, 'Hz')
        print('    Scan options:', display_scan_options(scan_options))

        try:
            input('\nPresionar ENTER para continuar\n')
            txt = open('datosDAQ.txt','w')
            txt2 = open('datos2DAQ.txt','w')
            txt.write('Frecuencia de muestreo en muestras por segundo:' + str(frec) + '\n')
            txt2.write('Frecuencia de muestreo en muestras por segundo:' + str(frec2) + '\n')

        except (NameError, SyntaxError):
            pass

        system('clear')

        # Empezamos la adquisicion.
        rate = ai_device.a_in_scan(low_channel, high_channel, input_mode,ranges[range_index], samples_per_channel,frec, scan_options, flags, data1)

        aux = data1[0]
        ver = True

        try:
            # bucle para la toma de datos
            while True:
                try:
                    # Obtenemos el estado de la operacion en segundo plano
                    status, transfer_status = ai_device.get_scan_status()

                    reset_cursor()
                    # Mensaje de inicializacion
                    print('Porfavor Presione CTRL + C para terminar con el proceso\n')
                    print('Dispositivo DAQ activo: ', descriptor.dev_string, ' (',descriptor.unique_id, ')\n', sep='')
                    print('Frecuencia de escaneo actual = ', '{:.6f}'.format(frec), 'Hz\n')

                    index = transfer_status.current_index
                    print('currentTotalCount = ',transfer_status.current_total_count)
                    print('currentScanCount = ',transfer_status.current_scan_count)
                    print('currentIndex = ', index, '\n')

                    if data1[index + i] == aux and ver == True:
                        txt.write(str(data1[index + i])+'\n')
                        ver = False
                    elif data1[index + i] != aux:
                        aux = data1[index + i]
                        ver = True

                    print('chan =',i + low_channel, ': ','{:.8f}'.format(data1[index + i]))

                    #for i in range(channel_count):
                        #clear_eol()
                        #print('chan =',i + low_channel, ': ','{:.8f}'.format(data[index + i]))
                        #n = data[index + i]
                        #print(n, 'info')
                        #print(data[index + i], 'info para guardar')
                        #txt.write(str(data[index + i]) + '\n' )

                    
                    #sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass
    except RuntimeError as error:
        print('\n', error)
    finally:
        if daq_device:
            # Stop the acquisition if it is still running.
            if status == ScanStatus.RUNNING:
                ai_device.scan_stop()
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()

def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')

def display_scan_options(bit_mask):
    """Create a displays string for all scan options."""
    options = []
    if bit_mask == ScanOption.DEFAULTIO:
        options.append(ScanOption.DEFAULTIO.name)
    for option in ScanOption:
        if option & bit_mask:
            options.append(option.name)
    return ', '.join(options)

if __name__ == '__main__':
    main()