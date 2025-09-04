# =============================================================================#
# coding: utf-8
# Jorge Garcia-Farieta & Mariana Jaber: 2022
# Description:
# =============================================================================#

import pandas as pd
from ..cosmology.a_to_z import redshift_from_scalefactor
import numpy as np
import os
from pathlib import Path

PATH = Path(os.path.abspath(os.path.dirname(__file__)))

LEGACY_DATA_PATH = str(PATH / "../../legacy_data")

def read_sims_DM_ELEPHANT_all_z(inputdir=LEGACY_DATA_PATH + "/output_rmax_42/", modelname="GR"):
    '''
    Parameters
    ----------
    inputdir : string
    modelname: string

    Returns
    -------
    v12dataDM, xidataDM
    '''

    # Reading v12 obtained from simulations
    v12data1 = pd.read_csv(inputdir + modelname + "_z0.0/v12Avg.dat", sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])
    v12data2 = pd.read_csv(inputdir + modelname + "_z0.3/v12Avg.dat", sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])
    v12data3 = pd.read_csv(inputdir + modelname + "_z0.5/v12Avg.dat", sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    v12dataDM = {
        "z0.0": v12data1,
        "z0.3": v12data2,
        "z0.5": v12data3
    }

    # Reading 2PCF obtained from simulations
    xidata1 = pd.read_csv(inputdir + modelname + "_z0.0/xiAvg.dat", sep='\s+', comment='#',
                          names=["r", "xi", "Errxi"])
    xidata2 = pd.read_csv(inputdir + modelname + "_z0.3/xiAvg.dat", sep='\s+', comment='#',
                          names=["r", "xi", "Errxi"])
    xidata3 = pd.read_csv(inputdir + modelname + "_z0.5/xiAvg.dat", sep='\s+', comment='#',
                          names=["r", "xi", "Errxi"])

    xidataDM = {
        "z0.0": xidata1,
        "z0.3": xidata2,
        "z0.5": xidata3
    }

    return v12dataDM, xidataDM

def read_clpt(inputdir="/home/jaber/shared/data/CLPT_outputs/", rmax=40):
    '''
    Read the results from CLPT runs
    Remember to add units according to CLPT documentation:
        Veloicties are given in units of $v/(a H(a) f_v)$
        (this gives the results a dimension of distance),
        where a is the scale factor, $H(a)$ is the Hubble parameter and $f_v$ is the growth factor.

    Parameters
    ----------
    inputdir: global directory for CLPT data
    rmax: 40, or 140

    Returns
    -------
    v12CLPT, xiCLPT
    '''

    #
    if rmax == 40:
        add_path = 'rmax40/'
    else:
        add_path = 'rmax140/'

    dir = inputdir + add_path

    v12CLPT1 = pd.read_csv(dir + "v12_z0p0.txt", sep='\s+', comment='#', usecols=[0, 1, 2],
                           names=["r", "v12L", "v12"])
    v12CLPT2 = pd.read_csv(dir + "v12_z0p3.txt", sep='\s+', comment='#', usecols=[0, 1, 2],
                           names=["r", "v12L", "v12"])
    v12CLPT3 = pd.read_csv(dir + "v12_z0p5.txt", sep='\s+', comment='#', usecols=[0, 1, 2],
                           names=["r", "v12L", "v12"])

    v12CLPT = {
        "z0.0": v12CLPT1,
        "z0.3": v12CLPT2,
        "z0.5": v12CLPT3
    }

    xiCLPT1 = pd.read_csv(dir + "xi_z0p0.txt", sep='\s+', comment='#', usecols=[0, 1, 2], names=["r", "xiL", "xi"])
    xiCLPT2 = pd.read_csv(dir + "xi_z0p3.txt", sep='\s+', comment='#', usecols=[0, 1, 2], names=["r", "xiL", "xi"])
    xiCLPT3 = pd.read_csv(dir + "xi_z0p5.txt", sep='\s+', comment='#', usecols=[0, 1, 2], names=["r", "xiL", "xi"])

    xiCLPT = {
        "z0.0": xiCLPT1,
        "z0.3": xiCLPT2,
        "z0.5": xiCLPT3
    }

    return v12CLPT, xiCLPT

def bias_data():
    biasdata = pd.DataFrame({
        "Redshift": ["z0.0", "z0.3", "z0.5"],
        "DM": [1.0, 1.0, 1.0],
        "Haloes": [1.50, 1.75, 1.92],
        "Galaxies": [1.59, 1.80, 1.94]})
    biasdata.set_index('Redshift', inplace=True)

    return biasdata

    print(r"The bias for halos at z=0 is b=", biasdata.loc['z0.0', "Haloes"])

# read data millenium

def read_data_millenium(inputdir="/home/jaber/shared/data/"):
    # Reading v12 obtained from ELEPHANT simulations
    v12data1 = pd.read_csv(inputdir + "v12-millenium_dm_data_LCDM2160/LCDM2160_snap00162_f002_velo.f0.1_vstat_obs",
                           sep='\s+', comment='#',
                           names=["r", "rmin", "rmax", "v12", "S12", "VO", "SO", "S3V12", "S3VO", "S4V12", "S4VO",
                                  "xi"], usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    v12data2 = pd.read_csv(inputdir + "v12-millenium_dm_data_LCDM2160/LCDM2160_snap00145_f002_velo.f0.1_vstat_obs",
                           sep='\s+', comment='#',
                           names=["r", "rmin", "rmax", "v12", "S12", "VO", "SO", "S3V12", "S3VO", "S4V12", "S4VO",
                                  "xi"], usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    v12data3 = pd.read_csv(inputdir + "v12-millenium_dm_data_LCDM2160/LCDM2160_snap00133_f002_velo.f0.1_vstat_obs",
                           sep='\s+', comment='#',
                           names=["r", "rmin", "rmax", "v12", "S12", "VO", "SO", "S3V12", "S3VO", "S4V12", "S4VO",
                                  "xi"], usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    v12data4 = pd.read_csv(inputdir + "v12-millenium_dm_data_LCDM2160/LCDM2160_snap00116_f002_velo.f0.1_vstat_obs",
                           sep='\s+', comment='#',
                           names=["r", "rmin", "rmax", "v12", "S12", "VO", "SO", "S3V12", "S3VO", "S4V12", "S4VO",
                                  "xi"], usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    v12dataDM = {
        "z0.0": v12data1[["r", "v12"]],
        "z0.5": v12data2[["r", "v12"]],
        "z1.0": v12data3[["r", "v12"]],
        "z2.0": v12data4[["r", "v12"]]
    }

    # Reading 2PCF obtained from ELEPHANT simulations
    xidataDM = {
        "z0.0": v12data1[["r", "xi"]],
        "z0.5": v12data2[["r", "xi"]],
        "z1.0": v12data3[["r", "xi"]],
        "z2.0": v12data4[["r", "xi"]]
    }

    return v12dataDM, xidataDM

def read_snapshot_DUDEG_pk(inputdir="/opt/cosmo_data/sims/DUDEG_LCDM_1400/", save_file=False):
    '''
    Use the power spectrum files for DUDEG simulations, available at /opt/cosmo_data/sims/DUDEG_LCDM_1400/ to infer the snapshots scale factors
    '''

    a_values_list = []
    z_values_list = []

    for i in np.arange(100, 163):
        file_pk = inputdir + 'powerspec_' + str(i) + '.txt'

        pk_df = pd.read_csv(file_pk, sep='\s+', usecols=[0],
                            names=['foo']
                            )

        aval = pk_df.foo[0]
        zval = redshift_from_scalefactor(aval)

        a_values_list.append(aval)
        z_values_list.append(zval)

    a_values = np.array(a_values_list)
    z_values = np.array(z_values_list)

    fname_a = 'scale_factors_DUDEG_snapshots_100_162.txt'
    fname_z = 'redshifts_DUDEG_snapshots_100_162.txt'

    shared_path = '/home/jaber/shared/data/'  ### TO-DO change to use the same inputdir

    file_a = shared_path + fname_a
    file_z = shared_path + fname_z
    if save_file:
        np.savetxt(file_a, a_values)
        np.savetxt(file_z, z_values)

        print('----- a values saved in: ', file_a)
        print('----- z values saved in: ', file_z)

    return a_values, z_values

def cfs_pks_DUDEG(inputpath='/opt/cosmo_data/sims/DUDEG_LCDM_1400/'):
    xi_list = []
    pk_list = []

    for i in np.arange(100, 163):
        # Read correl functions
        base_filename_cf = 'correl_'
        file_cf = inputpath + base_filename_cf + str(i) + '.txt'
        cf = np.loadtxt(file_cf, skiprows=2)  # numpy > pandas

        xi_list.append(cf[:, 1])

        # Read power spectrum
        base_filename_pk = 'powerspec_'
        file_pk = inputpath + base_filename_pk + str(i) + '.txt'
        pk_df = pd.read_csv(file_pk, sep='\s+', usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                            names=['k', 'delta', 'shotlim', 'Pk', 'cmodes', 'Delta_noncorr', 'Pk_noncorr',
                                   'P_Efstathiou', 'SumP', 'lv'],
                            skiprows=4)
        l_box_cubed = 10**9
        # factor_lvPk = (2 * np.pi) ** 3 * 4 * np.pi * (pk_df.k) ** 3 / pk_df.lv
        # pk_val = pk_df.Pk * factor_lvPk
        pk_val = pk_df.Pk * l_box_cubed
        pk_list.append(pk_val)

    # ## After the loop, convert the lists to arrays

    xi_array = np.array(xi_list)
    pk_array = np.array(pk_list)

    # Because the k_vals and r_vals are the same for all files, we retrieve them now after the loop ended
    r_array = cf[:, 0]
    k_array = np.array(pk_df.k)

    r, xi, k, pk = r_array, xi_array, k_array, pk_array
    return r, xi, k, pk
