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
from camera.camera_builder import (ACTIVE_CAMERA, STATIC_CAMERA)

class CameraManager:

    def __init__(self):
        self.local_cameras = {}
        self.remote_cameras= {}
        self.session_map = {}
        self.remote_message_queue = []


    def addCamera(self, camera):
        cam_id = camera.getId()
        self.local_cameras[cam_id] = camera


    def addRemoteCamera(self, camera):
        cam_id = camera['id']
        self.remote_cameras[cam_id] = camera


    def getCameraById(self, cam_id):
        if cam_id in self.local_cameras:
            return self.local_cameras[cam_id]
        else:
            return None


    def getCameras(self, type=None):
        local_cameras = self.local_cameras.values()
        if type:
            cameras = []
            for camera in local_cameras:
                if camera.getType() == type:
                    cameras.append(camera)
            return cameras
        else:
            return local_cameras


    def getAvailableCamera(self, type):
        for cam_id, camera in self.local_cameras.items():
            if not camera.hasSession() and camera.getType() == type:
                return camera
        return None


    def sendMessage(self, cam_id, message):
        if cam_id in self.local_cameras:
            self.local_cameras[cam_id].newMessage(message)
        elif cam_id in self.remote_cameras:
            self.remote_message_queue.append((cam_id, message))
        else:
            logging.error("Error sending message to camera! Invalid camera ID")


    def getRemoteMessages(self):
        messages = []
        while self.remote_message_queue:
            messages.append(self.remote_message_queue.pop(0))
        return messages


    def isWaiting(self):
        for camera in self.local_cameras.values():
            if camera.isWaiting():
                return True
        return False
            
