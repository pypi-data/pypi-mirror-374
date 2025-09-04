# =============================================================================#
# coding: utf-8
# Mariana Jaber & Jorge Garcia-Farieta: 2022
# Description: Calculates the
# 2PCF from analytical P(k)  using a CLASS transfer function
# and implements the numerical derivative of xi(r,a) wrt to scale factor:
# partial xi(r,a)/partial(a)
# =============================================================================#

import os
from pathlib import Path

from ..cosmology.a_to_z import *
from .integrate_xi import *

from scipy.integrate import simpson
from scipy.interpolate import interp1d
from scipy.special import spherical_jn

PATH = Path(os.path.abspath(os.path.dirname(__file__)))
CAMB_DATA_PATH = str(PATH / "../../resources") + "/"
user_CAMB_outputdir_Pk = str(PATH / "../../../data_camb/output_Pk_camb") + "/"

def xis_from_pk(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                use_r_array = True,
                use_z_array = False, z_args=[0, 2, 0.1],
                redshift_simulation=[0, 0.3, 0.5, 1],
                CAMB_path=CAMB_DATA_PATH,
                CAMB_outputdir_Pk=user_CAMB_outputdir_Pk,
                MG=False, model='00', rcH0=1.000, F_R0=0.00001):
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

    :param CAMB_OUTPUTDIR_Pk:
    :param MG: boolean
    :param model: int from 0-6, choice of MG model to use
    :param rcH0: int nDGP
    :param F_R0: int Hu-Sawicki f(R)

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


    # ------- Empty lists to save our results
    corr_func_list = []
    barcorr_func_list = []
    bbarcorr_func_list = []

    # ------- Create the power spectra for each redshift value
    CAMB_dir   = CAMB_path + 'CAMB/'
    MGCAMB_dir = CAMB_path + 'MGCAMB/'

    CAMB_outputdir_Pk = CAMB_outputdir_Pk + which_cosmology['model']+"_h"+str(which_cosmology['h'])+"_Ob"+str(which_cosmology['Ob0'])+"_Ocdm"+str(which_cosmology['Ocdm0'])+"_ns"+str(which_cosmology['ns'])+"_As"+str(which_cosmology['As'])+"_Ob0h2"+str(which_cosmology['Ob0h2'])+"_Ocdm0h2"+str(which_cosmology['Ocdm0h2'])+"/"
    os.makedirs(CAMB_outputdir_Pk, exist_ok=True)
    os.system("chmod -f 777 " + CAMB_outputdir_Pk)

    if (do_Pknonlinear==False and MG==False):  # --> It means to use CAMB with linear Pk.
        os.system("rm -f " + CAMB_outputdir_Pk + "*")
        CAMB_parameterfile = CAMB_dir + "inifiles/PkLIN_" + which_cosmology['model']+"_h"+str(which_cosmology['h'])+"_Ob"+str(which_cosmology['Ob0'])+"_Ocdm"+str(which_cosmology['Ocdm0'])+"_ns"+str(which_cosmology['ns'])+"_As"+str(which_cosmology['As'])+"_Ob0h2"+str(which_cosmology['Ob0h2'])+"_Ocdm0h2"+str(which_cosmology['Ocdm0h2'])+".ini"
        write_camb_parameterfile(hh=which_cosmology['h'], Ob0=which_cosmology['Ob0'], Ocdm0=which_cosmology['Ocdm0'],
                                 ns=which_cosmology['ns'], As=which_cosmology['As'], redshifts=redshifts,
                                 Ob0h2=which_cosmology['Ob0h2'], Ocdm0h2=which_cosmology['Ocdm0h2'],
                                 filename=CAMB_parameterfile,
                                 output_path=CAMB_outputdir_Pk, TypePk=0,
                                 Nthreads=0, kmax=100)
        exec_camb(path_to_camb=CAMB_dir + "fortran/",
                  param_file=CAMB_parameterfile, execute=1)

        for zi in redshifts:
            kk, Plini = np.genfromtxt(
                CAMB_outputdir_Pk + "LINEARmatterpower_z" + "%0.3f" % zi + ".dat",
                unpack=True)
            Xi_lin = pk2xi(r_Mpch_log, kk, Plini, kmin=None, kmax=None,
                           kfactor=100, kbinsmax=100000,
                           Rg=None)
            xi_bar_lin = xi_bar(r_Mpch_log, r_Mpch_log, Xi_lin)
            xi_bbar_lin = xi_bar_lin / (1 + Xi_lin)
            corr_func_list.append(Xi_lin)
            barcorr_func_list.append(xi_bar_lin)
            bbarcorr_func_list.append(xi_bbar_lin)

    elif (do_Pknonlinear==True and MG==False):  # --> It means to use CAMB with NO linear Pk (halofit).
        os.system("rm -f " + CAMB_outputdir_Pk + "*")
        CAMB_parameterfile = CAMB_dir + "inifiles/PkNOLIN_" + which_cosmology['model']+"_h"+str(which_cosmology['h'])+"_Ob"+str(which_cosmology['Ob0'])+"_Ocdm"+str(which_cosmology['Ocdm0'])+"_ns"+str(which_cosmology['ns'])+"_As"+str(which_cosmology['As'])+"_Ob0h2"+str(which_cosmology['Ob0h2'])+"_Ocdm0h2"+str(which_cosmology['Ocdm0h2'])+".ini"
        write_camb_parameterfile(hh=which_cosmology['h'], Ob0=which_cosmology['Ob0'], Ocdm0=which_cosmology['Ocdm0'],
                                 ns=which_cosmology['ns'], As=which_cosmology['As'], redshifts=redshifts,
                                 Ob0h2=which_cosmology['Ob0h2'], Ocdm0h2=which_cosmology['Ocdm0h2'],
                                 filename=CAMB_parameterfile,
                                 output_path=CAMB_outputdir_Pk, TypePk=1,
                                 Nthreads=0, kmax=100)
        exec_camb(path_to_camb=CAMB_dir + "fortran/",
                  param_file=CAMB_parameterfile, execute=1)

        for zi in redshifts:
            kk, Pnonlin = np.genfromtxt(
                CAMB_outputdir_Pk + "NOLINEARmatterpower_z" + "%0.3f" % zi + ".dat",
                unpack=True)
            Xi_hf = pk2xi(r_Mpch_log, kk, Pnonlin, kmin=None, kmax=None,
                          kfactor=100, kbinsmax=100000,
                          Rg=None)
            xi_bar_hf = xi_bar(r_Mpch_log, r_Mpch_log, Xi_hf)
            xi_bbar_hf = xi_bar_hf / (1 + Xi_hf)
            corr_func_list.append(Xi_hf)
            barcorr_func_list.append(xi_bar_hf)
            bbarcorr_func_list.append(xi_bbar_hf)

    elif (do_Pknonlinear==False and MG==True):  # --> It means to use MGCAMB with linear Pk.
        os.system("rm -f " + CAMB_outputdir_Pk + "*")
        CAMB_parameterfile = MGCAMB_dir + "ini_files/PkLIN_" + which_cosmology['model']+"_h"+str(which_cosmology['h'])+"_Ob"+str(which_cosmology['Ob0'])+"_Ocdm"+str(which_cosmology['Ocdm0'])+"_ns"+str(which_cosmology['ns'])+"_As"+str(which_cosmology['As'])+"_Ob0h2"+str(which_cosmology['Ob0h2'])+"_Ocdm0h2"+str(which_cosmology['Ocdm0h2'])+".ini"
        write_mgcamb_parameterfile(hh=which_cosmology['h'], Ob0=which_cosmology['Ob0'], Ocdm0=which_cosmology['Ocdm0'],
                                 ns=which_cosmology['ns'], As=which_cosmology['As'], redshifts=redshifts,
                                 Ob0h2=which_cosmology['Ob0h2'], Ocdm0h2=which_cosmology['Ocdm0h2'],
                                 filename=CAMB_parameterfile,
                                 output_path=CAMB_outputdir_Pk, TypePk=0,
                                 Nthreads=0, kmax=100, model=model, rcH0=rcH0, F_R0=F_R0)
        exec_mgcamb(path_to_camb=MGCAMB_dir + "fortran/",
                  param_file=CAMB_parameterfile, execute=1)

        for zi in redshifts:
            kk, Plini = np.genfromtxt(
                CAMB_outputdir_Pk + "LINEARmatterpower_z" + "%0.3f" % zi + ".dat",
                unpack=True)
            Xi_lin = pk2xi(r_Mpch_log, kk, Plini, kmin=None, kmax=None,
                           kfactor=100, kbinsmax=100000,
                           Rg=None)
            xi_bar_lin = xi_bar(r_Mpch_log, r_Mpch_log, Xi_lin)
            xi_bbar_lin = xi_bar_lin / (1 + Xi_lin)
            corr_func_list.append(Xi_lin)
            barcorr_func_list.append(xi_bar_lin)
            bbarcorr_func_list.append(xi_bbar_lin)

    elif (do_Pknonlinear==True and MG==True):  # --> It means to use MGCAMB with NO linear Pk (halofit).
        os.system("rm -f " + CAMB_outputdir_Pk + "*")
        CAMB_parameterfile = MGCAMB_dir + "ini_files/PkNOLIN_" + which_cosmology['model']+"_h"+str(which_cosmology['h'])+"_Ob"+str(which_cosmology['Ob0'])+"_Ocdm"+str(which_cosmology['Ocdm0'])+"_ns"+str(which_cosmology['ns'])+"_As"+str(which_cosmology['As'])+"_Ob0h2"+str(which_cosmology['Ob0h2'])+"_Ocdm0h2"+str(which_cosmology['Ocdm0h2'])+".ini"
        write_mgcamb_parameterfile(hh=which_cosmology['h'], Ob0=which_cosmology['Ob0'], Ocdm0=which_cosmology['Ocdm0'],
                                 ns=which_cosmology['ns'], As=which_cosmology['As'], redshifts=redshifts,
                                 Ob0h2=which_cosmology['Ob0h2'], Ocdm0h2=which_cosmology['Ocdm0h2'],
                                 filename=CAMB_parameterfile,
                                 output_path=CAMB_outputdir_Pk, TypePk=1,
                                 Nthreads=0, kmax=100, model=model, rcH0=rcH0, F_R0=F_R0)
        exec_camb(path_to_camb=MGCAMB_dir + "fortran/",
                  param_file=CAMB_parameterfile, execute=1)

        for zi in redshifts:
            kk, Pnonlin = np.genfromtxt(
                CAMB_outputdir_Pk + "NOLINEARmatterpower_z" + "%0.3f" % zi + ".dat",
                unpack=True)
            Xi_hf = pk2xi(r_Mpch_log, kk, Pnonlin, kmin=None, kmax=None,
                          kfactor=100, kbinsmax=100000,
                          Rg=None)
            xi_bar_hf = xi_bar(r_Mpch_log, r_Mpch_log, Xi_hf)
            xi_bbar_hf = xi_bar_hf / (1 + Xi_hf)
            corr_func_list.append(Xi_hf)
            barcorr_func_list.append(xi_bar_hf)
            bbarcorr_func_list.append(xi_bbar_hf)

    else:
        print("Option no valid. Please verify your inputs.")

    # ------ After the loop, we convert the lists to Arrays of arrays
    xi_array = np.array(corr_func_list)
    xi_bar_array = np.array(barcorr_func_list)
    xi_bbar_array = np.array(bbarcorr_func_list)

    feedback_lvl = False

    if feedback_lvl:
        print('------------------------------------------------')
        print('Done calculating correlation functions from P(k)')
        print('------------------------------------------------')
    else:
        pass


    rarray = r_Mpch_log

    return rarray, scale_factors, redshifts, xi_array, xi_bar_array, xi_bbar_array


