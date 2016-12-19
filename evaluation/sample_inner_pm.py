di = 5
x_lower = 0
x_upper = 1
from moeadv.operators import pm_inner
operator = pm_inner(0, 1, di)
from random import random

nbins = 100

import time
for xx in range(11):
    print("----")
    bins = dict([(x,0) for x in range(nbins+1)])
    x_parent = 0.1 * xx
    for _ in range(100000):
        x_child = operator(x_parent)
        the_bin = int(x_child * nbins)
        bins[the_bin] += 1

    for the_bin in range(nbins+1):
        print(bins[the_bin])

    time.sleep(0.3)
