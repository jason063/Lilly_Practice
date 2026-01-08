

import pandas as pd
from typing import Union, List, Optional
from logger_experiment import logger_experiment

logger = logger_experiment(name="lilly_auth")


def _parse_file(user_input):
    if isinstance(user_input, list):
        return user_input

    if not isinstance(user_input, str):
        return []

    # Remove surrounding brackets if present
    cleaned = user_input.strip().strip("[]")

    # Split and clean quotes
    columns = [
        item.strip().strip("'").strip('"')

        for item in cleaned.split(",")
        if item.strip()
    ]

    logger.debug(f"_parse_file | parsed columns={columns}")
    return columns


def _is_missing(col: Optional[Union[str, int]]) -> bool:
    if col is None:
        return True

    col_str = str(col).strip()

    if col_str == "" or col_str.startswith("Unnamed"):
        return True

    if col_str.isdigit():
        return True

    return False


def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("normalize_dataframe_headers | start")

    try:
        if df is None:
            raise ValueError("Input DataFrame is None")

        df = df.copy()
        print("1111111")
        # ✅ FIX: handle stringified-list headers using _parse_file
        if len(df.columns) == 1:
            col = df.columns[0]

            if isinstance(col, str) and col.strip().startswith("["):
                parsed_cols = _parse_file(col)
                print("222222222222222222")

                if parsed_cols:
                    df.columns = parsed_cols
                    df = df.iloc[1:].reset_index(drop=True)
                    logger.info("Fixed stringified-list column headers")
                    return df

        current_cols = list(df.columns)
        n_cols = df.shape[1]
        print("3333",current_cols)

        logger.debug(f"Current columns={current_cols}, n_cols={n_cols}")

        missing_indices = [i for i, c in enumerate(current_cols) if _is_missing(c)]
        logger.debug(f"Missing indices={missing_indices}")

        # ✅ Case 1: All headers present
        if not missing_indices:
            logger.info("All headers present. No action required.")
            return df

        # ✅ Case 2: No headers at all
        if len(missing_indices) == n_cols:
            new_cols = input(
                f"Enter ALL {n_cols} column names (comma-separated): like A, B, C, D : "
            )

            parsed = _parse_file(new_cols)

            if len(parsed) != n_cols:
                raise ValueError(
                    f"Expected {n_cols} headers, got {len(parsed)} -> {parsed}"
                )

            df.columns = parsed
            logger.info("All column headers assigned.")
            return df

        # ✅ Case 3: Partial headers missing
        logger.info(f"Missing column positions: {missing_indices}")

        for idx in missing_indices:
            col_input = input(f"Enter column name for position {idx}: ")
            parsed = _parse_file(col_input)

            if not parsed:
                raise ValueError(f"Empty header provided for index {idx}")

            # Take first value if user enters CSV
            current_cols[idx] = parsed[0]

        df.columns = current_cols
        logger.info("Missing column headers filled.")
        return df

    except Exception:
        logger.exception("normalize_dataframe_headers | failure")
        raise

    finally:
        logger.info("normalize_dataframe_headers | end")



# import pandas as pd
# from typing import Union, List, Optional
# from logger_experiment import logger_experiment
# import ast

# logger = logger_experiment(name="lilly_auth")


# def _parse_file(user_input):
#     if isinstance(user_input, list):
#         return user_input

#     # Remove brackets
#     cleaned = user_input.strip()[1:-1]

#     # Split and clean quotes
#     columns = [
#         item.strip().strip("'").strip('"')
#         for item in cleaned.split(",")
#         if item.strip()
#     ]
#     print("columns++++++++",columns )

#     return columns




# def _is_missing(col: Optional[Union[str, int]]) -> bool:
#     if col is None:
#         return True

#     col_str = str(col).strip()

#     if col_str == "" or col_str.startswith("Unnamed"):
#         return True

#     if col_str.isdigit():
#         return True

#     return False



# def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
#     logger.info("normalize_dataframe_headers | start")

#     try:
#         if df is None:
#             raise ValueError("Input DataFrame is None")

#         df = df.copy()

