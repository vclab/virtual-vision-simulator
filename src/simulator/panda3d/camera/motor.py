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


class Motor:
    def __init__(self, object_ptr, method):
        self.object_ptr = object_ptr
        self.method = method
        self.curve = LinearAnimationCurve()
        self.is_running = False

    def newValue(self, start, end, duration):
        self.is_running = True
        self.start_value = start
        self.end_value = end
        self.difference = self.end_value - self.start_value
        self.duration = duration
        self.cur_time = 0.0

    def update(self, increment):
        if self.is_running:
            self.cur_time += increment
            progress = self.curve.getValue(self.cur_time / self.duration)
            new_value = self.start_value + progress * self.difference
            eval("self.object_ptr.%s(%s)" % (self.method, new_value))
            
            if self.cur_time >= self.duration:
                self.is_running = False
    def stop(self):
        self.is_running = False

class InOutAnimationCurve:

    def __init__(self):
        pass


    def getValue(self, progress):
        if progress < 0.5:
            return 2 * pow(progress, 2)
        else:
            return -2 * pow(progress - 1, 2) + 1

class LinearAnimationCurve:

    def __init__(self):
        pass

    def getValue(self, progress):
        return progress

