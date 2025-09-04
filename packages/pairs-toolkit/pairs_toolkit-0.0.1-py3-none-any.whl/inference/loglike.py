# =============================================================================#
# coding:        utf-8
# Mariana Jaber: 2022
# Description:   Gaussian  approximation of the likelihood for v12(r,a)
# =============================================================================#
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools
import emcee
from scipy.optimize import minimize

from ..data_io.read_data import *
from ..model.v12_num_deriv_of_xi import *
from ..cosmology import *
from ..cosmology.constants import *


# TODO: we need to add the three snapshots in the sum of the data
def loglike_full(theta, z_eval, r_bins, v12_sim, v12_err):
    """
    Logarithm of the likelihood function (the probability of a dataset given the model parameters)
    Parameters
    ----------

    theta: cosmological parameters vector to be sampled
    z_eval: redshift at which we are evaluating the likelihood
    r_bins: r_bins of simulation data
    v12_sim: v12(r_bins)
    v12_err: v12 errors

    Returns
    -------
    logL = -0.5 * np.sum((v12_simulation - v12_model) ** 2 / v12_err ** 2)
    """
    #  ---- reads the data and defines the binning for the model ------
    r_min = r_bins.min()
    r_max = r_bins.max()
    rsize = len(r_bins)
    #  ---- sets the parameters for the model -----
    bias = 1.0
    do_Pk_non_linear = True

    lnA_s, Oc0h2_val, h_val = theta

    As_val = np.exp(lnA_s) / 10 ** 10
    my_cosmology = define_cosmology(Ocdm0h2=Oc0h2_val, h=h_val, As=As_val)
    # my_cosmology = define_cosmology(Om0=omega_m0, h=h_val, As=A_s)

    cosmo_args = my_cosmology, bias, do_Pk_non_linear

    #  ---- calculates the v12_model for the selected redshift --------
    r_, v12_model, a_, z_, xi_, dxi_da_ = v12_from_numerical_deriv(cosmo_args, 
                                z_array=None, 
                                r_array=r_bins, 
                                r_args=None,
                                use_r_array = True,
                                use_z_array = False, z_args=[0, 2, 0.1],
                                redshift_simulation=[0, 0.3, 0.5, 1],
                                which_simulation_redshift=0,
                                CAMB_path="/opt/cosmo_data/",
                                CAMB_outputdir_Pk="/home/jaber/shared/data/output_Pk_camb/",
                                MG=False, model='00', rcH0=1.000, F_R0=0.00001)
    # TODO: add the three snapshots, for loop?
    return -0.5 * np.sum((v12_sim - v12_model) ** 2 / v12_err ** 2)

def loglike_as(theta, z_eval, r_bins, v12_sim, v12_err):
    """
    Logarithm of the likelihood function (the probability of a dataset given the model parameters)
    Parameters
    ----------

    theta: cosmological parameters vector to be sampled
    z_eval: redshift at which we are evaluating the likelihood
    r_bins: r_bins of simulation data
    v12_sim: v12(r_bins)
    v12_err: v12 errors

    Returns
    -------
    logL = -0.5 * np.sum((v12_simulation - v12_model) ** 2 / v12_err ** 2)
    """
    #  ---- reads the data and defines the binning for the model ------
    r_min = r_bins.min()
    r_max = r_bins.max()
    rsize = len(r_bins)
    #  ---- sets the parameters for the model -----
    bias = 1.0
    do_Pk_non_linear = True

    lnA_s = theta
    As_val = np.exp(lnA_s) / 10 ** 10
    # WARNING: defined this way, the ELEPHANT is hardcoded in the cosmological parameters
    my_cosmology = define_cosmology(As=As_val)

    cosmo_args = my_cosmology, bias, do_Pk_non_linear

    #  ---- calculates the v12_model for the selected redshift --------
    r_, v12_model, a_, z_, xi_, dxi_da_ = v12_from_numerical_deriv(cosmo_args,
                                                                    z_array=None, r_array=None,
                                                                    use_r_array = False,
                                                                    use_z_array= False,
                                                                   r_args=[r_min, r_max, rsize],
                                                                   z_args=[0, 2, 0.1],
                                                                   redshift_simulation=[0, 0.3, 0.5, 1],
                                                                   which_simulation_redshift=z_eval,MG=False, model='00')

    return -0.5 * np.sum((v12_sim - v12_model) ** 2 / v12_err ** 2)

