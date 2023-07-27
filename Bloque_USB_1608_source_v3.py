from __future__ import print_function
from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,ScanOption, create_float_buffer, InterfaceType, AiInputMode, AInFlag)
from time import sleep
from os import system
from sys import stdout
import numpy as np
from gnuradio import gr




class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, canal = 0, range_index = 0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='USB_1608series_source',   # will show up in GRC
            in_sig=[],
            out_sig=[np.float32]
        )

        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.canal = canal
        self.range_index = range_index
        self.index_output = 0

        self.daq_device = None
        self.ai_device = None
        self.status = ScanStatus.IDLE
        self.scan_options = ScanOption.CONTINUOUS
        self.flags = AInScanFlag.DEFAULT
        self.interface_type = InterfaceType.ANY

        # Realizo la conexion con el dispositivo
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
            self.ai_device = daq_device.get_ai_device()
            if self.ai_device is None:
                raise RuntimeError('Error: El dispositivo DAQ no soporta entradas analogicas')
            
            # Establecemos la conexion con el dispositivo DAQ, 3 flash de led indica que la conexion fue exitosa
            descriptor = daq_device.get_descriptor()
            print('\nConectando con', descriptor.dev_string, '- por favor espere')
            daq_device.connect(connection_code=0)
            if daq_device.is_connected() == True:
                daq_device.flash_led(3)
            else:
                raise RuntimeError('Error: No se pudo hacer conexion con el dispositivo')

            ai_info = self.ai_device.get_info()

            # La entrada por defecto es SINGLE_ENDED.
            self.input_mode = AiInputMode.SINGLE_ENDED

            # Obtenemos un lista de rango de voltajes validos
            self.ranges = ai_info.get_ranges(self.input_mode)

            print('\n', descriptor.dev_string, ' listo', sep='')
            print('    Canal: ', self.canal)
            print('    Modo Input: ', self.input_mode.name)
            print('    Rango: ', self.ranges[self.range_index].name)
            
        except RuntimeError as error:
            print('\n', error)


    def work(self, input_items, output_items):
        """codigo para tarjeta de adquisicion"""
        #print('chan =',self.low_channel, ': ','{:.8f}'.format(self.data[index]))

        for i in range(len(output_items[0])):
            data = self.ai_device.a_in(self.canal,self.input_mode,self.ranges[self.range_index],AInFlag.DEFAULT)
            output_items[0][i] = data
            print(output_items[0][i])

        return len(output_items[0])