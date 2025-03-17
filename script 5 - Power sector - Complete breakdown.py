# In[1]:
# Date: Sep 15, 2024
# Project: Emissions & capacity by scenario (CP, NGFS NZ, Modified NZ 1.5C 50%) for Global, India, US, Vietnam, Turkeye, Indonesia, Germany
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
# LOAD EMISSIONS DATA - POWER
df_emissions_currentpolicy = pd.read_excel('2 - output/script 4.2/9.1 - Current policy - Secondary - annual.xlsx')
df_emissions_netzero = pd.read_excel('2 - output/script 4.2/9.2 - Net zero - Secondary - annual.xlsx')
df_emissions_nz1550v2 = pd.read_excel('2 - output/script 4.2/6.1 - NZ-15-50 - v2 - Secondary - annual.xlsx')
df_emissions_nz1550v3 = pd.read_excel('2 - output/script 4.2/10.1 - NZ-15-50 - v3 - Secondary - annual.xlsx')

df_emissions_nz1550v3 = df_emissions_nz1550v3.drop(columns=['iso_3', 'classification'])

# --------------
# LOAD POWER DATA
df_power_coal = pd.read_excel('2 - output/script 1/4 - power - coal.xlsx')
df_power_gas = pd.read_excel('2 - output/script 1/5 - power - gas.xlsx')
df_power_oil = pd.read_excel('2 - output/script 1/6 - power - oil.xlsx')




# In[]

# YOY change data for Downscaling countries

# set years columns
years_columns = [str(year) for year in range(2024, 2051)]


# --------------
# YOY change data
df_change_currentpolicy = df_emissions_currentpolicy.copy()
df_change_currentpolicy[years_columns] = df_change_currentpolicy[years_columns].pct_change(axis=1) * 100
df_change_currentpolicy[years_columns] = df_change_currentpolicy[years_columns].fillna(0)

df_change_netzero = df_emissions_netzero.copy()
df_change_netzero[years_columns] = df_emissions_netzero[years_columns].pct_change(axis=1) * 100
df_change_netzero[years_columns] = df_change_netzero[years_columns].fillna(0)

df_change_nz1550v2 = df_emissions_nz1550v2.copy()
df_change_nz1550v2[years_columns] = df_change_nz1550v2[years_columns].pct_change(axis=1) * 100
df_change_nz1550v2[years_columns] = df_change_nz1550v2[years_columns].fillna(0)

df_change_nz1550v3 = df_emissions_nz1550v3.copy()
df_change_nz1550v3[years_columns] = df_change_nz1550v3[years_columns].pct_change(axis=1) * 100
df_change_nz1550v3[years_columns] = df_change_nz1550v3[years_columns].fillna(0)



# In[4]: FILTER FOR COUNTIES
############################

# Get list of EMDE countries

# load datasets
temp_directory = r'C:\Users\panah\OneDrive\Desktop\Work\2 - RA - Climate fin\2 - output\script a - country codes'
#df_country_developing = pd.read_excel(temp_directory + r'\2 - developing.xlsx')
#df_country_emerging = pd.read_excel(temp_directory + r'\3 - emerging.xlsx')

df_country_unfccc = pd.read_excel('1 - input/Country Datasets/UNFCCC classification.xlsx')
df_country_unfccc_dev = df_country_unfccc[df_country_unfccc['classification'] == "Developing"]
df_country_unfccc_dop = df_country_unfccc[df_country_unfccc['classification'] == "All Developed"]

# get and combine lists
#v_countrycodes_developing = list(df_country_developing['alpha-3'].unique())
#v_countrycodes_emerging = list(df_country_emerging['alpha-3'].unique())
#v_countrycodes_emde = v_countrycodes_developing + v_countrycodes_emerging

v_countrycodes_unfccc_dev = list(df_country_unfccc_dev['iso_3'].unique())
v_countrycodes_unfccc_dop = list(df_country_unfccc_dop['iso_3'].unique())

# delete
del temp_directory, df_country_unfccc, df_country_unfccc_dev, df_country_unfccc_dop





# In[4]: FILTER FOR COUNTIES
############################



# countries
# Collect unique country codes from all three dataframes
regions = list((set(df_power_coal['countryiso3']) | set(df_power_gas['countryiso3']) | set(df_power_oil['countryiso3']) | set(df_emissions_currentpolicy['Region'])) - {'unknown', 'TZ1'})
regions_with_extras = regions + ["devunfccc", "dopunfccc", "global"]



# combine power data
df_power = pd.concat([df_power_coal, df_power_gas, df_power_oil], axis=0, ignore_index=True)
df_power_country = df_power.groupby(['countryiso3', 'subsector'])['annual_co2_calc'].sum().reset_index()
df_power_country.loc[df_power_country['countryiso3']=='TZ1','countryiso3'] = 'TZA'
df_power_country = df_power_country[df_power_country['countryiso3'] != 'unknown']



# --------------
# Case 1: Current policy

# countries
for region in regions:
    if region in df_emissions_currentpolicy['Region'].unique():
        # If the region exists, assign its data
        globals()[f"df_emissions_currentpolicy_{region.lower()}"] = df_emissions_currentpolicy[df_emissions_currentpolicy["Region"] == region]
    else:
        # If the region does NOT exist, assign fallback value
        df_temp = df_change_currentpolicy[df_change_currentpolicy["Region"] == 'Downscaling|Countries without IEA statistics']
        temp_power_country = df_power_country[df_power_country['countryiso3'] == region]
        mapping_dict = temp_power_country.set_index('subsector')['annual_co2_calc']
        df_temp['2024'] = df_temp['fuel_type'].map(mapping_dict).fillna(0)

        # Apply cumulative percentage change for 2025-2050 --- skip 2024 as starting point
        for year in years_columns[1:]:
            df_temp[year] = df_temp[years_columns[years_columns.index(year) - 1]] * (1 + df_temp[year] / 100)
            
        globals()[f"df_emissions_currentpolicy_{region.lower()}"] = df_temp

