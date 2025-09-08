from requests import get as webget
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from pandas import DataFrame, Series, read_excel, concat, ArrowDtype
from pyarrow import Table, timestamp, scalar as pa_scalar
from pyarrow.compute import field as pa_field
from pyarrow.parquet import ParquetWriter
from numpy import isnan
from pathlib import Path

__version__ = "1.0.1"


# Contains a directory of BPA historical power generation data
_BPA_SRC = "https://transmission.bpa.gov/Business/Operations/Wind/default.aspx"
_UA = {"User-Agent": f"BPA-Puller/{__version__}"}
_DEFAULT_OUT_DIR = Path("bpa_data")
_PST = ZoneInfo("America/Los_Angeles")


def _pdt_parse(dates: Series) -> Series:
    # Daylight savings ends at 1am on the first Sunday of November
    # Start by figuring out what date is the first sunday of september for the given year
    # Then take its iso DOW and subtract it from 8, then set the result to be the new day
    # Example: 2021-11-1 is iso DOW 1, so 8-1=7 -> First sunday is on 2021-11-7
    # Example: 2022-11-1 is iso DOW 2, so 8-2=6 -> First sunday is on 2021-11-6
    nov_first = datetime(year=datetime.strptime(dates[0], "%m/%d/%y %H:%M").year, month=11, day=1, hour=1, minute=0)
    end_dst = nov_first.replace(day=8-nov_first.isoweekday()).strftime("%m/%d/%y %H:%M")

    first_seen, second_seen = False, False  # Tracking vars
    parsed_dates = []
    for ts in dates:
        if ts == end_dst:  # Check for 1am on the end of DST
            if first_seen: second_seen = True  # Second time we've seen it
            else: first_seen = True  # First time

        new_ts = datetime.strptime(ts, "%m/%d/%y %H:%M")

        if second_seen: new_ts.replace(tzinfo=_PST, fold=1)  # If we're on the second round of 1ams, set post-DST value
        else: new_ts.replace(tzinfo=_PST)  # Else just parse normally
        parsed_dates.append(int(new_ts.timestamp()))

    return Series(parsed_dates)

def _float_fix(data: Series) -> Series:
    """Cast mixed nulls ints and floats to only ints and nulls"""
    corrected = []
    for i in data:
        if issubclass(type(i), int): corrected.append(int(i))
        elif issubclass(type(i), float):
            if isnan(i): corrected.append(None)
            else: corrected.append(int(i))
        elif isinstance(i, str): corrected.append(None)
        else: print(f"Couldn't parse {repr(i)}")

    return Series(data=corrected, dtype="int32[pyarrow]")