def loglike_omc(theta, z_eval, r_bins, v12_sim, v12_err):
    """
    Logarithm of the likelihood function (the probability of a dataset given the model parameters)
    Parameters
    ----------

    theta: cosmological parameters vector to be sampled
    z_eval: redshift at which we are evaluating the likelihood
    r_bins: r_bins of simulation data
    v12_sim: v12(r_bins)
    v12_err: v12 errors

    Returns
    -------
    logL = -0.5 * np.sum((v12_simulation - v12_model) ** 2 / v12_err ** 2)
    """
    #  ---- reads the data and defines the binning for the model ------
    r_min = r_bins.min()
    r_max = r_bins.max()
    rsize = len(r_bins)
    #  ---- sets the parameters for the model -----
    bias = 1.0
    do_Pk_non_linear = True

    Oc0h2_val = theta

    # WARNING: defined this way, the ELEPHANT is hardcoded in the cosmological parameters
    my_cosmology = define_cosmology(Ocdm0h2=Oc0h2_val)

    cosmo_args = my_cosmology, bias, do_Pk_non_linear

    #  ---- calculates the v12_model for the selected redshift --------
    r_, v12_model, a_, z_, xi_, dxi_da_ = v12_from_numerical_deriv(cosmo_args,
                                                                   r_args=[r_min, r_max, rsize],
                                                                   which_simulation_redshift=z_eval)

    return -0.5 * np.sum((v12_sim - v12_model) ** 2 / v12_err ** 2)

## TODO: do we need this? Remove
def loglike_h0(theta, z_eval, r_bins, v12_sim, v12_err):

    """
    Logarithm of the likelihood function (the probability of a dataset given the model parameters)
    Parameters
    ----------

    theta: cosmological parameters vector to be sampled
    z_eval: redshift at which we are evaluating the likelihood
    r_bins: r_bins of simulation data
    v12_sim: v12(r_bins)
    v12_err: v12 errors

    Returns
    -------
    logL = -0.5 * np.sum((v12_simulation - v12_model) ** 2 / v12_err ** 2)
    """
    #  ---- reads the data and defines the binning for the model ------
    r_min = r_bins.min()
    r_max = r_bins.max()
    rsize = len(r_bins)
    #  ---- sets the parameters for the model -----
    bias = 1.0
    do_Pk_non_linear = True

    h_val = theta

    # WARNING: defined this way, the ELEPHANT is hardcoded in the cosmological parameters
    my_cosmology = define_cosmology(h=h_val)

    cosmo_args = my_cosmology, bias, do_Pk_non_linear

    #  ---- calculates the v12_model for the selected redshift --------
    r_, v12_model, a_, z_, xi_, dxi_da_ = v12_from_numerical_deriv(cosmo_args,
                                                                   r_args=[r_min, r_max, rsize],
                                                                   which_simulation_redshift=z_eval)

    return -0.5 * np.sum((v12_sim - v12_model) ** 2 / v12_err ** 2)

def log_prior_full(theta):
    """

    Parameters
    ----------
    theta

    Returns
    -------

    """
    lnA_s, Oc0h2_val, h_val = theta
    if 0.06 < Oc0h2_val < 0.2 and 0.5 < h_val < 0.9 and 1.5 < lnA_s < 3.5:
        return 0.0
    return -np.inf

def log_prior_as(theta):
    """

    Parameters
    ----------
    theta

    Returns
    -------

    """
    lnA_s = theta
    if 1.5 < lnA_s < 3.5:
        return 0.0
    return -np.inf

def log_prior_omc(theta):
    """

    Parameters
    ----------
    theta

    Returns
    -------

    """
    Oc0h2_val = theta
    if 0.06 < Oc0h2_val < 0.2 :
        return 0.0
    return -np.inf

def log_prior_h0(theta):
    """

    Parameters
    ----------
    theta

    Returns
    -------

    """
    h_val = theta
    if 0.5 < h_val < 0.9:
        return 0.0
    return -np.inf


# ---- dictionary of likelihood functions --------------

AS_ONLY = 0
OMC_ONLY = 1
H0_ONLY = 2
FULL = 3

loglike_set = (
    ("lnAs", loglike_as, log_prior_as),
    ("omch2", loglike_omc, log_prior_omc),
    ("h0", loglike_h0, log_prior_h0),
    ("full", loglike_full, log_prior_full)
)

# ------------------------------------------------------


def log_probability(theta, z_eval, r_bins, v12_sim, v12_err, which_like=FULL):
    """

    Parameters
    ----------
    theta: parameters to be sampled (depends on which)
    z_eval
    r_bins
    v12_sim
    v12_err
    which_like: 0:AS, 1:OmegaCh2, 2: h0, 3: Full
    Returns
    -------

    """

    like_name, log_likelihood, log_prior = loglike_set[which_like]

    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, z_eval, r_bins, v12_sim, v12_err)



#which_like = FULL
#like_name, log_likelihood, log_prior = loglike_set[which_like]
#print(like_name)