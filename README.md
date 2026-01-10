# Healthcare Report

A production-ready healthcare report application that enables nurses to search client records and generate professional PDF reports. Built with React + FastAPI on Databricks.

## Overview

This application serves healthcare professionals who need to search for client assessment records, review AI-generated risk assessments, and generate comprehensive PDF reports for clinical documentation.

### Key Features

- Client search with name, NHI, and date range filters
- Interactive data table with single-row selection
- AI-enhanced risk assessment display (housing, disability, mental health)
- Professional PDF report generation matching clinical standards
- In-browser report preview before download
- Secure authentication via Databricks proxy headers

## Architecture

### Tech Stack

**Backend:**
- FastAPI for REST API endpoints
- Databricks SQL Warehouse for data access
- ReportLab for PDF generation
- Pydantic for data validation

**Frontend:**
- React 18 with TypeScript
- Mantine UI component library
- Axios for HTTP requests
- Lucide React for icons

### Project Structure

```
react-chatbot/
├── main.py                    # FastAPI application entry point
├── app.yaml                   # Databricks deployment configuration
├── requirements.txt           # Python dependencies
├── services/
│   ├── __init__.py
│   ├── databricks_service.py  # Databricks SQL Warehouse queries
│   └── pdf_service.py         # PDF report generation
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main application component
│   │   ├── api/chatApi.ts     # API client functions
│   │   ├── context/
│   │   │   └── AppContext.tsx # Application state management
│   │   ├── components/
│   │   │   ├── Header.tsx     # Application header with user menu
│   │   │   ├── UserMenu.tsx   # User profile and logout
│   │   │   ├── SearchPanel.tsx # Search filters and controls
│   │   │   ├── DataTable.tsx  # Results table with selection
│   │   │   └── ReportPreview.tsx # Report preview and download
│   │   └── types/index.ts     # TypeScript interfaces
│   └── build/                 # Compiled frontend assets
└── assets/
    └── logo.png               # Logo for PDF reports
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Access to Databricks workspace with SQL Warehouse

### Environment Variables

```bash
DATABRICKS_HOST=adb-1108746899088703.3.azuredatabricks.net
DATABRICKS_WAREHOUSE_ID=6880e1544b69181f
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/archerzou/react-chatbot.git
cd react-chatbot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build the frontend:
```bash
cd frontend
npm install
npm run build
cd ..
```

4. Run the application:
```bash
python main.py
```

The application will be available at http://localhost:8000

## Development Workflow

### Running Locally

1. Start the backend server:
```bash
python main.py
```

2. For frontend development with hot reloading:
```bash
cd frontend
npm start
```

### Building for Production

```bash
cd frontend
npm run build
```

## API Documentation

### Endpoints

#### GET /api/login
Returns current user information from proxy headers.

**Response:**
```json
{
  "user_info": {
    "email": "user@example.com",
    "user_id": "user123",
    "username": "user"
  }
}
```

#### POST /api/search
Search for clients based on filters.

**Request:**
```json
{
  "client_name": "John",
  "client_nhi": null,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "results": [
    {
      "koo_clientid": "abc123",
      "client_name": "John Smith",
      "client_nhi": "ABC1234",
      "create_date": "2024-06-15",
      "response_house": "Yes",
      "response_impa": "No",
      "response_mmh": "Yes"
    }
  ],
  "total": 1
}
```

#### GET /api/report/{client_id}
Get detailed report data for a specific client.

**Response:**
```json
{
  "koo_clientid": "abc123",
  "client_name": "John Smith",
  "client_nhi": "ABC1234",
  "dhb": "Auckland",
  "housing_concerns": 1,
  "housing_risk_categories": "Overcrowding",
  "house_summary": "AI-generated housing summary...",
  "impa_summary": "AI-generated impairment summary...",
  "mmh_summary": "AI-generated mental health summary..."
}
```

#### GET /api/report/{client_id}/pdf
Download PDF report for a specific client.

**Response:** PDF file (application/pdf)

## Deployment

### Databricks Deployment

The application is configured for deployment on Databricks Apps via `app.yaml`:

```yaml
command:
  - "gunicorn"
  - "main:app"
  - "-w"
  - "2"
  - "--worker-class"
  - "uvicorn.workers.UvicornWorker"

env:
  - name: "DATABRICKS_HOST"
    value: "adb-1108746899088703.3.azuredatabricks.net"
  - name: "DATABRICKS_WAREHOUSE_ID"
    value: "6880e1544b69181f"
```

## Data Sources

The application queries two Databricks tables:

- **Search Table:** `dev_structured.analytics.measureresponses_cleaned` - Lightweight table for client search
- **Report Table:** `dev_structured.analytics.measureresponses_ai_final` - Comprehensive table with AI summaries

## Troubleshooting

### Common Issues

**Build fails with TypeScript errors:**
- Ensure all dependencies are installed: `npm install`
- Check for type mismatches in component props

**Cannot connect to Databricks:**
- Verify DATABRICKS_HOST and DATABRICKS_WAREHOUSE_ID environment variables
- Ensure service principal credentials are configured

**PDF generation fails:**
- Check that ReportLab is installed: `pip install reportlab`
- Verify logo.png exists in assets directory

**Search returns no results:**
- Verify at least one search parameter is provided
- Check date format (YYYY-MM-DD)

## License

This project is proprietary software for healthcare use.
