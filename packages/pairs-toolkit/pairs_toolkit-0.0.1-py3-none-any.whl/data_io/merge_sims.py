# =============================================================================#
# coding: utf-8
# Mariana Jaber 2023 : jaber@cft.edu.pl
# Description: Merge simulation data provided by JG with new errors from WH
# =============================================================================#

import numpy as np
import pandas as pd
import os
from os import sys


def merge_data_sims_GR():
    '''
    Merge the small and intermediate values from GR simulations
    As a result it saves a new file
    Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/GR_z0.X/v12AvgMerged.dat
    Returns: MESSAGE
    '''

    # ----------------- READING ---------------------
    ### Snapshots are defined: z0.0 = 38, z0.3 = 31, z0.5 = 27
    ### Models GR, N1, N5, F5, F6
    ### Scales contained: r = 0.05 - 1.94
    path_small_scales = '/opt/cosmo_data/sims/ELEPHANT/DM_subsamples/pairwise_vel/'

    ### Scales contained: 0.106639 - 42.3625
    ### Models GR, N1, N5, F5, F6
    path_inter_scales = '/home/jaber/shared/data/output_v12_DM/'



    ## Interm scales

    V12_GR_R40_z00_file = path_inter_scales +'GR_z0.0/v12Avg.dat'
    V12_GR_R40_z03_file = path_inter_scales +'GR_z0.3/v12Avg.dat'
    V12_GR_R40_z05_file = path_inter_scales +'GR_z0.5/v12Avg.dat'

    V12_GR_R40_z00 = pd.read_csv(V12_GR_R40_z00_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_GR_R40_z03= pd.read_csv(V12_GR_R40_z03_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_GR_R40_z05 = pd.read_csv(V12_GR_R40_z05_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])


    ## Small scales

    V12_GR_R2_z00_file = path_small_scales +'GR/GR_out38.v12.aver'
    V12_GR_R2_z03_file = path_small_scales +'GR/GR_out31.v12.aver'
    V12_GR_R2_z05_file = path_small_scales +'GR/GR_out27.v12.aver'

    V12_GR_R2_z00 = pd.read_csv(V12_GR_R2_z00_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_GR_R2_z03 = pd.read_csv(V12_GR_R2_z03_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_GR_R2_z05 = pd.read_csv(V12_GR_R2_z05_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])


    # ----------------- merging  ---------------------
    # -------- #
    r_cut = 1.0
    # -------- #


    ##  We need to replace the small bins of intermediate by the info contained in small data r2.0:
    ##  This seems to be the range where the errors of the new data are smaller than the
    ##  original dataset
    V12_GR_R2_z00_clean = V12_GR_R2_z00[V12_GR_R2_z00.r<r_cut]
    V12_GR_R2_z03_clean = V12_GR_R2_z03[V12_GR_R2_z03.r<r_cut]
    V12_GR_R2_z05_clean = V12_GR_R2_z05[V12_GR_R2_z05.r<r_cut]

    ###### intermediate scales ######

    ## data r40: dropped the smaller bins to substitute them by the new data
    V12_GR_R40_z00_clean = V12_GR_R40_z00[V12_GR_R40_z00.r>r_cut]
    V12_GR_R40_z03_clean = V12_GR_R40_z03[V12_GR_R40_z03.r>r_cut]
    V12_GR_R40_z05_clean = V12_GR_R40_z05[V12_GR_R40_z05.r>r_cut]

    ## Merged simulation data:
    # Concatenate the two dataframes
    v12_GR_Z00_merged = pd.concat([V12_GR_R2_z00_clean, V12_GR_R40_z00_clean])
    v12_GR_Z03_merged = pd.concat([V12_GR_R2_z03_clean, V12_GR_R40_z03_clean])
    v12_GR_Z05_merged = pd.concat([V12_GR_R2_z05_clean, V12_GR_R40_z05_clean])


    # Before finding the two bins two average we need to reset the index of the combined dataframe
    v12_GR_Z00_merged = v12_GR_Z00_merged.reset_index(drop=True)
    v12_GR_Z03_merged = v12_GR_Z03_merged.reset_index(drop=True)
    v12_GR_Z05_merged = v12_GR_Z05_merged.reset_index(drop=True)

    ### Find the indices of the two bins with r values closest to each other:

    min_diff_z00 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z03 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z05 = float('inf')  # Initialize minimum difference to a large value

    closest_idx_z00 = None
    closest_idx_z03 = None
    closest_idx_z05 = None

    for i in range(len(v12_GR_Z00_merged) - 1):
        diff_z00 = abs(v12_GR_Z00_merged.iloc[i + 1]['r'] - v12_GR_Z00_merged.iloc[i]['r'])
        if diff_z00 < min_diff_z00:
            min_diff_z00 = diff_z00
            closest_idx_z00 = i

    for j in range(len(v12_GR_Z03_merged) - 1):
        diff_z03 = abs(v12_GR_Z03_merged.iloc[j + 1]['r'] - v12_GR_Z03_merged.iloc[j]['r'])
        if diff_z03 < min_diff_z03:
            min_diff_z03 = diff_z03
            closest_idx_z03 = j

    for k in range(len(v12_GR_Z05_merged) - 1):
        diff_z05 = abs(v12_GR_Z05_merged.iloc[k + 1]['r'] - v12_GR_Z05_merged.iloc[k]['r'])
        if diff_z05 < min_diff_z05:
            min_diff_z05 = diff_z05
            closest_idx_z05 = k


    # Calculate the average of the closest bins for each column
    average_row_z00 = v12_GR_Z00_merged.iloc[closest_idx_z00:closest_idx_z00 + 2].mean()
    average_row_z03 = v12_GR_Z03_merged.iloc[closest_idx_z03:closest_idx_z03 + 2].mean()
    average_row_z05 = v12_GR_Z05_merged.iloc[closest_idx_z05:closest_idx_z05 + 2].mean()

    # Drop the closest rows
    v12_GR_Z00_merged = v12_GR_Z00_merged.drop([closest_idx_z00, closest_idx_z00 + 1])
    v12_GR_Z03_merged = v12_GR_Z03_merged.drop([closest_idx_z03, closest_idx_z03 + 1])
    v12_GR_Z05_merged = v12_GR_Z05_merged.drop([closest_idx_z05, closest_idx_z05 + 1])

    # Add the average row at the end of the DataFrame
    v12_GR_Z00_merged = v12_GR_Z00_merged.append(average_row_z00, ignore_index=True)
    v12_GR_Z03_merged = v12_GR_Z03_merged.append(average_row_z03, ignore_index=True)
    v12_GR_Z05_merged = v12_GR_Z05_merged.append(average_row_z05, ignore_index=True)


    # Sort the combined dataframe based on the 'r' column in ascending order
    v12_GR_Z00_merged= v12_GR_Z00_merged.sort_values('r', ascending=True)
    v12_GR_Z03_merged= v12_GR_Z03_merged.sort_values('r', ascending=True)
    v12_GR_Z05_merged= v12_GR_Z05_merged.sort_values('r', ascending=True)

    # Reset the index of the combined dataframe again
    v12_GR_Z00_merged = v12_GR_Z00_merged.reset_index(drop=True)
    v12_GR_Z03_merged = v12_GR_Z03_merged.reset_index(drop=True)
    v12_GR_Z05_merged = v12_GR_Z05_merged.reset_index(drop=True)


    # ----------------- Saving  ---------------------

    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.3', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.5', exist_ok=True)


    v12_GR_Z00_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.0/v12AvgMerged.dat', sep=' ')
    v12_GR_Z03_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.3/v12AvgMerged.dat', sep=' ')
    v12_GR_Z05_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/GR_z0.5/v12AvgMerged.dat', sep=' ')

    print('Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/GR_z0.X/v12AvgMerged.dat')
    print('>>>>> ')
    print('with X = 0, 3, or 5')
    print('>>>>> ')
    print('The way of reading them is:  pd.read_csv(args, skiprows=1)')
    print('>>>>> ')

    return

def merge_data_sims_FofR(modelname="F5"):
    """
    Merge the small and intermediate values from f(R) simulations
    As a result it saves a new file
    Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/F{Y}_z0.{X}/v12AvgMerged.dat
    with Y=5,6 and X=0,3,5

   Parameters
   ----------
   modelname = 'F5' or 'F6'

   Returns
   -------
   """
    ### ----------------- READING ---------------------
    ### Snapshots are defined: z0.0 = 38, z0.3 = 31, z0.5 = 27
    ### Models GR, N1, N5, F5, F6
    ### Scales contained: r = 0.05 - 1.94
    path_small_scales = '/opt/cosmo_data/sims/ELEPHANT/DM_subsamples/pairwise_vel/'

    ### Scales contained: 0.106639 - 42.3625
    ### Models GR, N1, N5, F5, F6
    path_inter_scales = '/home/jaber/shared/data/output_v12_DM/'

    if modelname == 'F5':

        V12_FY_R40_z00_file = path_inter_scales +'F5_z0.0/v12Avg.dat'
        V12_FY_R40_z03_file = path_inter_scales +'F5_z0.3/v12Avg.dat'
        V12_FY_R40_z05_file = path_inter_scales +'F5_z0.5/v12Avg.dat'

        V12_FY_R2_z00_file = path_small_scales +'F5/F5_out38.v12.aver'
        V12_FY_R2_z03_file = path_small_scales +'F5/F5_out31.v12.aver'
        V12_FY_R2_z05_file = path_small_scales +'F5/F5_out27_v12.aver' # typo in filename

    else:
        V12_FY_R40_z00_file = path_inter_scales + 'F6_z0.0/v12Avg.dat'
        V12_FY_R40_z03_file = path_inter_scales + 'F6_z0.3/v12Avg.dat'
        V12_FY_R40_z05_file = path_inter_scales + 'F6_z0.5/v12Avg.dat'

        V12_FY_R2_z00_file = path_small_scales + 'F6/F6_out38.v12.aver'
        V12_FY_R2_z03_file = path_small_scales + 'F6/F6_out31.v12.aver'
        V12_FY_R2_z05_file = path_small_scales + 'F6/F6_out27.v12.aver'

    ## Interm scales

    V12_FY_R40_z00 = pd.read_csv(V12_FY_R40_z00_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])

    V12_FY_R40_z03 = pd.read_csv(V12_FY_R40_z03_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])

    V12_FY_R40_z05 = pd.read_csv(V12_FY_R40_z05_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])


    ## Small scales

    V12_FY_R2_z00 = pd.read_csv(V12_FY_R2_z00_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_FY_R2_z03 = pd.read_csv(V12_FY_R2_z03_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_FY_R2_z05 = pd.read_csv(V12_FY_R2_z05_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])


    # ----------------- merging  ---------------------
    # -------- #
    r_cut_1 = 1.2
    r_cut_2 = 1.0
    ## Two different cutting scales to guarantee overlapping in the data
    # -------- #


    ##  We need to replace the small bins of intermediate by the info contained in small data r2.0:
    ##  This seems to be the range where the errors of the new data are smaller than the
    ##  original dataset
    V12_FY_R2_z00_clean = V12_FY_R2_z00[V12_FY_R2_z00.r<r_cut_1]
    V12_FY_R2_z03_clean = V12_FY_R2_z03[V12_FY_R2_z03.r<r_cut_1]
    V12_FY_R2_z05_clean = V12_FY_R2_z05[V12_FY_R2_z05.r<r_cut_1]

    ###### intermediate scales ######

    ## data r40: dropped the smaller bins to substitute them by the new data
    V12_FY_R40_z00_clean = V12_FY_R40_z00[V12_FY_R40_z00.r>r_cut_2]
    V12_FY_R40_z03_clean = V12_FY_R40_z03[V12_FY_R40_z03.r>r_cut_2]
    V12_FY_R40_z05_clean = V12_FY_R40_z05[V12_FY_R40_z05.r>r_cut_2]

    ## Merged simulation data:
    # Concatenate the two dataframes
    v12_FY_Z00_merged = pd.concat([V12_FY_R2_z00_clean, V12_FY_R40_z00_clean])
    v12_FY_Z03_merged = pd.concat([V12_FY_R2_z03_clean, V12_FY_R40_z03_clean])
    v12_FY_Z05_merged = pd.concat([V12_FY_R2_z05_clean, V12_FY_R40_z05_clean])


    # Before finding the two closest bins too average we need to reset the index of the combined dataframe
    v12_FY_Z00_merged = v12_FY_Z00_merged.reset_index(drop=True)
    v12_FY_Z03_merged = v12_FY_Z03_merged.reset_index(drop=True)
    v12_FY_Z05_merged = v12_FY_Z05_merged.reset_index(drop=True)

    ### Find the indices of the two bins with r values closest to each other:

    min_diff_z00 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z03 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z05 = float('inf')  # Initialize minimum difference to a large value

    closest_idx_z00 = None
    closest_idx_z03 = None
    closest_idx_z05 = None

    for i in range(len(v12_FY_Z00_merged) - 1):
        diff_z00 = abs(v12_FY_Z00_merged.iloc[i + 1]['r'] - v12_FY_Z00_merged.iloc[i]['r'])
        if diff_z00 < min_diff_z00:
            min_diff_z00 = diff_z00
            closest_idx_z00 = i

    for j in range(len(v12_FY_Z03_merged) - 1):
        diff_z03 = abs(v12_FY_Z03_merged.iloc[j + 1]['r'] - v12_FY_Z03_merged.iloc[j]['r'])
        if diff_z03 < min_diff_z03:
            min_diff_z03 = diff_z03
            closest_idx_z03 = j

    for k in range(len(v12_FY_Z05_merged) - 1):
        diff_z05 = abs(v12_FY_Z05_merged.iloc[k + 1]['r'] - v12_FY_Z05_merged.iloc[k]['r'])
        if diff_z05 < min_diff_z05:
            min_diff_z05 = diff_z05
            closest_idx_z05 = k


    # Calculate the average of the closest bins for each column
    average_row_z00 = v12_FY_Z00_merged.iloc[closest_idx_z00:closest_idx_z00 + 2].mean()
    average_row_z03 = v12_FY_Z03_merged.iloc[closest_idx_z03:closest_idx_z03 + 2].mean()
    average_row_z05 = v12_FY_Z05_merged.iloc[closest_idx_z05:closest_idx_z05 + 2].mean()

    # Drop the closest rows
    v12_FY_Z00_merged = v12_FY_Z00_merged.drop([closest_idx_z00, closest_idx_z00 + 1])
    v12_FY_Z03_merged = v12_FY_Z03_merged.drop([closest_idx_z03, closest_idx_z03 + 1])
    v12_FY_Z05_merged = v12_FY_Z05_merged.drop([closest_idx_z05, closest_idx_z05 + 1])

    # Add the average row at the end of the DataFrame
    v12_FY_Z00_merged = v12_FY_Z00_merged.append(average_row_z00, ignore_index=True)
    v12_FY_Z03_merged = v12_FY_Z03_merged.append(average_row_z03, ignore_index=True)
    v12_FY_Z05_merged = v12_FY_Z05_merged.append(average_row_z05, ignore_index=True)


    # Sort the combined dataframe based on the 'r' column in ascending order
    v12_FY_Z00_merged= v12_FY_Z00_merged.sort_values('r', ascending=True)
    v12_FY_Z03_merged= v12_FY_Z03_merged.sort_values('r', ascending=True)
    v12_FY_Z05_merged= v12_FY_Z05_merged.sort_values('r', ascending=True)

    # Reset the index of the combined dataframe again
    v12_FY_Z00_merged = v12_FY_Z00_merged.reset_index(drop=True)
    v12_FY_Z03_merged = v12_FY_Z03_merged.reset_index(drop=True)
    v12_FY_Z05_merged = v12_FY_Z05_merged.reset_index(drop=True)


    # ----------------- Saving  ---------------------

    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.0', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.3', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.5', exist_ok=True)


    v12_FY_Z00_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.0/v12AvgMerged.dat', sep=' ')
    v12_FY_Z03_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.3/v12AvgMerged.dat', sep=' ')
    v12_FY_Z05_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.5/v12AvgMerged.dat', sep=' ')

    # print('Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/FY_z0.X/v12AvgMerged.dat')
    print(
        'Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/' + modelname + '_z0.X/v12AvgMerged.dat')
    print('>>>>> ')
    print('>>>>> ')
    print('with  X = 0, 3, or 5')
    print('>>>>> ')
    print('The way of reading them is:  pd.read_csv(args, skiprows=1)')
    print('>>>>> ')

    return

def merge_data_sims_nDGP(modelname="N5"):
    """
    !!!!!! nan in old N1 z03 data !!!!!!
    !!!!! fix: use the data stored in /home/jaber/velocities/velocities/data/output_rmax_42/N1_z0.3/v12Avg.dat

    Merge the small and intermediate values from nDGP simulations
    As a result it saves a new file
    Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/N{Y}_z0.{X}/v12AvgMerged.dat
    with Y=5,1 and X=0,3,5

   Parameters
   ----------
   modelname = 'N5' or 'N1'

   Returns
   -------
   """
    ### ----------------- READING ---------------------
    ### ----------------- READING ---------------------
    ### Snapshots are defined: z0.0 = 38, z0.3 = 31, z0.5 = 27
    ### Models N1, N5
    ### Scales contained: r = 0.05 - 1.94
    path_small_scales = '/opt/cosmo_data/sims/ELEPHANT/DM_subsamples/pairwise_vel/'

    ### Scales contained: 0.106639 - 42.3625
    ### Models N1, N5
    # path_inter_scales = '/home/jaber/shared/data/output_v12_DM/' ## old bug of NAN in Jorge's data
    path_inter_scales = '/home/jaber/velocities/velocities/data/output_rmax_42/'


    if modelname == 'N5':

        V12_NY_R40_z00_file = path_inter_scales +'N5_z0.0/v12Avg.dat'
        V12_NY_R40_z03_file = path_inter_scales +'N5_z0.3/v12Avg.dat'
        V12_NY_R40_z05_file = path_inter_scales +'N5_z0.5/v12Avg.dat'



        V12_NY_R2_z00_file = path_small_scales +'N5/N5_out38.v12.aver'
        V12_NY_R2_z03_file = path_small_scales +'N5/N5_out31.v12.aver'
        V12_NY_R2_z05_file = path_small_scales +'N5/N5_out27.v12.aver'

    else:
        V12_NY_R40_z00_file = path_inter_scales + 'N1_z0.0/v12Avg.dat'
        V12_NY_R40_z03_file = path_inter_scales + 'N1_z0.3/v12Avg.dat'
        V12_NY_R40_z05_file = path_inter_scales + 'N1_z0.5/v12Avg.dat'

        V12_NY_R2_z00_file = path_small_scales + 'N1/N1_out38.v12.aver'
        V12_NY_R2_z03_file = path_small_scales + 'N1/N1_out31.v12.aver'
        V12_NY_R2_z05_file = path_small_scales + 'N1/N1_out27.v12.aver'

    ## Interm scales

    V12_NY_R40_z00 = pd.read_csv(V12_NY_R40_z00_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])

    V12_NY_R40_z03 = pd.read_csv(V12_NY_R40_z03_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])

    V12_NY_R40_z05 = pd.read_csv(V12_NY_R40_z05_file, sep='\s+', comment='#',
                                 names=["r", "v12", "Errv12"])


    ## Small scales

    V12_NY_R2_z00 = pd.read_csv(V12_NY_R2_z00_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_NY_R2_z03 = pd.read_csv(V12_NY_R2_z03_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])

    V12_NY_R2_z05 = pd.read_csv(V12_NY_R2_z05_file,sep='\s+', comment='#',
                           names=["r", "v12", "Errv12"])


    # ----------------- merging  ---------------------
    # -------- #
    r_cut_1 = 1.2
    r_cut_2 = 1.0
    ## Two different cutting scales to guarantee overlapping in the data
    # -------- #


    ##  We need to replace the small bins of intermediate by the info contained in small data r2.0:
    ##  This seems to be the range where the errors of the new data are smaller than the
    ##  original dataset
    V12_NY_R2_z00_clean = V12_NY_R2_z00[V12_NY_R2_z00.r<r_cut_1]
    V12_NY_R2_z03_clean = V12_NY_R2_z03[V12_NY_R2_z03.r<r_cut_1]
    V12_NY_R2_z05_clean = V12_NY_R2_z05[V12_NY_R2_z05.r<r_cut_1]

    ###### intermediate scales ######

    ## data r40: dropped the smaller bins to substitute them by the new data
    V12_NY_R40_z00_clean = V12_NY_R40_z00[V12_NY_R40_z00.r>r_cut_2]
    V12_NY_R40_z03_clean = V12_NY_R40_z03[V12_NY_R40_z03.r>r_cut_2]
    V12_NY_R40_z05_clean = V12_NY_R40_z05[V12_NY_R40_z05.r>r_cut_2]

    ## Merged simulation data:
    # Concatenate the two dataframes
    v12_NY_Z00_merged = pd.concat([V12_NY_R2_z00_clean, V12_NY_R40_z00_clean])
    v12_NY_Z03_merged = pd.concat([V12_NY_R2_z03_clean, V12_NY_R40_z03_clean])
    v12_NY_Z05_merged = pd.concat([V12_NY_R2_z05_clean, V12_NY_R40_z05_clean])


    # Before finding the two closest bins too average we need to reset the index of the combined dataframe
    v12_NY_Z00_merged = v12_NY_Z00_merged.reset_index(drop=True)
    v12_NY_Z03_merged = v12_NY_Z03_merged.reset_index(drop=True)
    v12_NY_Z05_merged = v12_NY_Z05_merged.reset_index(drop=True)

    ### Find the indices of the two bins with r values closest to each other:

    min_diff_z00 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z03 = float('inf')  # Initialize minimum difference to a large value
    min_diff_z05 = float('inf')  # Initialize minimum difference to a large value

    closest_idx_z00 = None
    closest_idx_z03 = None
    closest_idx_z05 = None

    for i in range(len(v12_NY_Z00_merged) - 1):
        diff_z00 = abs(v12_NY_Z00_merged.iloc[i + 1]['r'] - v12_NY_Z00_merged.iloc[i]['r'])
        if diff_z00 < min_diff_z00:
            min_diff_z00 = diff_z00
            closest_idx_z00 = i

    for j in range(len(v12_NY_Z03_merged) - 1):
        diff_z03 = abs(v12_NY_Z03_merged.iloc[j + 1]['r'] - v12_NY_Z03_merged.iloc[j]['r'])
        if diff_z03 < min_diff_z03:
            min_diff_z03 = diff_z03
            closest_idx_z03 = j

    for k in range(len(v12_NY_Z05_merged) - 1):
        diff_z05 = abs(v12_NY_Z05_merged.iloc[k + 1]['r'] - v12_NY_Z05_merged.iloc[k]['r'])
        if diff_z05 < min_diff_z05:
            min_diff_z05 = diff_z05
            closest_idx_z05 = k


    # Calculate the average of the closest bins for each column
    average_row_z00 = v12_NY_Z00_merged.iloc[closest_idx_z00:closest_idx_z00 + 2].mean()
    average_row_z03 = v12_NY_Z03_merged.iloc[closest_idx_z03:closest_idx_z03 + 2].mean()
    average_row_z05 = v12_NY_Z05_merged.iloc[closest_idx_z05:closest_idx_z05 + 2].mean()

    # Drop the closest rows
    v12_NY_Z00_merged = v12_NY_Z00_merged.drop([closest_idx_z00, closest_idx_z00 + 1])
    v12_NY_Z03_merged = v12_NY_Z03_merged.drop([closest_idx_z03, closest_idx_z03 + 1])
    v12_NY_Z05_merged = v12_NY_Z05_merged.drop([closest_idx_z05, closest_idx_z05 + 1])

    # Add the average row at the end of the DataFrame
    v12_NY_Z00_merged = v12_NY_Z00_merged.append(average_row_z00, ignore_index=True)
    v12_NY_Z03_merged = v12_NY_Z03_merged.append(average_row_z03, ignore_index=True)
    v12_NY_Z05_merged = v12_NY_Z05_merged.append(average_row_z05, ignore_index=True)


    # Sort the combined dataframe based on the 'r' column in ascending order
    v12_NY_Z00_merged= v12_NY_Z00_merged.sort_values('r', ascending=True)
    v12_NY_Z03_merged= v12_NY_Z03_merged.sort_values('r', ascending=True)
    v12_NY_Z05_merged= v12_NY_Z05_merged.sort_values('r', ascending=True)

    # Reset the index of the combined dataframe again
    v12_NY_Z00_merged = v12_NY_Z00_merged.reset_index(drop=True)
    v12_NY_Z03_merged = v12_NY_Z03_merged.reset_index(drop=True)
    v12_NY_Z05_merged = v12_NY_Z05_merged.reset_index(drop=True)


    # ----------------- Saving  ---------------------

    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.0', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.3', exist_ok=True)
    os.makedirs('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.5', exist_ok=True)


    v12_NY_Z00_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.0/v12AvgMerged.dat', sep=' ')
    v12_NY_Z03_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.3/v12AvgMerged.dat', sep=' ')
    v12_NY_Z05_merged.to_csv('/home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.5/v12AvgMerged.dat', sep=' ')

    print('Files saved in the new location: /home/jaber/shared/data/output_v12_DM_merged/'+modelname+'_z0.X/v12AvgMerged.dat')
    print('>>>>> ')
    print('with X = 0, 3, or 5')
    print('>>>>> ')
    print('The way of reading them is:  pd.read_csv(args, skiprows=1)')
    print('>>>>> ')

    return