#         # 🔥 FIX: handle stringified list headers
#         if len(df.columns) == 1:
#             col = df.columns[0]
#             if isinstance(col, str) and col.strip().startswith("["):
#                 try:
#                     parsed_cols = ast.literal_eval(col)
#                     if isinstance(parsed_cols, list):
#                         df.columns = [c.strip().strip("'").strip('"') for c in parsed_cols]
#                         df = df.iloc[1:].reset_index(drop=True)
#                         logger.info("Fixed stringified-list column headers")
#                         return df
#                 except Exception:
#                     pass

#         current_cols = list(df.columns)
#         n_cols = df.shape[1]

#         print("++++++++currentcols, n_cols", current_cols, n_cols)

#         missing_indices = [i for i, c in enumerate(current_cols) if _is_missing(c)]
#         print("missingindices++++++++++++", missing_indices)

#         # ✅ Case 1: All headers present
#         if not missing_indices:
#             logger.info("All headers present. No action required.")
#             print("✅ All column headers already present.")
#             return df

#         # ✅ Case 2: No headers at all
#         if len(missing_indices) == n_cols:
#             new_cols = input(
#                 f"Enter ALL {n_cols} column names (comma-separated): "
#             )
#             parsed = _parse_file(new_cols)

#             if len(parsed) != n_cols:
#                 raise ValueError(
#                     f"Expected {n_cols} headers, got {len(parsed)} -> {parsed}"
#                 )

#             df.columns = parsed
#             print("✅ Column headers assigned.")
#             return df

#         # ✅ Case 3: Partial headers missing
#         print("Missing column positions:", missing_indices)

#         for idx in missing_indices:
#             col_name = input(f"Enter column name for position {idx}: ").strip()
#             if not col_name:
#                 raise ValueError(f"Empty header provided for index {idx}")
#             current_cols[idx] = col_name

#         df.columns = current_cols
#         print("✅ Missing column headers filled.")
#         return df

#     except Exception:
#         logger.exception("normalize_dataframe_headers | failure")
#         raise

#     finally:
#         logger.info("normalize_dataframe_headers | end")



# df_data = data_read_process_interactive(
#     url="C://Users//neerajkumar-sh//lilly//data_lilly.xlsx",
#     sheet_name="Sheet1",
#     header=None
# )

# df = normalize_dataframe_headers(df_data)
# print(df)
# print(df.head(5))
# print(df.head(1))
# print(df.tail(10))
# print(df.columns)
# print(df['Description'])



# 

# import pandas as pd
# from typing import List
# from logger_experiment import logger_experiment


# import pandas as pd
# from typing import Union, List, Optional
# import logging
# from io import BytesIO
# import os
# from urllib.parse import urlparse
# import requests
# from pathlib import Path
# from logging import handlers
# from logger_experiment import logger_experiment
# from url import *
# from sheet import *
# from inserting_columns import *

# logger = logger_experiment(name="lilly_auth")

# def data_read_process_interactive(
#     url: str,
#     sheet_name: Optional[str] = None,
#     engine: str = 'openpyxl',
#     header: Optional[int] = None,
#     names: Optional[List[str]] = None,
#     parse_dates: Optional[List[str]] = None
# ) -> pd.DataFrame:
#     df_data_01 = pd.read_excel(
#         url,
#         sheet_name=sheet_name if sheet_name else 0,
#         engine=engine,
#         header=header,
#         names=names,
#         parse_dates=parse_dates
#     )
#     return df_data_01



# logger = logger_experiment(name="lilly_auth")



# def _parse_file(user_input: Optional[str,List[str]]) -> Optional[str, List[str]]:
#     """Parse comma-separated input safely."""
#     try:
#         parsed = [c.strip() for c in user_input.split(",") if c.strip()]
#         logger.debug(f"_parse_file | raw='{user_input}' | parsed={parsed}")
#         print("++++++++++++++++++parsed", parsed)
#         return parsed
#     except Exception:
#         logger.exception("_parse_file failed")
#         raise




# def _is_missing(col: Optional[str, List[str]]) -> bool:
#     """
#     Determines whether a column header is effectively missing.
#     Treats numeric-looking headers (int or str) as missing.
#     """
#     if col is None:
#         return True

#     col_str = str(col).strip()

#     # Empty or auto-generated headers
#     if col_str == "" or col_str.startswith("Unnamed"):
#         return True

#     # Numeric-only headers (e.g. '0', '1', '23') → positional, not semantic
#     if col_str.isdigit():
#         return True

#     return False


