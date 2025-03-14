# In[1]:
# Date: July 28, 2024
# Project: Applying NGFS trends to FA data - Secondary energy / Power sector
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
import matplotlib.cm as cm





# In[]
# Directory & load data

# ---------------
directory = r'C:\Users\panah\OneDrive\Desktop\Work\3 - NGFS analysis'
os.chdir(directory)
del directory


# --------------
# load power plants data
df_power_coal = pd.read_excel('2 - output\script 1/2.1 - power - coal.xlsx')   
df_power_gas = pd.read_excel('2 - output\script 1/2.2 - power - gas.xlsx')   
df_power_oil = pd.read_excel('2 - output\script 1/2.3 - power - oil.xlsx')   
df_power = pd.read_excel('2 - output\script 1/1.1 - power - overall.xlsx')   


# -----------------------
# load emimssions & growth projections from NGFS
df_gcam_emissions_secondary = pd.read_excel('2 - output/script 2/2.3 - GCAM - emissions - secondary.xlsx')
df_gcam_emissions_secondary_change = pd.read_excel('2 - output/script 2/3.2 - GCAM - change - secondary.xlsx')





# In[]
# set year variables

# ---------------
# set year columns
year_columns = [str(year) for year in range(2024, 2051)]




    
# In[]
# get power by source and country for mapping

# ---------------
# by country for each power source
df_power_coal = df_power_coal.groupby(['standard_iso3'])['annual_co2_calc'].sum()
df_power_coal = df_power_coal.reset_index()

df_power_gas = df_power_gas.groupby(['standard_iso3'])['annual_co2_calc'].sum()
df_power_gas = df_power_gas.reset_index()

df_power_oil = df_power_oil.groupby(['standard_iso3'])['annual_co2_calc'].sum()
df_power_oil = df_power_oil.reset_index()





# In[]
# check for countries across datasets: NGFS vs FA

# -------------------
# get list of NGFS countries
df_ngfs_countries = df_gcam_emissions_secondary_change[df_gcam_emissions_secondary_change['Scenario'] == 'Current Policies']
df_ngfs_countries = df_ngfs_countries[df_ngfs_countries['Variable'].str.contains('Secondary')]
df_ngfs_countries = df_ngfs_countries[['Region', 'Variable', '2024']]

df_ngfs_countries = df_ngfs_countries.pivot(index='Region', columns='Variable', values='2024')
df_ngfs_countries.reset_index(inplace = True)


# -------------------
# Get list of FA countries
df_fa_countries = df_power[['standard_iso3']].drop_duplicates()
df_fa_countries.reset_index(drop=True, inplace = True)


# Add FA data into the country list above
df_fa_countries = pd.merge(df_fa_countries,df_power_coal,
                           on='standard_iso3',
                           how='left')

df_fa_countries = pd.merge(df_fa_countries,df_power_gas,
                           on='standard_iso3',
                           how='left')

df_fa_countries = pd.merge(df_fa_countries,df_power_oil,
                           on='standard_iso3',
                           how='left')


# -------------------
# merge with NGFS data
df_merged_countries_raw = pd.merge(df_fa_countries, df_ngfs_countries,
                               left_on='standard_iso3',
                               right_on='Region',
                               how='outer')

# df names
df_merged_countries_raw.columns = ['country_FA', 'coal_FA', 'gas_FA', 'oil_FA', 'country_NGFS',
                               'coal_NGFS', 'gas_NGFS', 'oil_NGFS']





# In[]
# get new merged country dataframe

# -------------------
# get new dataframe
df_merged_countries_edited = df_merged_countries_raw.copy()

# remove 'unknown' from FA country list
df_merged_countries_edited = df_merged_countries_edited[df_merged_countries_edited['country_FA'] != 'unknown']

# for countries in FA that dont have NGFS equivalent, set them as 'Downscaling|Countries without IEA statistics'
df_merged_countries_edited['country_NGFS'] = df_merged_countries_edited['country_NGFS'].replace(np.nan, 'Downscaling|Countries without IEA statistics')

# remove NA's in FA country list
df_merged_countries_edited = df_merged_countries_edited[df_merged_countries_edited['country_FA'].notna()]

# group by NGFS countries --- Now all FA countries have an equivalent from NGFS
df_merged_countries_edited = df_merged_countries_edited.groupby('country_NGFS')[['coal_FA', 'gas_FA', 'oil_FA']].sum()
df_merged_countries_edited.reset_index(inplace = True)





# In[]
# use mapping to add emissions values to year 2024

