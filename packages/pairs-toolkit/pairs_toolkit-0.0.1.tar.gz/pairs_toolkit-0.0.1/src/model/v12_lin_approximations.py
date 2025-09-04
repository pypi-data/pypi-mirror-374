# =============================================================================#
# coding: utf-8
# Mariana Jaber & Jorge Garcia-Farieta: 2022
# Description:
# =============================================================================#
import numpy as np
from .a_to_z import *
from ..model.core_functions import xis_from_pk
from .cosmology import *


def v12_approx(cosmo_args, z_array, r_array,r_args=[0.1, 40, 50],
               use_r_array=True,
               use_z_array=False, z_args=[0, 2, 0.1],
               redshift_simulation=[0, 0.3, 0.5, 1],
               which_simulation_redshift=0.0,
               CAMB_path="/opt/cosmo_data/",
               CAMB_outputdir_Pk="/home/jaber/shared/data/output_Pk_camb/",
               MG=False, model='00', rcH0=1.000, F_R0=0.00001):
    """
    Approximated solution for pairwise velocities without numerical
    derivative:
    [Peebles LSS, , eqn: 71.12 and Juszkiewicz et al 1999, eqn: 8c]
    v12(r,a) = -2/3 H * a * r * f * xibb(r)
    where f = d ln D+ / dln a ~ Om^gamma, gamma = 6/11 for LCDM
    and xi(r) is the double bar linear two-point correlation function.
    ------
    Parameters
    ------
    :param cosmo_args: (which_cosmology, bias, do_Pknonlinear)
            which_cosmology = dictionary define using cosmology.py
            bias: float
                linear bias 1.0
            do_Pknonlinear: boolean
    :param r_args: tuple of floats
            [r_min, r_max, r_size]
    :param z_args: tuple of floats
            [z_in, z_end, z_size]
    :param redshift_simulation: tuple of floats
    :param which_simulation_redshift: choosen redshift snapshot from simulation
    :return: r,  v12_QuasiLin
    """
    '''
        Return the pairwise velocity at given distances in the quasi-linear regime.
        v12_QuasiLin = -2/3 * a * r * H(a) * flin * xibarbar
        f = d ln D+ / dln a ~ Om^gamma, gamma = 6/11 for LCDM
    '''



    r, a, z, xibbar_array, xibbar_array, xibbar_array = xis_from_pk(cosmo_args, z_array,
                                                                    r_array, r_args,
                                                                    use_r_array, use_z_array, z_args,
                                                                    redshift_simulation,
                                                                    CAMB_path,
                                                                    CAMB_outputdir_Pk,
                                                                    MG, model, rcH0, F_R0)

    which_cosmology, bias, do_Pknonlinear = cosmo_args

    idx_which_a = ID_snapshot_selector(z, which_simulation_redshift)

    Hofz = hubble_flat(z=which_simulation_redshift, dict_cosmology=which_cosmology)
    flin = f_lin(z=which_simulation_redshift, dict_cosmology=which_cosmology)
    xibb=xibbar_array[idx_which_a, :]

    v12_QuasiLin = -2/3 * a[idx_which_a]**2 * r * Hofz * flin * xibb

    return r, v12_QuasiLin


def CLPT_v12_units_factor(z, cosmodict):
    """
    Conversion factor to get velocity units [km/s] from CLPT output.
    :param z: redshift (float)
    :param cosmodict: dictionary that contains cosmologycal parameters
    """
    '''
        Return the conversion factor for CLPT (float)
        factor = a * H(a) * f(a)
    '''
    CLPTunits = scalefactor_from_redshift(z)*hubble_flat(z, cosmodict)*f_lin(z, cosmodict)
    return CLPTunits
