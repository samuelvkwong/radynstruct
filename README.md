# Radiology Report Structuring Application

A web application for batch processing free-text radiology reports and structuring them according to customizable templates using AI.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Project Structure](#project-structure)
7. [Installation & Development](#installation--development)
8. [Usage Guide](#usage-guide)
9. [API Reference](#api-reference)
10. [Common Commands](#common-commands)
11. [Architecture](#architecture)
12. [Troubleshooting](#troubleshooting)
13. [Development](#development)
14. [Performance & Security](#performance--security)
15. [Future Roadmap](#future-roadmap)
16. [License](#license)

## Overview

This application enables efficient batch processing of radiology reports, transforming unstructured free-text into standardized, structured data. It combines a modern React frontend with a Python FastAPI backend, powered by AI for intelligent text extraction.

## Features

- **Batch Upload**: Upload multiple radiology reports at once
- **AI-Powered Extraction**: Automatically structure reports using Claude API
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
- Anthropic Claude API for AI processing

## Prerequisites

- Docker & Docker Compose installed
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Quick Start

### Getting Started (3 commands)

1. **First-time setup**
   ```bash
   make setup
   ```
   This creates your `.env` file. Edit it and add your `ANTHROPIC_API_KEY`:
   ```env
   ANTHROPIC_API_KEY=your_api_key_here
   SECRET_KEY=change-this-to-a-random-string
   ```

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

## Project Structure

### High-level Structure

```
radiology-report-app/
├── frontend/           # React frontend application
├── backend/            # FastAPI backend application
└── docker-compose.yml  # Docker orchestration
```

### Frontend Structure

```
frontend/
└── src/
    ├── components/
    │   ├── upload/          # File upload components
    │   ├── templates/       # Template designer
    │   └── results/         # Results viewer
    ├── services/
    │   └── api.ts          # API client
    └── App.tsx             # Main application
```

### Backend Structure

```
backend/
└── app/
    ├── api/              # API endpoints
    │   ├── templates.py  # Template CRUD operations
    │   └── reports.py    # Report processing endpoints
    ├── core/             # Core configuration
    │   ├── config.py     # Settings
    │   └── database.py   # Database setup
    ├── models/           # SQLAlchemy models
    │   └── models.py     # Database models
    ├── schemas/          # Pydantic schemas
    │   └── schemas.py    # Request/response schemas
    ├── services/         # Business logic
    │   └── ai_service.py # AI integration
    ├── tasks/            # Celery tasks
    │   └── report_tasks.py # Async report processing
    └── main.py          # FastAPI application
```

## Installation & Development

All development and deployment is done through Docker. Follow the [Quick Start](#quick-start) guide above to get started.

### Working with Docker Containers

Access the containers for development tasks:

```bash
# Access backend shell for Python development
make shell-backend

# Access database shell
make db-shell

# View logs for debugging
make logs
make logs-backend
make logs-frontend
```

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

## API Reference

### API Testing

Use the interactive API documentation at http://localhost:8000/docs

### Template Endpoints

- `GET /api/templates/` - List all templates
- `GET /api/templates/{id}` - Get template details
- `POST /api/templates/` - Create new template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template

### Report Endpoints

- `POST /api/reports/batches` - Upload batch of reports
- `GET /api/reports/batches` - List all batches
- `GET /api/reports/batches/{id}` - Get batch details
- `GET /api/reports/batches/{id}/reports` - Get reports in batch
- `GET /api/reports/{id}` - Get single report

### Example API Calls

#### Create a batch via API

```bash
curl -X POST "http://localhost:8000/api/reports/batches" \
  -H "Content-Type: multipart/form-data" \
  -F "name=Test Batch" \
  -F "template_id=1" \
  -F "files=@report1.txt" \
  -F "files=@report2.txt"
```

#### Get templates

```bash
curl "http://localhost:8000/api/templates/"
```

### Database Models

#### User
- Basic user authentication (placeholder for future auth)

#### Template
- Pre-built and custom report templates
- JSON structure defining expected fields

#### ReportBatch
- Container for multiple reports
- Tracks processing progress

#### StructuredReport
- Individual radiology report
- Stores original text and extracted structured data

### AI Processing

The application uses the Anthropic Claude API to extract structured information from free-text radiology reports. The AI service:

1. Receives report text and template structure
2. Constructs a prompt asking Claude to extract relevant information
3. Returns structured JSON matching the template

## Common Commands

```bash
make help          # Show all available commands
make logs          # View logs from all services
make logs-backend  # View backend and worker logs only
make logs-frontend # View frontend logs only
make logs-db       # View database logs
make stop          # Stop all services
make restart       # Restart all services
make shell-backend # Open a shell in backend container
make db-shell      # Open PostgreSQL shell
make status        # Check health of all services
make health        # Run health checks on all services
make clean         # Stop and remove containers (keeps data)
make reset         # Full reset including database (deletes all data)
```

## Architecture

### System Architecture

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
       ├──────► PostgreSQL (Data storage)
       │
       └──────► Redis ──► Celery Workers
                            │
                            ▼
                       Claude API
                    (AI processing)
```

### Component Responsibilities

- **React Frontend**: User interface for uploading reports, viewing results, and designing templates
- **FastAPI Backend**: RESTful API, request handling, and business logic
- **PostgreSQL**: Persistent storage for templates, batches, and structured reports
- **Redis**: Message broker for Celery task queue
- **Celery Workers**: Asynchronous processing of reports using Claude API
- **Claude API**: AI-powered extraction of structured data from free text

## Troubleshooting

### Service Health

**Check if all services are running**
```bash
make status    # View status of all containers
make health    # Run health checks on all services
```

### Common Issues

#### Services won't start
```bash
# View logs to see what's wrong
make logs

# Or view specific service logs
make logs-backend
make logs-frontend
```

#### Backend/Celery issues
```bash
# Check backend and worker logs
make logs-backend

# Common issues:
# - Missing ANTHROPIC_API_KEY in .env
# - Invalid API key or no credits
# - Database not ready (wait for health checks)
```

#### Frontend not loading
```bash
# Check frontend logs
make logs-frontend

# Ensure backend is healthy first
make health
```

#### Database connection issues
```bash
# Check database logs
make logs-db

# Access database shell to debug
make db-shell
```

#### "Port already in use" errors
```bash
# Stop any conflicting services
make stop

# Or kill specific ports (example on Unix-based systems):
# lsof -ti:8000 | xargs kill -9  # Backend
# lsof -ti:3000 | xargs kill -9  # Frontend
```

#### Need to reset everything
```bash
# Full reset (deletes all data)
make reset

# Then restart
make start
```

## Development

### Running Tests

Run tests inside the Docker container:
```bash
make shell-backend
# Inside the container:
pytest
```

### Code Quality

Format and lint code inside the Docker container:
```bash
make shell-backend
# Inside the container:
black app/
flake8 app/
```

## Performance & Security

### Performance Tips

- **Batch Size**: Upload 10-50 reports per batch for optimal processing
- **File Format**: .txt files process fastest; PDFs require extraction
- **Concurrent Processing**: Celery processes reports in parallel
- **Template Design**: Simpler templates result in faster processing

### Security Notes

- Never commit .env files with real API keys
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Implement user authentication for production use
- Follow HIPAA guidelines if handling real patient data

## Future Roadmap

Planned enhancements:

1. Add user authentication (JWT)
2. Implement role-based access control
3. Add export functionality (CSV, Excel)
4. Support for PDF/DOCX parsing
5. Enhanced error handling and validation
6. Audit logging for compliance
7. Batch export and reporting features

## License

MIT