# ---------------
# create df for FA grwoth projetions; remove 2020-2023 years --- i.e start from 2024
df_fa_emissions_secondary = df_gcam_emissions_secondary_change.drop(columns = ['2020', '2021', '2022', '2023']) # removing 2020-2023
df_fa_emissions_secondary["2024"] = 0 # set all 2024 values to zero --- these will be filled by FA data


# -------------------
# add FA value for 2024 for each fuel type
# coal
# Step 1: Filter to include only rows where 'Variable' contains "coal"
df_growth_secondary_coal = df_gcam_emissions_secondary_change[df_gcam_emissions_secondary_change['fuel_type'] == "Coal"]

# Step 2: Create a mapping Series
co2_mapping = df_merged_countries_edited.set_index('country_NGFS')['coal_FA']

# Step 3: Map and substitute values in the '2024' column for the filtered DataFrame
df_growth_secondary_coal['2024'] = df_growth_secondary_coal['Region'].map(co2_mapping)

# Step 4: Update the original DataFrame
df_fa_emissions_secondary.update(df_growth_secondary_coal)


# -------------------
# gas
df_growth_secondary_gas = df_gcam_emissions_secondary_change[df_gcam_emissions_secondary_change['fuel_type'] == "Gas"]
co2_mapping = df_merged_countries_edited.set_index('country_NGFS')['gas_FA']
df_growth_secondary_gas['2024'] = df_growth_secondary_gas['Region'].map(co2_mapping)
df_fa_emissions_secondary.update(df_growth_secondary_gas)


# -------------------
# oil
df_growth_secondary_oil = df_gcam_emissions_secondary_change[df_gcam_emissions_secondary_change['fuel_type'] == "Oil"]
co2_mapping = df_merged_countries_edited.set_index('country_NGFS')['oil_FA']
df_growth_secondary_oil['2024'] = df_growth_secondary_oil['Region'].map(co2_mapping)
df_fa_emissions_secondary.update(df_growth_secondary_oil)


# -------------------
del co2_mapping, df_growth_secondary_coal, df_growth_secondary_gas, df_growth_secondary_oil
del df_power_coal, df_power_oil, df_power_gas
del df_power





# In[] 
# project emissions using annual change

# -------------------
# we get dataframe for secondary energy by source/country/scenario with annual emissions values
for i in range(1, len(year_columns)):
    previous_year = year_columns[i - 1]  # Get the previous year
    current_year = year_columns[i]       # Get the current year
    
    # Ensure the current year column exists before calculation
    if current_year in df_fa_emissions_secondary.columns:
        # Check for 'inf' values in the current year's percentage change column
        inf_mask = np.isinf(df_fa_emissions_secondary[current_year])
        
        # Update the current year's values based on the previous year where no 'inf' is present
        df_fa_emissions_secondary.loc[~inf_mask, current_year] = df_fa_emissions_secondary[previous_year] * (1 + df_gcam_emissions_secondary_change[current_year] / 100)
        
        # For rows where 'inf' is present, replace with the corresponding value from df_actual_values
        df_fa_emissions_secondary.loc[inf_mask, current_year] = df_gcam_emissions_secondary.loc[inf_mask, current_year]


# -------------------
# change units
df_fa_emissions_secondary['Unit'] = "MtCO2e"


# -------------------
# delete
del i, current_year, previous_year, inf_mask





# In[] 
# break down by scenarios

# -------------------
df_fa_emissions_secondary_cp = df_fa_emissions_secondary[df_fa_emissions_secondary['Scenario'] == "Current Policies"]
df_fa_emissions_secondary_nz = df_fa_emissions_secondary[df_fa_emissions_secondary['Scenario'] == "Net Zero 2050"]





# In[]
# export data
######################################

# -------------------
# FA projected data  --- overall
df_fa_emissions_secondary.to_excel('2 - output/script 3.1/1.1 - Secondary - emissions FA - projection.xlsx', index=False)


# -------------------
# FA projected emissions by scenario
df_fa_emissions_secondary_cp.to_excel('2 - output/script 3.1/2.1 - Secondary - emissions FA - projection - current policies.xlsx', index=False)
df_fa_emissions_secondary_nz.to_excel('2 - output/script 3.1/2.2 - Secondary - emissions FA - projection - net zero.xlsx', index=False)


# -------------------
# country matching 
df_merged_countries_raw.to_excel('2 - output/script 3.1/3.1 - Merged countries - raw.xlsx', index=False)
df_merged_countries_edited.to_excel('2 - output/script 3.1/3.2 - Merged countries - formatted.xlsx', index=False)
df_fa_countries.to_excel('2 - output/script 3.1/3.3 - Countries - FA.xlsx', index=False)
df_ngfs_countries.to_excel('2 - output/script 3.1/3.4 - Countries - NGFS.xlsx', index=False)





