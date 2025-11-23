from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import json
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.models import ReportBatch, StructuredReport, Template
from app.schemas.schemas import ReportBatchCreate, ReportBatchResponse, StructuredReportResponse
from app.tasks.report_tasks import process_report_task

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/batches", response_model=ReportBatchResponse, status_code=201)
async def create_batch(
    name: str = Form(...),
    template_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Create a new batch and upload JSON file(s) containing arrays of report texts.
    Expected JSON format: ["report 1 text...", "report 2 text...", ...]
    """
    # Validate template exists
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Collect all reports from all JSON files
    all_reports = []

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, "temp")
    os.makedirs(upload_dir, exist_ok=True)

    # Process each JSON file
    for file in files:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only .json files are allowed."
            )

        # Read and parse JSON file
        try:
            content = await file.read()
            json_data = json.loads(content.decode("utf-8"))

            # Validate that it's an array
            if not isinstance(json_data, list):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid JSON format in {file.filename}. Expected an array of report texts."
                )

            # Validate that array elements are strings
            for idx, report_text in enumerate(json_data):
                if not isinstance(report_text, str):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid report at index {idx} in {file.filename}. Expected string, got {type(report_text).__name__}."
                    )
                if not report_text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Empty report at index {idx} in {file.filename}."
                    )

            # Add reports to collection with source filename
            for report_text in json_data:
                all_reports.append({
                    "text": report_text,
                    "source_file": file.filename
                })

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON in {file.filename}: {str(e)}"
            )

    if not all_reports:
        raise HTTPException(
            status_code=400,
            detail="No reports found in uploaded files."
        )

    # Create batch with correct total_reports count
    batch = ReportBatch(
        name=name,
        template_id=template_id,
        total_reports=len(all_reports),
        status="pending"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Create batch-specific upload directory
    batch_upload_dir = os.path.join(settings.UPLOAD_DIR, str(batch.id))
    os.makedirs(batch_upload_dir, exist_ok=True)

    # Create report records and queue processing
    for idx, report_data in enumerate(all_reports):
        report = StructuredReport(
            batch_id=batch.id,
            template_id=template_id,
            original_text=report_data["text"],
            filename=f"{report_data['source_file']}_report_{idx + 1}",
            status="pending"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # Queue processing task
        process_report_task.delay(report.id)

    return batch


@router.get("/batches", response_model=List[ReportBatchResponse])
def get_batches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all report batches"""
    batches = db.query(ReportBatch).offset(skip).limit(limit).all()
    return batches


@router.get("/batches/{batch_id}", response_model=ReportBatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get a specific batch by ID"""
    batch = db.query(ReportBatch).filter(ReportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/batches/{batch_id}/reports", response_model=List[StructuredReportResponse])
def get_batch_reports(batch_id: int, db: Session = Depends(get_db)):
    """Get all reports in a batch"""
    reports = db.query(StructuredReport).filter(
        StructuredReport.batch_id == batch_id
    ).all()
    return reports


@router.get("/{report_id}", response_model=StructuredReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific structured report"""
    report = db.query(StructuredReport).filter(
        StructuredReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
