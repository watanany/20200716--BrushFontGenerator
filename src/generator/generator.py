#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, random
import numpy as np
import codecs
from threading import Thread
from copy import deepcopy
from dtw.dp import DP
from myloader import MyLoader
from sign.signature import Signature


class Generator(object):
    def __init__(self):
        self.skels_dir = '../../data/xy/temp'
        self.bs_dir = '../../data/xyp'

        # skels = MyLoader().get_signs(self.skels_dir, show=True)
        # self.skels = []
        # for i in range(100):
        #     index = random.randint(0, len(skels) - 1)
        #     skel = skels.pop(index)
        #     self.skels.append(skel)

        self.skels = MyLoader().get_signs(self.skels_dir, show=True)
            
        self.index = 0
        self.assembles = []
        self.gen_infos = []
        
        # DTW の設定
        self.refs = self.get_strokes(MyLoader(), self.bs_dir)
        self.threshold = 100#0.15

        # 毛筆文字のストロークのリスト
        self.parts = self.get_strokes(MyLoader(sampling=False), self.bs_dir)

    def __getitem__(self, index):
        return self.assembles[index], self.gen_infos[index]
        
    def __iter__(self):
        for sign, gen_info in zip(self.assembles, self.gen_infos):
            yield sign, gen_info

    def __len__(self):
        return len(self.assembles)
        
    def generate(self, skeleton, threshold):
        u'引数で与えられた文字骨格を元に毛筆文字組み立てる'
        gen_info = []
        matched_strokes = []

        dp = DP({'MODE_XY': 1.0})
        dp.load_refs(self.refs)
        
        for i, stroke in enumerate(skeleton):
            gen_info.append({
                'dist': float('inf'),
                'min_id': None,
                'min_path': None,
                'is_added': False,
            })

            # DP マッチング
            min_id = dp.load_test(stroke).starting(0, 0).match().min_id

            if min_id is not None:
                dist = dp.dp_distance(min_id)
                ref = deepcopy(self.parts[min_id])
                path = dp.backtrack(min_id)
                dist = float(dist) / len(path)
                
                gen_info[i]['dist'] = dist
                gen_info[i]['min_id'] = min_id
                gen_info[i]['min_path'] = path
                if dist < self.threshold:
                    # ストロークを文字の形を成すように移動する
                    x, y = ref[:, 0], ref[:, 1]
                    ref[:, 0] = x - x[0] + stroke[0][0]
                    ref[:, 1] = y - y[0] + stroke[0][1]
                    matched_strokes.append(ref)
                    gen_info[i]['is_added'] = True

        sign = Signature(data=matched_strokes)
        sign.header['Character'] = skeleton.header['Character']

        return sign, gen_info

    def generate_all(self):
        u'全ての文字を生成を試みる'
        self.assembles = [None] * len(self.skels)
        self.gen_infos = [None] * len(self.skels)

        thread_list = []
        
        for i in range(len(self.skels)):
            def target(index):
                u'一つの文字を生成するスレッド用関数'
                sign, gen_info = self.generate(self.skels[index], self.threshold)
                self.assembles[index] = sign
                self.gen_infos[index] = gen_info

            # スレッドを生成し文字生成を始める
            thread=  Thread(target=target, args=(i,))
            thread.start()
            thread_list.append(thread)

        # スレッドが終了するまで待つ
        for thread in thread_list:
            thread.join()


    def interfuse(self, skeleton, gen_info, w):
        u'ストローク混合文字を生成する'
        data = []

        # ストローク一本ごとに処理
        for stroke, info in zip(skeleton, gen_info):
            if not info['is_added']:
                continue

            # ストロークの対応点を各リストに格納していく
            ref = self.refs[info['min_id']]
            rp_list = [ref[i] for i, j in info['min_path']]
            tp_list = [stroke[j] for i, j in info['min_path']]

            # 毛筆ストローク・毛筆ストロークの開始点
            part = self.parts[info['min_id']]
            starting_point = part[0]
            data.append([])

            # 対応する座標の間に存在する対応点を計算する
            for rp, rq, tp, tq in zip(rp_list, rp_list[1:], tp_list, tp_list[1:]):
                # 二点間の時間を取得し、その間にある点について処理する
                start_time, end_time = rp[5], rq[5]
                i_list = []
                p_list = []

                # 毛筆文字のストロークの座標をリストに格納する
                for i, p in enumerate(part):
                    if start_time <= p[5] <= end_time:
                        i_list.append(i)
                        p_list.append(p)
                        
                # 一度処理した座標は処理対象から外す
                part = np.delete(part, i_list, axis=0)
                
                # 各座標間の長さの合計(ストロークの長さ)を測る
                length = 0
                for p, q in zip(p_list, p_list[1:]):
                    length += np.linalg.norm(q[0:2] - p[0:2])

                # 混ぜ合わせるべき対応点を計算する
                v = tq - tp
                for i, p in enumerate(p_list):
                    accnorm = 0
                    for q, r in zip(p_list[:i], p_list[1:i]):
                        accnorm += np.linalg.norm(r[0:2] - q[0:2])

                    # 対応点
                    rate = float(accnorm) / length
                    cor = tp + v * rate

                    # 文字の形を成すようにストロークの開始点を合わせる
                    p = deepcopy(p)
                    p[0] = p[0] - starting_point[0] + stroke[0][0]
                    p[1] = p[1] - starting_point[1] + stroke[0][1]

                    # XY座標を混ぜ合わせる
                    p[0:2] = w * p[0:2] + (1 - w) * cor

                    data[-1].append(p)

        sign = Signature(data=data)
        sign.header['Character'] = skeleton.header['Character']

        return sign
                        
    def interfuse_all(self, w):
        u'ストロークを混ぜ合わせる'
        self.assembles = [None] * len(self.skels)
        
        thread_list = []

        for i in range(len(self.skels)):
            def target(index):
                sign = self.interfuse(self.skels[index], self.gen_infos[index], w)
                self.assembles[index] = sign

            thread = Thread(target=target, args=(i,))
            thread.start()
            thread_list.append(thread)

        for thread in thread_list:
            thread.join()

    @staticmethod
    def get_strokes(loader, dir, show=True):
        u'Loaderを使ってディレクトリからストロークを得る'
        signs = loader.get_signs(dir, show=show)
        strokes = []

        for sign in signs:
            for stroke in sign:
                strokes.append(stroke)

        return strokes
