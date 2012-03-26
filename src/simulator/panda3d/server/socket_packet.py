#!/usr/bin/env python
#
# Copyright (c) 2011-2012 Faisal Z. Qureshi, Wiktor Starzyk
#
# This file is part of the Virtual Vision Simulator.
#
# The Virtual Vision Simulator is free software: you can 
# redistribute it and/or modify it under the terms 
# of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
#
# The Virtual Vision Simulator is distributed in the hope 
# that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Virtual Vision Simulator.  
# If not, see <http://www.gnu.org/licenses/>.
#


from struct import pack, calcsize
from struct import unpack, unpack_from
import logging

class SocketPacket():


    def __init__(self, header='', data='', header_length=4, offset=0):
        self.header = header
        self.data = data
        self.header_length = header_length
        self.offset = offset


    def get_header(self):
        return self.header


    def get_body(self):
        return self.data


    # adding data to construct a socket_packet for sending
    # over the network
    def add_data(self, data):
        self.data += data
        self.offset += len(data)
    
    
    def add_bool(self, v):
        fmt = "!?"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)


    def add_int(self, v):
        fmt = "!i"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)
#        print "Size of int", calcsize(fmt)


    def add_uint(self, v):
        fmt = "!I"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)

   
    def add_long(self, v):
        fmt = "!l"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)


    def add_float(self, v):
        fmt = "!f"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)


    def add_double(self, v):
        fmt = "!d"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)


    def add_string(self, str):
        nbytes = len(str)
        self.add_int(nbytes)
        self.add_data(str)


    def add_char(self, v):
        fmt = "!B"
        self.data += pack(fmt, v)
        self.offset += calcsize(fmt)
        
    def add_packet(self, packet):
        self.add_string(packet.data)
        self.add_int(packet.offset)
        self.add_string(packet.header)
        self.add_int(packet.header_length)


    def encode_header(self): # should be the last call before you send it on
        fmt = "!l"
        if len(self.data) == 0:
            logging.warning("Empty Packet")
        self.header = pack(fmt, len(self.data))


    # reading data items from a socket packet (typically) received 
    # over the network. this reading process is destructive.
    # decode_header must be called before attempting to read data.
    def decode_header(self):
        fmt = "!i"
        v = unpack(fmt, self.header)
        self.offset = 0
        if v[0] == 0:
            logging.warning("Received empty packet")
            
        return v[0]


    def get_bool(self):
        fmt = "!?"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_int(self):
        fmt = "!i"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_uint(self):
        fmt = "!I"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_long(self):
        fmt = "!l"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_float(self):
        fmt = "!f"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_double(self):
        fmt = "!d"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_char(self):
        fmt = "!B"
        v = unpack_from(fmt, self.data, self.offset)
        self.offset += calcsize(fmt)
        return v[0]


    def get_string(self):
        nbytes = self.get_int()
        i = self.offset
        self.offset += nbytes
        return self.data[i:self.offset]


    def get_packet(self):
        data = self.get_string()
        offset = self.get_int()
        header = self.get_string()
        header_length = self.get_int()
        self.offset = offset
        return SocketPacket(header, data, header_length, offset)

