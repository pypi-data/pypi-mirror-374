# =============================================================================#
# coding: utf-8
# Mariana Jaber & Jorge Garcia-Farieta: 2022
# Implementation of CAMB for python: Antonela Taverna 2025
# Description: Calculates the
# 2PCF from analytical P(k)  using a CLASS transfer function
# and implements the numerical derivative of xi(r,a) wrt to scale factor:
# partial xi(r,a)/partial(a)
# =============================================================================#

import os
from pathlib import Path

from ..cosmology.a_to_z import *
from .integrate_xi import *
from ..cosmology.constants import *
from ..cosmology.cosmology import *

from scipy.integrate import simpson
from scipy.interpolate import interp1d
from scipy.special import spherical_jn
import camb

def xis_from_pk_pycamb(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                use_r_array = True,
                use_z_array = False, z_args=[0, 2, 0.1],
                redshift_simulation=[0, 0.3, 0.5, 1]):
    """
    Calculates P(k) for a given cosmology. Obtains the respective Xi(r,a) and its
    integral, Xi_bar(r,a).
    Parameters:
    ----------
    :param cosmo_args: tuple
                (which_cosmology, bias=1, do_Pknonlinear=True).
    which_cosmology: dictionary defined in cosmology.py. Default values are from ELEPHANT
                simulations. The tuple includes flags for either linear or non-linear (halo-fit),
                and max k scale (k = 50Mpc/h)
    bias:   float
            for biased tracers, the linear bias value
            default value 1.0
    do_Pknonlinear: boolean
            True  -> uses halo-fit implementation for the non-linear power spectrum
            False -> uses linear power spectrum
    :param r_args: tuple of floats
            [r_min, r_max, r_array_size]

    :param use_z_array: boolean
            False -> generates a linear array of redshifts
            True ->  expects an array with z-values

    :param z_args: tuple of floats
            [z_in, z_end, z_step_size]

    :param z_array: if use_z_array set to True, an array of z-values should be passed

    :param r_array: if use_r_array is set to True, an array of r-values should be passed

    :param redshift_simulation:    tuple of floats
            values of redshift for the snapshots of the simulations available
            For instance, ELEPHANT: [0, 0.3, 0.5, 1]
            MILLENIUM-LIKE: [0, 0.5, 1, 2]

    Returns
    -------
    r_Mpch_log: array
        r array in Mpc/h
    scale_factors: array
        scale factors
    redshifts:  array
        redshift values
    xi_array: n-dim array
        array containing the linear(nolinear) 2PCFs as function of r for each value of the
        scale factor
        shape of array: (r_values, scale_factor_values)
    xi_bar_array: n-dim array
        array containing the integral of the linear(nolinear) 2PCFs as function of r
        for each value of the scale factor
        shape of array: (r_values, scale_factor_values)
    xi_bbar_array: n-dim array
        array containing the integral of the linear(nolinear) 2PCFs normalized by 1/(1+xi)
         as function of r for each value of the scale factor
        shape of array: (r_values, scale_factor_values)

    """
    # ------- cosmology arguments
    which_cosmology, bias, do_Pknonlinear = cosmo_args

    for key in ['h','Om0','Ob0','Ocdm0','sigma80','ns','Ob0h2','Ocdm0h2']:
        which_cosmology[key] = round(which_cosmology[key], 6)

    h = which_cosmology['h']
    Om0 = which_cosmology['Om0']
    Ob0 = which_cosmology['Ob0']
    Ocdm0 = which_cosmology['Ocdm0']
    ns = which_cosmology['ns']
    As = which_cosmology['As']

    if use_z_array:
        redshifts = z_array

    else:
        # ------ Create the z array, including the z-values for simulation snapshots
        z_in, z_end, z_step_size = z_args
        zsteps = int((z_end - z_in) / z_step_size + 1)
        redshifts = np.linspace(z_in, z_end, zsteps, endpoint=True)
        redshifts = np.round(redshifts, 4)


    # ------- In case simulation snapshots are not included: add them
    redshifts = np.unique(np.append(redshifts, redshift_simulation))
    redshifts = np.sort(redshifts, axis=0)
    scale_factors = scalefactor_from_redshift(redshifts)

    # ------- Define our r array to match the simulations range
    # ------- Include the case where the r-array is user-defined
    if use_r_array:
        r_Mpch_log = r_array

    else:
        # ------- Unpack r_array
        r_min, r_max, r_array_size = r_args

        r_Mpch_log = np.logspace(np.log10(r_min), np.log10(r_max),
                             int(r_array_size),
                             endpoint=True)

    # ------- Set parameters
    kkmax=100
    param = set_params_pycamb(_h=h,
                             _Ob0=Ob0,
                             _Ocdm0=Ocdm0,
                             _ns=ns,
                             _As=As,
                             _do_Pknonlinear=do_Pknonlinear,
                             _redshifts=redshifts,
                             _kmax=kkmax,
                             _k_per_logint=0, #100,
                             _omnuh2=0.0,
                             )
    


    # ------- Calculate Power Spectrum for specified params
    camb.set_feedback_level(level=0)
    results = camb.get_results(param)
    

    #CAMB fortran
    matter =  'delta_cdm'
    kh, zcamb, pk = results.get_matter_power_spectrum(minkh=1e-4,
                                                      maxkh=104.549,
                                                      npoints=694,
                                                      var1=matter,
                                                      var2=matter)
    
    
    matter =  'delta_nonu'  #['delta_cdm', 'delta_nonu', 'delta_tot']
    #kh, zcamb, pk = results.get_matter_power_spectrum(minkh=1e-4,
    #                                                  maxkh=100,
    #                                                  npoints=500,
    #                                                  var1=matter,
    #                                                  var2=matter)

    #---------- test
    print('shape pk_pycamb', np.shape(pk), np.max(kh))

    # ------- Comparing with other inifile
    #print('----------------- Comparing w/inifile')
    #ini_file = 'PkNOLIN_GR_h0.697_Ob0.046_Ocdm0.235_ns0.971_As2.297100987e-09_Ob0h20.022347_Ocdm0h20.114165.ini'
    #compare_inifile_fortran_pycamb(_file_name = ini_file, _param_py=param, _redshifts=redshifts)
    #print('------------------')

    # ------- Empty lists to save our results
    corr_func_list = []
    barcorr_func_list = []
    bbarcorr_func_list = []

    for i in range(len(redshifts)):
        Xi = pk2xi(r_Mpch_log, kh, pk[i], kmin=None, kmax=None,
                        kfactor=100, kbinsmax=100000,
                        Rg=None)
        xi_bar_ = xi_bar(r_Mpch_log, r_Mpch_log, Xi)
        xi_bbar = xi_bar_ / (1 + Xi)

        corr_func_list.append(Xi)
        barcorr_func_list.append(xi_bar_)
        bbarcorr_func_list.append(xi_bbar)


    # ------ After the loop, we convert the lists to Arrays of arrays
    xi_array = np.array(corr_func_list)
    xi_bar_array = np.array(barcorr_func_list)
    xi_bbar_array = np.array(bbarcorr_func_list)


    rarray = r_Mpch_log

    return rarray, scale_factors, redshifts, xi_array, xi_bar_array, xi_bbar_array

