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


import wx
import sys
import socket
import cv
import thread
import getopt
import logging

from pandac.PandaModules import NetDatagram
from simulator.panda3d.server.socket_packet import SocketPacket

SAVE_IMAGES = False

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

VP_SESSION = 100
VP_REQ_IMG = 101
VP_REQ_CAM_LIST = 102
VP_TRACKING_DATA = 103
VP_SIGNATURE = 104
VP_CAM_PAN = 105
VP_CAM_TILT = 106
VP_CAM_ZOOM = 107
VP_CAM_DEFAULT = 108
VP_CAM_IMAGE = 109
VP_CAM_RESOLUTION = 110

SYNC_SESSION = 200
SYNC_REQ_CAM_LIST = 201
SYNC_REMOTE_CAM_LIST = 202
SYNC_STEP = 203
SYNC_CAM_MESSAGE = 204

STATIC_PIPELINE = 0
ACTIVE_PIPELINE = 1

SESSION_TYPE = 1

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, ip_address, port, pipeline):
        wx.Frame.__init__(self, parent, id, title, size=(230, 360))

        panel = wx.Panel(self, -1)
        wx.Button(panel, 100, "Pan Left", (10,0), (100,30))
        wx.Button(panel, 101, "Pan Right", (120,0), (100,30))
        wx.Button(panel, 102, "Tilt Up", (10,40), (100,30))
        wx.Button(panel, 103, "Tilt Down", (120,40), (100,30))
        wx.Button(panel, 104, "Zoom In", (10,80), (100,30))
        wx.Button(panel, 105, "Zoom Out", (120,80), (100,30))
        wx.Button(panel, 106, "Default", (65,120), (100,30))
        wx.Button(panel, 107, "Get Image", (65, 160), (100, 30))

        wx.StaticBox(panel, -1, 'Image Resolution', (10, 200), size=(210, 150))
        wx.StaticText(panel, -1, 'Width:', (25, 235))
        self.width = wx.TextCtrl(panel, 108, "", (85, 225), (120, 30))
        wx.StaticText(panel, -1, 'Height:', (25, 270))
        self.height = wx.TextCtrl(panel, 109, "", (85, 260), (120, 30))
        wx.Button(panel, 110, "Set Resolution", (85, 300), (120, 30))

        try:
            logging.debug("Connecting to server with IP: %s and PORT: %s" 
                          %(ip_address, port))
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip_address, port))
            #self.client_socket.settimeout(3)
            self.client_socket.setblocking(0)

        except Exception as e:
            print "Error connecting to server!"
            sys.exit(0)

        self.read_buffer = ''
        self.write_buffer = ''
        self.read_state = 0
        self.packet = SocketPacket()
        self.connected = False
        self.x1 = 100
        self.x2 = 140
        self.count = 0
        self.pipeline = pipeline

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.step, self.timer)
        self.timer.Start(0.01 * 1000.0, oneShot=False)

        self.Bind(wx.EVT_BUTTON, self.pan, id=100)
        self.Bind(wx.EVT_BUTTON, self.pan, id=101)
        self.Bind(wx.EVT_BUTTON, self.tilt, id=102)
        self.Bind(wx.EVT_BUTTON, self.tilt, id=103)
        self.Bind(wx.EVT_BUTTON, self.zoom, id=104)
        self.Bind(wx.EVT_BUTTON, self.zoom, id=105)
        self.Bind(wx.EVT_BUTTON, self.default, id=106)
        self.Bind(wx.EVT_BUTTON, self.getImage, id=107)
        self.Bind(wx.EVT_BUTTON, self.setResolution, id=110)

     
    def step(self, event):
        self.reader_polling()
        self.write_polling()


    def write_packet(self, packet):
        self.write_buffer = self.write_buffer + packet.get_header() + packet.get_body()


    def write_polling(self):
        if self.write_buffer <> '':
            self.client_socket.send(self.write_buffer)
        self.write_buffer = ''
        return


    def reader_polling(self):
        data = ""
        try:
            data = self.client_socket.recv(1024)

        except socket.error, ex:
            pass

        if data != '':
            self.read_buffer = self.read_buffer + data

        while (True):
            if self.read_state == 0:
                if len(self.read_buffer) >= self.packet.header_length:
                    bytes_consumed = self.packet.header_length
                    self.packet.header = self.read_buffer[:bytes_consumed]
                    self.read_body_length = self.packet.decode_header()  # consumes packet.data
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
        return

    def setResolution(self, event):
        try:
            width = int(self.width.GetValue())
            height = int(self.height.GetValue())
            self.width.SetValue("")
            self.height.SetValue("")
        except Exception as e:
            logging.error("Resolution is not valid!")
        else:
            w = SocketPacket()
            w.add_int(VP_CAM_RESOLUTION)
            w.add_int(self.client_id)
            w.add_int(self.cam_id)
            w.add_int(width)
            w.add_int(height)
            w.encode_header()
            self.write_packet(w)


    def pan(self, event):
        id = event.GetEventObject().GetId()

        if id == 100:
            direction = -1

        else:
            direction = 1

        angle = direction * 10
        w = SocketPacket()
        w.add_int(VP_CAM_PAN)
        w.add_int(self.client_id)
        w.add_int(self.cam_id)
        w.add_float(angle)
        w.encode_header()
        self.write_packet(w)


    def tilt(self, event):
        id = event.GetEventObject().GetId()

        if id == 102:
            direction = 1

        else:
            direction = -1

        angle = direction * 10
        w = SocketPacket()
        w.add_int(VP_CAM_TILT)
        w.add_int(self.client_id)
        w.add_int(self.cam_id)
        w.add_float(angle)
        w.encode_header()
        self.write_packet(w)


    def zoom(self, event):
        id = event.GetEventObject().GetId()

        if id == 104:
            direction = -1

        else:
            direction = 1

        angle = direction * 10
        w = SocketPacket()
        w.add_int(VP_CAM_ZOOM)
        w.add_int(self.client_id)
        w.add_int(self.cam_id)
        w.add_float(angle)
        w.encode_header()
        self.write_packet(w)


    def default(self, event):
        w = SocketPacket()
        w.add_int(VP_CAM_DEFAULT)
        w.add_int(self.client_id)
        w.add_int(self.cam_id)
        w.encode_header()
        self.write_packet(w)


    def getImage(self, event):
        w = SocketPacket()
        w.add_int(VP_CAM_IMAGE)
        w.add_int(self.client_id)
        w.add_int(self.cam_id)
        w.encode_header()
        self.write_packet(w)


    def new_data_callback(self, packet):
        message_type = packet.get_int()
        if message_type == VV_ACK_OK:
          server_ip = packet.get_string()
          server_port = packet.get_int()
          self.client_id = packet.get_int()
          logging.info("Connection Established.")

          w = SocketPacket()
          w.add_int(VP_SESSION)
          w.add_int(self.client_id)
          w.add_char(SESSION_TYPE)
          w.add_char(self.pipeline)
          w.encode_header()
          self.write_packet(w)


        elif message_type == VV_VP_ACK_OK:
          packet.get_string()
          packet.get_int()
          self.cam_id = packet.get_int()
          self.connected = True


        elif message_type == VV_REQ_VIDEO_ANALYSIS:
            logging.debug("VV_REQ_VIDEO_ANALYSIS")
            ip = packet.get_string()
            port = packet.get_int()
            self.camera_id = packet.get_int()
            self.SetTitle("Camera %s Controller" % self.camera_id)


        elif message_type == VV_IMG:
            logging.debug("NEW IMAGE")
            server_ip = packet.get_string()
            server_port = packet.get_int()
            cam_id = packet.get_int()
            width = packet.get_int()
            height = packet.get_int()
            depth = packet.get_int()
            color_code = packet.get_char()
            jpeg =  packet.get_bool()
            time = packet.get_double()
            image = packet.get_string()

            cv_im = self.createImage(image, width, height, depth, color_code, jpeg)

            self.camera_id = cam_id
            cv.ShowImage("Image", cv_im)
            if SAVE_IMAGES:
                cv.SaveImage("cam%s_%s.jpg" % (cam_id, self.count), cv_im)
                self.count+=1
            cv.WaitKey()


    def createImage(self, image_data, width, height, depth, color_code, jpeg=False):
        if jpeg:
            length = len(image_data)
            image = cv.CreateMatHeader(1, length, cv.CV_8UC1)
            cv.SetData(image, image_data, length)
            return cv.DecodeImage(image)
        else:
            image = cv.CreateImageHeader((width, height), depth, 4)
            cv.SetData(image, image_data)


def usage():
    print ""
    print "USAGE: python sample_client.py [options]"
    print "Options:"
    print "- p port\t: Set the port of the virtual world"
    print "- a ip_address\t: Set the ip address of the virtual world"
    print "- s\t\t: Save the images received from the server"
    print "- h \t\t: Print this help message and exit"
    print "--debug\t\t: Show debug messages"
    print ""


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:hs", ["debug", "address=", "port=" "static"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    debug = False
    ip_address = IP
    port = PORT
    pipeline = ACTIVE_PIPELINE
    for o, a in opts:

        if o in ("--debug"):
            debug = True
        
        elif o in ("-a", "--address"):
            ip_address = a
        
        elif o in ("-p", "--port"):
            port = int(a)

        elif o in ("-h"):
            usage()
            sys.exit(0)

        elif o in ("-s"):
            SAVE_IMAGES = True

        elif o in ("--static"):
            pipeline = STATIC_PIPELINE


    format_str = '%(levelname)s: %(message)s'
    if debug:
        logging.basicConfig(format=format_str, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format_str, level=logging.INFO)

    app = wx.App()
    frame = MyFrame(None, -1, 'Sample Client', ip_address, port, pipeline)
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main()
