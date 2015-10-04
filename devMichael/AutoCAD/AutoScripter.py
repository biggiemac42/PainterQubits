# Author: Michael T. Fang <mfang@caltech.edu>

""" Easy AutoCAD Scripter
This module simplies the drawing process for scripts that automate AutoCAD.
It draws various shapes by printing to a script file defined by the user, 
which is then run on AutoCAD.

The following is a simple example that draws some CPWs (with tapering)
on three defined layers (shown here: http://i.imgur.com/k8qN1yN.png):

ac = AutoScripter('test.scr')
ac.addLayer("CPW1",[100,200,50])
ac.addCPWStraight(width = 24, gap = 24, start = [0,0], end = [100,0])
ac.addCPWRamp(widthStart = 24, gapStart = 24, widthEnd = 12, gapEnd = 12, start = [100,0], end = [200,0])
ac.addCPWStraight(width = 12, gap = 12, start = [200,0], end = [300,0])
ac.addCPWRamp(widthStart = 12, gapStart = 12, widthEnd = 6, gapEnd = 6, start = [300,0], end = [400,0])
ac.addCPWStraight(width = 6, gap = 6, start = [400,0], end = [500,0])
ac.addLayer("CPW2",[100,50,200])
ac.addCPWStraight(width = 4, gap = 8, start = [-30,0], end = [-230,100])
ac.addCPWRamp(widthStart = 4, gapStart = 8, widthEnd = 16, gapEnd = 32, start = [-230,100], end = [-330,150])
ac.addLayer("CPW3",[200,50,100])
ac.addCPWStraight(width = 2, gap = 12, start = [-100,0], end = [-100,-100])
ac.addCPWStraight(width = 150, gap = 100, start = [0,400], end = [150,400])
ac.addCPWRamp(widthStart = 150, gapStart = 100, widthEnd = 2, gapEnd = 2, start = [150,400], end = [300,400])
ac.addCPWStraight(width = 2, gap = 2, start = [300,400], end = [500,400])

"""
import math

class AutoScripter:
    def __init__(self,filename):
        self.script = open(filename,'w')
        self.script.write("(setvar \"CmdEcho\" 0)\n-osnap\n\n")
        self.prevAngle = 0

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
    def addCPWStraight(self, width, gap, start, end):
        ''' Adds a coplanar waveguide with the specified width and gap from start to end'''
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
        self.prevAngle = theta

    def rotateAndWritePoint(self,theta,x,y,pivot):
        ''' Rotates the specified point (x,y) by an angle theta
            around the pivot and write the result to the script'''
        x_rot = math.cos(theta)*(x - pivot[0]) \
            - math.sin(theta)*(y - pivot[1]) + pivot[0]
        y_rot = math.sin(theta)*(x - pivot[0])  \
            + math.cos(theta)*(y - pivot[1]) + pivot[1]
        self.script.write("%f,%f\n" \
            % (x_rot, y_rot))

    def getDisplacementAndAngle(self, start, end):
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
        ''' Adds a coplanar waveguide with a linear ramp'''
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
        self.prevAngle = theta

    def addCPWAngBend(self, width, gap, radius, angle, start, startAngle):
        # TODO
        pass

