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

from direct.task import Task
from simulator.panda3d.controller import MANUAL
from simulator.panda3d.server.message_handler import *

RC_CAMERA = 1

class Sync:

    def __init__(self, task_mgr, controller, camera_mgr, remote_sync):
        self.controller = controller
        self.camera_mgr = camera_mgr
        self.sync_session = None
        self.task_mgr = task_mgr
        task_mgr.add(self.updateSync, "Update Sync", 0)
        self.controller.setMode(MANUAL)
        self.remote_sync = remote_sync


    def setSession(self, session, vv_id, ip, port):
        self.sync_session = session
        self.vv_id = vv_id
        self.ip = ip
        self.port = port
        self.ready = True


    def updateSync(self, task):
        if self.sync_session:
            # Process messages from sync module
            messages = self.sync_session.getMessages()
            conn_id = self.sync_session.conn_id
            for type, message in messages:
                if type == SYNC_REQ_CAM_LIST:
                    logging.debug("Received SYNC_REQ_CAM_LIST message " \
                                  "from conn:%s" % conn_id)
                    cameras = self.camera_mgr.getCameras(RC_CAMERA)
                    message = eVV_ADV_CAM_LIST(self.ip, self.port, cameras)
                    self.sync_session.sendMessage(message)
                    logging.debug("Sent VV_ADV_CAM_LIST message to conn:%s" 
                                  % conn_id)
                    self.ready = False
                                  
                elif type == SYNC_STEP:
                    logging.debug("Received SYNC_STEP message from conn:%s" 
                                  % conn_id)
                    increment = message.get_float()
                    self.controller.step(increment)
                    self.ready = False
                    
                elif type == SYNC_REMOTE_CAM_LIST:
                    logging.debug("Received SYNC_REMOTE_CAM_LIST message " \
                                  "from conn:%s" % conn_id)
                    cameras = dSYNC_REMOTE_CAM_LIST(message)
                    for camera in cameras.values():
                        self.camera_mgr.addRemoteCamera(camera)
                elif type == SYNC_CAM_MESSAGE:
                    logging.info("Received SYNC_CAM_MESSAGE message from " \
                                  "conn:%s" % conn_id)
                    cam_id, message  = dSYNC_CAM_MESSAGE(message)
                    self.camera_mgr.sendMessage(cam_id, message)

            # Process messages from cameras
            messages = self.camera_mgr.getRemoteMessages()
            for cam_id, message in messages:
                new_message = eVV_CAM_MESSAGE(self.ip, self.port, cam_id, 
                                              message)
                self.sync_session.sendMessage(new_message)
                logging.info("Sent VV_CAM_MESSAGE to conn:%s" % conn_id)

            if not self.ready and not self.camera_mgr.isWaiting():
                message = eVV_READY(self.ip, self.port, self.vv_id)
                self.sync_session.sendMessage(message)
                logging.debug("Sent VV_READY message to conn:%s" % conn_id)
                self.ready = True

        # If not using remote sync client, update the world clock
        elif not self.remote_sync:
            if not self.camera_mgr.isWaiting():
                self.controller.step(0.033)

        return Task.cont