# regionals
df_emissions_currentpolicy_devunfccc = df_emissions_currentpolicy[df_emissions_currentpolicy["Region"].isin(v_countrycodes_unfccc_dev)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_currentpolicy_dopunfccc = df_emissions_currentpolicy[df_emissions_currentpolicy["Region"].isin(v_countrycodes_unfccc_dop)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_currentpolicy_global = df_emissions_currentpolicy.groupby('fuel_type')[years_columns].sum().reset_index()


# --------------
# Case 2: Netzero

# countries
for region in regions:
    if region in df_emissions_currentpolicy['Region'].unique():
        # If the region exists, assign its data
        globals()[f"df_emissions_netzero_{region.lower()}"] = df_emissions_netzero[df_emissions_netzero["Region"] == region]
    else:
        # If the region does NOT exist, assign fallback value
        df_temp = df_change_netzero[df_change_netzero["Region"] == 'Downscaling|Countries without IEA statistics']
        temp_power_country = df_power_country[df_power_country['countryiso3'] == region]
        mapping_dict = temp_power_country.set_index('subsector')['annual_co2_calc']
        df_temp['2024'] = df_temp['fuel_type'].map(mapping_dict).fillna(0)

        # Apply cumulative percentage change for 2025-2050 --- skip 2024 as starting point
        for year in years_columns[1:]:
            df_temp[year] = df_temp[years_columns[years_columns.index(year) - 1]] * (1 + df_temp[year] / 100)
            
        globals()[f"df_emissions_netzero_{region.lower()}"] = df_temp

# regionals
df_emissions_netzero_devunfccc = df_emissions_netzero[df_emissions_netzero["Region"].isin(v_countrycodes_unfccc_dev)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_netzero_dopunfccc = df_emissions_netzero[df_emissions_netzero["Region"].isin(v_countrycodes_unfccc_dop)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_netzero_global = df_emissions_netzero.groupby('fuel_type')[years_columns].sum().reset_index()



# --------------
# Case 3: Netzero 1.5C 50% adjusted

# countries
for region in regions:
    if region in df_emissions_nz1550v2['Region'].unique():
        # If the region exists, assign its data
        globals()[f"df_emissions_nz1550v2_{region.lower()}"] = df_emissions_nz1550v2[df_emissions_nz1550v2["Region"] == region]
    else:
        # If the region does NOT exist, assign fallback value
        df_temp = df_change_nz1550v2[df_change_nz1550v2["Region"] == 'Downscaling|Countries without IEA statistics']
        temp_power_country = df_power_country[df_power_country['countryiso3'] == region]
        mapping_dict = temp_power_country.set_index('subsector')['annual_co2_calc']
        df_temp['2024'] = df_temp['fuel_type'].map(mapping_dict).fillna(0)

        # Apply cumulative percentage change for 2025-2050 --- skip 2024 as starting point
        for year in years_columns[1:]:
            df_temp[year] = df_temp[years_columns[years_columns.index(year) - 1]] * (1 + df_temp[year] / 100)
            
        globals()[f"df_emissions_nz1550v2_{region.lower()}"] = df_temp

# regionals
df_emissions_nz1550v2_devunfccc = df_emissions_nz1550v2[df_emissions_nz1550v2["Region"].isin(v_countrycodes_unfccc_dev)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_nz1550v2_dopunfccc = df_emissions_nz1550v2[df_emissions_nz1550v2["Region"].isin(v_countrycodes_unfccc_dop)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_nz1550v2_global = df_emissions_nz1550v2.groupby('fuel_type')[years_columns].sum().reset_index()




# --------------
# Case 4: Netzero 1.5C 50% adjusted --- no growth

# countries
for region in regions:
    if region in df_emissions_nz1550v3['Region'].unique():
        # If the region exists, assign its data
        globals()[f"df_emissions_nz1550v3_{region.lower()}"] = df_emissions_nz1550v3[df_emissions_nz1550v3["Region"] == region]
    else:
        # If the region does NOT exist, assign fallback value
        df_temp = df_change_nz1550v3[df_change_nz1550v3["Region"] == 'Downscaling|Countries without IEA statistics']
        temp_power_country = df_power_country[df_power_country['countryiso3'] == region]
        mapping_dict = temp_power_country.set_index('subsector')['annual_co2_calc']
        df_temp['2024'] = df_temp['fuel_type'].map(mapping_dict).fillna(0)

        # Apply cumulative percentage change for 2025-2050 --- skip 2024 as starting point
        for year in years_columns[1:]:
            df_temp[year] = df_temp[years_columns[years_columns.index(year) - 1]] * (1 + df_temp[year] / 100)
            
        globals()[f"df_emissions_nz1550v3_{region.lower()}"] = df_temp


# regionals
df_emissions_nz1550v3_devunfccc = df_emissions_nz1550v3[df_emissions_nz1550v3["Region"].isin(v_countrycodes_unfccc_dev)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_nz1550v3_dopunfccc = df_emissions_nz1550v3[df_emissions_nz1550v3["Region"].isin(v_countrycodes_unfccc_dop)].groupby('fuel_type')[years_columns].sum().reset_index()
df_emissions_nz1550v3_global = df_emissions_nz1550v3.groupby('fuel_type')[years_columns].sum().reset_index()



del year, df_temp, mapping_dict, temp_power_country





# In[4]: GET GHG INTENTITY FACTORS
##################################

# --------------
# get emissions intensity by country
# this function creates a weighted average by countries (emissions by activity)
def weighted_avg_intensity_coal(group):
    return (group['emissions_factor_perMWh'] * group['activity']).sum() / group['activity'].sum()

def weighted_avg_intensity_gas_oil(group):
    return (group['emission_factor'] * group['activity']).sum() / group['activity'].sum()



# apply the function --- this also directs them to dictionaries
df_power_coal_intensity_series = df_power_coal.groupby('countryiso3').apply(weighted_avg_intensity_coal)
df_power_gas_intensity_series = df_power_gas.groupby('countryiso3').apply(weighted_avg_intensity_gas_oil)
df_power_oil_intensity_series = df_power_oil.groupby('countryiso3').apply(weighted_avg_intensity_gas_oil)

# Compute global average excluding NaN values
coal_avg_intensity = df_power_coal_intensity_series.mean()
gas_avg_intensity = df_power_gas_intensity_series.mean()
oil_avg_intensity = df_power_oil_intensity_series.mean()

# Fill missing values with the global average
df_power_coal_intensity_series = df_power_coal_intensity_series.fillna(coal_avg_intensity)
df_power_gas_intensity_series = df_power_gas_intensity_series.fillna(gas_avg_intensity)
df_power_oil_intensity_series = df_power_oil_intensity_series.fillna(oil_avg_intensity)

# Convert to dictionary
df_power_coal_intensity = df_power_coal_intensity_series.to_dict()
df_power_gas_intensity = df_power_gas_intensity_series.to_dict()
df_power_oil_intensity = df_power_oil_intensity_series.to_dict()










# In[4]: GET GHG UTILIZATION FACTORS
####################################

# --------------
# get capacity factors by country (utilization factor)
# this function creates a weighted average by countries (emissions by activity)
def weighted_avg_utilization_coal(group):
    return (group['capacity_factor'] * group['activity']).sum() / group['activity'].sum()


# apply the function
df_power_coal_utilization_series = df_power_coal.groupby('countryiso3').apply(weighted_avg_utilization_coal)
df_power_gas_utilization_series = df_power_gas.groupby('countryiso3').apply(weighted_avg_utilization_coal)
df_power_oil_utilization_series = df_power_oil.groupby('countryiso3').apply(weighted_avg_utilization_coal)

# Compute global average excluding NaN values
coal_avg_utilization = df_power_coal_utilization_series.mean()
gas_avg_utilization = df_power_gas_utilization_series.mean()
oil_avg_utilization = df_power_oil_utilization_series.mean()

# Fill missing values with the global average
df_power_coal_utilization_series = df_power_coal_utilization_series.fillna(coal_avg_utilization)
df_power_gas_utilization_series = df_power_gas_utilization_series.fillna(gas_avg_utilization)
df_power_oil_utilization_series = df_power_oil_utilization_series.fillna(oil_avg_utilization)

# Convert to dictionary
df_power_coal_utilization = df_power_coal_utilization_series.to_dict()
df_power_gas_utilization = df_power_gas_utilization_series.to_dict()
df_power_oil_utilization = df_power_oil_utilization_series.to_dict()










# In[4]: CONVERT EMISSIONS TO GENERATION
########################################

# Divide emissions by the intensity factors to get MWh
# GHG / (GHG/MWh) = MWh
# For used capacity: divide total generation by (24x365)
# For total capacity: divide used capacity by the capacity factor (or utilization factor)


# create dataframes

# countries
for region in regions:
    globals()[f"df_totalcapacity_currentpolicy_{region.lower()}"] = globals()[f"df_emissions_currentpolicy_{region.lower()}"].copy()

for region in regions:
    globals()[f"df_totalcapacity_netzero_{region.lower()}"] = globals()[f"df_emissions_netzero_{region.lower()}"].copy()

for region in regions:
    globals()[f"df_totalcapacity_nz1550v2_{region.lower()}"] = globals()[f"df_emissions_nz1550v2_{region.lower()}"].copy()

for region in regions:
    globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"] = globals()[f"df_emissions_nz1550v3_{region.lower()}"].copy()




# regionals
df_totalcapacity_currentpolicy_devunfccc = df_emissions_currentpolicy.copy()[df_emissions_currentpolicy['Region'].isin(v_countrycodes_unfccc_dev)]
df_totalcapacity_currentpolicy_dopunfccc = df_emissions_currentpolicy.copy()[df_emissions_currentpolicy['Region'].isin(v_countrycodes_unfccc_dop)]
df_totalcapacity_currentpolicy_global = df_emissions_currentpolicy.copy()

df_totalcapacity_netzero_devunfccc = df_emissions_netzero.copy()[df_emissions_netzero['Region'].isin(v_countrycodes_unfccc_dev)]
df_totalcapacity_netzero_dopunfccc = df_emissions_netzero.copy()[df_emissions_netzero['Region'].isin(v_countrycodes_unfccc_dop)]
df_totalcapacity_netzero_global = df_emissions_netzero.copy()

df_totalcapacity_nz1550v2_devunfccc = df_emissions_nz1550v2.copy()[df_emissions_nz1550v2['Region'].isin(v_countrycodes_unfccc_dev)]
df_totalcapacity_nz1550v2_dopunfccc = df_emissions_nz1550v2.copy()[df_emissions_nz1550v2['Region'].isin(v_countrycodes_unfccc_dop)]
df_totalcapacity_nz1550v2_global = df_emissions_nz1550v2.copy()

df_totalcapacity_nz1550v3_devunfccc = df_emissions_nz1550v3.copy()[df_emissions_nz1550v3['Region'].isin(v_countrycodes_unfccc_dev)]
df_totalcapacity_nz1550v3_dopunfccc = df_emissions_nz1550v3.copy()[df_emissions_nz1550v3['Region'].isin(v_countrycodes_unfccc_dop)]
df_totalcapacity_nz1550v3_global = df_emissions_nz1550v3.copy()



########################################################
#  1. CURRENT POLICY -----------------------------------
########################################################

# --------------
# total capacity
# 1 - coal
for region in regions_with_extras:
    # Get the DataFrame for the current region
    df = globals()[f"df_totalcapacity_currentpolicy_{region.lower()}"]
    
    # Apply the transformation for "Coal"
    df.loc[df['fuel_type'] == "Coal", years_columns] = (
        df.loc[df['fuel_type'] == "Coal", years_columns]
        .div(df['Region'].map(df_power_coal_intensity).fillna(coal_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_coal_utilization).fillna(coal_avg_utilization), axis=0)
    )


# 2 - gas
for region in regions_with_extras:
    # Get the DataFrame for the current region
    df = globals()[f"df_totalcapacity_currentpolicy_{region.lower()}"]

    # Apply the transformation for "Gas"
    df.loc[df['fuel_type'] == "Gas", years_columns] = (
        df.loc[df['fuel_type'] == "Gas", years_columns]
        .div(df['Region'].map(df_power_gas_intensity).fillna(gas_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_gas_utilization).fillna(gas_avg_utilization), axis=0)
    )


# 3 - oil
for region in regions_with_extras:
    # Get the DataFrame for the current region
    df = globals()[f"df_totalcapacity_currentpolicy_{region.lower()}"]
   
    # Apply the transformation for "Oil"
    df.loc[df['fuel_type'] == "Oil", years_columns] = (
        df.loc[df['fuel_type'] == "Oil", years_columns]
        .div(df['Region'].map(df_power_oil_intensity).fillna(oil_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_oil_utilization).fillna(oil_avg_utilization), axis=0)
    )


# for regionals group all countries
df_totalcapacity_currentpolicy_devunfccc = df_totalcapacity_currentpolicy_devunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_currentpolicy_dopunfccc = df_totalcapacity_currentpolicy_dopunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_currentpolicy_global = df_totalcapacity_currentpolicy_global.groupby('fuel_type')[years_columns].sum().reset_index()




########################################################
#  2. NET ZERO -----------------------------------------
########################################################

# --------------
# total capacity
# 1 - coal
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_netzero_{region.lower()}"]
    df.loc[df['fuel_type'] == "Coal", years_columns] = (
        df.loc[df['fuel_type'] == "Coal", years_columns]
        .div(df['Region'].map(df_power_coal_intensity).fillna(coal_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_coal_utilization).fillna(coal_avg_utilization), axis=0)
    )

# 2 - gas
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_netzero_{region.lower()}"]
    df.loc[df['fuel_type'] == "Gas", years_columns] = (
        df.loc[df['fuel_type'] == "Gas", years_columns]
        .div(df['Region'].map(df_power_gas_intensity).fillna(gas_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_gas_utilization).fillna(gas_avg_utilization), axis=0)
    )

# 3 - oil
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_netzero_{region.lower()}"]
    df.loc[df['fuel_type'] == "Oil", years_columns] = (
        df.loc[df['fuel_type'] == "Oil", years_columns]
        .div(df['Region'].map(df_power_oil_intensity).fillna(oil_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_oil_utilization).fillna(oil_avg_utilization), axis=0)
    )

# Grouping for aggregated data
df_totalcapacity_netzero_devunfccc = df_totalcapacity_netzero_devunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_netzero_dopunfccc = df_totalcapacity_netzero_dopunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_netzero_global = df_totalcapacity_netzero_global.groupby('fuel_type')[years_columns].sum().reset_index()





########################################################
#  3. NET ZERO 1.5C 50% adjusted -----------------------
########################################################

# --------------
# total capacity
# 1 - coal
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v2_{region.lower()}"]
    df.loc[df['fuel_type'] == "Coal", years_columns] = (
        df.loc[df['fuel_type'] == "Coal", years_columns]
        .div(df['Region'].map(df_power_coal_intensity).fillna(coal_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_coal_utilization).fillna(coal_avg_utilization), axis=0)
    )

# 2 - gas
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v2_{region.lower()}"]
    df.loc[df['fuel_type'] == "Gas", years_columns] = (
        df.loc[df['fuel_type'] == "Gas", years_columns]
        .div(df['Region'].map(df_power_gas_intensity).fillna(gas_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_gas_utilization).fillna(gas_avg_utilization), axis=0)
    )

# 3 - oil
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v2_{region.lower()}"]
    df.loc[df['fuel_type'] == "Oil", years_columns] = (
        df.loc[df['fuel_type'] == "Oil", years_columns]
        .div(df['Region'].map(df_power_oil_intensity).fillna(oil_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_oil_utilization).fillna(oil_avg_utilization), axis=0)
    )

# Grouping for aggregated data
df_totalcapacity_nz1550v2_devunfccc = df_totalcapacity_nz1550v2_devunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_nz1550v2_dopunfccc = df_totalcapacity_nz1550v2_dopunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_nz1550v2_global = df_totalcapacity_nz1550v2_global.groupby('fuel_type')[years_columns].sum().reset_index()




########################################################
#  4. NET ZERO 1.5C 50% adjusted --- NO GROWTH ---------
########################################################

# --------------
# total capacity
# 1 - coal
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"]
    df.loc[df['fuel_type'] == "Coal", years_columns] = (
        df.loc[df['fuel_type'] == "Coal", years_columns]
        .div(df['Region'].map(df_power_coal_intensity).fillna(coal_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_coal_utilization).fillna(coal_avg_utilization), axis=0)
    )

# 2 - gas
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"]
    df.loc[df['fuel_type'] == "Gas", years_columns] = (
        df.loc[df['fuel_type'] == "Gas", years_columns]
        .div(df['Region'].map(df_power_gas_intensity).fillna(gas_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_gas_utilization).fillna(gas_avg_utilization), axis=0)
    )

# 3 - oil
for region in regions_with_extras:
    df = globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"]
    df.loc[df['fuel_type'] == "Oil", years_columns] = (
        df.loc[df['fuel_type'] == "Oil", years_columns]
        .div(df['Region'].map(df_power_oil_intensity).fillna(oil_avg_intensity), axis=0)
        .div((24 * 365))
        .div(df['Region'].map(df_power_oil_utilization).fillna(oil_avg_utilization), axis=0)
    )

# Grouping for aggregated data
df_totalcapacity_nz1550v3_devunfccc = df_totalcapacity_nz1550v3_devunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_nz1550v3_dopunfccc = df_totalcapacity_nz1550v3_dopunfccc.groupby('fuel_type')[years_columns].sum().reset_index()
df_totalcapacity_nz1550v3_global = df_totalcapacity_nz1550v3_global.groupby('fuel_type')[years_columns].sum().reset_index()



# delete extras
del df_power_oil_intensity, df_power_gas_intensity, df_power_coal_intensity
del df_power_oil_utilization, df_power_gas_utilization, df_power_coal_utilization
del df










# In[4]: ADD TOTAL ANNUAL & CUMULATIVE & AVOIDED --- EMISSIONS & CAPACITY FOR EACH COUNTRY
##########################################################################################

# --------------
# set some initial terms: column names, temporary variables to store data from the loops

# Define the columns names for the final DataFrames
new_column_names = ['ghg_annual_cp', 'ghg_annual_nz', 'ghg_annual_nznew', 'ghg_annaul_avoided',
                    'ghg_cumulative_cp', 'ghg_cumulative_nz', 'ghg_cumulative_nznew','ghg_cumulative_avoided',
                    'capacity_annual_cp', 'capacity_annual_nz', 'capacity_annual_nznew', 
                    'capacity_annaul_reduction','capacity_cumulative_reduction']


# List of country codes to iterate over
temp_country_codes = list(map(str.lower, regions_with_extras))

# Dictionary to store each country's DataFrame
temp_country_dfs = {}



# --------------
# this loop goes through each coutnry and scenario (both emissions & capacity) and combines each country into a single dataframe

# Loop through each country code
for country_code in temp_country_codes:

    # this is to select each countrie's respective data to start with
    temp_emissions_currentpolicy = globals()[f'df_emissions_currentpolicy_{country_code}'].copy()
    temp_emissions_netzero = globals()[f'df_emissions_netzero_{country_code}'].copy()
    temp_emissions_nz1550v3 = globals()[f'df_emissions_nz1550v3_{country_code}'].copy()
    temp_totalcapacity_currentpolicy = globals()[f'df_totalcapacity_currentpolicy_{country_code}'].copy()
    temp_totalcapacity_netzero = globals()[f'df_totalcapacity_netzero_{country_code}'].copy()
    temp_totalcapacity_nz1550v3 = globals()[f'df_totalcapacity_nz1550v3_{country_code}'].copy()
    
    
    # Emissions calculations --- total emissions across all fuel types --- and get avoided CP vs NZ15 50%
    temp_emissions_currentpolicy_annual = temp_emissions_currentpolicy[years_columns].sum(axis=0)
    temp_emissions_netzero_annual = temp_emissions_netzero[years_columns].sum(axis=0)
    temp_emissions_nz1550v3_annual = temp_emissions_nz1550v3[years_columns].sum(axis=0)
    temp_emissions_avoided_annual = temp_emissions_currentpolicy_annual - temp_emissions_nz1550v3_annual   

    temp_emissions_currentpolicy_cumulative = temp_emissions_currentpolicy_annual.cumsum()
    temp_emissions_netzero_cumulative = temp_emissions_netzero_annual.cumsum()
    temp_emissions_nz1550v3_cumulative = temp_emissions_nz1550v3_annual.cumsum()
    temp_emissions_avoided_cumulative = temp_emissions_avoided_annual.cumsum()


    # Capacity calculations --- total capacity across all fuel types --- and get avoided CP vs NZ15 50%
    temp_totalcapacity_currentpolicy_annual = temp_totalcapacity_currentpolicy[years_columns].sum(axis=0)
    temp_totalcapacity_netzero_annual = temp_totalcapacity_netzero[years_columns].sum(axis=0)
    temp_totalcapacity_nz1550v3_annual = temp_totalcapacity_nz1550v3[years_columns].sum(axis=0)
    temp_totalcapacity_avoided_annual = temp_totalcapacity_nz1550v3_annual.diff()
    temp_totalcapacity_avoided_cumulative = temp_totalcapacity_avoided_annual.cumsum()


    # Combine into a single DataFrame for the current country
    temp_combined = pd.concat([temp_emissions_currentpolicy_annual, temp_emissions_netzero_annual, temp_emissions_nz1550v3_annual, temp_emissions_avoided_annual,
                             temp_emissions_currentpolicy_cumulative, temp_emissions_netzero_cumulative, temp_emissions_nz1550v3_cumulative, temp_emissions_avoided_cumulative,
                             temp_totalcapacity_currentpolicy_annual, temp_totalcapacity_netzero_annual, temp_totalcapacity_nz1550v3_annual, temp_totalcapacity_avoided_annual,
                             temp_totalcapacity_avoided_cumulative], axis=1)

    # Rename columns
    temp_combined.columns = new_column_names
    
    # Store the DataFrame in the dictionary using the country code as the key
    temp_country_dfs[country_code] = temp_combined



# Access the DataFrames for each country, e.g., df_deu, df_usa, etc.
for country in regions_with_extras:
    globals()[f"df_country_{country.lower()}"] = temp_country_dfs[country.lower()]
    

# delete
del temp_combined, temp_country_codes, temp_country_dfs, country_code, new_column_names
del temp_emissions_avoided_annual, temp_emissions_avoided_cumulative, temp_emissions_currentpolicy_annual, temp_emissions_currentpolicy_cumulative, temp_emissions_nz1550v3_annual, temp_emissions_nz1550v3_cumulative
del temp_totalcapacity_avoided_annual, temp_totalcapacity_avoided_cumulative, temp_totalcapacity_currentpolicy_annual, temp_totalcapacity_nz1550v3_annual
del temp_emissions_currentpolicy, temp_emissions_nz1550v3, temp_totalcapacity_currentpolicy, temp_totalcapacity_nz1550v3










# In[4]: BY FUEL AVOIDED CAPACITY 
#######################################


# get annual total capacity avoided by country
for region in regions_with_extras:
    globals()[f"df_byfuel_avoided_annual_{region.lower()}"] = globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"].copy().assign(
        **globals()[f"df_totalcapacity_nz1550v3_{region.lower()}"][years_columns].diff(axis=1)
    )


# now get total avoided capacity by country and fuel
for region in regions_with_extras:
    annual_df = globals()[f"df_byfuel_avoided_annual_{region.lower()}"]
    globals()[f"df_byfuel_avoided_cumulative_{region.lower()}"] = annual_df.copy().assign(
        **{col: annual_df[years_columns].cumsum(axis=1)[col] for col in years_columns}
    )


del annual_df, region
del country
del df_power_coal, df_power_gas, df_power_oil
del df_power_coal_intensity_series, df_power_gas_intensity_series, df_power_oil_intensity_series
del df_power_coal_utilization_series, df_power_gas_utilization_series, df_power_oil_utilization_series
del coal_avg_intensity, coal_avg_utilization, gas_avg_intensity, gas_avg_utilization, oil_avg_intensity, oil_avg_utilization
del temp_emissions_netzero, temp_emissions_netzero_annual, temp_emissions_netzero_cumulative, temp_totalcapacity_netzero, temp_totalcapacity_netzero_annual
del regions_with_extras
del df_change_currentpolicy, df_change_netzero, df_change_nz1550v2


# In[]

# # export data

# # --------------
# # countries
# df_country_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.1 - country - DEU.xlsx', index = False)
# df_country_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.2 - country - IDN.xlsx', index = False)
# df_country_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.3 - country - IND.xlsx', index = False)
# df_country_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.4 - country - TUR.xlsx', index = False)
# df_country_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.5 - country - USA.xlsx', index = False)
# df_country_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.6 - country - VNM.xlsx', index = False)
# df_country_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.7 - country - POL.xlsx', index = False)
# df_country_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.8 - country - KAZ.xlsx', index = False)
# df_country_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.9 - country - EMDE.xlsx', index = False)
# df_country_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.10 - country - GLOBAL.xlsx', index = False)
# df_country_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.11 - country - ZAF.xlsx', index = False)
# df_country_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.12 - country - BGD.xlsx', index = False)
# df_country_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.13 - country - DEVUNFCCC.xlsx', index = False)
# df_country_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.14 - country - DOPUNFCCC.xlsx', index = False)
# df_country_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.15 - country - CHN.xlsx', index = False)
# df_country_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.16 - country - MEX.xlsx', index = False)
# df_country_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.17 - country - IRN.xlsx', index = False)
# df_country_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.18 - country - THA.xlsx', index = False)
# df_country_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/1.19 - country - EGY.xlsx', index = False)




# # --------------
# # emissions  - current policy
# df_emissions_currentpolicy_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.1 - emissions - current policy - DEU.xlsx', index = False)
# df_emissions_currentpolicy_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.2 - emissions - current policy - IDN.xlsx', index = False)
# df_emissions_currentpolicy_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.3 - emissions - current policy - IND.xlsx', index = False)
# df_emissions_currentpolicy_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.4 - emissions - current policy - TUR.xlsx', index = False)
# df_emissions_currentpolicy_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.5 - emissions - current policy - USA.xlsx', index = False)
# df_emissions_currentpolicy_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.6 - emissions - current policy - VNM.xlsx', index = False)
# df_emissions_currentpolicy_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.7 - emissions - current policy - POL.xlsx', index = False)
# df_emissions_currentpolicy_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.8 - emissions - current policy - KAZ.xlsx', index = False)
# df_emissions_currentpolicy_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.9 - emissions - current policy - EMDE.xlsx', index = False)
# df_emissions_currentpolicy_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.10 - emissions - current policy - GLOBAL.xlsx', index = False)
# df_emissions_currentpolicy_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.11 - emissions - current policy - ZAF.xlsx', index = False)
# df_emissions_currentpolicy_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.12 - emissions - current policy - BGD.xlsx', index = False)
# df_emissions_currentpolicy_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.13 - emissions - current policy - DEVUNFCCC.xlsx', index = False)
# df_emissions_currentpolicy_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.14 - emissions - current policy - DOPUNFCCC.xlsx', index = False)
# df_emissions_currentpolicy_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.15 - emissions - current policy - CHN.xlsx', index = False)
# df_emissions_currentpolicy_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.16 - emissions - current policy - MEX.xlsx', index = False)
# df_emissions_currentpolicy_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.17 - emissions - current policy - IRN.xlsx', index = False)
# df_emissions_currentpolicy_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.18 - emissions - current policy - THA.xlsx', index = False)
# df_emissions_currentpolicy_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/2.19 - emissions - current policy - EGY.xlsx', index = False)



# # emissions  - netzero
# df_emissions_netzero_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.1 - emissions - netzero - DEU.xlsx', index = False)
# df_emissions_netzero_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.2 - emissions - netzero - IDN.xlsx', index = False)
# df_emissions_netzero_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.3 - emissions - netzero - IND.xlsx', index = False)
# df_emissions_netzero_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.4 - emissions - netzero - TUR.xlsx', index = False)
# df_emissions_netzero_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.5 - emissions - netzero - USA.xlsx', index = False)
# df_emissions_netzero_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.6 - emissions - netzero - VNM.xlsx', index = False)
# df_emissions_netzero_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.7 - emissions - netzero - POL.xlsx', index = False)
# df_emissions_netzero_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.8 - emissions - netzero - KAZ.xlsx', index = False)
# df_emissions_netzero_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.9 - emissions - netzero - EMDE.xlsx', index = False)
# df_emissions_netzero_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.10 - emissions - netzero - GLOBAL.xlsx', index = False)
# df_emissions_netzero_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.11 - emissions - netzero - ZAF.xlsx', index = False)
# df_emissions_netzero_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.12 - emissions - netzero - BGD.xlsx', index = False)
# df_emissions_netzero_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.13 - emissions - netzero - DEVUNFCCC.xlsx', index = False)
# df_emissions_netzero_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.14 - emissions - netzero - DOPUNFCCC.xlsx', index = False)
# df_emissions_netzero_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.15 - emissions - netzero - CHN.xlsx', index = False)
# df_emissions_netzero_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.16 - emissions - netzero - MEX.xlsx', index = False)
# df_emissions_netzero_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.17 - emissions - netzero - IRN.xlsx', index = False)
# df_emissions_netzero_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.18 - emissions - netzero - THA.xlsx', index = False)
# df_emissions_netzero_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/3.19 - emissions - netzero - EGY.xlsx', index = False)



# # emissions  - net zero 1.5C 50%
# df_emissions_nz1550v2_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.1 - emissions - net zero 15C 50% - DEU.xlsx', index = False)
# df_emissions_nz1550v2_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.2 - emissions - net zero 15C 50% - IDN.xlsx', index = False)
# df_emissions_nz1550v2_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.3 - emissions - net zero 15C 50% - IND.xlsx', index = False)
# df_emissions_nz1550v2_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.4 - emissions - net zero 15C 50% - TUR.xlsx', index = False)
# df_emissions_nz1550v2_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.5 - emissions - net zero 15C 50% - USA.xlsx', index = False)
# df_emissions_nz1550v2_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.6 - emissions - net zero 15C 50% - VNM.xlsx', index = False)
# df_emissions_nz1550v2_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.7 - emissions - net zero 15C 50% - POL.xlsx', index = False)
# df_emissions_nz1550v2_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.8 - emissions - net zero 15C 50% - KAZ.xlsx', index = False)
# df_emissions_nz1550v2_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.9 - emissions - net zero 15C 50% - EMDE.xlsx', index = False)
# df_emissions_nz1550v2_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.10 - emissions - net zero 15C 50% - GLOBAL.xlsx', index = False)
# df_emissions_nz1550v2_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.11 - emissions - net zero 15C 50% - ZAF.xlsx', index = False)
# df_emissions_nz1550v2_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.12 - emissions - net zero 15C 50% - BGD.xlsx', index = False)
# df_emissions_nz1550v2_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.13 - emissions - net zero 15C 50% - DEVUNFCCC.xlsx', index = False)
# df_emissions_nz1550v2_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.14 - emissions - net zero 15C 50% - DOPUNFCCC.xlsx', index = False)
# df_emissions_nz1550v2_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.15 - emissions - net zero 15C 50% - CHN.xlsx', index = False)
# df_emissions_nz1550v2_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.16 - emissions - net zero 15C 50% - MEX.xlsx', index = False)
# df_emissions_nz1550v2_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.17 - emissions - net zero 15C 50% - IRN.xlsx', index = False)
# df_emissions_nz1550v2_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.18 - emissions - net zero 15C 50% - THA.xlsx', index = False)
# df_emissions_nz1550v2_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/4.19 - emissions - net zero 15C 50% - EGY.xlsx', index = False)



# # --------------
# # total capacity  - current policy
# df_totalcapacity_currentpolicy_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.1 - total capacity - current policy - DEU.xlsx', index = False)
# df_totalcapacity_currentpolicy_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.2 - total capacity - current policy - IDN.xlsx', index = False)
# df_totalcapacity_currentpolicy_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.3 - total capacity - current policy - IND.xlsx', index = False)
# df_totalcapacity_currentpolicy_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.4 - total capacity - current policy - TUR.xlsx', index = False)
# df_totalcapacity_currentpolicy_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.5 - total capacity - current policy - USA.xlsx', index = False)
# df_totalcapacity_currentpolicy_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.6 - total capacity - current policy - VNM.xlsx', index = False)
# df_totalcapacity_currentpolicy_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.7 - total capacity - current policy - POL.xlsx', index = False)
# df_totalcapacity_currentpolicy_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.8 - total capacity - current policy - KAZ.xlsx', index = False)
# df_totalcapacity_currentpolicy_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.9 - total capacity - current policy - EMDE.xlsx', index = False)
# df_totalcapacity_currentpolicy_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.10 - total capacity - current policy - GLOBAL.xlsx', index = False)
# df_totalcapacity_currentpolicy_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.11 - total capacity - current policy - ZAF.xlsx', index = False)
# df_totalcapacity_currentpolicy_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.12 - total capacity - current policy - BGD.xlsx', index = False)
# df_totalcapacity_currentpolicy_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.13 - total capacity - current policy - DEVUNFCCC.xlsx', index = False)
# df_totalcapacity_currentpolicy_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.14 - total capacity - current policy - DOPUNFCCC.xlsx', index = False)
# df_totalcapacity_currentpolicy_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.15 - total capacity - current policy - CHN.xlsx', index = False)
# df_totalcapacity_currentpolicy_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.16 - total capacity - current policy - MEX.xlsx', index = False)
# df_totalcapacity_currentpolicy_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.17 - total capacity - current policy - IRN.xlsx', index = False)
# df_totalcapacity_currentpolicy_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.18 - total capacity - current policy - THA.xlsx', index = False)
# df_totalcapacity_currentpolicy_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/5.19 - total capacity - current policy - EGY.xlsx', index = False)



# # total capacity   - netzero
# df_totalcapacity_netzero_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.1 - total capacity - netzero - DEU.xlsx', index = False)
# df_totalcapacity_netzero_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.2 - total capacity - netzero - IDN.xlsx', index = False)
# df_totalcapacity_netzero_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.3 - total capacity - netzero - IND.xlsx', index = False)
# df_totalcapacity_netzero_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.4 - total capacity - netzero - TUR.xlsx', index = False)
# df_totalcapacity_netzero_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.5 - total capacity - netzero - USA.xlsx', index = False)
# df_totalcapacity_netzero_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.6 - total capacity - netzero - VNM.xlsx', index = False)
# df_totalcapacity_netzero_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.7 - total capacity - netzero - POL.xlsx', index = False)
# df_totalcapacity_netzero_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.8 - total capacity - netzero - KAZ.xlsx', index = False)
# df_totalcapacity_netzero_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.9 - total capacity - netzero - EMDE.xlsx', index = False)
# df_totalcapacity_netzero_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.10 - total capacity - netzero - GLOBAL.xlsx', index = False)
# df_totalcapacity_netzero_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.11 - total capacity - netzero - ZAF.xlsx', index = False)
# df_totalcapacity_netzero_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.12 - total capacity - netzero - BGD.xlsx', index = False)
# df_totalcapacity_netzero_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.13 - total capacity - netzero - DEVUNFCCC.xlsx', index = False)
# df_totalcapacity_netzero_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.14 - total capacity - netzero - DOPUNFCCC.xlsx', index = False)
# df_totalcapacity_netzero_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.15 - total capacity - netzero - CHN.xlsx', index = False)
# df_totalcapacity_netzero_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.16 - total capacity - netzero - MEX.xlsx', index = False)
# df_totalcapacity_netzero_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.17 - total capacity - netzero - IRN.xlsx', index = False)
# df_totalcapacity_netzero_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.18 - total capacity - netzero - THA.xlsx', index = False)
# df_totalcapacity_netzero_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/6.19 - total capacity - netzero - EGY.xlsx', index = False)



# # total capacity   - net zero 1.5C 50%
# df_totalcapacity_nz1550v2_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.1 - total capacity - net zero 15C 50% - DEU.xlsx', index = False)
# df_totalcapacity_nz1550v2_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.2 - total capacity - net zero 15C 50% - IDN.xlsx', index = False)
# df_totalcapacity_nz1550v2_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.3 - total capacity - net zero 15C 50% - IND.xlsx', index = False)
# df_totalcapacity_nz1550v2_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.4 - total capacity - net zero 15C 50% - TUR.xlsx', index = False)
# df_totalcapacity_nz1550v2_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.5 - total capacity - net zero 15C 50% - USA.xlsx', index = False)
# df_totalcapacity_nz1550v2_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.6 - total capacity - net zero 15C 50% - VNM.xlsx', index = False)
# df_totalcapacity_nz1550v2_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.7 - total capacity - net zero 15C 50% - POL.xlsx', index = False)
# df_totalcapacity_nz1550v2_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.8 - total capacity - net zero 15C 50% - KAZ.xlsx', index = False)
# df_totalcapacity_nz1550v2_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.9 - total capacity - net zero 15C 50% - EMDE.xlsx', index = False)
# df_totalcapacity_nz1550v2_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.10 - total capacity - net zero 15C 50% - GLOBAL.xlsx', index = False)
# df_totalcapacity_nz1550v2_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.11 - total capacity - net zero 15C 50% - ZAF.xlsx', index = False)
# df_totalcapacity_nz1550v2_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.12 - total capacity - net zero 15C 50% - BGD.xlsx', index = False)
# df_totalcapacity_nz1550v2_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.13 - total capacity - net zero 15C 50% - DEVUNFCCC.xlsx', index = False)
# df_totalcapacity_nz1550v2_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.14 - total capacity - net zero 15C 50% - DOPUNFCCC.xlsx', index = False)
# df_totalcapacity_nz1550v2_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.15 - total capacity - net zero 15C 50% - CHN.xlsx', index = False)
# df_totalcapacity_nz1550v2_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.16 - total capacity - net zero 15C 50% - MEX.xlsx', index = False)
# df_totalcapacity_nz1550v2_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.17 - total capacity - net zero 15C 50% - IRN.xlsx', index = False)
# df_totalcapacity_nz1550v2_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.18 - total capacity - net zero 15C 50% - THA.xlsx', index = False)
# df_totalcapacity_nz1550v2_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/7.19 - total capacity - net zero 15C 50% - EGY.xlsx', index = False)



# # --------------
# # by fuel --- annual avoided
# df_byfuel_avoided_annual_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.1 - avoided capacity - annual - DEU.xlsx', index = False)
# df_byfuel_avoided_annual_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.2 - avoided capacity - annual - IDN.xlsx', index = False)
# df_byfuel_avoided_annual_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.3 - avoided capacity - annual - IND.xlsx', index = False)
# df_byfuel_avoided_annual_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.4 - avoided capacity - annual - TUR.xlsx', index = False)
# df_byfuel_avoided_annual_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.5 - avoided capacity - annual - USA.xlsx', index = False)
# df_byfuel_avoided_annual_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.6 - avoided capacity - annual - VNM.xlsx', index = False)
# df_byfuel_avoided_annual_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.7 - avoided capacity - annual - POL.xlsx', index = False)
# df_byfuel_avoided_annual_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.8 - avoided capacity - annual - KAZ.xlsx', index = False)
# df_byfuel_avoided_annual_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.9 - avoided capacity - annual - EMDE.xlsx', index = False)
# df_byfuel_avoided_annual_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.10 - avoided capacity - annual - GLOBAL.xlsx', index = False)
# df_byfuel_avoided_annual_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.11 - avoided capacity - annual - ZAF.xlsx', index = False)
# df_byfuel_avoided_annual_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.12 - avoided capacity - annual - BGD.xlsx', index = False)
# df_byfuel_avoided_annual_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.13 - avoided capacity - annual - DEVUNFCCC.xlsx', index = False)
# df_byfuel_avoided_annual_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.14 - avoided capacity - annual - DOPUNFCCC.xlsx', index = False)
# df_byfuel_avoided_annual_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.15 - avoided capacity - annual - CHN.xlsx', index = False)
# df_byfuel_avoided_annual_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.16 - avoided capacity - annual - MEX.xlsx', index = False)
# df_byfuel_avoided_annual_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.17 - avoided capacity - annual - IRN.xlsx', index = False)
# df_byfuel_avoided_annual_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.18 - avoided capacity - annual - THA.xlsx', index = False)
# df_byfuel_avoided_annual_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/8.19 - avoided capacity - annual - EGY.xlsx', index = False)



# # by fuel --- cumulative avoided
# df_byfuel_avoided_cumulative_deu.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.1 - avoided capacity - cumulative - DEU.xlsx', index = False)
# df_byfuel_avoided_cumulative_idn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.2 - avoided capacity - cumulative - IDN.xlsx', index = False)
# df_byfuel_avoided_cumulative_ind.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.3 - avoided capacity - cumulative - IND.xlsx', index = False)
# df_byfuel_avoided_cumulative_tur.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.4 - avoided capacity - cumulative - TUR.xlsx', index = False)
# df_byfuel_avoided_cumulative_usa.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.5 - avoided capacity - cumulative - USA.xlsx', index = False)
# df_byfuel_avoided_cumulative_vnm.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.6 - avoided capacity - cumulative - VNM.xlsx', index = False)
# df_byfuel_avoided_cumulative_pol.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.7 - avoided capacity - cumulative - POL.xlsx', index = False)
# df_byfuel_avoided_cumulative_kaz.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.8 - avoided capacity - cumulative - KAZ.xlsx', index = False)
# df_byfuel_avoided_cumulative_emde.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.9 - avoided capacity - cumulative - EMDE.xlsx', index = False)
# df_byfuel_avoided_cumulative_global.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.10 - avoided capacity - cumulative - GLOBAL.xlsx', index = False)
# df_byfuel_avoided_cumulative_zaf.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.11 - avoided capacity - cumulative - ZAF.xlsx', index = False)
# df_byfuel_avoided_cumulative_bgd.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.12 - avoided capacity - cumulative - BGD.xlsx', index = False)
# df_byfuel_avoided_cumulative_devunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.13 - avoided capacity - cumulative - DEVUNFCCC.xlsx', index = False)
# df_byfuel_avoided_cumulative_dopunfccc.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.14 - avoided capacity - cumulative - DOPUNFCCC.xlsx', index = False)
# df_byfuel_avoided_cumulative_chn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.15 - avoided capacity - cumulative - CHN.xlsx', index = False)
# df_byfuel_avoided_cumulative_mex.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.16 - avoided capacity - cumulative - MEX.xlsx', index = False)
# df_byfuel_avoided_cumulative_irn.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.17 - avoided capacity - cumulative - IRN.xlsx', index = False)
# df_byfuel_avoided_cumulative_tha.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.18 - avoided capacity - cumulative - THA.xlsx', index = False)
# df_byfuel_avoided_cumulative_egy.to_excel('2 - output/script 6.1 - Power sector - By country - Emissions & Capacity - Annual Cumulative Avoided/9.19 - avoided capacity - cumulative - EGY.xlsx', index = False)









