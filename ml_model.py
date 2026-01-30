import pickle
import os

MODEL_PATH = "data/match_model.pkl"

def train_dummy_model():
    model = {"w_urgency": 0.6, "w_distance": -0.3, "w_compat": 0.7}
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_dummy_model()
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict_score(urgency, distance, compatibility):
    model = load_model()
    score = (
        model["w_urgency"] * urgency +
        model["w_distance"] * distance +
        model["w_compat"] * compatibility
    )
    return round(score, 2)
