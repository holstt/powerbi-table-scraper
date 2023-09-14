# import log
import logging
from pathlib import Path

import pandas as pd

from src.config import OutputFormat

logger = logging.getLogger(__name__)


def save_csv(df: pd.DataFrame, path: Path) -> Path:
    # Warn if file name ends with .csv (we do not want to risk overwriting a file unintentionally by changing the path suffix from code)
    if path.suffix != ".csv":
        logger.warning(f"Saving as csv, but file extension is {path.suffix}")
        # raise ValueError(f"Path must end with .csv, got {path}")

    df.to_csv(path, index=False)
    return path


def save_excel(df: pd.DataFrame, path: Path) -> Path:
    if path.suffix != ".xlsx":
        logger.warning(f"Saving as excel, but file extension is {path.suffix}")
        # raise ValueError(f"Path must end with .xlsx, got {path}")

    with pd.ExcelWriter(path) as writer:
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

    return path


def save_table(df: pd.DataFrame, path: Path, format: OutputFormat):
    # Ensure dir exists
    path.parent.mkdir(parents=True, exist_ok=True)

    match format:
        case OutputFormat.CSV:
            return save_csv(df, path)
        case OutputFormat.EXCEL:
            return save_excel(df, path)
