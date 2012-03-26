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


from direct.task import Task

AUTOMATIC = 1
MANUAL = 2

class Controller:
    def __init__(self, virtual_world, mode):
        self.__virtual_world = virtual_world
        self.__task_manager = self.__virtual_world.taskMgr

        self.__mode = None
        self.setMode(mode)


    def __stepTask(self, task):
        self.step(None)
        return Task.cont


    def getTime(self):
        return self.__virtual_world.getTime()


    def step(self, increment):
        self.__virtual_world.step(increment)


    def setMode(self, mode):
        if mode == AUTOMATIC:
            if self.__mode != AUTOMATIC:
                self.__task_manager.add(self.__stepTask, "Step Task", 0)
                self.__mode = AUTOMATIC
        elif mode == MANUAL:
            if self.__mode != MANUAL:
                self.__task_manager.remove("Step Task")
                self.__mode = MANUAL


