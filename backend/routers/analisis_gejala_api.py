from fastapi import APIRouter, Body, HTTPException, status
import tensorflow as tf
import numpy as np
from typing import List
import os
from fastapi.responses import JSONResponse

router = APIRouter()

MODEL_PATH = "backend/model/model_nn.keras"
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"DEBUG: Model loaded successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to load model from {MODEL_PATH}: {e}")
        model = None  # Pastikan model tetap None jika gagal load

feature_names = [
    "Batuk", "Berkeringat di Malam Hari", "Kesulitan Bernapas", "Demam",
    "Nyeri Dada", "Dahak", "Penekanan Sistem Imun", "Kehilangan Rasa Senang",
    "Menggigil", "Kehilangan Konsentrasi", "Mudah_Tersinggung", "Kehilangan Nafsu Makan",
    "Kehilangan Energi", "Pembengkakan Kelenjar Getah Bening",
    "Tekanan Darah Sistolik", "Kategori BMI"
]


class InputData:
    def __init__(
        self,
        Batuk, Berkeringat_di_Malam_Hari, Kesulitan_Bernapas, Demam,
        Nyeri_Dada, Dahak, Penekanan_Sistem_Imun, Kehilangan_Rasa_Senang,
        Menggigil, Kehilangan_Konsentrasi, Mudah_Tersinggung, Kehilangan_Nafsu_Makan,
        Kehilangan_Energi, Pembengkakan_Kelenjar_Getah_Bening,
        Tekanan_Darah_Sistolik, BMI_kategori
    ):
        self.Batuk = Batuk
        self.Berkeringat_di_Malam_Hari = Berkeringat_di_Malam_Hari
        self.Kesulitan_Bernapas = Kesulitan_Bernapas
        self.Demam = Demam
        self.Nyeri_Dada = Nyeri_Dada
        self.Dahak = Dahak
        self.Penekanan_Sistem_Imun = Penekanan_Sistem_Imun
        self.Kehilangan_Rasa_Senang = Kehilangan_Rasa_Senang
        self.Menggigil = Menggigil
        self.Kehilangan_Konsentrasi = Kehilangan_Konsentrasi
        self.Mudah_Tersinggung = Mudah_Tersinggung
        self.Kehilangan_Nafsu_Makan = Kehilangan_Nafsu_Makan
        self.Kehilangan_Energi = Kehilangan_Energi
        self.Pembengkakan_Kelenjar_Getah_Bening = Pembengkakan_Kelenjar_Getah_Bening
        self.Tekanan_Darah_Sistolik = Tekanan_Darah_Sistolik
        self.BMI = BMI_kategori


def hitung_kategori_bmi(berat_kg: float, tinggi_cm: float) -> int:
    tinggi_m = tinggi_cm / 100
    bmi = berat_kg / (tinggi_m ** 2)
    if bmi < 18.5:
        return 0
    elif bmi < 25:
        return 1
    else:
        return 2


def predict(input_data: InputData):
    global model
    if model is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Model AI tidak tersedia di server")

    input_array = np.array([[  # Susun array input
        input_data.Batuk,
        input_data.Berkeringat_di_Malam_Hari,
        input_data.Kesulitan_Bernapas,
        input_data.Demam,
        input_data.Nyeri_Dada,
        input_data.Dahak,
        input_data.Penekanan_Sistem_Imun,
        input_data.Kehilangan_Rasa_Senang,
        input_data.Menggigil,
        input_data.Kehilangan_Konsentrasi,
        input_data.Mudah_Tersinggung,
        input_data.Kehilangan_Nafsu_Makan,
        input_data.Kehilangan_Energi,
        input_data.Pembengkakan_Kelenjar_Getah_Bening,
        input_data.Tekanan_Darah_Sistolik,
        input_data.BMI
    ]])
    try:
        prediction = model.predict(input_array)
        prediction_value = prediction[0][0] * 100
        return f"{prediction_value:.2f}%"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Terjadi error saat prediksi: {str(e)}")


@router.post("/predict/")
async def get_prediction(data: List[float] = Body(...)):
    # ✅ Nama variabel sudah benar: "data"
    if not isinstance(data, list) or len(data) != 17:
        return JSONResponse(
            status_code=200,
            content={"error": "Input harus 17 elemen: 15 fitur + berat + tinggi"}
        )

    *fitur, berat, tinggi = data
    bmi_kategori = hitung_kategori_bmi(berat, tinggi)

    input_data_args = fitur + [bmi_kategori]

    try:
        input_data = InputData(*input_data_args)
        prediction = predict(input_data)

        print("\n📥 Prediksi diminta:")
        for nama, nilai in zip(feature_names, input_data_args):
            print(f"  - {nama}: {nilai}")
        print(f"📤 Hasil prediksi: {prediction}")

        return {"prediction": prediction}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi error saat pemrosesan: {str(e)}"
        )
