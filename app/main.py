import os
import pickle
import logging
from fastapi import FastAPI
from pydantic import BaseModel

# Настройка логирования (для мониторинга, критерий 5)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Загрузка модели
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

class PredictRequest(BaseModel):
    x: list[float]

@app.get("/health")
def health():
    version = os.getenv("MODEL_VERSION", "v1.0.0")
    logger.info(f"Health check: status=ok, version={version}")
    return {"status": "ok", "version": version}  # Возвращает версию для мониторинга

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        prediction = model.predict([request.x])  # Адаптируй под свою модель
        logger.info(f"Prediction made: input={request.x}, output={prediction}")
        return {"prediction": prediction.tolist()}
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"error": str(e)}