import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from routers.analisis_rontgen_api import router
from io import BytesIO
from PIL import Image
import numpy as np
import os

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def generate_dummy_image(format='PNG'):
    img = Image.new("RGB", (384, 384), color=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


class TestRontgenPredictAPI(unittest.TestCase):

    @patch("routers.analisis_rontgen_api.best_model")
    def test_predict_rontgen_success_tuberculosis(self, mock_model):
        mock_model.predict.return_value = np.array(
            [[0.85]])  # Prediksi Tuberculosis
        file_data = generate_dummy_image()

        response = client.post(
            "/predict-rontgen/",
            files={"file": ("test.png", file_data, "image/png")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["label"], "Tuberculosis")
        self.assertEqual(response.json()["confidence"], 0.85)
        mock_model.predict.assert_called_once()

    @patch("routers.analisis_rontgen_api.best_model")
    def test_predict_rontgen_success_normal(self, mock_model):
        mock_model.predict.return_value = np.array([[0.15]])  # Prediksi Normal
        file_data = generate_dummy_image()

        response = client.post(
            "/predict-rontgen/",
            files={"file": ("test.png", file_data, "image/png")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["label"], "Normal")
        self.assertEqual(response.json()["confidence"], 0.85)  # 1 - 0.15
        mock_model.predict.assert_called_once()

    # Set model to None
    @patch("routers.analisis_rontgen_api.best_model", new=None)
    @patch("os.path.exists", return_value=False)  # Simulasikan model tidak ada
    def test_model_not_loaded(self, mock_exists):
        file_data = generate_dummy_image()

        response = client.post(
            "/predict-rontgen/",
            files={"file": ("test.png", file_data, "image/png")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"],
                         "Model tidak ditemukan di server")

    # Mock fungsi pemrosesan gambar
    @patch("routers.analisis_rontgen_api.image.load_img")
    def test_predict_rontgen_invalid_image_format(self, mock_load_img):
        mock_load_img.side_effect = Exception(
            "Invalid image format")  # Simulasikan error format
        # Berikan format yang mungkin tidak didukung
        file_data = generate_dummy_image(format='BMP')

        response = client.post(
            "/predict-rontgen/",
            files={"file": ("test.bmp", file_data, "image/bmp")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Terjadi error", response.json()["error"])
        self.assertIn("Invalid image format", response.json()["error"])

    @patch("routers.analisis_rontgen_api.best_model")
    @patch("routers.analisis_rontgen_api.image.load_img")
    # Patch img_to_array juga
    @patch("routers.analisis_rontgen_api.image.img_to_array")
    @patch("numpy.expand_dims")  # Patch numpy.expand_dims juga
    # Patch preprocess_input
    @patch("tensorflow.keras.applications.mobilenet_v2.preprocess_input")
    def test_predict_rontgen_prediction_error(self, mock_preprocess_input, mock_expand_dims, mock_img_to_array, mock_load_img, mock_model):
        # Pastikan mock_load_img dan mock_img_to_array mengembalikan nilai yang valid
        # agar exception hanya datang dari mock_model.predict
        # Mengembalikan objek mock untuk gambar
        mock_load_img.return_value = MagicMock()
        mock_img_to_array.return_value = np.array(
            [1, 2, 3])  # Mengembalikan array dummy
        mock_expand_dims.return_value = np.array(
            [[1, 2, 3]])  # Mengembalikan array dummy
        mock_preprocess_input.return_value = np.array(
            [[1, 2, 3]])  # Mengembalikan array dummy

        mock_model.predict.side_effect = Exception(
            "Prediction calculation error")  # Simulasikan error prediksi
        file_data = generate_dummy_image()

        response = client.post(
            "/predict-rontgen/",
            files={"file": ("test.png", file_data, "image/png")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Terjadi error", response.json()["error"])
        self.assertIn("Prediction calculation error", response.json()["error"])


if __name__ == "__main__":
    unittest.main()
