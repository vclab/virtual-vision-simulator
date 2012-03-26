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


class PTZCamera:

    def __init__(self, id, type, pos, up, dir):
        self.panda_camera = None
        self.id = id
        self.position = pos
        self.up_vector = up
        self.direction = dir
        self.type = type
        
        
    def getId(self):
        return self.id
        
        
    def getType(self):
        return self.type

    
    def getTypeString(self):
        return "PTZ CAMERA"
        
        
    def setPandaCamera(self, camera):
        self.panda_camera = camera
        
    
    def setCameraManager(self, manager):
        self.camera_manager = manager
        
        
    def zoomIn(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.zoomIn(angle, time)
        
        
    def zoomOut(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.zoomOut(angle, time)
        
        
    def panLeft(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.panLeft(angle, time)
        
        
    def panRight(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.panRight(angle, time)
        
        
    def tiltUp(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.tiltUp(angle, time)
        
        
    def tiltDown(self, angle=10, time=1.0):
        if self.panda_camera:
            self.panda_camera.tiltDown(angle, time)
        
        
    def revertToDefault(self, time=1.0):
        if self.panda_camera:
            self.panda_camera.revertToDefault(time)


    def reset(self):
        if self.panda_camera:
            self.panda_camera.reset()


    def update(self, time):
        pass
        
        
    def getPosition(self):
        return self.position
        
    
    def getUpVector(self):
        return self.up_vector
        
        
    def getDirection(self):
        return self.direction

    
    def isWaiting(self):
        return False
        

def buildCamera(config, type):
    id = config.id
    pos = config.position
    up = config.up_vector
    dir = config.default_direction
    camera_module = PTZCamera(id, type, pos, up, dir)
    return camera_module

