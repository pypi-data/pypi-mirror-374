# =============================================================================#
# coding: utf-8
# Mariana Jaber  2022
# Description: Uses numerical estimations of  xi(r,a) from several snapshots and
# takes its derivative wrt to scale factor to finally produce the v12(r,a)
# Simulation-only P(k) or Halo-Model P(k) prescriptions
# =============================================================================#

import numpy as np
from ..cosmology.a_to_z import *
from ..cosmology.cosmology import hubble_flat
from ..cosmology.constants import *
from ..model.integrate_xi import *
from ..data_io.read_data import read_snapshot_DUDEG_pk, cfs_pks_DUDEG
from core_functions import pk2xi
import pandas as pd


def numerical_deriv_xis_dudeg():
    '''
    Reads the P(k) from many snapshots from DUDEG simulations and calculates the corresponding 2PCFs
    Derivates such 2PCFs
    Returns
    -------
    r, a, z, xis, dxida_num
    '''

    scale_factors, z = read_snapshot_DUDEG_pk()
    r, xis, k, pks = cfs_pks_DUDEG()

    xinum_bar_list = []
    for i in np.arange(0, 63):
        xinum_bar = xi_bar(r, r, xis[i, :])
        xinum_bar_list.append(xinum_bar)

    barcorrhf_func_array = np.array(xinum_bar_list)
    dbarcorrhf_func_da_list = []

    for dd in range(len(r)):
        derivative_xibar = np.gradient(barcorrhf_func_array[:, dd], scale_factors)
        dbarcorrhf_func_da_list.append(derivative_xibar)

    #  # arrays of arrays:
    dbarcorrhf_func_array = np.array(dbarcorrhf_func_da_list)
    dxida_num = dbarcorrhf_func_array

    a = scale_factors

    return r, a, z, xis, dxida_num


def v12_from_numerical_deriv_num(which_cosmology, which_simulation_redshift=0):
    '''

    Parameters
    ----------
    which_cosmology: dictionary
    which_simulation_redshift: int

    Returns
    -------
    r_array, v12_(r, a_fix), a, z, xi_a, d_xi_da_a
    '''
    r, a, z, xis, dxida_num = numerical_deriv_xis_dudeg()

    idx_which_a = ID_snapshot_selector(z, which_simulation_redshift)

    #     zp = which_simulation_redshift

    Hofa = hubble_flat(z, which_cosmology)
    Hofa_in_kmsMpc = Hofa

    num = a[idx_which_a] * a[idx_which_a] * Hofa_in_kmsMpc[idx_which_a] * r * dxida_num[:, idx_which_a]
    den = 3 * (1 + xis[idx_which_a, :])
    v12 = - num / den / REDUCED_H0  # -- units of this output are km/s

    xi_a = xis[idx_which_a, :]
    d_xi_da_a = dxida_num[:, idx_which_a]

    return r, v12, a, z, xi_a, d_xi_da_a


def cfs_pks_HM(r_array_usr, use_r_array = True, r_args=[0.1, 40, 50], model='F6'):
    '''
    r_array_usr: array provided by the user
    use_r_array: Boolean: set to True to use the modified r_array for the merged simulations
    r_args: r_ini, r_end, r_steps [obsolete]
    model: string: 'N1', 'N5', 'F5', 'F6'
    Returns
    -------
    z, r, xi, k, pk
    '''
    # inputpath = '/home/gupta/PAIRWISE_VELOCITY_HALOMODEL/new_pk_logz/'
    inputpath = '/home/jaber/velocities/velocities/data/halo_model_mg/'
    # new files contain:  k, ratio, halo-fit_LCDM, new pk

    cols_mg = [0, 1, 2, 3]
    names_mg = ["k", "delta", "Pklcdm", "Pkhm"]
    dat_mg = '.dat'

    root_n1 = 'pk_hm_n1_z'
    root_n5 = 'pk_hm_n5_z'
    root_f5 = 'pk_hm_f5_z'
    root_f6 = 'pk_hm_f6_z'

    models = {
        'N1': (root_n1, cols_mg, names_mg, dat_mg),
        'N5': (root_n5, cols_mg, names_mg, dat_mg),
        'F5': (root_f5, cols_mg, names_mg, dat_mg),
        'F6': (root_f6, cols_mg, names_mg, dat_mg)
    }

    # ---------
    # empty lists to store the outputs
    pk_list = []
    xi_list = []
    # ---------

    # ------- Define our r array to match the simulations range
    # ------- Include the case where the r-array is user-defined
    if use_r_array:
        r_Mpch_log = r_array_usr

    else:
        # ------- Unpack r_array
        r_min, r_max, r_array_size = r_args

        r_Mpch_log = np.logspace(np.log10(r_min), np.log10(r_max),
                                 int(r_array_size),
                                 endpoint=True)


    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1, 1.2, 1.5, 1.86, 1.9, 2])
    # the value 0.297 has been renamed to 0.30 in the files

    HMredshifts = np.round(HMredshifts, 4)

    z_vals = HMredshifts

    # ---- loop over the redshifts
    for j in range(len(HMredshifts)):
        root = models[model][0]
        cols = models[model][1]
        names = models[model][2]
        dat = models[model][3]

        filename = root + "%1.2f" % HMredshifts[j] + dat
        file_pk = inputpath + filename

        #  pandas read the file

        pk_df = pd.read_csv(
            file_pk, sep='\s+',
            usecols=cols,
            names=names,
            skiprows=1)

        # save the total non-linear P(k) values. Append them to the empty list
        if model == 'LCDM':
            pk_val = pk_df.Pklcdm.values
        else:

            # pk_val = pk_df.Pkhm.values
            pk_val = pk_df.Pklcdm.values * pk_df.delta.values


        pk_list.append(pk_val)

        # convert the non-linear P(k) to Xi(r). Append them to the empty list

        rg = 0.1
        #
        pk_product = pk_df.Pklcdm.values * pk_df.delta.values
        xi_hf = pk2xi(
            r_Mpch_log,
            pk_df.k.values, pk_product,
            kmin=None, kmax=None,
            kfactor=100, kbinsmax=100000,
            Rg=rg)

        xi_list.append(xi_hf)

    # ## After the 2nd loop, we convert the lists to arrays

    xi_array = np.array(xi_list)
    pk_array = np.array(pk_list)

    # Because the k_vals and r_vals are the same for all files, we retrieve them now after the loop ended
    r_array = r_Mpch_log
    k_array = np.array(pk_df.k)

    r, xi, k, pk = r_array, xi_array, k_array, pk_array

    return z_vals, r, xi, k, pk


