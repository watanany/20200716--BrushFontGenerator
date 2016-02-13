#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from droplet import Droplet
from util import transform

class DropletModel(Droplet):
    u'複数のドロップレットで成り立つモデルを再現するクラス'
    def __init__(self, d1, d2, h, rate):
        super(DropletModel, self).__init__(d1, d2, h, forming=True)
        self.rate = list(rate)
        self.droplets = []

        # 上から順に並べていく
        diameters = [(d1 * w, d2 * w) for w in self.rate]
        height = d1 / 2.0

        for t1, t2 in diameters:
            droplet = Droplet(t1, t2, h, forming=True)
            droplet.translate(0, height - t1 / 2.0)
            height = height - t1
            self.droplets.append(droplet)

    def __len__(self):
        return len(self.droplets)

    def __getitem__(self, indices):
        return self.droplets[indices]

    def __iter__(self):
        p1 = np.array([-self.h, -self.r1])
        p2 = np.array([-self.h, +self.r1])
        x1, y1 = transform(p1, self.matrix)
        x2, y2 = transform(p2, self.matrix)

        if x2 - x1 != 0:
            f = (lambda x: float(y2 - y1) / (x2 - x1) * (x - x1) + y1)
            if self.center2[1] <= f(self.center2[0]):
                g = lambda x, y: y <= f(x)
                h = lambda x, y: y >= f(x)
            elif self.center2[1] >= f(self.center2[0]):
                g = lambda x, y: y >= f(x)
                h = lambda x, y: y <= f(x)

            for droplet in self.droplets:
                yield [(x, y) for x, y in droplet if g(x, y)]

            yield [(x, y) for x, y in self.shape]
        else:
            for droplet in self.droplets:
                for x, y in droplet:
                    yield x, y
        

    def redefine(self, d1, d2, h):
        u'ドロップレットの形を再定義する。平行移動・回転量は変わらない'
        diameters = [(d1 * w, d2 * w) for w in self.rate]

        for i, droplet in enumerate(self.droplets):
            t1, t2 = diameters[i]
            droplet.redefine(t1, t2, h)

    def translate(self, x, y):
        u'ドロップレットを(x, y)分だけ平行移動する'
        super(DropletModel, self).translate(x, y)
        for droplet in self.droplets:
            droplet.translate(x, y)

    def rotate(self, angle, x, y):
        u'ドロップレットを(x, y)を中心としてθ分だけ回転させる'
        super(DropletModel, self).rotate(angle, x, y)
        for droplet in self.droplets:
            droplet.rotate(angle, x, y)

    @property
    def area(self):
        return sum(droplet.area for droplet in self.droplets)
        
    @property
    def center(self):
        cx = (self.r1 - (self.r2 + self.h)) / 2.0
        center = np.array([cx, 0.0])
        return transform(center, self.matrix)

        
