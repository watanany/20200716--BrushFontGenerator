#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import point
from math import sqrt
from scipy.interpolate import splrep, splev

def liner_interpolate(stroke, interval):
    u'ストロークの座標間を等間隔で直線的に補完する'
    if len(stroke) == 1:
        return stroke

    result = []
    for p0, p1 in zip(stroke, stroke[1:]):
        point_list = point.liner_interpolate(p0, p1, interval)
        for p in point_list:
            result.append(p)

    return np.array(result)

def feature_sample(stroke, threshold):
    u'Rammerの方法でサンプリングを行う'
    if len(stroke) <= 2:
        return stroke
        
    index_list = [0, len(stroke) - 1]
    break_flag = False
    
    while True:
        count = 0
        combination = zip(index_list, index_list[1:])
        for i, j in combination:
            x1, y1 = stroke[i][:2]
            x2, y2 = stroke[j][:2]

            # 直線と点との距離を計算する式fを定義する
            if x2 - x1 != 0:
                m = (y2 - y1) / (x2 - x1)
                n = y1 - m * x1
                f = lambda x, y: abs(y - m * x - n) / sqrt(1 + m**2)
            else:
                f = lambda x, y: abs(x - x1)

            # p(x1, y1), q(x2, y2)間の直線から最も遠い点を見つける
            max_dist = 0
            max_index = None

            for k in range(i + 1, j):
                if k not in index_list:
                    x0, y0 = stroke[k][:2]
                    dist = f(x0, y0)

                    if max_dist < dist:
                        max_dist = dist
                        max_index = k

            if max_dist > threshold:
                index_list.append(max_index)
                index_list.sort()
            else:
                count += 1

        if count == len(combination):
            break

    return np.array([stroke[i] for i in index_list])

    

# def vectorize(stroke):
#     u'ストロークをベクトル化する'
#     stroke = stroke - stroke[0]
#     stroke = stroke.reshape((1, -1))
#     stroke = np.squeeze(stroke)
#     return stroke


# def spline_interpolate(stroke, interval):
#     u'ストロークの座標間をスプライン補間する'
#     x = stroke[:, 0]
#     y = stroke[:, 1]
#     f = splrep(x, y, s=0)
#     x = np.arange(x.min(), x.max(), interval)
#     y = splev(x, f, der=0)
#     result = [np.array(tx, ty) for tx, ty in zip(x, y)]
#     return np.array(result)

    
# def n_sample(stroke, n_points):
#     u"""ストロークから引数分サンプリングする。
#         座標数が足りない場合はstretch関数を使用し水増しされた後にサンプリングされる"""
#     result = []
#     stroke = stretch(stroke, n_points)
#     step = float(len(stroke)) / n_points
#     for i in range(n_points):
#         index = int(step * i)
#         result.append(stroke[index])

#     return np.array(result)


# def step_sample(stroke, step):
#     u'ストロークをステップ数ごとにサンプリングする'
#     result = []

#     for i, point in enumerate(stroke):
#         if i % step == 0:
#             result.append(point)

#     return np.array(result)


# def interval_sample(stroke, interval):
#     u'ストロークを等間隔にサンプリングする。座標間を補完した後でないと意味のある値にならない'
#     result = []
#     result.append(stroke[0])
    
#     i = 0
#     while i < len(stroke):
#         dist = 0
#         # i番目の点とi+1番目以降の点について距離を累積していきサンプリング間隔を超えたらサンプリングする
#         for j in range(len(stroke[i+1:])):
#             p = stroke[i]
#             q = stroke[j]
#             norm = np.linalg.norm(p[0:2] - q[0:2])
#             pre_dist = dist
#             dist += norm

#             if dist >= interval:
#                 if abs(dist - interval) <= abs(pre_dist - interval):
#                     i = j
#                 else:
#                     i = j - 1

#                 result.append(stroke[i])                        
#                 break

#     return np.array(result)
    
    
    
# def stretch(stroke, n_points):
#     u'ストロークを水増しする'
#     if len(stroke) == 1:
#         return stroke
    
#     while len(stroke) < n_points:
#         tmp = []

#         for p, q in zip(stroke, stroke[1:]):
#             r = (p + q) / 2.0
#             tmp.append(p)
#             tmp.append(r)
#         tmp.append(stroke[-1])

#         stroke = np.array(tmp)

#     return stroke


# def superimpose(up_stroke, under_stroke):
#     u'ストローク同士がなるべく重なるように平行移動する'
#     assert len(up_stroke) == len(under_stroke), u'[ERROR] ストロークの長さが異なります'
    
#     x0, y0 = up_stroke[:, 0], up_stroke[:, 1]
#     x1, y1 = under_stroke[:, 0], under_stroke[:, 1]

#     dx = x1 - x0
#     dy = y1 - y0
#     xp = float(sum(dx)) / len(dx)
#     yp = float(sum(dy)) / len(dy)

#     result = []
#     for p in up_stroke:
#         x = p[0] + xp
#         y = p[1] + yp
#         p = [x, y] + p[2:].tolist()
#         result.append(np.array(p))

#     return np.array(result)


# def StartingPointFixationMethod(stroke0, stroke1):
#     u'始点fix法でストローク間の距離を測る'
#     if len(stroke0) < len(stroke1):
#         stroke0, stroke1 = stroke1, stroke0
        
#     m = len(stroke0)
#     n = len(stroke1)
    
#     # 参照ストロークの始点までテストストロークを平行移動させる
#     stroke0 += stroke1[0] - stroke0[0]

#     # 座標数が少ない方に合わせて距離を計算する
#     dist = 0
#     for i in range(n):
#         dx = abs(stroke0[i][0] - stroke1[i][0])
#         dy = abs(stroke0[i][1] - stroke1[i][1])
#         print stroke0[i][0], stroke0[i][1]
#         print stroke1[i][0], stroke1[i][1]
#         print
#         dist += (dx + dy)

#     return float(m) / n * dist


