#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import degrees
from pyglet.gl import *


class ShinBrush(object):
    def __init__(self):
        self.point = None
    
    def update(self, point):
        self.point = point
        self.point

    def draw(self):
        if self.point[2] != 0:
            c = (1.0 - self.point[2]) * 0.3
            glColor4d(c, c, c, 1.0)

            glPushMatrix()
            glTranslated(self.point[0], self.point[1], 0.0)
            glScaled(self.point[2], self.point[2], 0.0)
            glScaled(0.050, 0.050, 0.0)
            glRotated(self.point[3] / 10 - 90 + 20, 0, 0, 1)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2d(0.0, 0.8)
            glVertex2d(0.4, 0.7)
            glVertex2d(0.5, 0.0)
            glVertex2d(0.4, -1.0)
            glVertex2d(0.0, -2.0)
            glVertex2d(-0.4, -2.5)
            glVertex2d(-0.9, -2.7)
            glVertex2d(-1.4, -2.7)  # bottom of model
            glVertex2d(-1.8, -2.4)
            glVertex2d(-2.0, -2.0)
            glVertex2d(-2.1, -1.4)
            glVertex2d(-1.9, -0.5)
            glVertex2d(-1.5, 0.1)
            glVertex2d(-1.0, 0.5)
            glEnd()
            glPopMatrix()

    @classmethod
    def get_brush(cls, w, h, a=1.0):
        return ShinBrush()