# ==================================

def numerical_deriv_xi_pycamb(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                       use_r_array = False,
                       use_z_array = False,   z_args=[0, 2, 0.1],
                       redshift_simulation=[0, 0.3, 0.5, 1]):
    """
    Calculates the  numerical derivative w.r.t. scale factor of Xi:
    i.e. partial Xi(r,a) / partial a

    :param cosmo_args: (which_cosmology, bias, do_Pknonlinear)
            which_cosmology = dictionary define using cosmology.py
            bias: float
                linear bias 1.0
            do_Pknonlinear: boolean
    :param r_args: tuple of floats
            [r_min, r_max, r_size]
    :param use_r_array: in case we need a user-defined r-array
    :param r_array: a user defined r_array
    :param z_args: tuple of floats
            [z_in, z_end, z_size]
    :param redshift_simulation: tuple of floats

    :return: r, a, z, xi_array, d_xi_da

    """

    r, scale_factors, z, xi_array, xi_bar_array, xi_bbar_array = \
        xis_from_pk_pycamb(cosmo_args, z_array, r_array, r_args,
                           use_r_array, use_z_array, z_args, redshift_simulation)

    d_bar_corr_func_da_list = []
    bar_corr_func_array = xi_bar_array

    # ----- actual derivative happens here:
    # ----- TO-DO: use a better derivative!!!
    for dd in range(len(r)):
        derivative = np.gradient(bar_corr_func_array[:, dd],
                                 scale_factors)
        d_bar_corr_func_da_list.append(derivative)

    # ---- arrays of arrays:
    d_bar_corr_func_array = np.array(d_bar_corr_func_da_list)

    d_xi_da = d_bar_corr_func_array

    a = scale_factors

    camb.set_feedback_level(level=0)

    return r, a, z, xi_array, d_xi_da

