# data_df.columns = ['Description', 'Priority', 'ShortDescription', 'ConfigurationItem', 'ElapsedTime', 'ContactNotes', 'ResolutionCode', 'ClosureCode']

# data_df_copy = data_df.copy()

# description=data_df_copy['Description']


# import nltk
# import regex as re
# from nltk.tokenize import word_tokenize, sent_tokenize, regexp_tokenize

# # regex_token = regexp_tokenize(text_corpus, 'excellent [A-a]')
# # print(regex_token)
# EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
# final_dict_as_list = []
# internal_list =[]


# def clean_line_keep_first_double_dash(line: str) -> str:
#     """
#     Keep only the first occurrence of '--' in a line as the key/value separator.
#     Replace any subsequent '--' with a single space.
#     """
#     # Split on the first '--' only
#     parts = line.split('--', 1)
#     if len(parts) == 1:
#         # No '--' in this line: return as-is (after email removal)
#         return EMAIL_RE.sub(' ', line)

#     head, tail = parts[0], parts[1]

#     # Remove emails from both head and tail (emails can appear anywhere)
#     head = EMAIL_RE.sub(' ', head)
#     tail = EMAIL_RE.sub(' ', tail)

#     # Replace any further '--' in the tail with a space
#     tail = tail.replace('--', ' ')

#     # Recompose the line, preserving the first separator
#     line = f"{head}--{tail}"
#     return line

# def data_cleaning(text: str) -> list[str]:
#     for each in list(description).splitlines():
#       print(type(each))
#     # print(type(index), type(each))
#       if each is None:
#         print(f"Nothing found")
#       else:
#         text = each.replace("\x08", "").replace("\t", " ").replace("\r", " ").replace("----","--")
#         text = re.sub(r"\s{2,}", " ", text).strip()
#         internal_list.append(clean_line_keep_first_double_dash(text))
#     return internal_list


# cleaned_lines = data_cleaning(description)
# for ln in cleaned_lines:
#     print(ln)




# Precompiled regex to remove emails

# def data_read(url: str) -> pd.DataFrame:
#     data_df = pd.read_excel('/content/colab_data_llm.xlsx', header=None)

# # Assign custom headers

#     data_df.columns = ['Description', 'Priority', 'ShortDescription', 'ConfigurationItem', 'ElapsedTime', 'ContactNotes', 'ResolutionCode', 'ClosureCode']

#     data_df_copy = data_df.copy()

#     description=data_df_copy['Description']
#     ResolutionCode=data_df_copy['ResolutionCode']
#     return description, ResolutionCode

text_corpus = {"a": "", "b":""}


# import re
# EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')


# def clean_line_keep_first_double_dash(line: str) -> str:
#     """
#     Keep only the first occurrence of '--' in a line as the key/value separator.
#     Replace any subsequent '--' with a single space. Remove emails and normalize whitespace.
#     """
#     # Basic normalization first
#     line = (
#         line.replace("\x08", "")
#             .replace("\t", " ")
#             .replace("\r", " ")
#     )
#     # Collapse long dash runs to '--' (e.g., '----' -> '--', '-----' -> '--')
#     line = re.sub(r'-{3,}', '--', line)

#     # Split on the first '--' only
#     parts = line.split('--', 1)
#     if len(parts) == 1:
#         # No '--' present; just remove emails and normalize whitespace
#         line = EMAIL_RE.sub(' ', line)
#         line = re.sub(r'\s{2,}', ' ', line).strip()
#         return line

#     head, tail = parts[0], parts[1]

#     # Remove emails from both head and tail
#     head = EMAIL_RE.sub(' ', head)
#     tail = EMAIL_RE.sub(' ', tail)

#     # Replace any further '--' in the tail with a space
#     tail = tail.replace('--', ' ')

#     # Recompose, preserving the first separator
#     cleaned = f"{head}--{tail}"

#     # Normalize whitespace
#     cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
#     return cleaned

# def data_cleaning(text_corpus: Union[dict, List[str], str]) -> list[str]:
#     """
#     Process a multi-line text corpus and return a list of cleaned lines,
#     where each line keeps only the first '--' as separator and has emails removed.
#     """
#     if text_corpus is None:
#         return []
    
#     internal_list = []

#     for key, text_corpus in text_corpus.enumerate():
#         value = text_corpus.splitlines()
#         if value is None:
#             # Skip Nones; though splitlines() won’t produce None
#                        continue
#         cleaned_line = clean_line_keep_first_double_dash(value)
#         internal_list.append(cleaned_line)


