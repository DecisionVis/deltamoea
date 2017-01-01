def dtlz2(ndv, nobj):
    """
    return an instance of dtlz2 with the requested number of
    decision variables and objectives.
    """

    """
    Quoting Deb et al. 2002...

    This test problem has a spherical Pareto-optimal front
    as in Figure 1:

    Minimize f_1(\vec{x}) = (1 + g(x_M))cos(x_1π/2)\ldots cos(x_{M-1}π/2)
    Minimize f_2(\vec{x}) = (1 + g(x_M))cos(x_1π/2)\ldots sin(x_{M-1}π/2)
    \vdots
    Minimize f_M(\vec{x}) = (1 + g(x_M))sin(x_1π/2)
    0 <= x_i <= 1 for i = 1,2,\ldots,n
    where g(x_M) = \sum_{x_i\in \vec{x_M}}(x_i - 0.5)^2
    """
    """
    The above is a little unclear with its dots and its \vec{x_M} versus
    x_M.  What it means is that each x_i where i < M gets included in f.
    index M-1 gets a sine except for f_1.
    M is the number of objectives and n is the number of decision variables.
    The decision variables where i is greater than or equal to M get
    incorporated in the function g.  This is the x_i \in \vec{x_M} bit,
    which is a total head-scratcher, notation-wise.
    Oh, I get it now.  \vec{x_M} is the vector of x_i, i >= M
    Also the lack of product notation in the product-of-cosines terms is
    a little maddening.  The objectives of index > 2 would be all the same
    except that you take one less cosine term for each objective.

    To make this concrete, let's start with n=3, M=2.  This is perhaps the
    simplest possible case.

    \vec{x_M} = (x_2, x_3)
    g(\vec{x_M}) = (x_2 - 0.5)^2 \times (x_3 - 0.5)^2

    f_1(\vec{x}) = (1 + g(\vec{x_M}))cos(x_1π/2)
    f_2(\vec{x}) = (1 + g(\vec{x_M}))sin(x_1π/2)

    OK, you could even do n=2, M=2:

    \vec{x_M} = (x_2)
    g(\vec{x_M}) = (x_2 - 0.5)^2

    f_1(\vec{x}) = (1 + g(\vec{x_M}))cos(x_1π/2)
    f_2(\vec{x}) = (1 + g(\vec{x_M}))sin(x_1π/2)

    You can't go lower and still have a meaningful test problem.
    Also we have n>=M as a constraint on the form of the problem.

    For this instance (2,2) of DTLZ2, we can see by inspection that
    0 <= g <= 0.25
    So 1 <= 1+g <= 1.25
    This depends entirely on x_2 and is minimized when x_2 = 0.5.
    cos(x_1π/2) is minimized when x_1 = 1.0.  sin(x_1π/2) is
    minimized when x_1 = 0.0.  Therein lies the conflict between
    the two objectives.  This also explains why adding more
    decisions doesn't make this problem much harder, because there's
    no conflict in the g function.  Indeed, in the (2,2) case, there's
    no conflict between x_1 and x_2.

    Hence an interest in rotated problems.
    """

