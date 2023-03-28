from __future__ import print_function
from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,ScanOption, create_float_buffer, InterfaceType, AiInputMode)
from time import sleep
from os import system
from sys import stdout
import numpy as np
from gnuradio import gr




class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, frecuencia=25.0, rango_index=0.0, low_channel=0.0, high_channel=0.0, samples_per_channel=1.0):  # only default arguments here
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


    def work(self, input_items, output_items):
        """example: multiply with constant"""
        #output_items[0][:] = self.frecuencia
        """codigo para tarjeta de adquisicion"""

        return len(output_items[0])