def numerical_deriv_xis_hm(r_array_usr, use_r_array = True, r_args=[0.1, 40, 50], model='LCDM'):
    '''
    Numerical derivative over redshift values of the Halo model correlation functions
     Parameters
    ----------
    r_array_usr: array provided by the user
    use_r_array: Boolean: set to True to use the modified r_array for the merged simulations
    r_args: tuple: [initial, end, steps] [obsolete]

     model: string: 'LCDM', 'N1', 'N5', 'F5', 'F6'

    Returns
    -------
    r, a, z, xis, dxida_num
    '''


    z_values, r, xis, k, pks = cfs_pks_HM(r_array_usr, use_r_array, r_args, model)

    a_values = scalefactor_from_redshift(z_values)
    scale_factors, z = a_values, z_values
    xinum_bar_list = []

    for i in range(len(z_values)):
        xinum_bar = xi_bar(r, r, xis[i, :])
        xinum_bar_list.append(xinum_bar)

    barcorrhf_func_array = np.array(xinum_bar_list)
    dbarcorrhf_func_da_list = []

    for dd in range(len(r)):
        derivative_xibar = np.gradient(barcorrhf_func_array[:, dd], scale_factors)
        dbarcorrhf_func_da_list.append(derivative_xibar)

    ## arrays of arrays:
    dbarcorrhf_func_array = np.array(dbarcorrhf_func_da_list)
    dxida_num = dbarcorrhf_func_array

    a = scale_factors
    return r, a, z, xis, dxida_num


def v12_from_numerical_deriv_hm(which_cosmology, r_array_usr, use_r_array = True, r_args=[0.1, 40, 50], model='LCDM',
                                which_simulation_redshift=0):
    '''
    Pairwise velocity estimation using the derivative over 2PCFs calculated from the Halo Model (S. Gupta)
    Parameters
    ----------
    which_cosmology: dictionary
    model: string
    r_array_usr: array provided by the user
    use_r_array: Boolean: set to True to use the modified r_array for the merged simulations
    r_args: tuple: [initial, end, steps] [obsolete]
    model: string: 'LCDM', 'N1', 'N5', 'F5', 'F6'
    which_simulation_redshift: int
    Returns
    -------
    r_array, v12_(r, a_fix), a, z, xi_a, d_xi_da_a
    '''
    r, a, z, xis, dxida_num = numerical_deriv_xis_hm(r_array_usr, use_r_array , r_args, model)

    idx_which_a = ID_snapshot_selector(z, which_simulation_redshift)
    # To-do: set the precision of the snapshot

    #     zp = which_simulation_redshift

    Hofa = hubble_flat(z, which_cosmology)
    Hofa_in_kmsMpc = Hofa

    num = a[idx_which_a] * a[idx_which_a] * Hofa_in_kmsMpc[idx_which_a] * r * dxida_num[:, idx_which_a]
    den = 3 * (1 + xis[idx_which_a, :])
    v12 = - num / den / REDUCED_H0  # -- units of this output are km/s

    xi_a = xis[idx_which_a, :]
    d_xi_da_a = dxida_num[:, idx_which_a]

    return r, v12, a, z, xi_a, d_xi_da_a
