"""
CivicLens — POST /api/upload
Accepts a CSV or Excel file, saves it to disk, runs the cleaning pipeline,
and returns a summary + data quality report.
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

# Import our cleaning pipeline
import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from data_processing.scripts.clean_data import load_file, clean_dataframe, summarize

router = APIRouter()

# Where uploaded files are saved
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 50


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    dataset_name: str = Form(default=""),
):
    """
    Upload a CSV or Excel file.
    - Validates file type and size
    - Saves to /uploads/
    - Runs the data cleaning pipeline
    - Returns metadata + cleaning report + data summary
    """

    # 1. Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: .csv, .xlsx, .xls"
        )

    # 2. Read file bytes and check size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB"
        )

    # 3. Save file to disk with a unique name to avoid collisions
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
        # Remove saved file if processing failed
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Data processing failed: {str(e)}")

    # 5. Return response
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "dataset_name": dataset_name or file.filename,
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
