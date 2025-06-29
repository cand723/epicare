import unittest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from routers.register.login import login_user
from model.LoginInput import LoginInput
from dotenv import load_dotenv

load_dotenv()


class TestLoginUser(unittest.IsolatedAsyncioTestCase):

    def get_response_json(self, response: JSONResponse):
        return json.loads(response.body.decode())

    # PERBAIKAN DI SINI: Patch get_supabase yang diimpor ke login.py
    @patch("routers.register.login.get_supabase", new_callable=MagicMock)
    @patch("routers.register.login.verify_password")
    # Nama mock juga diubah
    async def test_user_not_found(self, mock_verify_password, mock_get_supabase):
        mock_supabase_client = MagicMock()
        # Set return value of get_supabase()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        login_input = LoginInput(email="test@example.com", password="password")

        response = await login_user(login_input)
        content = self.get_response_json(response)

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(content["success"])

    # PERBAIKAN DI SINI: Patch get_supabase yang diimpor ke login.py
    @patch("routers.register.login.get_supabase", new_callable=MagicMock)
    @patch("routers.register.login.verify_password")
    # Nama mock juga diubah
    async def test_password_mismatch(self, mock_verify_password, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1, "email": "test@example.com",
             "password_hash": "hashed_pw", "verified": True}
        ]
        mock_verify_password.return_value = False
        login_input = LoginInput(
            email="test@example.com", password="wrongpassword")

        response = await login_user(login_input)
        content = self.get_response_json(response)

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(content["success"])

    # PERBAIKAN DI SINI: Patch get_supabase yang diimpor ke login.py
    @patch("routers.register.login.get_supabase", new_callable=MagicMock)
    @patch("routers.register.login.verify_password")
    # Nama mock juga diubah
    async def test_user_not_verified(self, mock_verify_password, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1, "email": "test@example.com",
             "password_hash": "hashed_pw", "verified": False}
        ]
        mock_verify_password.return_value = True
        login_input = LoginInput(email="test@example.com", password="password")

        response = await login_user(login_input)
        content = self.get_response_json(response)

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(content["success"])
        self.assertIn("verify your email", content["message"])

    # PERBAIKAN DI SINI: Patch get_supabase yang diimpor ke login.py
    @patch("routers.register.login.get_supabase", new_callable=MagicMock)
    @patch("routers.register.login.verify_password")
    # Nama mock juga diubah
    async def test_successful_login(self, mock_verify_password, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1, "email": "test@example.com", "password_hash": "hashed_pw",
             "verified": True, "name": "Test User"}
        ]
        mock_verify_password.return_value = True
        login_input = LoginInput(email="test@example.com", password="password")

        # ✅ Fix: mock request dengan session dictionary
        class FakeRequest:
            def __init__(self):
                self.session = {}

        mock_request = FakeRequest()

        response = await login_user(login_input, request=mock_request)
        content = json.loads(response.body.decode())

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(content["success"])
        self.assertEqual(content["user"]["email"], "test@example.com")
        self.assertEqual(
            mock_request.session["user"]["email"], "test@example.com")

    # PERBAIKAN DI SINI: Patch get_supabase yang diimpor ke login.py
    @patch("routers.register.login.get_supabase", new_callable=MagicMock)
    @patch("routers.register.login.verify_password")
    # Nama mock juga diubah
    async def test_exception_handling(self, mock_verify_password, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "DB error")
        login_input = LoginInput(email="test@example.com", password="password")

        response = await login_user(login_input)
        content = self.get_response_json(response)

        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Unexpected error", content["detail"])


if __name__ == "__main__":
    unittest.main()
