"""
CivicLens — POST /api/upload
Accepts a CSV or Excel file, saves it to disk, runs the cleaning pipeline,
persists cleaned rows to PostgreSQL, and returns a quality report.
"""

import os
import uuid
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Database
from backend.utils.database import get_db
from backend.api.models.dataset import Dataset, OperationalRecord, DataQualityLog

# Cleaning pipeline
import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from data_processing.scripts.clean_data import load_file, clean_dataframe, summarize

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 50


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    dataset_name: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV or Excel file.
    - Validates file type and size
    - Saves to /uploads/
    - Runs the data cleaning pipeline
    - Saves cleaned rows to PostgreSQL
    - Returns metadata + cleaning report + summary
    """

    # 1. Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: .csv, .xlsx, .xls"
        )

    # 2. Read and size-check the file
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB"
        )

    # 3. Save to disk
    unique_id = uuid.uuid4().hex[:8]
    saved_filename = f"{unique_id}_{file.filename}"
    save_path = UPLOAD_DIR / saved_filename
    with open(save_path, "wb") as f:
        f.write(contents)

    # 4. Run cleaning pipeline
    try:
        df = load_file(str(save_path))
        result = clean_dataframe(df)
        cleaned_df = result["cleaned_df"]
        cleaning_report = result["report"]
        data_summary = summarize(cleaned_df)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Data processing failed: {str(e)}")

    # 5. Save Dataset record to DB
    dataset = Dataset(
        name=dataset_name or file.filename,
        filename=saved_filename,
        row_count=cleaning_report["cleaned_rows"],
        status="cleaned",
    )
    db.add(dataset)
    db.flush()  # Get the auto-generated dataset.id before committing

    # 6. Save each cleaned row as an OperationalRecord
    for _, row in cleaned_df.iterrows():
        def safe(val):
            """Convert NaN/NaT to None for DB storage."""
            if val is None:
                return None
            try:
                if np.isnan(val):
                    return None
            except (TypeError, ValueError):
                pass
            return val

        record = OperationalRecord(
            dataset_id      = dataset.id,
            record_date     = row.get("date") if not str(row.get("date")) == "NaT" else None,
            location        = row.get("location"),
            program_type    = row.get("program_type"),
            clients_served  = safe(row.get("clients_served")),
            meals_distributed = safe(row.get("meals_distributed")),
            inventory_lbs   = safe(row.get("inventory_lbs")),
            volunteer_hours = safe(row.get("volunteer_hours")),
            zip_code        = str(row.get("zip_code", "")) or None,
            notes           = row.get("notes"),
        )
        db.add(record)

    # 7. Save quality issues to DataQualityLog
    if cleaning_report["duplicates_removed"] > 0:
        db.add(DataQualityLog(
            dataset_id=dataset.id,
            issue_type="duplicate",
            detail=f"{cleaning_report['duplicates_removed']} duplicate rows removed",
        ))

    if cleaning_report["nulls_filled"] > 0:
        db.add(DataQualityLog(
            dataset_id=dataset.id,
            issue_type="null",
            detail=f"{cleaning_report['nulls_filled']} null numeric values filled with 0",
        ))

    db.commit()
    db.refresh(dataset)

    # 8. Return response
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "original_filename": file.filename,
            "saved_as": saved_filename,
            "file_size_mb": round(size_mb, 3),
            "cleaning_report": {
                "original_rows": cleaning_report["original_rows"],
                "cleaned_rows": cleaning_report["cleaned_rows"],
                "duplicates_removed": cleaning_report["duplicates_removed"],
                "nulls_filled": cleaning_report["nulls_filled"],
                "type_fixes": cleaning_report["type_fixes"],
                "flagged_row_count": len(cleaning_report["flagged_rows"]),
            },
            "data_summary": {
                "row_count": data_summary["row_count"],
                "column_count": data_summary["column_count"],
                "columns": data_summary["columns"],
                "date_range": data_summary["date_range"],
                "numeric_summary": data_summary["numeric_summary"],
            },
        },
    )
