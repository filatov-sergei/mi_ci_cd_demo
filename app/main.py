import os
import pickle
import logging
from fastapi import FastAPI
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

model_path = "model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Critical error loading model: {e}")
    raise

class PredictRequest(BaseModel):
    x: list[float]

@app.get("/health")
def health():
    version = os.getenv("MODEL_VERSION", "v1.0.0")
    logger.info(f"Health check: status=ok, version={version}")
    return {"status": "ok", "version": version}

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        if len(request.x) != 4:
            raise ValueError("Input must be a list of 4 floats (Iris features)")
        prediction = model.predict([request.x])[0]
        logger.info(f"Prediction made: input={request.x}, output={prediction}")
        return {"prediction": int(prediction)}
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise