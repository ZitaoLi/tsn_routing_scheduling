import math

import numpy as np


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def lcm_d(a, b):
    # return a * b / math.gcd(a, b)
    return b / math.gcd(a, b) * a


def lcm_m(x):
    a = 1
    for i in range(len(x)):
        t = math.gcd(int(a), x[i])
        a = a / t * x[i]
    return a
