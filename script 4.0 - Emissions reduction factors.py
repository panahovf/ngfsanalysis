# In[1]:
# Date: Aug 11, 2024
# Project: Identify scale value to be aligned with carbon budget
# Author: Farhad Panahov




# In[2]:
# load packages

import os
import pandas as pd
import geopandas as gpd
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter










# In[3]:
# directory & load data

directory = r'C:\Users\panah\OneDrive\Desktop\Work\2 - RA - Climate fin'
os.chdir(directory)
del directory


# --------------
# load emissions data
df_emissions_secondary = pd.read_excel("2 - output/script 3.1/1.1 - Secondary - emissions FA - projection.xlsx")
df_emissions_primary = pd.read_excel("2 - output/script 3.2/1.1 - Primary - emissions FA - projection.xlsx")


# --------------
# load percent change dataset
df_change_secondary = pd.read_excel("2 - output/script 3.1/1.2 - Secondary - emissions FA - change.xlsx")
df_change_primary = pd.read_excel("2 - output/script 3.2/1.2 - Primary - emissions FA - change.xlsx")


# --------------
# load ngfs growth for total energy
df_ngfs_total_annual = pd.read_excel('2 - output/script 2/1.5 - GCAM - emissions - energy.xlsx')
df_ngfs_total_annual= df_ngfs_total_annual.drop(columns = ['2020', '2021', '2022', '2023']) # removing 2020-2023


# --------------
# load ngfs secondary & primary emissions
df_ngfs_secondary = pd.read_excel("2 - output/script 3.1/1.3 - Secondary - emissions NGFS - projection.xlsx")
df_ngfs_primary = pd.read_excel("2 - output/script 3.2/1.3 - Primary - emissions NGFS - projection.xlsx")


# --------------
# carbon budget
df_carbon_bugdet = pd.read_excel('1 - input/updated_carbon_budget_processed - 2024.xlsx')










# In[4]: DROP 2050-2100
############################

# drop 2051-2100
drop_columns = [str(year) for year in range(2051, 2101)]

df_emissions_secondary= df_emissions_secondary.drop(columns = drop_columns) # removing 2050-2100
df_emissions_primary= df_emissions_primary.drop(columns = drop_columns) # removing 2050-2100
df_change_secondary= df_change_secondary.drop(columns = drop_columns) # removing 2050-2100
df_change_primary= df_change_primary.drop(columns = drop_columns) # removing 2050-2100
df_ngfs_total_annual= df_ngfs_total_annual.drop(columns = drop_columns) # removing 2050-2100
df_ngfs_secondary= df_ngfs_secondary.drop(columns = drop_columns) # removing 2050-2100
df_ngfs_primary= df_ngfs_primary.drop(columns = drop_columns) # removing 2050-2100

del drop_columns










# In[4]: DIVIDE BY SCENARIOS
############################

# --------------
# current policies
#secondary
df_emissions_secondary_currentpolicy = df_emissions_secondary[df_emissions_secondary['Scenario'] == "Current Policies"]
df_emissions_secondary_currentpolicy.reset_index(drop=True, inplace=True)


# primary
df_emissions_primary_currentpolicy = df_emissions_primary[df_emissions_primary['Scenario'] == "Current Policies"]
df_emissions_primary_currentpolicy.reset_index(drop=True, inplace=True)

df_change_primary_currentpolicy = df_change_primary[df_change_primary['Scenario'] == "Current Policies"]
df_change_primary_currentpolicy.reset_index(drop=True, inplace=True)


# --------------
# net zero
#secondary
df_emissions_secondary_netzero = df_emissions_secondary[df_emissions_secondary['Scenario'] == "Net Zero 2050"]
df_emissions_secondary_netzero.reset_index(drop=True, inplace=True)

df_change_secondary_netzero = df_change_secondary[df_change_secondary['Scenario'] == "Net Zero 2050"]
df_change_secondary_netzero.reset_index(drop=True, inplace=True)

# primary
df_emissions_primary_netzero = df_emissions_primary[df_emissions_primary['Scenario'] == "Net Zero 2050"]
df_emissions_primary_netzero.reset_index(drop=True, inplace=True)

df_change_primary_netzero = df_change_primary[df_change_primary['Scenario'] == "Net Zero 2050"]
df_change_primary_netzero.reset_index(drop=True, inplace=True)


# --------------
# DO THE SAME TO THE NGFS
# secondary
df_ngfs_secondary_currentpolicy = df_ngfs_secondary[df_ngfs_secondary['Scenario'] == "Current Policies"]
df_ngfs_secondary_currentpolicy.reset_index(drop=True, inplace=True)

df_ngfs_secondary_netzero = df_ngfs_secondary[df_ngfs_secondary['Scenario'] == "Net Zero 2050"]
df_ngfs_secondary_netzero.reset_index(drop=True, inplace=True)

# primary
df_ngfs_primary_currentpolicy = df_ngfs_primary[df_ngfs_primary['Scenario'] == "Current Policies"]
df_ngfs_primary_currentpolicy.reset_index(drop=True, inplace=True)

df_ngfs_primary_netzero = df_ngfs_primary[df_ngfs_primary['Scenario'] == "Net Zero 2050"]
df_ngfs_primary_netzero.reset_index(drop=True, inplace=True)


# --------------
del df_change_primary, df_change_secondary, df_emissions_primary, df_emissions_secondary, df_ngfs_secondary, df_ngfs_primary










# In[4]: GET NGFS TOTAL ENERGY EMISSIONS GROWTH RATES
#####################################################

# --------------
# GET TOTALS FOR ALL SCENARIOS

# select years
year_columns = [str(year) for year in range(2024, 2051)]

# get total NGFS by scenario
df_ngfs_total_annual = df_ngfs_total_annual.groupby('Scenario')[year_columns].sum()

# get % change annually
# Calculate yearly percent change for each row
df_ngfs_annual_change = df_ngfs_total_annual.pct_change(axis=1) * 100
df_total_annual = df_ngfs_annual_change.copy()

# remove 2020-22
# set 2023 energy emissions at 37.4 GT CO2
# https://www.iea.org/reports/co2-emissions-in-2023/executive-summary
df_total_annual['2024'] = 37400 # set










# In[5]: PROJECT THE GROWTH TO ANNUAL EMISSIOSN
###############################################

# after this we get dataframe for secondary energy by source/country/scenario with annual emissions values
for i in range(1, len(year_columns)):
    previous_year = year_columns[i - 1]  # Get the previous year
    current_year = year_columns[i]       # Get the current year
    # Update the current year's values based on the previous year
    df_total_annual[current_year] = df_total_annual[previous_year] * (1 + df_total_annual[current_year] / 100)


del i, current_year, previous_year

df_total_annual.reset_index(inplace=True)


# -------------
# GET SCENARIOS
df_total_annual_currentpolicy = df_total_annual[df_total_annual['Scenario'] == "Current Policies"]
df_total_annual_netzero = df_total_annual[df_total_annual['Scenario'] == "Net Zero 2050"]


# --------------
del df_ngfs_total_annual, df_total_annual










# In[]: GET RESIDUAL EMISSIONS
##############################

