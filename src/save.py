from pathlib import Path

import pandas as pd

from src.config import OutputFormat


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_excel(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)


def save_table(df: pd.DataFrame, path: Path, format: OutputFormat):
    match format:
        case OutputFormat.CSV:
            save_csv(df, path)
        case OutputFormat.EXCEL:
            save_excel(df, path)
