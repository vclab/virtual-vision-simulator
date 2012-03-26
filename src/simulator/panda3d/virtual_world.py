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
import logging

from math import tan, radians

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText as OST
from direct.task import Task

from pandac.PandaModules import AntialiasAttrib, ClockObject, TextNode
from pandac.PandaModules import Vec3, VBase4
from pandac.PandaModules import Camera, OrthographicLens
from pandac.PandaModules import loadPrcFileData
from pandac.PandaModules import WindowProperties 

from builders.object_builder import ObjectBuilder
from builders.pedestrian_builder import PedestrianBuilder
from builders.light_builder import LightBuilder
from builders.camera_builder import PandaCameraBuilder
from file_io.scene_file import *
from file_io.pedestrian_file import *

from simulator.model import Model
from simulator.model import DIRECTIONALLIGHT
from simulator.panda3d.controller import Controller

WIDTH = 1024
HEIGHT = 768

loadPrcFileData("", "win-size %s %s" % (WIDTH, HEIGHT))
loadPrcFileData("", "texture-anisotropic-degree 10")

LIGHTS_PER_OBJECT = 4

PTZ_CAMERA = 1
WIDE_FOV_CAMERA = 2

MANUAL_CAMERA = False


def Length(a, b):
    ax, ay, az = a
    bx, by, bz = b
    length = (ax-bx) ** 2 + (ay-by) ** 2
    return length


