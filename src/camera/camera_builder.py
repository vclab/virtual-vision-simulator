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


import rc_camera
import rc_active_camera

STATIC_CAMERA = 0
ACTIVE_CAMERA = 1


def GetType(type):
    if type == "static_camera":
        return STATIC_CAMERA
    elif type == "active_camera":
        return ACTIVE_CAMERA
    else:
        return -1


class CameraBuilder:
    """Used to build different types of cameras"""


    def buildCamera(self, config):
        type = GetType(config.type)
        if type == ACTIVE_CAMERA:
            return rc_active_camera.buildCamera(config, ACTIVE_CAMERA)
        elif type == STATIC_CAMERA:
            return rc_camera.buildCamera(config, STATIC_CAMERA)
        else:
            return False

