from pathlib import Path

import pandas as pd

from src.config import OutputFormat


def save_csv(df: pd.DataFrame, path: Path) -> Path:
    path_csv = path.with_suffix(".csv")
    df.to_csv(path_csv, index=False)
    return path_csv


def save_excel(df: pd.DataFrame, path: Path) -> Path:
    path_excel = path.with_suffix(".xlsx")

    with pd.ExcelWriter(path_excel) as writer:
        EXTRA_SPACE = 4
        SHEET_NAME = "Sheet1"

        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)  # type: ignore

        # Auto-adjust all columns to fit their longest value
        for column in df:
            column_length: int = max(df[column].astype(str).map(len).max(), len(column))  # type: ignore
            col_idx = df.columns.get_loc(column)  # type: ignore
            writer.sheets[SHEET_NAME].set_column(
                col_idx, col_idx, column_length + EXTRA_SPACE
            )

    return path_excel


def save_table(df: pd.DataFrame, path: Path, format: OutputFormat):
    # Ensure dir exists
    path.parent.mkdir(parents=True, exist_ok=True)

    match format:
        case OutputFormat.CSV:
            return save_csv(df, path)
        case OutputFormat.EXCEL:
            return save_excel(df, path)
