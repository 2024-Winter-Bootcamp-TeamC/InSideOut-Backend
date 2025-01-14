from models import Report
from schemas.report import ReportsResponse, ResponseError
from sqlalchemy.orm import Session
from fastapi import HTTPException

def get_reports_by_user_id(user_id: int, db: Session):
    reports = db.query(Report).filter(Report.user_id == user_id, Report.is_deleted == False).all()
    
    if not reports:
        raise HTTPException(status_code=404, detail="No data was found.")
    
    report_list = []
    for report in reports:
        report_list.append({
            "report_id": report.id,
            "category": report.category,
            "title": report.title
        })

    return report_list
