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


from xml.sax import handler, make_parser
import numpy as np



class CameraFileHandler(handler.ContentHandler):

    def __init__(self):
      
        self.camera_configs = []
        self.cur_tag = ""

        self.config = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
      
        if name == "camera":
            type = attrs['type']
            self.config = CameraConfiguration()
            self.config.type = type
        self.cur_tag = name


    def endElement(self, name):
      
        if name == "camera":
            self.camera_configs.append(self.config)
            self.config = None


    def characters(self, char):
      
        if self.cur_tag == "color":
            color = [int(x) for x in char.split(" ")]
            self.config.color = color


        elif self.cur_tag == "id":
            self.config.id = int(char)

          
        elif self.cur_tag == "position":
            pos = [int(x) for x in char.split(" ")]
            self.config.position = pos

          
        elif self.cur_tag == "default_direction":
            direction = [float(x) for x in char.split(" ")]
            self.config.default_direction = direction

          
        elif self.cur_tag == "up_vector":
            up_vector = [int(x) for x in char.split(" ")]
            self.config.up_vector = up_vector


        elif self.cur_tag == "near_plane":
            near_plane = int(char)
            self.config.near_plane = near_plane


        elif self.cur_tag == "far_plane":
            far_plane = int(char)
            self.config.far_plane = far_plane


        elif self.cur_tag == "default_fov":
            fov = int(char)
            self.config.default_fov = fov


        elif self.cur_tag == "fov":
            fov = int(char)
            self.config.fov = fov


        elif self.cur_tag == "pan":
            pan = int(char)
            self.config.pan = pan
            
        elif self.cur_tag == "tilt":
            tilt = int(char)
            self.config.tilt = tilt


        elif self.cur_tag == "fov_limits":
            min, max = [int(x) for x in char.split(" ")]
            self.config.fov_limits = (min, max)


        elif self.cur_tag == "pan_limits":
            left, right = [int(x) for x in char.split(" ")]
            self.config.pan_limits = (left, right)
            
          
        elif self.cur_tag == "tilt_limits":
            down, up = [int(x) for x in char.split(" ")]
            self.config.tilt_limits = (down, up)

        elif self.cur_tag == "left":
            left = int(char)
            if left == -1:
                left = None
                
            self.config.left = left
        elif self.cur_tag == "right":
            right = int(char)
            if right == -1:
                right = None
                
            self.config.right = right
        
        else:
           pass

        self.cur_tag = ""
        
    def getCameraConfigs(self):
        return self.camera_configs

class CameraFileParser:

    def __init__(self):

        self.handler = CameraFileHandler()
        self.parser = make_parser()
        self.parser.setContentHandler(self.handler)

    def parse(self, file_name):

        try:
            camera_file = open(file_name, 'r')
            self.parser.parse(camera_file)
            camera_file.close()
        except IOError, e:
            pass
        
        return self.handler.getCameraConfigs()


class CameraConfiguration:
    def __init__(self):
        self.id = -1
        self.type = "ptz"
        self.color= (255,255,255)
        self.position = (0,0,0)
        self.up_vector = (0,1,0)
        self.default_direction = (0,0,0)
        self.default_fov = 90
        self.fov = 90
        self.pan = 0
        self.tilt = 0
        self.fov_limits = (10,90)
        self.pan_limits = (-25,25)
        self.tilt_limits = (-25,25)
        self.near_plane = 1
        self.far_plane = 100000
        self.left = None
        self.right = None
        