def pull_years(years: list = None, working_dir: Path = _DEFAULT_OUT_DIR) -> DataFrame:
    # Ensure directory structure is present
    if not working_dir.is_dir(): working_dir.mkdir(parents=True)

    # region Fetch Files
    # Pull the BPA's "Generation & Total Load" Page and parse into a beautiful soup (bs) object
    page_data = webget(url=_BPA_SRC, params=_UA).content
    bs = BeautifulSoup(page_data, "html.parser")

    # Find the list of links to data and download each to disk
    files = []
    for a in bs.find(attrs={"id": "OPIContent_FileTable"}).find_all("a"):
        name: str = a.getText()  # get the year
        href = a.get("href")  # Relative link to history file
        file_type = href.split(".")[-1]  # Get type (XLS or XLSX)
        link: str = urljoin(_BPA_SRC, href)  # Build full file URL

        if years and int(name) not in years: continue  # Only get specified years. If years is None, all are pulled

        full_path = working_dir / (name + '.' + file_type)  # Build path on disk
        files.append(full_path)

        # TODO - Better caching/checking scheme
        current_year = str(datetime.now().year)
        if not full_path.exists() or name == current_year:
            print(f"Pulling '{link}' for {full_path}")
            full_path.write_bytes(webget(url=link, params=_UA).content)
        else:
            print(f"'{link}' already exists at {full_path} - skipping")

    print(f"Finished pulling {len(files)} files")
    # endregion
    # region Parse Files
    year_data = []
    for file in files:
        year = int(file.stem)
        print(f"Parsing '{file}'")

        if year >= 2022:
            # noinspection PyTypeChecker
            data = read_excel(
                file, sheet_name="Data",
                header=1, names=[
                    "time",
                    "wind_forecast", "wind_basepoint", "wind_generation",
                    "load", "hydro_generation", "fossil_generation", "nuclear_generation",
                    "solar_forecast", "solar_basepoint", "solar_generation"
                ], usecols="B:I,K:M",
                na_filter=False, engine="openpyxl"
            )
            data["time"] = data["time"].map(lambda t: datetime.strptime(t, "%m/%d/%y %H:%M").replace(tzinfo=UTC).timestamp()).astype("int64")
            year_data.append(data)
        elif 2017 <= year <= 2021:
            # 2017 has two extra rows in the header
            header_offset = 25 if year == 2017 else 23

            # noinspection PyTypeChecker
            multi_tables: dict[str, DataFrame] = read_excel(
                file, sheet_name=["January-June", "July-December"],
                header=header_offset, names=[
                    "time",
                    "wind_forecast", "wind_generation",
                    "load", "hydro_generation", "fossil_generation", "nuclear_generation"
                ], usecols="A:G",
                na_filter=False, engine="xlrd"
            )

            df_jan = multi_tables["January-June"]  # Parse timestamps normally, ensuring PST is used
            df_jan["time"] = df_jan["time"].map(lambda t: int(datetime.strptime(t, "%m/%d/%y %H:%M").replace(tzinfo=_PST).timestamp())).astype("int64")

            df_jul = multi_tables["July-December"]  # Parse using daylight savings aware function to catch end of DST
            df_jul["time"] = _pdt_parse(df_jul["time"]).astype("int64")

            year_data += [df_jan, df_jul]  # Throw both dataframes into list
        elif 2011 <= year <= 2016:
            # noinspection PyTypeChecker
            multi_tables: dict[str, DataFrame] = read_excel(
                file, sheet_name=["January-June", "July-December"],
                header=22, names=[
                    "time",
                    "wind_forecast", "wind_generation",
                    "load", "hydro_generation", "thermal_generation"
                ], usecols="A:F",
                na_filter=False, engine="xlrd"
            )

            df_jan = multi_tables["January-June"]  # Parse January-June timestamps normally, ensuring PST is used
            df_jan["time"] = df_jan["time"].map(lambda t: int(datetime.strptime(t, "%m/%d/%y %H:%M").replace(tzinfo=_PST).timestamp())).astype("int64")

            df_jul = multi_tables["July-December"]  # Parse July-December timestamps using daylight savings aware function to catch end of DST
            df_jul["time"] = _pdt_parse(df_jul["time"]).astype("int64")

            year_data += [df_jan, df_jul]  # Throw both dataframes into list
        elif 2008 <= year <= 2010:
            sheet_name = "Sheet1" if year == 2010 else "5min data"  # 2010 has different sheet name
            # noinspection PyTypeChecker
            df_jan: DataFrame = read_excel(
                file, sheet_name=sheet_name,
                header=20, usecols="B:G", na_filter=False, engine="xlrd",
                names=["time", "wind_forecast", "wind_generation", "load", "hydro_generation", "thermal_generation"]
            )
            # noinspection PyTypeChecker
            df_july: DataFrame = read_excel(
                file, sheet_name=sheet_name,
                header=20, usecols="K:P", na_filter=False, engine="xlrd",
                names=["time", "wind_forecast", "wind_generation", "load", "hydro_generation", "thermal_generation"]
            )

            df_jan = df_jan[df_jan["time"] != ""]  # remove a bunch of empty columns that fill up the bottom of the columns

            # parsed in from Excel already as datetime.datetime objects, just need to clean them up
            df_jan["time"] = df_jan["time"].map(lambda t: int(t.replace(tzinfo=_PST).timestamp())).astype("int64")
            df_july["time"] = df_july["time"].map(lambda t: int(t.replace(tzinfo=_PST).timestamp())).astype("int64")
            year_data += [df_jan, df_july]
        elif year == 2007:
            # noinspection PyTypeChecker
            df_jan: DataFrame = read_excel(
                file, sheet_name="5min data",
                header=18, usecols="B:F", na_filter=False, engine="xlrd",
                names=["time", "wind_generation", "load", "hydro_generation", "thermal_generation"]
            )
            # noinspection PyTypeChecker
            df_july: DataFrame = read_excel(
                file, sheet_name="5min data",
                header=18, usecols="J:N", na_filter=False, engine="xlrd",
                names=["time", "wind_generation", "load", "hydro_generation", "thermal_generation"]
            )

            df_jan = df_jan[df_jan["time"] != ""]  # remove a bunch of empty columns that fill up the bottom of the columns

            # parsed in from Excel already as datetime.datetime objects, just need to clean them up
            df_jan["time"] = df_jan["time"].map(lambda t: int(t.replace(tzinfo=_PST).timestamp())).astype("int64")
            df_july["time"] = df_july["time"].map(lambda t: int(t.replace(tzinfo=_PST).timestamp())).astype("int64")
            year_data += [df_jan, df_july]
        else:
            print(f"There is no parser for {year}")
            continue
    # endregion
    # region Process
    all_years = concat(year_data, ignore_index=True).sort_values(by="time", ascending=True, ignore_index=True)
    all_years['time'] = all_years['time'].astype(ArrowDtype(timestamp('s')))  # convert from int to pyarrow timestamp type
    all_years["year"] = all_years["time"].map(lambda i: i.year)

    data_cols = all_years.columns[1:-1]  # fetch the names of the columns in the data tables except time and year
    for col in data_cols:
        all_years[col] = _float_fix(all_years[col])  # convert everything to integers

    sorting = [
        'load',  # This is the desired order of the final columns
        'nuclear_generation', 'hydro_generation', 'wind_generation', 'fossil_generation', 'solar_generation',
        'thermal_generation', 'wind_forecast', 'wind_basepoint', 'solar_forecast', 'solar_basepoint'
    ]
    exists_sorting = []
    for sort_col in sorting:  # Remove any columns from sorting if they're not in data
        if sort_col in data_cols: exists_sorting.append(sort_col)

    all_years = all_years[["time"] + exists_sorting + ["year"]]
    # endregion
    return all_years

