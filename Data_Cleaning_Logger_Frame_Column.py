
import pandas as pd
from typing import List, Optional
import logging
from io import BytesIO
import os
from urllib.parse import urlparse


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

def logger_experiment():
  logger = logging.getLogger('lilly_auth')
  #logger.setLevel(logging.DEBUG)
  logger.propagate = False
  # create file handler which logs even debug messages
  fh = logging.FileHandler('my_log_file.log', mode='a', encoding='utf-8', delay=False)

  fh.setLevel(logging.DEBUG)
  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.CRITICAL)
  # create formatter and add it to the handlers

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  formatter1 = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter1)
  fh.setFormatter(formatter)
  # add the handlers to logger  
  logger.addHandler(ch)
  logger.addHandler(fh)

  return logger

  # # 'application' code
  # logger.debug('debug message')
  # logger.info('info message')
  # logger.warning('warn message')
  # logger.error('error message')
  # logger.critical('critical message')






import os
from io import BytesIO
from urllib.parse import urlparse
import requests
import logging

# Assuming logger is already configured as 'lilly_auth'
logger = logging.getLogger('lilly_auth')

def check_remote_file(url):
    """Check if a remote file exists via HTTP/HTTPS."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Remote file check failed for Check_remote_file function {url}: {e}")
        return False

def url_input(url=None):
    """
    Validate and return a URL or file path for Excel input.
    Supports str, os.PathLike, BytesIO, and file-like objects.
    Prompts user if no valid input is provided.
    Checks existence for local paths and remote URLs.
    """
    try:
        if not url:
            url = input("Enter the path or URL of the Excel file: ").strip()

        if isinstance(url, str):
            # Remote URLs (HTTP/HTTPS)
            if url.startswith(("http://", "https://")):
                if check_remote_file(url):
                    logger.info(f"Valid remote URL provided: url_input function {url}")
                    return url
                else:
                    raise FileNotFoundError(f"Remote file not found at {url}")

            # file:// URLs
            elif url.startswith("file://"):
                parsed = urlparse(url)
                local_path = parsed.path
                if os.path.exists(local_path):
                    logger.info(f"Valid file:// path provided: {local_path}")
                    return local_path
                else:
                    raise FileNotFoundError(f"File not found at {local_path}")

            # Local path
            elif os.path.exists(url):
                logger.info(f"Valid local path provided: {url}")
                return url

            else:
                raise ValueError(f"Invalid path or URL: {url}")

        elif isinstance(url, os.PathLike):
            if os.path.exists(url):
                logger.info(f"Path object provided: {url}")
                return str(url)
            else:
                raise FileNotFoundError(f"File not found at {url}")

        elif hasattr(url, "read"):  # file-like object
            logger.info("File-like object provided.")
            return url

        elif isinstance(url, bytes):
            logger.warning("Passing byte strings is deprecated. Wrapping in BytesIO.")
            return BytesIO(url)

        else:
            raise ValueError(f"Unsupported input type: {type(url)}")

    except Exception as e:
        logger.error(f"Error in url_input: {e}")
        raise


# def url_input(url=None):
#     """
#     Validate and return a URL or file path for Excel input.
#     Supports str, os.PathLike, BytesIO, and file-like objects.
#     Prompts user if no valid input is provided.
#     """
#     try:
#         # If url is None or empty, ask user
#         if not url:
#             url = input("Enter the path or URL of the Excel file: ").strip()

#         # Validate type
#         if isinstance(url, str):
#             # Check if it's a valid URL or local path
#             if url.startswith(("http://", "https://", "ftp://", "s3://", "file://")) or os.path.exists(url):
#                 logger.info(f"Valid URL or path provided: {url}")
#                 return url
#             else:
#                 raise ValueError(f"Invalid path or URL: {url}")

#         elif isinstance(url, os.PathLike):
#             logger.info(f"Path object provided: {url}")
#             return str(url)

#         elif hasattr(url, "read"):  # file-like object
#             logger.info("File-like object provided.")
#             return url

#         elif isinstance(url, bytes):
#             logger.warning("Passing byte strings is deprecated. Wrapping in BytesIO.")
#             return BytesIO(url)

#         else:
#             raise ValueError(f"Unsupported input type: {type(url)}")

#     except Exception as e:
#         logger.error(f"Error in url_input: {e}")
#         raise


if __name__ == "__main__":
    logger = logger_experiment()
    url = url_input()
    print(type(url),url)
    
    
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