# --------------
# current policies --- emissions & percent change
df_residual_currentpolicy = df_total_annual_currentpolicy[year_columns] - df_emissions_secondary_currentpolicy[year_columns].sum() - df_emissions_primary_currentpolicy[year_columns].sum()
df_residual_currentpolicy_change = df_residual_currentpolicy.pct_change(axis = 1) * 100


# --------------
# netzero --- emissions & percent change
df_residual_netzero = df_total_annual_netzero[year_columns] - df_emissions_secondary_netzero[year_columns].sum() - df_emissions_primary_netzero[year_columns].sum()
df_residual_netzero_change = df_residual_netzero.pct_change(axis = 1) * 100










# In[]: GET CUMULATIVE EMISSIONS & ESTABLISH REDUCTION FACTORS

year_columns = [str(year) for year in range(2024, 2051)]


# --------------
# current policy --- # cumulative
df_total_cumulative_currentpolicy = df_total_annual_currentpolicy.copy()
df_total_cumulative_currentpolicy[year_columns] = df_total_cumulative_currentpolicy[year_columns].cumsum(axis=1)

var_total2050_currentpolicy = df_total_cumulative_currentpolicy['2050'].values[0] / 1000
# print(var_total2050_currentpolicy)
# 1062.135498610886

df_ratio_currentpolicy = df_carbon_bugdet.copy()
df_ratio_currentpolicy['Likelyhood 50%'] = var_total2050_currentpolicy/df_ratio_currentpolicy['Likelyhood 50%']
df_ratio_currentpolicy['Likelyhood 67%'] = var_total2050_currentpolicy/df_ratio_currentpolicy['Likelyhood 67%']

# print(df_ratio_currentpolicy)
#   Unnamed: 0  Likelyhood 50%  Likelyhood 67%
# 0      1.5°C        2.966859        4.116804
# 1      1.6°C        2.090818        2.603273
# 2      1.7°C        1.500191        1.903469
# 3      1.8°C        1.237920        1.500191
# 4      1.9°C        0.917215        1.237920
# 5        2°C        0.879251        1.053706




# --------------
# netzero --- # cumulative
df_total_cumulative_netzero = df_total_annual_netzero.copy()
df_total_cumulative_netzero[year_columns] = df_total_cumulative_netzero[year_columns].cumsum(axis=1)

var_total2050_netzero = df_total_cumulative_netzero['2050'].values[0] / 1000
# print(var_total2050_netzero)
# 469.5038277453807

df_ratio_netzero = df_carbon_bugdet.copy()
df_ratio_netzero['Likelyhood 50%'] = var_total2050_netzero/df_ratio_netzero['Likelyhood 50%']
df_ratio_netzero['Likelyhood 67%'] = var_total2050_netzero/df_ratio_netzero['Likelyhood 67%']

# print(df_ratio_netzero)
#   Unnamed: 0  Likelyhood 50%  Likelyhood 67%
# 0      1.5°C        1.311463        1.819782
# 1      1.6°C        0.924220        1.150745
# 2      1.7°C        0.663141        0.841405
# 3      1.8°C        0.547207        0.663141
# 4      1.9°C        0.405444        0.547207
# 5        2°C        0.388662        0.465778










# In[]: FIND NEW GROWTH RATES
#############################

year_columns2 = [str(year) for year in range(2025, 2051)]


# In[]
#########################################################################
#  1. VERSION 1: NO CHANGES TO POSITIVE GROWTH --------------------------
#########################################################################

# create a reductino factor matric
df_reduction_netzero_v1 = df_ratio_netzero.copy()
df_reduction_netzero_v1.iloc[:, [1, 2]] = 1


########################################################
#  1.1 NET ZERO: 1.5C 50% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 50%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 50%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 3084
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2]
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2]
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2]
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 1.8520000000000014 in 1822 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v1['Likelyhood 50%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_50_secondary_change_v1 = df_temp_secondary_netzero_change
df_nz15_50_secondary_v1 = df_temp_secondary_netzero

df_nz15_50_primary_change_v1 = df_temp_primary_netzero_change
df_nz15_50_primary_v1 = df_temp_primary_netzero

df_nz15_50_residual_change_v1 = df_temp_residual_netzero_change
df_nz15_50_residual_v1 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  1.2 NET ZERO: 1.5C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 8115
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2]
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2]
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2]
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
#Converged at reduction_start = 3.653000000000003 in 3572 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v1['Likelyhood 67%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_67_secondary_change_v1 = df_temp_secondary_netzero_change
df_nz15_67_secondary_v1 = df_temp_secondary_netzero

df_nz15_67_primary_change_v1 = df_temp_primary_netzero_change
df_nz15_67_primary_v1 = df_temp_primary_netzero

df_nz15_67_residual_change_v1 = df_temp_residual_netzero_change
df_nz15_67_residual_v1 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  1.3 NET ZERO: 1.6C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][1] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][1] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 1492
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2]
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2]
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2]
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 1.404000000000001 in 1390 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v1['Likelyhood 67%'][1] = reduction_start


# --------------
# save the annual changes datasets
df_nz16_67_secondary_change_v1 = df_temp_secondary_netzero_change
df_nz16_67_secondary_v1 = df_temp_secondary_netzero

df_nz16_67_primary_change_v1 = df_temp_primary_netzero_change
df_nz16_67_primary_v1 = df_temp_primary_netzero

df_nz16_67_residual_change_v1 = df_temp_residual_netzero_change
df_nz16_67_residual_v1 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










# In[]
#########################################################################
#  2. VERSION 2: DECREASE POSITIVE GROWTH RATES -------------------------
#########################################################################

### see in iterations --- all (sec, pri, res) are divide by the reduction factor when annual growth rate is positive

# create a reductino factor matric
df_reduction_netzero_v2 = df_ratio_netzero.copy()
df_reduction_netzero_v2.iloc[:, [1, 2]] = 1


########################################################
#  2.1 NET ZERO: 1.5C 50% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 50%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 50%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 3084
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2] / reduction_start
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2] / reduction_start
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2] / reduction_start
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 1.7980000000000016 in 1768 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v2['Likelyhood 50%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_50_secondary_change_v2 = df_temp_secondary_netzero_change
df_nz15_50_secondary_v2 = df_temp_secondary_netzero

df_nz15_50_primary_change_v2 = df_temp_primary_netzero_change
df_nz15_50_primary_v2 = df_temp_primary_netzero

df_nz15_50_residual_change_v2 = df_temp_residual_netzero_change
df_nz15_50_residual_v2 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  2.2 NET ZERO: 1.5C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 8115
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2] / reduction_start
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2] / reduction_start
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2] / reduction_start
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 3.477000000000003 in 3396 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v2['Likelyhood 67%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_67_secondary_change_v2 = df_temp_secondary_netzero_change
df_nz15_67_secondary_v2 = df_temp_secondary_netzero

df_nz15_67_primary_change_v2 = df_temp_primary_netzero_change
df_nz15_67_primary_v2 = df_temp_primary_netzero

df_nz15_67_residual_change_v2 = df_temp_residual_netzero_change
df_nz15_67_residual_v2 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  2.3 NET ZERO: 1.6C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][1] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][1] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 1492
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2] / reduction_start
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2] / reduction_start
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2] / reduction_start
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 1.3780000000000012 in 1364 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v2['Likelyhood 67%'][1] = reduction_start


