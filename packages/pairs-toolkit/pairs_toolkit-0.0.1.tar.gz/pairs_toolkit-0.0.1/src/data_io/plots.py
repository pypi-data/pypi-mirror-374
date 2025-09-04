# =============================================================================#
# coding: utf-8
# Mariana Jaber 2022
# Description:  Script to make the plots for the papers
# =============================================================================#

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
import pandas as pd
import itertools

from read_data import *
from ..model.v12_num_deriv_of_xi import *
from ..model.simulation_driven_dudeg import v12_from_numerical_deriv_hm
from ..cosmology.approx_v12 import *
from merge_sims import *
from cosmology import define_cosmology
from cosmology import *
from ..cosmology.constants import OMEGAB0H2, OMEGAC0H2, REDUCED_H0, AS
from ..model.stable_clustering import v12peak_sim_data, rstar_sim_data, read_solutions_rstar_v12peak, \
    read_solutions_rstar_v12peak  # v12peak_sim_data, rstar_sim_data, read_solutions_rstar_v12peak


## Pretty plots
class FancyFormatter(Formatter):
    """Formater for values with LaTeX fonts."""

    def __call__(self, v, pos=None):
        return r'${:.5G}$'.format(v)

    def format_data_short(self, value):
        return '{:.1f}'.format(value)


cosmoELEPHANT = define_cosmology()


def figure_1(fig_path='/home/jaber/shared/data/figs/', fig_name='fig1_v12_GR_scr',
             fig_type='.pdf', save_figure=False):
    '''
    This  contains CLPT, Juszkiewicz quasilinear solution, Linear solution and Halofit solution
    for every snapshot in the GR case.
    In the top panel we show r in 0.1-140Mpc/h  in linear scale, the middle row has a zoom-in in 0.1-40 Mpc/h scales,
    and the bottom row is the ratio between models and data from simulations.
    Returns
    -------

    '''

    ## before doing anything: read the params and warn if we're saving or not the fig in the right name/path

    # print('---- SAVING FIG  -----')
    ## Read these params from the user
    figpath = fig_path
    figname = fig_name
    fig_ext = fig_type
    dpi = 1200
    full_fig_name = figpath + figname + str(fig_ext)

    if save_figure:

        print('The figure will be saved at', full_fig_name)
    else:
        print('The figure will NOT be saved. The params were: ', full_fig_name)

    # ---------- SPECS FOR MODELS ---------------- #
    # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()
    cosmo_args = cosmoELEPHANT, 1.0, True
    cosmo_args_lin = cosmoELEPHANT, 1.0, False
    ## --- logarithmic redshift range

    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1,
         1.2, 1.5, 1.86, 1.9, 2])

    HMredshifts = np.round(HMredshifts, 4)

    z_vals = HMredshifts

    # ---------- READING DATA       -------------- #
    v12_GR_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    r_40 = v12_GR_Z00_merged.r.values

    path_large_scales = '/home/jaber/velocities/velocities/data/output_rmax140/'

    v12GRz00large_file = path_large_scales + 'GR_z0.0/v12Avg.dat'
    v12GRz03large_file = path_large_scales + 'GR_z0.3/v12Avg.dat'
    v12GRz05large_file = path_large_scales + 'GR_z0.5/v12Avg.dat'

    V12_GR_R140_z00 = pd.read_csv(v12GRz00large_file, sep='\s+', comment='#',
                                  names=["r", "v12", "Errv12"])

    V12_GR_R140_z03 = pd.read_csv(v12GRz03large_file, sep='\s+', comment='#',
                                  names=["r", "v12", "Errv12"])

    V12_GR_R140_z05 = pd.read_csv(v12GRz05large_file, sep='\s+', comment='#',
                                  names=["r", "v12", "Errv12"])

    r_args_140 = V12_GR_R140_z00['r'].min(), V12_GR_R140_z00['r'].max(), \
        V12_GR_R140_z00['r'].size

    # ---------- READING CLPT MODEL -------------- #
    v12clpt140 = read_clpt(rmax=140)
    v12clpt40 = read_clpt(rmax=40)

    print('>>>> Done reading data <<<< ')

    #### ---------  H(z) function and linear growth function -------- #########
    zi, zii, ziii = 0, 0.3, 0.5

    ai, aii, aiii = scalefactor_from_redshift(zi), scalefactor_from_redshift(
        zii), scalefactor_from_redshift(ziii)
    Hofzi, Hofzii, Hofziii = hubble_flat(zi, cosmoELEPHANT), hubble_flat(zii,
                                                                         cosmoELEPHANT), hubble_flat(
        ziii,
        cosmoELEPHANT)
    flin, fliin, fliiin = OmegaM_z(zi, cosmoELEPHANT) ** (6 / 11), OmegaM_z(zii,
                                                                            cosmoELEPHANT) ** (
                                  6 / 11), OmegaM_z(
        ziii, cosmoELEPHANT) ** (6 / 11)
    ####

    v12_clpt_140_00 = v12clpt140[0]['z0.0'].v12 * ai * Hofzi * flin
    v12_clpt_140_03 = v12clpt140[0]['z0.3'].v12 * aii * Hofzii * fliin
    v12_clpt_140_05 = v12clpt140[0]['z0.5'].v12 * aiii * Hofziii * fliiin

    v12_clpt_40_00 = v12clpt40[0]['z0.0'].v12 * ai * Hofzi * flin
    v12_clpt_40_03 = v12clpt40[0]['z0.3'].v12 * aii * Hofzii * fliin
    v12_clpt_40_05 = v12clpt40[0]['z0.5'].v12 * aiii * Hofziii * fliiin

    # ---------- RUNNING LIN & HF MODELS --------- #

    ## 140 Mpc/h
    print('>>>> Start running large scales   ')

    r140, v12_hf_r140_z00, aa, zz, xi_hf_r140_z00, dxida_hf_r140_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r140, v12_hf_r140_z03, aa, zz, xi_hf_r140_z03, dxida_hf_r140_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.33)

    r140, v12_hf_r140_z05, aa, zz, xi_hf_r140_z05, dxida_hf_r140_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    ##### linear  #######

    r140, v12_lin_r140_z00, aa, zz, xi_lin_r140_z00, dxida_lin_r140_z00 = v12_from_numerical_deriv(
        cosmo_args_lin, use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r140, v12_lin_r140_z03, aa, zz, xi_lin_r140_z03, dxida_lin_r140_z03 = v12_from_numerical_deriv(
        cosmo_args_lin,
        use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.3)

    r140, v12_lin_r140_z05, aa, zz, xi_lin_r140_z05, dxida_lin_r140_z05 = v12_from_numerical_deriv(
        cosmo_args_lin,
        use_r_array=False, r_array=None,
        z_array=z_vals,
        use_z_array=True,
        r_args=r_args_140,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    # ---------- RUN QUASILINEAR MODEL ----------- #

    r140, v12_qlin_r140_z00 = v12_approx(cosmo_args_lin,
                                         use_r_array=False, r_array=None,
                                         z_array=z_vals,
                                         use_z_array=True,
                                         r_args=r_args_140,
                                         which_simulation_redshift=0.0)

    r140, v12_qlin_r140_z03 = v12_approx(cosmo_args_lin,
                                         use_r_array=False, r_array=None,
                                         z_array=z_vals,
                                         use_z_array=True,
                                         r_args=r_args_140,
                                         which_simulation_redshift=0.3)

    r140, v12_qlin_r140_z05 = v12_approx(cosmo_args_lin,
                                         use_r_array=False, r_array=None,
                                         z_array=z_vals,
                                         use_z_array=True,
                                         r_args=r_args_140,
                                         which_simulation_redshift=0.5)
    print('Done running large scales  <<<<< ')

    print('>>>> Start running interm scales   ')

    r40, v12_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r40, v12_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.33)  ### mind this value!

    r40, v12_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    ##### linear  #######

    r40, v12_lin_r40_z00, aa, zz, xi_lin_r40_z00, dxida_lin_r40_z00 = v12_from_numerical_deriv(
        cosmo_args_lin, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r40, v12_lin_r40_z03, aa, zz, xi_lin_r40_z03, dxida_lin_r40_z03 = v12_from_numerical_deriv(
        cosmo_args_lin,
        use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.3)

    r40, v12_lin_r40_z05, aa, zz, xi_lin_r40_z05, dxida_lin_r40_z05 = v12_from_numerical_deriv(
        cosmo_args_lin,
        use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    # ---------- RUN QUASILINEAR MODEL ----------- #

    r40, v12_qlin_r40_z00 = v12_approx(cosmo_args, z_array=z_vals, r_array=r_40,
                                       r_args=None,
                                       use_r_array=True,
                                       use_z_array=True, z_args=None,
                                       redshift_simulation=[0, 0.3, 0.5, 1],
                                       which_simulation_redshift=0.0
                                       # CAMB_path="/opt/cosmo_data/",
                                       # CAMB_outputdir_Pk="/home/jaber/shared/data/output_Pk_camb/",
                                       # MG=False, model='00', rcH0=1.000, F_R0=0.00001
                                       )

    r40, v12_qlin_r40_z03 = v12_approx(cosmo_args, z_array=z_vals, r_array=r_40,
                                       r_args=None,
                                       use_r_array=True,
                                       use_z_array=True, z_args=None,
                                       redshift_simulation=[0, 0.3, 0.5, 1],
                                       which_simulation_redshift=0.3
                                       # CAMB_path="/opt/cosmo_data/",
                                       # CAMB_outputdir_Pk="/home/jaber/shared/data/output_Pk_camb/",
                                       # MG=False, model='00', rcH0=1.000, F_R0=0.00001
                                       )

    r40, v12_qlin_r40_z05 = v12_approx(cosmo_args, z_array=z_vals, r_array=r_40,
                                       r_args=None,
                                       use_r_array=True,
                                       use_z_array=True, z_args=None,
                                       redshift_simulation=[0, 0.3, 0.5, 1],
                                       which_simulation_redshift=0.5
                                       # CAMB_path="/opt/cosmo_data/",
                                       # CAMB_outputdir_Pk="/home/jaber/shared/data/output_Pk_camb/",
                                       # MG=False, model='00', rcH0=1.000, F_R0=0.00001
                                       )
    print('Done running interm scales  <<<<< ')

    ######################################################################################################
    ######################################################################################################
    # ---------- FIGURE BEGINS HERE -------------- #
    ncols, nrows = 3, 3
    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=False, sharey=False,
                              gridspec_kw={'height_ratios': [2, 2, 1]},
                              figsize=(36, 12), facecolor='w', edgecolor='k')
    figure.subplots_adjust(hspace=.23, wspace=.04)

    ############### this is needed on top of the fancy formatter

    mpl.rcParams['font.size'] = 35
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'

    ### SPECS ###

    xtext, ytext = 105, -290
    fs_xaxis, fs_yaxis = 40, 42
    fs_text = 60
    rmin, rmaxlin, rmaxlog = 0.1, 140, 40
    msize, csize = 16, 10
    lw_hf = 5


    for i in range(nrows):
        for j in range(ncols):
            # Increase tick label font size
            ax[i, j].tick_params(axis='x', labelsize=fs_xaxis)
            ax[i, j].tick_params(axis='y', labelsize=fs_yaxis)
            ax[i, j].xaxis.set_major_formatter(FancyFormatter())
            ax[i, j].yaxis.set_major_formatter(FancyFormatter())

    ################# LARGE SCALES no modification needed #################
    ##### z00
    # data from sims
    ax[0, 0].errorbar(V12_GR_R140_z00['r'], V12_GR_R140_z00['v12'],
                      yerr=V12_GR_R140_z00['Errv12'], marker='.',capsize=csize, ms=msize,
                      ls='none', c='black', label='DM particles')
    ax[0, 0].fill_between(V12_GR_R140_z00['r'],
                          V12_GR_R140_z00['v12'] - V12_GR_R140_z00['Errv12'],
                          V12_GR_R140_z00['v12'] + V12_GR_R140_z00['Errv12'],
                          alpha=0.2)

    # model halofit
    ax[0, 0].plot(r140, v12_hf_r140_z00, ls='-', c='red', lw=lw_hf, ms=3,
                  label=r'BBKGY-Halofit')
    ax[0, 0].plot(r140, v12_lin_r140_z00, ls='--', c='green', lw=4, ms=3,
                  label=r'BBKGY-Linear')
    ax[0, 0].plot(r140, v12_qlin_r140_z00, ls=':', c='purple', lw=4, ms=3,
                  label=r'Quasilinear')

    # model CLPT
    ax[0, 0].plot(v12clpt140[0]['z0.0'].r, v12_clpt_140_00, ls=':', c='blue',
                  label='CLPT')

    ax[0, 0].text(xtext, ytext, r'z=0', fontsize=fs_text)

    ##### z03
    # data from sims

    ax[0, 1].errorbar(V12_GR_R140_z03['r'], V12_GR_R140_z03['v12'],
                      yerr=V12_GR_R140_z03['Errv12'], marker='.',capsize=csize, ms=msize,
                      ls='none', c='black')
    ax[0, 1].fill_between(V12_GR_R140_z03['r'],
                          V12_GR_R140_z03['v12'] - V12_GR_R140_z03['Errv12'],
                          V12_GR_R140_z03['v12'] + V12_GR_R140_z03['Errv12'],
                          alpha=0.2)

    # model halofit linear quasilinear
    ax[0, 1].plot(r140, v12_hf_r140_z03, ls='-', c='red', lw=lw_hf, ms=3)
    ax[0, 1].plot(r140, v12_lin_r140_z03, ls='--', c='green', lw=lw_hf, ms=3)
    ax[0, 1].plot(r140, v12_qlin_r140_z03, ls=':', c='purple', lw=4, ms=3)

    # model CLPT
    ax[0, 1].plot(v12clpt140[0]['z0.3'].r, v12_clpt_140_03, ls=':', c='blue')

    ax[0, 1].text(xtext, ytext, r'z=0.3', fontsize=fs_text)

    ##### z05
    # data from sims
    ax[0, 2].errorbar(V12_GR_R140_z05['r'], V12_GR_R140_z05['v12'],
                      yerr=V12_GR_R140_z05['Errv12'], marker='.',capsize=csize, ms=msize,
                      ls='none', c='black')
    ax[0, 2].fill_between(V12_GR_R140_z05['r'],
                          V12_GR_R140_z05['v12'] - V12_GR_R140_z05['Errv12'],
                          V12_GR_R140_z05['v12'] + V12_GR_R140_z05['Errv12'],
                          alpha=0.2)

    # model halofit linear quasilinear
    ax[0, 2].plot(r140, v12_hf_r140_z05, ls='-', c='red', lw=lw_hf, ms=3)
    ax[0, 2].plot(r140, v12_lin_r140_z05, ls='--', c='green', lw=lw_hf, ms=3)
    ax[0, 2].plot(r140, v12_qlin_r140_z05, ls=':', c='purple', lw=4, ms=3)

    # model CLPT
    ax[0, 2].plot(v12clpt140[0]['z0.5'].r, v12_clpt_140_05, ls=':', c='blue')

    ax[0, 2].text(xtext, ytext, r'z=0.5', fontsize=fs_text)

    #################  INTERMEDIATE SCALES: with new errors from Hellwing  #################

    #####
    ax[1, 0].scatter(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                     marker='.',capsize=csize, ms=msize, c='black')
    ax[1, 0].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                      yerr=v12_GR_Z00_merged.Errv12.values,
                      marker='.',capsize=csize, ms=msize, ls='none', c='black')
    ax[1, 0].fill_between(v12_GR_Z00_merged.r.values,
                          v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values,
                          alpha=0.2)

    ax[1, 0].plot(r40, v12_hf_r40_z00, ls='-', c='red', lw=lw_hf, ms=3)
    ax[1, 0].plot(r40, v12_lin_r40_z00, ls='--', c='green', lw=lw_hf, ms=3)
    ax[1, 0].plot(r40, v12_qlin_r40_z00, ls=':', c='purple', lw=lw_hf, ms=3)

    # model CLPT
    ax[1, 0].plot(v12clpt40[0]['z0.0'].r, v12_clpt_40_00, ls=':', c='blue')

    ax[1, 0].set_xscale('log')

    #####

    ax[1, 1].scatter(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                     marker='.',capsize=csize, ms=msize, c='black')
    ax[1, 1].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                      yerr=v12_GR_Z03_merged.Errv12.values,
                      marker='.',capsize=csize, ms=msize, ls='none', c='black')
    ax[1, 1].fill_between(v12_GR_Z03_merged.r.values,
                          v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values,
                          alpha=0.2)

    ax[1, 1].plot(r40, v12_hf_r40_z03, ls='-', c='red', lw=lw_hf, ms=3)
    ax[1, 1].plot(r40, v12_lin_r40_z03, ls='--', c='green', lw=lw_hf, ms=3)
    ax[1, 1].plot(r40, v12_qlin_r40_z03, ls=':', c='purple', lw=lw_hf, ms=3)

    # model CLPT
    ax[1, 1].plot(v12clpt40[0]['z0.3'].r, v12_clpt_40_03, ls=':', c='blue')

    ax[1, 1].set_xscale('log')

    #####
    ax[1, 2].scatter(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                     marker='.',capsize=csize, ms=msize, c='black')
    ax[1, 2].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                      yerr=v12_GR_Z05_merged.Errv12.values,
                      marker='.',capsize=csize, ms=msize, ls='none', c='black')
    ax[1, 2].fill_between(v12_GR_Z05_merged.r.values,
                          v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values,
                          alpha=0.2)

    ax[1, 2].plot(r40, v12_hf_r40_z05, ls='-', c='red', lw=lw_hf, ms=3)
    ax[1, 2].plot(r40, v12_lin_r40_z05, ls='--', c='green', lw=lw_hf, ms=3)
    ax[1, 2].plot(r40, v12_qlin_r40_z05, ls=':', c='purple', lw=lw_hf, ms=3)

    # model CLPT
    ax[1, 2].plot(v12clpt40[0]['z0.5'].r, v12_clpt_40_05, ls=':', c='blue')

    ax[1, 2].set_xscale('log')

    # #################  RATIOS  with new errors from Hellwing  #################

    # v12_hf_r40_z00.v12.values
    ax[2, 0].plot(r40,
                  (1 - v12_hf_r40_z00 / v12_GR_Z00_merged.v12.values) * 100,
                  c='red', lw=lw_hf)
    ax[2, 1].plot(r40,
                  (1 - v12_hf_r40_z03 / v12_GR_Z03_merged.v12.values) * 100,
                  c='red', lw=lw_hf)
    ax[2, 2].plot(r40,
                  (1 - v12_hf_r40_z05 / v12_GR_Z05_merged.v12.values) * 100,
                  c='red', lw=lw_hf)

    ax[2, 0].plot(r40,
                  (1 - v12_lin_r40_z00 / v12_GR_Z00_merged.v12.values) * 100,
                  c='green', ls='--', lw=lw_hf)
    ax[2, 1].plot(r40,
                  (1 - v12_lin_r40_z03 / v12_GR_Z03_merged.v12.values) * 100,
                  c='green', ls='--', lw=lw_hf)
    ax[2, 2].plot(r40,
                  (1 - v12_lin_r40_z05 / v12_GR_Z05_merged.v12.values) * 100,
                  c='green', ls='--', lw=lw_hf)

    ax[2, 0].plot(r40,
                  (1 - v12_qlin_r40_z00 / v12_GR_Z00_merged.v12.values) * 100,
                  c='purple', ls=':', lw=lw_hf)
    ax[2, 1].plot(r40,
                  (1 - v12_qlin_r40_z03 / v12_GR_Z03_merged.v12.values) * 100,
                  c='purple', ls=':', lw=lw_hf)
    ax[2, 2].plot(r40,
                  (1 - v12_qlin_r40_z05 / v12_GR_Z05_merged.v12.values) * 100,
                  c='purple', ls=':', lw=lw_hf)

    ax[2, 0].fill_between(v12_GR_Z00_merged.r.values,
                          -v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.Errv12.values,
                          alpha=0.2)
    ax[2, 1].fill_between(v12_GR_Z03_merged.r.values,
                          -v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.Errv12.values,
                          alpha=0.2)
    ax[2, 2].fill_between(v12_GR_Z05_merged.r.values,
                          -v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.Errv12.values,
                          alpha=0.2)

    ## to-do: change size/placement of the legend
    # figure.legend(ncol=5, loc='upper center', bbox_to_anchor=(1.04, 1), fontsize=25)
    figure.tight_layout()
    figure.legend(ncol=5, fontsize=25, loc="upper center",
                    bbox_to_anchor=(0., 1.02, 1., .102), mode="expand",
                    borderaxespad=0.)
    # from https://matplotlib.org/2.0.2/users/legend_guide.html#legend-location

    for j in range(ncols):
        ax[2, j].set_xscale('log')
        ax[2, j].set_xlabel(r'$r$[Mpc/h]', fontsize=30)
    # ################################## SPECS ##################################

    lower, upper = -10, 10
    for j in range(ncols):
        ax[2, j].set_ylim(-21, 21)
        ax[2, j].set_xscale('log')
        ax[2, j].axhline(lower, ls=':', lw=2, color='k')
        ax[2, j].axhline(upper, ls=':', lw=2, color='k')
        ax[2, j].axhline(lower / 2, ls=':', lw=2, color='k')
        ax[2, j].axhline(upper / 2, ls=':', lw=2, color='k')
        ax[0, j].set_xlim(rmin, rmaxlin)
        ax[1, j].set_xlim(rmin, rmaxlog)
        ax[2, j].set_xlim(rmin, rmaxlog)

    for i in range(2):
        for j in range(ncols):
            ax[i, j].set_ylim(-350, 70)
            ax[i, 0].set_ylabel(r'$v_{12}(r)$', fontsize=30)

    ax[2, 0].set_ylabel(r'$\Delta v_{12}[\%]$', fontsize=30)

    print('---- Figure 1 done -----')
    # ----------------- Saving  ---------------------

    if save_figure:

        plt.savefig(full_fig_name, bbox_inches='tight', dpi=dpi)
        print('Figure saved at ', str(figpath) + str(figname),
              ' in the format: ', str(fig_type))

    else:
        print('Figure NOT saved ')

    return


