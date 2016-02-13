#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from math import sqrt, sin, cos, pi, atan2
from numbers import Number
from collections import Iterable


def tangent_points(r1, r2, h):
    u'２つの円の共通接線の接点を返す'
    # 円①の接点を計算する
    x1 = (-r1 * r2 + r1 ** 2) / h
    y1 = sqrt(r1 ** 2 - x1 ** 2)
    x1 -= h

    # 円②の接点を計算する
    x2 = (r1 * r2 - r2 ** 2) / h
    y2 = sqrt(r2 ** 2 - x2 ** 2)

    return (x1, y1), (x2, y2)


def droplet_func(r1, r2, h):
    u'ドロップレットの形を定義する関数'
    (x1, y1), (x2, y2) = tangent_points(r1, r2, h)

    def f1(x, ndigits=6):
        if -h - r1 <= x < x1:
            return sqrt(round(r1 ** 2 - (x + h) ** 2, ndigits))
        elif x1 <= x < x2:
            return (r2 ** 2 - x2 * x) / y2
        elif x2 <= x <= r2:
            return sqrt(round(r2 ** 2 - x ** 2, ndigits))
        else:
            raise ValueError('Domain error')

    def f2(x):
        # f1をNumberとIterable両方に対応できるように拡張する
        if isinstance(x, Number):
            return f1(x)
        elif isinstance(x, Iterable) and all(isinstance(r, Number) for r in x):
            res = []
            for r in x:
                res.append(f1(r))
            return np.array(res)
        else:
            raise TypeError('Not implemented for this type: {}'.format(type(x)))
                
    return f2



def droplet(r1, r2, h, num):
    u'ドロップレットを実際にnum 個サンプリングし返す'
    f = droplet_func(r1, r2, h)
    x = np.linspace(-h - r1, r2, num=(num / 2))

    res = []
    res += zip(x, f(x))
    res += zip(x, -f(x))[::-1]
    
    return np.array(res), {}



    
    
# def droplet2(r1, r2, h, num):
#     u'ドロップレットを実際にnum 個サンプリングし返す'
#     f = droplet_func(r1, r2, h)
#     x = np.linspace(-h, r2, num=(num / 2))

#     res = []
#     res += zip(x, f(x))
#     res += zip(x, -f(x))[::-1]
    
#     return np.array(res), {}





# def droplet(d1, d2, h, n_digits=6):
#     u'２つの円で構成されるドロップレット標準モデルをXY座標化し返す'

#     # TODO: 関数の整理
#     # TODO: エラーの条件の設定
    
#     # 円の半径を計算する
#     r1 = d1 / 2.0
#     r2 = d2 / 2.0

#     # 前提条件の宣言
#     assert d1 >= d2
    
#     # 円に接する直線の関数および円の関数
#     f = lambda c, d, x: (r2 ** 2 - c * x) / d
#     c1 = lambda x: sqrt(round(r1 ** 2 - (x + h) ** 2, n_digits))
#     c2 = lambda x: sqrt(round(r2 ** 2 - x ** 2, n_digits))


#     # if r1 >= r2 + h:
#     #     space_x = []
#     #     space_y = []
#     #     tmp = np.linspace(-h - r1, -h + r1, num=10).tolist()
#     #     space_x += tmp
#     #     space_y += [-c1(x) for x in tmp]
#     #     return np.array(zip(space_x, space_y)), {'area': r1 * r1 * pi, 'tangent_points': None}

#     # 円①と円②の共通接線が通る円上の点を計算する
#     a = (-r1 * r2 + r1 ** 2) / h
#     b = sqrt(r1 ** 2 - a ** 2)
#     a -= h

#     c = (r1 * r2 - r2 ** 2) / h
#     d = sqrt(r2 ** 2 - c ** 2)

#     if d == 0:
#         raise ZeroDivisionError()

#     # ドロップレットの座標を計算し格納していく
#     xy = []

#     # 円①
#     space_x = []
#     space_y = []
#     tmp = np.linspace(a, -h, num=10).tolist()
#     space_x += tmp
#     space_y += [-c1(x) for x in tmp]

#     tmp = np.linspace(-h, (-h - r1), num=10).tolist()
#     space_x += tmp
#     space_y += [-c1(x) for x in tmp]
    
#     tmp = np.linspace(-h - r1, -h, num=10).tolist()
#     space_x += tmp
#     space_y += [c1(x) for x in tmp]

#     tmp = np.linspace(-h, a, num=10).tolist()
#     space_x += tmp
#     space_y += [c1(x) for x in tmp]

#     xy += zip(space_x, space_y)
    
#     # 上の接線
#     space_x = np.linspace(a, c, num=10)
#     space_y = [f(c, d, x) for x in space_x]
#     xy += zip(space_x, space_y)

#     # 円②
#     space_x = np.linspace(c, r2, num=10)
#     space_y = [c2(x) for x in space_x]
#     xy += zip(space_x, space_y)
    
#     space_x = np.linspace(r2, c, num=10)
#     space_y = [-c2(x) for x in space_x]
#     xy += zip(space_x, space_y)
    
#     # 下の接線
#     space_x = np.linspace(c, a, num=10)
#     space_y = [f(c, -d, x) for x in space_x]
#     xy += zip(space_x, space_y)

#     # ドロップレットの面積を求めるための円と接線の積分関数
#     def area_c1(from_, to):
#         def g(x):
#             t = sqrt(round(r1 ** 2 - (x + h) ** 2, n_digits))
#             return (1 / 2.0) * ((x + h) * t + r1 ** 2 * atan2(x + h, t))

#         return g(to) - g(from_)

#     def area_c2(from_, to):
#         def g(x):
#             t = sqrt(round(r2 ** 2 - x ** 2, n_digits))
#             return (1 / 2.0) * (x * t + r2 ** 2 * atan2(x, t))
            
#         return g(to) - g(from_)

#     def area_f(from_, to):
#         def g(x):
#             return (-c / (2.0 * d)) * x ** 2 + (r2 / d) * x
            
#         return g(to) - g(from_)

#     xy = feature_sample(xy, r2 / 10.0)
#     xy = np.array(xy)
        
#     info = {
#         'tangent_points': np.array([
#             [(a, b), (a, -b)],
#             [(c, d), (c, -d)],
#         ]),
#         'area': 2.0 * (area_c1(-h - r1, a) + area_c2(c, r2) + area_f(a, c)),
#     }
    
#     return xy, info

