# Fictional dashboard data

All values are invented for development and class demonstrations. They are not stakeholder data, estimates of UMBC activity, or verified office statistics. Retriever Essentials is named in the SRS. Student Support (Demo Office) and Emergency Aid (Demo Office) are fictional placeholders, not confirmed UMBC offices. Metrics other than the SRS example of food pantry visits are proposed demo choices pending stakeholder confirmation.

## Files and scope

- `dashboard_metrics.csv`: all 288 metric observations.
- `retriever_essentials.csv`: 96 observations for one office.
- `demo_student_support.csv`: 96 observations for one placeholder office.
- `demo_emergency_aid.csv`: 96 observations for one placeholder office.
- `dashboard_metrics.json`: the same records under a `records` key, with dataset metadata.
- `generate.ps1`: deterministic generator. Run `& .\sample_data\generate.ps1` from the repository folder to regenerate.

The files cover October 2025 through September 2026, including summer dips, semester increases, different office volumes, decimal quantities, and an intentional zero-dollar aid observation. Each row represents one metric for one office, calendar month, and student level. There are no individual student records, names, emails, or IDs.

## Fields

| Field | Meaning |
| --- | --- |
| record_id | Stable demo observation ID, not a student ID or existing database key |
| office_id | Demo office slug, not the integer primary key in the Django Office model |
| office_name | Display label |
| time_period | First day of the month in ISO format |
| period_end | Last day of that month in ISO format |
| student_level | undergraduate or graduate |
| metric | Machine-readable metric name |
| value | Nonnegative number; CSV readers should parse as decimal |
| unit | Unit for that metric |
| is_demo | True for every record |

The natural uniqueness key is (office_id, time_period, student_level, metric).

## Metric definitions and aggregation

| Metric | Definition | Aggregation |
| --- | --- | --- |
| service_interactions | Food pantry visits for Retriever Essentials; support contacts for the demo offices. Repeat contacts count. | Sum across periods and levels; cross-office totals mean interactions, not people. |
| unique_students | Distinct students within one office, month, and student level, simulated as 68% of interactions. | Sum levels within one office and month only. Never sum across months or offices and label the result unique students. |
| referrals_made | Referral actions, simulated as 14% of interactions. | Sum; not a count of distinct referred students. |
| food_distributed_lb | Fictional pounds of food distributed by Retriever Essentials. | Sum within this metric. |
| cases_resolved | Fictional case resolution events at Demo Student Support. | Sum within this metric. This is not a cohort completion rate. |
| aid_disbursed_usd | Fictional dollars distributed by Demo Emergency Aid. | Sum within this metric. Zero is a recorded amount, not missing data. |

Do not sum the entire `value` column: that would mix students, visits, pounds, cases, and dollars. A metric absent from an office is not applicable, rather than a zero.

## Suggested dashboard

1. Filter by office, reporting month range, student level, and metric.
2. Show KPI cards for service interactions and referrals in the selection, plus that office's specific metric. Show unique students only when exactly one office and one month are selected.
3. Use a line chart for a single metric over months, and a bar chart for that metric split by student level. Use shared metrics for office comparisons.
4. Show the filtered observations in a table and export the same selection.
5. Display `Demo data — fictional values` above the dashboard.

These monthly aggregates support month-level filtering. They cannot produce accurate daily or partial-month counts; use a month picker or explicitly filter on reporting month. They support the date and student-level filters described in SRS sections 4 and 7, and the metric/value concept in section 6.

## Application integration boundary

These are software data fixtures, not Django `loaddata` fixtures. The Data page now accepts the JSON file and stores records in the MetricRecord model. See [IMPORTING.md](IMPORTING.md) for setup and permissions. There is no CSV importer yet. The CSV format is a proposed interchange schema, not an established stakeholder upload contract.

After importing, query MetricRecord through Django to filter by office, reporting month, student level, and metric. The JSON importer maps office names to Office rows and derives ownership from the authenticated account. MetricRecord stores the metric name and value together as a simplified initial schema, rather than implementing every separate entity in SRS section 6. DataImport tracks upload metadata. The dashboard itself is not connected to these records yet.

Use the per-office CSVs for future director upload demos. The combined CSV is for development and executive cross-office views. When migrating to real data, replace these files and confirm metric definitions, period grain, and upload columns with the stakeholders.
