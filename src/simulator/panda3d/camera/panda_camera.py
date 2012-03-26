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


from math import atan2, sqrt, degrees

from panda3d.core import Material
from pandac.PandaModules import VBase4, VBase3

import numpy as np
import cv

from ..panda3d_helper import *

class PandaCamera:

    def __init__(self, buffer, camera, camera_model):
    
        self.camera_np = camera
        self.lens = camera.node().getLens()
        self.buffer = buffer
        self.camera_model = camera_model
        
        self.frame_data = {"time": -1.0}
    
        self.color = (255, 255, 255)
        self.id = -1
        self.name = "cam00"
        self.pos = np.array([0, 0, 0])
        self.up = np.array([0, 1, 0])
        self.near_plane = 1
        self.far_plane = 100000
        
        self.fov_limits = [20, 90]
        self.pan_limits = [-30, 30]
        self.tilt_limits = [-30, 30]
        
        self.default_fov = self.fov = 90
        self.default_pan = self.pan = 0
        self.default_tilt = self.tilt = 0
        self.default_direction = self.direction = np.array([1, 0, 0])
        
        self.default_yaw = 0
        self.default_pitch = 0
        
        self.asprect_ratio = 1.0
        self.width = 640
        self.height = 480
        
        self.status = ""
        self.status_changed = False

        self.cur_time = 0
    
    
    def getCameraNode(self):
        """Get the node of the camera in the panda3d scene graph"""
        return self.camera_np
        
        
    def getBuffer(self):
        """Get the buffer where the rendered image is stored"""
        return self.buffer
        
        
    def getName(self):
        """Return the name of the camera based on its id"""
        return self.name
        
        
    def setColor(self, color):
        """Set the color of the camera"""
        self.color = color
        r, g, b = color
        self.camera_model.setColorScale(r/255.0, g/255.0, b/255.0, 1.0)
        
        
    def getColor(self):
        """Returns the color of the camera"""
        return self.color
        
        
    def setId(self, id):
        """
        Set the id of the camera.
        NOTE: The name of the camera is based on its id.
        """
    
        self.id = id
        self.name = "cam%s" % id
        
        
    def getId(self):
        """Get the id of the camera"""
        return self.id
        
        
    def setPos(self, pos):
        """Set the position of the camera"""
        self.pos = pos
        self.camera_np.setPos(*ToPandaCoordinates(VBase3(*pos)))
        self.camera_model.setPos(*ToPandaCoordinates(VBase3(*pos)))
        
        
    def getPos(self):
        """Returns the position of the camera"""
        return self.pos
        
        
    def setDefaultDirection(self, direction):
        """
        Sets the direction of the camera when in its default position.
        NOTE: The pan and tilt values are based off of the default direction
        """
        self.default_direction = direction
        yaw, pitch = VectorToHpr(direction)
        self.default_yaw = yaw
        self.default_pitch = pitch
        self.camera_np.setHpr(yaw, pitch, 0)
        self.camera_model.setHpr(yaw, pitch, 0)
        
        
    def getDefaultDirection(self):
        """
        Returns the direction of the camera when its it default position.
        """
        return self.default_direction
        
        
    def setUp(self, up_vector):
        """Sets the up vector of the camera"""
        self.up = up_vector
        
        
    def getUp(self):
        """Returns the up vector of the camera"""
        return self.up
        
    
    def setNear(self, near):
        """Sets the near plane of the camera"""
        self.near = near
        self.lens.setNear(near)
        
        
    def getNear(self):
        """Returns the near plane of the camera"""
        return self.near
        
    
    def setFar(self, far):
        """Sets the far plane of the camera"""
        self.far = far
        self.lens.setFar(far)
        
        
    def getFar(self):
        """Returns the far plane of the camera"""
        return self.far
        
        
    def setFov(self, fov):
        """Sets the current field of view of the camera"""
        min, max = self.fov_limits
        if fov <= min:
            new_fov = min
        elif fov >= max:
            new_fov = max
        else:
            new_fov = fov
            
        self.fov = new_fov
        self.lens.setFov(new_fov)
        
        
    def getFov(self):
        """Returns the current field of view"""
        return self.fov
        
        
    def setDefaultFov(self, fov):
        """Sets the fov for when the camera is in its default position"""
        self.default_fov = fov
        
        
    def getDefaultFov(self):
        """Returns the fov when the camera is in its default position."""
        return self.default_fov
        
        
    def setPan(self, pan):
        """Sets the pan value of the camera"""
        min, max = self.pan_limits
        if pan <= min:
            new_pan = min
        elif pan >= max:
            new_pan = max
        else:
            new_pan = pan
        self.pan = new_pan
        self.camera_np.setH(self.default_yaw - new_pan)
        self.camera_model.setH(self.default_yaw - new_pan)
        
        
    def getPan(self):
        """Return the current pan value"""
        return self.pan
        
    
    def setTilt(self, tilt):
        """Set the tilt value of the camera"""
        min, max = self.tilt_limits
        if tilt <= min:
            new_tilt = min
        elif tilt >= max:
            new_tilt = max
        else:
            new_tilt = tilt
            
        self.tilt = new_tilt
        self.camera_np.setP(self.default_pitch + new_tilt)
        self.camera_model.setP(self.default_pitch + new_tilt)
        
        
    def getTilt(self):
        """Returns the current tilt value"""
        return self.tilt
        
        
    def setFovLimits(self, min, max):
        """Sets the min and max field of views of the camera."""
        self.fov_limits = (min, max)
        
        
    def getFovLimits(self):
        """
        Returns the fov limits of the camera as a tuple if the min and max
        field of views.
        """
        return self.fov_limits
        
    
    def setPanLimits(self, min, max):
        """Sets the min and max pan values of the camera"""
        self.pan_limits = (min, max)
        
        
    def getPanLimits(self):
        """
        Returns the pan limits as a tupple containing the min and max pan 
        values.
        """
        return self.pan_limits
        
        
    def setTiltLimits(self, min, max):
        """Sets the min and max tilt values of the camera."""
        self.tilt_limits = (min, max)
        
        
    def getTiltLimits(self):
        """
        Returns the tilt limits as a tupple containing the min and max tilt 
        values
        """
        return self.tilt_limits
    
    
    def setImageSize(self, width, height):
        """Sets the width and height the rendered image will be"""
        self.width = width
        self.height = height
    
    
    def setAspectRatio(self, ap):
        """Sets the aspect ratio of the camera"""
        self.aspect_ratio = ap
        self.lens.setAspectRatio(ap)
        
        
    def getAspectRatio(self):
        """Returns the aspect ration of the camera"""
        return self.aspect_ratio
        
        
    def statusChanged(self):
        """
        A flag thats keeps track of whether the status of the camera has 
        changed.
        """
        return self.status_changed
        
        
    def setStatus(self, string):
        """
        Sets the status of this camera.
        """
        self.status = string
        self.status_changed = True
        
        
    def getStatusLabel(self):
        """
        Returns the status label of this camera.
        """
        self.status_changed = False
        return self.status
        
        
    def getFrameData(self, time=None):
        """
        Returns an image frame rendered using this camera. The image frame is
        made up of a dictionary containing the 'width', 'height', 'data', and
        'time' values.
        """
        if time and self.frame_data['time'] == time:
            return self.frame_data
            
        texture = self.buffer.getTexture()
        image = texture.getRamImage()#As('BGRA')
        image_string = image.getData()
        width = self.width
        height = self.height
        cv_im = cv.CreateImageHeader((width, height), cv.IPL_DEPTH_8U, 4)
        cv.SetData(cv_im, image_string)
        cv.Flip(cv_im, None, 0)
        self.frame_data = {"width":width, "height":height, "data":cv_im, 
                           "time":self.cur_time}
        return self.frame_data



