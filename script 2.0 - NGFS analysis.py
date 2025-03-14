# In[]
# Date: Feb 3, 2025
# Project: NGFS emissions projections vs Carbon Budget
# Author: Farhad Panahov


# ---------------
# Task #1: The datapoints are provided in 5 year intervals, ending in 2050
#   - Iterpolate linear trend line
#   - Obtain YoY % change 


# ---------------
# Task #2: Convert EJ estimates to GHG emissions

# For Secondary Energy
# I am using FA data to identify country specific emissions intensity values. 
# Oil and Gas are constant. Coal has some variation across countries


# For Primary Energy convert units and values to emissions
#   - Convert EJ/year to emissions 

# See below:

# COAL
# 1 EJ to tonne of coal equivalent = 34120842.37536 tonne of coal equivalent = 34.1208423754 million tonnes of coal; 
# 1 tonne of coal = 1.10231 short ton
# 1764.83 kgCO2 per short ton
# https://www.iea.org/data-and-statistics/data-tools/unit-converter
# https://www.eia.gov/environment/emissions/co2_vol_mass.php
# Supplementary: https://www.convertunits.com/from/EJ/to/tonne+of+coal+equivalent

# OIL
# 1 EJ = 163452108.5322 barrel of oil (BOE) = 163.4521085322 million barrels; 
# 0.43 metric tons CO2/barrel
# https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
# www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2022-approximate-conversion-factors.pdf
# Supplementary: https://www.kylesconverter.com/energy,-work,-and-heat/exajoules-to-million-barrels-of-oil-equivalent

# GAS
# 1 EJ = 27.93 billion cubic meters of natural gas
# 1 m3 = 1.932 kg CO2
# www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2022-approximate-conversion-factors.pdf
# https://www.eia.gov/environment/emissions/co2_vol_mass.php
# Supplementary: https://www.enbridgegas.com/ontario/business-industrial/incentives-conservation/energy-calculators/Greenhouse-Gas-Emissions#:~:text=It%20is%20also%20assumed%20that,2%2C%20page%20254%2D255.


# ---------------
# Task #4: Compare emissions globally to carbon budget
#   - Carbon budget is 400-580 Gt CO2 (https://www.ipcc.ch/sr15/chapter/chapter-2/)
#   - "This assessment suggests a remaining budget of about 420 GtCO2 for a two-thirds chance of limiting warming to 1.5°C, and of about 580 GtCO2 for an even chance"

# NOTE: Estimates as of beginning of 2023 were adopted from an earlier paper XXX by subtracting 31.5 Gt for energy-related
# CO2 in 2020, 36.1 Gt CO2 in 2021, 36.8 Gt CO2 in 2022. Resulting values are then adjusted by 37.2 Gt CO2 for 2023 as
# per IEA’s most recent estimate to derive carbon budget estimates as of beginning 2024
 




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
from functools import reduce





# In[]
# Directory & load data

# ---------------
directory = r'C:\Users\panah\OneDrive\Desktop\Work\3 - NGFS analysis'
os.chdir(directory)
del directory


# ---------------
# NGFS GCAM 6
df_gcam = pd.read_excel('1 - input/Downscaled_GCAM 6.0 NGFS_data.xlsx')


# ---------------
# load country power sector OIL, GAS and COAL emissions intensity data
# original intensity is given in million tonnes of CO2 per MWh; this section already converts it from MWh to EJ by multiplying to 277777777.778

# https://www.convertunits.com/from/EJ/to/MWh
# coal
df_ghgintensity_power_coal = pd.read_excel('2 - output/script 1/3.1 - country_power_co2factor_coal.xlsx')
df_ghgintensity_power_coal['intensity'] = df_ghgintensity_power_coal['intensity'] * (277777777.778) 

# gas
df_ghgintensity_power_gas = pd.read_excel('2 - output/script 1/3.2 - country_power_co2factor_gas.xlsx')
df_ghgintensity_power_gas['intensity'] = df_ghgintensity_power_gas['intensity'] * (277777777.778)

# oil
df_ghgintensity_power_oil = pd.read_excel('2 - output/script 1/3.3 - country_power_co2factor_oil.xlsx')
df_ghgintensity_power_oil['intensity'] = df_ghgintensity_power_oil['intensity'] * (277777777.778)


# ---------------
# load market and region datasets
df_unfccc_class = pd.read_excel('1 - input/Country Datasets/UNFCCC classification.xlsx')
df_regions = pd.read_excel('1 - input/Country Datasets/country_gca_region.xlsx')





# In[]
# Create filtered file + add rergions & development levels + other edits

df_gcam = df_gcam[df_gcam['Region'] != 'EU27']  # first remove EU27

