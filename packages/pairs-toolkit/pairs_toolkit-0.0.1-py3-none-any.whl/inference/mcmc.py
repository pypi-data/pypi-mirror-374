# =============================================================================#
# coding:        utf-8
# Mariana Jaber: 2024
# Description:   MCMC implementation of log(like(v12))
# =============================================================================#

import numpy as np
import emcee
import datetime
import os
import sys

from loglike import * 
from ..cosmology.constants import OMEGAB0H2, OMEGAC0H2, REDUCED_H0, AS

# -------- paths -----------------
# 
# Define the directory and file name

data_path = '/home/jaber/shared/data/'
path_to_save_figs   = os.path.join(data_path, 'figs/')
path_to_chains = os.path.join(data_path, 'chains/')


# Check if the directory exists, create it if it does not
if not os.path.exists(path_to_save_figs):
    os.makedirs(path_to_save_figs)

if not os.path.exists(path_to_chains):
    os.makedirs(path_to_chains)

# ------- date and time stamps -----
now = datetime.datetime.now()
date_str = now.strftime("%Y%m%d-%H%M")
# print(date_str)

# --- For now, by default the cosmology is the one for ELEPHANT
cosmoELEPHANT = define_cosmology()

# ----- set the true cosmological  parameters 
As_true = AS

logAs_true = np.log(10 ** 10 * As_true)
Och2_true = OMEGAC0H2
h_true = REDUCED_H0

true_vals = np.array([logAs_true, Och2_true, h_true])

### 
