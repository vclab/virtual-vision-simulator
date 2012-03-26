#!/usr/bin/env python
#
# Copyright (c) 2011-2012 Wiktor Starzyk, Faisal Z. Qureshi
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


import sys
import socket
import logging

from pandac.PandaModules import NetDatagram
from simulator.panda3d.server.socket_packet import SocketPacket

class SyncSession:

    def __init__(self, parent, ip , port, vv_id):
        self.parent = parent
        self.ip = ip
        self.port = port
        self.vv_id = vv_id
        self.conn_id = None
        self.cameras = []
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.socket.setblocking(0)
        except Exception as e:
            logging.error("Error connecting to server!")
            logging.error(e)
            sys.exit()
          
        self.read_buffer = ''
        self.write_buffer = ''
        self.read_state = 0
        self.packet = SocketPacket()


    def setCameras(self, cameras):
        self.cameras = cameras


    def hasCamera(self, cam_id):
        return cam_id in self.cameras


    def update(self):
        self.reader_polling()
        self.write_polling()


    def sendMessage(self, packet):
        self.write_buffer = self.write_buffer + packet.get_header() + packet.get_body()


    def write_polling(self):
        if self.write_buffer != '':
            self.socket.send(self.write_buffer)
        self.write_buffer = ''
        return


    def reader_polling(self):
        try:
            data = self.socket.recv(1024)
        except socket.error, ex:
            (error_number, error_message) = ex
            if error_number == 104:
                logging.error("VV%s unreachable!" % self.vv_id)
                sys.exit()
            data = ""

        if data != '':
            self.read_buffer = self.read_buffer + data
        while (True):
            if self.read_state == 0:
                if len(self.read_buffer) >= self.packet.header_length:
                    bytes_consumed = self.packet.header_length
                    self.packet.header = self.read_buffer[:bytes_consumed]
                    self.read_body_length = self.packet.decode_header()  
                    self.read_buffer = self.read_buffer[bytes_consumed:]
                    self.read_state = 1
                else:
                    break

            if self.read_state == 1:
                if len(self.read_buffer) >= self.read_body_length:
                    bytes_consumed = self.read_body_length
                    self.packet.data = self.read_buffer[:bytes_consumed]
                    self.packet.offset = 0
                    self.read_body_length = 0
                    self.read_buffer = self.read_buffer[bytes_consumed:]
                    self.read_state = 0
                    self.parent.newMessage(self.packet, self.vv_id)
                else:
                    break
                    