def figure_2(fig_path='/home/jaber/shared/data/figs/', fig_name='fig2_v12_MG_scr',
             fig_type='.pdf', save_figure=False):
    '''

    Parameters
    ----------
    fig_path
    fig_name
    fig_type
    save_figure

    Returns
    -------

    '''
    #  # before doing anything: read the params and warn the user if we're saving or not the fig in the right name/path

    # # Read these params from the user

    figpath = fig_path
    figname = fig_name
    fig_ext = fig_type
    dpi = 1200
    full_fig_name = figpath + figname + str(fig_ext)

    if save_figure:

        print('The figure will be saved at', full_fig_name)
    else:
        print('The figure will NOT be saved. The params were: ', full_fig_name)

    # ---------- SPECS FOR MODELS ---------------- #
    # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()
    cosmo_args = cosmoELEPHANT, 1.0, True

    ## --- logarithmic redshift range

    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1,
         1.2, 1.5, 1.86, 1.9, 2])

    HMredshifts = np.round(HMredshifts, 4)

    z_vals = HMredshifts

    # ---------- READING DATA       -------------- #
    v12_GR_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_GR_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/GR_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    # ---------- MG DATA  -------------#
    v12_F5_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_F5_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_F5_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_F6_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_F6_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_F6_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N5_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N5_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N5_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N1_Z00_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.0/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N1_Z03_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.3/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    v12_N1_Z05_merged = pd.read_csv(
        '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.5/v12AvgMerged.dat',
        sep='\s+', comment='#', names=["r", "v12", "Errv12"],
        skiprows=1)

    r_40_MG = v12_N1_Z03_merged.r.values
    r_40 = v12_GR_Z00_merged.r.values

    print('>>>> Done reading data <<<< ')
    # ---------- RUNNING LIN & HF MODELS --------- #

    print('>>>> Start running GR   ')
    r40, v12_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r40, v12_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.33)  ### mind this value!

    r40, v12_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=False,
        model='00',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    print('Done running large scales  <<<<< ')

    print('>>>> Start running F(R)   ')

    r40_MG, v12_F5_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.00)  ### mind this value!

    r40_MG, v12_F5_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.33)  ### mind this value!

    r40_MG, v12_F5_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.5)

    r40_MG, v12_F6_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.05)  ### mind this value!

    r40_MG, v12_F6_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.33)  ### mind this value!

    r40_MG, v12_F6_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='04',
        rcH0=1.0,
        F_R0=1e-06,
        which_simulation_redshift=0.5)

    print('Done running F(R)  <<<<< ')

    print('>>>> Start running nDGP   ')
    r40_MG, v12_N5_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=5.0,
        F_R0=1e-05,
        which_simulation_redshift=0.05)  ### mind this value!

    r40_MG, v12_N5_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=5.0,
        F_R0=1e-05,
        which_simulation_redshift=0.33)  ### mind this value!

    r40_MG, v12_N5_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=5.0,
        F_R0=1e-05,
        which_simulation_redshift=0.5)

    r40_MG, v12_N1_hf_r40_z00, aa, zz, xi_hf_r40_z00, dxida_hf_r40_z00 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.05)  ### mind this value!

    r40_MG, v12_N1_hf_r40_z03, aa, zz, xi_hf_r40_z03, dxida_hf_r40_z03 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.33)  ### mind this value!

    r40_MG, v12_N1_hf_r40_z05, aa, zz, xi_hf_r40_z05, dxida_hf_r40_z05 = v12_from_numerical_deriv(
        cosmo_args, use_r_array=True, r_array=r_40_MG,
        z_array=z_vals,
        use_z_array=True,
        # r_args= r_args_40,
        MG=True,
        model='99',
        rcH0=1.0,
        F_R0=1e-05,
        which_simulation_redshift=0.5)

    print('Done running NDGP  <<<<< ')

    ######################################################################################################
    ######################################################################################################
    # ---------- FIGURE BEGINS HERE -------------- #

    nrows, ncols = 4, 3

    models = ["GR", "F5", "F6", "N1", "N5"]
    cmodel = ["k", "#029e74", "#0273b2", "#d96d19", "#aa007f"]
    z_snap = ['0.0', '0.3', '0.5']

    ### This is what's formatting the figure, not the FancyFormatter class
    mpl.rcParams['font.size'] = 35
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'

    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=True, sharey=False,
                              gridspec_kw={'height_ratios': [2, 1, 2, 1]},
                              figsize=(35, 15), facecolor='w', edgecolor='k')
    figure.subplots_adjust(hspace=.15, wspace=.1)

    ###############
    ### SPECS ###
    fs_xaxis, fs_yaxis = 42, 38
    fs_x_text, fs_text = 70, 47
    msize, csize = 16, 3
    labelhf = 'BBKGY-Halofit'
    lower, upper = -10, 10

    for i in range(nrows):
        for j in range(ncols):
            ax[i, j].xaxis.set_major_formatter(FancyFormatter())
            ax[i, j].yaxis.set_major_formatter(FancyFormatter())

    ####  lines done first to be on the background of the figure
    for j in range(ncols):
        ax[1, j].axhline(0, ls='-', lw=1, color='gray')
        ax[3, j].axhline(0, ls='-', lw=1, color='gray')
        ax[1, j].axhline(lower, ls=':', lw=1, color='k')
        ax[1, j].axhline(upper, ls=':', lw=1, color='k')
        ax[1, j].axhline(lower / 2, ls=':', lw=1, color='k')
        ax[1, j].axhline(upper / 2, ls=':', lw=1, color='k')
        ax[3, j].axhline(lower, ls=':', lw=1, color='k')
        ax[3, j].axhline(upper, ls=':', lw=1, color='k')
        ax[3, j].axhline(lower / 2, ls=':', lw=1, color='k')
        ax[3, j].axhline(upper / 2, ls=':', lw=1, color='k')

    ##### ---------------- fofr ---------------

    ax[0, 0].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                      yerr=v12_GR_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[0, 0].errorbar(v12_F5_Z00_merged.r.values, v12_F5_Z00_merged.v12.values,
                      yerr=v12_F5_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[0, 0].errorbar(v12_F6_Z00_merged.r.values, v12_F6_Z00_merged.v12.values,
                      yerr=v12_F6_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[0, 0].fill_between(v12_GR_Z00_merged.r.values,
                          v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[0, 0].fill_between(v12_F5_Z00_merged.r.values,
                          v12_F5_Z00_merged.v12.values - v12_F5_Z00_merged.Errv12.values,
                          v12_F5_Z00_merged.v12.values + v12_F5_Z00_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[0, 0].fill_between(v12_F6_Z00_merged.r.values,
                          v12_F6_Z00_merged.v12.values - v12_F6_Z00_merged.Errv12.values,
                          v12_F6_Z00_merged.v12.values + v12_F6_Z00_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[0, 0].plot(r40, v12_hf_r40_z00, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[0, 0].plot(r40_MG, v12_F5_hf_r40_z00, ls='-', lw=1, color=cmodel[1])
    ax[0, 0].plot(r40_MG, v12_F6_hf_r40_z00, ls='-', lw=1, color=cmodel[2])

    ax[0, 1].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                      yerr=v12_GR_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[0, 1].errorbar(v12_F5_Z03_merged.r.values, v12_F5_Z03_merged.v12.values,
                      yerr=v12_F5_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[0, 1].errorbar(v12_F6_Z03_merged.r.values, v12_F6_Z03_merged.v12.values,
                      yerr=v12_F6_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[0, 1].fill_between(v12_GR_Z03_merged.r.values,
                          v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[0, 1].fill_between(v12_F5_Z03_merged.r.values,
                          v12_F5_Z03_merged.v12.values - v12_F5_Z03_merged.Errv12.values,
                          v12_F5_Z03_merged.v12.values + v12_F5_Z03_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[0, 1].fill_between(v12_F6_Z03_merged.r.values,
                          v12_F6_Z03_merged.v12.values - v12_F6_Z03_merged.Errv12.values,
                          v12_F6_Z03_merged.v12.values + v12_F6_Z03_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[0, 1].plot(r40, v12_hf_r40_z03, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[0, 1].plot(r40_MG, v12_F5_hf_r40_z03, ls='-', lw=1, color=cmodel[1])
    ax[0, 1].plot(r40_MG, v12_F6_hf_r40_z03, ls='-', lw=1, color=cmodel[2])

    ax[0, 2].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                      yerr=v12_GR_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[0, 2].errorbar(v12_F5_Z05_merged.r.values, v12_F5_Z05_merged.v12.values,
                      yerr=v12_F5_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[0, 2].errorbar(v12_F6_Z05_merged.r.values, v12_F6_Z05_merged.v12.values,
                      yerr=v12_F6_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[0, 2].fill_between(v12_GR_Z05_merged.r.values,
                          v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[0, 2].fill_between(v12_F5_Z05_merged.r.values,
                          v12_F5_Z05_merged.v12.values - v12_F5_Z05_merged.Errv12.values,
                          v12_F5_Z05_merged.v12.values + v12_F5_Z05_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[0, 2].fill_between(v12_F6_Z05_merged.r.values,
                          v12_F6_Z05_merged.v12.values - v12_F6_Z05_merged.Errv12.values,
                          v12_F6_Z05_merged.v12.values + v12_F6_Z05_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[0, 2].plot(r40, v12_hf_r40_z05, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[0, 2].plot(r40_MG, v12_F5_hf_r40_z05, ls='-', lw=1, color=cmodel[1])
    ax[0, 2].plot(r40_MG, v12_F6_hf_r40_z05, ls='-', lw=1, color=cmodel[2])

    #### ---------------- ndgp ---------------

    ax[2, 0].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                      yerr=v12_GR_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[2, 0].errorbar(v12_N1_Z00_merged.r.values, v12_N1_Z00_merged.v12.values,
                      yerr=v12_N1_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[2, 0].errorbar(v12_N5_Z00_merged.r.values, v12_N5_Z00_merged.v12.values,
                      yerr=v12_N5_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[2, 0].fill_between(v12_GR_Z00_merged.r.values,
                          v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[2, 0].fill_between(v12_N1_Z00_merged.r.values,
                          v12_N1_Z00_merged.v12.values - v12_N1_Z00_merged.Errv12.values,
                          v12_N1_Z00_merged.v12.values + v12_N1_Z00_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[2, 0].fill_between(v12_N5_Z00_merged.r.values,
                          v12_N5_Z00_merged.v12.values - v12_N5_Z00_merged.Errv12.values,
                          v12_N5_Z00_merged.v12.values + v12_N5_Z00_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[2, 0].plot(r40, v12_hf_r40_z00, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[2, 0].plot(r40_MG, v12_N1_hf_r40_z00, ls='-', lw=1, color=cmodel[3])
    ax[2, 0].plot(r40_MG, v12_N5_hf_r40_z00, ls='-', lw=1, color=cmodel[4])

    ax[2, 1].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                      yerr=v12_GR_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[2, 1].errorbar(v12_N1_Z03_merged.r.values, v12_N1_Z03_merged.v12.values,
                      yerr=v12_N1_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[2, 1].errorbar(v12_N5_Z03_merged.r.values, v12_N5_Z03_merged.v12.values,
                      yerr=v12_N5_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[2, 1].fill_between(v12_GR_Z03_merged.r.values,
                          v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[2, 1].fill_between(v12_N1_Z03_merged.r.values,
                          v12_N1_Z03_merged.v12.values - v12_N1_Z03_merged.Errv12.values,
                          v12_N1_Z03_merged.v12.values + v12_N1_Z03_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[2, 1].fill_between(v12_N5_Z03_merged.r.values,
                          v12_N5_Z03_merged.v12.values - v12_N5_Z03_merged.Errv12.values,
                          v12_N5_Z03_merged.v12.values + v12_N5_Z03_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[2, 1].plot(r40, v12_hf_r40_z03, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[2, 1].plot(r40_MG, v12_N1_hf_r40_z03, ls='-', lw=1, color=cmodel[3])
    ax[2, 1].plot(r40_MG, v12_N5_hf_r40_z03, ls='-', lw=1, color=cmodel[4])
    # ax[2,1].yaxis.set_major_formatter(FancyFormatter())

    ax[2, 2].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                      yerr=v12_GR_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[2, 2].errorbar(v12_N1_Z05_merged.r.values, v12_N1_Z05_merged.v12.values,
                      yerr=v12_N1_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[2, 2].errorbar(v12_N5_Z05_merged.r.values, v12_N5_Z05_merged.v12.values,
                      yerr=v12_N5_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.',capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[2, 2].fill_between(v12_GR_Z05_merged.r.values,
                          v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[2, 2].fill_between(v12_N1_Z05_merged.r.values,
                          v12_N1_Z05_merged.v12.values - v12_N1_Z05_merged.Errv12.values,
                          v12_N1_Z05_merged.v12.values + v12_N1_Z05_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[2, 2].fill_between(v12_N5_Z05_merged.r.values,
                          v12_N5_Z05_merged.v12.values - v12_N5_Z05_merged.Errv12.values,
                          v12_N5_Z05_merged.v12.values + v12_N5_Z05_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[2, 2].plot(r40, v12_hf_r40_z05, ls='-', lw=1, color=cmodel[0],
                  label=labelhf)
    ax[2, 2].plot(r40_MG, v12_N1_hf_r40_z05, ls='-', lw=1, color=cmodel[3])
    ax[2, 2].plot(r40_MG, v12_N5_hf_r40_z05, ls='-', lw=1, color=cmodel[4])

    #### =========== ratios =============
    # #################  RATIOS  with new errors from Hellwing  #################

    ax[1, 0].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z00 / v12_F5_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[1])
    ax[1, 0].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z00 / v12_F6_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[2])
    ax[1, 0].fill_between(v12_F5_Z00_merged.r.values,
                          -v12_F5_Z00_merged.Errv12.values,
                          v12_F5_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[1, 0].fill_between(v12_F6_Z00_merged.r.values,
                          -v12_F6_Z00_merged.Errv12.values,
                          v12_F6_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[1, 1].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z03 / v12_F5_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[1])
    ax[1, 1].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z03 / v12_F6_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[2])
    ax[1, 1].fill_between(v12_F5_Z03_merged.r.values,
                          -v12_F5_Z03_merged.Errv12.values,
                          v12_F5_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[1, 1].fill_between(v12_F6_Z03_merged.r.values,
                          -v12_F6_Z03_merged.Errv12.values,
                          v12_F6_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[1, 2].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z05 / v12_F5_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[1])
    ax[1, 2].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z05 / v12_F6_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[2])
    ax[1, 2].fill_between(v12_F5_Z05_merged.r.values,
                          -v12_F5_Z05_merged.Errv12.values,
                          v12_F5_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[1, 2].fill_between(v12_F6_Z05_merged.r.values,
                          -v12_F6_Z05_merged.Errv12.values,
                          v12_F6_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[3, 0].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z00 / v12_N1_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[3, 0].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z00 / v12_N5_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])
    ax[3, 0].fill_between(v12_N1_Z00_merged.r.values,
                          -v12_N1_Z00_merged.Errv12.values,
                          v12_N1_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[3, 0].fill_between(v12_N5_Z00_merged.r.values,
                          -v12_N5_Z00_merged.Errv12.values,
                          v12_N5_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    ax[3, 1].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z03 / v12_N1_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[3, 1].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z03 / v12_N5_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])
    ax[3, 1].fill_between(v12_N1_Z03_merged.r.values,
                          -v12_N1_Z03_merged.Errv12.values,
                          v12_N1_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[3, 1].fill_between(v12_N5_Z03_merged.r.values,
                          -v12_N5_Z03_merged.Errv12.values,
                          v12_N5_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    ax[3, 2].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z05 / v12_N1_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[3, 2].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z05 / v12_N5_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])
    ax[3, 2].fill_between(v12_N1_Z05_merged.r.values,
                          -v12_N1_Z05_merged.Errv12.values,
                          v12_N1_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[3, 2].fill_between(v12_N5_Z05_merged.r.values,
                          -v12_N5_Z05_merged.Errv12.values,
                          v12_N5_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    #### =========== ====== =============
    #### legends
    ax[0, 0].legend(fontsize=20)
    ax[2, 0].legend(fontsize=20)
    #### y-axis labels
    ax[0, 0].set_ylabel(r'$v_{12}(r)$', fontsize=fs_text)
    ax[2, 0].set_ylabel(r'$v_{12}(r)$', fontsize=fs_text)
    ax[1, 0].set_ylabel(r'$\Delta v_{12}$[%]', fontsize=fs_text)
    ax[3, 0].set_ylabel(r'$\Delta v_{12}$[%]', fontsize=fs_text)

    # Customize y-tick positions for all figures
    # Choose the y-tick positions you want to show
    ytick_positions = [-400, -300, -200, -100, 0]
    for i in [0, 2]:  # Rows 0 and 2
        for j in range(ncols):  # All columns
            ax[i, j].set_yticks(ytick_positions)

    #### =========== ====== =============
    for i in range(nrows):
        # Set y-axis label for the first column
        ax[i, 0].tick_params(axis='y', labelsize=fs_yaxis)
        # Hide y-axis labels for the 2nd and 3rd column
        ax[i, 1].tick_params(axis='y', labelleft=False)
        ax[i, 2].tick_params(axis='y', labelleft=False)
        for j in range(ncols):
            # Log scale
            ax[i, j].set_xscale('log')

    for j in range(ncols):
        ax[1, j].axhline(0, ls=':', lw=2, color='k')
        ax[3, j].axhline(0, ls=':', lw=2, color='k')
        ax[0, j].set_title(r'$z=$' + str(z_snap[j]), fontsize=fs_text)
        # Increase tick label font size
        ax[3, j].set_xlabel(r'$r[Mpc/h]$', fontsize=fs_x_text)
        ax[3, j].tick_params(axis='x', labelsize=fs_xaxis)
        ax[0, j].set_ylim(-400, 50)
        ax[2, j].set_ylim(-400, 50)
        ax[1, j].set_ylim(-21, 21)
        ax[3, j].set_ylim(-21, 21)

    for i in range(nrows):
        for j in range(ncols):
            # Fancy Formatter
            ax[i, j].xaxis.set_major_formatter(FancyFormatter())
            ax[i, j].yaxis.set_major_formatter(FancyFormatter())
    print('---- Figure 2 done -----')
    # ----------------- Saving  ---------------------

    if save_figure:

        plt.savefig(full_fig_name, bbox_inches='tight', dpi=dpi)
        print('Figure saved at ', str(figpath) + str(figname),
              ' in the format: ', str(fig_type))

    else:
        print('Figure NOT saved ')

    return


def figure_3(fig_path='/home/jaber/shared/data/figs/', fig_name='fig3_HM_scr',
             fig_type='.pdf', save_figure=False,
             which_snapshot=0):
    '''
    Parameters
    ----------
    fig_path
    fig_name
    fig_type
    save_figure
    which_snapshot

    Returns
    -------

    '''

    ## before doing anything: read the params and warn the user if we're saving or not the fig in the right name/path

    ## Read these params from the user

    figpath = fig_path
    figname = fig_name
    fig_ext = fig_type
    dpi = 1200

    full_fig_name = figpath + figname + str(fig_ext)

    if save_figure:

        print('The figure will be saved at', full_fig_name)
    else:
        print('The figure will NOT be saved. The params were: ', full_fig_name)

    # ---------- SPECS FOR MODELS ---------------- #
    # --- By default the cosmology is the one for ELEPHANT
    cosmoELEPHANT = define_cosmology()
    cosmo_args = cosmoELEPHANT, 1.0, True
    which_cosmology = cosmoELEPHANT
    ## --- logarithmic redshift range

    HMredshifts = np.array(
        [0, 0.05, 0.11, 0.18, 0.25, 0.297, 0.33, 0.43, 0.5, 0.54, 0.67, 0.82, 1,
         1.2, 1.5, 1.86, 1.9, 2])

    HMredshifts = np.round(HMredshifts, 4)

    z_vals = HMredshifts

    ### Depending on which redshift we want to plot:

    if which_snapshot == 0:
        # ---------- READING DATA       -------------- #
        # ---------- MG DATA  -------------#
        print('>>>> Start reading data:')
        v12_F5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.0/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_F6_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.0/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_N5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.0/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)
        v12_N1_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.0/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        r_40 = v12_F5_merged.r.values
        print('>>>> Done reading data <<<< ')

        print('>>>> Start running F(R) for the snapshot  ', str(which_snapshot))

        r40_MG, v12_F5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F5', which_simulation_redshift=0
        )

        r40_MG, v12_F6_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F6', which_simulation_redshift=0
        )

        r40_MG, v12_F5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.00)

        r40_MG, v12_F6_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-06,
            which_simulation_redshift=0.00)

        print('Done running F(R)  <<<<< ')

        print('>>>> Start running nDGP for the snapshot  ', str(which_snapshot))

        r40_MG, v12_N1_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N1', which_simulation_redshift=0
        )
        r40_MG, v12_N5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N5', which_simulation_redshift=0
        )

        r40_MG, v12_N5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='99',
            rcH0=5.0,
            F_R0=1e-05,
            which_simulation_redshift=0.05)  ### mind this value!

        r40_MG, v12_N1_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            # r_args= r_args_40,
            MG=True,
            model='99',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.05)  ### mind this value!

        print('Done running NDGP  <<<<< ')



    elif which_snapshot == 0.3:

        print('>>>> Start reading data:')
        v12_F5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.3/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_F6_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.3/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_N5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.3/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)
        v12_N1_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.3/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        r_40 = v12_F5_merged.r.values
        print('>>>> Done reading data <<<< ')

        print('>>>> Start running F(R) for the snapshot  ', str(which_snapshot))

        r40_MG, v12_F5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F5', which_simulation_redshift=0.297
        )

        r40_MG, v12_F6_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F6', which_simulation_redshift=0.297
        )

        r40_MG, v12_F5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.33)  ### mind this value!

        r40_MG, v12_F6_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-06,
            which_simulation_redshift=0.33)  ### mind this value!

        print('Done running F(R)  <<<<< ')

        print('>>>> Start running nDGP for the snapshot  ', str(which_snapshot))

        r40_MG, v12_N1_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N1', which_simulation_redshift=0.297
        )

        r40_MG, v12_N5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N5', which_simulation_redshift=0.297
        )

        r40_MG, v12_N5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='99',
            rcH0=5.0,
            F_R0=1e-05,
            which_simulation_redshift=0.33)  ### mind this value!

        r40_MG, v12_N1_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            # r_args= r_args_40,
            MG=True,
            model='99',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.33)  ### mind this value!
        print('Done running NDGP  <<<<< ')


    elif which_snapshot == 0.5:

        print('>>>> Start reading data:')
        v12_F5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F5_z0.5/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_F6_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/F6_z0.5/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        v12_N5_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N5_z0.5/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)
        v12_N1_merged = pd.read_csv(
            '/home/jaber/shared/data/output_v12_DM_merged/N1_z0.5/v12AvgMerged.dat',
            sep='\s+', comment='#', names=["r", "v12", "Errv12"],
            skiprows=1)

        r_40 = v12_F5_merged.r.values
        print('>>>> Done reading data <<<< ')

        print('>>>> Start running F(R) for the snapshot  ', str(which_snapshot))
        r40_MG, v12_F5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F5', which_simulation_redshift=0.5
        )

        r40_MG, v12_F6_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='F6', which_simulation_redshift=0.5
        )

        r40_MG, v12_F5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.5)

        r40_MG, v12_F6_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='04',
            rcH0=1.0,
            F_R0=1e-06,
            which_simulation_redshift=0.5)

        print('Done running F(R)  <<<<< ')
        print('>>>> Start running nDGP for the snapshot  ', str(which_snapshot))

        r40_MG, v12_N1_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N1', which_simulation_redshift=0.5
        )

        r40_MG, v12_N5_hm_r40, aa, zz, xi_hm_r40, dxida_hm_r40 = v12_from_numerical_deriv_hm(
            which_cosmology,
            r_array_usr=r_40, use_r_array=True, r_args=None,
            model='N5', which_simulation_redshift=0.5
        )

        r40_MG, v12_N5_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            MG=True,
            model='99',
            rcH0=5.0,
            F_R0=1e-05,
            which_simulation_redshift=0.5)

        r40_MG, v12_N1_hf_r40, aa, zz, xi_hf_r40, dxida_hf_r40 = v12_from_numerical_deriv(
            cosmo_args, use_r_array=True, r_array=r_40,
            z_array=z_vals,
            use_z_array=True,
            # r_args= r_args_40,
            MG=True,
            model='99',
            rcH0=1.0,
            F_R0=1e-05,
            which_simulation_redshift=0.5)
        print('Done running NDGP  <<<<< ')

    else:
        print("Option invalid. Please verify your inputs.")

    ######################################################################################################
    ######################################################################################################
    # ---------- FIGURE BEGINS HERE -------------- #

    # declare the N panels

    nrows, ncols = 1, 2

    figure, axis = plt.subplots(nrows=nrows, ncols=ncols,
                                sharex=True, sharey=True,
                                # figsize = (ancho, alto)
                                figsize=(30, 10), facecolor='w', edgecolor='k')

    figure.subplots_adjust(wspace=0.06)

    # #########

    mpl.rcParams['font.size'] = 35
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'
    models = ["GR", "F5", "F6", "N1", "N5"]
    cmodel = ["k", "#029e74", "#0273b2", "#d96d19", "#aa007f"]
    lw_m1, lw_m2 = 3, 2
    upper, lower = -5, 5

    ## These have to appear first to be on the background of the figure and not on top of the solutions
    for i in range(ncols):
        axis[i].axhline(0, ls='-', lw=1, color='gray')
        axis[i].axhline(lower, ls=':', lw=2, color='gray')
        axis[i].axhline(upper, ls=':', lw=2, color='gray')
        axis[i].axhline(2 * lower, ls=':', lw=2, color='gray')
        axis[i].axhline(2 * upper, ls=':', lw=2, color='gray')

    axis[0].plot(v12_N1_merged.r.values,
                 (1 - v12_N1_hm_r40 / v12_N1_merged.v12.values) * 100, lw=lw_m1,
                 ls='-', color='k', label='Gupta+2023')

    axis[0].plot(v12_N1_merged.r.values,
                 (1 - v12_N1_hm_r40 / v12_N1_merged.v12.values) * 100, lw=lw_m1,
                 ls='-', color=cmodel[3])
    axis[0].plot(v12_N5_merged.r.values,
                 (1 - v12_N5_hm_r40 / v12_N5_merged.v12.values) * 100, lw=lw_m2,
                 ls='-', color=cmodel[4])

    axis[0].plot(v12_N1_merged.r.values,
                 (1 - v12_N1_hf_r40 / v12_N1_merged.v12.values) * 100, lw=lw_m1,
                 ls='--', color='k', label='Halofit')

    axis[0].plot(v12_N1_merged.r.values,
                 (1 - v12_N1_hf_r40 / v12_N1_merged.v12.values) * 100, lw=lw_m1,
                 ls='--', color=cmodel[3])
    axis[0].plot(v12_N5_merged.r.values,
                 (1 - v12_N5_hf_r40 / v12_N5_merged.v12.values) * 100, lw=lw_m2,
                 ls='--', color=cmodel[4])

    axis[0].fill_between(r40_MG, -1 * v12_N1_merged.Errv12.values,
                         1 * v12_N1_merged.Errv12.values,
                         alpha=0.2, color=cmodel[3])
    axis[0].fill_between(r40_MG, -1 * v12_N5_merged.Errv12.values,
                         1 * v12_N5_merged.Errv12.values,
                         alpha=0.2, color=cmodel[4])

    axis[0].text(2, -20, 'N5', color=cmodel[4], fontsize=26)
    axis[0].text(10, -20, 'N1', color=cmodel[3], fontsize=36)

    axis[1].plot(v12_F5_merged.r.values,
                 (1 - v12_F5_hm_r40 / v12_F5_merged.v12.values) * 100, lw=lw_m1,
                 ls='-', color='k', label='Gupta+2023')

    axis[1].plot(v12_F5_merged.r.values,
                 (1 - v12_F5_hm_r40 / v12_F5_merged.v12.values) * 100, lw=lw_m1,
                 ls='-', color=cmodel[1])
    axis[1].plot(v12_F6_merged.r.values,
                 (1 - v12_F6_hm_r40 / v12_F6_merged.v12.values) * 100, lw=lw_m2,
                 ls='-', color=cmodel[2])

    axis[1].plot(v12_F5_merged.r.values,
                 (1 - v12_F5_hf_r40 / v12_F5_merged.v12.values) * 100, lw=lw_m1,
                 ls='--', color='k', label='Halofit')
    axis[1].plot(v12_F5_merged.r.values,
                 (1 - v12_F5_hf_r40 / v12_F5_merged.v12.values) * 100, lw=lw_m1,
                 ls='--', color=cmodel[1])
    axis[1].plot(v12_F6_merged.r.values,
                 (1 - v12_F6_hf_r40 / v12_F6_merged.v12.values) * 100, lw=lw_m2,
                 ls='--', color=cmodel[2])

    axis[1].fill_between(r40_MG, -1 * v12_F5_merged.Errv12.values,
                         1 * v12_F5_merged.Errv12.values,
                         alpha=0.2, color=cmodel[1])
    axis[1].fill_between(r40_MG, -1 * v12_F6_merged.Errv12.values,
                         1 * v12_F6_merged.Errv12.values,
                         alpha=0.2, color=cmodel[2])
    axis[1].text(2, -20, 'F6', color=cmodel[2], fontsize=36)
    axis[1].text(10, -20, 'F5', color=cmodel[1], fontsize=46)

    for i in range(ncols):
        axis[i].set_xscale('log')
        axis[i].set_xlabel(r'$r[Mpc/h]$', size=50)
        axis[i].set_ylim(-30, 30)
        axis[i].set_title(r'$z=$' + str(which_snapshot), fontsize=40)
        # Increase tick label font size
        axis[i].tick_params(axis='x', labelsize=42)
        axis[i].tick_params(axis='y', labelsize=40)
        # Fancy Formatter
        axis[i].xaxis.set_major_formatter(FancyFormatter())
        axis[i].yaxis.set_major_formatter(FancyFormatter())
        axis[i].legend(fontsize=35)

    axis[0].set_ylabel(r'$\Delta v_{12}[\%]$', size=40)

    print('---- Figure 3 done -----')
    # ----------------- Saving  ---------------------

    if save_figure:

        plt.savefig(full_fig_name, bbox_inches='tight', dpi=dpi)
        print('Figure saved at ', str(figpath) + str(figname),
              ' in the format: ', str(fig_type))

    else:
        print('Figure NOT saved ')

    return


def figure_stable_clustering(fig_path='/home/jaber/shared/data/figs/',
                             fig_name='fig4_vpeak_rstar_model_scr', fig_type='.pdf',
                             sufix='_HF',
                             save_figure=False):
    '''

    Parameters
    ----------
    fig_path: str
    fig_name: str
    fig_type: str
    sufix: str
    save_figure: bool

    Returns
    -------

    '''
    # # before doing anything: read the params and warn the user if we're saving or not the fig in the right name/path
    # # Read these params from the user

    figpath = fig_path
    figname = fig_name
    fig_ext = fig_type
    dpi = 1200

    full_fig_name = figpath + figname + str(fig_ext)

    if save_figure:

        print('The figure will be saved at', full_fig_name)
    else:
        print('The figure will NOT be saved. The params were: ', full_fig_name)

    # ----- Reading the errors generated from simulation data
    zvals, v12_GR, v12_F5, v12_F6, v12_N1, v12_N5 = v12peak_sim_data()
    zvals, Rs_GR, Rs_F5, Rs_F6, Rs_N1, Rs_N5 = rstar_sim_data()

    # -- factor to multiply the errors for Rstar
    mult = 5

    # ------ Reading the solutions
    peakRstarDF_dict = read_solutions_rstar_v12peak(sufix=sufix)

    # --------------- FIGURE BEGINS HERE ---------------------
    ncols, nrows = 1, 2
    models = ["GR", "F5", "F6", "N1", "N5"]
    cmodel = ["k", "#029e74", "#0273b2", "#d96d19", "#aa007f"]

    figure, axis = plt.subplots(nrows=nrows, ncols=ncols,
                                sharex=True, sharey=False,
                                figsize=(10, 10), facecolor='w', edgecolor='k')

    figure.subplots_adjust(hspace=.07, wspace=0.2)

    mpl.rcParams['font.size'] = 45
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'
    mpl.rcParams['axes.titlesize'] = 30  # fontsize of the axes title
    mpl.rcParams['axes.labelsize'] = 30  # fontsize of the x any y labels

    sl = 9  ## to include all we do not need this slice, we set 13 to go to only up-to z=1, 9 to go to 0.5
    ii = 0
    # To-do: move outside the plotting function
    # -------- Smoothing our solutions using Savitzky-Golay filter
    from scipy.signal import savgol_filter
    window_size = 9
    order = 3
    newzss = np.array((0, 0.18, 0.3, 0.33, 0.4, 0.45, 0.5)) #, 0.54, 0.67,0.82, 1.))
    newvgr = peakRstarDF_dict['GR'].v12Peak.values[2:sl]

    v12Peak_smooth_GR = savgol_filter(newvgr, window_length=5, polyorder=3)

    # v12Peak_smooth_GR = savgol_filter(peakRstarDF_dict['GR'].v12Peak.values[ii:sl+ii],
    #                                   window_size, order)
    v12Peak_smooth_F5 = savgol_filter(peakRstarDF_dict['F5'].v12Peak.values[ii:sl+ii],
                                      window_size, order)
    v12Peak_smooth_F6 = savgol_filter(peakRstarDF_dict['F6'].v12Peak.values[ii:sl+ii],
                                      window_size, order)
    v12Peak_smooth_N5 = savgol_filter(peakRstarDF_dict['N5'].v12Peak.values[ii:sl+ii],
                                      window_size, order)
    v12Peak_smooth_N1 = savgol_filter(peakRstarDF_dict['N1'].v12Peak.values[ii:sl+ii],
                                      window_size, order)

    # # # simulation data

    ls_sim = '-'
    ls_sol = ':'
    axis[0].errorbar(zvals, -v12_GR[0:3], yerr=v12_GR[3::], marker='o', ls=ls_sim, capsize=4, c=cmodel[0],
                     label=models[0])
    axis[0].fill_between(zvals, -(v12_GR[0:3] + v12_GR[3::]),
                         -(v12_GR[0:3] - v12_GR[3::]), color=cmodel[0],
                         alpha=0.2)
    axis[0].errorbar(zvals, -v12_F5[0:3], yerr=v12_F5[3::], marker='v', ls=ls_sim, capsize=4, c=cmodel[1],
                     label=models[1])
    axis[0].fill_between(zvals, -(v12_F5[0:3] + v12_F5[3::]),
                         -(v12_F5[0:3] - v12_F5[3::]), color=cmodel[1],
                         alpha=0.2)

    axis[0].errorbar(zvals, -v12_F6[0:3], yerr=v12_F6[3::], marker='P', ls=ls_sim, capsize=4, c=cmodel[2],
                     label=models[2])
    axis[0].fill_between(zvals, -(v12_F6[0:3] + v12_F6[3::]),
                         -(v12_F6[0:3] - v12_F6[3::]), color=cmodel[2],
                         alpha=0.2)

    axis[0].errorbar(zvals, -v12_N1[0:3], yerr=v12_N1[3::], c=cmodel[3], marker='s', ls=ls_sim, capsize=4,
                     label=models[3])
    axis[0].fill_between(zvals, -(v12_N1[0:3] + v12_N1[3::]),
                         -(v12_N1[0:3] - v12_N1[3::]), color=cmodel[3],
                         alpha=0.2)

    axis[0].errorbar(zvals, -v12_N5[0:3], yerr=v12_N5[3::], c=cmodel[4], marker='v', ls=ls_sim, capsize=4,
                     label=models[4])
    axis[0].fill_between(zvals, -(v12_N5[0:3] + v12_N5[3::]),
                         -(v12_N5[0:3] - v12_N5[3::]), color=cmodel[4],
                         alpha=0.2)

    # ------ model/theory
    axis[0].plot(newzss, v12Peak_smooth_GR, color=cmodel[0], ls=ls_sol, label =r'BBKGY-Halofit')
    # axis[0].plot(peakRstarDF_dict['GR'].z.values[:sl], v12Peak_smooth_GR, color=cmodel[0], ls=ls_sol, label =r'BBKGY-Halofit')
    #
    axis[0].plot(peakRstarDF_dict['F5'].z.values[:sl], v12Peak_smooth_F5, color=cmodel[1], ls=ls_sol)
    #
    axis[0].plot(peakRstarDF_dict['F6'].z.values[:sl], v12Peak_smooth_F6, color=cmodel[2], ls=ls_sol)
    #
    axis[0].plot(peakRstarDF_dict['N1'].z.values[:sl], v12Peak_smooth_N1, color=cmodel[3], ls=ls_sol)
    #
    axis[0].plot(peakRstarDF_dict['N5'].z.values[:sl], v12Peak_smooth_N5, color=cmodel[4], ls=ls_sol)

    #  ----------------------------------------
    ### ===== rstar plots
    # ----- data

    axis[1].errorbar(zvals, Rs_GR[0:3], yerr=Rs_GR[3::] * mult, marker='o', ls=ls_sim, capsize=4, c=cmodel[0],
                     label=models[0])
    axis[1].fill_between(zvals, (Rs_GR[0:3] + Rs_GR[3::]* mult),
                         (Rs_GR[0:3] - Rs_GR[3::]* mult), color=cmodel[0],
                         alpha=0.2)

    axis[1].errorbar(zvals, Rs_F5[0:3], yerr=Rs_F5[3::] * mult, marker='o', ls=ls_sim, capsize=4, c=cmodel[1],
                     label=models[1])
    axis[1].fill_between(zvals, (Rs_F5[0:3] + Rs_F5[3::] * mult),
                         (Rs_F5[0:3] - Rs_F5[3::] * mult), color=cmodel[1],
                         alpha=0.2)

    axis[1].errorbar(zvals, Rs_F6[0:3], yerr=Rs_F6[3::] * mult, marker='o', ls=ls_sim, capsize=4, c=cmodel[2],
                     label=models[2])
    axis[1].fill_between(zvals, (Rs_F6[0:3] + Rs_F6[3::] * mult),
                         (Rs_F6[0:3] - Rs_F6[3::] * mult), color=cmodel[2],
                         alpha=0.2)

    axis[1].errorbar(zvals, Rs_N1[0:3], yerr=Rs_N1[3::] * mult, marker='o', ls=ls_sim, capsize=4, c=cmodel[3],
                     label=models[3])
    axis[1].fill_between(zvals, (Rs_N1[0:3] + Rs_N1[3::] * mult),
                         (Rs_N1[0:3] - Rs_N1[3::] * mult), color=cmodel[3],
                         alpha=0.2)

    axis[1].errorbar(zvals, Rs_N5[0:3], yerr=Rs_N5[3::] * mult, marker='o', ls=ls_sim, capsize=4, c=cmodel[4],
                     label=models[4])
    axis[1].fill_between(zvals, (Rs_N5[0:3] + Rs_N5[3::] * mult),
                         (Rs_N5[0:3] - Rs_N5[3::] * mult), color=cmodel[4],
                         alpha=0.2)


    # ------- models
    Rs_smooth_GR = savgol_filter(peakRstarDF_dict['GR'].Rs.values[:sl], window_size, order)
    Rs_smooth_F5 = savgol_filter(peakRstarDF_dict['F5'].Rs.values[:sl], window_size, order)
    Rs_smooth_F6 = savgol_filter(peakRstarDF_dict['F6'].Rs.values[:sl], window_size, order)
    Rs_smooth_N5 = savgol_filter(peakRstarDF_dict['N5'].Rs.values[:sl], window_size, order)
    Rs_smooth_N1 = savgol_filter(peakRstarDF_dict['N1'].Rs.values[:sl], window_size, order)

    axis[1].plot(peakRstarDF_dict['GR'].z.values[:sl], Rs_smooth_GR, color=cmodel[0], ls=ls_sol, label =r'BBKGY-Halofit')
    axis[1].plot(peakRstarDF_dict['F5'].z.values[:sl], Rs_smooth_F5, color=cmodel[1], ls=ls_sol)
    axis[1].plot(peakRstarDF_dict['F6'].z.values[:sl], Rs_smooth_F6, color=cmodel[2], ls=ls_sol)
    axis[1].plot(peakRstarDF_dict['N1'].z.values[:sl], Rs_smooth_N1, color=cmodel[3], ls=ls_sol)
    axis[1].plot(peakRstarDF_dict['N5'].z.values[:sl], Rs_smooth_N5, color=cmodel[4], ls=ls_sol)

    axis[0].set_ylabel(r'$|\hat{v}_{12}|[km/s]$', size=30)
    axis[1].set_ylabel(r'$R_*(z)[Mpc/h]$', size=30)

    axis[0].set_ylim(245, 405)
    axis[1].set_ylim(3.9, 5.5)
    # Hide x-axis labels for the first row
    axis[0].tick_params(axis='x', labelleft=False)
    # Show x-axis label only for the 2nd row
    axis[1].set_xlabel(r'$z$', size=30)

    for i in range(nrows):
        axis[i].tick_params(axis='both', which='major', labelsize=26)
        axis[i].tick_params(axis='both', which='minor', labelsize=20)
        axis[i].xaxis.set_major_formatter(FancyFormatter())
        axis[i].yaxis.set_major_formatter(FancyFormatter())
        # axis[i].legend(fontsize=15)
    axis[0].legend(ncol=6, fontsize=15, loc="upper center",
                    bbox_to_anchor=(0., 1.02, 1., .102), mode="expand",
                    borderaxespad=0.)
    # print('---- Figure 4 done -----')
    # ----------------- Saving  ---------------------

    if save_figure:

        plt.savefig(full_fig_name, bbox_inches='tight', dpi=dpi)
        print('Figure saved at ', str(figpath) + str(figname),
              ' in the format: ', str(fig_type))

    else:
        print('Figure NOT saved ')

    return

def figure_deriv_xi():
    """
     This is a copy taken directly from http://localhost:7778/lab/tree/notebooks/v12/derivative_xi_r.ipynb
     to save the settings used to produce the figure.
     Needs to be adjusted for style and adapt the function to work on its own.

    # source:  https://stackoverflow.com/questions/25408393/getting-individual-colors-from-a-color-map-in-matplotlib
    # https://github.com/binodbhttr/mycolorpy/blob/master/usage_example.ipynb
    needs: from mycolorpy import colorlist as mcp

    Depends on: r_vals, v12_MODEL_ZVAL, aa, zz, xi_MODEL_ZVAL, dxida_MODEL_ZVAL  = v12_from_numerical_deriv()
    Returns
    -------

    """
    fig, axes = plt.subplots(1, figsize=(15, 10), sharex=True)
    ax = axes

    ### creating a color list
    color2 = mcp.gen_color(cmap="gnuplot2", n=16)

    rcParams['font.size'] = 25
    rcParams['lines.linewidth'] = 2
    rcParams['mathtext.fontset'] = 'cm'

    linew = 3
    msize = 12

    ax.plot(r_vals, dxida_gr_z00 / 1000, marker='.', markersize=msize, linestyle='-', lw=linew, mfc=cmodel[0],
            label=r'GR: $z(a_i)= 0.0$', color=cmodel[0])
    ax.plot(r_vals, dxida_f5_z00 / 1000, 'x-', markersize=msize, lw=linew, label=r'F5', color=cmodel[1])
    ax.plot(r_vals, dxida_f6_z00 / 1000, marker='+', markersize=msize, ls='-', lw=linew, label=r'F6', color=cmodel[2])
    ax.plot(r_vals, dxida_n1_z00 / 1000, marker='*', markersize=msize, ls='-', lw=linew, label=r'N1', color=cmodel[3])
    ax.plot(r_vals, dxida_n5_z00 / 1000, marker='v', markersize=msize, ls='-', lw=linew, label=r'N5', color=cmodel[4])

    # ax.plot(r_vals, dxida_gr_z03, ls=':',label = r'GR: $z(a_i)= 0.3$', color=cmodel[0])
    # ax.plot(r_vals, dxida_f5_z03, ls=':',label = r'F5', color=cmodel[1])
    # ax.plot(r_vals, dxida_f6_z03, ls=':',label = r'F6', color=cmodel[2])
    # ax.plot(r_vals, dxida_n1_z03, ls=':',label = r'N1', color=cmodel[3])
    # ax.plot(r_vals, dxida_n5_z03, ls=':',label = r'N5', color=cmodel[4])

    ax.plot(r_vals, dxida_gr_z05 / 1000, marker='.', markersize=msize, linestyle='--', mfc=cmodel[0],
            label=r'GR: $z(a_i)= 0.5$', color=cmodel[0])
    # ax.plot(r_vals, dxida_gr_z05,ls='--', lw=linew, label = r'GR: $z(a_i)= 0.5$', color=cmodel[0])

    ax.plot(r_vals, dxida_f5_z05 / 1000, marker='x', markersize=msize, linestyle='--', lw=linew, label=r'F5',
            color=cmodel[1])
    ax.plot(r_vals, dxida_f6_z05 / 1000, marker='+', markersize=msize, ls='--', lw=linew, label=r'F6', color=cmodel[2])
    ax.plot(r_vals, dxida_n1_z05 / 1000, marker='*', markersize=msize, ls='--', lw=linew, label=r'N1', color=cmodel[3])
    ax.plot(r_vals, dxida_n5_z05 / 1000, marker='v', markersize=msize, ls='--', lw=linew, label=r'N5', color=cmodel[4])

    a_vals = scalefactor_from_redshift(z_vals)

    ax.set_xscale('log')
    ax.legend(ncol=2, fontsize=25)
    ax.set_xlim(r_vals.min(), 3)
    ax.xaxis.set_major_formatter(FancyFormatter())
    ax.yaxis.set_major_formatter(FancyFormatter())

    ax.set_xlabel(r'$r [Mpc/h]$', size=45)
    ax.set_ylabel(r'$(10^{-3})\partial\bar\xi(r,a)/\partial a |_{a_i}$', size=45)

    figname = 'deriv_xibar_models_v2'
    # savefig('/home/jaber/shared/data/figs/'+figname+'.pdf', bbox_inches='tight', dpi=1200)


def figure_Deriv_xi_inset():
    """
        This is a copy taken directly from http://localhost:7778/lab/tree/notebooks/v12/derivative_xi_r.ipynb
        to save the settings used to produce the figure.
        Needs to be adjusted for style and adapt the function to work on its own.

       # source:  https://stackoverflow.com/questions/25408393/getting-individual-colors-from-a-color-map-in-matplotlib
       # https://github.com/binodbhttr/mycolorpy/blob/master/usage_example.ipynb
       needs: from mycolorpy import colorlist as mcp

       Depends on: r_vals, v12_MODEL_ZVAL, aa, zz, xi_MODEL_ZVAL, dxida_MODEL_ZVAL  = v12_from_numerical_deriv()
       Returns
       -------

       """
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    ncols, nrows = 1, 1
    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=False, sharey=False,
                              # gridspec_kw={'height_ratios': [1,1]},
                              figsize=(20, 15), facecolor='w', edgecolor='k')
    figure.subplots_adjust(hspace=.01, wspace=.01)

    ###############
    ### SPECS ###
    ### This is what's formatting the figure, not the FancyFormatter class

    ### creating a color list
    color2 = mcp.gen_color(cmap="gnuplot2", n=16)

    rcParams['font.size'] = 25
    rcParams['lines.linewidth'] = 2
    rcParams['mathtext.fontset'] = 'cm'

    linew = 3
    msize = 10
    fs_xaxis, fs_yaxis = 40, 35
    mmodel = ['.', 'x', 'd', '*', 'v']

    # Plot data in the main plot
    ax.text(0.01, 8.1, '$1000$', fontsize=35)

    ax.plot(r_vals, dxida_gr_z00 / 1000, marker='.', markersize=msize, linestyle='-', lw=linew, mfc=cmodel[0],
            label=r'GR: $z(a_i)= 0.0$', color=cmodel[0])
    ax.plot(r_vals, dxida_f5_z00 / 1000, 'x-', markersize=msize, lw=linew, label=r'F5', color=cmodel[1])
    ax.plot(r_vals, dxida_f6_z00 / 1000, marker='+', markersize=msize, ls='-', lw=linew, label=r'F6', color=cmodel[2])
    ax.plot(r_vals, dxida_n1_z00 / 1000, marker='*', markersize=msize, ls='-', lw=linew, label=r'N1', color=cmodel[3])
    ax.plot(r_vals, dxida_n5_z00 / 1000, marker='v', markersize=msize, ls='-', lw=linew, label=r'N5', color=cmodel[4])

    # ax.plot(r_vals, dxida_gr_z03, ls=':',label = r'GR: $z(a_i)= 0.3$', color=cmodel[0])
    # ax.plot(r_vals, dxida_f5_z03, ls=':',label = r'F5', color=cmodel[1])
    # ax.plot(r_vals, dxida_f6_z03, ls=':',label = r'F6', color=cmodel[2])
    # ax.plot(r_vals, dxida_n1_z03, ls=':',label = r'N1', color=cmodel[3])
    # ax.plot(r_vals, dxida_n5_z03, ls=':',label = r'N5', color=cmodel[4])

    ax.plot(r_vals, dxida_gr_z05 / 1000, marker='.', markersize=msize, linestyle='--', mfc=cmodel[0],
            label=r'GR: $z(a_i)= 0.5$', color=cmodel[0])
    # ax.plot(r_vals, dxida_gr_z05,ls='--', lw=linew, label = r'GR: $z(a_i)= 0.5$', color=cmodel[0])

    ax.plot(r_vals, dxida_f5_z05 / 1000, marker='x', markersize=msize, linestyle='--', lw=linew, label=r'F5',
            color=cmodel[1])
    ax.plot(r_vals, dxida_f6_z05 / 1000, marker='+', markersize=msize, ls='--', lw=linew, label=r'F6', color=cmodel[2])
    ax.plot(r_vals, dxida_n1_z05 / 1000, marker='*', markersize=msize, ls='--', lw=linew, label=r'N1', color=cmodel[3])
    ax.plot(r_vals, dxida_n5_z05 / 1000, marker='v', markersize=msize, ls='--', lw=linew, label=r'N5', color=cmodel[4])

    a_vals = scalefactor_from_redshift(z_vals)

    ax.set_xscale('log')
    ax.legend(ncol=2, fontsize=25, frameon=False)
    # ax.set_xlim(r_vals.min(), 3)
    ax.xaxis.set_major_formatter(FancyFormatter())
    ax.yaxis.set_major_formatter(FancyFormatter())

    ax.set_xlabel(r'$r [Mpc/h]$', size=45)
    ax.set_ylabel(r'$\partial\bar\xi(r,a)/\partial a |_{a_i}$', size=55)

    # ------ Create an inset plot within the main plot
    axins = inset_axes(ax, width='56%', height='50%', loc='center right')
    ##
    axins.plot(r_vals, 1 / (3 * (1 + xi_gr_z00)), ls='-', lw=linew, color=cmodel[0], label=r'$z= 0.0$')
    axins.plot(r_vals, 1 / (3 * (1 + xi_gr_z00)), ls='-', lw=linew, color=cmodel[1])
    axins.plot(r_vals, 1 / (3 * (1 + xi_gr_z00)), ls='-', lw=linew, color=cmodel[2])
    axins.plot(r_vals, 1 / (3 * (1 + xi_gr_z00)), ls='-', lw=linew, color=cmodel[3])
    axins.plot(r_vals, 1 / (3 * (1 + xi_gr_z00)), ls='-', lw=linew, color=cmodel[4])

    axins.plot(r_vals, scalefactor_from_redshift(0.5) / (3 * (1 + xi_gr_z05)), ls='--', label=r' $z= 0.5$',
               color=cmodel[0])
    axins.plot(r_vals, scalefactor_from_redshift(0.5) / (3 * (1 + xi_f5_z05)), ls='--', lw=linew, color=cmodel[1])
    axins.plot(r_vals, scalefactor_from_redshift(0.5) / (3 * (1 + xi_f6_z05)), ls='--', lw=linew, color=cmodel[2])
    axins.plot(r_vals, scalefactor_from_redshift(0.5) / (3 * (1 + xi_n1_z05)), ls='--', lw=linew, color=cmodel[3])
    axins.plot(r_vals, scalefactor_from_redshift(0.5) / (3 * (1 + xi_n5_z05)), ls='--', lw=linew, color=cmodel[4])
    ##

    axins.set_xscale('log')
    axins.xaxis.set_major_formatter(FancyFormatter())
    axins.yaxis.set_major_formatter(FancyFormatter())
    axins.legend(frameon=False, ncol=2)
    axins.set_ylabel(r'$a_i/3(1+\xi(r,a_i))$', size=40)
    axins.set_xlabel(r'$r [Mpc/h]$', size=40)

    # Add a connector line between the main plot and the inset plot
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset
    # mark_inset(ax_main, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    # Size of ticklabels
    ax.tick_params(axis='x', labelsize=fs_xaxis)
    ax.tick_params(axis='y', labelsize=fs_yaxis)


def figure_stable_clustering_visual():
    '''
    This is a copy taken directly from http://localhost:7778/lab/tree/notebooks/v12/test_rstar.ipynb to save the settings
    used to produce the figure. Needs to be adjusted for style and adapt the function to work on its own

    Depends on: calculate_rH_array() and v12_merged_data()


    Returns
    -------

    '''

    ncols, nrows = 1, 2
    model = ["GR", "F5", "F6", "N1", "N5"]
    cmodel = ["k", "#029e74", "#0273b2", "#d96d19", "#aa007f"]
    mmodel = ['.', 'x', 'd', '*', 'v']

    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=True, sharey=False,
                              figsize=(10, 20), facecolor='w', edgecolor='k')

    figure.subplots_adjust(hspace=.07, wspace=0.15)

    mpl.rcParams['font.size'] = 45
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'
    mpl.rcParams['axes.titlesize'] = 30  # fontsize of the axes title
    mpl.rcParams['axes.labelsize'] = 30  # fontsize of the x any y labels

    fs_xaxis, fs_yaxis = 22, 25
    fs_text = 25
    sz = 20
    lw_hf = 3
    csz = 3
    ax[0].errorbar(v12_merged_data['GR']['z0.0'].r.values, -v12_merged_data['GR']['z0.0'].v12.values,
                   yerr=-v12_merged_data['GR']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[0], elinewidth=3, capsize=csz, color=cmodel[0], label=model[0])
    ax[0].plot(v12_merged_data['GR']['z0.0'].r.values, calculate_rH_array(v12_merged_data, 'GR', 'z0.0', 0), ls='--',
               color=cmodel[0], label='rH(z)')
    ax[0].axvline(Rs_GR[0], ls=':', color=cmodel[0])

    ax[0].errorbar(v12_merged_data['F5']['z0.0'].r.values, -v12_merged_data['F5']['z0.0'].v12.values,
                   yerr=-v12_merged_data['F5']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[1], elinewidth=3, capsize=csz, color=cmodel[1], label=model[1])
    ax[0].axvline(Rs_F5[0], ls=':', color=cmodel[1])

    ax[0].errorbar(v12_merged_data['F6']['z0.0'].r.values, -v12_merged_data['F6']['z0.0'].v12.values,
                   yerr=-v12_merged_data['F6']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[2], elinewidth=3, capsize=csz, color=cmodel[2], label=model[2])
    ax[0].axvline(Rs_F6[0], ls=':', color=cmodel[2])

    ax[1].errorbar(v12_merged_data['GR']['z0.0'].r.values, -v12_merged_data['GR']['z0.0'].v12.values,
                   yerr=-v12_merged_data['GR']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[0], elinewidth=3, capsize=csz, color=cmodel[0], label=model[0])
    ax[1].plot(v12_merged_data['GR']['z0.0'].r.values, calculate_rH_array(v12_merged_data, 'GR', 'z0.0', 0), ls='--',
               color=cmodel[0], label='rH(z)')
    ax[1].axvline(Rs_GR[0], ls=':', color=cmodel[0])

    ax[1].errorbar(v12_merged_data['N1']['z0.0'].r.values, -v12_merged_data['N1']['z0.0'].v12.values,
                   yerr=-v12_merged_data['N1']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[3], elinewidth=3, capsize=csz, color=cmodel[3], label=model[3])
    ax[1].axvline(Rs_N1[0], ls=':', color=cmodel[3])

    ax[1].errorbar(v12_merged_data['N5']['z0.0'].r.values, -v12_merged_data['N5']['z0.0'].v12.values,
                   yerr=-v12_merged_data['N5']['z0.0'].Errv12.values,
                   markeredgewidth=1, marker=mmodel[4], elinewidth=3, capsize=csz, color=cmodel[4], label=model[4])
    ax[1].axvline(Rs_N5[0], ls=':', color=cmodel[4])

    for i in range(nrows):
        # Show legends
        ax[i].legend(fontsize=15)
        # Lg scale
        ax[i].set_xscale('log')
        # Lim on y values
        ax[i].set_ylim(-10, 400)
        ax[i].set_xlim(1, 40)
        ax[i].set_ylabel(r'$-v_{12}(r)$', fontsize=30)

    ax[1].set_xlabel(r'$r$[Mpc/h]', fontsize=30)

    figpath = '/home/jaber/shared/data/figs/'
    figname = 'rstar_allmodels_sim_data_z0.pdf'

    full_fig_name = figpath + figname
    # plt.savefig(full_fig_name, bbox_inches='tight')

def figure1_1column():
    ncols, nrows = 1, 9
    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=False, sharey=False,
                              gridspec_kw={'height_ratios': [2, 2, 1, 2, 2, 1, 2, 2, 1]},
                              figsize=(16, 38), facecolor='w', edgecolor='k')
    figure.subplots_adjust(hspace=.2, wspace=.01)

    ###############
    ### SPECS ###
    ### This is what's formatting the figure, not the FancyFormatter class
    plt.rcParams['font.size'] = 35
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['mathtext.fontset'] = 'cm'

    xtext, ytext = 108, -200
    fs_xaxis, fs_yaxis = 32, 28
    fs_text = 50
    rmin, rmaxlin, rmaxlog = 0.1, 140, 40

    msize, csize = 16, 10
    lw_hf = 5
    lwi = 4

    ################# LARGE SCALES no modification needed #################
    ##### z00
    # data from sims
    ax[0].errorbar(V12_GR_R140_z00['r'], V12_GR_R140_z00['v12'], yerr=V12_GR_R140_z00['Errv12'], marker='.',
                   capsize=csize, ms=msize, ls='none', c='black', label='DM particles')
    ax[0].fill_between(V12_GR_R140_z00['r'], V12_GR_R140_z00['v12'] - V12_GR_R140_z00['Errv12'],
                       V12_GR_R140_z00['v12'] + V12_GR_R140_z00['Errv12'], alpha=0.2)

    # model halofit
    ax[0].plot(r140, v12_hf_r140_z00, ls='-', c='red', lw=lw_hf, ms=3, label=r'BBKGY-Halofit')
    ax[0].plot(r140, v12_lin_r140_z00, ls='--', c='green', lw=4, ms=3, label=r'BBKGY-Linear')
    ax[0].plot(r140, v12_qlin_r140_z00, ls='-.', c='purple', lw=4, ms=3, label=r'Quasilinear')

    # model CLPT
    ax[0].plot(v12clpt140[0]['z0.0'].r, v12_clpt_140_00, ls=':', lw=lw_hf, c='blue', label='CLPT')

    ax[0].text(xtext, ytext, r'$z=0.0$', fontsize=fs_text)

    #################  INTERMEDIATE SCALES: with new errors from Hellwing  #################

    #####
    ax[1].scatter(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values, marker='.', c='black')
    ax[1].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values, yerr=v12_GR_Z00_merged.Errv12.values,
                   marker='.', ms=msize, ls='none', c='black')
    ax[1].fill_between(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                       v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values, alpha=0.2)

    ax[1].plot(r40, v12_hf_r40_z00, ls='-', c='red', lw=lw_hf, ms=3)
    ax[1].plot(r40, v12_lin_r40_z00, ls='--', c='green', lw=lw_hf, ms=3)
    ax[1].plot(r40, v12_qlin_r40_z00, ls='-.', c='purple', lw=lw_hf, ms=3)

    # ax[1,0].plot(v12_hf_r40_z00_df_new.r.values, v12_hf_r40_z00_df_new.v12.values, ls ='-',c='red', lw=lw_hf, ms=3)
    # ax[1,0].plot(v12_lin_r40_z00_df_new.r.values, v12_lin_r40_z00_df_new.v12.values, ls ='--',c='green', lw=lw_hf, ms=3)

    # model CLPT
    ax[1].plot(v12clpt40[0]['z0.0'].r, v12_clpt_40_00, ls=':', lw=lw_hf, c='blue')

    ##### z03
    # data from sims

    ax[3].errorbar(V12_GR_R140_z03['r'], V12_GR_R140_z03['v12'], yerr=V12_GR_R140_z03['Errv12'], marker='.', ms=msize,
                   ls='none', c='black')
    ax[3].fill_between(V12_GR_R140_z03['r'], V12_GR_R140_z03['v12'] - V12_GR_R140_z03['Errv12'],
                       V12_GR_R140_z03['v12'] + V12_GR_R140_z03['Errv12'], alpha=0.2)

    # model halofit linear quasilinear
    ax[3].plot(r140, v12_hf_r140_z03, ls='-', c='red', lw=lw_hf, ms=3)
    ax[3].plot(r140, v12_lin_r140_z03, ls='--', c='green', lw=lw_hf, ms=3)
    ax[3].plot(r140, v12_qlin_r140_z03, ls='-.', c='purple', lw=4, ms=3)

    # model CLPT
    ax[3].plot(v12clpt140[0]['z0.3'].r, v12_clpt_140_03, ls=':', lw=lw_hf, c='blue')

    ax[3].text(xtext, ytext, r'$z=0.3$', fontsize=fs_text)

    #####

    ax[4].scatter(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values, marker='.', c='black')
    ax[4].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values, yerr=v12_GR_Z03_merged.Errv12.values,
                   marker='.', ms=msize, ls='none', c='black')
    ax[4].fill_between(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                       v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values, alpha=0.2)

    ax[4].plot(r40, v12_hf_r40_z03, ls='-', c='red', lw=lw_hf, ms=3)
    ax[4].plot(r40, v12_lin_r40_z03, ls='--', c='green', lw=lw_hf, ms=3)
    ax[4].plot(r40, v12_qlin_r40_z03, ls='-.', c='purple', lw=lw_hf, ms=3)

    # model CLPT
    ax[4].plot(v12clpt40[0]['z0.3'].r, v12_clpt_40_03, ls=':', lw=lw_hf, c='blue')

    ##### z05
    # data from sims
    ax[6].errorbar(V12_GR_R140_z05['r'], V12_GR_R140_z05['v12'], yerr=V12_GR_R140_z05['Errv12'], marker='.', ms=msize,
                   ls='none', c='black')
    ax[6].fill_between(V12_GR_R140_z05['r'], V12_GR_R140_z05['v12'] - V12_GR_R140_z05['Errv12'],
                       V12_GR_R140_z05['v12'] + V12_GR_R140_z05['Errv12'], alpha=0.2)

    # model halofit linear quasilinear
    ax[6].plot(r140, v12_hf_r140_z05, ls='-', c='red', lw=lw_hf, ms=3)
    ax[6].plot(r140, v12_lin_r140_z05, ls='--', c='green', lw=lw_hf, ms=3)
    ax[6].plot(r140, v12_qlin_r140_z05, ls='-.', c='purple', lw=4, ms=3)

    # model CLPT
    ax[6].plot(v12clpt140[0]['z0.5'].r, v12_clpt_140_05, ls=':', lw=lw_hf, c='blue')

    ax[6].text(xtext, ytext, r'$z=0.5$', fontsize=fs_text)
    #####
    ax[7].scatter(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values, marker='.', c='black')
    ax[7].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values, yerr=v12_GR_Z05_merged.Errv12.values,
                   marker='.', ms=msize, ls='none', c='black')
    ax[7].fill_between(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                       v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values, alpha=0.2)

    ax[7].plot(r40, v12_hf_r40_z05, ls='-', c='red', lw=lw_hf, ms=3)
    ax[7].plot(r40, v12_lin_r40_z05, ls='--', c='green', lw=lw_hf, ms=3)
    ax[7].plot(r40, v12_qlin_r40_z05, ls='-.', c='purple', lw=lw_hf, ms=3)

    # model CLPT
    ax[7].plot(v12clpt40[0]['z0.5'].r, v12_clpt_40_05, ls=':', lw=lw_hf, c='blue')

    ########### RATIOS

    ax[2].set_ylim(-21, 21)
    ax[5].set_ylim(-21, 21)
    ax[8].set_ylim(-21, 21)

    ax[2].plot(r40, (1 - v12_hf_r40_z00 / v12_GR_Z00_merged.v12.values) * 100, c='red', lw=lw_hf)
    ax[5].plot(r40, (1 - v12_hf_r40_z03 / v12_GR_Z03_merged.v12.values) * 100, c='red', lw=lw_hf)
    ax[8].plot(r40, (1 - v12_hf_r40_z05 / v12_GR_Z05_merged.v12.values) * 100, c='red', lw=lw_hf)

    ax[2].plot(r40, (1 - v12_lin_r40_z00 / v12_GR_Z00_merged.v12.values) * 100, c='green', ls='--', lw=lw_hf)
    ax[5].plot(r40, (1 - v12_lin_r40_z03 / v12_GR_Z03_merged.v12.values) * 100, c='green', ls='--', lw=lw_hf)
    ax[8].plot(r40, (1 - v12_lin_r40_z05 / v12_GR_Z05_merged.v12.values) * 100, c='green', ls='--', lw=lw_hf)

    # ax[2].plot(r40, (1-v12_qlin_r40_z00/v12_GR_Z00_merged.v12.values)*100, c='purple', ls ='-.', lw=lw_hf )
    # ax[5].plot(r40, (1-v12_qlin_r40_z03/v12_GR_Z03_merged.v12.values)*100, c='purple', ls ='-.', lw=lw_hf )
    # ax[8].plot(r40, (1-v12_qlin_r40_z05/v12_GR_Z05_merged.v12.values)*100, c='purple', ls ='-.', lw=lw_hf )

    ax[2].fill_between(v12_GR_Z00_merged.r.values, -v12_GR_Z00_merged.Errv12.values, v12_GR_Z00_merged.Errv12.values,
                       alpha=0.2)
    ax[5].fill_between(v12_GR_Z03_merged.r.values, -v12_GR_Z03_merged.Errv12.values, v12_GR_Z03_merged.Errv12.values,
                       alpha=0.2)
    ax[8].fill_between(v12_GR_Z05_merged.r.values, -v12_GR_Z05_merged.Errv12.values, v12_GR_Z05_merged.Errv12.values,
                       alpha=0.2)

    ####

    ax[0].set_ylabel(r'$v_{12}(r)$', fontsize=50)
    ax[1].set_ylabel(r'$v_{12}(r)$', fontsize=50)
    ax[3].set_ylabel(r'$v_{12}(r)$', fontsize=50)
    ax[4].set_ylabel(r'$v_{12}(r)$', fontsize=50)
    ax[6].set_ylabel(r'$v_{12}(r)$', fontsize=50)
    ax[7].set_ylabel(r'$v_{12}(r)$', fontsize=50)

    ax[2].set_ylabel(r'$\Delta v_{12}[\%]$', fontsize=40)
    ax[5].set_ylabel(r'$\Delta v_{12}[\%]$', fontsize=40)
    ax[8].set_ylabel(r'$\Delta v_{12}[\%]$', fontsize=40)

    ax[1].set_xscale('log')
    ax[2].set_xscale('log')
    ax[4].set_xscale('log')
    ax[5].set_xscale('log')
    ax[7].set_xscale('log')
    ax[8].set_xscale('log')

    # Increase tick label font size
    # ax[i].tick_params(axis='y', labelsize=fs_yaxis)

    ax[0].set_xlim(rmin, rmaxlin)
    ax[1].set_xlim(rmin, rmaxlog)
    ax[2].set_xlim(rmin, rmaxlog)
    ax[3].set_xlim(rmin, rmaxlin)
    ax[4].set_xlim(rmin, rmaxlog)
    ax[5].set_xlim(rmin, rmaxlog)
    ax[6].set_xlim(rmin, rmaxlin)

    ax[7].set_xlim(rmin, rmaxlog)
    ax[8].set_xlim(rmin, rmaxlog)

    ax[8].set_xlabel(r'$r$[Mpc/h]', fontsize=50)
    # ax[3, 1].set_xlabel(r'$r$[Mpc/h]', fontsize=30)
    ax[0].tick_params(axis='x', labelsize=28)

    lower, upper = -10, 10

    ax[2].axhline(lower, ls=':', lw=2, color='k')
    ax[2].axhline(upper, ls=':', lw=2, color='k')
    ax[2].axhline(lower / 2, ls=':', lw=2, color='k')
    ax[2].axhline(upper / 2, ls=':', lw=2, color='k')

    ax[5].axhline(lower, ls=':', lw=2, color='k')
    ax[5].axhline(upper, ls=':', lw=2, color='k')
    ax[5].axhline(lower / 2, ls=':', lw=2, color='k')
    ax[5].axhline(upper / 2, ls=':', lw=2, color='k')

    ax[8].axhline(lower, ls=':', lw=2, color='k')
    ax[8].axhline(upper, ls=':', lw=2, color='k')
    ax[8].axhline(lower / 2, ls=':', lw=2, color='k')
    ax[8].axhline(upper / 2, ls=':', lw=2, color='k')

    # Hide y-axis labels for the 2nd and 3rd column
    ax[1].tick_params(axis='x', bottom=False)
    ax[4].tick_params(axis='x', bottom=False)

    for i in range(nrows):
        ax[i].tick_params(axis='y', labelsize=fs_yaxis)
        ax[i].tick_params(axis='x', labelsize=fs_xaxis)

        ax[i].xaxis.set_major_formatter(FancyFormatter())
        ax[i].yaxis.set_major_formatter(FancyFormatter())

    ax[0].legend(ncol=3, loc='upper center', bbox_to_anchor=(0.45, 1.6), fontsize=35)

    # ################################## SPECS ##################################

    figname = 'fig1_v12_GR_1column'

    # savefig('/home/jaber/shared/data/figs/'+figname+'.pdf', bbox_inches='tight', dpi=1200)

    #


def figure2_2columns():
    figpath = '/home/jaber/shared/data/figs/'
    figname = 'fig2_twocolumns_gupta'
    fig_ext = '.pdf'
    dpi = 1200
    full_fig_name = figpath + figname + str(fig_ext)

    #####################################################################################################
    #####################################################################################################
    # ---------- FIGURE BEGINS HERE -------------- #

    nrows, ncols = 6, 2

    models = ["GR", "F5", "F6", "N1", "N5"]
    cmodel = ["k", "#029e74", "#0273b2", "#d96d19", "#aa007f"]
    z_snap = ['0.0', '0.3', '0.5']

    ### This is what's formatting the figure, not the FancyFormatter class
    mpl.rcParams['font.size'] = 35
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['mathtext.fontset'] = 'cm'

    figure, ax = plt.subplots(nrows=nrows, ncols=ncols,
                              sharex=False, sharey=False,
                              gridspec_kw={'height_ratios': [2, 1, 2, 1, 2, 1]},
                              figsize=(34, 38), facecolor='w', edgecolor='k')
    figure.subplots_adjust(hspace=.01, wspace=.01)

    ###############
    ### SPECS ###
    xtext, ytext = 0.1, -300
    fs_xaxis, fs_yaxis = 50, 50
    fs_x_text, fs_text = 70, 87
    msize, csize = 18, 8
    lwhm, lw1 = 5, 3
    labelhf = 'BBKGY-Halofit'
    labelhm = 'BBKGY-Gupta+(23)'

    lower, upper = -10, 10

    for i in range(nrows):
        ax[i, 1].tick_params(axis='y', labelleft=False)
        ax[i, 0].tick_params(axis='y', labelsize=fs_yaxis)

    for i in [1, 3, 5]:
        #     #### y-axis labels
        ax[i - 1, 0].set_ylabel(r'$v_{12}(r)$', fontsize=1.5 * fs_text)
        ax[i, 0].set_ylabel(r'$\Delta v_{12}$[%]', fontsize=0.8 * fs_text)
        for j in range(ncols):
            ax[i, j].set_ylim(-21, 21)
            ax[i - 1, j].set_ylim(-450, 50)

    for j in range(ncols):
        ax[5, j].set_xlabel(r'$r[Mpc/h]$', fontsize=fs_x_text)
        ax[5, j].tick_params(axis='x', labelsize=fs_xaxis)
        for i in range(5):
            ax[i, j].tick_params(axis='x', labelbottom=False)

        for i in range(nrows):
            ax[i, j].set_xlim(0.04, 50)
            ax[i, j].set_xscale('log')
            # Hide y-axis labels for the 2nd and 3rd column
            ax[i, 1].tick_params(axis='y', labelleft=False)
            ax[i, j].xaxis.set_major_formatter(FancyFormatter())
            ax[i, j].yaxis.set_major_formatter(FancyFormatter())
        for i in [1, 3, 5]:
            ax[i, j].axhline(0, ls='-', lw=1, color='gray')
            ax[i, j].axhline(lower, ls=':', lw=1, color='k')
            ax[i, j].axhline(upper, ls=':', lw=1, color='k')
            ax[i, j].axhline(lower / 2, ls=':', lw=1, color='k')
            ax[i, j].axhline(upper / 2, ls=':', lw=1, color='k')

        ####  lines done first to be on the background of the figure

    # ax[2].axhline(lower / 2, ls=':', lw=1, color='k')

    ##### ---------------- fofr ---------------

    ax[0, 0].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                      yerr=v12_GR_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[0, 0].errorbar(v12_F5_Z00_merged.r.values, v12_F5_Z00_merged.v12.values,
                      yerr=v12_F5_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[0, 0].errorbar(v12_F6_Z00_merged.r.values, v12_F6_Z00_merged.v12.values,
                      yerr=v12_F6_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[0, 0].fill_between(v12_GR_Z00_merged.r.values,
                          v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[0, 0].fill_between(v12_F5_Z00_merged.r.values,
                          v12_F5_Z00_merged.v12.values - v12_F5_Z00_merged.Errv12.values,
                          v12_F5_Z00_merged.v12.values + v12_F5_Z00_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[0, 0].fill_between(v12_F6_Z00_merged.r.values,
                          v12_F6_Z00_merged.v12.values - v12_F6_Z00_merged.Errv12.values,
                          v12_F6_Z00_merged.v12.values + v12_F6_Z00_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[0, 0].plot(r40, v12_hf_r40_z00, ls='-', lw=2, color=cmodel[0],
                  label=labelhf)
    ax[0, 0].plot(r40_hm, v12_F5_hm_r40_z00, ls=':', lw=lwhm, color=cmodel[1],
                  label=labelhm)  ##### gupta
    ax[0, 0].plot(r40_hm, v12_F6_hm_r40_z00, ls=':', lw=lwhm, color=cmodel[2],
                  )  ##### gupta

    ax[0, 0].plot(r40_MG, v12_F5_hf_r40_z00, ls='-', lw=lw1, color=cmodel[1])

    ax[0, 0].plot(r40_MG, v12_F6_hf_r40_z00, ls='-', lw=lw1, color=cmodel[2])

    ax[2, 0].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                      yerr=v12_GR_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[2, 0].errorbar(v12_F5_Z03_merged.r.values, v12_F5_Z03_merged.v12.values,
                      yerr=v12_F5_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[2, 0].errorbar(v12_F6_Z03_merged.r.values, v12_F6_Z03_merged.v12.values,
                      yerr=v12_F6_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[2, 0].fill_between(v12_GR_Z03_merged.r.values,
                          v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[2, 0].fill_between(v12_F5_Z03_merged.r.values,
                          v12_F5_Z03_merged.v12.values - v12_F5_Z03_merged.Errv12.values,
                          v12_F5_Z03_merged.v12.values + v12_F5_Z03_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[2, 0].fill_between(v12_F6_Z03_merged.r.values,
                          v12_F6_Z03_merged.v12.values - v12_F6_Z03_merged.Errv12.values,
                          v12_F6_Z03_merged.v12.values + v12_F6_Z03_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[2, 0].plot(r40, v12_hf_r40_z03, ls='-', lw=lw1, color=cmodel[0],
                  label=labelhf)
    ax[2, 0].plot(r40_hm, v12_F5_hm_r40_z03, ls=':', lw=lwhm, color=cmodel[1],
                  )  ##### gupta
    ax[2, 0].plot(r40_hm, v12_F6_hm_r40_z03, ls=':', lw=lwhm, color=cmodel[2]
                  )  ##### gupta
    ax[2, 0].plot(r40_MG, v12_F5_hf_r40_z03, ls='-', lw=lw1, color=cmodel[1])
    ax[2, 0].plot(r40_MG, v12_F6_hf_r40_z03, ls='-', lw=lw1, color=cmodel[2])

    ax[4, 0].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                      yerr=v12_GR_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[4, 0].errorbar(v12_F5_Z05_merged.r.values, v12_F5_Z05_merged.v12.values,
                      yerr=v12_F5_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[1],
                      label=str(models[1]))
    ax[4, 0].errorbar(v12_F6_Z05_merged.r.values, v12_F6_Z05_merged.v12.values,
                      yerr=v12_F6_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[2],
                      label=str(models[2]))

    ax[4, 0].fill_between(v12_GR_Z05_merged.r.values,
                          v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[4, 0].fill_between(v12_F5_Z05_merged.r.values,
                          v12_F5_Z05_merged.v12.values - v12_F5_Z05_merged.Errv12.values,
                          v12_F5_Z05_merged.v12.values + v12_F5_Z05_merged.Errv12.values,
                          color=cmodel[1], alpha=0.2)
    ax[4, 0].fill_between(v12_F6_Z05_merged.r.values,
                          v12_F6_Z05_merged.v12.values - v12_F6_Z05_merged.Errv12.values,
                          v12_F6_Z05_merged.v12.values + v12_F6_Z05_merged.Errv12.values,
                          color=cmodel[2], alpha=0.2)

    ax[4, 0].plot(r40, v12_hf_r40_z05, ls='-', lw=lw1, color=cmodel[0], label=labelhf)
    ax[4, 0].plot(r40_hm, v12_F5_hm_r40_z05, ls=':', lw=lwhm, color=cmodel[1])  ##### gupta
    ax[4, 0].plot(r40_hm, v12_F6_hm_r40_z05, ls=':', lw=lwhm, color=cmodel[2])  ##### gupta

    ax[4, 0].plot(r40_MG, v12_F5_hf_r40_z05, ls='-', lw=lw1, color=cmodel[1])
    ax[4, 0].plot(r40_MG, v12_F6_hf_r40_z05, ls='-', lw=lw1, color=cmodel[2])

    #     #### ---------------- ndgp ---------------

    ax[0, 1].errorbar(v12_GR_Z00_merged.r.values, v12_GR_Z00_merged.v12.values,
                      yerr=v12_GR_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[0, 1].errorbar(v12_N1_Z00_merged.r.values, v12_N1_Z00_merged.v12.values,
                      yerr=v12_N1_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[0, 1].errorbar(v12_N5_Z00_merged.r.values, v12_N5_Z00_merged.v12.values,
                      yerr=v12_N5_Z00_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[0, 1].fill_between(v12_GR_Z00_merged.r.values,
                          v12_GR_Z00_merged.v12.values - v12_GR_Z00_merged.Errv12.values,
                          v12_GR_Z00_merged.v12.values + v12_GR_Z00_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[0, 1].fill_between(v12_N1_Z00_merged.r.values,
                          v12_N1_Z00_merged.v12.values - v12_N1_Z00_merged.Errv12.values,
                          v12_N1_Z00_merged.v12.values + v12_N1_Z00_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[0, 1].fill_between(v12_N5_Z00_merged.r.values,
                          v12_N5_Z00_merged.v12.values - v12_N5_Z00_merged.Errv12.values,
                          v12_N5_Z00_merged.v12.values + v12_N5_Z00_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[0, 1].plot(r40, v12_hf_r40_z00, ls='-', lw=lw1, color=cmodel[0],
                  label=labelhf)
    ax[0, 1].plot(r40_hm, v12_N1_hm_r40_z00, ls=':', lw=lwhm, color=cmodel[3],
                  label=labelhm)  ##### gupta
    ax[0, 1].plot(r40_hm, v12_N5_hm_r40_z00, ls=':', lw=lwhm, color=cmodel[4]
                  )  ##### gupta

    ax[0, 1].plot(r40_MG, v12_N1_hf_r40_z00, ls='-', lw=lw1, color=cmodel[3])
    ax[0, 1].plot(r40_MG, v12_N5_hf_r40_z00, ls='-', lw=lw1, color=cmodel[4])

    ax[2, 1].errorbar(v12_GR_Z03_merged.r.values, v12_GR_Z03_merged.v12.values,
                      yerr=v12_GR_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[2, 1].errorbar(v12_N1_Z03_merged.r.values, v12_N1_Z03_merged.v12.values,
                      yerr=v12_N1_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[2, 1].errorbar(v12_N5_Z03_merged.r.values, v12_N5_Z03_merged.v12.values,
                      yerr=v12_N5_Z03_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[2, 1].fill_between(v12_GR_Z03_merged.r.values,
                          v12_GR_Z03_merged.v12.values - v12_GR_Z03_merged.Errv12.values,
                          v12_GR_Z03_merged.v12.values + v12_GR_Z03_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[2, 1].fill_between(v12_N1_Z03_merged.r.values,
                          v12_N1_Z03_merged.v12.values - v12_N1_Z03_merged.Errv12.values,
                          v12_N1_Z03_merged.v12.values + v12_N1_Z03_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[2, 1].fill_between(v12_N5_Z03_merged.r.values,
                          v12_N5_Z03_merged.v12.values - v12_N5_Z03_merged.Errv12.values,
                          v12_N5_Z03_merged.v12.values + v12_N5_Z03_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[2, 1].plot(r40, v12_hf_r40_z03, ls='-', lw=lw1, color=cmodel[0],
                  label=labelhf)
    ax[2, 1].plot(r40_MG, v12_N1_hf_r40_z03, ls='-', lw=lw1, color=cmodel[3])
    ax[2, 1].plot(r40_MG, v12_N5_hf_r40_z03, ls='-', lw=lw1, color=cmodel[4])

    ## ax[2,1].yaxis.set_major_formatter(FancyFormatter())

    ax[4, 1].errorbar(v12_GR_Z05_merged.r.values, v12_GR_Z05_merged.v12.values,
                      yerr=v12_GR_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[0],
                      label=str(models[0]))
    ax[4, 1].errorbar(v12_N1_Z05_merged.r.values, v12_N1_Z05_merged.v12.values,
                      yerr=v12_N1_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[3],
                      label=str(models[3]))
    ax[4, 1].errorbar(v12_N5_Z05_merged.r.values, v12_N5_Z05_merged.v12.values,
                      yerr=v12_N5_Z05_merged.Errv12.values,
                      markeredgewidth=1, marker='.', capsize=csize, ms=msize, elinewidth=3,
                      ls='none', color=cmodel[4],
                      label=str(models[4]))

    ax[4, 1].fill_between(v12_GR_Z05_merged.r.values,
                          v12_GR_Z05_merged.v12.values - v12_GR_Z05_merged.Errv12.values,
                          v12_GR_Z05_merged.v12.values + v12_GR_Z05_merged.Errv12.values,
                          color=cmodel[0], alpha=0.2)
    ax[4, 1].fill_between(v12_N1_Z05_merged.r.values,
                          v12_N1_Z05_merged.v12.values - v12_N1_Z05_merged.Errv12.values,
                          v12_N1_Z05_merged.v12.values + v12_N1_Z05_merged.Errv12.values,
                          color=cmodel[3], alpha=0.2)
    ax[4, 1].fill_between(v12_N5_Z05_merged.r.values,
                          v12_N5_Z05_merged.v12.values - v12_N5_Z05_merged.Errv12.values,
                          v12_N5_Z05_merged.v12.values + v12_N5_Z05_merged.Errv12.values,
                          color=cmodel[4], alpha=0.2)

    ax[4, 1].plot(r40, v12_hf_r40_z05, ls='-', lw=lw1, color=cmodel[0],
                  label=labelhf)
    ax[4, 1].plot(r40_MG, v12_N1_hf_r40_z05, ls='-', lw=lw1, color=cmodel[3])
    ax[4, 1].plot(r40_MG, v12_N5_hf_r40_z05, ls='-', lw=lw1, color=cmodel[4])

    #     #### =========== ratios =============
    #     # #################  RATIOS  with new errors from Hellwing  #################

    ax[1, 0].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z00 / v12_F5_Z00_merged.v12.values) * 100,
                  ls='-', lw=lw1, color=cmodel[1])
    ax[1, 0].plot(r40_hm,
                  (1 - v12_F5_hm_r40_z00 / v12_F5_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[1])  ## Gupta
    ax[1, 0].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z00 / v12_F6_Z00_merged.v12.values) * 100,
                  ls='-', lw=lw1, color=cmodel[2])

    ax[1, 0].plot(r40_hm,
                  (1 - v12_F6_hm_r40_z00 / v12_F6_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[2])  ## Gupta

    ax[1, 0].fill_between(v12_F5_Z00_merged.r.values,
                          -v12_F5_Z00_merged.Errv12.values,
                          v12_F5_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[1, 0].fill_between(v12_F6_Z00_merged.r.values,
                          -v12_F6_Z00_merged.Errv12.values,
                          v12_F6_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[3, 0].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z03 / v12_F5_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[1])
    ax[3, 0].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z03 / v12_F6_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[2])

    ax[3, 0].plot(r40_hm,
                  (1 - v12_F5_hm_r40_z03 / v12_F5_Z03_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[1])  ## Gupta
    ax[3, 0].plot(r40_hm,
                  (1 - v12_F6_hm_r40_z03 / v12_F6_Z03_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[2])  ## Gupta

    ax[3, 0].fill_between(v12_F5_Z03_merged.r.values,
                          -v12_F5_Z03_merged.Errv12.values,
                          v12_F5_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[3, 0].fill_between(v12_F6_Z03_merged.r.values,
                          -v12_F6_Z03_merged.Errv12.values,
                          v12_F6_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[5, 0].plot(r40_MG,
                  (1 - v12_F5_hf_r40_z05 / v12_F5_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[1])
    ax[5, 0].plot(r40_MG,
                  (1 - v12_F6_hf_r40_z05 / v12_F6_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[2])

    ax[5, 0].plot(r40_hm,
                  (1 - v12_F5_hm_r40_z05 / v12_F5_Z05_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[1])  ## Gupta
    ax[5, 0].plot(r40_hm,
                  (1 - v12_F6_hm_r40_z05 / v12_F6_Z05_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[2])  ## Gupta

    ax[5, 0].fill_between(v12_F5_Z05_merged.r.values,
                          -v12_F5_Z05_merged.Errv12.values,
                          v12_F5_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[1])
    ax[5, 0].fill_between(v12_F6_Z05_merged.r.values,
                          -v12_F6_Z05_merged.Errv12.values,
                          v12_F6_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[2])

    ax[1, 1].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z00 / v12_N1_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[1, 1].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z00 / v12_N5_Z00_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])

    ax[1, 1].plot(r40_hm,
                  (1 - v12_N1_hm_r40_z00 / v12_N1_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[3])  ## Gupta
    ax[1, 1].plot(r40_hm,
                  (1 - v12_N5_hm_r40_z00 / v12_N5_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[4])  ## Gupta

    ax[1, 1].fill_between(v12_N1_Z00_merged.r.values,
                          -v12_N1_Z00_merged.Errv12.values,
                          v12_N1_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[1, 1].fill_between(v12_N5_Z00_merged.r.values,
                          -v12_N5_Z00_merged.Errv12.values,
                          v12_N5_Z00_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    ax[3, 1].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z03 / v12_N1_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[3, 1].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z03 / v12_N5_Z03_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])
    ax[3, 1].plot(r40_hm,
                  (1 - v12_N1_hm_r40_z00 / v12_N1_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[3])  ## Gupta
    ax[3, 1].plot(r40_hm,
                  (1 - v12_N5_hm_r40_z00 / v12_N5_Z00_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[4])  ## Gupta

    ax[3, 1].fill_between(v12_N1_Z03_merged.r.values,
                          -v12_N1_Z03_merged.Errv12.values,
                          v12_N1_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[3, 1].fill_between(v12_N5_Z03_merged.r.values,
                          -v12_N5_Z03_merged.Errv12.values,
                          v12_N5_Z03_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    ax[5, 1].plot(r40_MG,
                  (1 - v12_N1_hf_r40_z05 / v12_N1_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[3])
    ax[5, 1].plot(r40_MG,
                  (1 - v12_N5_hf_r40_z05 / v12_N5_Z05_merged.v12.values) * 100,
                  ls='-', lw=2, color=cmodel[4])
    ax[5, 1].plot(r40_hm,
                  (1 - v12_N1_hm_r40_z05 / v12_N1_Z05_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[3])  ## Gupta
    ax[5, 1].plot(r40_hm,
                  (1 - v12_N5_hm_r40_z05 / v12_N5_Z05_merged.v12.values) * 100,
                  ls=':', lw=lwhm, color=cmodel[4])  ## Gupta

    ax[5, 1].fill_between(v12_N1_Z05_merged.r.values,
                          -v12_N1_Z05_merged.Errv12.values,
                          v12_N1_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[3])
    ax[5, 1].fill_between(v12_N5_Z05_merged.r.values,
                          -v12_N5_Z05_merged.Errv12.values,
                          v12_N5_Z05_merged.Errv12.values,
                          alpha=0.2, color=cmodel[4])

    ax[0, 0].text(xtext, ytext, r'$z=0.0$', fontsize=fs_text)
    ax[2, 0].text(xtext, ytext, r'$z=0.3$', fontsize=fs_text)
    ax[4, 0].text(xtext, ytext, r'$z=0.5$', fontsize=fs_text)

    #     #### =========== ====== =============
    #     #### legends
    ax[0, 0].legend(ncol=3, loc='upper center', bbox_to_anchor=(0.35, 1.4), fontsize=42)
    ax[0, 1].legend(ncol=3, loc='upper center', bbox_to_anchor=(0.50, 1.4), fontsize=42)

    # print('---- Figure 2 done -----')
    # ----------------- Saving  ---------------------

    # plt.savefig(full_fig_name, bbox_inches='tight', dpi=dpi)


### Executing figure 1 ####
# figure_1(fig_name='fig1_script', save_figure=True)

### Executing figure 2 ####
figure_2(fig_name='fig2_ed', save_figure=True)

## executing figure 3 ####
# which_z = 0.5
# filename = 'fig3_CHANGED_z_' + str(which_z)
# figure_3(fig_name=filename, save_figure=True, which_snapshot=which_z)

# snapshot_labels = [0.5, 0.3, 0]
# for z in range(len(snapshots)):
#     which_z = snapshots[z]
#     filename = 'fig3_CHANGED_z_' + str(which_z)
#     figure_3(fig_name=filename, save_figure=True, which_snapshot=which_z)


# figure_stable_clustering(fig_name='Fig_stableclustering_HF_label_cut', save_figure=True, sufix='_HF')
