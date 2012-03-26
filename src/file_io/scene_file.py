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

from xml.sax import handler, make_parser

from simulator.model import AMBIENTLIGHT, SPOTLIGHT, POINTLIGHT, DIRECTIONALLIGHT

DEFAULT_SPOTLIGHT = {"fov":150, 
                     "exponent":1.5, 
                     "color":[0.7, 0.7, 0.7, 1], 
                     "pitch":-90,
                     "near":10,
                     "far":200,
                     "casts_shadow":True,
                     "shadow_caster":[4096, 4096]}

DEFAULT_DIRECTIONAL_LIGHT = {"color":[0.7, 0.7, 0.7, 1], 
                             "near":-10,
                             "far":200,
                             "casts_shadow":True,
                             "shadow_caster":[4096, 4096],
                             "film_size":[512, 512]}

class SceneFileHandler(handler.ContentHandler):

  def __init__(self, scene, object_builder, light_builder):

    self.scene = scene
    self.object_builder = object_builder
    self.light_builder = light_builder
    
    self.type = type
    self.current_tag = ""

  def startElement(self, name, attrs):
    if name == "model":
      self.newModel(attrs)
      
    elif name == "light":
      
      if "type" in attrs:
        type = attrs['type']
        
        if type == "ambient":
          self.newAmbientLight(attrs)
        
        elif type == "directional":
          self.newDirectionalLight(attrs)

        elif type == "spotlight":
          self.newSpotlight(attrs)


  def newModel(self, attrs):
    path = attrs["path"]
    scale = float(attrs["scale"])
    pos = [float(x) for x in attrs["pos"].split(" ")]
    hpr = [float(x) for x in attrs["hpr"].split(" ")]
    has_lighting = attrs["has_lighting"] in ['true', '1', 'True', 'TRUE']
    
    model = self.object_builder.buildObject(path, scale, pos, hpr, has_lighting)
    self.scene.addObject(model)


  def newDirectionalLight(self, attrs):
    # mandetory attributes
    hpr = [float(x) for x in attrs['hpr'].split(" ")]
    pos = [float(x) for x in attrs['pos'].split(" ")]

    # optional attributes
    if 'color' in attrs:
      color = [float(x) for x in attrs['color'].split(" ")]
    else:
      color = DEFAULT_DIRECTIONAL_LIGHT['color']

    if 'near' in attrs:
      near = float(attrs['near'])
    else:
      near = DEFAULT_DIRECTIONAL_LIGHT['near']

    if 'far' in attrs:
      far = float(attrs['far'])
    else:
      far = DEFAULT_DIRECTIONAL_LIGHT['far']

    if 'casts_shadow' in attrs:
      if int(attrs['casts_shadow']) == 1:
        casts_shadow = True
      else:
        casts_shadow = False
    else:
      casts_shadow = False

    if 'shadow_caster' in attrs:
      shadow_caster = [int(x) for x in attrs['shadow_caster'].split(" ")]
    else:
      shadow_caster = DEFAULT_DIRECTIONAL_LIGHT['shadow_caster']
    
    if 'film_size' in attrs:
      film_size = [int(x) for x in attrs['film_size'].split(" ")]
    else:
      film_size = DEFAULT_DIRECTIONAL_LIGHT['film_size']

    light = self.light_builder.buildDirectionalLight(hpr, pos, color, near,
                                                     far, casts_shadow,
                                                     shadow_caster, film_size)
    # the scene can only have one directional light
    if light:
      self.scene.addLight(light, DIRECTIONALLIGHT)


  def newAmbientLight(self, attrs):
    color = [float(x) for x in attrs['color'].split(" ")]
    light = self.light_builder.buildAmbientLight(color)
    self.scene.addLight(light, AMBIENTLIGHT)


  def newSpotlight(self, attrs):
    # mandetory attributes
    pos = [float(x) for x in attrs["pos"].split(" ")]

    # optional attributes
    if 'fov' in attrs:
      fov = int(attrs["fov"])

    if 'casts_shadow' in attrs:
      if int(attrs['casts_shadow']) == 1:
        casts_shadow = True
      else:
        casts_shadow = False
    else:
      casts_shadow = False

    if 'shadow_caster' in attrs:
      shadow_caster = [int(x) for x in attrs['shadow_caster'].split(" ")]
    else:
      shadow_caster = DEFAULT_SPOTLIGHT['shadow_caster']

    if 'pitch' in attrs:
      pitch = int(attrs['pitch'])
    else:
      pitch = DEFAULT_SPOTLIGHT['pitch']

    if 'near' in attrs:
      near = float(attrs['near'])
    else:
      near = DEFAULT_SPOTLIGHT['near']

    if 'far' in attrs:
      far = float(attrs['far'])
    else:
      far = DEFAULT_SPOTLIGHT['far']

    if 'exponent' in attrs:
      exponent = float(attrs["exponent"])
    else:
      exponent = DEFAULT_SPOTLIGHT['exponent']

    if 'color' in attrs:
      color = [float(x) for x in attrs['color'].split(" ")]
    else:
      color = DEFAULT_SPOTLIGHT['color']

    light = self.light_builder.buildSpotlight(pos, fov, exponent, casts_shadow, 
                                              shadow_caster, pitch, near, far, 
                                              color)
    self.scene.addLight(light, SPOTLIGHT)


class SceneFileParser:

  def __init__(self, scene, object_builder, light_builder):
    handler = SceneFileHandler(scene, object_builder, light_builder)
    self.parser = make_parser()
    self.parser.setContentHandler(handler)
    
  def parse(self, file_name):
    try:
      scene_file = open(file_name, 'r')
      self.parser.parse(scene_file)
      scene_file.close()
    except IOError, e:
      pass
