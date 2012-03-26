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

from pandac.PandaModules import NetDatagram

from socket_packet import SocketPacket

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

CAM_SESSION = 300
CAM_TRACK_SIGNATURE = 301


def eVV_ACK_OK(ip, port, client_id):
    packet = SocketPacket()
    packet.add_int(VV_ACK_OK)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(client_id)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_CAM_LIST(ip, port, cam_list):
    packet = SocketPacket()
    packet.add_int(VV_CAM_LIST)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(len(cam_list))
    for cam in cam_list:
      packet.add_int(cam)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_IMG(ip, port, cam_id, width, height, depth, color_code, jpeg, timestamp,
            image_data):
    packet = SocketPacket()
    packet.add_int(VV_IMG)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(cam_id)
    packet.add_int(width)
    packet.add_int(height)
    packet.add_int(depth)
    packet.add_char(color_code)
    packet.add_bool(jpeg)
    packet.add_double(timestamp)
    packet.add_string(image_data)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_REQ_SIGNATURE(ip, port, object_id):
    packet = SocketPacket()
    packet.add_int(VV_REQ_SIGNATURE)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(object_id)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_TRACK_SIGNATURE(ip, port, object_id, feature_str, sig):
    packet = SocketPacket()
    packet.add_int(VV_TRACK_SIGNATURE)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(object_id)
    packet.add_string(feature_str)
    packet.add_int(len(sig))
    for element in sig:
        packet.add_float(element)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_REQ_VIDEO_ANALYSIS(ip, port, cam_id, width, height, jpeg):
    packet = SocketPacket()
    packet.add_int(VV_REQ_VIDEO_ANALYSIS)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(cam_id)
    packet.add_int(width)
    packet.add_int(height)
    packet.add_int(jpeg)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_SYNC_ACK(ip, port, vv_id):
    packet = SocketPacket()
    packet.add_int(VV_SYNC_ACK)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(vv_id)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_READY(ip, port, vv_id):
    packet = SocketPacket()
    packet.add_int(VV_READY)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(vv_id)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_CAM_MESSAGE(ip, port, cam_id, message):
    packet = SocketPacket()
    packet.add_int(VV_CAM_MESSAGE)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(cam_id)
    packet.add_packet(message)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_VP_ACK_OK(ip, port, cam_id):
    packet = SocketPacket()
    packet.add_int(VV_VP_ACK_OK)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(cam_id) ## Added this
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_VP_ACK_FAILED(ip, port):
    packet = SocketPacket()
    packet.add_int(VV_VP_ACK_FAILED)
    packet.add_string(ip)
    packet.add_int(port)
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def eVV_ADV_CAM_LIST(ip, port, cam_list):
    packet = SocketPacket()
    packet.add_int(VV_ADV_CAM_LIST)
    packet.add_string(ip)
    packet.add_int(port)
    packet.add_int(len(cam_list))
    for camera in cam_list:
        id = camera.getId()
        type = camera.getType()
        position = camera.getPosition()
        direction = camera.getDirection()
        packet.add_int(id)
        packet.add_int(type)
        packet.add_float(position[0])
        packet.add_float(position[1])
        packet.add_float(position[2])
        packet.add_float(direction[0])
        packet.add_float(direction[1])
        packet.add_float(direction[2])
    packet.encode_header()
    
    datagram = NetDatagram()
    datagram.appendData('' + packet.get_header() + packet.get_body())
    return datagram


def dVV_ADV_CAM_LIST(packet):
    num_cams = packet.get_int()
    cams = {}
    for i in range(num_cams):
        id = packet.get_int()
        type = packet.get_int()
        x = packet.get_float()
        y = packet.get_float()
        z = packet.get_float()
        position = (x,y,z)
        x = packet.get_float()
        y = packet.get_float()
        z = packet.get_float()
        direction = (x,y,z)
        cam = {'id':id, 'type':type, 'pos':position, 'dir':direction}
        cams[id] = cam
    return (cams)


def dVP_SESSION(packet):
    type = packet.get_char()
    pipeline = packet.get_char()
    return (type, pipeline)


def dVP_REQ_IMG(packet):
    cam_id = packet.get_int()
    freq = packet.get_char()
    width = packet.get_int()
    height = packet.get_int()
    jpeg = packet.get_bool()
    return (cam_id, freq, width, height, jpeg)


