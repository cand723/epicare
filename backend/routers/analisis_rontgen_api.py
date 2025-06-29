from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import io
import os

router = APIRouter()

MODEL_PATH = "model/best_model.h5"
best_model = None
if os.path.exists(MODEL_PATH):
    best_model = tf.keras.models.load_model(MODEL_PATH)


@router.post("/predict-rontgen/")
async def predict_rontgen(file: UploadFile = File(...)):
    if best_model is None:
        return JSONResponse(status_code=500, content={"error": "Model tidak ditemukan di server"})

    try:
        contents = await file.read()
        img = image.load_img(io.BytesIO(contents), target_size=(384, 384))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        pred = best_model.predict(img_array)[0][0]
        label = "Tuberculosis" if pred > 0.5 else "Normal"
        confidence = pred if pred > 0.5 else 1 - pred

        return JSONResponse(content={
            "label": label,
            "confidence": round(float(confidence), 4)
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Terjadi error: {str(e)}"})
