# Author: Michael T. Fang <mfang@caltech.edu>

""" Easy AutoCAD Scripter
This module simplies the drawing process for scripts that automate AutoCAD.
It draws various shapes by printing to a script file defined by the user, 
which is then run on AutoCAD.

*** NOTE: When exporting dxf file in AutoCAD, use the 2000 DXF version format.

The following is a simple example that draws some CPWs (with tapering)
on three defined layers (shown here: http://i.imgur.com/k8qN1yN.png):

ac = AutoScripter('test.scr')
ac.addLayer("CPW1",[100,200,50])
ac.addCPWStraightSrtEnd(width = 24, gap = 24, start = [0,0], end = [100,0])
ac.addCPWRamp(widthStart = 24, gapStart = 24, widthEnd = 12, gapEnd = 12, start = [100,0], end = [200,0])
ac.addCPWStraightSrtEnd(width = 12, gap = 12, start = [200,0], end = [300,0])
ac.addCPWRamp(widthStart = 12, gapStart = 12, widthEnd = 6, gapEnd = 6, start = [300,0], end = [400,0])
ac.addCPWStraightSrtEnd(width = 6, gap = 6, start = [400,0], end = [500,0])
ac.addLayer("CPW2",[100,50,200])
ac.addCPWStraightSrtEnd(width = 4, gap = 8, start = [-30,0], end = [-230,100])
ac.addCPWRamp(widthStart = 4, gapStart = 8, widthEnd = 16, gapEnd = 32, start = [-230,100], end = [-330,150])
ac.addLayer("CPW3",[200,50,100])
ac.addCPWStraightSrtEnd(width = 2, gap = 12, start = [-100,0], end = [-100,-100])
ac.addCPWStraightSrtEnd(width = 150, gap = 100, start = [0,400], end = [150,400])
ac.addCPWRamp(widthStart = 150, gapStart = 100, widthEnd = 2, gapEnd = 2, start = [150,400], end = [300,400])
ac.addCPWStraightSrtEnd(width = 2, gap = 2, start = [300,400], end = [500,400])

"""
<<<<<<< HEAD
from math import *
<<<<<<< HEAD
import subprocess
from os import getcwd
import shlex
=======
>>>>>>> origin/master
=======
import math
>>>>>>> parent of d359ce7... Chip design begins