# ---------------
# merge with regions dataframe
df_gcam = pd.merge(df_gcam, df_regions[['alpha-3', 'gca_region']],
                     left_on='Region',
                     right_on='alpha-3',
                     how='left')

df_gcam = df_gcam.drop('alpha-3', axis=1)   # drop the extra column


# ---------------
# merge with development level dataframe
df_gcam = pd.merge(df_gcam, df_unfccc_class[['iso_3', 'classification']],
                     left_on='Region',
                     right_on='iso_3',
                     how='left')

df_gcam = df_gcam.drop('iso_3', axis=1)   # drop the extra column


# ---------------
# fill missing regions, and development levels with 'other'
df_gcam['gca_region'] = df_gcam['gca_region'].fillna('Other')
df_gcam['classification'] = df_gcam['classification'].fillna('Other')


# ---------------
# add fuel type
df_gcam['fuel_type'] = np.nan

df_gcam.loc[df_gcam['Variable'].str.contains('Coal'), 'fuel_type'] = "Coal"
df_gcam.loc[df_gcam['Variable'].str.contains('Gas'), 'fuel_type'] = "Gas"
df_gcam.loc[df_gcam['Variable'].str.contains('Oil'), 'fuel_type'] = "Oil"


# ---------------
# create a column indicating source of the country data
df_gcam['dataset'] = "NGFS"


# ---------------
# reorder columns by moving the last three columns to the fourth position
# bring region and develoment and fuel type to front and data source
# 4 columns from the end, to after 3rd column
df_gcam = df_gcam[df_gcam.columns[:3].tolist() + df_gcam.columns[-4:].tolist() + df_gcam.columns[3:-4].tolist()]


# ---------------
# remove years 2051 onwards
v_removeyears = [str(year) for year in range(2051, 2101)]
df_gcam = df_gcam.drop(columns=v_removeyears)


# ---------------
# delete 
del df_regions, df_unfccc_class, v_removeyears





# In[]
# Filter GCAM data for Primary and Secondary energy only

# ---------------
# filter overall dataset
df_gcam_filtered = df_gcam[df_gcam['Variable'].isin(['Primary Energy|Gas', 'Primary Energy|Oil',
                                                          'Primary Energy|Coal', 'Secondary Energy|Electricity|Coal',
                                                          'Secondary Energy|Electricity|Gas', 'Secondary Energy|Electricity|Oil'])]

# get energy emissions dataset
df_gcam_emissions_energy = df_gcam.loc[(df_gcam['Variable'] == 'Emissions|CO2|Energy')]

# get totak emissions dataset
df_gcam_emissions_total = df_gcam.loc[(df_gcam['Variable'] == 'Emissions|CO2')]


# ---------------
# delete
del df_gcam





# In[]
# TASK #1: The datapoints are provided in 5 year intervals, ending in 2050
#   - Iterpolate linear trend line
#   - Obtain YoY % change

# In[]

# ---------------
# interpolate the NaN values in the years columns
year_columns = [str(year) for year in range(2020, 2051)]
df_gcam_filtered[year_columns] = df_gcam_filtered[year_columns].interpolate(method='linear', axis=1)
df_gcam_emissions_energy[year_columns] = df_gcam_emissions_energy[year_columns].interpolate(method='linear', axis=1)
df_gcam_emissions_total[year_columns] = df_gcam_emissions_total[year_columns].interpolate(method='linear', axis=1)


# ---------------
# calculate yearly percent change for each row
df_gcam_filtered_change = df_gcam_filtered.copy()
df_gcam_filtered_change[year_columns] = df_gcam_filtered_change[year_columns].pct_change(axis=1).fillna(0) * 100
df_gcam_filtered_change['Unit'] = "YoY % change"

df_gcam_emissions_energy_change = df_gcam_emissions_energy.copy()
df_gcam_emissions_energy_change[year_columns] = df_gcam_emissions_energy_change[year_columns].pct_change(axis=1).fillna(0) * 100
df_gcam_emissions_energy_change['Unit'] = "YoY % change"





# In[]
# TASK #2: Convert EJ estimates to GHG emissions

# ---------------
# get copy dataframe
df_gcam_emissions = df_gcam_filtered.copy()


# ---------------
# change the units
df_gcam_emissions['Unit'] = "MtCO2e"




# In[]
# SECONDARY ENERGY
# I am using FA data to identify country specific emissions intensity values. 
# Oil and Gas are constant. Coal has some variation across countries

# ---------------
# get list of countries for coal, oil and gas secondary energy
gcam_countries_secondary = df_gcam_filtered[df_gcam_filtered['Variable'].isin(['Secondary Energy|Electricity|Gas',
                                                                               'Secondary Energy|Electricity|Oil',
                                                                               'Secondary Energy|Electricity|Coal'])][['Region']].drop_duplicates()

