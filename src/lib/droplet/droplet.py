#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from math import sin, cos, radians
from util import droplet, transform


class Droplet(object):
    u'単一のドロップレットモデルを再現するクラス'
    def __init__(self, d1, d2, h, forming=False):
        super(Droplet, self).__init__()
        self.d1 = float(d1)
        self.d2 = float(d2)
        self.h = float(h)
        self._shape, self.info = None, None
        self.matrix = np.mat(np.identity(3))
        self.num = 128

        if forming:
            self.form_droplet(num=self.num)

    def __len__(self):
        return len(self._shape)
        
    def __getitem__(self, indices):
        return self.shape[indices]

    def __iter__(self):
        return iter(self.shape)

    def form_droplet(self, num):
        u'実際に座標数 num でドロップレットを形成し内部フィールドに格納する'
        self._shape, self.info = droplet(self.r1, self.r2, self.h, num=num)
        
    def translate(self, x, y):
        u'ドロップレットを(x, y)分だけ平行移動する'
        self.matrix *= np.matrix([[1, 0, 0],
                                  [0, 1, 0],
                                  [x, y, 1]])
        
    def rotate(self, angle, x, y):
        u'ドロップレットを(x, y)を中心としてθ分だけ回転させる'
        # 回転の中心を原点に移動させる
        self.translate(-x, -y)
        
        # 原点を中心に回転させる
        a = radians(angle)
        self.matrix *= np.matrix([[cos(a), sin(a), 0],
                                  [-sin(a), cos(a), 0],
                                  [0, 0, 1]])
        
        # 回転の中心を元の位置に戻す
        self.translate(x, y)
        
    def redefine(self, d1, d2, h):
        u'ドロップレットの形を再定義する。平行移動・回転量は変わらない'
        self.d1 = d1
        self.d2 = d2
        self.h = h
        self._shape, self.info = droplet(d1, d2, h, num=self.num)

    @property
    def r1(self):
        return self.d1 / 2.0
        
    @property
    def r2(self):
        return self.d2 / 2.0

    @property
    def center1(self):
        center = np.array([-self.h, 0.0, 1.0])
        center = np.dot(center, self.matrix)
        return center.A1[0:2]

    @property
    def center2(self):
        center = np.array([0.0, 0.0, 1.0])
        center = np.dot(center, self.matrix)
        return center.A1[0:2]

    @property
    def area(self):
        return self.info['area']

    @property
    def shape(self):
        u'行列演算によって平行移動・回転を行ったXY座標の numpy.array を返す'
        shape = []
        for v in self._shape:
            v = transform(v, self.matrix)
            shape.append(v)
        return np.array(shape)
        


