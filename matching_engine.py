from math import radians, cos, sin, asin, sqrt
from ml_model import predict_score

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def blood_compatible(donor, patient):
    return donor == patient

def match(patient, donors):
    results = []
    for d in donors:
        if not blood_compatible(d["blood"], patient["blood"]):
            continue

        dist = haversine(patient["lat"], patient["lon"], d["lat"], d["lon"])
        score = predict_score(patient["urgency"], dist, 1)

        results.append({
            "donor": d["name"],
            "distance_km": round(dist, 1),
            "score": score
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
