# =============================================================================#
# coding: utf-8
# Mariana Jaber 2023
# Description:  Script to find the stable clustering regime
# =============================================================================#
import os
from os import sys
from stable_clustering import *

# rstar_sim_data()
# #
zss, rstar_gr, rpeak_gr, v12peak_gr = calculate_stable_clustering_and_peak(modelname='GR', idsufix='_SG',
                                                                           use_halofit=True)
# #
# zss, rstar_n1, rpeak_n1, v12peak_n1 = calculate_stable_clustering_and_peak(modelname='N1', idsufix='_SG',
#                                                                            use_halofit=False)
#
# zss, rstar_n5, rpeak_n5, v12peak_n5 = calculate_stable_clustering_and_peak(modelname='N5', idsufix='_SG',
#                                                                            use_halofit=False)
#
# zss, rstar_f5, rpeak_f5, v12peak_f5 = calculate_stable_clustering_and_peak(modelname='F5', idsufix='_SG',
#                                                                            use_halofit=False)
#
# zss, rstar_f6, rpeak_f6, v12peak_f6 = calculate_stable_clustering_and_peak(modelname='F6', idsufix='_SG',
#                                                                            use_halofit=False)


# zvals, v12_GR, v12_F5, v12_F6, v12_N1, v12_N5 = v12peak_sim_data()
# zvals, rstar_errors_all_models_hm = rstar_sim_data(sufix='_PLOT')
# zvals, rstar_errors_all_models_hf = rstar_sim_data(sufix='_hf')
# print(rstar_errors_all_models_hf['N5']/rstar_errors_all_models_hm['N5'])
# print(rstar_errors_all_models_hf['N1']/rstar_errors_all_models_hm['N1'])
# print(rstar_errors_all_models_hf['F5']/rstar_errors_all_models_hm['F5'])
# print(rstar_errors_all_models_hf['F6']/rstar_errors_all_models_hm['F6'])
# print(rstar_errors_all_models_hf['GR']/rstar_errors_all_models_hm['GR'])

# calculate_v12(modelname='GR', use_halofit=True)
#
# calculate_v12(modelname='F5', use_halofit=True)
# calculate_v12(modelname='F6', use_halofit=True)
# calculate_v12(modelname='N5', use_halofit=True)
# calculate_v12(modelname='N1', use_halofit=True)
#
# calculate_v12(modelname='F5', use_halofit=False)
# calculate_v12(modelname='F6', use_halofit=False)
# calculate_v12(modelname='N5', use_halofit=False)
# calculate_v12(modelname='N1', use_halofit=False)
