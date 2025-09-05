#Copyright 2025 Thales
#
# Redistribution and use in source and binary forms, with or 
# without modification, are permitted provided that the following 
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its 
#    contributors may be used to endorse or promote products derived from 
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED 
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


import sys
import struct
from typing import Iterator
from venv import logger
from fido2.hid import CtapHidDevice, list_descriptors, open_connection

from .device import ThalesDevice 
from .const import (thales_vendor_id)


class CtapHidThalesDevice(ThalesDevice, CtapHidDevice):
    def __init__(self, descriptor, connection,):
        ThalesDevice.__init__(self, descriptor.product_name, True)
        CtapHidDevice.__init__(self, descriptor, connection)

        # Set to default value
        self._fido_version = '.'.join(map(str, self._device_version))

        # Setup the Thales Serial Number with this default value
        self.serial_number = descriptor.serial_number

        # if firmware = 31, 2, 3, it returns the FIDO applet version
        self._discovery()
        if( descriptor.vid == thales_vendor_id):
            self._is_thales_device = True

    def __repr__(self):
        try:
            return f"CtapHidThalesDevice({self.name!r}, {self.device_version}, {self.serial_number})"
        except:
            # The object is not yet fully initialized
            return f"CtapHidThalesDevice({self.name!r})"
    
  
    def _discovery(self) -> bool:
        """
            Discover product details like S/N, Applet version...
        """        
        # Send GETDATA to the applet. works only on FMW > 29.x.x
        resp = self.call_raw(0x50, b"\x00\x01\x66")
        if (resp[0] == 0x00):
            if( self.device_version[0] >= 29 ):
                self._fido_version = resp[2:].decode("utf-8").split('\x00', 1)[0]
            else:
                self._pki_version = resp[2:].decode("utf-8").split('\x00', 1)[0]

        resp = self.call_raw(0x50, b"\x00\x01\x55")

        if (resp[0] == 1):            
            logger.info("This product do not have an accessible S/N")
            return False
        
        if (resp[0] != 0) or (resp[1] != 0x02) or (sys.getsizeof(resp) < 10): 
            logger.error("Unable to get Thales Serial Number")
            return False
                
        self.serial_number = resp[2:]
        return True



    def call_raw(self, command, data) -> bytes:
        """ This method is used to send raw APDU to the device
            There is no equivalent in the mother class CtapHidDevice
        """
        
        packet = struct.pack(">IB", self._channel_id, 128 | command) + data
        self._connection.write_packet(packet.ljust(self._packet_size, b"\0"))
        recv = self._connection.read_packet()

        r_channel = struct.unpack_from(">I", recv)[0]
        if r_channel != self._channel_id:
            raise Exception("Wrong channel")
              
        return recv[7:]
    
    #def _do_call(self, command, data, event, on_keepalive):
    #    bytes = super()._do_call( command, data, event, on_keepalive)
    #    return bytes

    def disconnect(self) -> None:
        pass

    @classmethod
    def list_devices(cls, thales_only = True, serial_number = None) -> Iterator[CtapHidDevice]:
        for d in list_descriptors():
            dev = cls(d, open_connection(d))
            if( not thales_only ) or ( dev.is_thales_device and thales_only):
                if( not serial_number ) or ( dev.serial_number == serial_number):
                    yield dev
    