# --------------
# save the annual changes datasets
df_nz16_67_secondary_change_v2 = df_temp_secondary_netzero_change
df_nz16_67_secondary_v2 = df_temp_secondary_netzero

df_nz16_67_primary_change_v2 = df_temp_primary_netzero_change
df_nz16_67_primary_v2 = df_temp_primary_netzero

df_nz16_67_residual_change_v2 = df_temp_residual_netzero_change
df_nz16_67_residual_v2 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul






# In[]
#########################################################################
#  3. VERSION 3: NO GROWTH -------------------------
#########################################################################

# get regional path
# load datasets
temp_directory = r'C:\Users\panah\OneDrive\Desktop\Work\2 - RA - Climate fin\2 - output\script a - country codes'
#df_country_developing = pd.read_excel(temp_directory + r'\2 - developing.xlsx')
#df_country_emerging = pd.read_excel(temp_directory + r'\3 - emerging.xlsx')

df_country_unfccc = pd.read_excel('1 - input/Country Datasets/UNFCCC classification.xlsx')


# Net zero 
# primary
df_change_primary_netzero = pd.merge(df_change_primary_netzero, df_country_unfccc[['iso_3', 'classification']],
                     left_on='Region',
                     right_on='iso_3',
                     how='left')
df_change_primary_netzero['classification'] = df_change_primary_netzero['classification'].fillna('Developing')

# secondary
df_change_secondary_netzero = pd.merge(df_change_secondary_netzero, df_country_unfccc[['iso_3', 'classification']],
                     left_on='Region',
                     right_on='iso_3',
                     how='left')
df_change_secondary_netzero['classification'] = df_change_secondary_netzero['classification'].fillna('Developing')




# FOR RATIO --- V2
# primary
df_temp_netzero_v2_15_primary = df_nz15_50_primary_v2.copy()
df_temp_netzero_v2_15_primary = pd.merge(df_temp_netzero_v2_15_primary, df_country_unfccc[['iso_3', 'classification']],
                     left_on='Region',
                     right_on='iso_3',
                     how='left')
df_temp_netzero_v2_15_primary['classification'] = df_temp_netzero_v2_15_primary['classification'].fillna('Developing')

# secondary
df_temp_netzero_v2_15_secondary = df_nz15_50_secondary_v2.copy()
df_temp_netzero_v2_15_secondary = pd.merge(df_temp_netzero_v2_15_secondary, df_country_unfccc[['iso_3', 'classification']],
                     left_on='Region',
                     right_on='iso_3',
                     how='left')
df_temp_netzero_v2_15_secondary['classification'] = df_temp_netzero_v2_15_secondary['classification'].fillna('Developing')




# getting reional ratio values
# Step 1: Group emissions by 'classification' before computing ratios
df_temp_netzero_v2_15_primary = df_temp_netzero_v2_15_primary.groupby('classification')[year_columns].sum().reset_index()
df_temp_netzero_v2_15_secondary = df_temp_netzero_v2_15_secondary.groupby('classification')[year_columns].sum().reset_index()

# Step 2: Compute ratios against 2024
df_temp_primary_region_ratio = df_temp_netzero_v2_15_primary.copy()
df_temp_primary_region_ratio[year_columns] = df_temp_netzero_v2_15_primary[year_columns].div(df_temp_netzero_v2_15_primary['2024'], axis=0)

df_temp_secondary_region_ratio = df_temp_netzero_v2_15_secondary.copy()
df_temp_secondary_region_ratio[year_columns] = df_temp_secondary_region_ratio[year_columns].div(df_temp_netzero_v2_15_secondary['2024'], axis=0)



### see in iterations --- all (sec, pri, res) are divide by the reduction factor when annual growth rate is positive

# create a reductino factor matric
df_reduction_netzero_v3 = df_ratio_netzero.copy()
df_reduction_netzero_v3.iloc[:, [1, 2]] = 1



########################################################
#  3.1 NET ZERO: 1.5C 50% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 50%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 50%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 3084
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        0
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            zero_mask = df_temp_secondary_netzero[current_year] == 0
            
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            
            df_temp_secondary_netzero.loc[inf_mask, current_year] = 0
                      
            # Use map() to align classification with development_level dynamically in the loop
            scaling_factor = df_temp_secondary_netzero['classification'].map(
                df_temp_secondary_region_ratio.set_index('classification')[current_year]
            )
    
            # Apply np.maximum calculation
            df_temp_secondary_netzero.loc[zero_mask, current_year] = np.minimum(
                scaling_factor * df_temp_secondary_netzero['2024'],
                df_temp_secondary_netzero[previous_year]
            )

    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        0
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            zero_mask = df_temp_primary_netzero[current_year] == 0

            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]

            # Use map() to align classification with development_level dynamically in the loop
            scaling_factor = df_temp_primary_netzero['classification'].map(
                df_temp_primary_region_ratio.set_index('classification')[current_year]
            )
    
            # Apply np.maximum calculation
            df_temp_primary_netzero.loc[zero_mask, current_year] = np.minimum(
                scaling_factor * df_temp_primary_netzero['2024'],
                df_temp_primary_netzero[previous_year]
            )

    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        0
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
#Converged at reduction_start = 1.5860000000000014 in 1556 iterations

# --------------
# add the factor to the dataframe
df_reduction_netzero_v3['Likelyhood 50%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_50_secondary_change_v3 = df_temp_secondary_netzero_change
df_nz15_50_secondary_v3 = df_temp_secondary_netzero

df_nz15_50_primary_change_v3 = df_temp_primary_netzero_change
df_nz15_50_primary_v3 = df_temp_primary_netzero

df_nz15_50_residual_change_v3 = df_temp_residual_netzero_change
df_nz15_50_residual_v3 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  3.2 NET ZERO: 1.5C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][0] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][0] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 8115
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2] / reduction_start
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2] / reduction_start
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2] / reduction_start
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 3.477000000000003 in 3396 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v2['Likelyhood 67%'][0] = reduction_start


# --------------
# save the annual changes datasets
df_nz15_67_secondary_change_v2 = df_temp_secondary_netzero_change
df_nz15_67_secondary_v2 = df_temp_secondary_netzero

df_nz15_67_primary_change_v2 = df_temp_primary_netzero_change
df_nz15_67_primary_v2 = df_temp_primary_netzero

df_nz15_67_residual_change_v2 = df_temp_residual_netzero_change
df_nz15_67_residual_v2 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul










########################################################
#  3.3 NET ZERO: 1.6C 67% ------------------------------
########################################################

# --------------
# set total variable
target_value = df_carbon_bugdet['Likelyhood 67%'][1] * 1000
tolerance = 0.01 * target_value # 1% +- buffer zone

# Start with an initial guess --- % over carbon budget
reduction_start = df_ratio_netzero['Likelyhood 67%'][1] - 1

