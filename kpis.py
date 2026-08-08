from datetime import timedelta

import pandas as pd

from department_configs import DepartmentConfig

PERIOD_DAYS = 30


def calculate_kpis(df: pd.DataFrame, config: DepartmentConfig) -> dict:
    period_end = df[config.date_column].max()
    current_start = period_end - timedelta(days=PERIOD_DAYS - 1)
    previous_start = current_start - timedelta(days=PERIOD_DAYS)
    previous_end = current_start - timedelta(days=1)

    current = df[df[config.date_column] >= current_start]
    previous = df[
        (df[config.date_column] >= previous_start) & (df[config.date_column] <= previous_end)
    ]

    current_total = round(float(current[config.metric_column].sum()), 2)
    previous_total = round(float(previous[config.metric_column].sum()), 2)

    if previous_total:
        growth_pct = round((current_total - previous_total) / previous_total * 100, 1)
    else:
        growth_pct = None

    breakdowns = []
    for breakdown in config.breakdowns:
        grouped = (
            current.groupby(breakdown.column)[config.metric_column]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        breakdowns.append(
            {
                "label": breakdown.label,
                # "rows", not "values" — dict.values is a built-in method name,
                # which Jinja's dot-notation would resolve instead of a dict key.
                "rows": [
                    {"name": name, "amount": round(float(amount), 2)}
                    for name, amount in grouped.items()
                ],
            }
        )

    return {
        "department": config.display_name,
        "metric_label": config.metric_label,
        "is_currency": config.is_currency,
        "higher_is_better": config.higher_is_better,
        "current_total": current_total,
        "previous_total": previous_total,
        "growth_pct": growth_pct,
        "period_start": current_start.date().isoformat(),
        "period_end": period_end.date().isoformat(),
        "breakdowns": breakdowns,
    }
