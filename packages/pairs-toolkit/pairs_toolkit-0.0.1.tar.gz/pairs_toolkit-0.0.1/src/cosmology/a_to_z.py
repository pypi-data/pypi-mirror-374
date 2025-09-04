# =============================================================================#
# coding: utf-8
# Jorge Garcia-Farieta & Mariana Jaber: 2022
# Description: 
# =============================================================================#
import numpy as np

def scalefactor_from_redshift(redshifts):
    '''
    returns the scale factor given the redshift
    '''
    scalefactor = 1 / (1 + redshifts)
    return scalefactor


def redshift_from_scalefactor(scalefactor):
    '''
    returns the redshift given the scalefactor
    '''
    redshift = 1 / scalefactor - 1
    return redshift


def ID_snapshot_selector(redshift, which_simulation_redshift):
    mask = np.where(redshift == which_simulation_redshift)
    index = mask[0][0]
    return index