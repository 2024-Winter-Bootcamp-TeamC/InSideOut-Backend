from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import report as ReportServices
from schemas.report import ReportsResponse, CreateResponse, ReportResponse
from database import get_db

router = APIRouter()

@router.get("/{user_id}", description="보고서 목록 조회", response_model=ReportsResponse)
def 보고서_목록_조회(user_id: int, db: Session = Depends(get_db)):
    try:
        reports = ReportServices.get_reports_by_user_id(user_id, db)
        return ReportsResponse(status="success", message="Data fetch successfuly", data=reports)
    except HTTPException as e:
        raise e


@router.post("/{user_id}", description="보고서 생성", response_model=CreateResponse)
def 보고서_생성(user_id: int, db: Session = Depends(get_db)):
    try:
        response = ReportServices.post_report_by_user_id(user_id, db)
        return CreateResponse(status="success", message="Data posted successfully", report_id=response)
    except HTTPException as e:
        raise e


@router.get("/view/{report_id}", description="보고서 조회", response_model=ReportResponse)
def 보고서_조회(report_id: int, db: Session = Depends(get_db)):
    try:
        # get_report_by_report_id에서 반환된 데이터를 받아옵니다
        response = ReportServices.get_report_by_report_id(report_id, db)
        
        # ReportResponse 모델에 맞게 데이터 반환
        return ReportResponse(
            status="success", 
            message="successfully",
            title=response["title"], 
            situation_summary=response["situation_summary"],
            emotion_summary=response["emotion_summary"],
            wording=response["wording"],
            emotion_percentage=response["emotion_percentage"]  # data 필드는 Dictionary 형태로 설정
        )
    except HTTPException as e:
        raise e

