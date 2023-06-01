from __future__ import print_function
from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,ScanOption, create_float_buffer, InterfaceType, AiInputMode)
from time import sleep
from os import system
from sys import stdout
import numpy as np
from gnuradio import gr




class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, frecuencia=25, rango_index=0, low_channel=0, high_channel=0, samples_per_channel=1):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='USB_1608series_source',   # will show up in GRC
            in_sig=[],
            out_sig=[np.float32]
        )

        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.frecuencia = frecuencia
        self.rango_index = rango_index
        self.low_channel = low_channel
        self.high_channel = high_channel
        self.samples_per_channel = samples_per_channel

        self.daq_device = None
        self.ai_device = None
        self.status = ScanStatus.IDLE
        self.scan_options = ScanOption.CONTINUOUS
        self.flags = AInScanFlag.DEFAULT
        self.interface_type = InterfaceType.ANY
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
                print('  [', i, '] ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

            # Si existe solo 1, su indice es automaticamente 0, si existe mas de 1, se debe verificar con que dispositivo queremos interactuar
            if number_of_devices > 1:
                descriptor_index = input('\nSeleccione un dispositivo DAQ, ingrese un numero entre 0 y ' + str(number_of_devices - 1) + ': ')
                descriptor_index = int(descriptor_index)
                if descriptor_index not in range(number_of_devices):
                    raise RuntimeError('Error: Indice descriptor invalido')
            else:
                descriptor_index = 0

            # Crea el dispositivo DAQ desde el descriptor con el indice especificado.
            self.daq_device = DaqDevice(devices[descriptor_index])

            # Obtiene el objeto AIDevice(Subsistema de entradas analogicas) y verifica si es valido.
            self.ai_device = self.daq_device.get_ai_device()
            if self.ai_device is None:
                raise RuntimeError('Error: El dispositivo DAQ no soporta entradas analogicas')

            # Verificamos si dispositivo DAQ especificado es compatible con una entrada analógica controlada por hardware
            ai_info = self.ai_device.get_info()
            if not ai_info.has_pacer():
                raise RuntimeError('\nError: El dispositivo DAQ especificado no es compatible con la entrada analógica controlada por hardware')
            
            # Establecemos la conexion con el dispositivo DAQ, 3 flash de led indica que la conexion fue exitosa
            descriptor = self.daq_device.get_descriptor()
            print('\nConectando con', descriptor.dev_string, '- por favor espere')
            self.daq_device.connect(connection_code=0)
            if self.daq_device.is_connected() != True:
                raise RuntimeError('Error: No se pudo hacer conexion con el dispositivo')
            
            # La entrada por defecto es SINGLE_ENDED.
            input_mode = AiInputMode.SINGLE_ENDED

            # conseguimos el numero de canales y validamos el numero del canal superior.
            number_of_channels = ai_info.get_num_chans_by_mode(input_mode)
            if self.high_channel >= number_of_channels:
                self.high_channel = number_of_channels - 1
            self.channel_count = self.high_channel - self.low_channel + 1

            # Obtenemos un lista de rango de voltajes validos
            ranges = ai_info.get_ranges(input_mode)

            # separamos un espacio de memoria para la informacion a recibir.
            self.data = create_float_buffer(self.channel_count, self.samples_per_channel)

            print('\n', descriptor.dev_string, ' ready', sep='')
            print('    Canales: ', self.low_channel, '-', self.high_channel)
            print('    Input mode: ', input_mode.name)
            print('    Rango: ', ranges[self.rango_index].name)
            print('    Muestras por canal: ', self.samples_per_channel)
            print('    Frecuencia: ', self.frecuencia, 'Hz')

            # Empezamos la adquisicion.
            rate = self.ai_device.a_in_scan(low_channel, high_channel, input_mode,ranges[self.rango_index], samples_per_channel,frecuencia, self.scan_options, self.flags, self.data)

        except RuntimeError as error:
            print('\n', error)


    def work(self, input_items, output_items):
        """example: multiply with constant"""
        #output_items[0][:] = self.frecuencia
        """codigo para tarjeta de adquisicion"""
        self.status, self.transfer_status = self.ai_device.get_scan_status()
        index = self.transfer_status.current_index
        #print(index)
        #print('chan =',self.low_channel, ': ','{:.8f}'.format(self.data[index]))
        output_items[0][:] = self.data[index]
        return len(output_items[0])