from moeadv.moeadv import RandomUniform
from moeadv.moeadv import Decision
import random

def test_random_uniform():
    for ndv in range(1,20):
        for aa in range(10):
            decisions = list()
            for _ in range(ndv):
                name = ""
                lower = random.normalvariate(0,1)
                upper = lower + random.random()
                delta = 0.1 * upper - lower
                decisions.append(Decision(name, lower, upper, delta))
            doe = RandomUniform(decisions)
            for bb in range(100):
                sample = doe.next_sample()
                for xx, dd in zip(sample, decisions):
                    if xx < dd.lower:
                        raise Exception("xx {} too low dd {}".format(xx, dd))
                    if xx > dd.upper:
                        raise Exception("xx {} too high dd {}".format(xx, dd))