# ==================================

def pk2xi(r, kh, pk, kmin=None, kmax=None, kfactor=100, kbinsmax=100000,
          Rg=None):
    """
    Power spectrum to 2-point density-density correlation function xi(r).
    Author: Krishna Naidoo, https://github.com/knaidoo29/
    Parameters
    ----------
    r : array
        Real space comoving distance.
    kh : array
        K values for the power spectrum.
    pk : array
        Power spectrum.
    kmin : float, optional
        Minimum k for sigmaR integration.
    kmax : float, optional
        Maximum k for sigmaR integration.
    kfactor : int, optional
        Binning extra factor.
    kbinsmax : int, optional
        Maximum kbins for the interpolated pk
    Rg : float, optional
        Gaussian smoothing scale.
    
    Returns
    -------
    xi : array
        Two point correlation function.
    """
    interp_PK = interp1d(kh, pk, kind='cubic')
    if kmin is None:
        kmin = kh.min()
    if kmax is None:
        kmax = kh.max()
    xi = np.zeros(len(r))
    for i in range(0, len(xi)):
        kscale = 2. * np.pi / r[i]
        kbins = kfactor * int(np.ceil((kmax - kmin) / kscale))
        if kbins > kbinsmax:
            kbins = kbinsmax
        k = np.linspace(kmin, kmax, kbins)
        p = interp_PK(k)
        if Rg is None:
            xi[i] = (1. / (2. * np.pi ** 2.)) * simpson(
                (k ** 2.) * p * spherical_jn(0, k * r[i]), k)
        else:
            Wg = np.exp(-0.5 * (k * Rg) ** 2.)
            xi[i] = (1. / (2. * np.pi ** 2.)) * simpson(
                (k ** 2.) * Wg * p * spherical_jn(0, k * r[i]), k)
    return xi


def v12_from_numerical_deriv_pycamb(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                             use_r_array = True,
                             use_z_array = False, z_args=[0, 2, 0.1],
                             redshift_simulation=[0, 0.3, 0.5, 1],
                             which_simulation_redshift=0):
    """
    Calculates the pairwise velocity, v12(r,a), of DM particles according to
    Juszkiewicz 1999 eqn 1 # to-do improve this description
    :param cosmo_args, any
    which_cosmology:
    bias:
    do_Pknonlinear:
    :param r_args:
    :param z_args:
    :param use_r_array: if True, take r_array as provided by the user
    :param use_z_array: if True, take z_array as provided by the user
    :param r_array user provided array
    :param z_array user provided array
    :param redshift_simulation:
    :param which_simulation_redshift:

    :return: r, v12,  a, z, xi_a, d_xi_da_a
    """
    r, a, z, xi_array, d_xi_da = numerical_deriv_xi_pycamb(cosmo_args, z_array, r_array,
                                                    r_args, use_r_array,
                                                    use_z_array, z_args,
                                                    redshift_simulation)
    which_cosmology, bias, do_Pknonlinear = cosmo_args

    idx_which_a = ID_snapshot_selector(z, which_simulation_redshift)
    # print('for the chosen redshift of ', which_simulation_redshift,
    #       'we have a = ', a[idx_which_a])
    zp = 1 / a - 1
    Hofa = hubble_flat(zp, which_cosmology)
    # Hofa = which_cosmology.hubble_function(1 / a - 1)
    # Hofa_in_kmsMpc = Hofa / (1000 / 3e8)
    Hofa_in_kmsMpc = Hofa

    # print('for the chosen redshift, H(z) = ', Hofa[idx_which_a] / (1000 / 3e8))
    # print('for the chosen redshift, H(z) = ', Hofa[idx_which_a])

    # since the arrays for r are expressed in Mpc/h we need to mind
    # the output and divide our v12 result by h (0.69)

    num = a[idx_which_a] * a[idx_which_a] * Hofa_in_kmsMpc[
        idx_which_a] * r * d_xi_da[:, idx_which_a]
    den = 3 * (1 + xi_array[idx_which_a, :])
    v12 = - num / den / REDUCED_H0  # -- units of this output are km/s

    xi_a = xi_array[idx_which_a, :]
    d_xi_da_a = d_xi_da[:, idx_which_a]

    return r, v12, a, z, xi_a, d_xi_da_a


