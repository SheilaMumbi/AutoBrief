import argparse

import config as app_config
from clean import clean
from department_configs import DEPARTMENTS, get_department
from extract import extract
from insights import generate_insight
from kpis import calculate_kpis
from report import build_report
from send import send_report


def run(department_key: str) -> str:
    department = get_department(department_key)

    df = extract(department)
    df = clean(df, department)
    kpis = calculate_kpis(df, department)
    insight = generate_insight(kpis)
    report_path = build_report(kpis, insight)
    send_report(report_path, subject=f"{department.display_name} Report — {kpis['period_end']}")

    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AutoBrief pipeline for one department.")
    parser.add_argument("--department", choices=list(DEPARTMENTS), default=app_config.DEPARTMENT)
    args = parser.parse_args()

    path = run(args.department)
    print(f"Report built -> {path}")
