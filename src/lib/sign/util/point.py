#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

def liner_interpolate(p0, p1, interval):
    dp = p1 - p0
    dist = np.linalg.norm(dp)

    result = []
    step = 0
    while step < dist:
        p = p0 + ((dp / dist) * step)
        result.append(p)
        step += interval
    result.append(p1)

    return np.array(result)
