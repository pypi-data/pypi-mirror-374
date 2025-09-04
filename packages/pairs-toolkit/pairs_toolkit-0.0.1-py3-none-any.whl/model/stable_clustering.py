# =============================================================================#
# coding: utf-8
# Mariana Jaber 2023
# Description:  Functions to find the stable clustering regime and v12min
# =============================================================================#

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
import pandas as pd
import itertools
from scipy.interpolate import UnivariateSpline
import os
from os import sys

from ..cosmology.a_to_z import scalefactor_from_redshift
from ..cosmology.cosmology import *
from .v12_num_deriv_of_xi import v12_from_numerical_deriv
from .simulation_driven_dudeg import v12_from_numerical_deriv_hm


def calculate_v12(modelname='F5', use_halofit=True):
    '''
    Calculate the v12(r) for each z in the z_arrau and save it as npy

    Parameters
    ----------
    modelname: str
    use_halofit: bool

    Returns
    -------

    '''
    # #  select one model at the time
    model = modelname

    # # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()

    # #--- READING ONE SNAPSHOT TO GET THE RANGE IN r FOR BETTER MATCHING
    v12_N1_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    r_40 = v12_GR_Z00_merged.r.values
    r_40_MG = v12_N1_Z03_merged.r.values

    # # hard-coded z-values
    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1,
         1.2, 1.5, 1.86, 1.9, 2])

    if model == 'GR':
        zvalues = np.round(HMredshifts, 2)  # # potential bug in LCDM case

    else:
        zvalues = np.round(HMredshifts, 4)  # #

    which_cosmology = cosmoELEPHANT

    # # cosmology, bias, nonlinear
    cosmo_args = which_cosmology, 1.0, True

    print('>>>> Start running v12 for all z-vals ')

    # # hard-coded r-range to avoid the first root (?)
    # # used to calculate r*a(z)*H(z) and to map the interpolating function for v12(r)
    r_spline = np.logspace(-0.3, 1.3, 500)

    path_to_solutions = '/home/jaber/shared/data/stable_clustering/v12model/'

    if use_halofit:
        sufix = '_HF'
    else:
        sufix = '_HM'

    for zval in zvalues:

        filename = path_to_solutions + model + '_v12_of_r_z_' + str(zval) + sufix

        # # Hubble factor first:
        factor_Hr = calculate_rH(r_spline, zval)

        # # -----  v12(z, r) ----
        if model == 'GR':
            # ## CAMB HALOFIT
            rr, v12_z, aa, zz, xi_hf_z, dxida_hf_z = v12_from_numerical_deriv(
                cosmo_args, use_r_array=True, r_array=r_40,
                use_z_array=True,
                z_array=zvalues,
                MG=False,
                model='00',  # redundant
                rcH0=1.0,  # redundant
                F_R0=1e-06,  # redundant
                which_simulation_redshift=zval)

            np.save(filename, np.array((rr, v12_z)))

        elif model == 'N1':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='99',
                    rcH0=1.0,  # # nDGP N1
                    F_R0=1e-05,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

        elif model == 'N5':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='99',
                    rcH0=5.0,  # # nDGP N1
                    F_R0=1e-05,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

        elif model == 'F5':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='04',
                    rcH0=1.0,
                    F_R0=1e-05,  # # f(r) F5
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

        elif model == 'F6':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='04',
                    rcH0=1.0,
                    F_R0=1e-06,  # # f(r) F6
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)
                np.save(filename, np.array((rr, v12_z)))

        else:
            print("Option invalid. Please verify your inputs.")

    return

# Define the function to calculate 'rH' values
def calculate_rH(rvals, zval):
    '''
    Calculating the function r*a(z)*H(z)
    Parameters
    ----------
    rvals: array
    zval:  float

    Returns
    -------
    array of len = len(rvals)
    '''
    # # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()
    factor_Hr_array = rvals * scalefactor_from_redshift(zval) * hubble_flat(zval, cosmoELEPHANT)
    return factor_Hr_array


def read_v12_sim_merged_data(path):
    '''
    Read the simulation data and returns a pandas df with structure: "r", "v12", "Errv12"
    Parameters
    ----------
    path: string

    Returns: dict
    -------

    '''
    dict_v12_peak_err_sims = pd.read_csv(path, sep='\s+', comment='#', names=["r", "v12", "Errv12"], skiprows=1)
    return dict_v12_peak_err_sims