# Set initial bounds for the reduction factor --- it will iterate across all vallues by 0.001 increment --- exhaustive approach
lower_bound = round(reduction_start / 10, 3)
upper_bound = round(reduction_start * 10, 3)
print((upper_bound - lower_bound)/0.001)
# 1492
# this shows how many iterations will run

# Step size for iterating over 3 decimal places
step_size = 0.001

# set iteration variable
iteration = 0


# --------------
# Iterate over the range with the specified step size
for reduction_start in np.arange(lower_bound, upper_bound, step_size):
    iteration += 1

    ### secondary
    # this piece updates annual percent change values by reduction factor
    # if annual change is positive, leave as is
    # if annual change is negative, update, but lowest it can go is -100%
    df_temp_secondary_netzero = df_change_secondary_netzero.copy()
    df_temp_secondary_netzero[year_columns2] = np.where(
        df_change_secondary_netzero[year_columns2] < 0,
        (df_change_secondary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_secondary_netzero[year_columns2] / reduction_start
    )
    
    
    # save annual changes in a separate dataframe
    df_temp_secondary_netzero_change = df_temp_secondary_netzero.copy()
    
    
    # now compute a new annaul emissions data
    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_secondary_netzero.columns:
            inf_mask = np.isinf(df_temp_secondary_netzero[current_year])
            df_temp_secondary_netzero.loc[~inf_mask, current_year] = df_temp_secondary_netzero[previous_year] * (1 + df_temp_secondary_netzero[current_year] / 100)
            df_temp_secondary_netzero.loc[inf_mask, current_year] = df_ngfs_secondary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask


    ### primary
    df_temp_primary_netzero = df_change_primary_netzero.copy()
    df_temp_primary_netzero[year_columns2] = np.where(
        df_change_primary_netzero[year_columns2] < 0,
        (df_change_primary_netzero[year_columns2] * reduction_start).clip(lower=-100),
        df_change_primary_netzero[year_columns2] / reduction_start
    )


    df_temp_primary_netzero_change = df_temp_primary_netzero.copy()


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
    
        if current_year in df_temp_primary_netzero.columns:
            inf_mask = np.isinf(df_temp_primary_netzero[current_year])
            df_temp_primary_netzero.loc[~inf_mask, current_year] = df_temp_primary_netzero[previous_year] * (1 + df_temp_primary_netzero[current_year] / 100)
            df_temp_primary_netzero.loc[inf_mask, current_year] = df_ngfs_primary_netzero.loc[inf_mask, current_year]


    del i, current_year, previous_year, inf_mask



    ### residual 
    df_temp_residual_netzero = df_residual_netzero_change.copy()
    df_temp_residual_netzero[year_columns2] = np.where(
        df_residual_netzero_change[year_columns2] < 0,
        (df_residual_netzero_change[year_columns2] * reduction_start).clip(lower=-100),
        df_residual_netzero_change[year_columns2] / reduction_start
    )


    df_temp_residual_netzero_change = df_temp_residual_netzero.copy()
    df_temp_residual_netzero['2024'] = df_residual_netzero['2024'].values


    for i in range(1, len(year_columns)):
        previous_year = year_columns[i - 1]
        current_year = year_columns[i]
       
        df_temp_residual_netzero[current_year] = df_temp_residual_netzero[previous_year] * (1 + df_temp_residual_netzero[current_year] / 100)


    del i, current_year, previous_year

    

    # get total emissions --- cumulative across all --- secondary, extraction, residual 
    var_temp_total_secondary = df_temp_secondary_netzero[year_columns].sum().sum()
    var_temp_total_primary = df_temp_primary_netzero[year_columns].sum().sum()
    var_temp_total_residiaul = df_temp_residual_netzero[year_columns].sum().sum()
    var_temp_total_all = var_temp_total_primary + var_temp_total_secondary + var_temp_total_residiaul



    # when within tolerance/buffer --- stop
    if abs(var_temp_total_all - target_value) <= tolerance:
        print(f"Converged at reduction_start = {reduction_start} in {iteration} iterations")
        break

else:
    print("No suitable reduction factor found within the bounds.")
# Converged at reduction_start = 1.3780000000000012 in 1364 iterations


# --------------
# add the factor to the dataframe
df_reduction_netzero_v2['Likelyhood 67%'][1] = reduction_start


# --------------
# save the annual changes datasets
df_nz16_67_secondary_change_v2 = df_temp_secondary_netzero_change
df_nz16_67_secondary_v2 = df_temp_secondary_netzero

df_nz16_67_primary_change_v2 = df_temp_primary_netzero_change
df_nz16_67_primary_v2 = df_temp_primary_netzero

df_nz16_67_residual_change_v2 = df_temp_residual_netzero_change
df_nz16_67_residual_v2 = df_temp_residual_netzero


# --------------
del iteration, lower_bound, reduction_start, step_size, target_value, tolerance, upper_bound
del var_temp_total_all, var_temp_total_primary, var_temp_total_secondary, var_temp_total_residiaul








# In[]: CREATE CUMULATIVE EMISSIONS BY FUEL TYPE FOR SEC & PRI
##############################################################

########################
# VERSION 1 ------------
########################

# --------------
# CUMULATIVE

# NZ 1.5C 50%

# secondary
df_nz15_50_secondary_v1_total = df_nz15_50_secondary_v1.groupby('fuel_type')[year_columns].sum()
df_nz15_50_secondary_v1_total[year_columns] = df_nz15_50_secondary_v1_total[year_columns].cumsum(axis=1)

# primary
df_nz15_50_primary_v1_total = df_nz15_50_primary_v1.groupby('fuel_type')[year_columns].sum()
df_nz15_50_primary_v1_total[year_columns] = df_nz15_50_primary_v1_total[year_columns].cumsum(axis=1)

# residual
df_nz15_50_residual_v1_total = df_nz15_50_residual_v1.copy()
df_nz15_50_residual_v1_total[year_columns] = df_nz15_50_residual_v1[year_columns].cumsum(axis=1) 


# total
df_nz15_50_total_v1 = df_nz15_50_secondary_v1_total[year_columns].sum() + \
                      df_nz15_50_primary_v1_total[year_columns].sum() + \
                      df_nz15_50_residual_v1_total[year_columns]


# --------------
# NZ 1.5C 67%

# secondary
df_nz15_67_secondary_v1_total = df_nz15_67_secondary_v1.groupby('fuel_type')[year_columns].sum()
df_nz15_67_secondary_v1_total[year_columns] = df_nz15_67_secondary_v1_total[year_columns].cumsum(axis=1)

# primary
df_nz15_67_primary_v1_total = df_nz15_67_primary_v1.groupby('fuel_type')[year_columns].sum()
df_nz15_67_primary_v1_total[year_columns] = df_nz15_67_primary_v1_total[year_columns].cumsum(axis=1)

# residual
df_nz15_67_residual_v1_total = df_nz15_67_residual_v1.copy()
df_nz15_67_residual_v1_total[year_columns] = df_nz15_67_residual_v1_total[year_columns].cumsum(axis=1) 

# total
df_nz15_67_total_v1 = df_nz15_67_secondary_v1_total[year_columns].sum() + \
                      df_nz15_67_primary_v1_total[year_columns].sum() + \
                      df_nz15_67_residual_v1_total[year_columns]


# --------------
# NZ 1.6C 67%

# secondary
df_nz16_67_secondary_v1_total = df_nz16_67_secondary_v1.groupby('fuel_type')[year_columns].sum()
df_nz16_67_secondary_v1_total[year_columns] = df_nz16_67_secondary_v1_total[year_columns].cumsum(axis=1)

# primary
df_nz16_67_primary_v1_total = df_nz16_67_primary_v1.groupby('fuel_type')[year_columns].sum()
df_nz16_67_primary_v1_total[year_columns] = df_nz16_67_primary_v1_total[year_columns].cumsum(axis=1)

# residual
df_nz16_67_residual_v1_total = df_nz16_67_residual_v1.copy()
df_nz16_67_residual_v1_total[year_columns] = df_nz16_67_residual_v1_total[year_columns].cumsum(axis=1) 

# total
df_nz16_67_total_v1 = df_nz16_67_secondary_v1_total[year_columns].sum() + \
                      df_nz16_67_primary_v1_total[year_columns].sum() + \
                      df_nz16_67_residual_v1_total[year_columns]





# --------------
# ANNUAL

# NZ 1.5C 50%

# secondary
df_nz15_50_secondary_v1_annual = df_nz15_50_secondary_v1.groupby('fuel_type')[year_columns].sum()

# primary
df_nz15_50_primary_v1_annual = df_nz15_50_primary_v1.groupby('fuel_type')[year_columns].sum()

# total
df_nz15_50_total_v1_annual = df_nz15_50_secondary_v1_annual[year_columns].sum() + \
                      df_nz15_50_primary_v1_annual[year_columns].sum() + \
                      df_nz15_50_residual_v1[year_columns]


# --------------
# NZ 1.5C 67%

# secondary
df_nz15_67_secondary_v1_annual = df_nz15_67_secondary_v1.groupby('fuel_type')[year_columns].sum()

# primary
df_nz15_67_primary_v1_annual = df_nz15_67_primary_v1.groupby('fuel_type')[year_columns].sum()

# total
df_nz15_67_total_v1_annual = df_nz15_67_secondary_v1_annual[year_columns].sum() + \
                      df_nz15_67_primary_v1_annual[year_columns].sum() + \
                      df_nz15_67_residual_v1[year_columns]


# --------------
# NZ 1.6C 67%

# secondary
df_nz16_67_secondary_v1_annual = df_nz16_67_secondary_v1.groupby('fuel_type')[year_columns].sum()

# primary
df_nz16_67_primary_v1_annual = df_nz16_67_primary_v1.groupby('fuel_type')[year_columns].sum()

# total
df_nz16_67_total_v1_annual = df_nz16_67_secondary_v1_annual[year_columns].sum() + \
                      df_nz16_67_primary_v1_annual[year_columns].sum() + \
                      df_nz16_67_residual_v1[year_columns]
                      
                      
                      
                      
########################
# VERSION 2 ------------
########################

# --------------
# NZ 1.5C 50%

# secondary
df_nz15_50_secondary_v2_total = df_nz15_50_secondary_v2.groupby('fuel_type')[year_columns].sum()
df_nz15_50_secondary_v2_total[year_columns] = df_nz15_50_secondary_v2_total[year_columns].cumsum(axis=1)

# primary
df_nz15_50_primary_v2_total = df_nz15_50_primary_v2.groupby('fuel_type')[year_columns].sum()
df_nz15_50_primary_v2_total[year_columns] = df_nz15_50_primary_v2_total[year_columns].cumsum(axis=1)

# residual
df_nz15_50_residual_v2_total = df_nz15_50_residual_v2.copy()
df_nz15_50_residual_v2_total[year_columns] = df_nz15_50_residual_v2[year_columns].cumsum(axis=1) 

# total
df_nz15_50_total_v2 = df_nz15_50_secondary_v2_total[year_columns].sum() + \
                      df_nz15_50_primary_v2_total[year_columns].sum() + \
                      df_nz15_50_residual_v2_total[year_columns]


# --------------
# NZ 1.5C 67%

# secondary
df_nz15_67_secondary_v2_total = df_nz15_67_secondary_v2.groupby('fuel_type')[year_columns].sum()
df_nz15_67_secondary_v2_total[year_columns] = df_nz15_67_secondary_v2_total[year_columns].cumsum(axis=1)

# primary
df_nz15_67_primary_v2_total = df_nz15_67_primary_v2.groupby('fuel_type')[year_columns].sum()
df_nz15_67_primary_v2_total[year_columns] = df_nz15_67_primary_v2_total[year_columns].cumsum(axis=1)

# residual
df_nz15_67_residual_v2_total = df_nz15_67_residual_v2.copy()
df_nz15_67_residual_v2_total[year_columns] = df_nz15_67_residual_v2_total[year_columns].cumsum(axis=1) 

# total
df_nz15_67_total_v2 = df_nz15_67_secondary_v2_total[year_columns].sum() + \
                      df_nz15_67_primary_v2_total[year_columns].sum() + \
                      df_nz15_67_residual_v2_total[year_columns]
                      

# --------------
# NZ 1.6C 67%

# secondary
df_nz16_67_secondary_v2_total = df_nz16_67_secondary_v2.groupby('fuel_type')[year_columns].sum()
df_nz16_67_secondary_v2_total[year_columns] = df_nz16_67_secondary_v2_total[year_columns].cumsum(axis=1)

# primary
df_nz16_67_primary_v2_total = df_nz16_67_primary_v2.groupby('fuel_type')[year_columns].sum()
df_nz16_67_primary_v2_total[year_columns] = df_nz16_67_primary_v2_total[year_columns].cumsum(axis=1)

# residual
df_nz16_67_residual_v2_total = df_nz16_67_residual_v2.copy()
df_nz16_67_residual_v2_total[year_columns] = df_nz16_67_residual_v2_total[year_columns].cumsum(axis=1) 

# total
df_nz16_67_total_v2 = df_nz16_67_secondary_v2_total[year_columns].sum() + \
                      df_nz16_67_primary_v2_total[year_columns].sum() + \
                      df_nz16_67_residual_v2_total[year_columns]










# In[11]


#####################################################################
#####################################################################
#####################################################################
#####################################################################
########## PLOTS PLOTS PLOTS PLOTS PLOTS PLOTS PLOTS ################
#####################################################################
#####################################################################
#####################################################################
#####################################################################



# In[6]:  PREPARE DATASETS
###########################

# --------------
# Ensure all DataFrames have the same year columns
common_years = df_nz15_50_primary_v1.columns.intersection(df_nz15_50_secondary_v1.columns).intersection(df_nz15_50_residual_v1.columns)


# --------------
# Align all DataFrames to have the same year columns

# --------------
# VERSION 1
# CUMULATIVE
# NZ 1.5C 50%
df_nz15_50_secondary_v1_total = df_nz15_50_secondary_v1_total[common_years]
df_nz15_50_primary_v1_total = df_nz15_50_primary_v1_total[common_years]
df_nz15_50_residual_v1_total = df_nz15_50_residual_v1_total[common_years]

# NZ 1.5C 67%
df_nz15_67_secondary_v1_total = df_nz15_67_secondary_v1_total[common_years]
df_nz15_67_primary_v1_total = df_nz15_67_primary_v1_total[common_years]
df_nz15_67_residual_v1_total = df_nz15_67_residual_v1_total[common_years]

# NZ 1.6C 67%
df_nz16_67_secondary_v1_total = df_nz16_67_secondary_v1_total[common_years]
df_nz16_67_primary_v1_total = df_nz16_67_primary_v1_total[common_years]
df_nz16_67_residual_v1_total = df_nz16_67_residual_v1_total[common_years]



# ANNUAL
# NZ 1.5C 50%
df_nz15_50_secondary_v1_annual = df_nz15_50_secondary_v1_annual[common_years]
df_nz15_50_primary_v1_annual = df_nz15_50_primary_v1_annual[common_years]
df_nz15_50_residual_v1 = df_nz15_50_residual_v1[common_years]

# NZ 1.5C 67%
df_nz15_67_secondary_v1_annual = df_nz15_67_secondary_v1_annual[common_years]
df_nz15_67_primary_v1_annual  = df_nz15_67_primary_v1_annual[common_years]
df_nz15_67_residual_v1 = df_nz15_67_residual_v1[common_years]

# NZ 1.6C 67%
df_nz16_67_secondary_v1_annual  = df_nz16_67_secondary_v1_annual[common_years]
df_nz16_67_primary_v1_annual  = df_nz16_67_primary_v1_annual[common_years]
df_nz16_67_residual_v1 = df_nz16_67_residual_v1[common_years]





# --------------
# VERSION 2
# CUMULATIVE
# NZ 1.5C 50%
df_nz15_50_secondary_v2_total = df_nz15_50_secondary_v2_total[common_years]
df_nz15_50_primary_v2_total = df_nz15_50_primary_v2_total[common_years]
df_nz15_50_residual_v2_total = df_nz15_50_residual_v2_total[common_years]

# NZ 1.5C 67%
df_nz15_67_secondary_v2_total = df_nz15_67_secondary_v2_total[common_years]
df_nz15_67_primary_v2_total = df_nz15_67_primary_v2_total[common_years]
df_nz15_67_residual_v2_total = df_nz15_67_residual_v2_total[common_years]

# NZ 1.6C 67%
df_nz16_67_secondary_v2_total = df_nz16_67_secondary_v2_total[common_years]
df_nz16_67_primary_v2_total = df_nz16_67_primary_v2_total[common_years]
df_nz16_67_residual_v2_total = df_nz16_67_residual_v2_total[common_years]


# --------------
# Define colors for extraction and power components
extraction_colors = {'Coal': '#991f17', 'Gas': '#b04238', 'Oil': '#c86558'}
power_colors = {'Coal': '#255e7e', 'Gas': '#3d708f', 'Oil': '#6996b3'}










# In[8]:

##################################################################################################
##################### VERSION 1: NO CHANGES TO POSITIVE ANNUAL GROWTH RATES ######################
##################################################################################################

# --------------
### CUMULATIVE

# NZ 1.5C 50%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_nz15_50_primary_v1_total
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_50_primary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_primary_v1_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_primary_v1_total.loc[fuel]

# Plot the stacked areas for components of df_nz15_50_secondary_v1_total on top of df_nz15_50_primary_v1_total
for fuel in df_nz15_50_secondary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_secondary_v1_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_secondary_v1_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_50_residual_v1_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_50_total_v1.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()





# --------------
# NZ 1.5C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_67_primary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_primary_v1_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_primary_v1_total.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz15_67_secondary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_secondary_v1_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_secondary_v1_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_67_residual_v1_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_67_total_v1.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()





# --------------
# NZ 1.6C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz16_67_primary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_primary_v1_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_primary_v1_total.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz16_67_secondary_v1_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_secondary_v1_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_secondary_v1_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz16_67_residual_v1_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz16_67_total_v1.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()










# --------------
# ANNUAL

# NZ 1.5C 50%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_50_primary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_primary_v1_annual.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_primary_v1_annual.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz15_50_secondary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_secondary_v1_annual.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_secondary_v1_annual.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_50_residual_v1.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_50_total_v1_annual.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Annual Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Annual emissions pathway consistent with 50% likelyhood of limiting warming to 1.5°C', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper right', fontsize=12)


plt.show()





# --------------
# NZ 1.5C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_67_primary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_primary_v1_annual.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_primary_v1_annual.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz15_67_secondary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_secondary_v1_annual.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_secondary_v1_annual.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_67_residual_v1.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_67_total_v1_annual.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Annual Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Annual emissions pathway consistent with 67% likelyhood of limiting warming to 1.5°C', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper right', fontsize=12)


plt.show()





# --------------
# NZ 1.6C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz16_67_primary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_primary_v1_annual.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_primary_v1_annual.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz16_67_secondary_v1_annual.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_secondary_v1_annual.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_secondary_v1_annual.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz16_67_residual_v1.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz16_67_total_v1_annual.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Annual Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Annual emissions pathway consistent with 67% likelyhood of limiting warming to 1.6°C', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper right', fontsize=12)


plt.show()










# In[]
##################################################################################################
##################### VERSION 2: POSITIVE ANNUAL GROWTH RATES REDUCED ############################
##################################################################################################

# --------------
# NZ 1.5C 50%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_50_primary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_primary_v2_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_primary_v2_total.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz15_50_secondary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_50_secondary_v2_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_50_secondary_v2_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_50_residual_v2_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_50_total_v2.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()





# --------------
# NZ 1.5C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz15_67_primary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_primary_v2_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_primary_v2_total.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz15_67_secondary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz15_67_secondary_v2_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz15_67_secondary_v2_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz15_67_residual_v2_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz15_67_total_v2.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()





# --------------
# NZ 1.6C 67%
# Plotting
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the stacked areas for components of df_extraction_annual_currentpolicy
bottom = pd.Series(0, index=common_years)
for fuel in df_nz16_67_primary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_primary_v2_total.loc[fuel], 
                    label=f'{fuel} (extraction)', color=extraction_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_primary_v2_total.loc[fuel]

# Plot the stacked areas for components of df_power_annual_currentpolicy on top of df_extraction_annual_currentpolicy
for fuel in df_nz16_67_secondary_v2_total.index:
    ax.fill_between(common_years, bottom, bottom + df_nz16_67_secondary_v2_total.loc[fuel], 
                    label=f'{fuel} (power)', color=power_colors[fuel], alpha=0.7)
    bottom += df_nz16_67_secondary_v2_total.loc[fuel]

# Plot the stacked area for df_residual with a dotted texture
ax.fill_between(common_years, bottom, bottom + df_nz16_67_residual_v2_total.loc[6].values, # 6 because index value is 6
                label='Other energy sources', color='#a4a2a8', alpha=0.5, hatch='.')

# # Plot the line for df_total_annual_currentpolicy
ax.plot(common_years, df_nz16_67_total_v2.values.flatten(), 
        color='black', linewidth=2, label='Total energy emissions')

# Customize the x-axis to show ticks every 5 years
plt.xticks([str(year) for year in range(2025, 2051, 5)])

# Formatter function to convert values to thousands
def thousands_formatter(x, pos):
    return f'{int(x/1000)}'    # the values are in Mt, but diving the axis by 1000 to show in Gt

# Set y-axis formatter to display values in thousands
ax = plt.gca()
ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(258000, 358000, color='#aebe8b', alpha=0.5)
plt.text(2, 275000, '1.5°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Add a shaded region between 400 and 580 on the y-axis
plt.axhspan(408000, 508000, color='#e7daaf', alpha=0.3)
plt.text(18, 485000, 'Carbon budget: 1.6°C warming', color='black', fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.5))

# Adding labels and legend
plt.xlabel('Year',fontsize = 15 )
plt.ylabel('GtCO2', fontsize = 15)
plt.title('Cumulative Emissions from Energy Sector', fontsize=25, pad=60)
plt.text(0.5, 1.05, 'Emissions from current power plants in operation are projected using modified growth rates \n from NGFS GCAM6 model to align cumulative emissions with carbon budget boundaries', transform=ax.transAxes, ha='center', fontsize=12)
plt.text(0.5, 1.01, 'Carbon budget range represents 50%-67% likelyhood for global warming', transform=ax.transAxes, ha='center', fontsize=12)

ax.legend(loc='upper left', fontsize=12)


plt.show()










# In[]
# export data

# --------------
# redcution factors
df_reduction_netzero_v1.to_excel('2 - output/script 4.2/1.1 - Net Zero - Reduction factors - v1 - positive growth no change.xlsx', index=False)
df_reduction_netzero_v2.to_excel('2 - output/script 4.2/1.2 - Net Zero - Reduction factors - v2 - positive growth reduced.xlsx', index=False)

# cumulative emissions ratios
df_ratio_netzero.to_excel('2 - output/script 4.2/1.3 - Emissions ratios to carbon budget - Net Zero.xlsx', index=False)
df_ratio_currentpolicy.to_excel('2 - output/script 4.2/1.4 - Emissions ratios to carbon budget - Current Policy.xlsx', index=False)


# --------------
# redisuals
df_residual_netzero.to_excel('2 - output/script 4.2/2.1 - Residuals - Net Zero - annual emissions.xlsx', index=False)
df_residual_netzero_change.to_excel('2 - output/script 4.2/2.2 - Residuals - Net Zero - change.xlsx', index=False)

df_residual_currentpolicy.to_excel('2 - output/script 4.2/2.3 - Residuals - Current Policy - annual emissions.xlsx', index=False)
df_residual_currentpolicy_change.to_excel('2 - output/script 4.2/2.4 - Residuals - Current Policy - change.xlsx', index=False)
                                    

# --------------
# VERSION 1

### Net zero 1.5C 50%
# emissions
df_nz15_50_secondary_v1.to_excel('2 - output/script 4.2/3.1 - NZ-15-50 - v1 - Secondary - annual.xlsx')
df_nz15_50_primary_v1.to_excel('2 - output/script 4.2/3.2 - NZ-15-50 - v1 - Primary - annual.xlsx')
df_nz15_50_residual_v1.to_excel('2 - output/script 4.2/3.3 - NZ-15-50 - v1 - Residual - annual.xlsx')
df_nz15_50_total_v1_annual.to_excel('2 - output/script 4.2/3 - NZ-15-50 - v1 - Total - annual.xlsx')

# change
df_nz15_50_secondary_change_v1.to_excel('2 - output/script 4.2/3.4 - NZ-15-50 - v1 - Secondary - Change.xlsx', index=False)
df_nz15_50_primary_change_v1.to_excel('2 - output/script 4.2/3.5 - NZ-15-50 - v1 - Primary - Change.xlsx', index=False)
df_nz15_50_residual_change_v1.to_excel('2 - output/script 4.2/3.6 - NZ-15-50 - v1 - Residual - Change.xlsx', index=False)

# cumulative
df_nz15_50_secondary_v1_total.to_excel('2 - output/script 4.2/3.7 - NZ-15-50 - v1 - Secondary - cumulative.xlsx')
df_nz15_50_primary_v1_total.to_excel('2 - output/script 4.2/3.8 - NZ-15-50 - v1 - Primary - cumulative.xlsx')
df_nz15_50_residual_v1_total.to_excel('2 - output/script 4.2/3.9 - NZ-15-50 - v1 - Residual - cumulative.xlsx')
df_nz15_50_total_v1.to_excel('2 - output/script 4.2/3.10 - NZ-15-50 - v1 - Total - cumulative.xlsx')


### Net zero 1.5C 67%
# emissions
df_nz15_67_secondary_v1.to_excel('2 - output/script 4.2/4.1 - NZ-15-67 - v1 - Secondary - annual.xlsx', index=False)
df_nz15_67_primary_v1.to_excel('2 - output/script 4.2/4.2 - NZ-15-67 - v1 - Primary - annual.xlsx', index=False)
df_nz15_67_residual_v1.to_excel('2 - output/script 4.2/4.3 - NZ-15-67 - v1 - Residual - annual.xlsx', index=False)

# change
df_nz15_67_secondary_change_v1.to_excel('2 - output/script 4.2/4.4 - NZ-15-67 - v1 - Secondary - Change.xlsx', index=False)
df_nz15_67_primary_change_v1.to_excel('2 - output/script 4.2/4.5 - NZ-15-67 - v1 - Primary - Change.xlsx', index=False)
df_nz15_67_residual_change_v1.to_excel('2 - output/script 4.2/4.6 - NZ-15-67 - v1 - Residual - Change.xlsx', index=False)

# cumulative
df_nz15_67_secondary_v1_total.to_excel('2 - output/script 4.2/4.7 - NZ-15-67 - v1 - Secondary - cumulative.xlsx', index=False)
df_nz15_67_primary_v1_total.to_excel('2 - output/script 4.2/4.8 - NZ-15-67 - v1 - Primary - cumulative.xlsx', index=False)
df_nz15_67_residual_v1_total.to_excel('2 - output/script 4.2/4.9 - NZ-15-67 - v1 - Residual - cumulative.xlsx', index=False)
df_nz15_67_total_v1.to_excel('2 - output/script 4.2/4.10 - NZ-15-67 - v1 - Total - cumulative.xlsx', index=False)


### Net zero 1.6C 67%
# emissions
df_nz16_67_secondary_v1.to_excel('2 - output/script 4.2/5.1 - NZ-16-67 - v1 - Secondary - annual.xlsx', index=False)
df_nz16_67_primary_v1.to_excel('2 - output/script 4.2/5.2 - NZ-16-67 - v1 - Primary - annual.xlsx', index=False)
df_nz16_67_residual_v1.to_excel('2 - output/script 4.2/5.3 - NZ-16-67 - v1 - Residual - annual.xlsx', index=False)

# change
df_nz16_67_secondary_change_v1.to_excel('2 - output/script 4.2/5.4 - NZ-16-67 - v1 - Secondary - Change.xlsx', index=False)
df_nz16_67_primary_change_v1.to_excel('2 - output/script 4.2/5.5 - NZ-16-67 - v1 - Primary - Change.xlsx', index=False)
df_nz16_67_residual_change_v1.to_excel('2 - output/script 4.2/5.6 - NZ-16-67 - v1 - Residual - Change.xlsx', index=False)

# cumulative
df_nz16_67_secondary_v1_total.to_excel('2 - output/script 4.2/5.7 - NZ-16-67 - v1 - Secondary - cumulative.xlsx', index=False)
df_nz16_67_primary_v1_total.to_excel('2 - output/script 4.2/5.8 - NZ-16-67 - v1 - Primary - cumulative.xlsx', index=False)
df_nz16_67_residual_v1_total.to_excel('2 - output/script 4.2/5.9 - NZ-16-67 - v1 - Residual - cumulative.xlsx', index=False)
df_nz16_67_total_v1.to_excel('2 - output/script 4.2/5.10 - NZ-16-67 - v1 - Total - cumulative.xlsx', index=False)


# --------------
# VERSION 2

### Net zero 1.5C 50%
# emissions
df_nz15_50_secondary_v2.to_excel('2 - output/script 4.2/6.1 - NZ-15-50 - v2 - Secondary - annual.xlsx', index=False)
df_nz15_50_primary_v2.to_excel('2 - output/script 4.2/6.2 - NZ-15-50 - Primary - v2 - annual.xlsx', index=False)
df_nz15_50_residual_v2.to_excel('2 - output/script 4.2/6.3 - NZ-15-50 - Residual - v2 - annual.xlsx', index=False)

# change
df_nz15_50_secondary_change_v2.to_excel('2 - output/script 4.2/6.4 - NZ-15-50 - v2 - Secondary - Change.xlsx', index=False)
df_nz15_50_primary_change_v2.to_excel('2 - output/script 4.2/6.5 - NZ-15-50 - v2 - Primary - Change.xlsx', index=False)
df_nz15_50_residual_change_v2.to_excel('2 - output/script 4.2/6.6 - NZ-15-50 - v2 - Residual - Change.xlsx', index=False)

# cumulative
df_nz15_50_secondary_v2_total.to_excel('2 - output/script 4.2/6.7 - NZ-15-50 - v2 - Secondary - cumulative.xlsx', index=False)
df_nz15_50_primary_v2_total.to_excel('2 - output/script 4.2/6.8 - NZ-15-50 - v2 - Primary - cumulative.xlsx', index=False)
df_nz15_50_residual_v2_total.to_excel('2 - output/script 4.2/6.9 - NZ-15-50 - v2 - Residual - cumulative.xlsx', index=False)
df_nz15_50_total_v2.to_excel('2 - output/script 4.2/6.10 - NZ-15-50 - v2 - Total - cumulative.xlsx', index=False)


### Net zero 1.5C 67%
# emissions
df_nz15_67_secondary_v2.to_excel('2 - output/script 4.2/7.1 - NZ-15-67 - v2 - Secondary - annual.xlsx', index=False)
df_nz15_67_primary_v2.to_excel('2 - output/script 4.2/7.2 - NZ-15-67 - v2 - Primary - annual.xlsx', index=False)
df_nz15_67_residual_v2.to_excel('2 - output/script 4.2/7.3 - NZ-15-67 - v2 - Residual - annual.xlsx', index=False)

# change
df_nz15_67_secondary_change_v2.to_excel('2 - output/script 4.2/7.4 - NZ-15-67 - v2 - Secondary - Change.xlsx', index=False)
df_nz15_67_primary_change_v2.to_excel('2 - output/script 4.2/7.5 - NZ-15-67 - v2 - Primary - Change.xlsx', index=False)
df_nz15_67_residual_change_v2.to_excel('2 - output/script 4.2/7.6 - NZ-15-67 - v2 - Residual - Change.xlsx', index=False)

# cumulative
df_nz15_67_secondary_v2_total.to_excel('2 - output/script 4.2/7.7 - NZ-15-67 - v2 - Secondary - cumulative.xlsx', index=False)
df_nz15_67_primary_v2_total.to_excel('2 - output/script 4.2/7.8 - NZ-15-67 - v2 - Primary - cumulative.xlsx', index=False)
df_nz15_67_residual_v2_total.to_excel('2 - output/script 4.2/7.9 - NZ-15-67 - v2 - Residual - cumulative.xlsx', index=False)
df_nz15_67_total_v2.to_excel('2 - output/script 4.2/7.10 - NZ-15-67 - v2 - Total - cumulative.xlsx', index=False)


### Net zero 1.6C 67%
# emissions
df_nz16_67_secondary_v2.to_excel('2 - output/script 4.2/8.1 - NZ-16-67 - v2 - Secondary - annual.xlsx', index=False)
df_nz16_67_primary_v2.to_excel('2 - output/script 4.2/8.2 - NZ-16-67 - v2 - Primary - annual.xlsx', index=False)
df_nz16_67_residual_v2.to_excel('2 - output/script 4.2/8.3 - NZ-16-67 - v2 - Residual - annual.xlsx', index=False)

# change
df_nz16_67_secondary_change_v2.to_excel('2 - output/script 4.2/8.4 - NZ-16-67 - v2 - Secondary - Change.xlsx', index=False)
df_nz16_67_primary_change_v2.to_excel('2 - output/script 4.2/8.5 - NZ-16-67 - v2 - Primary - Change.xlsx', index=False)
df_nz16_67_residual_change_v2.to_excel('2 - output/script 4.2/8.6 - NZ-16-67 - v2 - Residual - Change.xlsx', index=False)

# cumulative
df_nz16_67_secondary_v2_total.to_excel('2 - output/script 4.2/8.7 - NZ-16-67 - v2 - Secondary - cumulative.xlsx', index=False)
df_nz16_67_primary_v2_total.to_excel('2 - output/script 4.2/8.8 - NZ-16-67 - v2 - Primary - cumulative.xlsx', index=False)
df_nz16_67_residual_v2_total.to_excel('2 - output/script 4.2/8.9 - NZ-16-67 - v2 - Residual - cumulative.xlsx', index=False)
df_nz16_67_total_v2.to_excel('2 - output/script 4.2/8.10 - NZ-16-67 - v2 -Total - cumulative.xlsx', index=False)



# --------------
# VERSION 3

### Net zero 1.5C 50%
# emissions
df_nz15_50_secondary_v3.to_excel('2 - output/script 4.2/10.1 - NZ-15-50 - v3 - Secondary - annual.xlsx', index=False)
df_nz15_50_primary_v3.to_excel('2 - output/script 4.2/10.2 - NZ-15-50 - Primary - v3 - annual.xlsx', index=False)
df_nz15_50_residual_v3.to_excel('2 - output/script 4.2/10.3 - NZ-15-50 - Residual - v3 - annual.xlsx', index=False)




### Current policy & Net zero - by country
# emissions
df_emissions_secondary_currentpolicy.to_excel('2 - output/script 4.2/9.1 - Current policy - Secondary - annual.xlsx', index=False)
df_emissions_secondary_netzero.to_excel('2 - output/script 4.2/9.2 - Net zero - Secondary - annual.xlsx', index=False)

