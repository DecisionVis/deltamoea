"""
Test problems.
"""
from math import pi
from math import sin
from math import cos
import random

def uniform_random_dv_rotation(ndv):
    """
    construct a uniform rotation for the decision variables.
    Based on iorio 2006.
    """

    """
    Quoting iorio 2006:
    R is an m \times m rotation matrix.  N(0,1) is the normal
    distribution with mean 0 and variance 1.

    for i = 0 to m do (rows)
        for j = 0 to m do (columns)
            R_{ij} = N(0,1)
        end for
        for j = 0 to m do
            R_{ij} = R_{ij} / ||R_i||
        end for
        \vec{d} = R_i
        for all j s.t. 0 <= j <= i
            n = ||\vec{d}||
            p = \vec{d} \dot R_j
            for k = 0 to m do
                d_k = (d_k - p \dot R_{jk}) / (n^2)
            end for
        end for
        R_i = \vec{d} / ||\vec{d}||
    end for
    """

def dtlz2(ndv, nobj):
    """
    return an instance of dtlz2 with the requested number of
    decision variables and objectives.
    """
    def evaluate(xx):
        """
        xx (indexable): decision variables x_j
        x_j (float 0<=x_j<=1): decision variable
        j = i-1 for the purposes of translation from Deb et al.
            because Python counts zero.
        """
        # To ease translation, always produce jj from ii.
        gg = sum((xx[jj] - 0.5)**2.0
                 for jj in (ii-1 for ii in range(nobj, ndv+1)))
        gplus1 = 1.0 + gg
        scaled_pi_over_2 = [x * pi * 0.5 for x in xx]
        ff = list()
        f1 = gplus1
        for ii in range(1, nobj):
            jj = ii - 1
            scaled = scaled_pi_over_2[jj]
            f1 = f1 * cos(scaled)
        ff.append(f1)
        for ii in range(2, nobj):
            fi = gplus1
            for i2 in range(1, nobj + 1 - ii):
                jj = i2 - 1
                scaled = scaled_pi_over_2[jj]
                fi = fi * cos(scaled)
            i2 = nobj
            jj = i2 - 1
            fi = fi * sin(scaled)
            ff.append(fi)
        ii = nobj
        jj = ii - 1
        scaled = scaled_pi_over_2[jj]
        fM = gplus1 * sin(scaled)
        ff.append(fM)
        return ff
    return evaluate