# def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Ensures DataFrame has proper first-row headers like Excel.

#     Rules:
#     1. If all headers exist -> return df
#     2. If some headers missing -> ask user for only those
#     3. If no headers at all -> ask user for full list
#     """
#     logger.info("normalize_dataframe_headers | start")

#     try:
#         if df is None:
#             raise ValueError("Input DataFrame is empty or no dataframepresent")

#         df = df.copy()
#         current_cols = list(df.columns)
#         n_cols = df.shape[1]
#         print("+++++++++++", n_cols)

#         logger.debug(
#             f"normalize_dataframe_headers | n_cols={n_cols} | current_cols={current_cols}"
#         )

#         # Detect missing headers
#         missing_indices = [i for i, c in enumerate(current_cols) if _is_missing(c)]
#         print("missingindices++++++++++++",missing_indices)

#         # ✅ Case 1: All headers present
#         if not missing_indices and missing_indices :
#             logger.info("All headers present. No action required.")
#             print("✅ All column headers already present.")
#             return df

#         # ✅ Case 2: No headers at all
#         if len(missing_indices) == n_cols:
#             logger.info("No headers detected. Requesting full header list from user.")
#             new_cols = input(
#                 f"Enter ALL {n_cols} column names (comma-separated): "
#             )

#             parsed = _parse_csv(new_cols)

#             if len(parsed) != n_cols:
#                 msg = (
#                     f"Expected {n_cols} headers, "
#                     f"got {len(parsed)} -> {parsed}"
#                 )
#                 logger.error(msg)
#                 raise ValueError(msg)

#             df.columns = list(parsed)
#             logger.info("Headers assigned successfully (no-headers case).")
#             print("✅ Column headers assigned.")
#             columns=[]
#             for each in df.columns:
#                 columns.append(each)
#             df.columns = columns
#             return df

#         # ✅ Case 3: Partial headers missing
#         logger.info(
#             f"Partial headers detected. Missing positions: {missing_indices}"
#         )
#         print("\nMissing column positions:", missing_indices)

#         for idx in missing_indices:
#             col_name = input(
#                 f"Enter column name for position {idx}: "
#             ).strip()

#             if not col_name:
#                 msg = f"Empty header provided for index {idx}"
#                 logger.error(msg)
#                 raise ValueError(msg)

#             current_cols[idx] = col_name
#             logger.debug(
#                 f"Filled missing header at index {idx} with '{col_name}'"
#             )
        
#         df.columns = list(current_cols)
        
#         logger.info("Missing headers filled successfully.")
#         print("✅ Missing column headers filled.")
#         columns=[]
#         for each in df.columns:
#             columns.append(each)
#         df.columns = columns
#         return df

#     except Exception:
#         logger.exception("normalize_dataframe_headers | failure")
#         raise

#     finally:
#         logger.info("normalize_dataframe_headers | end")


# df_data = data_read_process_interactive()
# df = normalize_dataframe_headers(df_data)
# print(df)


# import pandas as pd
# from typing import List
# from logger_experiment import logger_experiment  # adjust path if needed

# logger = logger_experiment(name="lilly_auth")  # reuse shared logger

# def _parse_csv(user_input: str) -> List[str]:
#     """Parse comma-separated input safely (trims whitespace, removes empties)."""
#     try:
#         parsed = [c.strip() for c in user_input.split(",") if c.strip()]
#         logger.debug(f"_parse_csv | raw='{user_input}' | parsed={parsed}")
#         return parsed
#     except Exception as e:
#         logger.exception(f"_parse_csv failed for input: {user_input}")
#         raise

# def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Ensures DataFrame has complete column headers.
#     Handles:
#       - No headers (ask for all)
#       - Partial headers (fill missing 'Unnamed' or None)
#     Logs all major steps and errors.
#     """
#     logger.info("normalize_dataframe_headers | start")
#     try:
#         if df is None:
#             logger.error("normalize_dataframe_headers | received df=None")
#             raise ValueError("Input DataFrame is None")

#         df = df.copy()
#         current_cols = list(df.columns)
#         n_cols = df.shape[1]

#         logger.debug(f"normalize_dataframe_headers | current_cols={current_cols} | n_cols={n_cols}")

#         print("\nCurrent DataFrame columns:")
#         for i, c in enumerate(current_cols):
#             print(f"  {i}: {c}")