def calculate_stable_clustering_and_peak(modelname='F5', idsufix='_0', use_halofit=True):
    """
    modelname: {'F5', 'F6', 'N1', 'N5', 'GR'}
    idsufix: '_0' to be added to the filename in case of re-writing files
    Note:
    For GR we can only use MGCAMB-halofit.
    """
    # #  select one model at the time
    model = modelname

    # # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()

    r_root_z = []  # # empty list to save the root values
    v12_peak_z = []  # # empty list to store the peak values of v12
    r_peak_z = []  # # empty list to store the location of the peak

    # #--- READING ONE SNAPSHOT TO GET THE RANGE IN r FOR BETTER MATCHING
    v12_N1_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    r_40 = v12_GR_Z00_merged.r.values
    r_40_MG = v12_N1_Z03_merged.r.values

    # # hard-coded z-values
    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1,
         1.2, 1.5, 1.86, 1.9, 2])

    if model == 'GR':
        zvalues = np.round(HMredshifts, 2)  # # potential bug in LCDM case

    else:
        zvalues = np.round(HMredshifts, 4)  # #

    which_cosmology = cosmoELEPHANT

    # # cosmology, bias, nonlinear
    cosmo_args = which_cosmology, 1.0, True

    print('>>>> Start running v12 for all z-vals ')

    # # hard-coded r-range to avoid the first root (?)
    # # used to calculate r*a(z)*H(z) and to map the interpolating function for v12(r)
    r_spline = np.logspace(-0.3, 1.3, 500)

    for zval in zvalues:

        # # Hubble factor first:
        factor_Hr = calculate_rH(r_spline, zval)

        # # -----  v12(z, r) ----
        if model == 'GR':
            # ## CAMB HALOFIT
            rr, v12_z, aa, zz, xi_hf_z, dxida_hf_z = v12_from_numerical_deriv(
                cosmo_args, use_r_array=True, r_array=r_40,
                use_z_array=True,
                z_array=zvalues,
                MG=False,
                model='00',  # redundant
                rcH0=1.0,  # redundant
                F_R0=1e-06,  # redundant
                which_simulation_redshift=zval)

        elif model == 'N1':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='99',
                    rcH0=1.0,  # # nDGP N1
                    F_R0=1e-05,
                    which_simulation_redshift=zval)
            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)

        elif model == 'N5':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='99',
                    rcH0=5.0,  # # nDGP N1
                    F_R0=1e-05,
                    which_simulation_redshift=zval)
            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)

        elif model == 'F5':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='04',
                    rcH0=1.0,
                    F_R0=1e-05,  # # f(r) F5
                    which_simulation_redshift=zval)
            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)

        elif model == 'F6':
            if use_halofit:
                # ## CAMB HALOFIT
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv(
                    cosmo_args, use_r_array=True, r_array=r_40_MG,
                    z_array=zvalues,
                    use_z_array=True,
                    MG=True,
                    model='04',
                    rcH0=1.0,
                    F_R0=1e-06,  # # f(r) F6
                    which_simulation_redshift=zval)
            else:
                ### HALO MODEL SUHANI
                rr, v12_z, aa, zz, xi_hm_z, dxida_hm_z = v12_from_numerical_deriv_hm(
                    which_cosmology,
                    r_array_usr=r_40_MG, use_r_array=True,
                    r_args=None,
                    model=model,
                    which_simulation_redshift=zval)

        else:
            print("Option invalid. Please verify your inputs.")

        # ---- # finding the peak:
        # # Take the max as there is an abs()
        v12peak = np.abs(v12_z).max()

        id_peak = np.where(np.abs(v12_z) == v12peak)
        r_peak, v12peak = np.round(rr[id_peak][0], 3), np.round(v12peak, 3)
        r_peak_z = np.append(r_peak_z, r_peak)

        v12_peak_z = np.append(v12_peak_z, v12peak)

        # ---- # interpolating the v12(r) over the new r_range
        # # returns an interpolating function for v12(r)
        v12_of_r_spl = UnivariateSpline(rr, v12_z)

        # # mapping the interpolating function over the new array
        minus_v12_interp = -v12_of_r_spl(r_spline)

        # # relative differences between both arrays
        diff_array = np.abs(minus_v12_interp - factor_Hr)

        # To find the root we find the minimum value of the relative differences
        # and select the id of the array element for such case
        id_root = np.where(diff_array == diff_array.min())

        r_root, v12_root = r_spline[id_root][0], minus_v12_interp[id_root][0]
        r_root, v12_root = np.round(r_root, 3), np.round(v12_root, 3)

        # # update the list appending the root(z)
        r_root_z = np.append(r_root_z, r_root)

    print(
        'Done running v12, interpolating. Finding min & root for all z-s  <<<<< ')

    r_root_z_array = np.array(r_root_z)
    r_peak_z_array = np.array(r_peak_z)
    v12_peak_array = np.array(v12_peak_z)

    # create a data frame with the arrays stored
    PeakRstarDF = pd.DataFrame({'z_vals': zvalues,
                                'r_root': r_root_z_array,
                                'r_peak': r_peak_z_array,
                                'v12_peak': v12_peak_array})

    print(' ==== Done for model: ', modelname, ' ====== ')

    # ----------------- Saving  ---------------------

    path_tomake = '/home/jaber/shared/data/stable_clustering/'
    os.makedirs(path_tomake, exist_ok=True)

    full_file_name = path_tomake + modelname + idsufix + '.dat'
    PeakRstarDF.to_csv(full_file_name, sep=' ')

    print('Files saved in the new location: ', full_file_name)
    print('>>>>> ')

    print('The way of reading them is:  pd.read_csv(args, skiprows=1)')
    print('<<<<< ')

    return zz, r_root_z_array, r_peak_z_array, v12_peak_array


