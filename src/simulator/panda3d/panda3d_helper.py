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


from math import cos, sin, pi, atan2, sqrt, degrees
import numpy as np

def ToPandaCoordinates(point):
 
  matrix = np.zeros((3,3))
  matrix[0,0] = 1
  matrix[2,1] = 1
  matrix[1,2] = -1

  return np.dot(matrix, point)
  
  
def FromPandaCoordinates(point):

  matrix = np.zeros((3,3))
  matrix[0,0] = 1
  matrix[1,2] = 1
  matrix[2,1] = -1

  return np.dot(matrix, point)
  
def VectorToHpr(vector):
  x, y, z = vector
  yaw = -90 - degrees(atan2(z, x))
  pitch = degrees(atan2(y, sqrt(x * x + z * z)))
  return yaw, pitch