def _save_to_parquet(dataframe: DataFrame, out_file: Path) -> int:
    # years = dataframe["year"].unique()
    a = Table.from_pandas(dataframe, preserve_index=False)

    writer = ParquetWriter(
        where=out_file.resolve(),
        schema=a.schema,
        version="2.6",
        compression="GZIP",
        column_encoding="DELTA_BINARY_PACKED",
        use_dictionary=False
    )

    writer.write_table(a, row_group_size=2e5)  # Roughly 2 years per row group

    # for year in years:
    #     this_year = pa_scalar(datetime(year, 1, 1))
    #     next_year = pa_scalar(datetime(year + 1, 1, 1))
    #
    #     years_data = a.filter((this_year <= pa_field('time')) & (pa_field('time') < next_year))
    #     writer.write_table(years_data, row_group_size=1.5e6)

    writer.close()
    return len(a)

def cli():
    from argparse import ArgumentParser
    from time import time

    parser = ArgumentParser()
    parser.add_argument("DATES", nargs="*", type=int, help="Dates to fetch data for")
    parser.add_argument("--out", "-o", type=Path, help="Output file")
    parser.add_argument("--range", "-r", action="store_true", help="If used, then data will be pulled for the full range between [Date] 1 and [Date] 2")
    parser.add_argument("--format", "-f", type=str, default="PARQUET", help="Format to use for output, valid types are \"Pandas\" and \"Parquet\"")

    args = parser.parse_args()

    if args.format.lower() == "parquet": out_format = ".parquet"
    elif args.format.lower() == "pandas": out_format = ".pkl.gz"
    else: raise ValueError(f"Unknown export format '{args.format}'")

    if args.out: out = args.out
    else: out = Path(f"output-{int(time())}{out_format}")

    if args.range:
        if len(args.DATES) != 2: raise ValueError(f"Cannot create date range from {len(args.DATES)} dates, need 2")
        elif args.DATES[0] >= args.DATE[1]: raise ValueError("Date 1 must be less than Date 2 for range operation")
        dates = list(range(args.DATES[0], args.DATES[1] + 1))
    elif not args.DATES: dates = None
    else: dates = args.DATES

    if dates: print(f"Pulling {len(dates)} years:\n\t" + "\n\t".join([str(i) for i in dates]))
    else: print("No years specified, pulling everything")
    data = pull_years(years=dates)

    print(f"Writing data to {out}")
    if out_format == ".parquet": _save_to_parquet(data, out)
    elif out_format == ".pkl.gz": data.to_pickle(out)


if __name__ == '__main__':
    cli()