#### UNUSED FUNCTION
#### TO-DO: Use it in the function below
# def find_v12_min_values(df):
#     '''
#     Finds the min value of v12 in a given dataframe
#     Parameters
#     ----------
#     df: dataframe containing the simulation data
#
#     Returns
#     -------
#     v12_min
#     relative_error = Errv12_min / v12_min
#     '''
#     min_index = df['v12'].idxmin()
#     v12_min = df.loc[min_index].v12
#     Errv12_min = df.loc[min_index].Errv12
#     relative_error = Errv12_min / v12_min  # Calculate relative error
#     return v12_min, relative_error

## now we define a function to read the solutions generated with the function defined above:
# ### Reading the solutions
def read_solutions_rstar_v12peak(sufix='_HM'):
    '''

    Parameters
    ----------
    sufix: str : _HF for the solutions using Halofit, _HM for the solutions using Halomodel

    Returns
    -------

    '''

    # Define the models you want to read
    models = ["GR", "F5", "F6", "N1", "N5"]
    path_solutions_Rs = '/home/jaber/shared/data/stable_clustering/'

    # Initialize an empty dictionary to store the DataFrames
    dict_model_Rs_vpeak = {}

    # Iterate over the models and Read the data
    for model in models:
        filename = path_solutions_Rs + model + sufix + '.dat'
        df = pd.read_csv(filename, sep='\s+', comment='#', names=["z", "Rs", "rPeak", "v12Peak"], skiprows=1)
        dict_model_Rs_vpeak[model] = df

    pd_dict = dict_model_Rs_vpeak

    # Now, peakRstarDF_dict contains DataFrames for all models, accessible by model name
    # peakRstarDF_dict["GR"], peakRstarDF_dict["F5"], ..., with columns "z", "Rs", "rPeak", "v12Peak"
    return pd_dict


