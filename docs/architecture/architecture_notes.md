# CivicLens — Architecture Notes

## Overview

CivicLens is structured as a three-tier web application:
- **Presentation layer**: React frontend
- **Application layer**: FastAPI backend
- **Data layer**: PostgreSQL + data processing scripts

---

## Component Breakdown

### Frontend (`/frontend`)
Built with React 18 + Vite + Tailwind CSS.

| Folder | Purpose |
|---|---|
| `src/components/` | Reusable UI components (cards, charts, buttons) |
| `src/pages/` | Route-level page components (Upload, Dashboard, Q&A, Reports) |
| `src/hooks/` | Custom React hooks (useDataset, useClaude) |
| `src/utils/` | API client (axios), formatters, helpers |
| `public/` | Static assets |

Key pages:
- `/` — Home / Upload page
- `/dashboard/:datasetId` — Dashboard for a specific dataset
- `/qa/:datasetId` — Natural language Q&A interface
- `/reports/:datasetId` — Report generation interface

---

### Backend (`/backend`)
Built with FastAPI (Python). Exposes a REST API.

| Folder | Purpose |
|---|---|
| `api/` | FastAPI app, route handlers, request/response models |
| `services/` | Business logic (ClaudeService, DataService, ReportService) |
| `utils/` | Shared helpers (db connection, file handling) |
| `tests/` | pytest test suite |

Key endpoints (planned):
```
POST   /api/upload              Upload and process a file
GET    /api/datasets            List all datasets
GET    /api/datasets/{id}       Get dataset metadata + summary
POST   /api/query               Natural language Q&A
POST   /api/summary/{id}        Generate Claude summary
POST   /api/report/{id}         Generate stakeholder report
GET    /api/quality/{id}        Get data quality report
```

---

### Data Processing (`/data_processing`)
Pure Python scripts. Run as part of the upload pipeline.

| File | Purpose |
|---|---|
| `scripts/clean_data.py` | Main cleaning and validation logic |
| `validators/` | Per-column type and range validators |
| `transformers/` | Data transformations (date normalization, column mapping) |
| `sample_data/` | Sample CSV for development and testing |

Processing pipeline:
1. File uploaded → saved to `/uploads/`
2. `load_file()` reads CSV or Excel into a DataFrame
3. `clean_dataframe()` applies validation rules and returns a cleaned DataFrame + report
4. Backend ingests cleaned rows into PostgreSQL via SQLAlchemy
5. `summarize()` computes statistics for use in Claude prompts

---

### Database (`/database`)
PostgreSQL 15. Managed with SQLAlchemy ORM and Alembic migrations.

| Folder | Purpose |
|---|---|
| `schemas/` | Raw SQL schema definitions |
| `migrations/` | Alembic migration scripts |
| `queries/` | Analytical SQL queries (used in backend services) |
| `seeds/` | Seed scripts to load sample data |

Core tables:
- `datasets` — uploaded file metadata
- `operational_records` — cleaned row-level data
- `claude_queries` — log of all Claude API calls
- `data_quality_log` — issues flagged during cleaning

---

### Claude Prompts (`/claude_prompts`)
Markdown template files. Each prompt is versioned and editable.

| Folder | Prompt type |
|---|---|
| `summary/` | Dataset summary generation |
| `qa/` | Natural language → SQL → answer |
| `reports/` | Stakeholder report generation |
| `templates/` | Shared prompt components (system messages, tone guidelines) |

All prompts are rendered server-side with Python f-strings before being sent to the Claude API.

---

### Dashboard (`/dashboard`)
React visualization layer. Uses Recharts.

| Folder | Purpose |
|---|---|
| `charts/` | Individual chart components (LineChart, BarChart, KPICard) |
| `widgets/` | Composite dashboard widgets |
| `layouts/` | Page-level dashboard layouts |

---

## Design Decisions

**Why FastAPI?** Async-first, automatic OpenAPI docs, Pydantic validation — ideal for a data API.

**Why PostgreSQL?** Supports complex analytical queries, JSON columns for flexible schema, scales well.

**Why Recharts?** Pure React, composable, well-maintained, good Tailwind compatibility.

**Why prompt templates as Markdown files?** Non-technical users and prompt engineers can edit them without touching Python code. Makes iteration fast.

**Why separate data processing from backend?** The cleaning scripts can be run standalone (CLI or scheduled job) without needing the API server, which simplifies testing and future batch workflows.

---

## Future Architecture Considerations

- **Background jobs**: Use Celery + Redis for async processing of large files
- **Auth**: Add JWT-based authentication for multi-org support
- **Caching**: Redis cache for expensive SQL aggregations
- **Observability**: Add structured logging and trace IDs for all Claude API calls
