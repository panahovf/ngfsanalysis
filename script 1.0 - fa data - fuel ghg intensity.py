# In[]
# Date: Feb 3, 2025
# Project: Country level emissions intensity data for power and extraction sectors from Forward Analytics data
# Author: Farhad Panahov





# In[]
# Load packages

import os
import pandas as pd
import geopandas as gpd
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter





# In[]
# Directory & load data

# ---------------
directory = r'C:\Users\panah\OneDrive\Desktop\Work\3 - NGFS analysis'
os.chdir(directory)
del directory


# ---------------
# load power data
df_power = pd.read_csv("1 - input/v3_power_Forward_Analytics2024.csv")
df_extraction = pd.read_csv("1 - input/v2_extraction_operating_ForwardAnalytics2024.csv")





# In[]
# Filter & edit data

# ---------------
# filter by operating
df_power = df_power[df_power['status'] == 'operating']    
df_extraction = df_extraction[df_extraction['status'].isin(['operating', 'Operating'])]    

# ---------------
# create emissions factor across all datasets
df_power['standard_ghg_intensity'] = df_power['annual_co2_calc']/df_power['activity']
df_extraction['standard_ghg_intensity'] = df_extraction['emissions_co2e_million_tonnes']/df_extraction['activity']


# ---------------
# create countries across all datasets
df_power['standard_iso3'] = df_power['countryiso3']
df_extraction['standard_iso3'] = df_extraction['country_iso_3']


# ---------------
# fix data error: Tanzania is given as TZ1, but should be TZA
df_power.loc[df_power['standard_iso3'] == "TZ1", 'standard_iso3'] = "TZA"
df_extraction.loc[df_extraction['standard_iso3'] == "TZ1", 'standard_iso3'] = "TZA"


# ---------------
# break oil, coal and gas separately
df_power_oil = df_power[df_power['subsector'] == "Oil"]
df_power_gas = df_power[df_power['subsector'] == "Gas"]
df_power_coal = df_power[df_power['subsector'] == "Coal"]

df_extraction_oil = df_extraction[df_extraction['subsector_extraction'] == "Oil"]
df_extraction_gas = df_extraction[df_extraction['subsector_extraction'] == "Gas"]
df_extraction_coal = df_extraction[df_extraction['subsector_extraction']=='Coal']





# In[]
# Create a function to get weighted average for emissions intensity and utilization factor (power only) based on activity

# ---------------
# function for GHG factor
def weighted_avg_ghgintensity(group):
    return (group['standard_ghg_intensity'] * group['activity']).sum() / group['activity'].sum()


# ---------------
# utilization factor (for power only)
def weighted_avg_utilfactor(group):
    return (group['capacity_factor'] * group['activity']).sum() / group['activity'].sum()





# In[]
# Apply the function to both power & extraction sectors to get WA emissions intensity and utilization factor

# ---------------
# sectors & fuels
sectors = ['power', 'extraction']
fuels = ['coal', 'oil', 'gas']


# ---------------
# run nested loop
for sector in sectors:
    
    for fuel in fuels:
        
        # select data frame
        tdf_sector_fuel = globals()[f'df_{sector}_{fuel}']

        # get weighted average for each country
        tdf_country_average_ghgintensity = tdf_sector_fuel.groupby('standard_iso3').apply(weighted_avg_ghgintensity)
        
        # Compute global average and fill NA values with the average
        global_avg_ghgintensity = tdf_country_average_ghgintensity.mean()
        tdf_country_average_ghgintensity = tdf_country_average_ghgintensity.fillna(global_avg_ghgintensity)
                   
        # Change the name for the column
        tdf_country_average_ghgintensity.name = 'intensity'

        # Reset the index
        tdf_country_average_ghgintensity = tdf_country_average_ghgintensity.reset_index()

        # assign 
        globals()[f'df_ghgintensity_{sector}_{fuel}'] = tdf_country_average_ghgintensity

        # run similar loop for utilization for power sector
        if sector == 'power':
            tdf_country_average_utilfactor = tdf_sector_fuel.groupby('standard_iso3').apply(weighted_avg_utilfactor)
            global_avg_utilfactor = tdf_country_average_utilfactor.mean()
            tdf_country_average_utilfactor = tdf_country_average_utilfactor.fillna(global_avg_utilfactor)
            tdf_country_average_utilfactor.name = 'utilization'
            tdf_country_average_utilfactor = tdf_country_average_utilfactor.reset_index()
            globals()[f'df_utilfactor_{sector}_{fuel}'] = tdf_country_average_utilfactor



# ---------------
# delete loop variables
del fuel, fuels, sector, sectors, global_avg_ghgintensity, global_avg_utilfactor
del tdf_country_average_ghgintensity, tdf_country_average_utilfactor, tdf_sector_fuel





# In[]
# Export data


# ---------------
# by sector data
df_power.to_excel('2 - output/script 1/1.1 - power - overall.xlsx', index=False)
df_extraction.to_excel('2 - output/script 1/1.2 - extraction - overall.xlsx', index=False)


# ---------------
# by fuel data
df_power_coal.to_excel('2 - output/script 1/2.1 - power - coal.xlsx', index=False)
df_power_gas.to_excel('2 - output/script 1/2.2 - power - gas.xlsx', index=False)
df_power_oil.to_excel('2 - output/script 1/2.3 - power - oil.xlsx', index=False)

df_extraction_coal.to_excel('2 - output/script 1/2.4 - extraction_coal.xlsx', index=False)
df_extraction_gas.to_excel('2 - output/script 1/2.5 - extraction_gas.xlsx', index=False)
df_extraction_oil.to_excel('2 - output/script 1/2.6 - extraction_oil.xlsx', index=False)


# ---------------
# intensity data
df_ghgintensity_power_coal.to_excel('2 - output/script 1/3.1 - country_power_co2factor_coal.xlsx', index=False)
df_ghgintensity_power_gas.to_excel('2 - output/script 1/3.2 - country_power_co2factor_gas.xlsx', index=False)
df_ghgintensity_power_oil.to_excel('2 - output/script 1/3.3 - country_power_co2factor_oil.xlsx', index=False)

df_ghgintensity_extraction_coal.to_excel('2 - output/script 1/3.4 - country_extraction_co2factor_coal.xlsx', index=False)
df_ghgintensity_extraction_gas.to_excel('2 - output/script 1/3.5 - country_extraction_co2factor_gas.xlsx', index=False)
df_ghgintensity_extraction_oil.to_excel('2 - output/script 1/3.6 - country_extraction_co2factor_oil.xlsx', index=False)


# ---------------
# utilization factors in power sector
df_utilfactor_power_coal.to_excel('2 - output/script 1/4.1 - country_power_utilfactor_coal.xlsx', index=False)
df_utilfactor_power_gas.to_excel('2 - output/script 1/4.2 - country_power_utilfactor_gas.xlsx', index=False)
df_utilfactor_power_oil.to_excel('2 - output/script 1/4.3 - country_power_utilfactor_oil.xlsx', index=False)









