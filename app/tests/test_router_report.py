import unittest
from unittest.mock import patch, MagicMock
from routers.report import view_report_list, create_report, view_report, delete_report
from schemas.report import ReportsResponse, CreateResponse, ReportResponse, ResponseStatus
from sqlalchemy.orm import Session

class TestReportRouter(unittest.TestCase):
    @patch("crud.report.get_reports_by_user_id")
    def test_view_report_list(self, mock_get_reports):
        mock_reports = [
            {"report_id": 1, "title": "Test Report 1", "category": "General", "user_id": 1, "situation_summary": "Summary 1", "emotion_summary": {}, "wording": {}, "emotion_percentage": {}},
            {"report_id": 2, "title": "Test Report 2", "category": "General", "user_id": 1, "situation_summary": "Summary 2", "emotion_summary": {}, "wording": {}, "emotion_percentage": {}},
        ]
        mock_get_reports.return_value = mock_reports
        mock_db = MagicMock(spec=Session)

        response = view_report_list(1, db=mock_db)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "Data fetch successfuly")
        self.assertEqual(len(response.data), 2)

    @patch("crud.report.post_report_by_user_id")
    async def test_create_report(self, mock_post_report):
        mock_post_report.return_value = 3
        mock_db = MagicMock(spec=Session)
        
        # 매개변수 추가
        user_id = 1
        chatroom_id = 42  # 테스트용 chatroom_id 값

        # chatroom_id 포함하여 함수 호출
        response = await create_report(user_id, chatroom_id, db=mock_db)
        
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "Data posted successfully")
        self.assertEqual(response.report_id, 3)

    @patch("crud.report.get_report_by_report_id")
    def test_view_report(self, mock_get_report):
        mock_report = {
            "report_id": 1,
            "title": "Test Report",
            "situation_summary": "Test Summary",
            "emotion_summary": {},
            "wording": {},
            "emotion_percentage": {},
            "category": "General",
        }
        mock_get_report.return_value = mock_report
        mock_db = MagicMock(spec=Session)

        response = view_report(1, db=mock_db)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "successfully")
        self.assertEqual(response.title, "Test Report")

    @patch("crud.report.delete_report_by_report_id")
    def test_delete_report(self, mock_delete_report):
        mock_delete_report.return_value = {"status": "success", "message": "Deleted successfully"}
        mock_db = MagicMock(spec=Session)
        response = delete_report(1, db=mock_db)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "Deleted successfully")

if __name__ == "__main__":
    unittest.main()
