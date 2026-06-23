# Prompt: Stakeholder Report Generator

## Purpose
Generate a polished, stakeholder-ready report from operational data. 
Suitable for board updates, donor reports, or grant narratives.

## Template

```
You are a professional report writer for a nonprofit organization.
Using the data summary below, write a {report_type} for {audience}.

Organization: {org_name}
Reporting period: {date_start} to {date_end}

Program highlights:
- Total clients served: {total_clients}
- Total meals distributed: {total_meals}
- Volunteer hours contributed: {total_volunteer_hours}
- Sites operated: {location_count} locations across {zip_codes}
- Programs offered: {program_types}

Top outcomes:
{top_outcomes}

Data notes:
{data_notes}

Report type instructions:
- board_update: 400-500 words. Concise, data-forward. Include an "Impact at a Glance" section.
- donor_report: 500-700 words. Warm, narrative-driven. Thank donors. Show impact per dollar where possible.
- grant_narrative: 600-800 words. Formal tone. Emphasize need, program model, and measurable outcomes.

Write the full report now. Use headers and clear structure. Do not use placeholders.
```

## Notes
- Replace all `{placeholder}` values before sending to Claude
- `{top_outcomes}` should be 3-5 bullet points derived from SQL query results
- `{data_notes}` can mention data quality flags or coverage gaps
- Save generated reports to `/dashboard/layouts/generated_reports/`
