#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import numpy as np
import util.stroke as st
from copy import deepcopy
from util.signature import *
from header import Header


class Signature(object):
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
        u'文字データファイルからデータを読み込む'
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
        u'データリストからデータを読み込む'
        self.header = Header()
        self.path = None
        self.data = []

        for stroke in data:
            if len(stroke) != 0:
                stroke = np.array(stroke)
                self.data.append(stroke)

    def make_header_from_data(self):
        u'現在のデータからヘッダ情報を推定し返す'
        header = Header()
        header['Dimension'] = self.dim
        
        if self.dim == 2:
            header['Data-Type'] = ('X', 'Y')
        elif self.dim == 6:
            header['Data-Type'] = ('X', 'Y', 'Pressure', 'Azimuth', 'Altitude', 'Time(Seconds)')
            
        header['Stroke-Count'] = self.stroke_count
        header['Point-Counts'] = self.point_counts
        return header

    def save_as(self, path):
        u'データをファイルに保存する'
        with codecs.open(path, 'w', 'utf-8') as w:
            if self.header is not None:
                print >>w, self.header

                for stroke in self.data:
                    for point in stroke:
                        print >>w, '\t'.join(str(p) for p in point)
                    print >>w, ''
            else:
                raise RuntimeError(u'ヘッダが構成されていません')

        return self

    def liner_interpolate(self, interval):
        u'直線的に座標間を補完する'
        self.data = liner_interpolate(self.data, interval)
        return self
        
    def n_sample(self, n_points):
        u'データから等間隔に引数分座標を取得する'
        self.data = n_sample(self.data, n_points)
        return self

    def feature_sample(self, threshold):
        u'Rammerの方法でデータをサンプリングする'
        self.data = feature_sample(self.data, threshold)
        return self

    def normalize_with_canvas_size(self, width=1.0, height=1.0):
        u'キャンパスサイズでデータを正規化する'
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
        u'文字の領域に対して正規化を行う'
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
        u'データの横幅'
        x = self.merged_stroke[:, 0]
        return max(x) - min(x)

    @property
    def height(self):
        u'データの縦幅'
        y = self.merged_stroke[:, 1]
        return max(y) - min(y)

    @property
    def merged_stroke(self):
        u'全てのストロークを一つにまとめたストロークを返す'
        result = []
        for stroke in self.data:
            for p in stroke:
                result.append(p)
        return np.array(result)

    @property
    def stroke_count(self):
        u'画数'
        return len(self.data)

    @property
    def point_counts(self):
        u'各ストロークごとの座標数のリスト'
        return [len(stroke) for stroke in self.data]

    @property
    def dim(self):
        u'データの次元'
        dim = set()
        for point in self.merged_stroke:
            dim.add(len(point))

        if len(dim) != 1:
            raise RuntimeError(u'次元の異なるデータを混同しています')
            
        return dim[0]



        

        
