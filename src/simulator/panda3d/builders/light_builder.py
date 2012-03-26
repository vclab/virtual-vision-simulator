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


from pandac.PandaModules import Spotlight, AmbientLight, DirectionalLight
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec4, Point3, VBase4, VBase3

class LightBuilder:
  """Used to build different Panda3D lights"""
  
  def __init__(self, parent):
    self.parent = parent
    self.light_counter = 0
    self.has_dlight = False

  def buildSpotlight(self, pos, fov, exponent, casts_shadow, shadow_caster, pitch, near, far, color):
    """
    Builds a Panda3D Spotlight at the specified position with the specified
    field of view and color
    """
    self.light_counter += 1
    light = Spotlight("light%s" % self.light_counter)
    if casts_shadow:
      x, y = shadow_caster
      light.setShadowCaster(True, x, y)
      light.getLens().setFar(far)
    else:
      light.setShadowCaster(False)
      light.getLens().setFar(2)
    light.setColor(VBase4(*color))
    light.getLens().setNear(near)
    lightnp = render.attachNewNode(light)
    lightnp.setPos(*pos)
    lightnp.setP(pitch)
    light.getLens().setFov(fov)
    
    light.setExponent(exponent)
    return lightnp
    

  def buildAmbientLight(self, color):
    """
    Builds a Panda3D Ambient Light with the specified color.
    """
    alight = render.attachNewNode(AmbientLight("Ambient"))
    alight.node().setColor(Vec4(*color))
    render.setLight(alight)
    return alight


  def buildDirectionalLight(self, hpr, pos, color, near, far, casts_shadow, shadow_caster, film_size):
    """
    Builds a Panda3D directional light with the specified rotation, position
    and color. 
    NOTE: This light tends to be buggy. Requires at least one spotlight for it 
    to work properly. 
    """
    if not self.has_dlight:
        self.light_counter += 1
        dlight = DirectionalLight("light%s" % self.light_counter)
        dlight.getLens().setFilmSize(*film_size)
        dlight.getLens().setNearFar(near, far);
        if shadow_caster:
            x, y = shadow_caster
            dlight.setShadowCaster(True, x, y)
        else:
            dlight.setShadowCaster(False)
        #dlight.showFrustum()
        dlightnp = render.attachNewNode(dlight)
        dlightnp.setPos(VBase3(*pos))
        dlightnp.setHpr(VBase3(*hpr))
        dlight.setColor(VBase4(*color))
        render.setLight(dlightnp)
        return dlightnp
    else:
        return 0

