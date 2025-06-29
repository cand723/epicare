from routers.register.register import register_user
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.responses import JSONResponse
from fastapi import status
import sys
import os
from datetime import datetime
from fastapi import HTTPException
import json  # <--- PASTIKAN INI ADA DAN TIDAK DIKOMENTARI
# import unittest # Duplikasi, sudah diimpor di atas
from fastapi.requests import Request

# Tambahkan path backend ke sys agar bisa impor modul dari root
# Asumsi test_register.py ada di 'epicare-fullstack/backend/tests/'
# Dan routers ada di 'epicare-fullstack/backend/routers/'
# Kita ingin menambahkan 'epicare-fullstack/backend/' ke sys.path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'backend')))


class FakeRequest:
    def __init__(self, json_data):
        self._json_data = json_data

    async def json(self):
        return self._json_data


class TestRegisterUser(unittest.IsolatedAsyncioTestCase):

    # Helper method to parse JSONResponse content
    def get_response_json(self, response: JSONResponse):
        # json diimpor di bagian atas file, jadi seharusnya bisa diakses di sini
        return json.loads(response.body.decode())

    # Patch get_supabase() secara langsung di mana ia diimpor ke register.py
    # Juga patch send_verification_email dan hash_password
    @patch("routers.register.register.get_supabase")
    @patch("routers.register.register.send_verification_email")
    @patch("routers.register.register.hash_password", return_value="hashed_password")
    async def test_successful_register(self, mock_hash, mock_send_email, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client

        # Mock respons untuk select (email belum ada)
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Mock respons untuk insert (berhasil)
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "user-123", "email": "testuser@example.com", "name": "Test User", "gender": "male", "date": "2024-05-01",
                "password_hash": "hashed_password", "verified": False, "verification_token": "some-token"}
        ]
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.status_code = 201

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword",
            "gender": "male",
            "date": "2024-05-01"
        })

        response = await register_user(request)
        # Respons sekarang adalah dict, bukan JSONResponse
        self.assertIsInstance(response, dict)
        self.assertIn("message", response)
        self.assertIn("User registered successfully", response["message"])
        mock_send_email.assert_called_once()  # Pastikan email verifikasi dikirim

    @patch("routers.register.register.get_supabase")
    @patch("routers.register.register.send_verification_email")
    @patch("routers.register.register.hash_password", return_value="hashed_password")
    async def test_email_already_registered(self, mock_hash, mock_send_email, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client

        # Mock respons untuk select (email sudah ada)
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "exists", "email": "testuser@example.com"}
        ]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.status_code = 200

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword",
            "gender": "male",
            "date": "2024-05-01"
        })

        with self.assertRaises(HTTPException) as context:
            await register_user(request)
        # Gunakan status.HTTP_400_BAD_REQUEST
        self.assertEqual(context.exception.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Email already registered.")
        # Pastikan email tidak dikirim jika pendaftaran gagal
        mock_send_email.assert_not_called()

    async def test_invalid_payload(self):
        request = MagicMock()
        request.json = AsyncMock(return_value={
            "email": "invalid"
            # Payload tidak lengkap, akan memicu ValidationError
        })

        response = await register_user(request)
        # Respons error validasi adalah JSONResponse
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code,
                         status.HTTP_422_UNPROCESSABLE_ENTITY)

        # PERBAIKAN DI SINI: Parse body JSONResponse
        content = self.get_response_json(response)
        self.assertIn("detail", content)
        # Pydantic ValidationError returns list of errors
        self.assertIsInstance(content["detail"], list)
        # Anda bisa menambahkan assertion yang lebih spesifik tentang isi detail errors Pydantic jika perlu

    @patch("routers.register.register.get_supabase")
    @patch("routers.register.register.send_verification_email")
    @patch("routers.register.register.hash_password", return_value="hashed_password")
    async def test_register_send_email_failure(self, mock_hash, mock_send_email, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "user-123", "email": "testuser@example.com", "name": "Test User", "gender": "male", "date": "2024-05-01",
                "password_hash": "hashed_password", "verified": False, "verification_token": "some-token"}
        ]
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.status_code = 201

        mock_send_email.side_effect = Exception(
            "Email sending failed")  # Simulasikan kegagalan kirim email

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword",
            "gender": "male",
            "date": "2024-05-01"
        })

        # PERBAIKAN DI SINI: Tangkap HTTPException yang diharapkan
        with self.assertRaises(HTTPException) as context:
            await register_user(request)
        self.assertEqual(context.exception.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to send verification email",
                      context.exception.detail)
        mock_send_email.assert_called_once()  # Pastikan email sending dicoba

    @patch("routers.register.register.get_supabase")
    @patch("routers.register.register.send_verification_email")
    @patch("routers.register.register.hash_password", return_value="hashed_password")
    async def test_register_db_insert_failure(self, mock_hash, mock_send_email, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        # Simulasikan kegagalan insert
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = []
        # Atau status lain yang menunjukkan kegagalan
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.status_code = 500

        request = MagicMock()
        request.json = AsyncMock(return_value={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword",
            "gender": "male",
            "date": "2024-05-01"
        })

        with self.assertRaises(HTTPException) as context:
            await register_user(request)
        self.assertEqual(context.exception.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Gagal mendaftarkan user", context.exception.detail)
        # Email tidak boleh dikirim jika pendaftaran DB gagal
        mock_send_email.assert_not_called()


if __name__ == '__main__':
    unittest.main()