def numerical_deriv_xi(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                       use_r_array = False,
                       use_z_array = False,   z_args=[0, 2, 0.1],
                       redshift_simulation=[0, 0.3, 0.5, 1],
                       CAMB_path=CAMB_DATA_PATH,
                       CAMB_outputdir_Pk=user_CAMB_outputdir_Pk,
                       MG=False, model='00', rcH0=1.000, F_R0=0.00001):
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
    :param CAMB_path:
    :param CAMB_OUTPUTDIR_Pk:
    :param MG: boolean
    :param model: int if MG=True, model='99' for NDGP, or  model='04' for Hu-Sawicki F(R)
    :param rcH0: int if model='99' nDGP 1.000 or 5.000 for N1 or N5 respectively
    :param F_R0: int if model='04'  fR0(R) = 1e05, 1e06 for F5 or F6 respectively

    :return: r, a, z, xi_array, d_xi_da

    """

    r, scale_factors, z, xi_array, xi_bar_array, xi_bbar_array = \
        xis_from_pk(cosmo_args, z_array, r_array, r_args, use_r_array, use_z_array, z_args, redshift_simulation,
        CAMB_path, CAMB_outputdir_Pk, MG, model, rcH0, F_R0)

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

    feedback_lvl = False

    if feedback_lvl:
        print('------------------------------------------------')
        print('Done calculating the numerical derivative of xi(r,a)')
        print('------------------------------------------------')
    else:
        pass

    return r, a, z, xi_array, d_xi_da


# CAMB implementation
def write_camb_parameterfile(hh=0.7, Ob0=0.045, Ocdm0=0.28, ns=0.971, As=2.0e-09, redshifts=[0],
                             Ob0h2=None, Ocdm0h2=None, filename="parameter.ini",
                             output_path='./', TypePk=0, Nthreads=0, kmax=100):
    '''
    Function completely writen by JEGF
    Parameters
    ----------
    hh
    Ob0
    Ocdm0
    ns
    As
    redshifts
    Ob0h2
    Ocdm0h2
    filename
    output_path
    TypePk
    Nthreads
    kmax

    Returns
    -------

    '''
    if os.path.isfile(filename):
        pass
        # print("Parameter file exists")
    else:
        #print("Parameter file does not exist... creating the file\n")
        f = open(filename, "x")
        f.close()
    os.system("chmod -f 777 " + filename)

    redshifts = np.unique(redshifts)

    # print("redshifts for CAMB = ", redshifts)
    Numredshifts = len(redshifts)
    redshifts_sorted_reverse = redshifts[::-1]

    if Ob0h2==None:
        Ob0h2 = np.round(Ob0*hh**2, 6)
    if Ocdm0h2==None:
        Ocdm0h2 = np.round(Ocdm0*hh**2, 6)

    f = open(filename, "w")
    f.write("output_root = \n")
    f.write("get_scalar_cls = F\n")
    f.write("get_vector_cls = F\n")
    f.write("get_tensor_cls = F\n")
    f.write("get_transfer   = T\n")
    f.write("do_lensing     = F\n")
    if TypePk == 0:
        f.write("do_nonlinear = 0\n")
    elif TypePk == 1:
        f.write("do_nonlinear = 1\n")
    else:
        f.write("do_nonlinear = 0\n")
        print(
            "Type of Pk no valid.... Pk computed as linear, please check your inputs")
    f.write("l_max_scalar      = 2200\n")
    f.write("l_max_tensor      = 1500\n")
    f.write("k_eta_max_tensor  = 3000\n")
    f.write("ombh2          = " + str(np.round(Ob0h2, 6)) + "\n")
    f.write("omch2          = " + str(np.round(Ocdm0h2, 6)) + "\n")
    f.write("omnuh2         = 0.0\n")
    f.write("omk            = 0\n")
    f.write("hubble         = " + str(100. * hh) + "\n")
    f.write("dark_energy_model  = fluid\n")
    f.write("w              = -1\n")
    f.write("cs2_lam        = 1\n")
    f.write("temp_cmb           = 2.7255\n")
    f.write("helium_fraction    = 0.24\n")
    f.write("massless_neutrinos = 2.046\n")
    f.write("nu_mass_eigenstates = 1\n")
    f.write("massive_neutrinos  = 1\n")
    f.write("share_delta_neff = T\n")
    f.write("nu_mass_fractions = 1\n")
    f.write("nu_mass_degeneracies = \n")
    f.write("initial_power_num         = 1\n")
    f.write("pivot_scalar              = 0.05\n")
    f.write("pivot_tensor              = 0.05\n")
    f.write("scalar_amp(1)             = " + str(As) + "\n")
    f.write("scalar_spectral_index(1)  = " + str(ns) + "\n")
    f.write("scalar_nrun(1)            = 0\n")
    f.write("scalar_nrunrun(1)         = 0\n")
    f.write("tensor_spectral_index(1)  = 0\n")
    f.write("tensor_nrun(1)            = 0\n")
    f.write("tensor_parameterization   = 1\n")
    f.write("initial_ratio(1)          = 1\n")
    f.write("reionization         = T\n")
    f.write("re_use_optical_depth = T\n")
    f.write("re_optical_depth     = 0.09\n")
    f.write("re_delta_redshift    = 1.5\n")
    f.write("re_ionization_frac   = -1\n")
    f.write("re_helium_redshift = 3.5\n")
    f.write("re_helium_delta_redshift = 0.4\n")
    f.write("recombination_model = Recfast\n")
    f.write("RECFAST_fudge = 1.14\n")
    f.write("RECFAST_fudge_He = 0.86\n")
    f.write("RECFAST_Heswitch = 6\n")
    f.write("RECFAST_Hswitch  = T\n")
    f.write("initial_condition   = 1\n")
    f.write("initial_vector = -1 0 0 0 0\n")
    f.write("vector_mode = 0\n")
    f.write("COBE_normalize = F\n")
    f.write("CMB_outputscale = 7.42835025e12\n")
    f.write("transfer_high_precision = F\n")
    f.write("transfer_kmax           = " + str(kmax) + "\n")
    f.write("transfer_k_per_logint   = 0\n")
    f.write("transfer_num_redshifts  = " + str(Numredshifts) + "\n")
    f.write("transfer_interp_matterpower = T\n")

    for zz in range(1, len(redshifts_sorted_reverse) + 1):
        f.write("transfer_redshift(" + str(zz) + ")    = " + "%0.3f" %
                redshifts_sorted_reverse[zz - 1] + "\n")
        if TypePk == 0:
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "LINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "LINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
        elif TypePk == 1:
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "NOLINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "NOLINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
        else:
            f.write("do_nonlinear = 0\n")
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "LINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "LINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            print(
                "Type of Pk no valid.... Pk computed as linear, please check your inputs")

    f.write("transfer_power_var = 2\n")
    f.write("scalar_output_file = scalCls.dat\n")
    f.write("vector_output_file = vecCls.dat\n")
    f.write("tensor_output_file = tensCls.dat\n")
    f.write("total_output_file  = totCls.dat\n")
    f.write("lensed_output_file = lensedCls.dat\n")
    f.write("lensed_total_output_file  =lensedtotCls.dat\n")
    f.write("lens_potential_output_file = lenspotentialCls.dat\n")
    f.write("FITS_filename      = scalCls.fits\n")
    f.write("do_lensing_bispectrum = F\n")
    f.write("do_primordial_bispectrum = F\n")
    f.write("bispectrum_nfields = 1\n")
    f.write("bispectrum_slice_base_L = 0\n")
    f.write("bispectrum_ndelta=3\n")
    f.write("bispectrum_delta(1)=0\n")
    f.write("bispectrum_delta(2)=2\n")
    f.write("bispectrum_delta(3)=4\n")
    f.write("bispectrum_do_fisher= F\n")
    f.write('bispectrum_fisher_noise=0')
    f.write("bispectrum_fisher_noise_pol=0\n")
    f.write("bispectrum_fisher_fwhm_arcmin=7\n")
    f.write("bispectrum_full_output_file=\n")
    f.write("bispectrum_full_output_sparse=F\n")
    f.write("bispectrum_export_alpha_beta=F\n")
    f.write("feedback_level = 0\n")
    f.write("output_file_headers = T\n")
    f.write("derived_parameters = F\n")
    f.write("lensing_method = 1\n")
    f.write("accurate_BB = F\n")
    f.write("massive_nu_approx = 1\n")
    f.write("accurate_polarization   = T\n")
    f.write("accurate_reionization   = T\n")
    f.write("do_tensor_neutrinos     = T\n")
    f.write("accurate_massive_neutrino_transfers = F\n")
    f.write("do_late_rad_truncation   = T\n")
    f.write("halofit_version = 4\n")
    f.write("number_of_threads       = " + str(Nthreads) + "\n")
    f.write("accuracy_boost          = 1\n")
    f.write("l_accuracy_boost        = 1\n")
    f.write("l_sample_boost          = 1\n")
    f.close()
    # return print("CAMB parameterfile created successfully:)")
    return


def exec_camb(path_to_camb, param_file, execute=1):
    '''
    Function entirely coded by JEGF
    Parameters
    ----------
    path_to_camb
    param_file
    execute

    Returns
    -------

    '''
    feedback = False
    if feedback:
        print('----------------------------')
        print('>>> Running camb')
        print('----------------------------')

    # --- command line
    command_line = path_to_camb + 'camb ' + param_file + " > /dev/null"
    # print(command_line)
    # --- Execute command
    if execute == 1:
        os.system(command_line)
    else:
        print(command_line)

    # print('done for model')


# MGCAMB implementation
def write_mgcamb_parameterfile(hh=0.7, Ob0=0.045, Ocdm0=0.28, ns=0.971, As=2.0e-09, redshifts=[0],
                             Ob0h2=None, Ocdm0h2=None, filename="parameter.ini",
                             output_path='./', TypePk=0, Nthreads=0, kmax=100,
                             model='00', rcH0=1.000, F_R0 = 0.00001):
    '''
    Function entirely coded by JEGF
    Parameters
    ----------
    hh
    Ob0
    Ocdm0
    ns
    As
    redshifts
    Ob0h2
    Ocdm0h2
    filename
    output_path
    TypePk
    Nthreads
    kmax
    model
    rcH0
    F_R0

    Returns
    -------

    '''
    if os.path.isfile(filename):
        pass
    else:
        print("Parameter file does not exist... creating the file\n")
        f = open(filename, "x")
        f.close()
    os.system("chmod -f 777 " + filename)

    redshifts = np.unique(redshifts)

    Numredshifts = len(redshifts)
    redshifts_sorted_reverse = redshifts[::-1]

    if Ob0h2==None:
        Ob0h2 = np.round(Ob0*hh**2, 6)
    if Ocdm0h2==None:
        Ocdm0h2 = np.round(Ocdm0*hh**2, 6)

    f = open(filename, "w")
    f.write("output_root = \n")
    f.write("get_scalar_cls = F\n")
    f.write("get_vector_cls = F\n")
    f.write("get_tensor_cls = F\n")
    f.write("get_transfer   = T\n")
    f.write("do_lensing     = F\n")
    if TypePk == 0:
        f.write("do_nonlinear = 0\n")
    elif TypePk == 1:
        f.write("do_nonlinear = 1\n")
    else:
        f.write("do_nonlinear = 0\n")
        print(
            "Type of Pk no valid.... Pk computed as linear, please check your inputs")
    f.write("l_max_scalar      = 2200\n")
    f.write("l_max_tensor      = 1500\n")
    f.write("k_eta_max_tensor  = 3000\n")
    f.write("k_eta_max_scalar  = 4400.0000000000000\n")
    f.write("use_physical      = T\n")
    f.write("ombh2          = " + str(np.round(Ob0h2, 6)) + "\n")
    f.write("omch2          = " + str(np.round(Ocdm0h2, 6)) + "\n")
    f.write("omnuh2         = 0.0\n")
    f.write("omk            = 0\n")
    f.write("hubble         = " + str(100. * hh) + "\n")
    f.write("model          = " + model + "\n")
    if model == '99':
        f.write("rcH0 = " + str(rcH0) + "\n")
    f.write("GRtrans        = 0.001\n")
    f.write("B1             = 0 \n")
    f.write("lambda1_2      = 0 \n")
    f.write("B2             = 0 \n")
    f.write("lambda2_2      = 0 \n")
    f.write("ss             = 4 \n")
    f.write("MGQfix         = 1 \n")
    f.write("MGRfix         = 1 \n")
    f.write("Qnot           = 1. \n")
    f.write("Rnot           = 1. \n")
    f.write("sss            = 0. \n")
    f.write("B0             = " + str(F_R0) + "\n")
    f.write("beta1          = 1.3333333 \n")
    f.write("s              = 4 \n")
    f.write("Linder_gamma   = 0.545 \n")
    f.write("beta_star      = 1.0d0 \n")
    f.write("a_star         = 0.5d0 \n")
    f.write("xi_star        = 0.001d0 \n")
    f.write("beta0          = 1.d0 \n")
    f.write("xi0            = 0.0001 \n")
    f.write("DilS           = 0.24d0 \n")
    f.write("DilR           = 1.d0 \n")
    f.write("A2             = 1e3 \n")
    f.write("F_R0           = " + str(F_R0) + "d0 \n")
    f.write("FRn            = 1.d0 \n")
    f.write("w              = -1\n")
    f.write("cs2_lam        = 1\n")
    f.write("temp_cmb           = 2.7255\n")
    f.write("helium_fraction    = 0.24\n")
    f.write("massless_neutrinos = 2.046\n")
    f.write("nu_mass_eigenstates = 1\n")
    f.write("massive_neutrinos  = 1\n")
    f.write("share_delta_neff = T\n")
    f.write("nu_mass_fractions = 1\n")
    f.write("nu_mass_degeneracies = \n")
    f.write("initial_power_num         = 1\n")
    f.write("pivot_scalar              = 0.05\n")
    f.write("pivot_tensor              = 0.05\n")
    f.write("scalar_amp(1)             = " + str(As) + "\n")
    f.write("scalar_spectral_index(1)  = " + str(ns) + "\n")
    f.write("scalar_nrun(1)            = 0\n")
    f.write("scalar_nrunrun(1)         = 0\n")
    f.write("tensor_spectral_index(1)  = 0\n")
    f.write("tensor_nrun(1)            = 0\n")
    f.write("tensor_parameterization   = 1\n")
    f.write("initial_ratio(1)          = 1\n")
    f.write("reionization         = T\n")
    f.write("re_use_optical_depth = T\n")
    f.write("re_optical_depth     = 0.09\n")
    f.write("re_redshift          = 11\n")
    f.write("re_delta_redshift    = 1.5\n")
    f.write("re_ionization_frac   = -1\n")
    f.write("re_helium_redshift = 3.5\n")
    f.write("re_helium_delta_redshift = 0.4\n")
    f.write("recombination_model = Recfast\n")
    f.write("RECFAST_fudge = 1.14\n")
    f.write("RECFAST_fudge_He = 0.86\n")
    f.write("RECFAST_Heswitch = 6\n")
    f.write("RECFAST_Hswitch  = T\n")
    f.write("initial_condition   = 1\n")
    f.write("initial_vector = -1 0 0 0 0\n")
    f.write("vector_mode = 0\n")
    f.write("COBE_normalize = F\n")
    f.write("CMB_outputscale = 7.42835025e12\n")
    f.write("transfer_high_precision = T\n")
    f.write("transfer_kmax           = " + str(kmax) + "\n")
    f.write("transfer_k_per_logint   = 6\n")
    f.write("transfer_num_redshifts  = " + str(Numredshifts) + "\n")
    f.write("transfer_interp_matterpower = T\n")

    for zz in range(1, len(redshifts_sorted_reverse) + 1):
        f.write("transfer_redshift(" + str(zz) + ")    = " + "%0.3f" %
                redshifts_sorted_reverse[zz - 1] + "\n")
        if TypePk == 0:
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "LINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "LINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
        elif TypePk == 1:
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "NOLINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "NOLINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
        else:
            f.write("do_nonlinear = 0\n")
            f.write("transfer_filename(" + str(
                zz) + ")    = " + output_path + "LINEARtransfer_out_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            f.write("transfer_matterpower(" + str(
                zz) + ") = " + output_path + "LINEARmatterpower_z" + "%0.3f" %
                    redshifts_sorted_reverse[zz - 1] + ".dat\n")
            print(
                "Type of Pk no valid.... Pk computed as linear, please check your inputs")

    f.write("transfer_power_var = 2\n")
    f.write("scalar_output_file = scalCls.dat\n")
    f.write("vector_output_file = vecCls.dat\n")
    f.write("tensor_output_file = tensCls.dat\n")
    f.write("total_output_file  = totCls.dat\n")
    f.write("lensed_output_file = lensedCls.dat\n")
    f.write("lensed_total_output_file  =lensedtotCls.dat\n")
    f.write("lens_potential_output_file = lenspotentialCls.dat\n")
    f.write("FITS_filename      = scalCls.fits\n")
    f.write("do_lensing_bispectrum = F\n")
    f.write("do_primordial_bispectrum = F\n")
    f.write("bispectrum_nfields = 1\n")
    f.write("bispectrum_slice_base_L = 0\n")
    f.write("bispectrum_ndelta=3\n")
    f.write("bispectrum_delta(1)=0\n")
    f.write("bispectrum_delta(2)=2\n")
    f.write("bispectrum_delta(3)=4\n")
    f.write("bispectrum_do_fisher= F\n")
    f.write('bispectrum_fisher_noise=0\n')
    f.write("bispectrum_fisher_noise_pol=0\n")
    f.write("bispectrum_fisher_fwhm_arcmin=7\n")
    f.write("bispectrum_full_output_file=\n")
    f.write("bispectrum_full_output_sparse=F\n")
    f.write("bispectrum_export_alpha_beta=F\n")
    f.write("feedback_level = 0\n")
    f.write("output_file_headers = T\n")
    f.write("derived_parameters = F\n")
    f.write("lensing_method = 1\n")
    f.write("accurate_BB = F\n")
    f.write("massive_nu_approx = 1\n")
    f.write("accurate_polarization   = T\n")
    f.write("accurate_reionization   = T\n")
    f.write("do_tensor_neutrinos     = T\n")
    f.write("accurate_massive_neutrino_transfers = F\n")
    f.write("do_late_rad_truncation   = T\n")
    f.write("halofit_version = 4\n")
    f.write("number_of_threads       = " + str(Nthreads) + "\n")
    f.write("accuracy_boost          = 1\n")
    f.write("l_accuracy_boost        = 1\n")
    f.write("l_sample_boost          = 1\n")
    f.write("high_accuracy_default   = T\n")
    f.close()
    return


def exec_mgcamb(path_to_camb, param_file, execute=1):
    '''
    Function entirely coded by JEGF
    Parameters
    ----------
    path_to_camb
    param_file
    execute

    Returns
    -------

    '''
    feedback = False
    if feedback:
        print('----------------------------')
        print('>>> Running camb')
        print('----------------------------')

    # --- command line
    command_line = path_to_camb + 'camb ' + param_file + " > /dev/null"
    # print(command_line)
    # --- Execute command
    if execute == 1:
        os.system(command_line)
    else:
        print(command_line)


def As_from_sigma8(hh=0.7, Ob0=0.045, Ocdm0=0.28, ns=0.971, sigma8=0.82, As=2.0e-09, Ob0h2=None, Ocdm0h2=None,
                   path_to_camb='/opt/cosmo_data/CAMB/fortran/', parfilename="parameter.ini",
                   outputfile_sigma8="sigma8_z0.txt", output_path='./', Nthreads=0, kmax=100):
    '''
    This function computes the scalar amplitude, As, given the growth rate, sigma8(z=0), to normalize the linear
    power spectrum from CAMB.
    The function runs CAMB once to get the proper 'new' scalar amplitude, As, which is used
    as an input for the parameterfile in CAMB.
    '''
    write_camb_parameterfile(hh, Ob0, Ocdm0, ns, As, 0, Ob0h2, Ocdm0h2, parfilename, output_path, 0, Nthreads, kmax)
    feedback = False
    if feedback:
        print('----------------------------')
        print('>>> Running camb')
        print('----------------------------')

    # --- command line
    command_line = path_to_camb + 'camb ' + parfilename + '>' + outputfile_sigma8
    # print(command_line)
    # --- Execute command
    os.system(command_line)

    print('CAMB run successfully... reading sigma8 at z=0')
    sigma8_z0 = np.genfromtxt(outputfile_sigma8, delimiter='0 sigma8 (all matter) =', skip_footer=1)[1]
    true_sigma8_z0 = sigma8
    old_As = As
    new_As = old_As * (true_sigma8_z0 / sigma8_z0) ** 2

    return new_As


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