def v12peak_sim_data():
    '''
    Find the v12 min from the simulation data and return the value and error
    '''

    print('>>> Reading the simulation data arrays: GR and MG ')
    # ---------- READING DATA       -------------- #

    path_to_sims = '/home/jaber/shared/data/output_v12_DM_merged/'

    cases = [
        ("GR", ["z0.0", "z0.3", "z0.5"]),
        ("F5", ["z0.0", "z0.3", "z0.5"]),
        ("F6", ["z0.0", "z0.3", "z0.5"]),
        ("N5", ["z0.0", "z0.3", "z0.5"]),
        ("N1", ["z0.0", "z0.3", "z0.5"])
    ]

    v12_merged_data = {}

    for prefix, redshifts in cases:
        v12_merged_data[prefix] = {}

        for redshift in redshifts:
            path = f'{path_to_sims}{prefix}_{redshift}/v12AvgMerged.dat'
            v12_merged_data[prefix][redshift] = read_v12_sim_merged_data(path)

    v12_GR = []
    GR_Z00_min_index = v12_merged_data['GR']['z0.0']['v12'].idxmin()
    v12PeakGRz00_v12 = v12_merged_data['GR']['z0.0'].loc[GR_Z00_min_index].v12
    v12PeakGRz00_Err = v12_merged_data['GR']['z0.0'].loc[GR_Z00_min_index].Errv12

    GR_Z03_min_index = v12_merged_data['GR']['z0.3']['v12'].idxmin()
    v12PeakGRz03_v12 = v12_merged_data['GR']['z0.3'].loc[GR_Z03_min_index].v12
    v12PeakGRz03_Err = v12_merged_data['GR']['z0.3'].loc[GR_Z03_min_index].Errv12

    GR_Z05_min_index = v12_merged_data['GR']['z0.5']['v12'].idxmin()
    v12PeakGRz05_v12 = v12_merged_data['GR']['z0.5'].loc[GR_Z05_min_index].v12
    v12PeakGRz05_Err = v12_merged_data['GR']['z0.5'].loc[GR_Z05_min_index].Errv12


    v12_GR.append((v12PeakGRz00_v12, v12PeakGRz03_v12, v12PeakGRz05_v12,
                   v12PeakGRz00_Err, v12PeakGRz03_Err, v12PeakGRz05_Err))

    v12_F5 = []
    F5_Z00_min_index = v12_merged_data['F5']['z0.0']['v12'].idxmin()
    v12PeakF5z00_v12 = v12_merged_data['F5']['z0.0'].loc[F5_Z00_min_index].v12
    v12PeakF5z00_Err = v12_merged_data['F5']['z0.0'].loc[F5_Z00_min_index].Errv12

    F5_Z03_min_index = v12_merged_data['F5']['z0.3']['v12'].idxmin()
    v12PeakF5z03_v12 = v12_merged_data['F5']['z0.3'].loc[F5_Z03_min_index].v12
    v12PeakF5z03_Err = v12_merged_data['F5']['z0.3'].loc[F5_Z03_min_index].Errv12

    F5_Z05_min_index = v12_merged_data['F5']['z0.5']['v12'].idxmin()
    v12PeakF5z05_v12 = v12_merged_data['F5']['z0.5'].loc[F5_Z05_min_index].v12
    v12PeakF5z05_Err = v12_merged_data['F5']['z0.5'].loc[F5_Z05_min_index].Errv12

    v12_F5.append((v12PeakF5z00_v12, v12PeakF5z03_v12, v12PeakF5z05_v12,
                   v12PeakF5z00_Err, v12PeakF5z03_Err, v12PeakF5z05_Err))

    v12_F6 = []
    F6_Z00_min_index = v12_merged_data['F6']['z0.0']['v12'].idxmin()
    v12PeakF6z00_v12 = v12_merged_data['F6']['z0.0'].loc[F6_Z00_min_index].v12
    v12PeakF6z00_Err = v12_merged_data['F6']['z0.0'].loc[F6_Z00_min_index].Errv12

    F6_Z03_min_index = v12_merged_data['F6']['z0.3']['v12'].idxmin()
    v12PeakF6z03_v12 = v12_merged_data['F6']['z0.3'].loc[F6_Z03_min_index].v12
    v12PeakF6z03_Err = v12_merged_data['F6']['z0.3'].loc[F6_Z03_min_index].Errv12

    F6_Z05_min_index = v12_merged_data['F6']['z0.5']['v12'].idxmin()
    v12PeakF6z05_v12 = v12_merged_data['F6']['z0.5'].loc[F6_Z05_min_index].v12
    v12PeakF6z05_Err = v12_merged_data['F6']['z0.5'].loc[F6_Z05_min_index].Errv12

    v12_F6.append((v12PeakF6z00_v12, v12PeakF6z03_v12, v12PeakF6z05_v12,
                   v12PeakF6z00_Err, v12PeakF6z03_Err, v12PeakF6z05_Err))

    v12_N1 = []
    N1_Z00_min_index = v12_merged_data['N1']['z0.0']['v12'].idxmin()
    v12PeakN1z00_v12 = v12_merged_data['N1']['z0.0'].loc[N1_Z00_min_index].v12
    v12PeakN1z00_Err = v12_merged_data['N1']['z0.0'].loc[N1_Z00_min_index].Errv12

    N1_Z03_min_index = v12_merged_data['N1']['z0.3']['v12'].idxmin()
    v12PeakN1z03_v12 = v12_merged_data['N1']['z0.3'].loc[N1_Z03_min_index].v12
    v12PeakN1z03_Err = v12_merged_data['N1']['z0.3'].loc[N1_Z03_min_index].Errv12

    N1_Z05_min_index = v12_merged_data['N1']['z0.5']['v12'].idxmin()
    v12PeakN1z05_v12 = v12_merged_data['N1']['z0.5'].loc[N1_Z05_min_index].v12
    v12PeakN1z05_Err = v12_merged_data['N1']['z0.5'].loc[N1_Z05_min_index].Errv12

    v12_N1.append((v12PeakN1z00_v12, v12PeakN1z03_v12, v12PeakN1z05_v12,
                   v12PeakN1z00_Err, v12PeakN1z03_Err, v12PeakN1z05_Err))

    v12_N5 = []
    N5_Z00_min_index = v12_merged_data['N5']['z0.0']['v12'].idxmin()
    v12PeakN5z00_v12 = v12_merged_data['N5']['z0.0'].loc[N5_Z00_min_index].v12
    v12PeakN5z00_Err = v12_merged_data['N5']['z0.0'].loc[N5_Z00_min_index].Errv12

    N5_Z03_min_index = v12_merged_data['N5']['z0.3']['v12'].idxmin()
    v12PeakN5z03_v12 = v12_merged_data['N5']['z0.3'].loc[N5_Z03_min_index].v12
    v12PeakN5z03_Err = v12_merged_data['N5']['z0.3'].loc[N5_Z03_min_index].Errv12

    N5_Z05_min_index = v12_merged_data['N5']['z0.5']['v12'].idxmin()
    v12PeakN5z05_v12 = v12_merged_data['N5']['z0.5'].loc[N5_Z05_min_index].v12
    v12PeakN5z05_Err = v12_merged_data['N5']['z0.5'].loc[N5_Z05_min_index].Errv12

    v12_N5.append((v12PeakN5z00_v12, v12PeakN5z03_v12, v12PeakN5z05_v12,
                   v12PeakN5z00_Err, v12PeakN5z03_Err, v12PeakN5z05_Err))

    v12_GR = np.array(v12_GR).flatten()
    v12_F5 = np.array(v12_F5).flatten()
    v12_F6 = np.array(v12_F6).flatten()
    v12_N5 = np.array(v12_N5).flatten()
    v12_N1 = np.array(v12_N1).flatten()

    zvals = 0, 0.3, 0.5

    return zvals, v12_GR, v12_F5, v12_F6, v12_N1, v12_N5


