#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
from functools import partial
from sign.loader import Loader
from sign.signature import Signature

class MyLoader(Loader):
    def __init__(self, sampling=True, *args, **kwds):
        interval = sqrt(2)
        threshold = sqrt(2)

        order = [
            partial(Signature.normalize_with_signature_domain, width=256, height=256),
            partial(Signature.liner_interpolate, interval=interval),
            partial(Signature.feature_sample, threshold=threshold),
            partial(Signature.normalize_with_signature_domain, width=1.0, height=1.0),
            self.change_coordsys,
        ]

        if not sampling:
            order = order[3:]
        else:
            order = [order[0]] + order[2:]    ### test ###

        super(MyLoader, self).__init__(order, *args, **kwds)

    @staticmethod
    def change_coordsys(sign):
        u'文字データの座標系を変換する'
        for stroke in sign:
            for point in stroke:
                point[1] = 1.0 - point[1]

