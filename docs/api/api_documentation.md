# CivicLens API Documentation

> Base URL: `http://localhost:8000`  
> All endpoints return JSON. All request bodies are JSON unless noted.

---

## Health

### `GET /health`
Returns API status.

**Response**
```json
{ "status": "ok" }
```

---

## Datasets

### `POST /api/upload`
Upload a CSV or Excel file. The file is cleaned and stored.

**Request** — `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | CSV or Excel file |
| `dataset_name` | string | No | Human-readable name |

**Response**
```json
{
  "dataset_id": 1,
  "name": "Q1 Distribution Data",
  "row_count": 30,
  "status": "cleaned",
  "cleaning_report": {
    "duplicates_removed": 0,
    "nulls_filled": 4,
    "flagged_rows": []
  }
}
```

---

### `GET /api/datasets`
List all uploaded datasets.

**Response**
```json
[
  {
    "id": 1,
    "name": "Q1 Distribution Data",
    "row_count": 30,
    "uploaded_at": "2024-01-08T10:00:00Z",
    "status": "cleaned"
  }
]
```

---

### `GET /api/datasets/{dataset_id}`
Get metadata and summary stats for a specific dataset.

**Response**
```json
{
  "id": 1,
  "name": "Q1 Distribution Data",
  "date_range": { "start": "2024-01-08", "end": "2024-03-11" },
  "row_count": 30,
  "total_clients": 4521,
  "total_meals": 14203,
  "locations": ["Downtown Hub", "Eastside Center", "Westpark Pantry", "Northside Clinic"],
  "program_types": ["Emergency Food Box", "Senior Meal Program", "Mobile Pantry", "Health Screening"]
}
```

---

## Claude Endpoints

### `POST /api/summary/{dataset_id}`
Generate a plain-English summary of the dataset using Claude.

**Response**
```json
{
  "dataset_id": 1,
  "summary": "Between January and March 2024, your team served over 4,500 clients..."
}
```

---

### `POST /api/query`
Ask a natural language question about a dataset.

**Request body**
```json
{
  "dataset_id": 1,
  "question": "Which location served the most clients in February?"
}
```

**Response**
```json
{
  "question": "Which location served the most clients in February?",
  "sql": "SELECT location, SUM(clients_served) AS total FROM operational_records WHERE ...",
  "result": [{ "location": "Westpark Pantry", "total": 645 }],
  "answer": "Westpark Pantry served the most clients in February, with 645 people helped."
}
```

---

### `POST /api/report/{dataset_id}`
Generate a stakeholder report using Claude.

**Request body**
```json
{
  "report_type": "donor_report",
  "audience": "major donors",
  "org_name": "Bay Area Food Network",
  "date_start": "2024-01-01",
  "date_end": "2024-03-31"
}
```

**Response**
```json
{
  "dataset_id": 1,
  "report_type": "donor_report",
  "content": "Dear Friends and Supporters,\n\nThis quarter, your generosity made it possible..."
}
```

---

## Data Quality

### `GET /api/quality/{dataset_id}`
Get the data quality report for a dataset.

**Response**
```json
{
  "dataset_id": 1,
  "duplicates_removed": 0,
  "nulls_filled": 4,
  "flagged_issues": [
    { "issue_type": "null", "column_name": "meals_distributed", "row_index": 7, "detail": "Health Screening events typically have no meal count" }
  ]
}
```

---

## Error Responses

All errors follow this shape:
```json
{
  "detail": "Human-readable error message",
  "error_code": "UPLOAD_FAILED"
}
```

Common HTTP status codes:
| Code | Meaning |
|---|---|
| 400 | Bad request (invalid file type, missing field) |
| 404 | Dataset not found |
| 422 | Validation error |
| 500 | Internal server error |