# print(type(description)
# cleaned_lines = data_cleaning(description)
# for ln in cleaned_lines:
#     print(ln)


# import re
# from typing import List, Union, Dict, Iterable, Any, Optional

# # Pre-compiled email regex (simple, pragmatic pattern)
# EMAIL_RE = re.compile(
#     r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
# )

# # Normalize various unicode dashes to ASCII '-' for consistency
# UNICODE_DASHES = r'[\u2012\u2013\u2014\u2015\u2212]'

# def _normalize_dashes(text: str) -> str:
#     if not text:
#         return text
#     # Replace common unicode dashes with '-'
#     text = re.sub(UNICODE_DASHES, '-', text)
#     # Collapse runs of 3+ '-' to exactly '--' (e.g., '----' -> '--')
#     text = re.sub(r'-{3,}', '--', text)
#     return text

# def clean_line_keep_first_double_dash(line: str) -> str:
#     """
#     Keep only the first occurrence of '--' in a line as the key/value separator.
#     Replace any subsequent '--' with a single space. Remove emails and normalize whitespace.
#     """
#     if line is None:
#         return ""
#     # Basic normalization first
#     line = (
#         str(line)
#         .replace("\x08", "")
#         .replace("\t", " ")
#         .replace("\r", " ")
#     )
#     line = _normalize_dashes(line)

#     # Split on the first '--' only
#     parts = line.split('--', 1)
#     if len(parts) == 1:
#         # No '--' present; just remove emails and normalize whitespace
#         line = EMAIL_RE.sub(' ', line)
#         line = re.sub(r'\s{2,}', ' ', line).strip()
#         return line

#     head, tail = parts[0], parts[1]

#     # Remove emails from both head and tail
#     head = EMAIL_RE.sub(' ', head)
#     tail = EMAIL_RE.sub(' ', tail)

#     # Replace any further '--' in the tail with a space
#     tail = tail.replace('--', ' ')

#     # Recompose, preserving the first separator
#     cleaned = f"{head}--{tail}"

#     # Normalize whitespace
#     cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
#     return cleaned


# def _to_iterable_of_lines(text_corpus: Any) -> Iterable[str]:
#     """
#     Normalize various input types to an iterable of lines (strings).
#     Accepts str, list[str], dict(any->str), pandas Series, or a DataFrame column (Series).
#     Splits multi-line strings into individual lines.
#     """
#     # Lazy import to avoid hard dependency if pandas isn't used
#     try:
#         import pandas as pd
#         is_series = isinstance(text_corpus, pd.Series)
#     except Exception:
#         is_series = False

#     if text_corpus is None:
#         return []

#     # If a single string: split into lines
#     if isinstance(text_corpus, str):
#         return [ln for ln in text_corpus.splitlines() if ln is not None]

#     # If a dict: take values (assuming values are strings or None)
#     if isinstance(text_corpus, dict):
#         lines: List[str] = []
#         for v in text_corpus.values():
#             if v is None:
#                 continue
#             if isinstance(v, str):
#                 lines.extend(v.splitlines())
#             elif isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
#                 # If values are lists of strings
#                 for item in v:
#                     if item is None:
#                         continue
#                     lines.extend(str(item).splitlines())
#             else:
#                 lines.extend(str(v).splitlines())
#         return lines

#     # If a list/tuple: may contain strings or multi-line strings
#     if isinstance(text_corpus, (list, tuple)):
#         lines: List[str] = []
#         for item in text_corpus:
#             if item is None:
#                 continue
#             if isinstance(item, str):
#                 lines.extend(item.splitlines())
#             else:
#                 lines.extend(str(item).splitlines())
#         return lines

#     # If pandas Series (DataFrame column)
#     if is_series:
#         # Convert to strings safely and splitlines
#         # Drop NaN
#         series = text_corpus.dropna().astype(str)
#         lines: List[str] = []
#         for cell in series:
#             lines.extend(cell.splitlines())
#         return lines

#     # Fallback: convert to string and split
#     return str(text_corpus).splitlines()


# def data_cleaning(text_corpus: Union[Dict[Any, Any], List[str], str]) -> List[str]:
#     """
#     Process a text corpus and return a list of cleaned lines,
#     where each line keeps only the first '--' as separator and has emails removed.
#     Accepts str, list[str], dict(any->str), pandas Series, or DataFrame column (Series).
#     """
#     lines = _to_iterable_of_lines(text_corpus)
#     cleaned: List[str] = []
#     for ln in lines:
#         # Skip empty/whitespace-only lines
#         if ln is None:
#             continue
#         s = ln.strip()
#         if not s:
#             continue
#         cleaned.append(clean_line_keep_first_double_dash(s))
#     return cleaned



