import numpy as np
from gnuradio import gr
from uldaq import (get_daq_device_inventory,DaqDevice,InterfaceType,AiInputMode,AInFlag)
from os import system
from sys import stdout


class blk(gr.sync_block):
    def __init__(self, canal=0,rango_index=0):  
        gr.sync_block.__init__(
            self,
            name='USB_1608series_source',   # will show up in GRC
            in_sig=[],
            out_sig=[np.float32]
        )

        self.canal = canal
        self.rango_index = rango_index
        
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
        print('    Rango: ', self.ranges[self.rango_index].name)

        self.data = self.ai_device.a_in(self.canal,self.input_mode,self.ranges[self.rango_index],AInFlag.DEFAULT)


    def work(self, input_items, output_items):
        output_items[0][:] = self.data
        return len(output_items[0])