# def rstar_sim_data_bis():
#     '''
#     Find the rstar from the simulation data and return the value and error
#     '''
#
#     print('>>> Reading the simulation data arrays: GR and MG ')
#     # ---------- READING DATA       -------------- #
#
#     path_to_sims = '/home/jaber/shared/data/output_v12_DM_merged/'
#
#     cases = [
#         ("GR", ["z0.0", "z0.3", "z0.5"]),
#         ("F5", ["z0.0", "z0.3", "z0.5"]),
#         ("F6", ["z0.0", "z0.3", "z0.5"]),
#         ("N5", ["z0.0", "z0.3", "z0.5"]),
#         ("N1", ["z0.0", "z0.3", "z0.5"])
#     ]
#
#     v12_merged_sims_data = {}
#
#     for prefix, redshifts in cases:
#         v12_merged_sims_data[prefix] = {}
#
#         for redshift in redshifts:
#             path = f'{path_to_sims}{prefix}_{redshift}/v12AvgMerged.dat'
#             v12_merged_sims_data[prefix][redshift] = read_v12_sim_merged_data(path)
#
#     # Add spline to interpolate the simulation data
#     r_spline = np.logspace(-0.3, 1.3, 500)
#
#     Rs_GR = []
#     # GR_Z00_min_index = v12_merged_sims_data['GR']['z0.0']['v12'].idxmin()
#     # v12PeakGRz00_v12 = v12_merged_sims_data['GR']['z0.0'].loc[GR_Z00_min_index].v12
#     # v12PeakGRz00_Err = v12_merged_sims_data['GR']['z0.0'].loc[GR_Z00_min_index].Errv12
#     #
#     # GR_Z03_min_index = v12_merged_sims_data['GR']['z0.3']['v12'].idxmin()
#     # v12PeakGRz03_v12 = v12_merged_sims_data['GR']['z0.3'].loc[GR_Z03_min_index].v12
#     # v12PeakGRz03_Err = v12_merged_sims_data['GR']['z0.3'].loc[GR_Z03_min_index].Errv12
#     #
#     # GR_Z05_min_index = v12_merged_sims_data['GR']['z0.5']['v12'].idxmin()
#     # v12PeakGRz05_v12 = v12_merged_sims_data['GR']['z0.5'].loc[GR_Z05_min_index].v12
#     # v12PeakGRz05_Err = v12_merged_sims_data['GR']['z0.5'].loc[GR_Z05_min_index].Errv12
#     #
#     # Rs_GR.append((v12PeakGRz00_v12, v12PeakGRz03_v12, v12PeakGRz05_v12,
#     #                v12PeakGRz00_Err, v12PeakGRz03_Err, v12PeakGRz05_Err))
#
#     Rs_F5 = []
#     # F5_Z00_min_index = v12_merged_sims_data['F5']['z0.0']['v12'].idxmin()
#     # v12PeakF5z00_v12 = v12_merged_sims_data['F5']['z0.0'].loc[F5_Z00_min_index].v12
#     # v12PeakF5z00_Err = v12_merged_sims_data['F5']['z0.0'].loc[F5_Z00_min_index].Errv12
#     #
#     # F5_Z03_min_index = v12_merged_sims_data['F5']['z0.3']['v12'].idxmin()
#     # v12PeakF5z03_v12 = v12_merged_sims_data['F5']['z0.3'].loc[F5_Z03_min_index].v12
#     # v12PeakF5z03_Err = v12_merged_sims_data['F5']['z0.3'].loc[F5_Z03_min_index].Errv12
#     #
#     # F5_Z05_min_index = v12_merged_sims_data['F5']['z0.5']['v12'].idxmin()
#     # v12PeakF5z05_v12 = v12_merged_sims_data['F5']['z0.5'].loc[F5_Z05_min_index].v12
#     # v12PeakF5z05_Err = v12_merged_sims_data['F5']['z0.5'].loc[F5_Z05_min_index].Errv12
#     #
#     # Rs_F5.append((v12PeakF5z00_v12, v12PeakF5z03_v12, v12PeakF5z05_v12,
#     #                v12PeakF5z00_Err, v12PeakF5z03_Err, v12PeakF5z05_Err))
#
#     Rs_F6 = []
#     # F6_Z00_min_index = v12_merged_sims_data['F6']['z0.0']['v12'].idxmin()
#     # v12PeakF6z00_v12 = v12_merged_sims_data['F6']['z0.0'].loc[F6_Z00_min_index].v12
#     # v12PeakF6z00_Err = v12_merged_sims_data['F6']['z0.0'].loc[F6_Z00_min_index].Errv12
#     #
#     # F6_Z03_min_index = v12_merged_sims_data['F6']['z0.3']['v12'].idxmin()
#     # v12PeakF6z03_v12 = v12_merged_sims_data['F6']['z0.3'].loc[F6_Z03_min_index].v12
#     # v12PeakF6z03_Err = v12_merged_sims_data['F6']['z0.3'].loc[F6_Z03_min_index].Errv12
#     #
#     # F6_Z05_min_index = v12_merged_sims_data['F6']['z0.5']['v12'].idxmin()
#     # v12PeakF6z05_v12 = v12_merged_sims_data['F6']['z0.5'].loc[F6_Z05_min_index].v12
#     # v12PeakF6z05_Err = v12_merged_sims_data['F6']['z0.5'].loc[F6_Z05_min_index].Errv12
#     #
#     # Rs_F6.append((v12PeakF6z00_v12, v12PeakF6z03_v12, v12PeakF6z05_v12,
#     #                v12PeakF6z00_Err, v12PeakF6z03_Err, v12PeakF6z05_Err))
#
#     Rs_N1 = []
#     # N1_Z00_min_index = v12_merged_sims_data['N1']['z0.0']['v12'].idxmin()
#     # v12PeakN1z00_v12 = v12_merged_sims_data['N1']['z0.0'].loc[N1_Z00_min_index].v12
#     # v12PeakN1z00_Err = v12_merged_sims_data['N1']['z0.0'].loc[N1_Z00_min_index].Errv12
#     #
#     # N1_Z03_min_index = v12_merged_sims_data['N1']['z0.3']['v12'].idxmin()
#     # v12PeakN1z03_v12 = v12_merged_sims_data['N1']['z0.3'].loc[N1_Z03_min_index].v12
#     # v12PeakN1z03_Err = v12_merged_sims_data['N1']['z0.3'].loc[N1_Z03_min_index].Errv12
#     #
#     # N1_Z05_min_index = v12_merged_sims_data['N1']['z0.5']['v12'].idxmin()
#     # v12PeakN1z05_v12 = v12_merged_sims_data['N1']['z0.5'].loc[N1_Z05_min_index].v12
#     # v12PeakN1z05_Err = v12_merged_sims_data['N1']['z0.5'].loc[N1_Z05_min_index].Errv12
#     #
#     # Rs_N1.append((v12PeakN1z00_v12, v12PeakN1z03_v12, v12PeakN1z05_v12,
#     #                v12PeakN1z00_Err, v12PeakN1z03_Err, v12PeakN1z05_Err))
#
#     Rs_N5 = []
#     # N5_Z00_min_index = v12_merged_sims_data['N5']['z0.0']['v12'].idxmin()
#     # v12PeakN5z00_v12 = v12_merged_sims_data['N5']['z0.0'].loc[N5_Z00_min_index].v12
#     # v12PeakN5z00_Err = v12_merged_sims_data['N5']['z0.0'].loc[N5_Z00_min_index].Errv12
#     #
#     # N5_Z03_min_index = v12_merged_sims_data['N5']['z0.3']['v12'].idxmin()
#     # v12PeakN5z03_v12 = v12_merged_sims_data['N5']['z0.3'].loc[N5_Z03_min_index].v12
#     # v12PeakN5z03_Err = v12_merged_sims_data['N5']['z0.3'].loc[N5_Z03_min_index].Errv12
#     #
#     # N5_Z05_min_index = v12_merged_sims_data['N5']['z0.5']['v12'].idxmin()
#     # v12PeakN5z05_v12 = v12_merged_sims_data['N5']['z0.5'].loc[N5_Z05_min_index].v12
#     # v12PeakN5z05_Err = v12_merged_sims_data['N5']['z0.5'].loc[N5_Z05_min_index].Errv12
#     #
#     # Rs_N5.append((v12PeakN5z00_v12, v12PeakN5z03_v12, v12PeakN5z05_v12,
#     #                v12PeakN5z00_Err, v12PeakN5z03_Err, v12PeakN5z05_Err))
#
#     Rs_GR = np.array(Rs_GR).flatten()
#     Rs_F5 = np.array(Rs_F5).flatten()
#     Rs_F6 = np.array(Rs_F6).flatten()
#     Rs_N5 = np.array(Rs_N5).flatten()
#     Rs_N1 = np.array(Rs_N1).flatten()
#
#     zvals = 0, 0.3, 0.5
#
#     return zvals, Rs_GR, Rs_F5, Rs_F6, Rs_N1, Rs_N5


