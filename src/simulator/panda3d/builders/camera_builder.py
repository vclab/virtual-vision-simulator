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


import os
from pandac.PandaModules import Spotlight
from pandac.PandaModules import Filename
from panda3d.core import (WindowProperties, FrameBufferProperties, GraphicsPipe,
                          GraphicsOutput, Texture)
from direct.actor.Actor import Actor

from ..camera.panda_ptz_camera import PandaPTZCamera


class PandaCameraBuilder:
    """Used to build different types of cameras"""

    def __init__(self, parent):
        self.parent = parent


    def buildPandaPTZCamera(self, config):
        buffer = self.makeFBO("camera buffer")
        panda_camera = base.makeCamera(buffer)
        panda_camera.reparentTo(render)
        path = Filename.fromOsSpecific(os.path.dirname(__file__))
        camera_model = loader.loadModel("%s/../camera/camera.egg" % path)
        camera_model.setScale(0.3)
        camera_model.reparentTo(render)
        
        panda_ptz_camera = PandaPTZCamera(buffer, panda_camera, camera_model)
        panda_ptz_camera.setColor(config.color)
        panda_ptz_camera.setId(config.id)
        panda_ptz_camera.setPos(config.position)
        panda_ptz_camera.setFovLimits(*config.fov_limits)
        panda_ptz_camera.setPanLimits(*config.pan_limits)
        panda_ptz_camera.setTiltLimits(*config.tilt_limits)
        panda_ptz_camera.setDefaultDirection(config.default_direction)
        panda_ptz_camera.setUp(config.up_vector)
        panda_ptz_camera.setNear(config.near_plane)
        panda_ptz_camera.setFar(config.far_plane)
        panda_ptz_camera.setFov(config.fov)
        panda_ptz_camera.setDefaultFov(config.default_fov)
        panda_ptz_camera.setPan(config.pan)
        panda_ptz_camera.setTilt(config.tilt)

        return panda_ptz_camera


    def makeFBO(self, name):
        """Creates an offscreen buffer with the specified name"""
        
        winprops = WindowProperties()
        props = FrameBufferProperties()
        props.setRgbColor(1)
        tex = Texture('Tex')
        gsg = base.win.getGsg()
        ge = base.graphicsEngine
        buffer = ge.makeOutput(base.pipe, 
                               name, 
                               -2, 
                               props, 
                               winprops,
                               GraphicsPipe.BFRefuseWindow | 
                               GraphicsPipe.BFFbPropsOptional, 
                               gsg, 
                               base.win)

        buffer.addRenderTexture(tex, GraphicsOutput.RTMCopyRam)
        return buffer