def dVP_TRACKING_DATA(packet):
    width = packet.get_int()
    height = packet.get_int()
    num_objects = packet.get_int()
    object_list = {}
    for i in range(num_objects):
        object_id = packet.get_int()
        x1 = packet.get_int()
        y1 = packet.get_int()
        x2 = packet.get_int()
        y2 = packet.get_int()
        object_list[object_id] = (x1, y1, x2, y2)

    return (width, height, object_list)


def dVP_SIGNATURE(packet):
    object_id = packet.get_int()
    feature_string = packet.get_string()
    sig_len = packet.get_int()
    sig_elements = []
    for i in range(sig_len):
        sig_elements.append(packet.get_float())
    return (object_id, feature_string, sig_len, sig_elements)


def dVP_CAM_PAN(packet):
    angle = packet.get_float()
    return (angle)


def dVP_CAM_TILT(packet):
    angle = packet.get_float()
    return (angle)


def dVP_CAM_ZOOM(packet):
    angle = packet.get_float()
    return (angle)


def dVP_CAM_DEFAULT(packet):
    pass


def dVP_CAM_RESOLUTION(packet):
    width = packet.get_int()
    height = packet.get_int()
    return ((width, height))


def dSYNC_SESSION(packet):
    vv_id = packet.get_int()
    return vv_id


def dSYNC_REMOTE_CAM_LIST(packet):
    num_cams = packet.get_int()

    cam_list = {}
    for i in range(num_cams):
        id = packet.get_int()
        type = packet.get_int()
        x = packet.get_float()
        y = packet.get_float()
        z = packet.get_float()
        position = (x,y,z)
        x = packet.get_float()
        y = packet.get_float()
        z = packet.get_float()
        direction = (x,y,z)
        cam = {'id':id, 'type':type, 'pos':position, 'dir':direction}
        cam_list[id] = cam
    return (cam_list)


def dSYNC_STEP(packet):
    increment = packet.get_float()
    return increment


def dSYNC_CAM_MESSAGE(packet):
    cam_id = packet.get_int()
    message = packet.get_packet()
    return (cam_id, message)


def eSYNC_SESSION(id, vv_id):
    packet = SocketPacket()
    packet.add_int(SYNC_SESSION)
    packet.add_int(id)
    packet.add_int(vv_id)
    packet.encode_header()
    return packet


def eSYNC_REQ_CAM_LIST(id):
    packet = SocketPacket()
    packet.add_int(SYNC_REQ_CAM_LIST)
    packet.add_int(id)
    packet.encode_header()
    return packet


def eSYNC_REMOTE_CAM_LIST(conn_id, cam_list):
    packet = SocketPacket()
    packet.add_int(SYNC_REMOTE_CAM_LIST)
    packet.add_int(conn_id)
    num_cams = len(cam_list)
    packet.add_int(num_cams)
    for camera in cam_list:
        cid = camera['id']
        type = camera['type']
        position = camera['pos']
        direction = camera['dir']
        packet.add_int(cid)
        packet.add_int(type)
        packet.add_float(position[0])
        packet.add_float(position[1])
        packet.add_float(position[2])
        packet.add_float(direction[0])
        packet.add_float(direction[1])
        packet.add_float(direction[2])
    packet.encode_header()
    
    return packet


def eSYNC_STEP(id, increment):
    packet = SocketPacket()
    packet.add_int(SYNC_STEP)
    packet.add_int(id)
    packet.add_float(increment)
    packet.encode_header()
    
    return packet


def eSYNC_CAM_MESSAGE(id, cam_id, message):
    packet = SocketPacket()
    packet.add_int(SYNC_CAM_MESSAGE)
    packet.add_int(id)
    packet.add_int(cam_id)
    packet.add_packet(message)
    packet.encode_header()
    
    return packet


def eCAM_TRACK_SIGNATURE(cid, oid, feature_str, elements):
    packet = SocketPacket()
    packet.add_int(CAM_TRACK_SIGNATURE)
    packet.add_int(cid)
    packet.add_int(oid)
    packet.add_string(feature_str)
    packet.add_int(len(elements))
    for element in elements:
        packet.add_float(element)
    packet.encode_header()
    
    return packet


def dCAM_TRACK_SIGNATURE(packet):
    cam_id = packet.get_int()
    obj_id = packet.get_int()
    feature_string = packet.get_string()
    sig_len = packet.get_int()
    elements = []
    for i in range(sig_len):
        elements.append(packet.get_float())
    return (cam_id, obj_id, feature_string, elements)


