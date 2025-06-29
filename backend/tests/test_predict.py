import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import os

from routers.analisis_gejala_api import router, hitung_kategori_bmi, predict, InputData


class TestPredictAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):  # Tidak perlu menerima argumen mock di sini lagi
        cls.app = FastAPI()
        cls.app.include_router(router)
        cls.client = TestClient(cls.app)

    @classmethod
    def tearDownClass(cls):
        pass  # Tidak perlu cleanup khusus untuk TestClient

    def setUp(self):
        # setUp tidak perlu melakukan apa-apa lagi karena patch di level metode
        pass

    def tearDown(self):
        # tearDown tidak perlu melakukan apa-apa lagi
        pass

    # Setiap metode tes yang menggunakan 'model' akan di-patch secara individual
    # Patch model hanya untuk metode ini
    @patch('routers.analisis_gejala_api.model')
    # Menerima mock_model sebagai argumen
    def test_valid_input_prediction(self, mock_model):
        mock_model.predict.return_value = np.array([[0.85]])
        input_data = [1] * 15 + [60.0, 170.0]

        response = self.client.post("/predict/", json=input_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prediction"], "85.00%")
        mock_model.predict.assert_called_once()

    # Metode ini tidak menggunakan 'model', jadi tidak perlu argumen mock_model
    def test_invalid_input_length(self):
        input_data = [1] * 10
        response = self.client.post("/predict/", json=input_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.json())
        self.assertEqual(
            response.json()["error"], "Input harus 17 elemen: 15 fitur + berat + tinggi")

    # Patch model menjadi None dan os.path.exists ke False hanya untuk metode ini
    @patch("routers.analisis_gejala_api.model", new=None)
    @patch("os.path.exists", return_value=False)
    # Menerima mock_exists, tidak perlu mock_model
    def test_model_not_loaded(self, mock_exists):
        response = self.client.post("/predict/", json=[1] * 15 + [60.0, 170.0])
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn("Model AI tidak tersedia di server",
                      response.json()["detail"])

    # Patch model hanya untuk metode ini
    @patch('routers.analisis_gejala_api.model')
    # Menerima mock_model sebagai argumen
    def test_model_predict_exception(self, mock_model):
        mock_model.predict.side_effect = Exception(
            "Prediction calculation error")
        input_data = [1] * 15 + [60.0, 170.0]
        response = self.client.post("/predict/", json=input_data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn(
            "Terjadi error saat prediksi: Prediction calculation error", response.json()["detail"])

    # --- Test cases untuk hitung_kategori_bmi ---
    # Metode ini tidak menggunakan 'model', jadi tidak perlu argumen mock_model
    def test_bmi_category_underweight(self):
        self.assertEqual(hitung_kategori_bmi(50, 170), 0)
        self.assertEqual(hitung_kategori_bmi(53.4, 170), 0)

    def test_bmi_category_normal(self):
        self.assertEqual(hitung_kategori_bmi(54, 170), 1)
        self.assertEqual(hitung_kategori_bmi(72, 170), 1)

    def test_bmi_category_overweight(self):
        self.assertEqual(hitung_kategori_bmi(73, 170), 2)
        self.assertEqual(hitung_kategori_bmi(80, 170), 2)


if __name__ == "__main__":
    unittest.main()
