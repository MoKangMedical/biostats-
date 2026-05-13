"""
Export endpoints for downloading analysis results
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import base64
import io

from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.services.export import ExportService

router = APIRouter()


# Request/Response models
class ExportRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Analysis results to export")
    format: str = Field(default="csv", description="Export format: csv, xlsx, json")
    filename: Optional[str] = Field(None, description="Custom filename")


class ExportResponse(BaseModel):
    content: str
    filename: str
    format: str


class ReportRequest(BaseModel):
    analysis_type: str = Field(..., description="Type of analysis")
    parameters: Dict[str, Any] = Field(..., description="Analysis parameters")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    interpretation: str = Field(..., description="Plain-language interpretation")
    charts: Optional[List[str]] = Field(None, description="Base64 encoded chart images")


class ReportResponse(BaseModel):
    content: str
    filename: str
    format: str


# Endpoints
@router.post("/data", response_model=ExportResponse)
async def export_data(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Export analysis results to various formats
    
    Supports CSV, Excel, and JSON formats.
    """
    try:
        if request.format == "csv":
            result = ExportService.to_csv(
                data=request.data,
                filename=request.filename or "analysis_results.csv"
            )
        elif request.format == "xlsx":
            result = ExportService.to_excel(
                data=request.data,
                filename=request.filename or "analysis_results.xlsx"
            )
        elif request.format == "json":
            result = ExportService.to_json(
                data=request.data,
                filename=request.filename or "analysis_results.json"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}. Use csv, xlsx, or json."
            )
        
        return ExportResponse(
            content=result["content"],
            filename=result["filename"],
            format=result["format"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export error: {str(e)}"
        )


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive HTML report
    
    Creates a professional report with analysis results, visualizations, and interpretation.
    """
    try:
        result = ExportService.generate_report(
            analysis_type=request.analysis_type,
            parameters=request.parameters,
            results=request.results,
            interpretation=request.interpretation,
            charts=request.charts
        )
        
        return ReportResponse(
            content=result["content"],
            filename=result["filename"],
            format=result["format"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report generation error: {str(e)}"
        )


@router.post("/download")
async def download_export(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Download exported file directly
    
    Returns a file download response.
    """
    try:
        if request.format == "csv":
            result = ExportService.to_csv(
                data=request.data,
                filename=request.filename or "analysis_results.csv"
            )
            media_type = "text/csv"
        elif request.format == "xlsx":
            result = ExportService.to_excel(
                data=request.data,
                filename=request.filename or "analysis_results.xlsx"
            )
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif request.format == "json":
            result = ExportService.to_json(
                data=request.data,
                filename=request.filename or "analysis_results.json"
            )
            media_type = "application/json"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}"
            )
        
        # Decode base64 content
        content = base64.b64decode(result["content"])
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Download error: {str(e)}"
        )
