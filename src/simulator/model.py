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

from math import pi, fabs

AMBIENTLIGHT = 1
SPOTLIGHT = 2
POINTLIGHT = 3
DIRECTIONALLIGHT = 4

class Model:
    """
    This class defines the model used to store all of the information needed by
    the simulator. This includes:
    - cameras
    - pedestrians
    - lights
    - static objects
    as well as any other data that has to be stored.
    """

    def __init__(self, directory):

        self.directory = directory

        self.camera_list= {}
        self.pedestrian_list = {}
        self.light_list = {SPOTLIGHT:[], AMBIENTLIGHT:[], POINTLIGHT:[], DIRECTIONALLIGHT:[]}
        self.object_list = []
        self.run_list = []
        self.camera_modules = {}

        # self.bounds = ((0,0,0), (0,0,0))
        # self.length = 0
        # self.width = 0
        # self.height = 0


    # def getDimensions(self):
    #     """ 
    #     Returns the scene dimensions as a tuple containing the length, width and
    #     height.
    #     """
    #     return (self.length, self.width, self.height)


    # def getLength(self):
    #     """Returns the length of the scene"""
    #     return self.length


    # def getWidth(self):
    #     """Returns the width of the scene"""
    #     return self.width


    # def getHeight(self):
    #     """Returns the height of the scene"""
    #     return self.height


    # def setBounds(self, bottom_left, top_right):
    #     """
    #     Set the bounds of the scene by specifying the bottom_left and top_right
    #     bounds of the scene.
    #     """
    #     x1, y1, z1 = bottom_left
    #     x2, y2, z2 = top_right
    #     self.length = fabs(x2 - x1)
    #     self.width = fabs(z2 - z1)
    #     self.height = fabs(y2 - y1)
    #     self.bounds = (bottom_left, top_right)


    # def getBounds(self):
    #     """
    #     Returns the bounds of the scene as a tuple containing the bottom left 
    #     and top right corners of the scene.
    #     """
    #     return self.bounds


    def addCameraModule(self, module):
        self.camera_modules[module.getId()] = module


    def getCameraModules(self):
        return self.camera_modules.values()


    def getCameraModuleById(self, id):  
        try:
            camera = self.camera_modules[id]
            return camera
        except Exception as e:
            print "Error: Invalid camera id"
            return None


    def addCamera(self, camera):
        """Add a camera to the scene"""
        self.camera_list[camera.getId()] = camera


    def getCameraByColor(self, color):
        """Get the camera with the specified color"""
        print "model.getCameraByColor"
        for camera in self.camera_list.values():
          if camera.getColor() == color:
            return camera
        return None


    def getCameraByName(self, name):
        """Get the camera with the specified name"""
        for camera in self.camera_list.values():
          if camera.getName() == name:
            return camera
        return None


    def getCameraById(self, id):
        """Get the camera with the specified id"""
        try:
            camera = self.camera_list[id]
            return camera
        except Exception as e:
            print "Error: Invalid camera id!"
            return None


    def getCameraList(self):
        """Get a list of all the cameras in the scene"""
        return self.camera_list.values()


    def addPedestrian(self, pedestrian):
        """Add a pedestrian to the scene"""
        self.pedestrian_list[pedestrian.getId()] = pedestrian


    def getPedestrianById(self, index):
        """Get the pedestrian with the specified ID"""
        try:
            pedestrian = self.pedestrian_list[index]
            return pedestrian
        except Exception as e:
            print "Error: Invalid pedestrian id!"
            return None


    def getPedestrianList(self):
        """Get a list of all the pedestrians in the scene"""
        return self.pedestrian_list.values()


    def addLight(self, light, type):
        """Add a light to the scene"""
        self.light_list[type].append(light)


    def getLightList(self, type=SPOTLIGHT):
        """Get a list of all the lights in the scene"""
        return self.light_list[type]


    def addObject(self, object):
        """Add a static object to the scene"""
        self.object_list.append(object)


    def getObjectList(self):
        """Get a list of all static objects in the scene"""
        return self.object_list


    def getRunList(self):
        """Get a list of all the runs"""
        return self.run_list


    def addRun(self, object):
        """Add an object to the run list"""
        self.run_list.append(object)

