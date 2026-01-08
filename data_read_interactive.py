import pandas as pd
from typing import Optional, List

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
