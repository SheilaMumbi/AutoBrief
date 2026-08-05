import argparse
import random

import pandas as pd

from department_configs import DEPARTMENTS, get_department

random.seed(42)  # fixed seed = same "random" data every time you run this


def generate_for(department_key: str) -> str:
    config = get_department(department_key)
    df = pd.DataFrame(config.generate_sample_rows())
    df.to_csv(config.data_path, index=False)
    return config.data_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample data for one or all departments.")
    parser.add_argument(
        "--department",
        choices=list(DEPARTMENTS) + ["all"],
        default="all",
        help="Which department to generate data for (default: all)",
    )
    args = parser.parse_args()

    keys = list(DEPARTMENTS) if args.department == "all" else [args.department]
    for key in keys:
        path = generate_for(key)
        print(f"Generated {DEPARTMENTS[key].display_name} data -> {path}")
