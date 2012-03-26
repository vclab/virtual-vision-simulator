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


class SystemStateLog:
  def __init__(self, path, scene):
    self.path = path
    self.filename = "system_state_log.xml"
    self.scene = scene
    
  def open(self):
    try:
      self.file = open("%s/%s" %(self.path, self.filename), 'w')
      self.file.write("<system_state_data>\n")
    except IOError as e:
      print "IOERROR:", e
    
  def update(self, time):
    try:
      self.file.write("<time_step>\n")
      self.file.write("\t<time>%s</time>\n" % time)
      #write pedestrian information
      self.file.write("\t<pedestrians>\n")
      for object in self.scene.getPedestrianList():
        self.file.write("\t\t<pedestrian>\n")
        for key, value in object.getStateLogData().items():
          self.file.write("\t\t\t<%s>%s</%s>\n" %(key, value, key))
        self.file.write("\t\t</pedestrian>\n")
      self.file.write("\t</pedestrians>\n")
      #write camera_information
      self.file.write("\t<cameras>\n")
      for camera in self.scene.getCameraList().values():
        self.file.write("\t\t<camera>\n")
        for key, value in camera.getStateLogData().items():
          self.file.write("\t\t\t<%s>%s</%s>\n" %(key, value, key))
        self.file.write("\t\t</camera>\n")
      self.file.write("\t</cameras>\n")
      self.file.write("</time_step>\n")
    except IOError as e:
      print "IOERROR:", e
    
  def close(self):
    try:
      self.file.write("</system_state_data>\n")
      self.file.close()
    except IOError as e:
      print "IOERROR:", e
