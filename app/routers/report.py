from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import report as ReportServices
from schemas.report import ReportsResponse, CreateResponse, ReportResponse,ResponseStatus
from database import get_db

router = APIRouter()

@router.get("/{user_id}", description="보고서 목록 조회", response_model=ReportsResponse)
def view_report_list(user_id: int, db: Session = Depends(get_db)):
    try:
        reports = ReportServices.get_reports_by_user_id(user_id, db)
        return ReportsResponse(status="success", message="Data fetch successfuly", data=reports)
    except HTTPException as e:
        raise e


@router.post("/{user_id}", description="보고서 생성", response_model=CreateResponse)
def create_report(user_id: int,db: Session = Depends(get_db)):
    try:
        response = ReportServices.post_report_by_user_id(user_id, db)
        return CreateResponse(status="success", message="Data posted successfully", report_id=response)
    except HTTPException as e:
        raise e


@router.get("/view/{report_id}", description="보고서 조회", response_model=ReportResponse)
def view_report(report_id: int, db: Session = Depends(get_db)):
    try:
        response = ReportServices.get_report_by_report_id(report_id, db)

        return ReportResponse(
            status="success", 
            message="successfully",
            title=response["title"], 
            situation_summary=response["situation_summary"],
            emotion_summary=response["emotion_summary"],
            wording=response["wording"],
            emotion_percentage=response["emotion_percentage"]  
        )
    except HTTPException as e:
        raise e

@router.delete("/{report_id}", description="보고서 삭제", response_model=ResponseStatus)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    try:
        response = ReportServices.delete_report_by_report_id(report_id, db)
        return ResponseStatus(status=response["status"], message=response["message"])
    except HTTPException as e:
        raise e
