import config as app_config
from report import format_number


def generate_insight(kpis: dict) -> str:
    if not app_config.GEMINI_API_KEY:
        return _fallback_summary(kpis)

    try:
        from google import genai

        client = genai.Client(api_key=app_config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=_build_prompt(kpis),
        )
        text = (response.text or "").strip()
        return text or _fallback_summary(kpis)
    except Exception:
        return _fallback_summary(kpis)


def _build_prompt(kpis: dict) -> str:
    growth_pct = kpis["growth_pct"] or 0
    direction = "up" if growth_pct >= 0 else "down"

    lines = [
        f"You are writing a short, plain-English weekly summary for the {kpis['department']} team.",
        f"Headline metric — {kpis['metric_label']}: {kpis['current_total']} "
        f"({direction} {abs(growth_pct)}% vs the prior {30}-day period, which was {kpis['previous_total']}).",
    ]
    for breakdown in kpis["breakdowns"]:
        top = ", ".join(f"{row['name']} ({row['amount']})" for row in breakdown["rows"][:3])
        if top:
            lines.append(f"{breakdown['label']}: {top}")

    lines.append(
        "Write 2-3 sentences highlighting what changed and why it might matter to this team. "
        "Only use the numbers given above — do not invent or estimate anything else."
    )
    return "\n".join(lines)


def _fallback_summary(kpis: dict) -> str:
    growth_pct = kpis["growth_pct"]
    if growth_pct is None:
        trend = "no prior-period data to compare against"
    else:
        direction = "up" if growth_pct >= 0 else "down"
        trend = f"{direction} {abs(growth_pct)}% versus the prior period"

    total = format_number(kpis["current_total"], kpis["is_currency"])
    return (
        f"{kpis['department']} {kpis['metric_label']} totaled {total} "
        f"for {kpis['period_start']} to {kpis['period_end']}, {trend}."
    )
