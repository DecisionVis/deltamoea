"""
Test problems.
"""
from math import pi
from math import sin
from math import cos
from array import array # no numpy???
import random

import pprint

def uniform_random_dv_rotation(ndv):
    """
    construct a uniform rotation matrix for the decision
    variables.
    The matrix is randomly generated but there is no guarantee
    that it has any particular distribution.
    Returns a function that applies the rotation.
    """

    def make_matrix():
        """
        this is defined as a function in a function because I want
        the locals to go out of scope and not get captured by the
        rotate function I'm going to return
        """
        matrix = [array('d', range(ndv)) for _ in range(ndv)]
        # generate a random matrix
        for ii in range(ndv):
            for jj in range(ndv):
                matrix[ii][jj] = random.normalvariate(0, 1)
        pprint.pprint(matrix)
        for ii, uu in enumerate(matrix):

            for vv in matrix[ii+1:]:
        # orthogonalize and normalize:
        # for each row u,
        #     compute the length of u
        #     divide u by ||u|| to get a unit vector in the direction of u
        #     replace u with this unit vector: u = u / ||u||
        #     for every following row v
        #         compute the dot product between v and u.  This is the length of the projection of v along u.
        #         multiply this by u and subtract from v.  Now v and u are orthogonal, and u is normalized.



            #print("matrix {}".format(matrix))
            #for ii in range(ndv):
            #print("norm row {}: {}".format(ii, norm))
            for jj in range(ndv):
                matrix[ii][jj] = matrix[ii][jj] / norm
            #assert(abs(sum(x ** 2 for x in matrix[ii]) ** 0.5 - 1.0) < 1e-6)
            print("normalized row {} is {}".format(ii, matrix[ii]))
            dd = [x for x in matrix[ii]]
            for jj in range(ii+1):
                nn = sum(x ** 2 for x in dd) ** 0.5
                nsquared = nn ** 2
                pp = sum(dd[kk] * matrix[kk][jj] for kk in range(ndv))
                print("nn {} nsquared {} pp {}".format(nn, nsquared, pp))
                for kk in range(ndv):
                    dd[kk] = (dd[kk] - pp * matrix[jj][kk]) / nsquared
                print("jj {} dd = {}".format(jj, dd))
            nn = sum(x ** 2 for x in dd) ** 0.5
            print("nn {} dd {} R{} {}".format(nn, dd, ii, matrix[ii]))
            for jj in range(ndv):
                matrix[ii][jj] = dd[jj] / nn
        return matrix
    matrix = make_matrix()
    if ndv == 2:
        assert(matrix[0][1] == -matrix[1][0])
        assert(matrix[0][0] == matrix[1][1])
        determinant = matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
        print("determinant {}".format(determinant))
        assert(determinant == 1)
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
