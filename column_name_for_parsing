

import pandas as pd
from typing import Dict, Union, List, Optional
from inserting_columns import _parse_file
from logger_experiment import logger_experiment

logger = logger_experiment(name="lilly_auth")


def get_dataframe_columns(
    df: pd.DataFrame,
    column_names: Optional[Union[str, List[str]]] = None,
    allow_interactive: bool = True
) -> Union[Dict[str, pd.Series], pd.DataFrame]:
    """
    Accepts a column name or list of names (string or list).
    Returns a dict {column_name: pandas.Series}

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame (must not be None or empty).
    column_names : Optional[Union[str, List[str]]]
        Single column name, list of names, or None.
        If None and `allow_interactive` is True, will prompt via input().
    allow_interactive : bool
        If True and column_names is None, prompt for comma-separated names.

    Returns
    -------
    Dict[str, pd.Series]
        Mapping of column name to DataFrame Series.

    Raises
    ------
    ValueError
        If df is None/empty or no column names were provided/resolved.
    KeyError
        If any requested columns are not found in df.columns.
    """

    # Validate DataFrame
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")

    # Resolve input for column names
    if column_names is None:
        if allow_interactive:
            user_input = input("Enter column name or list of column names (comma-separated): ").strip()
            column_names = user_input
        else:
            raise ValueError("No column names provided and interactive input is disabled")

    # Normalize via your helper
    col_names = _parse_file(column_names)  # expected to return List[str]
    logger.debug(f"Requested columns={col_names}")

    # Validate resolved names
    if not col_names:
        raise ValueError("No column names provided")

    # Detect missing columns
    missing = [c for c in col_names if c not in df.columns]
    if missing:
        logger.error(f"Columns not found: {missing}")
        raise KeyError(f"Columns not found in DataFrame: {missing}")

    # Build the mapping
    resolved = {c: df[c] for c in col_names}
    logger.info(f"Resolved columns={list(resolved.keys())}")

    return resolved, df


# import pandas as pd
# from inserting_columns import _parse_file
# from logger_experiment import logger_experiment
# from typing import Union, List, Dict

# logger = logger_experiment(name="lilly_auth")


# def get_dataframe_columns(
#     df: pd.DataFrame,
#     user_input: Union[str, List[str]]
# ) -> Dict[str, pd.Series]:
#     """
#     Accepts a column name or list of names (string or list).
#     Returns a dict {column_name: pandas.Series}
#     """
#     if df is None or df.empty:
#         raise ValueError("Input DataFrame is empty or None")
#     if user_input is None:
#         user_input=input("Ebter teh column name to b eparsed")
#     col_names = _parse_file(user_input)
#     logger.debug(f"Requested columns={col_names}")

#     if not col_names:
#         raise ValueError("No column names provided")

#     missing = [c for c in col_names if c not in df.columns]
#     if missing:
#         logger.error(f"Columns not found: {missing}")
#         raise KeyError(f"Columns not found in DataFrame: {missing}")

#     resolved = {c: df[c] for c in col_names}
#     logger.info(f"Resolved columns={list(resolved.keys())}")

#     return resolved
