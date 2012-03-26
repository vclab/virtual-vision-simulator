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


import sys, os
import time
import socket
import logging


from pandac.PandaModules import NetDatagram
from simulator.panda3d.server.socket_packet import SocketPacket
from simulator.panda3d.server.message_handler import (eSYNC_SESSION,
                                                      eSYNC_REQ_CAM_LIST, 
                                                      eSYNC_STEP,
                                                      eSYNC_REMOTE_CAM_LIST,
                                                      eSYNC_CAM_MESSAGE,
                                                      dVV_ADV_CAM_LIST)

from sync_session import SyncSession

IP = 'localhost'
PORT = 9099

#Message Types
VV_ACK_OK = 0
VV_CAM_LIST = 1
VV_IMG = 2
VV_REQ_SIGNATURE = 3
VV_TRACK_SIGNATURE = 4
VV_REQ_VIDEO_ANALYSIS = 5
VV_SYNC_ACK = 6
VV_READY = 7
VV_CAM_MESSAGE = 8
VV_VP_ACK_OK = 9
VV_VP_ACK_FAILED = 10
VV_ADV_CAM_LIST = 11

SYNC_SESSION = 200
SYNC_REQ_CAM_LIST = 201
SYNC_REMOTE_CAM_LIST = 202
SYNC_STEP = 203
SYNC_CAM_MESSAGE = 204

STATIC_CAMERA = 0
ACTIVE_CAMERA = 1

CAMERAS_TO_STRING = {STATIC_CAMERA: "STATIC CAMERA", ACTIVE_CAMERA: "ACTIVE CAMERA"}

class SyncClient():

    def __init__(self, server_list):
      
      self.vv_map = {}
      self.num_vvs = 0
      self.vv_ready = []
      for server in server_list:
          ip, port = server
          self.num_vvs += 1
          session = SyncSession(self, ip, port, self.num_vvs)
          self.vv_map[self.num_vvs] = session
          logging.info("VV%s ip:%s, port:%s" %(self.num_vvs, ip, port))
          
      logging.info("Total VVs: %s" % self.num_vvs)
      

    def run(self):
        try:
            while 1:
                for session in self.vv_map.values():
                    session.update()
                
                if len(self.vv_ready) == self.num_vvs:
#                    time.sleep(1)
                    self.vv_ready = []
                    for session in self.vv_map.values():
                        message = eSYNC_STEP(session.conn_id, 0.033)
                        session.sendMessage(message)
                        logging.debug("Sent SYNC_STEP message to conn:%s" %
                                      session.vv_id)
        except KeyboardInterrupt as e:
            pass


    def newMessage(self, packet, sid):
        message_type = packet.get_int()
        if message_type == VV_ACK_OK:
            logging.debug("Received VV_ACK_OK message from conn:%s" % sid)
            ip = packet.get_string()
            port = packet.get_int()
            conn_id = packet.get_int()
            self.vv_map[sid].conn_id = conn_id
            message = eSYNC_SESSION(conn_id, sid)
            self.vv_map[sid].sendMessage(message)
            logging.debug("Sent SYNC_SESSION message to conn:%s" % sid)

        elif message_type == VV_SYNC_ACK:
            ip = packet.get_string()
            port = packet.get_int()
            vv_id = packet.get_int()
            if vv_id != sid:
                logging.warning("vv_id does not match session_id!")
            # Request a list of cameras from the vv
            conn_id = self.vv_map[sid].conn_id
            message = eSYNC_REQ_CAM_LIST(conn_id)
            self.vv_map[sid].sendMessage(message)

        elif message_type == VV_ADV_CAM_LIST:
            logging.debug("Received VV_CAM_LIST message from conn:%s" % sid)
            ip = packet.get_string()
            port = packet.get_int()
            cameras = dVV_ADV_CAM_LIST(packet)
            self.vv_map[sid].setCameras(cameras)
            conn_id = self.vv_map[sid].conn_id
            logging.info("Received cameras from VV%s" % sid)
            for camera in cameras.values():
                id = camera['id']
                type = CAMERAS_TO_STRING[camera['type']]
                logging.info("Cam%s %s" % (id, type))
            
            if self.num_vvs > 1:
                cam_list = cameras.values()
                for vv_id, vv in self.vv_map.items():
                    if vv_id != sid:
                        message = eSYNC_REMOTE_CAM_LIST(conn_id, cam_list)
                        self.vv_map[vv_id].sendMessage(message)
                        logging.debug("Sent SYNC_REMOTE_CAM_LIST message " \
                                       "to conn:%s" % sid)
                
        elif message_type == VV_READY:
            logging.debug("Received VV_READY message from conn:%s" % sid)
            ip = packet.get_string()
            port = packet.get_int()
            vv_id = packet.get_int()
            self.vv_ready.append(vv_id)

        elif message_type == VV_CAM_MESSAGE:
            logging.info("Received VV_CAM_MESSAGE message from conn:%s" % sid)
            ip = packet.get_string()
            port = packet.get_int()
            cam_id = packet.get_int()
            cam_message = packet.get_packet()
            conn_id = self.vv_map[sid].conn_id
            for session in self.vv_map.values():
                if session.hasCamera(cam_id):
                    message = eSYNC_CAM_MESSAGE(conn_id, cam_id, cam_message)
                    session.sendMessage(message)
                    logging.info("Sent SYNC_CAM_MESSAGE message " \
                                     "to conn:%s" % session.conn_id)
