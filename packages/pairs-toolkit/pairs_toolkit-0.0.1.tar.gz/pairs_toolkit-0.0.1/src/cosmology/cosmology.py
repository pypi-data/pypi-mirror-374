# =============================================================================#
# coding: utf-8
# Jorge Garcia-Farieta & Mariana Jaber: 2022
# Description:
# =============================================================================#
import numpy as np
from .constants import *

# TODO: Rewrite the functions as 
# def my_function(a, b, *args, **kwargs):
#    pass
#
# For instance: some_cosmology_function(z, *cosmoargs,**others)

class Cosmology:
    # The first method is the initialiser 

    def __init__(self, 
                 h, Om0,Ob0, sigma80, ns, As, Obh2, Ocdm0h2, model):
        self.h = h,
        self.Om0 = Om0,
        self.Ob0 = Ob0,
        self.sigma80 = sigma80,
        self.ns = ns,
        self.As = As,
        self.Obh2 = Obh2,
        self.Ocdm0h2 = Ocdm0h2,
        self.model = model
    
    # The second method reads the input parameters and creates a dictionary to store the cosmology used 
        
    def define_cosmology(self): 
        Ocdm0 = np.round(self.Om0 - self.Ob0, 6)
        if self.Ob0h2==None:
            self.Ob0h2 = np.round(self.Ob0*self.h**2, 6)
        if self.Ocdm0h2==None:
            self.Ocdm0h2 = np.round(self.Ocdm0*self.h**2, 6)
        cosmodict = {'h': self.h,
                 'Om0': self.Om0,
                 'Ob0': self.Ob0,
                 'Ocdm0': np.round(self.Om0 - self.Ob0, 6),
                 'sigma80': self.sigma80,
                 'ns': self.ns,
                 'As': self.As,
                 'Ob0h2': self.Ob0h2,
                 'Ocdm0h2': self.Ocdm0h2,
                 'model': self.model
                 }
        return cosmodict
    
 
# TODO: inherit the class Cosmology attributes to the rest of the functions 
    
# BUG: As does not overule sigma8 and visceversa 
    ## Should we move As_from_sigma8() function from 
    ## core_functions.py to this module?
    ## new_As = old_As * (true_sigma8_z0 / sigma8_z0) ** 2

def define_cosmology(h=REDUCED_H0, Om0=OMEGA_M0, Ob0=OMEGA_B0, sigma80=SIGMA80,
                     ns=NS, As=AS, Ob0h2=None, Ocdm0h2=None, model="GR"):
    Ocdm0 = np.round(Om0 - Ob0, 6)
    if Ob0h2==None:
        Ob0h2 = np.round(Ob0*h**2, 6)
    if Ocdm0h2==None:
        Ocdm0h2 = np.round(Ocdm0*h**2, 6)

    cosmodict = {'h': h,
                 'Om0': Om0,
                 'Ob0': Ob0,
                 'Ocdm0': np.round(Om0 - Ob0, 6),
                 'sigma80': sigma80,
                 'ns': ns,
                 'As': As,
                 'Ob0h2': Ob0h2,
                 'Ocdm0h2': Ocdm0h2,
                 'model': model
                 }
    return cosmodict


def hubble_flat(z, dict_cosmology):
    """
    Hubble-function in terms of OmegaMatter
    for  a flat universe
    :param dict_cosmology: dictionary
    :param z: float
    :return: Hubble function at given redshift
    """
    h, OmegaM = dict_cosmology['h'], dict_cosmology['Om0']
    hubble_func = 100 * h * np.sqrt(
        OMEGAR0 * (1 + z) ** 4 + OmegaM * (1 + z) ** 3 +
        (1 - OMEGAR0 - OmegaM))

    return hubble_func


def E_z_flat(z, dict_cosmology):
    """
    Reduced hubble function E(z)=H(z)/H0
    :param z:
    :param dict_cosmology:
    :return: Reduced hubble E(z)
    """
    h, OmegaM = dict_cosmology['h'], dict_cosmology['Om0']
    Hz = hubble_flat(z, dict_cosmology)
    H0 = 100 * h

    return Hz / H0


# ##### ---------------   Density for DM  -----------------------#####

def rhomz(z, dict_cosmology):
    """
    Volumentric energy density of the dark matter fluid component
    """
    h, OmegaM = dict_cosmology['h'], dict_cosmology['Om0']
    rhom0 = OmegaM * RHOCR0
    rho_m_z = rhom0 * (1 + z) * 3

    return rho_m_z


def OmegaM_z(z, dict_cosmology):
    """
    OmegaM as function of redshift for a flat LCDM universe
    :param z: float
    :param dict_cosmology:
    :return:
    """
    h, OmegaM = dict_cosmology['h'], dict_cosmology['Om0']
    E_z_2 = E_z_flat(z, dict_cosmology) * E_z_flat(z, dict_cosmology)
    omz = OmegaM * (1 + z) ** 3 / E_z_2

    return omz


def f_lin(z, dict_cosmology):
    """
    Linear growth factor, dlnD/dlna, where D is the growth function
    Approximated as Omegam^gamma with gamma = 6/11 (valid only for LCDM!)
    :param z:
    :param dict_cosmo:
    :return: f(z)
    """
    growth_idx = 6. / 11.
    gl = growth_idx

    OmMz = OmegaM_z(z, dict_cosmology)
    flin = OmMz ** gl

    return flin
