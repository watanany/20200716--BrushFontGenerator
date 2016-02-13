#!/usr/bin/env python
# -*- coding: utf-8 -*-
from droplet import *
from brush import *


def transform(v, mat):
    u"ベクトル[v]に対して行列[mat]を使ってアフィン変換を行う"
    v = np.array([v[0], v[1], 1])
    m = np.dot(v, mat)
    return m.A1[0:2]


