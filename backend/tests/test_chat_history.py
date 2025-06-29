from routers.chat_history import router
import unittest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4
import sys
import os

# Tambahkan path backend ke sys agar bisa impor modul dari root
# Asumsi test_chat_history.py ada di 'epicare-fullstack/backend/tests/'
# Dan routers ada di 'epicare-fullstack/backend/routers/'
# Kita ingin menambahkan 'epicare-fullstack/backend/' ke sys.path
sys.path.insert(0, os.path.abspath(
    # Ini harusnya sudah benar
    os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))


# Mock FastAPI app dengan chat_history router
app = FastAPI()
app.include_router(router)
client = TestClient(app)

user_id = str(uuid4())
chat_id = str(uuid4())


class TestChatHistoryAPI(unittest.TestCase):

    # Patch get_supabase() secara langsung di mana ia diimpor ke chat_history.py
    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_create_chat(self, mock_get_supabase):
        # Konfigurasi mock untuk rantai panggilan
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.status_code = 201
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.data = [{
            "id": chat_id,
            "user_id": user_id,
            "title": "New Chat",
            "created_at": "2025-05-26T00:00:00"
        }]

        response = client.post("/chat_history/chats",
                               json={"user_id": user_id, "title": "New Chat"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "New Chat")
        mock_get_supabase.assert_called_once()  # Memastikan get_supabase dipanggil

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_create_chat_failure(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.status_code = 500
        # Simulasi kegagalan
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.data = None
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.count = None
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.error = {
            'message': 'DB error'}

        response = client.post("/chat_history/chats",
                               json={"user_id": user_id, "title": "Failed Chat"})

        # Memastikan status code error dari API
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to create chat", response.json()["detail"])

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_get_chats(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.status_code = 200
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [{
            "id": chat_id,
            "user_id": user_id,
            "title": "Chat 1",
            "created_at": "2025-05-25T12:00:00"
        }]
        response = client.get(f"/chat_history/chats/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_get_chats_no_data(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.status_code = 200
        # Simulasi tidak ada data
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

        response = client.get(f"/chat_history/chats/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_create_message(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.status_code = 201
        mock_supabase_client.from_.return_value.insert.return_value.execute.return_value.data = [{
            "id": str(uuid4()),
            "chat_id": chat_id,
            "sender": "user",
            "content": "Hello",
            "created_at": "2025-05-26T01:00:00"
        }]
        response = client.post("/chat_history/messages", json={
            "chat_id": chat_id,
            "sender": "user",
            "content": "Hello"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Hello")

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_get_messages(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.status_code = 200
        mock_supabase_client.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [{
            "id": str(uuid4()),
            "chat_id": chat_id,
            "sender": "bot",
            "content": "Hi!",
            "created_at": "2025-05-26T01:05:00"
        }]
        response = client.get(f"/chat_history/messages/{chat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_update_chat_title(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.update.return_value.eq.return_value.execute.return_value.status_code = 200
        mock_supabase_client.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
            "id": chat_id,
            "user_id": user_id,
            "title": "Updated Title",
            "created_at": "2025-05-26T01:00:00"
        }]
        response = client.patch(
            f"/chat_history/chats/{chat_id}", json={"title": "Updated Title"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Title")

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_update_chat_title_not_found(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        mock_supabase_client.from_.return_value.update.return_value.eq.return_value.execute.return_value.status_code = 200
        # Simulasi tidak ditemukan
        mock_supabase_client.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = []

        response = client.patch(
            f"/chat_history/chats/{chat_id}", json={"title": "Updated Title"})
        # API harusnya mengembalikan 404 jika tidak ditemukan
        self.assertEqual(response.status_code, 404)
        self.assertIn("Chat not found", response.json()["detail"])

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_delete_chat(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        # Mock respons untuk delete messages
        mock_supabase_client.from_.return_value.delete.return_value.eq.return_value.execute.side_effect = [
            # Pesan berhasil dihapus
            MagicMock(status_code=200, data=[{"id": "message1"}]),
            # Chat berhasil dihapus
            MagicMock(status_code=200, data=[{"id": chat_id}])
        ]

        response = client.delete(f"/chat_history/chats/{chat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Chat deleted successfully", response.json()["message"])

    @patch("routers.chat_history.get_supabase")  # <--- PERBAIKAN DI SINI
    def test_delete_chat_not_found(self, mock_get_supabase):
        mock_supabase_client = MagicMock()
        mock_get_supabase.return_value = mock_supabase_client
        # Mock respons untuk delete messages dan kemudian chat (chat tidak ditemukan)
        mock_supabase_client.from_.return_value.delete.return_value.eq.return_value.execute.side_effect = [
            # Pesan berhasil dihapus
            MagicMock(status_code=200, data=[{"id": "message1"}]),
            MagicMock(status_code=200, data=[])  # Chat tidak ditemukan
        ]

        response = client.delete(f"/chat_history/chats/{chat_id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Chat not found or failed to delete",
                      response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
