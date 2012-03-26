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


from panda_camera import PandaCamera

from motor import *

class PandaPTZCamera(PandaCamera):

    def __init__(self, buffer, camera, camera_model):
        PandaCamera.__init__(self, buffer, camera, camera_model)
        self.zoom_motor = Motor(self, "setFov")
        self.pan_motor = Motor(self, "setPan")
        self.tilt_motor = Motor(self, "setTilt")
        self.reset()
        
    def zoomIn(self, angle=10, time=1.0):
        current = self.getFov()
        new = current - angle
        self.zoom_motor.newValue(current, new, time)
        
        
    def zoomOut(self, angle=10, time=1.0):
        current = self.getFov()
        new = current + angle
        self.zoom_motor.newValue(current, new, time)
        
        
    def panLeft(self, angle=10, time=1.0):
        current = self.getPan()
        new = current - angle
        self.pan_motor.newValue(current, new, time)
        
        
    def panRight(self, angle=10, time=1.0):
        current = self.getPan()
        new = current + angle
        self.pan_motor.newValue(current, new, time)
        
        
    def tiltUp(self, angle=10, time=1.0):
        current = self.getTilt()
        new = current + angle
        self.tilt_motor.newValue(current, new, time)
        
        
    def tiltDown(self, angle=10, time=1.0):
        current = self.getTilt()
        new = current - angle
        self.tilt_motor.newValue(current, new, time)
        
        
    def revertToDefault(self, time=1.0):
        fov = self.getDefaultFov()
        cur_fov = self.getFov()
        self.zoom_motor.newValue(cur_fov, fov, time)
        
        pan = 0
        cur_pan = self.getPan()
        self.pan_motor.newValue(cur_pan, pan, time)
        
        tilt = 0
        cur_tilt = self.getTilt()
        self.tilt_motor.newValue(cur_tilt, tilt, time)
        
        
    def reset(self):
        self.zoom_motor.stop()
        self.pan_motor.stop()
        self.tilt_motor.stop()
        
        self.setFov(self.getDefaultFov())
        self.setPan(0)
        self.setTilt(0)
        self.cur_time = 0
        
        
    def update(self, time):
        increment = time - self.cur_time
        self.cur_time = time
        self.zoom_motor.update(increment)
        self.pan_motor.update(increment)
        self.tilt_motor.update(increment)
        

