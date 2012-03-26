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
sys.path.append(os.path.join(os.getcwd(), '..' ))

import socket
import atexit
import logging
import copy

from direct.task import Task
from pandac.PandaModules import QueuedConnectionManager
from pandac.PandaModules import QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader
from pandac.PandaModules import ConnectionWriter
from pandac.PandaModules import NetDatagram
from pandac.PandaModules import NetAddress 
from pandac.PandaModules import PointerToConnection
from direct.gui.OnscreenText import OnscreenText as OST
from pandac.PandaModules import TextNode

from socket_packet import SocketPacket
from message_handler import *
from vp_session import VPSession
from sync_session import SyncSession
from sync import Sync
from camera.camera_builder import ACTIVE_CAMERA, STATIC_CAMERA

BACKLOG = 1000

STATIC_PIPELINE = 0
PTZ_PIPELINE = 1

VP = 1
SYNC = 2

VP_BASIC = 0
VP_ADVANCED = 1

PIPELINE = {STATIC_PIPELINE:"static", PTZ_PIPELINE:"active"}
VP_TYPE = {VP_BASIC:"basic", VP_ADVANCED:"advanced"}

class SocketServer():

    def __init__(self, port, virtual_world, camera_mgr, sync_session):
        self.port = port
        self.virtual_world = virtual_world
        self.cam_mgr = camera_mgr
        
        self.task_mgr = virtual_world.taskMgr
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cReader.setRawMode(True)
        self.cWriter = ConnectionWriter(self.cManager, 1)
        self.cWriter.setRawMode(True)
        self.tcpSocket = self.cManager.openTCPServerRendezvous(port, BACKLOG)
        self.cListener.addConnection(self.tcpSocket)
        
        self.activeSessions = {}
        self.connection_map = {}
        self.set_handlers()
        
        hostname = socket.gethostname()
        a, b, address_list = socket.gethostbyname_ex(hostname)
        self.ip = address_list[0]
        logging.info("Addresses %s" % address_list)
        logging.info("Server is running on ip: %s, port: %s" 
                     %(self.ip, self.port))
        
        self.client_counter = 0
        self.read_buffer = ''
        self.read_state = 0
        self.read_body_length = 0
        self.packet = SocketPacket()
        
        controller = virtual_world.getController()
        self.sync = Sync(self.task_mgr, controller, camera_mgr, sync_session)
        self.vv_id = None
        if sync_session:
            logging.info("Waiting for Sync Client!")
        
        self.showing_info = False
        virtual_world.accept("i", self.toggleInfo)
        self.sync_session = sync_session
        self.createInfoLabel()

        atexit.register(self.exit)


    def createInfoLabel(self):

        string = self.generateInfoString()
        self.info_label = OST(string, 
                              pos=(-1.3, -0.5), 
                              fg=(1,1,1,1), 
                              bg=(0,0,0,0.7),
                              scale=0.05, 
                              align=TextNode.ALeft)
        self.info_label.hide()
    
    def generateInfoString(self,):
        string = " IP:\t%s  \n" % self.ip
        string += " PORT:\t%s \n" % self.port
        if self.sync_session:
            string += " MODE:\tSync Client\n"
            string += " VV ID:\t%s\n" % self.vv_id
        else:
            string += " MODE:\tAutomatic\n"
          
        cameras = self.cam_mgr.getCameras()
        num_cameras = len(cameras)

        for camera in cameras:
            id = camera.getId()
            type = camera.getTypeString()
            string += " Cam%s:\t%s\n" %(id, type)
        string += "\n"
        return string
    
    
    def set_handlers(self):
        self.task_mgr.add(self.connection_polling, "Poll new connections", -39)
        self.task_mgr.add(self.reader_polling, "Poll reader", -40)
        self.task_mgr.add(self.disconnection_polling, "PollDisconnections", -41)


    def connection_polling(self, taskdata):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConn = PointerToConnection()
            if self.cListener.getNewConnection(rendezvous,netAddress, newConn):
                conn = newConn.p()
                self.cReader.addConnection(conn)     # Begin reading connection
                conn_id = self.client_counter
                logging.info("New Connection from ip:%s, conn:%s"
                             % (conn.getAddress(), conn_id))
                self.connection_map[conn_id] = conn
                self.client_counter += 1
                message = eVV_ACK_OK(self.ip, self.port, conn_id)
                self.sendMessage(message, conn)

        return Task.cont


    def reader_polling(self, taskdata):

        if self.cReader.dataAvailable():
            datagram = NetDatagram()  # catch the incoming data in this instance
            # Check the return value; if we were threaded, someone else could have
            # snagged this data before we did
            if self.cReader.getData(datagram):
                self.read_buffer = self.read_buffer + datagram.getMessage()
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
                    self.new_data_callback(self.packet)

                else:
                    break
        return Task.cont


    def new_data_callback(self, packet):
        packet = copy.deepcopy(packet)
        message_type = packet.get_int()
        conn_id = packet.get_int()
        if message_type == VP_SESSION:
            conn = self.connection_map[conn_id]
            type = packet.get_char()
            pipeline = packet.get_char()
            logging.debug("Received VP_SESSION message from conn:%s, " \
                          "type=%s, pipeline=%s" 
                          %(conn_id, VP_TYPE[type], PIPELINE[pipeline]))
            self.newVPSession(conn, type, pipeline, conn_id)

        elif message_type == SYNC_SESSION:
            vv_id = packet.get_int()
            self.vv_id = vv_id
            string = self.generateInfoString()
            self.info_label.setText(string)
            conn = self.connection_map[conn_id]
            logging.debug("Received SYNC_SESSION message from conn:%s" %conn_id)
            self.newSyncSession(conn, conn_id, vv_id)
            logging.info("Sync client connected")
            
        elif message_type == VP_REQ_CAM_LIST:
            logging.debug("Received VP_REQ_CAM_LIST message from conn:%s" 
                          % conn_id) 
            cameras = self.cam_mgr.getCameras()
            pipeline = self.activeSessions[conn_id].getPipeline()
            camera_type = None
            if pipeline == STATIC_PIPELINE:
                camera_type = VP_STATIC_CAMERA
            elif pipeline == PTZ_PIPELINE:
                camera_type = VP_ACTIVE_CAMERA
            cam_list = []
            for camera in cameras:
                if camera_type == camera.getType() and not camera.hasSession():
                    cam_list.append(camera.getId())
            message = eVV_CAM_LIST(self.ip, self.port, cam_list)
            conn = self.connection_map[conn_id]
            logging.debug("Sent VV_CAM_LIST message to conn:%s" % conn_id)
            self.sendMessage(message, conn)

        elif message_type == VP_REQ_IMG:
            cam_id = packet.get_int()
            frequency = packet.get_char()
            width = packet.get_int()
            height = packet.get_int()
            jpeg = packet.get_bool()
            data = (frequency, width, height, jpeg)
            camera = self.cam_mgr.getCameraById(cam_id)
            logging.debug("Received VV_REQ_IMG message from conn:%s" % conn_id)
            if camera and not camera.hasSession():
                session = self.activeSessions[conn_id]
                session.addCamera(cam_id)
                camera.setSession(session, VP_BASIC, self.ip, self.port, data)
            
        else:
            if conn_id in self.activeSessions:
                self.activeSessions[conn_id].newMessage(message_type, packet)


    def newVPSession(self, conn, type, pipeline, conn_id):

        if type == VP_ADVANCED:
            camera_type = -1
            if pipeline == STATIC_PIPELINE:
                camera_type = STATIC_CAMERA ## Change this to use a different static camera class
            elif pipeline == PTZ_PIPELINE:
                camera_type = ACTIVE_CAMERA
            if camera_type != -1:
                cam = self.cam_mgr.getAvailableCamera(camera_type)
                if cam:
                    session = VPSession(conn_id, conn, self, VP, pipeline)
                    session.addCamera(cam.getId())
                    self.activeSessions[conn_id] = session
                    message = eVV_VP_ACK_OK(self.ip, self.port, cam.getId())
                    logging.debug("Sent VV_VP_ACK_OK message to conn:%s" 
                                  % conn_id)
                    self.sendMessage(message, conn)
                    cam.setSession(session, type, self.ip, self.port)
                    
                else:
                    message = eVV_VP_ACK_FAILED(self.ip, self.port)
                    logging.debug("Sent VV_VP_ACK_FAILED message to conn:%s" 
                                  % conn_id)
                    self.sendMessage(message, conn)
        else:
            message = eVV_VP_ACK_FAILED(self.ip, self.port)
            logging.debug("Sent VV_VP_ACK_FAILED message to conn:%s" 
                          % conn_id)
            self.sendMessage(message, conn)


    def newSyncSession(self, conn, conn_id, vv_id):
        session = SyncSession(conn_id, conn, self, SYNC)
        self.sync.setSession(session, vv_id, self.ip, self.port)
        self.activeSessions[conn_id] = session
        message = eVV_SYNC_ACK(self.ip, self.port, vv_id)
        logging.debug("Sent VV_SYNC_ACK message to conn:%s" % conn_id)
        self.sendMessage(message, conn)


    def sendMessage(self, message, conn):
        self.cWriter.send(message, conn)


    def disconnection_polling(self, taskdata):
        if(self.cManager.resetConnectionAvailable()):
            connectionPointer = PointerToConnection()
            self.cManager.getResetConnection(connectionPointer)
            lostConnection = connectionPointer.p()
            for session in self.activeSessions.values():
                if session.conn == lostConnection:
                    logging.info("Lost Connection from ip:%s, conn:%s" 
                                 %(session.client_address, session.conn_id))
                    conn_id = session.conn_id
                    if session.getSessionType() == VP:
                        cameras = session.getCameras()
                        for cam_id in cameras:
                            camera = self.cam_mgr.getCameraById(cam_id)
                            camera.clearSession()
                      
                    del self.activeSessions[conn_id]
                    del self.connection_map[conn_id]
                    break
            self.cManager.closeConnection(lostConnection)
        return Task.cont
    

    def toggleInfo(self):
        if self.showing_info:
            self.info_label.hide()
            self.showing_info = False
        else:
            self.info_label.show()
            self.showing_info = True


    def exit(self):
        for connection in self.connection_map.values():
            self.cReader.removeConnection(connection)
        self.cManager.closeConnection(self.tcpSocket)
        self.tcpSocket.getSocket().Close()

