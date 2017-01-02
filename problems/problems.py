"""
Test problems.
"""
from math import pi
from math import sin
from math import cos
from array import array # no numpy???
import random

def make_matrix(ndv):
    """
    this is defined as a function in a function because I want
    the locals to go out of scope and not get captured by the
    rotate function I'm going to return
    """
    matrix = [array('d', range(ndv)) for _ in range(ndv)]
    # generate a random matrix (per Iorio 2006)
    for ii in range(ndv):
        for jj in range(ndv):
            matrix[ii][jj] = random.normalvariate(0, 1)
    # Gram–Schmidt orthonormalization per Wikipedia
    # (Iorio's Algorithm 1 wasn't working for me)
    for ii, uu in enumerate(matrix):
        length = sum(x**2 for x in uu)**0.5
        for jj in range(ndv):
            uu[jj] = uu[jj] / length
        # uu is now normalized
        for vv in matrix[ii+1:]:
            dot = sum(xx*yy for xx, yy in zip(uu, vv))
            # projection of vv along uu
            projection = [dot * x for x in uu]
            for jj in range(ndv):
                vv[jj] = vv[jj] - projection[jj]
            # vv is now orthogonal to uu
    # Because it's orthonormal, the matrix is now a rotation.
    # The use of the normal variate is supposed to distribute
    # the rotation evenly on the hypersphere, but I really have
    # no idea!
    return matrix

def uniform_random_dv_rotation(ndv):
    """
    construct a uniform rotation matrix for the decision
    variables.
    The matrix is randomly generated but there is no guarantee
    that it has any particular distribution.
    Returns a function that applies the rotation.
    """
    matrix = make_matrix(ndv)
    def rotate(xx):
        yy = [0 for _ in xx]
        for ii in range(ndv):
            for jj in range(ndv):
                yy[ii] += matrix[ii][jj] * xx[jj]
        return yy
    return rotate

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

def dtlz2_rotated(ndv, nobj):
    rotate = uniform_random_dv_rotation(ndv)
    straight_dtlz2 = dtlz2(ndv, nobj)
    scale = ndv ** -0.5
    def evaluate(xx):
        # transform x into range -0.5 to 0.5 from 0 to 1
        shifted = [t - 0.5 for t in xx]
        rotated = rotate(shifted)
        # Now transform back into range 0 1
        unshifted = [t + 0.5 for t in rotated]
        # And scale down by the square root of n to keep within the
        # domain.  This will probably make it impossible to cover the whole
        # pareto front.
        scaled = [t*scale for t in unshifted]
        print(scaled)
        assert(all(s >= 0 for s in scaled))
        assert(all(s <= 1 for s in scaled))
        return straight_dtlz2(scaled)
    return evaluate
