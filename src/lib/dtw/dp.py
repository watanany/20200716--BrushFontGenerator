#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt, isinf

class DP(object):
    u"""\
    DPマッチングを行うクラス
    参照データのリストとテストデータを事前に格納する必要がある。
    各データはXY座標のリスト、もしくはそれに近いオブジェクトである必要がある
    """
    
    # 枝のリスト(REF, TEST)のタプル
    # 根_ref - REF, 根_test - TEST で葉(端点)と節点が得られる
    B = [
        [(0, 0), (1, 0)],
        [(0, 0), (1, 1)],
        [(0, 0), (1, 2)],
    ]

    # DPW用の枝リスト
    B_DPW = [
        [(0, 0), (1, 1)],
        [(0, 0), (1, 0), (2, 1)],
        [(0, 0), (0, 1), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (3, 1)],
        [(0, 0), (0, 1), (0, 2), (1, 3)],
    ]

    def __init__(self, weight):
        self.load_weight(weight)
        self.refs = None
        self.test = None
        self.DPTable = None
        self.min_id = None
        self.current_min_branch = None

        if 'MODE_DPW' in self.weight:
            self.B = self.B_DPW
            
    def load_refs(self, refs):
        u'参照ベクトルのリストをセットする: refs:=XY座標のリストを一つまたは複数収めたリスト'
        self.refs = []

        for ref in refs:
            self.refs.append([])
            for point in ref:
                self.refs[-1].append(list(point))
        
        return self

    def load_test(self, test):
        u'テストデータベクトルをセットする: test:=XY座標のリスト'
        self.test = []

        for point in test:
            self.test.append(list(point))
            
        return self
    
    def load_weight(self, weight):
        u'局所距離を計算するための重みを決定する'
        self.weight = dict(weight)
        return self
        
    def starting(self, ox, oy):
        u'参照ベクトルのリストとテストベクトルの開始点を引数の場所に移動させる'
        # 参照ベクトル群を移動させる
        for refdata_id, ref in enumerate(self.refs):
            dx = ox - ref[0][0]
            dy = oy - ref[0][1]

            for i, point in enumerate(ref):
                point[0] = point[0] + dx
                point[1] = point[1] + dy
                
        dx = ox - self.test[0][0]
        dy = oy - self.test[0][1]

        # テストベクトルを移動させる
        for i, point in enumerate(self.test):
            x = point[0] + dx
            y = point[1] + dy
            self.test[i] = (x, y)

        return self

    def match(self):
        u'DP Matchingを行い、データを内部フィールドに格納する'
        min_id = None
        min_dist = float('inf')
        
        test = self.test
        self.DPTable = []

        # 全ての参照ごとにテストデータと比較していく
        for refdata_id, ref in enumerate(self.refs):
            # DPW用の変数
            self.current_min_branch = None

            # コスト計算用に len(ref) x len(test) の二次元リストを作り、無限で初期化する
            cost = [[float('inf') for j in range(len(test))] for i in range(len(ref))]
            cost[0][0] = self.local_distance(refdata_id, 0, 0)
            
            # 全ての点を比較
            for i in range(1, len(ref)):
                for j in range(len(test)):
                    min_cost = float('inf')
                    min_branch = None

                    # 最もコストが小さくなる枝を見つける
                    for branch in self.B:
                        leaf = branch[-1]
                        if (i - leaf[0] >= 0) and (j - leaf[1] >= 0):
                            c = cost[i - leaf[0]][j - leaf[1]]
                            if c < min_cost:
                                min_cost = c
                                min_branch = branch

                    # コストテーブルを更新
                    self.current_min_branch = min_branch
                    cost[i][j] = min_cost + self.local_distance(refdata_id, i, j)

            # 参照ごとにコストテーブルを格納していく
            self.DPTable.append(cost)

            # DP距離が既存の距離よりも短い場合更新する
            dist = cost[-1][-1]
            if dist < min_dist:
                min_id = refdata_id
                min_dist = dist

        self.min_id = min_id
        self.min_dist = min_dist

        return self
        
    def dp_distance(self, refdata_id):
        u'計算されたDP距離を返す'
        return self.DPTable[refdata_id][-1][-1]

    def backtrack(self, refdata_id):
        u'最小コストとなるDP経路を返す'
        cost = self.DPTable[refdata_id]
        i = len(cost) - 1
        j = len(cost[i]) - 1

        if isinf(cost[i][j]):
            return None
        else:
            path = [(i, j)]

            while True:
                # 枝の葉ごとのコストを格納する
                min_cost = float('inf')
                min_leaf = None
                for branch in self.B:
                    leaf = branch[-1]
                    if i - leaf[0] >= 0 and j - leaf[1] >= 0:
                        if cost[i - leaf[0]][j - leaf[1]] < min_cost:
                            min_cost = cost[i - leaf[0]][j - leaf[1]]
                            min_leaf = leaf
                            
                # 最小のコストとなる葉を求め、次の対応点を求める
                if min_leaf is not None:
                    j = j - min_leaf[1]
                    i = i - min_leaf[0]
                    path.append((i, j))
                else:
                    break

            return path[::-1]


    def local_distance(self, refdata_id, ref_id, test_id):
        u'重み付きで局所距離を計算する'
        d = {}
        if 'MODE_XY' in self.weight:
            d['MODE_XY'] = self.local_distance_XY(refdata_id, ref_id, test_id)
        if 'MODE_DV' in self.weight:
            d['MODE_DV'] = self.local_distance_DV(refdata_id, ref_id, test_id)
        if 'MODE_DPW' in self.weight:
            d['MODE_DPW'] = self.local_distance_DPW(refdata_id, ref_id, test_id)

        dist = 0
        for mode, w in self.weight.items():
            dist += w * d[mode]

        return dist
    
    def local_distance_XY(self, refdata_id, ref_id, test_id):
        u'XY座標用の局所距離を計算し返す'
        ref = self.refs[refdata_id]
        x1, y1 = self.refs[refdata_id][ref_id][0:2]
        x2, y2 = self.test[test_id][0:2]

        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def local_distance_DV(self, refdata_id, ref_id, test_id):
        u'方向ベクトル(Directional Vector)用の局所距離を計算し返す'
        ref = self.refs[refdata_id]
        test = self.test
        px1, py1 = ref[ref_id][0:2]
        px2, py2 = test[test_id][0:2]

        if ref_id + 1 >= len(ref) or test_id + 1 >= len(test):
            return sqrt((px2 - px1) ** 2 + (py2 - py1) ** 2)
        else:
            nx1, ny1 = ref[ref_id + 1][0:2]
            nx2, ny2 = test[test_id + 1][0:2]
            dx1, dy1 = (nx1 - px1, ny1 - py1)
            dx2, dy2 = (nx2 - px2, ny2 - py2)
        
            return sqrt((dx1 - dx2) ** 2 + (dy1 - dy2) ** 2)
    
    def local_distance_DPW(self, refdata_id, ref_id, test_id):
        u'DPWマッチング用の局所距離を計算し返す'
        branch = self.current_min_branch
        ref = self.refs[refdata_id]
        test = self.test

        if branch is None:
            dist = self.local_distance_XY(refdata_id, ref_id, test_id)
        else:
            nodes, leaf = branch[:-1], branch[-1]

            i = ref_id - leaf[0]
            j = test_id - leaf[1]
            dx = ref[i][0] - test[j][0]
            dy = ref[i][1] - test[j][1]

            dist = 0
            for node in nodes:
                i = ref_id - node[0]
                j = test_id - node[1]
                x = (test[j][0] + dx) - ref[i][0]
                y = (test[j][1] + dy) - ref[i][1]
                dist += sqrt(x * x + y * y)
                
        return dist

