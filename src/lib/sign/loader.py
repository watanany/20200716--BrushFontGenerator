#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from glob import glob
from sign.signature import Signature

class Loader(object):
    def __init__(self, order, recursive=False):
        self.recursive = recursive
        self.order = order
        
    @staticmethod
    def get_pathes(dir, recursive):
        u'ディレクトリから再帰的・非再帰的に文字データのパスのリストを得る'
        result = []
        
        if not recursive:
            result = glob(os.path.join(dir, '*.sign'))
        else:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith('.sign'):
                        path = os.path.join(root, file)
                        result.append(path)

        return result
        
    def get_signs(self, dir, show=False):
        u'パラメータによって文字データのリストを得る'
        result = []

        for path in self.get_pathes(dir, self.recursive):
            if show:
                print path
            sign = Signature(path)
            self.process(sign)
            result.append(sign)

        return result

    def process(self, sign):
        u'文字データを加工する'
        for func in self.order:
            func(sign)
            



