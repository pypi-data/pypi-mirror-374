# =============================================================================#
# coding: utf-8
# Mariana Jaber & Jorge Garcia-Farieta: 2022
# Description:
# =============================================================================#

from ..cosmology.a_to_z import *
from .core_functions import *
from ..cosmology.constants import *
from ..cosmology.cosmology import *

PATH = Path(os.path.abspath(os.path.dirname(__file__)))
CAMB_DATA_PATH = str(PATH / "../../resources") + "/"
user_CAMB_outputdir_Pk = str(PATH / "../../../data_camb/output_Pk_camb") + "/"

def v12_from_numerical_deriv(cosmo_args, z_array, r_array, r_args=[0.1, 40, 50],
                             use_r_array = True,
                             use_z_array = False, z_args=[0, 2, 0.1],
                             redshift_simulation=[0, 0.3, 0.5, 1],
                             which_simulation_redshift=0,
                             CAMB_path=CAMB_DATA_PATH,
                             CAMB_outputdir_Pk=user_CAMB_outputdir_Pk,
                             MG=False, model='00', rcH0=1.000, F_R0=0.00001):
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
    :param CAMB_path:
    :param CAMB_OUTPUTDIR_Pk:
    :param MG: boolean
    :param model: int if MG=True, model='99' for NDGP, or  model='04' for Hu-Sawicki F(R)
    :param rcH0: int if model='99' nDGP 1.000 or 5.000 for N1 or N5 respectively
    :param F_R0: int if model='04'  fR0(R) = 1e05, 1e06 for F5 or F6 respectively
    :return: r, v12,  a, z, xi_a, d_xi_da_a
    """

    r, a, z, xi_array, d_xi_da = numerical_deriv_xi(cosmo_args, z_array, r_array,
                                                    r_args, use_r_array,
                                                    use_z_array, z_args,
                                                    redshift_simulation, CAMB_path, CAMB_outputdir_Pk,
                                                    MG, model, rcH0, F_R0)
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