#         header_exists = input(
#             "\nDoes the dataset have column headers? (y/n) "
#             "Please verify using any CSV/XLSX reader (preferably Excel): "
#         ).strip().lower()

#         logger.info(f"User response for header_exists: {header_exists}")

#         # ---- No headers at all ----
#         if header_exists == "n":
#             new_cols = input(
#                 f"Enter ALL {n_cols} column names (comma-separated): "
#                 "e.g., Description, Priority, ShortDescription, ConfigurationItem, etc: "
#             )

#             parsed = _parse_csv(new_cols)
#             logger.debug(f"User provided headers (no headers case): {parsed}")

#             if len(parsed) != n_cols:
#                 msg = f"Expected {n_cols} column names, got {len(parsed)} | provided={parsed}"
#                 logger.error(msg)
#                 raise ValueError(msg)

#             df.columns = parsed
#             logger.info("Column headers assigned for 'no headers' case.")
#             print("✅ Column headers assigned.")
#             return df

#         # ---- Partial headers or already present ----
#         missing_indices = [
#             i for i, c in enumerate(current_cols)
#             if c is None or str(c).strip() == "" or str(c).startswith("Unnamed")
#         ]

#         logger.debug(f"Detected missing_indices={missing_indices}")

#         if not missing_indices:
#             logger.info("All column headers already present.")
#             print("✅ All column headers already present.")
#             return df

#         print("\nMissing column positions:")
#         print(missing_indices)

#         # Collect user-provided names for each missing position
#         for idx in missing_indices:
#             col_name = input(f"Enter column name for position {idx}: ").strip()
#             if not col_name:
#                 msg = f"Empty column name provided for position {idx}"
#                 logger.warning(msg)
#                 raise ValueError(msg)
#             current_cols[idx] = col_name
#             logger.debug(f"Filled missing column at position {idx} with '{col_name}'")

#         df.columns = current_cols
#         logger.info("Missing column headers filled successfully.")
#         print("✅ Missing column headers filled.")
#         return df

#     except Exception as e:
#         # Logs the full traceback to your file handler
#         logger.exception("normalize_dataframe_headers | error occurred")
#         # Re-raise to allow caller to handle; this keeps your pipeline predictable
#         raise
#     finally:
#         logger.info("normalize_dataframe_headers | end")



# # import pandas as pd
# # from typing import List
# # from logger_experiment import *

# # logger = logger_experiment()

# # def _parse_csv(user_input: str) -> List[str]:
# #     return [c.strip() for c in user_input.split(",") if c.strip()]

# # def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
# #     """
# #     Ensures DataFrame has complete column headers.
# #     Handles:
# #       - No headers
# #       - Partial headers
# #     """
# #     df = df.copy()

# #     current_cols = list(df.columns)
# #     n_cols = df.shape[1]

# #     print("\nCurrent DataFrame columns:")
# #     for i, c in enumerate(current_cols):
# #         print(f"  {i}: {c}")

# #     header_exists = input(
# #         "\nDoes the dataset have column headers? (y/n) please verify using any csv, xlxs reading software prefreable excel: "
# #     ).strip().lower()

# #     # ---- No headers at all ----
# #     if header_exists == "n":
# #         new_cols = input(
# #             f"Enter ALL {n_cols} column names (comma-separated): preferrable [Description, Priority, ShortDescription, ConfigurationItem, etc] "
# #         )
# #         parsed = _parse_csv(new_cols)

# #         if len(parsed) != n_cols:
# #             raise ValueError(
# #                 f"Expected {n_cols} column names, got {len(parsed)}"
# #             )

# #         df.columns = parsed
# #         print("✅ Column headers assigned.")
# #         return df

# #     # ---- Partial headers ----
# #     missing_indices = [
# #         i for i, c in enumerate(current_cols)
# #         if c is None or str(c).startswith("Unnamed")
# #     ]

# #     if not missing_indices:
# #         print("✅ All column headers already present.")
# #         return df

# #     print("\nMissing column positions:")
# #     print(missing_indices)

# #     for idx in missing_indices:
# #         col_name = input(
# #             f"Enter column name for position {idx}: "
# #         ).strip()
# #         current_cols[idx] = col_name

# #     df.columns = current_cols
# #     print("✅ Missing column headers filled.")
# #     return df


