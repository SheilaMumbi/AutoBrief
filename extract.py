import pandas as pd

from department_configs import DepartmentConfig


def extract(config: DepartmentConfig) -> pd.DataFrame:
    return pd.read_csv(config.data_path)
