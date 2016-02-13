#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from copy import deepcopy
from sign.signature import Signature


if len(sys.argv) != 2:
    raise SystemExit()


sign = Signature(sys.argv[1])

plt.subplot(131)
plt.xlim(0, 255)
plt.ylim(255, 0)
plt.plot(sign.merged_stroke[:, 0], sign.merged_stroke[:, 1], 'o')

x = sign.merged_stroke[:, 0]
y = sign.merged_stroke[:, 1]

p = np.array([
    [ x.min(), y[np.where(x == x.min())][0] ],
    [ x[np.where(y == y.max())][0], y.max() ],
    [ x.max(), y[np.where(x == x.max())][0] ],
    [ x[np.where(y == y.min())][0], y.min() ],
    [ x.min(), y[np.where(x == x.min())][0] ],
])

q = np.array([
    [ x.min(), y.min() ],
    [ x.min(), y.max() ],
    [ x.max(), y.max() ],
    [ x.max(), y.min() ],
    [ x.min(), y.min() ],
])

plt.plot(p[:, 0], p[:, 1], 'r--')
plt.plot(q[:, 0], q[:, 1], 'g--')


sign.liner_interpolate(sqrt(2))
plt.subplot(132)
plt.xlim(0, 255)
plt.ylim(255, 0)
plt.plot(sign.merged_stroke[:, 0], sign.merged_stroke[:, 1], 'o')


sign.feature_sample(sqrt(2))
plt.subplot(133)
plt.xlim(0, 255)
plt.ylim(255, 0)
plt.plot(sign.merged_stroke[:, 0], sign.merged_stroke[:, 1], 'o')


plt.show()
