# Bpa Fetch
A tool to fetch and parse historical Balancing Authority (power generation) data published by the Bonneville Power Administration (BPA). 
Data is provided in 5 minute increments as far back as 2007 and the full set can be found [here (under item 5)](https://transmission.bpa.gov/Business/Operations/Wind/default.aspx).

## Output Columns
The following columns are in the output data, all power numbers are in megawatts. Note that the available columns has changed over time so what columns are present will depend on what years you've pulled.
1) `time` - UTC timestamp for the data. **[Always Available]**
2) `load` - Load in BPA area. Note that BPA provides power to other Transmission Authorities so load will likely not be equal to the sum of generation. **[Always Available]**
3) `nuclear_generation` - Generation from nuclear sources. **[Available 2017 Onwards]**
4) `hydro_generation` - Generation from hydroelectric sources. **[Always Available]**
5) `wind_generation` - Generation from wind farms. **[Always Available]**
6) `fossil_generation` - Generation from fossil fuel and biomass sources. **[Available 2017 Onwards]**
7) `solar_generation` - Generation from commercial solar farms. **[Available 2022 Onwards]**
8) `thermal_generation` - Generation from thermal sources including fossil fuels and nuclear. **[Available Until 2017]**
9) `wind_forecast` - Forecasted output provided by operators. **[Available 2018 Onward]**
10) `wind_basepoint` - Sum of dispatches when BPA is participating in the EIM, otherwise operator forecasts. **[Available 2022 Onward]**
11) `solar_forecast` - Forecasted output provided by operators. **[Available 2022 Onward]**
12) `solar_basepoint` - Sum of dispatches when BPA is participating in the EIM, otherwise operator forecasts. **[Available 2022 Onward]**
13) `year` - Year the data is for. **[Always Available]**

**NOTE**: For wind farms with output split between Transmission Authorities, only the portion sent to BPA is reported.

## Installation
This tool is distributed through PyPi and can be installed using `pip install bpa_fetch`

## Usage

`python bpa_fetch.py [DATES ...] -r -o file.format -f format`

The follow arguments are available:
- `DATES` : A list of space seperated years to pull (ig: `2010 2013 2020`). If no dates are provided, all years will be pulled.
- `--out -o`: The file to save pulled data to. If not specified, `out-{timestamp}.[format]` will be used.
- `--range -r`: If this flag is used, two years will be expected for `DATES` and all years between `DATE 1` and `DATE 2` will be pulled (inclusive).
- `--format -f`: The format of the saved data, options are `Parquet`<sup>1</sup> and `Pandas`. When using pandas, the default file extension is `.pkl.gz` unless set using `-o`. Defaults to `PARQUET`

If the package is installed with pip, the script `bpa-fetch` is available with the same arguments and `python bpa_fetch.py`
<br><sup>1</sup> - [Parquet](https://parquet.apache.org/docs/overview/) is a file format developed by the Apache Software Foundation for data analysis workloads and provides small file sizes and fast, efficient queries. To view and work with Parquet, tools like [Tad](https://www.tadviewer.com/) and [DuckDB](https://duckdb.org/) can be used.

### Examples
- To pull all years and save as the default filename and format: `python bpa_fetch.py`
- To pull all years between 2010 & 2016 and save as pandas to the default filename: `python bpa_fetch.py 2010 2016 -r -f pandas`
- To pull years 2012, 2015, and 2016 and save as a parquet to `output/year-data.parquet`: `python bpa_fetch.py 2012 2015 2016 -o "output/year-data.parquet"`
- To pull only 2017: `python bpa_fetch.py 2017`


## User Functions
The function `bpa_fetch.pull_years` is also available and returns a pandas Dataframe of the pulled data.
It takes two arguments:
- `years` is a list of years (as `ints`) to pull, if `None` than all years will be pulled.
- `working_dir` is a `pathlib.Path` object pointing to the directory to use during execution. Defaults to `./bpa_data`


## Caching
To speed up execution and reduce network traffic, rudimentary caching system is used that saves the BPA files to disk at `working_dir` on first run and then only downloads the current year going forwards.
This implementation has some potential issues including failing to pull updated data if run in the new year, leaving the previous year missing data. Improvements to this system are in development 
