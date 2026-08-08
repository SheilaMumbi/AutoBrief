# AutoBrief

**Every department has the same Friday afternoon.**

Someone opens a spreadsheet, exports the week's numbers, and starts building a summary by hand — pulling totals, comparing them to last week, guessing at *why* something moved, formatting it into something presentable, and emailing it around before they can log off. Sales does it. So does Finance, Marketing, Support, HR, and whoever owns the supply chain spreadsheet. Six teams, six versions of the same manual ritual, every single week.

None of that work is actually hard. It's just repetitive in a way that eats an afternoon and produces a report that's stale the moment it's sent, written by whoever had time that day rather than whoever's best at writing it.

**AutoBrief is that ritual, automated.** Point it at a department's data — one of six built-in sample datasets, or a CSV/JSON file you upload yourself — and it pulls the numbers, cleans them up, calculates the KPIs that matter, writes a plain-English summary of what changed, renders it into a report with charts, and emails it to whoever needs to see it. What used to be an hour of manual work is a few seconds and a click.

It started as a single sales-reporting script. It's now a small multi-user web app: sign in, pick a department (or bring your own data), watch the dashboard build itself, and send it on.

---

## What it actually solves

| The manual version | AutoBrief |
|---|---|
| Export data, eyeball it for errors | Cleaning is automatic — nulls, duplicates, and bad values are handled before a KPI is ever calculated |
| Manually calculate totals and % change | KPIs and period-over-period growth are computed in plain pandas — no guessing, no stale formulas |
| Write commentary explaining the numbers | Gemini reads the *computed* KPIs and writes a short summary — it never touches raw data, so it can't misreport a number |
| Format it into something presentable | A styled report with charts is generated automatically |
| Email it manually, one recipient at a time | Type an address, hit send — from any device, no spreadsheet required |
| Only works for whichever department built the script | One engine, six departments out of the box, plus upload-your-own-data for anything else |

## Tour of the codebase

### Entry points
| File | What it does |
|---|---|
| **`app.py`** | The Flask app. Wires up the database, login manager, and blueprints; owns the routes for the dashboard (`/`), a department's report (`/department/<key>`), sending it (`/department/<key>/send`), settings (`/settings`), and the owner-only admin view (`/admin`). |
| **`main.py`** | The original CLI entry point — runs all six pipeline steps for one department and exits. `python main.py --department finance`. Useful for cron jobs / scheduled runs without the web app at all. |

### The pipeline (generic — no department-specific code lives here)
| File | What it does |
|---|---|
| **`extract.py`** | Step 1. Reads a department's CSV into a DataFrame. Doesn't care if that CSV is a bundled sample or something a user uploaded five minutes ago — both are just a `data_path` on a `DepartmentConfig`. |
| **`clean.py`** | Step 2. Drops duplicate rows, coerces numeric/date columns, fills missing text values with `"Unknown"`, and throws out rows with an impossible (negative) metric. Driven entirely by what the config says *should* be numeric — no hardcoded column names. |
| **`kpis.py`** | Step 3. Splits the data into "this 30 days" vs. "the 30 days before that," sums the metric for each, calculates % growth, and ranks the top 5 rows for each breakdown (e.g. top products, top regions). Returns one plain dict — the single source of truth every other step reads from. |
| **`insights.py`** | Step 4. Hands the KPI dict to Gemini (`gemini-flash-latest`) and asks for 2–3 sentences on what changed and why it matters. If there's no API key, or the call fails, it falls back to a template-generated sentence instead of breaking the report. |
| **`report.py`** | Step 5. Renders `templates/report.html` into a standalone HTML file (what actually gets emailed), and holds `format_number()` — the one function that decides currency formatting (`KSh 1,234.00`) everywhere in the app, web and email alike. |
| **`send.py`** | Step 6. Emails the rendered report via SMTP. When `DRY_RUN=true` (the default) or no recipient is given, it just prints what *would* have been sent instead of touching the network. |