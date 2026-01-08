from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

from services.databricks_service import DatabricksService
from services.pdf_service import PDFService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(override=True)

# Pydantic models
class SearchRequest(BaseModel):
    client_name: Optional[str] = None
    client_nhi: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ClientSearchResult(BaseModel):
    koo_clientid: str
    koo_contactid: Optional[str] = None
    client_name: str
    client_nhi: Optional[str] = None
    create_date: Optional[date] = None
    response_house: Optional[str] = None
    response_impa: Optional[str] = None
    response_mmh: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[ClientSearchResult]
    total: int

class ReportData(BaseModel):
    koo_clientid: str
    client_name: Optional[str] = None
    client_nhi: Optional[str] = None
    dhb: Optional[str] = None
    domicile: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    primary_caregiver: Optional[str] = None
    well_child_level_of_need: Optional[str] = None
    housing_concerns: Optional[int] = None
    housing_risk_categories: Optional[str] = None
    is_disability_discussed: Optional[int] = None
    disability_categories: Optional[str] = None
    family_member_disability: Optional[str] = None
    mmh_concerns: Optional[int] = None
    mental_health_categories: Optional[str] = None
    family_mental_concerns: Optional[int] = None
    family_mental_health_categories: Optional[str] = None
    family_member_impact: Optional[str] = None
    house_summary: Optional[str] = None
    impa_summary: Optional[str] = None
    mmh_summary: Optional[str] = None

class UserInfo(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    access_token: Optional[str] = None

# Initialize services
databricks_service = DatabricksService()
pdf_service = PDFService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Healthcare Dashboard API")
    yield
    logger.info("Shutting down Healthcare Dashboard API")

app = FastAPI(lifespan=lifespan)
api_app = FastAPI()

# Mount API
app.mount("/api", api_app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get user info from headers
async def get_user_info(request: Request) -> UserInfo:
    """Get user information from request headers (set by Databricks proxy)"""
    email = request.headers.get("X-Forwarded-Email")
    user_id = request.headers.get("X-Forwarded-User")
    username = request.headers.get("X-Forwarded-Preferred-Username", "")
    # Get user's access token for Databricks API calls (user authorization)
    access_token = request.headers.get("X-Forwarded-Access-Token")
    
    if username:
        username = username.split("@")[0]
    
    # For local development, use test user if no headers present
    if not user_id:
        return UserInfo(
            email="test@example.com",
            user_id="test_user",
            username="test_user",
            access_token=access_token
        )
    
    return UserInfo(
        email=email,
        user_id=user_id,
        username=username,
        access_token=access_token
    )

# API Routes
@api_app.get("/")
async def root():
    return {"message": "Healthcare Dashboard API is running"}

@api_app.get("/login")
async def login(user_info: UserInfo = Depends(get_user_info)):
    """Return user info for authentication"""
    return {"user_info": user_info.model_dump()}

@api_app.get("/logout")
async def logout():
    """Redirect to Databricks logout"""
    databricks_host = os.getenv("DATABRICKS_HOST", "")
    if databricks_host:
        return RedirectResponse(url=f"https://{databricks_host}/login.html", status_code=303)
    return {"message": "Logged out"}

@api_app.post("/search", response_model=SearchResponse)
async def search_clients(
    request: SearchRequest,
    user_info: UserInfo = Depends(get_user_info)
):
    """Search for clients based on filters"""
    try:
        logger.info(f"Search request from user {user_info.user_id}: {request}")
        
        # Validate at least one search parameter
        if not request.client_name and not request.client_nhi and not request.start_date and not request.end_date:
            raise HTTPException(
                status_code=400,
                detail="At least one search parameter is required (client_name, client_nhi, or date range)"
            )
        
        # Check if user has access token (required for Databricks queries)
        if not user_info.access_token:
            raise HTTPException(
                status_code=401,
                detail="User access token not available. Please ensure you are logged in."
            )
        
        results = databricks_service.search_clients(
            user_token=user_info.access_token,
            client_name=request.client_name,
            client_nhi=request.client_nhi,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return SearchResponse(results=results, total=len(results))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching clients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching clients: {str(e)}")

@api_app.get("/report/{client_id}", response_model=ReportData)
async def get_report_data(
    client_id: str,
    user_info: UserInfo = Depends(get_user_info)
):
    """Get report data for a specific client"""
    try:
        logger.info(f"Report data request from user {user_info.user_id} for client {client_id}")
        
        # Check if user has access token (required for Databricks queries)
        if not user_info.access_token:
            raise HTTPException(
                status_code=401,
                detail="User access token not available. Please ensure you are logged in."
            )
        
        report_data = databricks_service.get_report_data(client_id, user_info.access_token)
        
        if not report_data:
            raise HTTPException(status_code=404, detail=f"Report data not found for client {client_id}")
        
        return report_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting report data: {str(e)}")

@api_app.get("/report/{client_id}/pdf")
async def generate_pdf(
    client_id: str,
    user_info: UserInfo = Depends(get_user_info)
):
    """Generate and return PDF report for a client"""
    try:
        logger.info(f"PDF generation request from user {user_info.user_id} for client {client_id}")
        
        # Check if user has access token (required for Databricks queries)
        if not user_info.access_token:
            raise HTTPException(
                status_code=401,
                detail="User access token not available. Please ensure you are logged in."
            )
        
        # Get report data
        report_data = databricks_service.get_report_data(client_id, user_info.access_token)
        
        if not report_data:
            raise HTTPException(status_code=404, detail=f"Report data not found for client {client_id}")
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_pdf(report_data)
        
        # Create filename
        client_name = report_data.get("client_name", "unknown").replace(" ", "_")
        filename = f"client_report_{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Mount static files for frontend (must be last)
try:
    ui_app = StaticFiles(directory="frontend/build", html=True)
    app.mount("/", ui_app)
except Exception as e:
    logger.warning(f"Could not mount frontend static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
