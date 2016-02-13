#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import numpy as np
import util.stroke as st
from math import sqrt
from copy import deepcopy
from itertools import permutations
from collections import OrderedDict
from util.signature import *
from header import Header


class Signature2D(object):
    def __init__(self, path=None, data=None):
        self.header = Header()
        self.data = None
        self.path = None
        
        if path is not None:
            self.load_from_file(path)
        elif data is not None:
            self.load_from_data(data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, indices):
        return self.data[indices]

    def __iter__(self):
        return iter(self.data)

    def __copy__(self):
    	return deepcopy(self)

    def __deepcopy__(self, memo):
        sign = self.__class__()
        sign.header = deepcopy(self.header, memo)
        sign.data = deepcopy(self.data, memo)
        sign.path = deepcopy(self.path, memo)
        return sign

    def load_from_file(self, path):
        path = os.path.abspath(path)
        with codecs.open(path, 'r', 'utf-8') as r:
            # ヘッダー情報の読み込み
            buffer = []
            for line in r:
                line = line.rstrip()
                if line == '':
                    break
                else:
                    buffer.append(line)

            header = Header(buffer='\n'.join(buffer))

            # ボディ情報(座標リスト)の読み込み
            data = []
            stroke = []
            for line in r:
                line = line.rstrip()
                if line == '':
                    if len(stroke) != 0:
                        data.append(np.array(stroke))
                        stroke = []
                else:
                    point = [float(_) for _ in line.split()]
                    stroke.append(np.array(point))

            if len(stroke) != 0:
                data.append(np.array(stroke))
                stroke = []

        # 情報をプロパティにセットする
        self.header = header
        self.data = data
        self.path = path

    def load_from_data(self, data):
        self.header = Header()
        self.path = None
        self.data = []

        for stroke in data:
            if len(stroke) != 0:
                stroke = np.array(stroke)
                self.data.append(stroke)

    def make_header_from_data(self):
        header = Header()
        header['Dimension'] = 2
        header['Data-Type'] = ('X', 'Y')
        header['Stroke-Count'] = self.stroke_count
        header['Point-Counts'] = [len(stroke) for stroke in self.data]
        return header

    def save_as(self, path):
        with codecs.open(path, 'w', 'utf-8') as w:
            if self.header is not None:
                print >>w, self.header

                for stroke in self.data:
                    for point in stroke:
                        print >>w, '\t'.join(str(p) for p in point)
                    print >>w, ''

        return self

    def liner_interpolate(self, interval):
        self.data = liner_interpolate(self.data, interval)
        return self
        
    def n_sample(self, n_points):
        self.data = n_sample(self.data, n_points)
        return self

    def feature_sample(self, threshold):
        self.data = feature_sample(self.data, threshold)
        return self

    def normalize_with_canvas_size(self, width=1.0, height=1.0):
        if 'Canvas-Size' not in self.header:
            raise KeyError("Signature's header must have 'Canvas-Size' to normalize")
        
        canvas_w, canvas_h = self.header['Canvas-Size']
        x = self.merged_stroke[:, 0]
        y = self.merged_stroke[:, 1]

        min_x = x.min()
        min_y = y.min()
        
        for i, stroke in enumerate(self.data):
            for j, point in enumerate(stroke):
                point[0] = (point[0] - min_x) / canvas_w * width
                point[1] = (point[1] - min_y) / canvas_h * height

    def normalize_with_signature_domain(self, width=1.0, height=1.0):
        x = self.merged_stroke[:, 0]
        y = self.merged_stroke[:, 1]
        w = x.max() - x.min()
        h = y.max() - y.min()

        min_x = x.min()
        min_y = y.min()

        for i, stroke in enumerate(self.data):
            for j, point in enumerate(stroke):
                point[0] = (point[0] - min_x) / w * width
                point[1] = (point[1] - min_y) / h * height

    @property
    def width(self):
        x = self.merged_stroke[:, 0]
        return max(x) - min(x)

    @property
    def height(self):
        y = self.merged_stroke[:, 1]
        return max(y) - min(y)

    @property
    def rectangle(self):
        x = self.merged_stroke[:, 0]
        y = self.merged_stroke[:, 1]
        r = [[None, None],
             [None, None]]
        r[0][0] = ( x.min(), y.min() )
        r[0][1] = ( x.max(), y.min() )
        r[1][0] = ( x.min(), y.max() )
        r[1][1] = ( x.max(), y.max() )
        return r

    @property
    def merged_stroke(self):
        result = []
        for stroke in self.data:
            for p in stroke:
                result.append(p)
        return np.array(result)

    @property
    def stroke_count(self):
        return len(self.data)

    @property
    def point_counts(self):
        return [len(stroke) for stroke in self.data]

    @property
    def dim(self):
        return len(self.data[0])


        


def test():
    import matplotlib.pyplot as plt
    path = u'C:/Users/m5171146/git/BrushDrawer/generator/data/XY/HIRAKANA/12379.sign'
    sign = Signature2D(path=path)
    sign.normalize(256, 256)
    sign.liner_interpolate()
    sign.feature_sample(1.0)

    x = sign.merged_stroke[:, 0]
    y = sign.merged_stroke[:, 1]
    plt.plot(x, -y, '.')
    plt.show()


if __name__ == '__main__':
    test()
