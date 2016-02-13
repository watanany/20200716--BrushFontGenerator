#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from dropletmodel import DropletModel
from util import convert_wintab_azimuth, convert_wintab_altitude
from abcbrush import AbstractBrush


class SimpleBrush(AbstractBrush):
    def __init__(self, param):
        # 前提条件の確認
        param_names = ['length', 'k', 'D', 'humidity']
        assert all(p_name in param for p_name in param_names)
        assert all(0 <= param[p_name] <= 1 for p_name in param if p_name in ['k', 'humidity'])
        
        for p_name in param_names:
            setattr(self, p_name, param[p_name])
            
        self.param = param
        self.point = None
        self.pre_layer = []
        self.layer = []
        self.rate = [1.0]
        
    def __getitem__(self, indices):
        return self.layer[indices]
        
    def __iter__(self):
        return iter(self.layer)

    def update(self, point):
        u'ドロップレットモデルのパラメータを計算する'
        x, y, pressure, azimuth, altitude, time = point

        # 一つ前の座標値とレイヤーを保存する
        self.pre_layer = self.layer
        self.pre_point = self.point

        # ペンタブ用の角度をドロップレットモデル用の角度に変換する
        self.point = np.array(point)
        self.point[3] = convert_wintab_azimuth(self.point[3])
        self.point[4] = convert_wintab_altitude(self.point[4])

        if pressure != 0:
            d1 = self.D * pressure
            d2 = d1 * self.k * self.humidity
            h = self.length * pressure

            # ドロップレットモデルを更新する
            self.layer = [
                DropletModel(d1, d2, h, self.rate),
            ]

            # ドロップレットモデルの平行移動・回転を行う
            for model in self.layer:
                model.rotate(self.point[3], 0, 0)
                model.translate(x, y)
        else:
            self.layer = []

    def hull(self):
        u'hull-rule'
        def f(model):
            # [0] min, [1] max
            x = []
            y = []
            for droplet in model:
                for _x, _y in droplet:
                    x.append(_x)
                    y.append(_y)

            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            return [
                [min_x, y[x.index(min_x)]],
                [max_x, y[x.index(max_x)]],
                [x[y.index(min_y)], min_y],
                [x[y.index(max_y)], max_y],
            ]

        if len(self.pre_layer) != 0 and len(self.layer) != 0:
            p_list = f(self.pre_layer[0])
            q_list = f(self.layer[0])

            for p in p_list:
                yield p
                for q in q_list:
                    yield q