import re
from typing import List, Union, Dict, Iterable, Any, Optional

# Pre-compiled email regex (simple, pragmatic pattern)
EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

# Normalize various unicode dashes to ASCII '-' for consistency
UNICODE_DASHES = r'[\u2012\u2013\u2014\u2015\u2212]'

def _normalize_dashes(text: str) -> str:
    if not text:
        return text
    # Replace common unicode dashes with '-'
    text = re.sub(UNICODE_DASHES, '-', text)
    # Collapse runs of 3+ '-' to exactly '--' (e.g., '----' -> '--')
    text = re.sub(r'-{3,}', '--', text)
    return text

def clean_line_keep_first_double_dash(line: str) -> str:
    """
    Keep only the first occurrence of '--' in a line as the key/value separator.
    Replace any subsequent '--' with a single space. Remove emails and normalize whitespace.
    """
    if line is None:
        return ""
    # Basic normalization first
    line = (
        str(line)
        .replace("\x08", "")
        .replace("\t", " ")
        .replace("\r", " ")
    )
    line = _normalize_dashes(line)

    # Split on the first '--' only
    parts = line.split('--', 1)
    if len(parts) == 1:
        # No '--' present; just remove emails and normalize whitespace
        line = EMAIL_RE.sub(' ', line)
        line = re.sub(r'\s{2,}', ' ', line).strip()
        return line

    head, tail = parts[0], parts[1]

    # Remove emails from both head and tail
    head = EMAIL_RE.sub(' ', head)
    tail = EMAIL_RE.sub(' ', tail)

    # Replace any further '--' in the tail with a space
    tail = tail.replace('--', ' ')

    # Recompose, preserving the first separator
    cleaned = f"{head}--{tail}"

    # Normalize whitespace
    cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
    return cleaned


# --------------------------
# Dict-like processing layer
# --------------------------

def _clean_multiline_string(s: Optional[str], keep_empty: bool = False) -> str:
    """
    Clean a multi-line string cell by applying line cleaning to each line,
    then recomposing with newline separators.
    """
    if s is None:
        return "" if keep_empty else ""
    lines = str(s).splitlines()
    cleaned_lines: List[str] = []
    for ln in lines:
        if ln is None:
            continue
        st = ln.strip()
        if not st and not keep_empty:
            continue
        cleaned_lines.append(clean_line_keep_first_double_dash(st))
    return "\n".join(cleaned_lines)

def clean_dictlike_preserve_keys(
    data_map: Dict[str, Any],
    keep_empty_lines: bool = False
) -> Dict[str, Any]:
    """
    Accepts a dict-like where values may be:
        - str (possibly multi-line)
        - list/tuple of strings
        - pandas Series (each cell may be multi-line)
    Returns a dict with the SAME KEYS and processed values of the SAME TYPE,
    so you can directly append to your DataFrame.

    For Series: preserves index alignment, cleans each cell (line-by-line) and rejoins with '\n'.
    For list/tuple: cleans each element (string), preserving element boundaries and rejoins per element.
    For str: cleans and rejoins lines with '\n'.
    """
    try:
        import pandas as pd
        has_pandas = True
    except Exception:
        has_pandas = False

    out: Dict[str, Any] = {}

    for key, val in data_map.items():
        # Handle None
        if val is None:
            out[key] = None
            continue

        # pandas Series (DataFrame column)
        if has_pandas and isinstance(val, pd.Series):
            # Drop NaN -> treat as empty string; preserve index
            cleaned_series = val.astype(str).apply(
                lambda cell: _clean_multiline_string(cell, keep_empty=keep_empty_lines)
            )
            out[key] = cleaned_series
            continue

        # list/tuple of strings (or mixed)
        if isinstance(val, (list, tuple)):
            cleaned_list: List[str] = []
            for item in val:
                if item is None:
                    cleaned_list.append("" if keep_empty_lines else "")
                    continue
                cleaned_list.append(_clean_multiline_string(str(item), keep_empty=keep_empty_lines))
            # Preserve original type (list or tuple)
            out[key] = type(val)(cleaned_list)
            continue

        # single string
        if isinstance(val, str):
            out[key] = _clean_multiline_string(val, keep_empty=keep_empty_lines)
            continue

        # Fallback: convert to str and process
        out[key] = _clean_multiline_string(str(val), keep_empty=keep_empty_lines)

    return out
