# Radiology Report Structuring Application

A web application for batch processing free-text radiology reports and structuring them according to customizable templates using AI.

## Overview

This application enables efficient batch processing of radiology reports, transforming unstructured free-text into standardized, structured data. It combines a modern React frontend with a Python FastAPI backend, powered by a LLM for intelligent text extraction.

## Features

- **Batch Upload**: Upload multiple radiology reports at once
- **LLM-Powered Extraction**: Automatically structure reports using your choice of LLM from OpenAI, Claude, or Ollama.
- **Pre-built Templates**: Ready-to-use templates for common radiology exams
- **Custom Template Designer**: Create templates tailored to your specific needs
- **Export Structured Data**: Access and export structured report data
- **Real-time Progress**: Monitor processing status of report batches
- **Asynchronous Processing**: Celery-powered parallel report processing

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- React Hook Form for form handling
- React Dropzone for file uploads
- TanStack Table for data display
- Axios for API communication

### Backend
- Python 3.11+
- FastAPI web framework
- PostgreSQL database
- Redis for task queue management
- Celery for asynchronous task processing
- SQLAlchemy ORM

## Quick Start

### Getting Started (3 commands)

1. **First-time setup**
   ```bash
   make setup
   ```
   This creates your `.env` file. Edit it and add either your `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or use the Ollama configuration.

2. **Start the application**
   ```bash
   make start
   ```
   Wait approximately 30 seconds for all services to start and health checks to pass.

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

That's it! The database will be automatically seeded with default templates.

### What's Running?

The application runs 5 Docker containers:
- **Frontend** (React) - Port 3000
- **Backend** (FastAPI) - Port 8000
- **Celery Worker** (async tasks)
- **PostgreSQL** (database) - Port 5432
- **Redis** (task queue) - Port 6379

All services include health checks and will auto-restart if they fail.

## Usage Guide

### 1. Uploading Reports

#### Using Pre-built Templates:
1. Go to "Upload Reports" tab
2. Select a template (e.g., "Chest X-Ray", "CT Brain")
3. Enter a batch name (e.g., "Morning Reports - Jan 15")
4. Drag and drop your report files (.txt, .pdf, .doc, .docx)
5. Click "Upload and Process Reports"

#### Example Report Text:
```text
CLINICAL INDICATION: Shortness of breath

TECHNIQUE: PA and lateral chest radiographs

FINDINGS:
The lungs are clear without focal consolidation, pleural effusion, or pneumothorax.
The cardiac silhouette is normal in size.
The mediastinal contours are unremarkable.
No acute osseous abnormalities.

IMPRESSION: Normal chest radiograph.
```

### 2. Viewing Results

1. Navigate to "View Batches" tab
2. Select a batch from the list
3. Monitor processing progress
4. Click on individual reports to see:
   - Structured data extracted by AI
   - Original report text
   - Processing status and confidence score

### 3. Creating Custom Templates

1. Go to "Design Template" tab
2. Enter template information:
   - Name: e.g., "Custom Cardiac MRI"
   - Description: Brief description
   - Template Type: e.g., "cardiac_mri"
3. Add fields:
   - Click "+ Add Field"
   - Enter field name (e.g., "clinical_indication")
   - Choose type (Text or Object)
   - Add description
   - For Object type, add subfields
4. Click "Create Template"

#### Example Custom Template Structure:
```json
{
  "patient_info": {
    "age": "Patient age",
    "gender": "Patient gender"
  },
  "clinical_indication": "Reason for scan",
  "findings": {
    "heart": "Cardiac findings",
    "vessels": "Vascular findings"
  },
  "impression": "Final impression"
}
```

### 4. Default Templates

The application comes with 4 pre-built templates:

1. **Chest X-Ray** - Standard chest radiograph
2. **CT Brain** - CT scan of brain
3. **Abdominal CT** - CT abdomen and pelvis
4. **MRI Spine** - Spine MRI examination

## Future Roadmap

Planned enhancements:

1. Structure reports according to a common data standard/ontology
2. Add local LLM configuration
3. Add export functionality (CSV, JSON)

## License

MIT
