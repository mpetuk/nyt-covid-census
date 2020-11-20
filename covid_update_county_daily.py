import numpy as np
import pandas as pd
import datetime
import os
import urllib.request
import sys

# New York Times Covid-19 data
# Updated daily: new rows added

url_covid = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

# Census data: continental US population by county 
# Updated once a year: new columns added
# https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv


# Download census file locally unless already downloaded:

CENSUS_URL = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv"
CENSUS_PATH = os.path.join(os.path.dirname(os.path.realpath('__file__')),"census")

def fetch_census_data(census_url=CENSUS_URL, census_path=CENSUS_PATH):
    if not os.path.isdir(census_path):
        os.makedirs(census_path)
    file_path = os.path.join(census_path, "counties_est2019.csv")
    if not os.path.isfile(file_path):
        print('Downloading census file')
        urllib.request.urlretrieve(census_url, file_path)
    else:
        print('Census file exists; skipping download')

fetch_census_data()

# Load columns of interest from  census file into pandas dataframe
# Note: columns 3 and 4 are 'state' and 'county' 2-digit and 3-digit codes, respectively, with leading zeros where applicable

census_df = pd.read_csv(os.path.join(CENSUS_PATH, "counties_est2019.csv")
                        , header=None
                        , skiprows=1
                        , encoding='latin-1'
                        , usecols =[0,3,4,18]
                        , dtype = {3:str,4:str,18:np.int64}) 

census_df.columns = ['sumlev','state','county','popestimate2019']

# Column 'sumlev' identifies summary level: 50 == county, 40 == state
census_counties_df = pd.DataFrame(census_df[census_df['sumlev']==50])

# Create 5-digit long fips column
census_counties_df['fips'] = census_counties_df['state'] + census_counties_df['county']


# Download daily NYT Covid-19 data
covid_df = pd.read_csv(url_covid
                       , dtype = {'date': str, 'fips':str}
                       , parse_dates = ['date'])

# Merge Covid data with Census data on fips with Covid data as a driver (hence left join)
# indicator = True adds column '_merge' to the dataframe - useful for quantifying mis/matches 
combo_df = covid_df.merge(census_counties_df[['fips','popestimate2019']]
                          , how = 'left'
                          , on = 'fips'
                          , indicator = True)



# In the  Covid data there is a county 'New York City' - not a real county --> doesn't match to Census data
# New York City comprises of 5 counties (none of them are present in NYT Covid data)
# Filling missing population for 'New York City' with sum of populations of 5 of its counties, 8,336,817
# census_counties_df[census_counties_df['fips'].isin(["36005","36047","36061","36081","36085"])].popestimate2019.sum()
# 8336817

combo_df.loc[(combo_df['popestimate2019'].isna()) & (combo_df['county']=='New York City'), 'popestimate2019'] = 8336817

# Dropping records for the rest of the unmatched counties from Covid data for now 
combo_df = combo_df[(combo_df['_merge']!='left_only')|(combo_df['county']=='New York City')]

# Filling missing fips for 'New York City' with a made-up value to retain it in the summary data
combo_df.loc[combo_df['fips'].isna(),'fips'] =  'nycny'


# Add column capturing start date of the reporting week
combo_df['week_start'] = combo_df['date'].dt.to_period('W').apply(lambda r: r.start_time)

# Create timestamp to be used in the output file name
timestamp = datetime.datetime.today().strftime('%Y%m%d')

# Create weekly and daily summary outputs:

for i in ['date','week_start']:

    # Create dataframe with cumulative sums for cases and deaths to date
    cumulative_df = combo_df[[i,'fips','cases','deaths']]\
                            .groupby(['fips',i], sort=False)\
                            .sum()\
                            .groupby(by='fips',sort=False)\
                            .cumsum()\
                            .reset_index()

    # Rename columns before merge
    cumulative_df.columns = ['fips',i,'cumulative_cases','cumulative_deaths']
    
    if i == 'week_start':
        sumlev = 'weekly'
        
        summary_df =  combo_df[[i,'fips','county','state','popestimate2019','cases','deaths']]\
                                   .groupby([i,'fips','county','state','popestimate2019'])\
                                   .agg({'cases':'sum','deaths':'sum'})\
                                   .reset_index()
    else:
        sumlev = 'daily'
        summary_df = pd.DataFrame(combo_df)
   
    # Add cumulative metrics back to the combined covid and census dataframe
    summary_df = summary_df.merge(cumulative_df, how = 'inner', on = [i,'fips'])
   
    # Add column capturing load date of the data
    summary_df['load_date'] = pd.to_datetime('today').date()
        

    # Output dataframe as csv to output folder
    output_path = os.path.join(os.path.dirname(os.path.realpath('__file__')),"output", sumlev)
    if not os.path.isdir(output_path):
       os.makedirs(output_path)

    outfile_path = os.path.join(output_path, 'nyt_covid_' + timestamp + '.csv')

    summary_df.to_csv(open(outfile_path,'w'), index=False)