class VirtualWorld(ShowBase): 

    def __init__(self, scene_file, pedestrian_file, dir, mode):
        ShowBase.__init__(self)

        self.globalClock = ClockObject.getGlobalClock()
        self.globalClock.setMode(ClockObject.MSlave)
        
        self.directory = dir
        self.model = Model(dir)
        self.loadScene(scene_file)
        self.loadPedestrians(pedestrian_file)
        
        self.cam_label = OST("Top Down", pos=(0, 0.95), fg=(1,1,1,1), 
                             scale=0.05, mayChange=True)
        self.time_label = OST("Time: 0.0", pos=(-1.3, 0.95), fg=(1,1,1,1), 
                              scale=0.06, mayChange=True, align=TextNode.ALeft)
                                       
        self.accept("arrow_right", self.changeCamera, [1])
        self.accept("arrow_left", self.changeCamera, [-1])
        self.accept("escape", self.exit)
        self.accept("aspectRatioChanged", self.setAspectRatio)
        self.accept("window-event", self.windowChanged)

        #base.disableMouse()
        lens = OrthographicLens()
        lens.setFilmSize(1550, 1000)
        self.display_region = base.win.makeDisplayRegion()
        self.default_camera = render.attachNewNode(Camera("top down"))
        self.default_camera.node().setLens(lens)
        self.default_camera.setPosHpr(Vec3( -75, 0, 2200), Vec3(0, -90, 0))

        self.setCamera(0)

        self.controller = Controller(self, mode)
        self.taskMgr.add(self.updateCameraModules, "Update Camera Modules", 80)
        
        self.globalClock.setFrameTime(0.0)
        self.width = WIDTH
        self.height = HEIGHT

        props = WindowProperties( ) 
        props.setTitle( 'Virtual Vision Simulator' ) 
        base.win.requestProperties( props ) 


    def getModel(self):
        """
        Returns the model that stores all of the cameras, pedestrians and 
        static objects in the scene.
        """
        return self.model


    def getController(self):
        """
        Returns a controller that is used to control the world time.
        """
        return self.controller


    def getTime(self):
        """
        Returns the current time in the world.
        """
        return self.globalClock.getFrameTime()


    def loadScene(self, scene_file):
        """
        Loads the static objects that make up the scene. Also loads the lights
        that illuminate the scene and for performance implications, sets what 
        lights affect what objects.
        """
        if not os.path.exists(scene_file):
            logging.error("The path '%s' does not exist" % scene_file)
            sys.exit()
        light_builder = LightBuilder(self)
        object_builder = ObjectBuilder(self, self.directory)
        parser = SceneFileParser(self.model, object_builder, light_builder)
        parser.parse(scene_file)
        
        self.setUpLights()


    def setUpLights(self):
        # Set what lights illuminate what objects
        light_list = self.model.getLightList()
        static_objects = self.model.getObjectList()
        for object in static_objects:
            if object.hasLighting():
                model_root = object.getModel().getChildren()[0]
                children = model_root.getChildren()
                for child in children:
                    light_map = {}
                    for index, light in enumerate(light_list):
                        distance = Length(child.getPos(render), light.getPos())
                        half_fov = light.node().getLens().getFov()[0] / 2.0
                        height = light.getPos()[2]
                        radius = height * tan(radians(half_fov))
                        if distance > radius ** 2 + 2500 + 10:
                            continue
                        if distance not in light_map:
                            light_map[distance] = [index]
                        else:
                            light_map[distance].append(index)

                    sorted_lights = sorted(light_map.keys())
                    light_count = 0
                    for key in sorted_lights:
                        for i in light_map[key]:
                            child.setLight(light_list[i])
                            light_count += 1
                            if light_count > LIGHTS_PER_OBJECT:
                                break
                        if light_count > LIGHTS_PER_OBJECT:
                            break
                    child.flattenStrong()
        
        # Apply a directional light to the static models        
        light_list = self.model.getLightList(DIRECTIONALLIGHT)
        if light_list:
            for object in static_objects:
                if object.hasLighting():
                    model_root = object.getModel().getChildren()[0]
                    model_root.setLight(light_list[0])

        render.setShaderAuto()
        render.setAntialias(AntialiasAttrib.MLine)


    def loadPedestrians(self, pedestrian_file):
        """Loads the pedestrians into the scene."""
        if not os.path.exists(pedestrian_file):
            logging.error("The path '%s' does not exist" % pedestrian_file)
            sys.exit()
        pedestrian_builder = PedestrianBuilder(self, "../media/characters/")
        parser = PedestrianFileParser(self.model, pedestrian_builder)
        parser.parse("../media/characters/pedestrians.xml")
        parser.parse(pedestrian_file)


    def addCamera(self, config):
        """
        This method is used to add a new panda camera to the world. The panda
        camera is returned so that it can be linked with a camera module.
        """
        type = config.type
        cam_builder = PandaCameraBuilder(self)
        if type == WIDE_FOV_CAMERA:
            pass
        else:
            camera = cam_builder.buildPandaPTZCamera(config)
            self.model.addCamera(camera)
        return camera


    def setAspectRatio(self):
        """
        This method is called when the aspect ratio of the window changes.
        It updates the aspect ratios of all the cameras.
        """
        width = base.win.getXSize()
        height = base.win.getYSize()
        ratio = self.camLens.getAspectRatio()
        camera_list = self.model.getCameraList()
        for camera in camera_list:
            camera.setAspectRatio(ratio)
            camera.setImageSize(width, height)

        self.default_camera.node().getLens().setAspectRatio(ratio)
        r =  width / float(height)
        self.time_label.setPos(-r, 0.95)


    def changeCamera(self, num):
        """
        This method is used to toggle the camera that is viewed in the main 
        window. Typically num is either 1 or -1 denoting whether to toggle up
        or down the camera list.
        """
        number = self.cur_camera + 1 + num
        num_cameras = len(self.model.getCameraList())
        if number > num_cameras:
            number = 0
        elif number < 0:
            number = num_cameras
        self.setCamera(number)


    def setCamera(self, num):
        """
        This method sets which cameras view is shown in the panda3d window.
        """
        if MANUAL_CAMERA:
            self.cur_camera = num -1
            return
        
        self.display_region.setClearColor(VBase4(0, 0, 0, 1))
        self.display_region.setClearColorActive(True)
        self.display_region.setClearDepthActive(True)
        if num == 0:
            self.cur_camera = -1
            self.display_region.setCamera(self.default_camera)
            self.cam_label.setText("Top Down")
        else:
            camera_list = self.model.getCameraList()
            index = num - 1
            if index < len(camera_list):
                self.cur_camera = index
                camera = camera_list[index]
                camera_np = camera.getCameraNode()
                self.display_region.setCamera(camera_np)
                name = camera.getName()
                status_label = camera.getStatusLabel()
                label = "%s: %s" %(name, status_label)
                self.cam_label.setText(label)


    def step(self, increment):
        """
        This method updates the world by one time step.
        """
        if increment:
            new_time = self.globalClock.getFrameTime() + increment
        else:
            new_time = self.globalClock.getRealTime()
            
        self.globalClock.setFrameTime(new_time)
        self.time_label.setText("Time: %.2f" % new_time)
        
        self.updateActors()
        self.updateCameras()


    def updateActors(self):
        """
        This method updates the pedestrians in the scene by calling their update
        functions.
        """
        pedestrians = self.model.getPedestrianList()
        time = self.getTime()
        for pedestrian in pedestrians:
            if pedestrian.isActive(time):
                pedestrian.update(time)


    def updateCameras(self):
        """
        This method updates the panda cameras which are used to provide the
        higher level camera modules with rendered images of the scene. There
        is one panda camera for each camera module.
        """
        time = self.getTime()
        camera_list = self.model.getCameraList()
        for camera in camera_list:
            camera.update(time)
        
        if self.cur_camera != -1:
            cur_camera = camera_list[self.cur_camera]
            if cur_camera.statusChanged():
                name = cur_camera.getName()
                status_label = cur_camera.getStatusLabel()
                label = "%s: %s" %(name, status_label)
                self.cam_label.setText(label)


    def updateCameraModules(self, task):
        """
        This method updates the camera modules by calling their update function.
        This allows the camera modules to process messages and complete any
        tasks that were assigned to them.
        """
        time = self.getTime()
        for camera in self.model.getCameraModules():
            camera.update(time)
        return Task.cont


    def windowChanged(self, window):
        """
        This function is called when the window is modified. It updates the
        image size used by the cameras when getting the rendered image from the 
        texture.
        """
        wp = window.getProperties()
        width = wp.getXSize()
        height = wp.getYSize()
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            camera_list = self.model.getCameraList()
            for camera in camera_list:
                camera.setImageSize(width, height)
        self.windowEvent(window)


    def exit(self):
        sys.exit()


