#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
from pyglet.gl import *
from droplet.brush import Brush
from droplet.simplebrush import SimpleBrush

class MyBrush(Brush):
    def __init__(self, *args, **kwds):
        super(MyBrush, self).__init__(*args, **kwds)
        #self.N = 9
        #self.rate = [1.0 / self.N] * self.N
        
    def draw(self):
        u'現在の座標にドロップレットモデル(毛筆)を描く'        
        # ドロップレットモデルを描く
        c = 0.1
        glColor4d(c, c, c, 1.0)

        for model in self:
            for droplet in model:
                glBegin(GL_POLYGON)
                #glBegin(GL_LINES)
                for x, y in droplet:
                    glVertex2d(x, y)
                glEnd()

        # glBegin(GL_POLYGON)
        # for x, y in self.hull():
        #     glVertex2d(x, y)
        # glEnd()

    @classmethod
    def get_brush(cls, width, height, a=1.0):
        b = sqrt(width * width + height * height) / 1.2
        brush = cls({
            'length': 0.15 * a * b,
            'D': 0.1 * a * b,
            'humidity': 0.5,
            'k': 0.5,
            
            'hair_number': 30,
            'pigment': 0.8, 
            'threshold': {
                ((1, 2), 3): 0.8,
                ((3, 4), 5): 0.8,
            },
            'p_tip': [0.8, 0.2],
        })

        return brush
        






# class MyBrush(ShinBrush):
#     @classmethod
#     def get_brush(cls, width, height):
#         brush = cls()
#         return brush
        
    
