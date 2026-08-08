import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

import config as app_config


def format_number(value, is_currency: bool = False) -> str:
    if value is None:
        return "N/A"
    formatted = f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"
    return f"KSh {formatted}" if is_currency else formatted


def build_report(kpis: dict, insight: str) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    env.globals["format_number"] = format_number
    template = env.get_template("report.html")

    html = template.render(
        kpis=kpis,
        insight=insight,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    os.makedirs(app_config.OUTPUT_DIR, exist_ok=True)
    slug = kpis["department"].lower().replace(" ", "_")
    out_path = os.path.join(app_config.OUTPUT_DIR, f"{slug}_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return out_path
