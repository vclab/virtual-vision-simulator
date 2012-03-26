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


class PedestrianFileHandler(handler.ContentHandler):

    def __init__(self, model, pedestrian_builder):

        self.pbuilder = pedestrian_builder
        self.model = model
        self.cur_tag = ""
        self.p = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name == "pedestrian":
            character = attrs['character']
            texture = attrs['texture']
            scale = float(attrs['scale'])
            hpr = [int(x) for x in attrs['hpr'].split(" ")]
            pos = [float(x) for x in attrs['pos'].split(" ")]
            self.p = self.pbuilder.buildPedestrian(character, texture, scale, 
                                                   hpr, pos)
        
        elif name == "action":
            name = attrs['name']
            filename = attrs['anim']
            angle = float(attrs['angle'])
            diff = [float(x) for x in attrs['diff'].split(" ")]
            action = {'name':name, 'filename':filename, 'angle':angle, 'diff':diff}
            self.actions.append(action)
         
        elif name == "commands":
            if "start_time" in attrs:
                start_time = float(attrs['start_time'])
                self.p.setStartTime(start_time)

        elif name == "character":
            self.name = attrs['name']
            self.model_path = attrs['model']
            self.texture_dir = attrs['textures']
            self.animation_dir = attrs['animations']
            self.actions = []
        
        self.cur_tag = name

    def endElement(self, name):
        if name == "pedestrian":
            self.model.addPedestrian(self.p)
            self.p = None
            
        elif name == "character":
            self.pbuilder.addCharacter(self.name, self.model_path, 
                                       self.texture_dir, self.animation_dir,
                                       self.actions)

    def characters(self, char):
          
        if self.cur_tag == "point":
            point = [float(x) for x in char.split(" ")]
            self.p.addTrajectoryPoint(point)

        elif self.cur_tag == "color":
            color = [int(x) for x in char.split(" ")]
            self.p.setColor(color)
        elif self.cur_tag == "commands":
            self.p.addCommands([x.strip() for x in char.strip().split(" ")])

        self.cur_tag = ""


class PedestrianFileParser:

    def __init__(self, model, pedestrian_builder):
        self.handler = PedestrianFileHandler(model, pedestrian_builder)
        self.parser = make_parser()
        self.parser.setContentHandler(self.handler)

    def parse(self, in_file):
        try:
            pedestrian_file = open(in_file, 'r')
            self.parser.parse(pedestrian_file)
            pedestrian_file.close()
        except IOError, e:
            pass

