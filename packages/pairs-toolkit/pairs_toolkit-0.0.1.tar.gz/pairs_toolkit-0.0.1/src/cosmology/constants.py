# =============================================================================#
# coding: utf-8
# Mariana Jaber & Jorge Garcia-Farieta: 2022
# Description:
# =============================================================================#
# -----------------------------------------
#   \\\\\     BASIC CONSTANTS        \\\\\\
# -----------------------------------------
import numpy as np

# -- Physical constants
PI = np.pi
C = 299792458.  # m/s
HBAR = 6.62606896 / (2 * PI) * 1e-34  # J.s
E = 1.6021773 * 1e-19  # electron unit charge
G = 6.6738 * 1e-11  # Newton's gravity constant
Mpc = 3.085678 * 1e22  # meters
KBoltz = 1.3806504 * 1e-23  # J/K

# ---- Masa  de Planck y masa reducida de Planck en eV
MPlanck = np.sqrt(HBAR * C / (8 * PI * G)) * C ** 2 / E
mplanck = MPlanck * np.sqrt(8 * PI * G)

# ----  CMB temperature (in Kelvin), neutrinos
Tg0 = 2.7255
Neff = 3.046  # 3.046 vanilla value  # 3.13 (eqn. 60a-60d, arXiv:1502.01589)
THETHADEC = 1.04105e-2
TAU = 0.079
Z_DRAG = 1059.57
Z_DEC = 1090.09

# ----- Hubble parameter and units
REDUCED_H0 = 0.697
H0 = (REDUCED_H0 * 1e5) / C
H0P = (100 * 1e3) / 2.99792458e+8

# --------- critical density
RHOCR0 = 3 * (REDUCED_H0 * MPlanck * E * Mpc * 10 ** 5 / (C ** 2 * HBAR)) ** 2  # units?

rho_crit = 2.77536627e11  # h^2 Msun/Mpc^3
deltac = 1.686  # spherical collapse value

# ------- today's value of radiation density
RHOR0 = (1 + Neff * 7. / 8. * (4. / 11.) ** (
        4. / 3.)) * PI ** 2 / 15. * Tg0 ** 4 * (KBoltz * Mpc / (C * HBAR)) ** 4

# ------------------------------
# The default value of the densities
OMEGAR0 = 0.  # RHOR0 / RHOCR0
OMEGA_M0 = 0.281
OMEGA_B0 = 0.046
OMEGA_CDM0 = OMEGA_M0 - OMEGA_B0

#  ------ PHYSICAL DENSITIES
OMEGAB0H2 = OMEGA_B0 * REDUCED_H0 * REDUCED_H0  # 0.022347214
OMEGAC0H2 = OMEGA_CDM0 * REDUCED_H0 * REDUCED_H0  # 0.1142

# --- other parameters from the simulations
L_BOX = 1024.0   # Mpc/h
SIGMA80 = 0.842  # changed from 0.82 to fix the large scales discrepancies
NS = 0.971
AS = 2.297100987e-9  # changed  from 2.0e-9 to the value that provides the SIGMA8 = 0.842
