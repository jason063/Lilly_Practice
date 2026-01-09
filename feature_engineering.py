
import pandas as pd
import re
import os



def add_head_tail_columns_multiline_with_date(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Parse `data[column]`:
    - 'head--tail' on same line OR 'head--' then tail on subsequent lines
    - While inside a head, a line with '--' is considered a NEW head only if the left part
      looks like a column name (alphabetic / question mark) and does NOT start with a digit.
    - Special extraction:
        * If head == 'The expected print is': store the FIRST date found (DD Mon YYYY),
          ignoring any time info (e.g., '06 Nov 2025' from '06 Nov 2025 4--09 PM CET').
        * If head == 'Which environment?': store the tail as-is (e.g., 'Production').

    Original `column` is not modified.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("`data` must be a pandas DataFrame.")
    if column not in data.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    series = data[column].astype(str).fillna("")

    # --- helpers ---
    month_pat = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
    date_regex = re.compile(rf'\b(\d{{1,2}}\s+{month_pat}\s+\d{{4}})\b', re.IGNORECASE)

    def looks_like_new_head(line: str) -> bool:
        """Decide if a line with '--' starts a NEW head."""
        if "--" not in line:
            return False
        left, _ = line.split("--", 1)
        left = left.strip()
        # Treat as a head if it contains letters or '?' and does NOT start with a digit
        # This avoids false heads like '06 Nov 2025 4--09 PM CET'
        return bool(re.search(r'[A-Za-z?]', left)) and not re.match(r'^\d', left)

    def base_col_for_head(head: str) -> str:
        h = head.strip()
        # If you need special handling for Description, add it here
        # if h.lower() == "description" and "Description" in data.columns:
        #     return "new_description"
        return h

    def extract_first_date(text: str) -> str:
        """Return the first 'DD Mon YYYY' found, else empty string."""
        m = date_regex.search(text)
        return m.group(1) if m else ""

    # --- main loop ---
    for idx, cell in series.items():
        current_head = None
        tail_lines = []

        lines = [ln for ln in str(cell).splitlines() if ln.strip()]
        if not lines:
            continue

        def flush_current_head():
            nonlocal current_head, tail_lines
            if not current_head:
                return

            tail_text = "\n".join(tail_lines).strip()
            base = base_col_for_head(current_head)

            value_to_write = tail_text  # default

            # Head-specific logic
            if current_head.strip().lower() == "the expected print is":
                # Extract FIRST date only
                date_only = extract_first_date(tail_text)
                value_to_write = date_only if date_only else tail_text

            # Ensure column exists
            if base not in data.columns:
                data[base] = pd.NA

            # Write (append if something already exists)
            existing = data.at[idx, base]
            if pd.isna(existing) or str(existing).strip() == "":
                data.at[idx, base] = value_to_write
            else:
                data.at[idx, base] = f"{existing}\n{value_to_write}"

            # reset
            current_head = None
            tail_lines = []

        for line in lines:
            if "--" in line and looks_like_new_head(line):
                # new head starts
                flush_current_head()
                head, tail = line.split("--", 1)
                current_head = head.strip()
                tail_lines = [tail.strip()] if tail.strip() else []
            else:
                # either no '--' or it's a false head (e.g., date/time line with '--')
                if current_head:
                    # minimal cleanup
                    cleaned = " ".join(line.split())
                    tail_lines.append(cleaned)
                else:
                    # no active head; ignore free lines
                    pass

        # end-of-cell flush
        flush_current_head()

    return data

# #working column data conversion
# def add_head_tail_columns(data: pd.DataFrame, column: str) -> pd.DataFrame:
#     """
#     For each row in `data[column]`, split lines by 'head--tail' pairs.
#     Create/assign new columns per row where column name = head and value = tail.
#     Special case: if head == 'Description' and 'Description' exists, write to 'new_description'.
#     If a line has no '--', clean it (remove emails + normalize spaces) and keep it in the original column.
#     Returns the modified DataFrame.
#     """

#     # --- Basic checks ---
#     if not isinstance(data, pd.DataFrame):
#         raise TypeError("`data` must be a pandas DataFrame.")

#     if column not in data.columns:
#         raise KeyError(f"Column '{column}' not found in DataFrame.")

#     # Ensure we're working with strings, and replace NaNs with empty strings
#     series = data[column].astype(str).fillna("")

#     # --- Iterate row-wise through target column ---
#     for idx, cell in series.items():
#         # Split cell into lines; skip blank lines
#         lines = [ln for ln in str(cell).splitlines() if ln.strip()]
#         if not lines:
#             continue

#         for line in lines:
#             # Split by '--' exactly once
#             parts = line.split("--", 1)

#             if len(parts) == 1:
#                 # No '--' present; just remove emails and normalize whitespace
#                 # (keeping your comment intent)
#                 cleaned = re.sub(r"\S+@\S+", "", parts[0])       # remove simple email patterns
#                 cleaned = " ".join(cleaned.split())              # normalize spaces
#                 data.at[idx, column] = cleaned                   # write back to the original column
#                 continue

#             head = parts[0].strip()
#             tail = parts[1].strip()

#             # Special handling for existing Description column
#             if head == "Description" and "Description" in data.columns:
#                 target_col = "new_description"
#             else:
#                 target_col = head

#             # Create the target column if it doesn't exist
#             if target_col not in data.columns:
#                 # Use pd.NA so the column is consistently nullable
#                 data[target_col] = pd.NA

#             # Assign tail into this row for the target column
#             data.at[idx, target_col] = tail

#             # Debug prints (optional; comment out in production)
#             # print("printing head and tail ++++++++++++++++++++++++++++++++", head, tail)

#     # Return the DataFrame (your code was returning a string; better return the object)
#     return data

def save_to_desktop(df: pd.DataFrame, base_name: str = "") -> dict:
    desktop = os.path.expanduser("~/Desktop")
    target_dir = desktop if os.path.isdir(desktop) else os.getcwd()

    excel_path = os.path.join(target_dir, f"{base_name}.xlsx")
    csv_path = os.path.join(target_dir, f"{base_name}.csv")

    # Save using openpyxl for .xlsx as per policy
    df.to_excel(excel_path, index=False, engine='openpyxl')
    df.to_csv(csv_path, index=False)

    return {"excel": excel_path, "csv": csv_path}


# import re
# import pandas as pd
# from typing import Union, Dict, List
# import os
# from logger_experiment import logger_experiment

# logger = logger_experiment(name="lilly_auth")

# def feature_engineering(data: Union[pd.DataFrame, pd.Series, str, List[str], dict], column:Union[pd.Series, str, List[str]]) -> Union[pd.DataFrame, pd.Series, str, List[str], dict]:
#     internal_list_str_data=[]
#     try:
#         # if isinstance(data, Union[]) -> None:
#         #     pass
#         if isinstance(data, str):
#             str_data = data
#             return f"str Data provided {str_data}"
#         elif isinstance(data, List):
#             list_data = data
#             return f"list Data provided  {list_data}"
#         elif isinstance(data, pd.Series):
#             series_data = data
#             return f"Series Data provided {series_data}"
#         elif isinstance(data, pd.DataFrame):
#             for each in data.columns:
#                 if each == column:
#                     # each = each.lower()
#                     dataframe_data = data[each].values
#                     print("printing head and tail ++++++++++++++++++++++++++++++++",dataframe_data)
#                     for each in dataframe_data.splitlines():
#                         parts = each.split("--", 1)
#                         if len(parts) == 1:
#                         # No '--' present; just remove emails and normalize whitespace, we can keep for any further data clenaing like PII etc
#                             data[column] = parts
#                         head, tail = parts[0], parts[1]
#                         if head in data.columns and head == "Description":
#                             head = "new_" + head
#                             data[head] = tail
#                         elif head in data.columns:
#                             data[head] = tail                        
#                         print("printing head and tail ++++++++++++++++++++++++++++++++",head, tail)
#                         data[head] = tail
#                         print(data)
                        
                        
                    
#             return f"dataframe provided {data}"
#         elif isinstance(data, dict):
#             dict_data = data
#             return f"dataframeprovided : {dict_data}"
#     except Exception:
#         logger.info("no data is able tpo read | failure")
#         raise

#     finally:
#         logger.info("we have data now iterate ity BSDK | end")