def rstar_sim_data():
    '''
    Returns arrays for zval and rstar from each model from the simulation data.

    The function reads simulation data arrays and calculates the minimum 'r' values for each case.

    Returns:
    min_r_values (dict): A dictionary containing the minimum 'r' values for each case.
    '''

    # ---------- READING DATA -------------- #

    path_to_sims = '/home/jaber/shared/data/output_v12_DM_merged/'

    cases = [
        ("GR", ["z0.0", "z0.3", "z0.5"], [0, 0.3, 0.5]),
        ("F5", ["z0.0", "z0.3", "z0.5"], [0, 0.3, 0.5]),
        ("F6", ["z0.0", "z0.3", "z0.5"], [0, 0.3, 0.5]),
        ("N5", ["z0.0", "z0.3", "z0.5"], [0, 0.3, 0.5]),
        ("N1", ["z0.0", "z0.3", "z0.5"], [0, 0.3, 0.5])
    ]

    # Add spline to interpolate the simulation data
    r_spline = np.logspace(-0.3, 1.3, 500)

    # Initialize a dictionary to store min_r values for each case
    rstar_values_dict = {}

    for model_label, redshifts, z_snap in cases:
        rstar_values_dict[model_label] = {}

        for redshift, zval in zip(redshifts, z_snap):
            path = f'{path_to_sims}{model_label}_{redshift}/v12AvgMerged.dat'
            v12_z_sim = read_v12_sim_merged_data(path)

            factor_Hr = calculate_rH(r_spline, zval)
            factor_Hr_sim = calculate_rH(v12_z_sim['r'].values, zval)

            ## Manually add one column to the dataframe to contain the rH values
            v12_z_sim['rH'] = factor_Hr_sim

            # ---- # interpolating the v12(r) over the new r_range
            # # returns an interpolating function for v12(r)
            rr = v12_z_sim['r'].values
            v12_z_sim_val = v12_z_sim['v12'].values
            v12_of_r_sim_spl = UnivariateSpline(rr, v12_z_sim_val)

            # # mapping the interpolating function over the new array
            minus_v12_interp = -v12_of_r_sim_spl(r_spline)

            # # relative differences between both arrays
            diff_array = np.abs(minus_v12_interp - factor_Hr)

            # to find the root we find the minimum value of the relative differences
            # and select the id of the array element for such case
            rstar_index = np.where(diff_array == diff_array.min())

            rstar_val, v12_star = r_spline[rstar_index][0], minus_v12_interp[rstar_index][0]
            rstar_val, v12_star = np.round(rstar_val, 3), np.round(v12_star, 3)

            # To find the errors we use the simulation data (non interpolated)
            # Filter the simulation DataFrame to exclude rows where r < 1
            filtered_df = v12_z_sim[v12_z_sim['r'] >= 1]
            # Find the value of 'r' for which abs(-v12 - rH) is the minimum in the filtered DataFrame
            rstar_index_no_interp = (filtered_df['v12'] + filtered_df['rH']).abs().idxmin()
            # Calculate associated error
            # we will use the 'square-errors' using the v12 relative error for the Rstar value
            r_star_err_num = filtered_df.loc[rstar_index_no_interp, 'Errv12']
            r_star_err_den = filtered_df.loc[rstar_index_no_interp, 'v12']
            r_star_err = np.abs(r_star_err_num / r_star_err_den)

            rstar_values_dict[model_label][redshift] = {
                'Rs': rstar_val,
                'ErrRs': r_star_err
            }

    Rs_GR = []
    Rs_F5 = []
    Rs_F6 = []
    Rs_N1 = []
    Rs_N5 = []

    Rs_GR.append((rstar_values_dict['GR']['z0.0']['Rs'], rstar_values_dict['GR']['z0.3']['Rs'],
                  rstar_values_dict['GR']['z0.5']['Rs'],
                  rstar_values_dict['GR']['z0.0']['ErrRs'],
                  rstar_values_dict['GR']['z0.3']['ErrRs'], rstar_values_dict['GR']['z0.5']['ErrRs']))

    Rs_F5.append((rstar_values_dict['F5']['z0.0']['Rs'], rstar_values_dict['F5']['z0.3']['Rs'],
                  rstar_values_dict['F5']['z0.5']['Rs'],
                  rstar_values_dict['F5']['z0.0']['ErrRs'],
                  rstar_values_dict['F5']['z0.3']['ErrRs'], rstar_values_dict['F5']['z0.5']['ErrRs']))
  
    Rs_F6.append((rstar_values_dict['F6']['z0.0']['Rs'], rstar_values_dict['F6']['z0.3']['Rs'],
                  rstar_values_dict['F6']['z0.5']['Rs'],
                  rstar_values_dict['F6']['z0.0']['ErrRs'],
                  rstar_values_dict['F6']['z0.3']['ErrRs'], rstar_values_dict['F6']['z0.5']['ErrRs']))

    Rs_N1.append((rstar_values_dict['N1']['z0.0']['Rs'], rstar_values_dict['N1']['z0.3']['Rs'],
                  rstar_values_dict['N1']['z0.5']['Rs'],
                  rstar_values_dict['N1']['z0.0']['ErrRs'],
                  rstar_values_dict['N1']['z0.3']['ErrRs'], rstar_values_dict['N1']['z0.5']['ErrRs']))

    Rs_N5.append((rstar_values_dict['N5']['z0.0']['Rs'], rstar_values_dict['N5']['z0.3']['Rs'],
                  rstar_values_dict['N5']['z0.5']['Rs'],
                  rstar_values_dict['N5']['z0.0']['ErrRs'],
                  rstar_values_dict['N5']['z0.3']['ErrRs'], rstar_values_dict['N5']['z0.5']['ErrRs']))


    Rs_GR = np.array(Rs_GR).flatten()
    Rs_F5 = np.array(Rs_F5).flatten()
    Rs_F6 = np.array(Rs_F6).flatten()
    Rs_N1 = np.array(Rs_N1).flatten()
    Rs_N5 = np.array(Rs_N5).flatten()


    zvals = 0, 0.3, 0.5

    # return  rstar_values_dict
    return zvals, Rs_GR, Rs_F5, Rs_F6, Rs_N1, Rs_N5