class AutoScripter:
    def __init__(self,filename):
        self.script = open(filename,'w')
        self.script.write("(setvar \"CmdEcho\" 0)\n-osnap\n\n")
        self.prevAngleRad = 0.0
        self.prevEnd = [0.0,0.0]

    def addLayer(self, name = "NameMe", color = [255,255,255]): 
        """ Creates a new layer with the specified name and 
            RGB color"""
        self.script.write("-LAYER\nMAKE\n%s\n" % name)
        self.script.write("COLOR\nTRUECOLOR\n%d,%d,%d\n\n\n" \
            % tuple(color))

    def setLayer(self, name): 
        """ Changes current layer to specified by name"""
        self.script.write("-LAYER\nSET\n%s\n\n" % name)

    def addRect(self, base, xlen, ylen): 
        """ Adds a rectangle with corners (base[0],base[1]) and 
            (base[0] + xlen, base[1] + ylen)"""
        self.script.write("RECTANGLE\n%f,%f\n%f,%f\n" \
            % (base[0], base[1], base[0] + xlen, base[1] + ylen))

    def addCircle(self, base, r): 
        """ Adds a circle with radius r with center (base[0],base[1])"""
        self.script.write("CIRCLE\n%f,%f\n%f\n" % (base[0],base[1],r))

    def addCircleArray(self, base, r, space = [2,2], nRepeat = [2,2]):
        """ Repeats a circle nRepeat times upwards and rightwards with 
            separation given by space"""
        self.script.write("CIRCLE\n%f,%f\n%f\n" % (base[0],base[1], r))
        self.script.write("ARRAY\nLAST\n\n\n")
        self.script.write("%d\n%d\n" % tuple(nRepeat))
        if nRepeat[0] == 1:
            self.script.write("%f\n" % space[1])
        elif nRepeat[1] == 1:
            self.script.write("%f\n" % space[0])
        else:
            self.script.write("%f\n%f\n" % tuple(space))
    def addCPWStraightSrtEnd(self, width, gap, start, end):
        """ Adds a coplanar waveguide with the specified width and gap from start to end"""
        [disp, theta] = self.getDisplacementAndAngle(start, end)
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - width/2 - gap,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - width/2 - gap,start)
        self.script.write("c\n")
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + width/2 + gap,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + width/2 + gap,start)
        self.script.write("c\n")
        self.prevAngleRad = theta
        self.prevEnd = end
    def addCPWStraightLenAng(self, width, gap, length, start, angleRad):
        """ For cases when defining end coordinate relative to start in polar
            coordinate is more convenient."""
        end = [start[0] + length*math.cos(angleRad), start[1] + length*math.sin(angleRad)]
        self.addCPWStraightSrtEnd(width, gap, start, end)

    def rotateAndWritePoint(self,theta,x,y,pivot):
        """ Rotates the specified point (x,y) by an angle theta
            around the pivot and write the result to the script"""
        [x_rot,y_rot] = self.rotatePoint(theta,x,y,pivot)
        self.script.write("%f,%f\n" \
            % (x_rot, y_rot))

    def rotatePoint(self,theta,x,y,pivot):
        """ Rotates the specified point (x,y) by an angle theta
            around the pivot and write the result to the script"""
        x_rot = math.cos(theta)*(x - pivot[0]) \
            - math.sin(theta)*(y - pivot[1]) + pivot[0]
        y_rot = math.sin(theta)*(x - pivot[0])  \
            + math.cos(theta)*(y - pivot[1]) + pivot[1]
        return [x_rot,y_rot]

    def getDisplacementAndAngle(self, start, end):
        """ Does what it says"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        disp = (dx**2 + dy**2)**0.5
        if dx == 0 and dy > 0:
            theta = math.pi/2
        elif dx == 0 and dy < 0:
            theta = -math.pi/2
        elif dx < 0:
            theta = math.atan(dy/dx) + math.pi
        else:
            theta = math.atan(dy/dx)
        return [disp, theta]

    def addCPWRamp(self, widthStart, gapStart, widthEnd, gapEnd, start, end):
        """ Adds a coplanar waveguide with a linear ramp."""
        [disp, theta] = self.getDisplacementAndAngle(start, end)
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - widthStart/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - widthEnd/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - widthEnd/2 - gapEnd,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - widthStart/2 - gapStart,start)
        self.script.write("c\n")
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + widthStart/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + widthEnd/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + widthEnd/2 + gapEnd,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + widthStart/2 + gapStart,start)
        self.script.write("c\n")
        self.prevAngleRad = theta
        self.prevEnd = end

    def addCPWAngBend(self, width, gap, radius, angle, start, startAngleRad = 0):
        """ Adds a coplanar waveguide with a bend from startAngle to angle.
            Angle should be between -180 and 180 degrees. The radius of 
            the bend is defined from the middle of center the trace. 
            AutoCAD can only do arcs clockwise, so the code is a bit 
            verbose and tedious. """
        angleRad = math.pi*angle/180
        rw2 = radius + width/2
        rw2g = radius + width/2 + gap
        
        if angle > 0:
            center = [start[0], start[1] + radius]
            self.CPWAngBendHelperPositive(center, start, radius, width ,gap, angleRad, startAngleRad)
            x = start[0] + radius*math.sin(angleRad)
            y = start[1] + radius - radius*math.cos(angleRad)
        elif angle < 0:
            center = [start[0], start[1] - radius]
            self.CPWAngBendHelperNegative(center, start, radius, width ,gap, angleRad, startAngleRad)
            x = start[0] - radius*math.sin(angleRad)
            y = start[1] - radius + radius*math.cos(angleRad)           
        self.prevAngleRad = startAngleRad + angleRad
        self.prevEnd = self.rotatePoint(startAngleRad,x,y,start)

    def CPWAngBendHelperPositive(self, center, start, radius, width ,gap, angleRad ,startAngleRad):
        """ This is pretty much just the ugly geometry part of the bent CPW with angleRad > 0"""
        for i in range(0,2):
            # i = 0 makes the right side etch pattern
            # i = 1 makes the left side etch pattern
            if i == 0:
                sign = 1
            else:
                sign = -1
            rw2 = radius + sign*width/2
            rw2g = radius + sign*width/2 + sign*gap

            self.script.write("ARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)               
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2, start)
            arcEnd = [center[0] + rw2*math.sin(angleRad), \
                center[1] - rw2*math.cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)

            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1],start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0] + sign*gap*math.sin(angleRad), \
                arcEnd[1] - sign*gap*math.cos(angleRad),start)
            # self.rotateAndWritePoint(startAngleRad, arcEnd[0] - sign*gap*math.sin(angleRad), \
            #     arcEnd[1] + gap*math.cos(angleRad),start)

            self.script.write("\nARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2g, start)
            arcEnd = [center[0] + rw2g*math.sin(angleRad), \
                center[1] - rw2g*math.cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)

            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2, start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2g, start)
            self.script.write("\n")

    def CPWAngBendHelperNegative(self, center, start, radius, width ,gap, angleRad ,startAngleRad):
        """ This is pretty much just the ugly geometry part of the bent CPW with angleRad < 0"""
        for i in range(0,2):
            # i = 0 makes the right side etch pattern
            # i = 1 makes the left side etch pattern
            angleRad = -angleRad
            if i == 0:
                sign = 1
            else:
                sign = -1
            rw2 = radius + sign*width/2
            rw2g = radius + sign*width/2 + sign*gap
            self.script.write("ARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1], start)
            arcEnd = [center[0] + rw2*math.sin(sign*angleRad), \
                center[1] + rw2*math.cos(sign*angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2,start)

            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2,start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2g,start)

            self.script.write("\nARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)
            arcEnd = [center[0] + rw2g*math.sin(sign*angleRad), \
                center[1] + rw2g*math.cos(sign*angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2g, start)

            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0] - sign*gap*math.sin(sign*angleRad), \
                arcEnd[1] - sign*gap*math.cos(sign*angleRad),start)
            self.script.write("\n")

<<<<<<< HEAD
    def CPWMeander(self, width, gap, lengthTotal, radius, straightLength, startPhaseRad, start, startAngleRad):
        """ Generates a CPW meander which starts with a phase defined as follows: http://i.imgur.com/K03NLCl.png
            lengthTotal, radius, and straightLength more or less set the overall size of the meander"""
        startPhaseRad = startPhaseRad % (2*pi)
        lengthSoFar = 0 # Metric for length accumulation and stopping
        turn = 0 # Which way do I turn next? Clockwise (CW) or CCW?

        # First bend of meander
        if startPhaseRad == 0:
            self.addCPWAngBend(width, gap, radius, -180, self.prevEnd, self.prevAngleRad)
            lengthSoFar +=  radius*pi
            turn = 1
        elif startPhaseRad == pi:
            self.addCPWAngBend(width, gap, radius, 180, self.prevEnd, self.prevAngleRad)
            lengthSoFar += radius*pi
            turn = -1
        else:
            self.addCPWAngBend(width, gap, radius, 180*(startPhaseRad - pi)/pi, self.prevEnd, self.prevAngleRad)
            lengthSoFar += abs(radius*(startPhaseRad - pi))
            # Figure out which diretion to turn next
            if startPhaseRad < pi and startPhaseRad > 0:
                turn = 1
            else:
                turn = -1
        # The middle bulk of the meander
        while lengthTotal - (radius*pi + straightLength) > lengthSoFar:
            self.addCPWStraightLenAng(width, gap, straightLength, self.prevEnd, self.prevAngleRad)
            self.addCPWAngBend(width, gap, radius, turn*180, self.prevEnd, self.prevAngleRad)
            turn = -turn
            lengthSoFar += straightLength + radius*pi
        # The tail end of the meander
        if (lengthTotal - lengthSoFar) < straightLength: # Not long enough to finish straight segment
            self.addCPWStraightLenAng(width, gap, lengthTotal - lengthSoFar, self.prevEnd, self.prevAngleRad)
            lengthSoFar += lengthTotal - lengthSoFar
        else: # Can finish straight segment, need to end on a curve
            self.addCPWStraightLenAng(width, gap, straightLength, self.prevEnd, self.prevAngleRad)
            lastAngle = 180*(lengthTotal - lengthSoFar - straightLength)/(pi*radius) # Angle needed for ending
            self.addCPWAngBend(width, gap, radius, turn*lastAngle, self.prevEnd, self.prevAngleRad)
            lengthSoFar += straightLength + pi*lastAngle/180*radius

    def launchPadBegin(self, padWidth, totalWidth, traceWidth, traceGap, padLength, rampLength, start, startAngleRad):
        """  Begin a trace with a lunach pad """
        padGap = (totalWidth - padWidth)/2
        self.addCPWRectGap(padWidth, padGap, padGap, start, startAngleRad)
<<<<<<< HEAD
        self.addCPWStraightLenAng(padWidth, padGap, padLength, self.prevEnd, self.prevAngleRad)
        self.addCPWRampLenAng(padWidth, padGap, traceWidth, traceGap, rampLength, self.prevEnd, self.prevAngleRad)
=======
        self.addCPWStraightLenAng(padWidth, padGap, padLength, a.prevEnd, a.prevAngleRad)
        self.addCPWRampLenAng(padWidth, padGap, traceWidth, traceGap, rampLength, a.prevEnd, a.prevAngleRad)
>>>>>>> origin/master

    def launchPadEnd(self, padWidth, totalWidth, traceWidth, traceGap, padLength, rampLength, start, startAngleRad):
        """ End a trace with a lunach pad """
        padGap = (totalWidth - padWidth)/2
<<<<<<< HEAD
        self.addCPWRampLenAng(traceWidth, traceGap, padWidth, padGap, rampLength, self.prevEnd, self.prevAngleRad)
        self.addCPWStraightLenAng(padWidth, padGap, padLength, self.prevEnd, self.prevAngleRad)
        self.addCPWRectGap(padWidth, padGap, padGap, self.prevEnd, self.prevAngleRad)
=======
        self.addCPWRampLenAng(traceWidth, traceGap, padWidth, padGap, rampLength, a.prevEnd, a.prevAngleRad)
        self.addCPWStraightLenAng(padWidth, padGap, padLength, a.prevEnd, a.prevAngleRad)
        self.addCPWRectGap(padWidth, padGap, padGap, a.prevEnd, a.prevAngleRad)

# Make a complex CPW trace (See here: http://i.imgur.com/mGCyDBt.png)
a = AutoScripter('test.scr')
width = 4
gap = 4
width2 = 10
gap2 = 10
sign = 1
a.addLayer("Frame", [250,50,50])
a.addRect(base = [0,0], xlen = 10000, ylen = 10000)
a.addLayer("CPW", [50,250,50])
a.launchPadBegin(150, 300, width, gap, 200, 200, [3000,200], startAngleRad = pi/2)
a.addCPWAngBend(width, gap, 100, -45, a.prevEnd, a.prevAngleRad)
a.addCPWStraightLenAng(width, gap, length = 200, start = a.prevEnd, startAngleRad = a.prevAngleRad)
a.addCPWAngBend(width, gap, 100, 45, a.prevEnd, a.prevAngleRad)
for i in range(2,10):
    sign = -sign
    a.addCPWStraightLenAng(width, gap, 100, a.prevEnd, a.prevAngleRad)
    a.addCPWAngBend(width, gap, 2*(width + gap)*i, -180*sign, a.prevEnd, a.prevAngleRad)
=======
# Make a complex CPW trace (See here: http://i.imgur.com/ftmFp21.png)
a = AutoScripter('test.scr')
width = 5
gap = 5
sign = 1
a.addCPWStraightLenAng(width, gap, length = 100, start = [250,-250], angleRad = math.pi/8)
a.addCPWAngBend(width, gap, width + gap, 45, a.prevEnd, a.prevAngleRad)
for i in range(2,10):
    sign = -sign
    a.addCPWStraightLenAng(width, gap, 100, a.prevEnd, a.prevAngleRad)
    a.addCPWAngBend(width, gap, 1.5*(width + gap)*i, -180*sign, a.prevEnd, a.prevAngleRad)
>>>>>>> parent of d359ce7... Chip design begins
for i in range(0,3):
    a.addCPWStraightLenAng(width, gap, 100, a.prevEnd, a.prevAngleRad)
    a.addCPWAngBend(width, gap, 2*(width + gap), -90, a.prevEnd, a.prevAngleRad)
for i in range(0,3):
    a.addCPWAngBend(width, gap, 4*(width + gap), 90, a.prevEnd, a.prevAngleRad)
<<<<<<< HEAD
a.addCPWStraightLenAng(width, gap, 500, a.prevEnd, a.prevAngleRad)
a.CPWMeander(width, gap, 2500, 25, 150, -pi/3, a.prevEnd, a.prevAngleRad)
a.addCPWRampLenAng(width, gap, width2, gap2, 50, a.prevEnd, a.prevAngleRad)
a.CPWMeander(width2, gap2, 2500, 25, 150, pi/2, a.prevEnd, a.prevAngleRad)
a.addCPWRampLenAng(width2, gap2, width/2, gap/2, 100, a.prevEnd, a.prevAngleRad)
a.addCPWStraightLenAng(width/2, gap/2, 200, a.prevEnd, a.prevAngleRad)
a.addCPWAngBend(width/2, gap/2, 100, 30, a.prevEnd, a.prevAngleRad)
a.launchPadEnd(150, 300, width/2, gap/2, 200, 200, a.prevEnd, a.prevAngleRad)
>>>>>>> origin/master
=======
a.addCPWStraightLenAng(width, gap, 200, a.prevEnd, a.prevAngleRad)
>>>>>>> parent of d359ce7... Chip design begins
