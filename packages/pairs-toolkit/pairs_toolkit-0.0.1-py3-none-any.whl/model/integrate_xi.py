# =============================================================================#
# coding: utf-8
# Jorge Garcia-Farieta & Mariana Jaber: 2022
# Description:
# =============================================================================#

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline


def xi_bar(RR, rr, xi):
    '''
    computes xi_bar(RR) = 3/RR^3 ∫rr^2 xi drr.
    rr array can be lineal or log spaced.
    '''
    # uses an interpolation and the integrate
    result = 0
    xibar_list = []
    integrand = InterpolatedUnivariateSpline(rr, rr ** 2 * xi,
                                             k=3)  # k=3 gives linear order 3
    for ii in range(len(RR)):
        result = 3. / RR[ii] ** 3 * integrand.integral(0, RR[ii])
        xibar_list.append(result)

    xibar_array = np.array(xibar_list)
    return xibar_array
