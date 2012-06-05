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


import sys
import os
import argparse
import logging

import atexit

from pandac.PandaModules import Filename

from file_io.camera_file import *
from camera.camera_builder import CameraBuilder
from camera.camera_manager import CameraManager
from simulator.panda3d.virtual_world import VirtualWorld
from simulator.panda3d.server.socket_server import SocketServer
from simulator.panda3d.controller import AUTOMATIC, MANUAL

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', dest='directory', required=True,
        help='the directory where the config files are located')
    parser.add_argument('-p', '--port', dest='port', type=int, default=9099,
        help='the port the server should run on')
    parser.add_argument('-a', '--automatic', dest='mode', action='store_const',
        const=AUTOMATIC, default=MANUAL,
        help='set the mode of the simulation controller to automatic')
    parser.add_argument('-s', '--sync', dest='sync', action='store_true',
        default=False, help='a Sync session is used to control the time')
    parser.add_argument('-m', '--models', dest='models',
        help='the directory where the models are located')
    parser.add_argument('--debug', dest='debug', action='store_const',
        const=logging.DEBUG, default=logging.INFO, help='show debug messages')
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=args.debug)

    # Create the virtual world by loading all of the models that make up the 
    # scene as well as all of the pedestrians.
    virtual_world = VirtualWorld(os.path.join(args.directory, 'scene.xml'),
        os.path.join(args.directory, 'pedestrians.xml'),
        Filename.fromOsSpecific(args.directory), args.mode)
    model = virtual_world.getModel()
    
    # Create the camera manager which keeps track of what cameras are linked to 
    # what Vision Processing clients. Also acts as a message sender used to send
    # messages between cameras
    camera_manager = CameraManager()
    
    # Load all of the camera modules.
    # Each camera module is linked with a panda camera that has the ability to
    # render to a texture that can be processed using opencv.
    camera_file = os.path.join(args.directory, 'cameras.xml')
    if not os.path.exists(camera_file):
            logging.error("The path '%s' does not exist" % camera_file)
            sys.exit()
    parser = CameraFileParser()
    configs = parser.parse(camera_file)
    camera_builder = CameraBuilder()
    for config in configs:
        cam_module = camera_builder.buildCamera(config)
        if not cam_module:
            continue
        model.addCameraModule(cam_module)
        cam_type = cam_module.getType()
        camera_manager.addCamera(cam_module)
        camera = virtual_world.addCamera(config)
        cam_module.setPandaCamera(camera)
        cam_module.setCameraManager(camera_manager)

    # Create the server object that listens for incoming messages and connection 
    # requests from other modules.
    if args.mode != AUTOMATIC:
        server = SocketServer(args.port, virtual_world, camera_manager,
            args.sync)

    # Start the main event loop that runs the world.
    virtual_world.run()


if __name__ == "__main__":
    main()