# def rstar_sim_data_old(sufix='_PLOT'):
#     '''
#     DEPRECATED FUNCTION (AS THIS USES THE MODEL TO INTERPOLATE)
#     '''
#     print('>>> Reading the simulation data arrays: GR and MG ')
#     # ---------- READING DATA       -------------- #
#
#     path_to_sims = '/home/jaber/shared/data/output_v12_DM_merged/'
#
#     cases = [
#         ("GR", ["z0.0", "z0.3", "z0.5"]),
#         ("F5", ["z0.0", "z0.3", "z0.5"]),
#         ("F6", ["z0.0", "z0.3", "z0.5"]),
#         ("N5", ["z0.0", "z0.3", "z0.5"]),
#         ("N1", ["z0.0", "z0.3", "z0.5"])
#     ]
#
#     v12_merged_data = {}
#
#     for model_label, redshifts in cases:
#         v12_merged_data[model_label] = {}
#
#         for redshift in redshifts:
#             path = f'{path_to_sims}{model_label}_{redshift}/v12AvgMerged.dat'
#             v12_merged_data[model_label][redshift] = read_v12_sim_merged_data(path)
#
#     # ----- ### Reading the solutions
#
#     # Define the models you want to read data for
#     models = ["GR", "F5", "F6", "N1", "N5"]
#     path_solutions_Rs = '/home/jaber/shared/data/stable_clustering/'
#
#     # Initialize an empty dictionary to store the DataFrames
#     peakRstarDF_dict = {}
#
#     # Iterate over the models and read the data
#     #### DEPRECATED FUNCTION FOR THIS REASON:
#     #### HERE WE ARE USING THE SOLUTIONS OF RS TO FIND THE RS IN THE DATA
#     #### CLEARLY NOT WHAT WE WANTED
#     for model in models:
#         filename = path_solutions_Rs + model + sufix + '.dat'
#         df = pd.read_csv(filename, sep='\s+', comment='#', names=["z", "Rs", "rPeak", "v12Peak"], skiprows=1)
#         peakRstarDF_dict[model] = df
#
#     # Now, peakRstarDF_dict contains DataFrames for all models, accessible by model name
#     # peakRstarDF_dict["GR"], peakRstarDF_dict["F5"], ...
#
#     z_snapshots = np.array([0, 0.297, 0.5])
#     idx_snapshots = np.array([0, 5, 8])
#
#     # Define the data and cases
#     data_cases = [
#         ('GR', peakRstarDF_dict['GR'].Rs.values[idx_snapshots],
#          [v12_merged_data['GR']['z0.0'], v12_merged_data['GR']['z0.3'], v12_merged_data['GR']['z0.5']]),
#         ('F5', peakRstarDF_dict['F5'].Rs.values[idx_snapshots],
#          [v12_merged_data['F5']['z0.0'], v12_merged_data['F5']['z0.3'], v12_merged_data['F5']['z0.5']]),
#         ('F6', peakRstarDF_dict['F6'].Rs.values[idx_snapshots],
#          [v12_merged_data['F6']['z0.0'], v12_merged_data['F6']['z0.3'], v12_merged_data['F6']['z0.5']]),
#         ('N1', peakRstarDF_dict['N1'].Rs.values[idx_snapshots],
#          [v12_merged_data['N1']['z0.0'], v12_merged_data['N1']['z0.3'], v12_merged_data['N1']['z0.5']]),
#         ('N5', peakRstarDF_dict['N5'].Rs.values[idx_snapshots],
#          [v12_merged_data['N5']['z0.0'], v12_merged_data['N5']['z0.3'], v12_merged_data['N5']['z0.5']]),
#     ]
#
#     # Initialize a dictionary to store associated errors for each model
#     associated_error_r_root_dict = {}
#
#     # Loop through data cases
#     for model_name, PeakRstarDF, v12_dfs in data_cases:
#         r_root_values = PeakRstarDF
#         closest_indices_r_root_model = []
#         associated_error_r_root_dict[model_name] = []
#
#         # Loop through different redshifts
#         for i, v12_df in enumerate(v12_dfs):
#             closest_index = np.abs(v12_df['r'] - r_root_values[i]).idxmin()
#             ### we will use the 'square-errors' using the v12 relative error for the Rstar value
#             r_root_err_num = v12_df.iloc[closest_index].Errv12
#             r_root_err_den = v12_df.iloc[closest_index].v12
#             r_root_err = r_root_err_num / r_root_err_den
#             associated_error_r_root_dict[model_name].append((r_root_values[i], r_root_err))
#
#     # # Convert the lists of associated errors to numpy arrays
#     for model_name in associated_error_r_root_dict:
#         associated_error_r_root_dict[model_name] = np.array(associated_error_r_root_dict[model_name])
#
#     zvals = z_snapshots
#
#     return zvals, associated_error_r_root_dict