# merge all CO2 factors
df_ghgintensity_power = [df_ghgintensity_power_coal, df_ghgintensity_power_oil, df_ghgintensity_power_gas]

for fuel in df_ghgintensity_power:
    gcam_countries_secondary = gcam_countries_secondary.merge(fuel, 
                                                               left_on='Region', 
                                                               right_on='standard_iso3', 
                                                               how='left').drop(columns=['standard_iso3'])

# rename columns for clarity
gcam_countries_secondary.columns = ['Region', 'coal', 'oil', 'gas']


# ---------------
# set average factors to countries with no actual values in FA data
gcam_countries_secondary[['coal', 'oil', 'gas']] = gcam_countries_secondary[['coal', 'oil', 'gas']].fillna(gcam_countries_secondary[['coal', 'oil', 'gas']].mean())


# ---------------
# delete
del df_ghgintensity_power, df_ghgintensity_power_gas, df_ghgintensity_power_oil, df_ghgintensity_power_coal, fuel





# In[]
# Convert secondary energy to emissions

# ---------------
# create a mapping of Variables to emission factor dictionaries
emissions_factors_secondary = {
    'Secondary Energy|Electricity|Coal': gcam_countries_secondary.set_index('Region')['coal'].to_dict(),
    'Secondary Energy|Electricity|Gas': gcam_countries_secondary.set_index('Region')['gas'].to_dict(),
    'Secondary Energy|Electricity|Oil': gcam_countries_secondary.set_index('Region')['oil'].to_dict()}


# ---------------
# map the factor based on 'Variable' and 'Region'
df_gcam_emissions['Factor'] = df_gcam_emissions.apply(
    lambda row: emissions_factors_secondary.get(row['Variable'], {}).get(row['Region'], 1), axis=1)

# apply the factor to the yearly columns
df_gcam_emissions[year_columns] = df_gcam_emissions[year_columns].mul(df_gcam_emissions['Factor'], axis=0)

# drop the temporary 'Factor' column
df_gcam_emissions.drop(columns=['Factor'], inplace=True)


# ---------------
# delete
del emissions_factors_secondary, gcam_countries_secondary





# In[]
# PRIMARY ENERGY
# Convert primary energy to emissions    
    
# ---------------
# define the constant to multiply for unit conversion --- SEE INTRO FOR FORMULAS
emissions_factors_primary = {
    'Primary Energy|Coal': 34120842.37536*1.10231*1764.83 / 10**3 / 10**6,   #EJ to Tonne to Short Ton to KgCO2 to tCO2 to MtCO2 --- final unit: MtCO2
    'Primary Energy|Gas':  27.93*10**9*1.932 / 10**3 / 10**6,                  #EJ to million cubic meters of natural gas to tCO2 to Mt --- final unit: MtCO2
    'Primary Energy|Oil': 163452108.5322*0.43 / 10**6                       #EJ to barrel to tCO2 to Mt --- final unit: MtCO2
}


# ---------------
# process for primary energy rows in gcam
for variable, factor in emissions_factors_primary.items():
    mask = df_gcam_emissions['Variable'] == variable  # Filter rows
    df_gcam_emissions.loc[mask, year_columns] *= factor  # Apply factor to year columns
    

# ---------------
# delete
del variable, factor, mask, emissions_factors_primary





# In[]
# Break down data by secondary and primary

# ---------------
# break down emissions by primary and secondary 
df_gcam_emissions_primary = df_gcam_emissions[df_gcam_emissions['Variable'].str.contains('Primary')]
df_gcam_emissions_secondary = df_gcam_emissions[df_gcam_emissions['Variable'].str.contains('Secondary')]

df_gcam_emissions_primary_change = df_gcam_filtered_change[df_gcam_filtered_change['Variable'].str.contains('Primary')]
df_gcam_emissions_secondary_change = df_gcam_filtered_change[df_gcam_filtered_change['Variable'].str.contains('Secondary')]





# In[]
# Prepare data from plots

# ---------------
# get total energy emissions --- cumulative by scenario
df_gcam_emissions_energy_byscenario_cumulative = df_gcam_emissions_energy.groupby(['Scenario'])[year_columns].sum()
df_gcam_emissions_energy_byscenario_cumulative.reset_index(inplace=True)





# In[]
# Create a 'comparison' dataframe across multiple sources

# ---------------
year2022 = "2022"


# ---------------
# manual comparison dataframe
# Creating a DataFrame with specified rows and columns
# for secondary

