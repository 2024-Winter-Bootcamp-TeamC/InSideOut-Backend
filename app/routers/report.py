from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import report as ReportServices
from schemas.report import ReportsResponse
from database import get_db

router = APIRouter()

@router.post("/{user_id}", description="보고서 목록 조회", response_model=ReportsResponse)
def 보고서_목록_조회(user_id: int, db: Session = Depends(get_db)):
    try:
        reports = ReportServices.get_reports_by_user_id(user_id, db)
        return ReportsResponse(status="success", message="Data posted successfully", data=reports)
    except HTTPException as e:
        raise e
