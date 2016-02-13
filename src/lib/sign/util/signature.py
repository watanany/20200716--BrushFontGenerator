#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import numpy as np
import stroke as st
from math import sqrt
from copy import deepcopy
from itertools import permutations
from collections import OrderedDict


def liner_interpolate(data, interval):
    result = []
    for stroke in data:
        stroke = st.liner_interpolate(stroke, interval)
        result.append(stroke)

    return result


def feature_sample(data, threshold):
    result = []
    for stroke in data:
        stroke = st.feature_sample(stroke, threshold)
        result.append(stroke)

    return result


# def n_sample(data, n_points):
#     result = []
#     for stroke in data:
#         stroke = st.n_sample(stroke, n_points)
#         result.append(stroke)

#     return np.array(result)

    
# def find_correspond(data0, data1):
#     u'対応するストロークを探し、その組み合わせを返す'
    
#     raise NotImplemented()

#     m = len(data0)
#     n = len(data1)
#     assert m >= n, u'[ERROR] 第一引数の画数が第二引数の画数以上である必要があります'

#     # 予め、距離を全て計算しておく
#     dist_table = np.zeros((m, n))
#     for i, stroke0 in enumerate(sign0.data):
#         for j, stroke1 in enumerate(sign1.data):
#             dist_table[i, j] = st.StartingPointFixationMethod(stroke0, stroke1)
    
#     # 全ての組み合わせについて距離を測る
#     P = list(permutations(range(m), n))
#     min_dist = float('inf')
#     min_index = -1
#     for index in range(len(P)):
#         d = 0
#         for i, j in zip(P[index], range(n)):
#             d += dist_table[i, j]
#         if d < min_dist:
#             min_dist = d
#             min_index = index

#     return zip(P[min_index], range(n))