print(df_gcam_emissions.loc[df_gcam_emissions['Scenario']=="Current Policies"].groupby('Variable')[year2022].sum())
# Primary Energy|Coal                  10751.329821
# Primary Energy|Gas                    7511.737102
# Primary Energy|Oil                   12642.965708
# Secondary Energy|Electricity|Coal    10321.783879
# Secondary Energy|Electricity|Gas      2748.633597
# Secondary Energy|Electricity|Oil       615.605970

print(df_gcam_emissions_energy.loc[df_gcam_emissions_energy['Scenario']=="Current Policies"][year2022].sum())
# 33169.208880000006

print(df_gcam_emissions_total.loc[df_gcam_emissions_total['Scenario']=="Current Policies"][year2022].sum())
# 34214.287679999994


# ---------------
# SECONDARY EMISSIONS
df_comparison_secondary = {
    'NGFS Secondary\n(author\'s estimate)': [10.321, 2.748, 0.615],  # Initial values for secondary from above
    'Forward Analytics': [10.085, 3.41, 0.641]  # Initial values from Moritz
}

# Define the index for the rows corresponding to coal, oil, and gas
df_comparison_secondary = pd.DataFrame(df_comparison_secondary, index=['Coal', 'Gas', 'Oil'])


# ---------------
# PRIMARY EMISSIONS
df_comparison_primary = {
    'NGFS Primary\n(author\'s estimate)': [10.751, 7.511, 12.643],  # Initial values for primary from above
    'IEA': [14.308, 7.168, 10.307],     # IEA https://www.iea.org/data-and-statistics/data-tools/greenhouse-gas-emissions-from-energy-data-explorer
    'OWID':[14.23,7.56,10.9] # OurWorldInData https://ourworldindata.org/emissions-by-fuel
}

# Define the index for the rows corresponding to coal, oil, and gas
df_comparison_primary = pd.DataFrame(df_comparison_primary, index=['Coal', 'Gas', 'Oil'])


# ---------------
# TOTAL EMISSIOSN
df_comparison_total = {
    'GHG': [30.906,33.169, 34.214, 34.981, 37.15]  # Current policy primary energy = see above and sum it
     # IEA https://www.iea.org/data-and-statistics/data-tools/greenhouse-gas-emissions-from-energy-data-explorer
     # OurWorldInData https://ourworldindata.org/emissions-by-fuel
}

# Define the index for the rows corresponding to coal, oil, and gas
df_comparison_total = pd.DataFrame(df_comparison_total, index=['NGFS Primary Energy\n(author\'s estimate)','NGFS Energy', 'NGFS Total', 'IEA Fuel Combustion', 'OWID Fossil Fuels'])






# In[]
# Export data

# ---------------
# gcam dataset
df_gcam_filtered.to_excel('2 - output/script 2/1.1 - GCAM - EJ.xlsx', index=False)
df_gcam_emissions.to_excel('2 - output/script 2/1.2 - GCAM - emissions.xlsx', index=False)
df_gcam_filtered_change.to_excel('2 - output/script 2/1.3 - GCAM - change.xlsx', index=False)


# ---------------
# breakdowns
df_gcam_emissions_total.to_excel('2 - output/script 2/2.1 - GCAM - emissions - total.xlsx', index=False)
df_gcam_emissions_energy.to_excel('2 - output/script 2/2.2 - GCAM - emissions - energy.xlsx', index=False)
df_gcam_emissions_secondary.to_excel('2 - output/script 2/2.3 - GCAM - emissions - secondary.xlsx', index=False)
df_gcam_emissions_primary.to_excel('2 - output/script 2/2.4 - GCAM - emissions - primary.xlsx', index=False)


# ---------------
# breakdowns --- YoY change
df_gcam_emissions_energy_change.to_excel('2 - output/script 2/3.1 - GCAM - change - energy.xlsx', index=False)
df_gcam_emissions_secondary_change.to_excel('2 - output/script 2/3.2 - GCAM - change - secondary.xlsx', index=False)
df_gcam_emissions_primary_change.to_excel('2 - output/script 2/3.3 - GCAM - change - primary.xlsx', index=False)


# ---------------
# breakdowns --- cumulative by scenario
df_gcam_emissions_energy_byscenario_cumulative.to_excel('2 - output/script 2/4.1 - GCAM - emissions - energy by scenario - cumulative.xlsx', index=False)


# ---------------
# comparisons
df_comparison_total.to_excel('2 - output/script 2/5.1 - GCAM - comparison - total.xlsx', index=False)
df_comparison_secondary.to_excel('2 - output/script 2/5.2 - GCAM - comparison - secondary.xlsx', index=False)
df_comparison_primary.to_excel('2 - output/script 2/5.3 - GCAM - comparison - primary.xlsx', index=False)


