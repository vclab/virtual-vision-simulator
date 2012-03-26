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
import logging
import sys

from pandac.PandaModules import Filename
from pandac.PandaModules import Spotlight
from direct.actor.Actor import Actor
from simulator.panda3d.panda_object import PandaObject

class ObjectBuilder:
  
    def __init__(self, parent, config_path):
        self.parent = parent
        self.config_path = config_path


    def buildObject(self, model, scale, pos, hpr, has_lighting=True):
        """Builds a static object using the Panda3D loadModel function"""
        path = os.path.normpath("%s/%s" % (self.config_path, model))
        if not os.path.exists(path):
            logging.error("The path '%s' does not exist" % path)
            sys.exit()
        path = Filename.fromOsSpecific(path)
        object = self.parent.loader.loadModel(path)
        object.setPos(*pos)
        object.setHpr(*hpr)
        object.setScale(scale)
        object.reparentTo(self.parent.render)
        static_object = PandaObject(object, has_lighting)
        return static_object
