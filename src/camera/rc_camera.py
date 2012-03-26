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


import logging
from math import fabs

import cv

from ptz_camera.ptz_camera import PTZCamera
from simulator.panda3d.server.message_handler import *


BASIC_VP = 0
ADVANCED_VP = 1

RGB = 0
BGR = 1
RRRGGGBBB = 2
BGRA = 3

CHANNELS = 4
FREQ = 1

SPEED = 20.0 # degrees per second


class RCCamera(PTZCamera):

    def __init__(self, id, type, pos, up, dir):
        self.message_queue = []
        self.vp = None
        self.vp_type = None
        self.task = None
        self.type = type
        self.image_width = 640
        self.image_height = 480
        PTZCamera.__init__(self, id, type, pos, up, dir)


    def hasSession(self):
        """
        Returns True if the camera is linked to a VP Session, False otherwise.
        """
        return self.vp
        
        
    def getSessionId(self):
        """
        Returns the session id of the VP Session the camera is linked to.
        """
        return self.vp.conn_id


    def setSession(self, session, type, ip, port, task_info=None):
        """Sets the vp session that is linked to this camera"""
        self.vp = session
        self.vp_type = type
        self.ip = ip
        self.port = port
        conn_id = session.conn_id
        cam_id = self.id
        if type == ADVANCED_VP:
            logging.debug("VP on conn:%s linked to cam%s" %(conn_id, cam_id))
            # Request the vision processing client to start analysing the feed 
            # from this camera
            id = self.id
            width = self.image_width
            height = self.image_height
            jpeg = True
            message = eVV_REQ_VIDEO_ANALYSIS(ip, port, id, width, height, jpeg)
            self.vp.sendMessage(message)
            logging.debug("Sent VV_REQ_VIDEO_ANALYSIS message to conn:%s" 
                          % self.vp.conn_id)
            #self.task = Task(FREQ, width, height, jpeg)
            
        elif type == BASIC_VP:
            freq, width, height, jpeg = task_info
            #self.task = Task(freq, width, height, jpeg)


    def clearSession(self):
        """
        This method clears the vp session the camera was linked to. It stops
        any of the assigned tasks and reverts the camera back to its default
        position.
        """
        conn_id = self.vp.conn_id
        cam_id = self.id
        logging.debug("VP on conn:%s unlinked from cam%s" %(conn_id, cam_id))
        self.vp = None
        self.vp_type = None
        self.task = None
        if self.panda_camera:
            self.panda_camera.revertToDefault()
            self.panda_camera.setStatus("idle")


    def newMessage(self, message):
        """Adds a message to the cameras message queue."""
        message.decode_header()
        type = message.get_int()
        self.message_queue.append((type, message))


    def update(self, time):
        """
        This function is called at every time step to allow a camera to
        complete any tasks that it has to do. This includes processing messages
        as well as updating the camera parameters.
        """
        # Complete any tasks that need to be completed
        if self.task and not self.task.wait:
            if time > self.task.prev_time:
                self.task.counter += 1
                self.task.prev_time = time
            if self.task.frequency == self.task.counter:
                self.task.counter = 0
                self.completeTask(self.task, time)
        
        # Process messages received from other cameras
        while len(self.message_queue) > 0:
            type, message = self.message_queue.pop()
            self.processMessage(type, message)
        
        # Process messages received from the vp
        if self.vp:
            messages = self.vp.getMessages(self.id)
            for type, message in messages:
                self.processMessage(type, message)


    def processMessage(self, type, message):
        """
        This method processes any messages that are sent to a vp camera. The
        messages can come from either a vision processing module or a different
        camera.
        """
        conn_id = self.vp.conn_id
       
        if type == VP_CAM_IMAGE:
            self.sendFrame()
            logging.debug("Received VP_GET_IMAGE message from conn:%s" % conn_id)

        elif type == VP_CAM_RESOLUTION:
            self.image_width, self.image_height = dVP_CAM_RESOLUTION(message)
            logging.debug("Received VP_SET_RESOLUTION message from conn:%s" % conn_id)
            
      
    def sendFrame(self, time=None, task=None):

        frame = self.panda_camera.getFrameData(time)
        frm_time = frame['time']

        frm_w = frame['width']
        frm_h = frame['height']
        image_data = frame['data']

        if task:
            exp_w = task.width
            exp_h = task.height
            jpeg = task.jpeg

        else:
            exp_w = self.image_width
            exp_h = self.image_height
            jpeg = True

        # Resize image if the expected height and width are not met.
        if exp_w != frm_w or exp_h != frm_h:
            new_image = cv.CreateImage((exp_w, exp_h), cv.IPL_DEPTH_8U, 4)
            cv.Resize(image_data, new_image)
        
        else:
            new_image = image_data

        if jpeg:
            new_image = cv.EncodeImage('.jpg', new_image)
        
        image_string = new_image.tostring()
        message = eVV_IMG(self.ip, self.port, self.id, exp_w, exp_h, 
                          cv.IPL_DEPTH_8U, BGRA, jpeg, frm_time, image_string)
        self.vp.sendMessage(message)

        logging.debug("Sent VV_IMG message to conn:%s, frame_time: %s, jpeg:%s" 
                      % (self.vp.conn_id, frm_time, jpeg))


    def completeTask(self, task, time):
        """
        This method gets an image frame from the camera, resizes it and 
        compresses it if necessary and sends it to the assigned vision 
        processing module.
        """
        self.sendFrame(time, task)
        self.task.wait = False #This should be true if


    def isWaiting(self):
        """
        Returns True if the camera is waiting for a message from the client.
        Otherwise, it return False
        """
        if self.task:
            return self.task.wait
        
        else:
            return False


    def getTypeString(self):
        return "Static Camera"


class Task:
    """
    This class is used as a struct to store information about a tracking task.
    This includes:
        - how frequently images will be sent to the vision pipeline
        - the width and height of the image, 
        - a counter that keeps track of how many time steps have occured since
          the last image was sent. 
        - wether or not it should be compressed as a jpeg
        - wether it is waiting for tracking data from the vision pipeline
        - the last time an image was sent
    """
    def __init__(self, freq, width, height, jpeg):
        self.frequency = freq
        self.width = width
        self.height = height
        self.counter = 0
        self.jpeg = jpeg
        self.wait = False
        self.prev_time = -1


def buildCamera(config, type):
    id = config.id
    pos = config.position
    up = config.up_vector
    dir = config.default_direction
    camera_module = RCCamera(id, type, pos, up, dir)
    return camera_module
