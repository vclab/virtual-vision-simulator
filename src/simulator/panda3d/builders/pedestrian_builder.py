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

from pandac.PandaModules import Spotlight
from direct.actor.Actor import Actor
from pandac.PandaModules import VBase3

from ..panda3d_helper import *
from ..panda_pedestrian import PandaPedestrian

class PedestrianBuilder:
    """Used to build a Panda3D actor"""
    def __init__(self, parent, config_path):
        self.parent = parent
        self.config_path = config_path
        self.pedestrian_count = 0
        self.characters = {}


    def buildPedestrian(self, character_name, texture, scale, hpr, pos):
        """Builds a Panda3D actor by using the specified model and texture"""
        if not character_name in self.characters:
            return
        character = self.characters[character_name]
        model_path = os.path.normpath("%s/%s" 
                                      % (self.config_path, character['model']))
        if not os.path.exists(model_path):
            logging.error("The path '%s' does not exist" % model_path)
            sys.exit()
        
        actor = Actor(model_path)
        tex_dir = character['texture_dir']
        tex_path = os.path.normpath("%s/%s/%s" 
                                    %(self.config_path, tex_dir, texture))
        if not os.path.exists(tex_path):
            logging.error("The path '%s' does not exist" % tex_path)
            sys.exit()
        tex = loader.loadTexture(tex_path)
        actor.setTexture(tex,1)
        actor.reparentTo(self.parent.render)
        actor.setScale(scale)
        actor.setHpr(VBase3(*hpr))
        actor.setPos(*ToPandaCoordinates(VBase3(*pos)))
        
        joint = character['joint']
        panda_pedestrian = PandaPedestrian(actor, texture, self.parent.taskMgr, joint)
        panda_pedestrian.setId(self.pedestrian_count)
        self.pedestrian_count += 1
        
        anim_path = character['animation_dir']
        actions = character['actions']
        for action in actions:
            name = action['name']
            filename = action['filename']
            angle = action['angle']
            diff = action['diff']
            #name, path = self.formatAnimation(name, path)
            path = os.path.normpath("%s/%s/%s" 
                                    %(self.config_path, anim_path, filename))
            panda_pedestrian.addAnimation(name, path)
            panda_pedestrian.addAction(name, angle, diff)

        
        return panda_pedestrian  


    def addCharacter(self, name, model, texture_dir, animation_dir, actions):
        character = {}
        character['model'] = model
        character['texture_dir'] = texture_dir
        character['animation_dir'] = animation_dir
        character['joint'] = "%s-Bip" % name
        character['actions'] = actions
        self.characters[name] = character


    def formatAnimation(self, name, path):
        return (name,"%s/%s" % (self.config_path, path))
