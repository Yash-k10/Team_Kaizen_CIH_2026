import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "data/match_model.pkl"

def train_model():
    data = {
        "blood_match": [1,1,0,1,0,1],
        "organ_match": [1,1,1,0,1,1],
        "urgency_level": [5,4,3,5,2,4],
        "waiting_days": [300,200,150,400,100,250],
        "age_gap": [10,5,20,15,30,8],
        "distance_km": [20,50,100,30,200,40],
        "priority": [1,1,0,1,0,1]
    }

    df = pd.DataFrame(data)

    X = df.drop("priority", axis=1)
    y = df["priority"]

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("ML model trained and saved.")

def predict_priority(features):
    model = joblib.load(MODEL_PATH)
    df = pd.DataFrame([features])
    return model.predict_proba(df)[0][1]
