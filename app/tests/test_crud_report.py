import unittest
from database import SessionLocal, clear_db
from crud.report import (
    get_reports_by_user_id,
    post_report_by_user_id,
    get_report_by_report_id,
    delete_report_by_report_id,
)
from models import Report, EmotionPercentage, Emotion


class TestReportCRUD(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()  # 세션 생성

    def tearDown(self):
        clear_db()  # DB 초기화
        self.db.close()  # 세션 종료

    # get_reports_by_user_id 함수 테스트
    def test_get_reports_by_user_id(self):
        # given
        test_user_id = 1
        test_report = Report(
            user_id=test_user_id,
            title="Test Report",
            category="General",
            situation_summary="Test Situation",
            emotion_summary={"joy": "Happiness"},
            is_deleted=False,
        )
        self.db.add(test_report)
        self.db.commit()

        # when
        reports = get_reports_by_user_id(test_user_id, self.db)

        # then
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["title"], "Test Report")
        self.assertEqual(reports[0]["category"], "General")

    # post_report_by_user_id 함수 테스트
    def test_post_report_by_user_id(self):
        # given
        test_user_id = 1
        chatroom_id = 42

        # Mock 입력 데이터 준비
        category = "General"
        situation_summary = "Test Situation"
        client_message = "User Input"
        emotion_message = "Emotion Response"

        def mock_create_report(client_message, emotion_message):
            return {"joy": 50}, {"joy": "Happiness"}

        # when
        all_emotion_percentage, all_emotion_summary = mock_create_report(client_message, emotion_message)
        response_data = Report(
            user_id=test_user_id,
            title="2025-01-22",  # 테스트 실행 날짜
            situation_summary=situation_summary,
            emotion_summary=all_emotion_summary,
            category=category,
        )
        self.db.add(response_data)
        self.db.commit()
        self.db.refresh(response_data)

        # then
        report = self.db.query(Report).filter(Report.id == response_data.id).first()
        self.assertIsNotNone(report)
        self.assertEqual(report.user_id, test_user_id)
        self.assertEqual(report.title, "2025-01-22")

    # get_report_by_report_id 함수 테스트
    def test_get_report_by_report_id(self):
        # given
        test_report = Report(
            user_id=1,
            title="Test Report",
            category="General",
            situation_summary="Test Situation",
            emotion_summary={"joy": "Happiness"},
            is_deleted=False,
        )
        self.db.add(test_report)
        self.db.commit()

            # Emotion 데이터 추가
        test_emotion = Emotion(
            id=1,  # 기쁨이
            emotion_name="기쁨이",
            wording="You are happy!",
            explanation="Feeling of joy and happiness."
        )
        self.db.add(test_emotion)
        self.db.commit()

        test_emotion_percentage = EmotionPercentage(
            report_id=test_report.id,
            emotion_id=1,  # 기쁨이
            percentages=50.0,
            is_deleted=False,
        )
        self.db.add(test_emotion_percentage)
        self.db.commit()

        # when
        report_data = get_report_by_report_id(test_report.id, self.db)

        # then
        self.assertEqual(report_data["title"], "Test Report")
        self.assertEqual(report_data["emotion_summary"], {"joy": "Happiness"})
        self.assertEqual(report_data["emotion_percentage"]["1"], 50.0)

    # delete_report_by_report_id 함수 테스트
    def test_delete_report_by_report_id(self):
        # given
        test_report = Report(
            user_id=1,
            title="Report to Delete",
            category="General",
            situation_summary="To be deleted.",
            emotion_summary={"sadness": "Feeling down"},
            is_deleted=False,
        )
        self.db.add(test_report)
        self.db.commit()

        test_emotion_percentage = EmotionPercentage(
            report_id=test_report.id,
            emotion_id=2,
            percentages=40.0,
            is_deleted=False,
        )
        self.db.add(test_emotion_percentage)
        self.db.commit()

        # when
        result = delete_report_by_report_id(test_report.id, self.db)

        # then
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Report deleted successfully")

        # Verify deletion
        deleted_report = self.db.query(Report).filter(Report.id == test_report.id).first()
        self.assertTrue(deleted_report.is_deleted)

        deleted_emotions = self.db.query(EmotionPercentage).filter(EmotionPercentage.report_id == test_report.id).all()
        self.assertTrue(all(e.is_deleted for e in deleted_emotions))


if __name__ == "__main__":
    unittest.main()
