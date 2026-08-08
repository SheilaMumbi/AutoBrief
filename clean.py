import pandas as pd

from department_configs import DepartmentConfig


def clean(df: pd.DataFrame, config: DepartmentConfig) -> pd.DataFrame:
    df = df.drop_duplicates()

    df[config.date_column] = pd.to_datetime(df[config.date_column], errors="coerce")

    for column in config.numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    text_columns = [
        column for column in df.columns
        if column not in config.numeric_columns and column != config.date_column
    ]
    for column in text_columns:
        df[column] = df[column].fillna("Unknown")

    df = df.dropna(subset=[config.date_column, *config.numeric_columns])
    df = df[df[config.metric_column] >= 0]

    return df.reset_index(drop=True)
