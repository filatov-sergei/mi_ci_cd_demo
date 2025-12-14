import os
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Загрузка модели
model = joblib.load("model.pkl")

class PredictRequest(BaseModel):
    x: list[float]

@app.get("/health")
def health():
    return {"status": "ok", "version": os.getenv("MODEL_VERSION", "v1.0.0")}

@app.post("/predict")
def predict(request: PredictRequest):
    prediction = model.predict([request.x])
    return {"prediction": prediction.tolist()}