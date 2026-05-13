"""
API Router - Main router for all API endpoints
"""

from fastapi import APIRouter

from app.api.endpoints import auth, users, analyses, uploads, statistics, advanced_statistics, visualization, interpretation, export, billing

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(advanced_statistics.router, prefix="/statistics/advanced", tags=["Advanced Statistics"])
api_router.include_router(visualization.router, prefix="/visualization", tags=["Visualization"])
api_router.include_router(interpretation.router, prefix="/interpretation", tags=["AI Interpretation"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
