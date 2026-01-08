
import pandas as pd
from typing import List

def _parse_csv(user_input: str) -> List[str]:
    return [c.strip() for c in user_input.split(",") if c.strip()]

def normalize_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures DataFrame has complete column headers.
    Handles:
      - No headers
      - Partial headers
    """
    df = df.copy()

    current_cols = list(df.columns)
    n_cols = df.shape[1]

    print("\nCurrent DataFrame columns:")
    for i, c in enumerate(current_cols):
        print(f"  {i}: {c}")

    header_exists = input(
        "\nDoes the dataset have column headers? (y/n): "
    ).strip().lower()

    # ---- No headers at all ----
    if header_exists == "n":
        new_cols = input(
            f"Enter ALL {n_cols} column names (comma-separated): "
        )
        parsed = _parse_csv(new_cols)

        if len(parsed) != n_cols:
            raise ValueError(
                f"Expected {n_cols} column names, got {len(parsed)}"
            )

        df.columns = parsed
        print("✅ Column headers assigned.")
        return df

    # ---- Partial headers ----
    missing_indices = [
        i for i, c in enumerate(current_cols)
        if c is None or str(c).startswith("Unnamed")
    ]

    if not missing_indices:
        print("✅ All column headers already present.")
        return df

    print("\nMissing column positions:")
    print(missing_indices)

    for idx in missing_indices:
        col_name = input(
            f"Enter column name for position {idx}: "
        ).strip()
        current_cols[idx] = col_name

    df.columns = current_cols
    print("✅ Missing column headers filled.")
    return df

