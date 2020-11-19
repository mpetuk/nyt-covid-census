# Daily and Weekly Updates of Nationwide Infection Counts by County

This repo is designed to prepare daily and weekly COVID-19 summaries by county using the two data sources below:

* New York Times COVID-19 Data ([source](https://github.com/nytimes/covid-19-data/blob/master/README.md))

* 2019 Population Estimate Data 2019 Population Estimate Data ([source](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html))

Everything is handled by _covid_update_county_daily.py_ script, i.e.:
<ol>
<li>Downloading COVID and Census data 
<ul>
<li>Census data, being practically static, is downloaded once and stored in ./census folder until next year data becomes available</li>
</ul>
<li>Combining them by appending 2019 (most recent) county population estimates to COVID-19 data</li>
<li>Summarizing data by day and FIPS as well as by week and FIPS</li>
<li>Outputing summary files to ./output/daily and ./output/weekly folders, respectively</li>
</ol>
<p>
For every FIPS code<sup>1</sup> and date<sup>2</sup>, the following metrics are provided: population, daily/weekly
cases, daily/weekly deaths, cumulative cases to date, and cumulative death counts to
date.<br>

The script is designed to be run daily and provide the latest COVID-19 data available at time of execution. 
At the very first execution, the script is designed to create folders structure referred to above.
</p>
<sup>1</sup> <sub>there are missing FIPS in COVID-19 data as well as FIPS that don't match to Census data. These are currently omitted from the output with the exception of New York City</sub>

<sup>2</sup> <sub>every date available in COVID-19 data. Gaps in dates are possible and have not been addressed at this point </sub>

## Learnings & thoughts about the data sources:
<ul>
<li>COVID-19:</li>
<ul>
<li>contains 742,008 records</li>
<li>contains data on 3,217 FIPS</li>
<li>unlike Census data, contains data for US territories</li>
<ul>
<li>FIPS > 60000</li>
</ul>
<li>contains records with missing FIPS (7,068 or ~1%)</li>
<ul>
<li> every state has at least one such record</li>
</ul>
<ul>
<li>there are 4 distinct counties with missing FIPS:'New York City', 'Unknown', 'Kansas City', and 'Joplin' </li>
<ul>
<li> 'New York City' is not a county; instead it comprises of 5 counties ("36005","36047","36061","36081","36085": none of these are in the Covid file) - this has been used to fill missing population for 'New York City' records</li>
<li> 'Joplin' is not a county; it is the largest city in Jasper County, Missouri</li>
<li> 'Kansas City' is not a county; most of it lies within Jackson County, Missouri</li>
<li> there are records for both, Jasper and Jackson counties - will need consolidation</li>
</li>
</ul>
</ul>
<li>contains records with county == 'Uknown'</li>
<ul>
<li> all of such records have missing FIPS</li>
</ul>
<li>contains data for 302 days in the range of (2020-01-21 and 2020-11-17 as of 2020-11-18</li>
<ul>
<li> only one county has data for all 302 days (FIPS ==53061 or Snohomish County in Washington)</li>
<li> average number of reporting days per county is 228</li>
<li> one county, Loving in Texas (FIPS == 48301, which is Blanco County in Census file), has only one record: for 2020-11-17</li>
</ul>
<li> county names for the same FIPS can be different from the Census ones</li>
</ul>
<li>Census:</li>
<ul>
<li>carries records for continental US only</li>
<li>contains 3,142 records, one for each FIPS (75 FIPS less than COVID-19 data)</li>
<li>contains 164 columns, with 16 groups of yearly metrics</li>
<li>need to concatinate state and county codes to get FIPS</li>
</ul>


## How you sanity checked your output
<ul>
<li>sum of county's daily/weekly metrics should be equal to the most recent cumulative ones: compare cases and deaths summed to date and fips level with cumulative cases and deaths retrieved from the records with maximum date</li>
<li>cumulative metrics should not decrease overtime within each county - ranks (without ties (method = first)) based on date and cumulative metrics should coincide</li>
<li>weekly summary file should be smaller than daily by the factor of ~7</li>
</ul>

## Things you would add given more time

<ul>
<li>add logging</li>
<li>reconcile the rest of the records with FIPS missing (and county is not 'Uknown') or not matching Census (US territories)</li>
<ul>
<li>get population for US territories' counties</li>
</ul>
<li>add downloading of a new Census file based on current date and the date when next year's data becomes available (once a year)</li>
<li>choose population metric based on current date </li>
<li>process only net new/delta records from COVID-19 data and change structure to update existing report with new data points</l>
<li>consider adding records for missing dates so that each county has the same number of records - to help with dashboards, charts, and other representations of time series data</l>
</ul>


