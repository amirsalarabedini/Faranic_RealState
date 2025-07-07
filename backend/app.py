from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import json
import sys
import os
from datetime import datetime
import uuid
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the main orchestrator function
from main import main as run_main_script

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="Faranic Real Estate API",
    description="A comprehensive real estate analysis API powered by multi-agent AI system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ReportRequest(BaseModel):
    query: str = Field(..., description="The user's query for real estate analysis")
    report_date: Optional[str] = Field(None, description="Optional date for the report (e.g., 'March 21, 2024')")
    language: Optional[str] = Field("English", description="Language for the report (English/Persian)")

class ReportResponse(BaseModel):
    status: str
    report_id: str
    report: str
    timestamp: str

class ErrorResponse(BaseModel):
    status: str
    error: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# In-memory storage for demo purposes (use a proper database in production)
report_storage = {}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/generate_report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate a complete real estate analysis report"""
    try:
        report_id = str(uuid.uuid4())
        logger.info(f"Generating report {report_id} for query: {request.query}")
        
        # Run the async generator and collect all chunks
        full_report_chunks = []
        async for chunk in run_main_script(request.query, request.report_date):
            full_report_chunks.append(chunk)
        
        final_report = "".join(full_report_chunks)
        
        # Store the report
        report_data = {
            "report_id": report_id,
            "query": request.query,
            "report": final_report,
            "timestamp": datetime.now().isoformat(),
            "language": request.language
        }
        report_storage[report_id] = report_data
        
        logger.info(f"Report {report_id} generated successfully")
        
        return ReportResponse(
            status="success",
            report_id=report_id,
            report=final_report,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status="error",
                error="report_generation_failed",
                message=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )

@app.post("/generate_report_stream")
async def generate_report_stream(request: ReportRequest):
    """Generate a real estate analysis report with streaming response"""
    try:
        async def generate_stream():
            report_id = str(uuid.uuid4())
            logger.info(f"Streaming report {report_id} for query: {request.query}")
            
            # Send initial metadata
            initial_data = {
                "type": "metadata",
                "report_id": report_id,
                "timestamp": datetime.now().isoformat(),
                "query": request.query
            }
            yield f"data: {json.dumps(initial_data)}\n\n"
            
            # Stream the report chunks
            full_report_chunks = []
            async for chunk in run_main_script(request.query, request.report_date):
                full_report_chunks.append(chunk)
                chunk_data = {
                    "type": "chunk",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # Send completion signal
            final_report = "".join(full_report_chunks)
            report_data = {
                "report_id": report_id,
                "query": request.query,
                "report": final_report,
                "timestamp": datetime.now().isoformat(),
                "language": request.language
            }
            report_storage[report_id] = report_data
            
            completion_data = {
                "type": "complete",
                "report_id": report_id,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            logger.info(f"Streaming report {report_id} completed")

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

    except Exception as e:
        logger.error(f"Error streaming report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status="error",
                error="streaming_failed",
                message=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )

@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Retrieve a previously generated report"""
    if report_id not in report_storage:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                status="error",
                error="report_not_found",
                message=f"Report with ID {report_id} not found",
                timestamp=datetime.now().isoformat()
            ).dict()
        )
    
    return report_storage[report_id]

@app.get("/reports")
async def list_reports():
    """List all generated reports"""
    reports = []
    for report_id, report_data in report_storage.items():
        reports.append({
            "report_id": report_id,
            "query": report_data["query"],
            "timestamp": report_data["timestamp"],
            "language": report_data.get("language", "English")
        })
    
    return {
        "status": "success",
        "reports": reports,
        "total_count": len(reports)
    }

@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a specific report"""
    if report_id not in report_storage:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                status="error",
                error="report_not_found",
                message=f"Report with ID {report_id} not found",
                timestamp=datetime.now().isoformat()
            ).dict()
        )
    
    del report_storage[report_id]
    return {
        "status": "success",
        "message": f"Report {report_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Faranic Real Estate API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "/health",
            "generate_report": "/generate_report",
            "generate_report_stream": "/generate_report_stream",
            "get_report": "/reports/{report_id}",
            "list_reports": "/reports",
            "delete_report": "/reports/{report_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 