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
import getopt
import logging

import atexit

from pandac.PandaModules import Filename

from file_io.camera_file import *
from camera.camera_builder import CameraBuilder
from camera.camera_manager import CameraManager
from simulator.panda3d.virtual_world import VirtualWorld
from simulator.panda3d.server.socket_server import SocketServer
from simulator.panda3d.controller import AUTOMATIC, MANUAL

PORT = 9099

def usage():
    print ""
    print "usage: python 3D_Simulator.py [options]"
    print "Options:"
    print "-d directory\t: Set the directory where the config files are located"
    print "-p port\t\t: Set the port the server should run on (default is 9099)"
    print "-a \t\t: Set the mode of the simulation controller to automatic"
    print "-s \t\t: A Sync session is used to control the time"
    print "-h \t\t: Print this help message and exit"
    print "-m \t\t: Set the directory where the models are located"
    print "--debug\t: Show debug messages"
    print ""


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:p:ahs", 
                                   ["dir=", "port=", "debug"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    directory = None
    port = PORT
    mode = MANUAL
    sync = False
    debug = False
    for o, a in opts:
        if o in ("-d", "--dir"):
            directory = Filename.fromOsSpecific(a)
            scene_file = os.path.join(a, "scene.xml")
            camera_file = os.path.join(a, "cameras.xml")
            pedestrian_file = os.path.join(a, "pedestrians.xml")
        elif o in ("-p", "--port"):
            port = int(a)
            
        elif o in ("-a"):
            mode = AUTOMATIC
            
        elif o in ("-h"):
            usage()
            sys.exit(0)
            
        elif o in ("-s"):
            sync = True
            
        elif o in ("--debug"):
            debug = True

    if not directory:
        print "Please specify a scenario directory using the -d flag!"
        sys.exit(2)
    
    format_str = '%(levelname)s: %(message)s'
    if debug:
        logging.basicConfig(format=format_str, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format_str, level=logging.INFO)

    # Create the virtual world by loading all of the models that make up the 
    # scene as well as all of the pedestrians.
    virtual_world = VirtualWorld(scene_file, pedestrian_file, directory, mode)
    model = virtual_world.getModel()
    
    # Create the camera manager which keeps track of what cameras are linked to 
    # what Vision Processing clients. Also acts as a message sender used to send
    # messages between cameras
    camera_manager = CameraManager()
    
    # Load all of the camera modules.
    # Each camera module is linked with a panda camera that has the ability to
    # render to a texture that can be processed using opencv.
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
    if mode != AUTOMATIC:
        server = SocketServer(port, virtual_world, camera_manager, sync)

    # Start the main event loop that runs the world.
    virtual_world.run()


if __name__ == "__main__":
    main()
