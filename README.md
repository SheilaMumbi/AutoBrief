# AutoBrief
 
**An automated sales reporting pipeline; pulls data, cleans it, calculates KPIs, generates written insights with the Gemini API, and emails the finished report.**
 
This project replaces a task that's normally done by hand every week (pulling numbers, building a summary, writing commentary, sending it around) with a pipeline that does it end to end. It's built as six small, single-purpose steps rather than one script, so each stage can be tested, swapped, or extended on its own.
 
> 🚧 Work in progress — I'm building and documenting this one piece at a time. Check the commit history to follow the build in order.

## What it does
 
1. **Extract** — pull raw sales data (currently CSV, designed to swap in a Postgres/Neon connection)
2. **Clean** — fix nulls, drop duplicates, correct bad values, standardize formats
3. **Calculate KPIs** — revenue, period-over-period growth, top products/regions/categories
4. **Generate insights** — feed the *computed* KPIs (never raw data) to the Gemini API to write a plain-English summary
5. **Build the report** — render KPIs + summary into a styled HTML report
6. **Send it** — email the finished report automatically
The KPI math is always done in plain Python/pandas — the AI's only job is narrating numbers that were already calculated, not doing arithmetic itself. That keeps the numbers trustworthy while still getting the benefit of a written summary.