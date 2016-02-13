#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DPW(DP):
    B_DPW = [
        [(0, 0), (1, 1)],
        [(0, 0), (1, 0), (2, 1)],
        [(0, 0), (0, 1), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (3, 1)],
        [(0, 0), (0, 1), (0, 2), (1, 3)],
    ]
    
    def __init__(self, weight):
        pass
