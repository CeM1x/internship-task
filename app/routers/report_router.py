from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.report.weekly import WeeklyReport
from app.services.report_analysis_service import ReportAnalysisService
from app.workers.reports import generate_52_weeks_reports

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/run", status_code=202)
def run_reports() -> dict:
    generate_52_weeks_reports.send()
    return {"status": "queued"}


@router.get("/analysis", response_model=list[WeeklyReport], status_code=status.HTTP_200_OK)
async def get_transaction_analysis(session: AsyncSession = Depends(get_async_session)):
    service = ReportAnalysisService(session)
    return await service.build_52_weeks_analysis()
