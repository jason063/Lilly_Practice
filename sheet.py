from typing import Union, List, Optional
import logging
from io import BytesIO
import os
from urllib.parse import urlparse
import requests
from pathlib import Path
from logging import handlers
from logger_experiment import logger_experiment


logger = logger_experiment(name="lilly_auth")

NameType = Union[str, int, list[str]]

def sheet_name(
    name: Optional[NameType] = None,
    default: Optional[NameType] = None
) -> NameType:
    """
    Return a sheet identifier which may be:
      - str: sheet name
      - int: sheet index (0-based or 1-based, as your caller defines)
      - list[str]: multiple sheet names
    If 'name' is not provided, prompt the user. Blank input falls back to 'default'.
    """
    # If no name provided, ask the user
    if name is None:
        user = input("Enter the sheet name (leave blank for first sheet/default): ").strip()
        if user == "":
            if default is None:
                # Decide your preferred default; here we make 'first sheet' explicit.
                # You could also return 0 to mean first sheet index.
                return "Sheet1"
            return default
        name = user

    # Validate list[str] content if a list is provided
    if isinstance(name, list):
        if not all(isinstance(x, str) for x in name):
            raise ValueError("If 'name' is a list, it must be list[str] (all elements strings).")

    # Validate int if needed (optional: ensure non-negative)
    if isinstance(name, int) and name < 0:
        raise ValueError("Sheet index (int) must be non-negative.")

    return name
