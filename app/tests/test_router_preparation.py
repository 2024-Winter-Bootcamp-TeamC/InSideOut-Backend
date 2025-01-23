import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import asyncio
from routers.preparation import upload_data

class TestPreparationRouter(unittest.TestCase):

    def test_upload_data_success(self):
        test_user_id = 1
        test_category = "test_category"
        test_content = "test_content"
        test_files = ["test_files_context"]

        mock_response = {"message": "success"}

        with patch("crud.preparation.file", return_value=mock_response) as mock_file:
            mock_db = MagicMock(spec=Session)

            result = asyncio.run(upload_data(
                user_id = test_user_id,
                category = test_category,
                files = test_files,
                content = test_content,
                db = mock_db,
            ))

        assert result == mock_response

        mock_file.assert_called_once_with(
            mock_db,
            test_user_id,
            test_category,
            test_files,
            test_content,
        )

    