def set_params_pycamb(_h, _Ob0, _Ocdm0, _ns, _As,
                      _do_Pknonlinear, _redshifts,
                      _kmax=100, _k_per_logint=0,
                      _omnuh2=0.0):
    """
    Set CAMB parameters

    Returns:
    --------
    camb.CAMBparams
        Configured CAMB parameters object.
    """

    pars = camb.CAMBparams()

    pars.set_cosmology(H0=_h * 100,
                       ombh2=np.round(_Ob0 * _h**2, 6),
                       omch2=np.round(_Ocdm0 * _h**2, 6),
                       # ---fixed
                       omk=0.0,
                       TCMB=2.7255,
                       YHe=0.24,
                       num_massive_neutrinos = 1,
                       )
    
    
    pars.InitPower.set_params(ns=_ns,
                              As=_As,
                              # ---fixed
                              nrun= 0.0,
                              nrunrun=0.0,
                              nt=0.0,
                              ntrun=0.0,
                              r=0.0,
                              pivot_scalar=0.05,
                              pivot_tensor=0.05,
                              parameterization='tensor_param_indeptilt',
                              )
    

    pars.NonLinearModel.halofit_version = 4  # 9 mead2020
    if _do_Pknonlinear:
        #pars.NonLinear = camb.model.NonLinear_both
        pars.NonLinear = camb.model.NonLinear_pk
        print('HaloFit_version=', pars.NonLinearModel.halofit_version)
    else:
        pars.NonLinear = camb.model.NonLinear_none
    
    # ------- Set Fixed parameters
    pars.omnuh2 = _omnuh2
    pars.InitPower.At = 0.0

    pars.set_matter_power(redshifts=_redshifts, kmax=_kmax)

    pars.WantCls = False
    pars.WantScalars = False
    pars.WantVectors = False
    pars.WantTensors = False
    pars.WantTransfer = True
    pars.WantDerivedParameters = False
    pars.DoLensing = False
    pars.DoLateRadTruncation = True
    pars.scalar_initial_condition = 'initial_adiabatic'

    # Transfer
    pars.Transfer.high_precision = False
    pars.Transfer.kmax = _kmax
    pars.Transfer.k_per_logint = _k_per_logint
    Numredshifts = len(_redshifts)
    pars.Transfer.PK_num_redshifts = Numredshifts
    pars.PK_redshifts = _redshifts
    pars.Transfer.accurate_massive_neutrinos = False

    # Dark Enegry
    pars.set_dark_energy(w=-1.0,
                         cs2=1.0,
                         dark_energy_model='fluid')
    
    # Neutrino (default params CAMB-fortran)   
    pars.num_nu_massless = 2.046
    pars.nu_mass_eigenstates = 1
    pars.share_delta_neff = True
    pars.nu_mass_fractions = [1.0]
    pars.nu_mass_degeneracies = [0.0]
    pars.MassiveNuMethod = 'Nu_trunc'

    # Reionization (default params CAMB-fortran)
    pars.Reion.reionization = True
    pars.Reion.use_optical_depth = True
    pars.Reion.optical_depth = 0.09
    pars.Reion.delta_redshift = 1.5
    pars.Reion.fraction = -1.0
    pars.Reion.helium_redshift = 3.5
    pars.Reion.helium_delta_redshift = 0.4

    # Recombination (Recfast default)
    pars.Recomb.Recfast_fudge = 1.14
    pars.Recomb.Recfast_fudge_He = 0.86
    pars.Recomb.Recfast_Heswitch = 6
    pars.Recomb.Recfast_Hswitch = True

    # Accuracy (default params CAMB-fortran)
    pars.Accuracy.AccurateBB = False
    pars.Accuracy.AccuratePolarization = True
    pars.Accuracy.AccurateReionization = True
    pars.Accuracy.AccuracyBoost = 1.0
    pars.Accuracy.lAccuracyBoost = 1.0
    pars.Accuracy.lSampleBoost = 1.0

    return pars

def compare_inifile_fortran_pycamb(_file_name, _param_py, _redshifts):
    
    PATH = Path(os.path.abspath(os.path.dirname(__file__)))
    path_ini = str(PATH / "../../resources/CAMB/inifiles") + "/"
    ini_file = path_ini + _file_name
    pars_ini_file = camb.read_ini(ini_file)
    pars_ini_file.set_matter_power(redshifts=_redshifts)
    print('Comparing params pycamb  <-> params read .ini ==========')
    diffs = pars_ini_file.diff( _param_py)
    
    return diffs
