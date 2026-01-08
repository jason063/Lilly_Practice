import pandas as pd
from typing import Union, List, Optional
import logging
from io import BytesIO
import os
from urllib.parse import urlparse
import requests
from pathlib import Path
from logging import handlers
from logger_experiment import logger_experiment
from url import *
from sheet import *
from inserting_columns import *
from column_name_for_parsing import *
from preprocessing import *


pd.set_option('display.max_colwidth', None)   # show full text
pd.set_option('display.max_rows', None)       # show all rows (careful for big data)
pd.set_option('display.max_columns', None)

logger = logger_experiment(name="lilly_auth")

def data_read_process_interactive(
    url: str,
    sheet_name: Optional[str] = None,
    engine: str = 'openpyxl',
    header: Optional[int] = None,
    names: Optional[List[str]] = None,
    parse_dates: Optional[List[str]] = None
) -> pd.DataFrame:
    df_data_01 = pd.read_excel(
        url,
        sheet_name=sheet_name if sheet_name else 0,
        engine=engine,
        header=header,
        names=names,
        parse_dates=parse_dates
    )
    return df_data_01




  # # 'application' code
  # logger.debug('debug message')
  # logger.info('info message')
  # logger.warning('warn message')
  # logger.error('error message')
  # logger.critical('critical message')
# Assuming logger is already configured as 'lilly_auth'


if __name__ == "__main__":
    logger = logger_experiment(name="lilly_auth")
    url = url_input()
    sheet_name = sheet_name()
    df_data=data_read_process_interactive(url,sheet_name)
    # print(df_data)
    df=normalize_dataframe_headers(df_data)
    #print(df)
    column_names = input("enter the name of columns`")
    columns,df = get_dataframe_columns(df, column_names)
    processed=clean_dictlike_preserve_keys(columns)    
    df= df.assign( Description_clean = processed["Description"])
    #, ShortDescription_clean = processed["ShortDescription"]
    print(df.head(5))

    


    # sheet_name = input("Enter the sheet name (leave blank for first sheet): ").strip() or None
    # engine = input("Enter the engine (default is 'openpyxl'): ").strip() or 'openpyxl'

    # header_input = input("Enter the header row index (leave blank if no header): ").strip()
    # header = int(header_input) if header_input else None

    # names_input = input("Enter the column names (comma-separated, leave blank to use file headers): ").strip()
    # names = [name.strip() for name in names_input.split(",")] if names_input else None

    # parse_dates_input = input("Enter columns to parse as dates (comma-separated, optional): ").strip()
    # parse_dates = [col.strip() for col in parse_dates_input.split(",")] if parse_dates_input else None

    # df_data = data_read_process_interactive(url, sheet_name, engine, header, names, parse_dates)

    # print("\n✅ Data Loaded Successfully!")
    # print("DataFrame Preview:")
    # print(df_data.head())

# import json
# class JSONFormatter(logging.Formatter):
#     def format(self, record):
#         payload = {
#             "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
#             "logger": record.name,
#             "level": record.levelname,
#             "file": record.filename,
#             "line": record.lineno,
#             "process": record.process,
#             "thread": record.threadName,
#             "message": record.getMessage(),
#         }
#         return json.dumps(payload, ensure_ascii=False)
