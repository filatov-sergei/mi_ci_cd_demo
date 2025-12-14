import joblib
import os

def test_model_file_exists():
    assert os.path.exists("model.pkl") == False, "Model should not exist before training"